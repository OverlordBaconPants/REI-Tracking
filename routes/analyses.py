from utils.flash import flash_message
from utils.money import Money, Percentage
import logging
from flask import Blueprint, render_template, request, current_app, jsonify, redirect, url_for, send_file
from flask_login import login_required, current_user
from services.report_generator import generate_lender_report, LenderMetricsCalculator, MAOCalculator
from services.analysis_calculations import create_analysis as create_analysis_calc  # Renamed import
import uuid
from datetime import datetime, timezone
import os
import json
import traceback
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    Paragraph, Spacer, Table, TableStyle, 
    BaseDocTemplate, Frame, PageTemplate, FrameBreak
)
from config import Config
from typing import Dict, Any, List, Tuple, Optional

analyses_bp = Blueprint('analyses', __name__)

# Configure logging
logger = logging.getLogger(__name__)

class DynamicFrameDocument(BaseDocTemplate):
    """Custom document template for PDF generation"""
    def __init__(self, filename, **kwargs):
        BaseDocTemplate.__init__(self, filename, **kwargs)
        self.top_height = 1.5*inch  # Set a default height
        self._calc_frames()

    def handle_flowables(self, flowables):
        frame = self.frame
        for flowable in flowables:
            if isinstance(flowable, Table) and not hasattr(self, 'measured_top_height'):
                # Measure the height of the logo and title table
                w, h = flowable.wrap(self.width, self.height)
                self.top_height = h + 0.25*inch  # Add some padding
                self.measured_top_height = True
                self._calc_frames()
            try:
                frame = frame.add(flowable, self.canv, trySplit=self.allowSplitting)
            except:
                if not frame.allow_split:
                    raise
                flowable = flowable.splitOn(frame, self.canv)
                if not flowable:
                    raise
                frame = frame.split(flowable[0], self.canv)
                self.afterFlowable(flowable[0])
                flowables = [flowable[1]] + flowables[1:]
            if not frame:
                frame = self.handle_nextPageTemplate(flowables)
                self.handle_frameEnd()

    def _calc_frames(self):
        page_height = self.height
        page_width = self.width
        top_margin = self.topMargin
        bottom_margin = self.bottomMargin
        left_margin = self.leftMargin
        right_margin = self.rightMargin

        # Full width frame for logo and title
        full_frame = Frame(
            left_margin, 
            page_height - top_margin - self.top_height,
            page_width - left_margin - right_margin, 
            self.top_height,
            id='full'
        )
        
        # Two column frames for the rest of the content
        column_height = page_height - top_margin - bottom_margin - self.top_height
        column_width = (page_width - left_margin - right_margin - 12) / 2  # 12 is gutter width
        
        left_frame = Frame(
            left_margin, 
            bottom_margin, 
            column_width, 
            column_height, 
            id='col1'
        )
        
        right_frame = Frame(
            left_margin + column_width + 12,
            bottom_margin,
            column_width,
            column_height,
            id='col2'
        )
        
        self.addPageTemplates([
            PageTemplate(id='FirstPage', frames=[full_frame, left_frame, right_frame]),
            PageTemplate(id='TwoColumn', frames=[left_frame, right_frame])
        ])

@analyses_bp.route('/create_analysis', methods=['GET', 'POST']) 
@login_required
def create_analysis():
    """Handle both GET and POST requests for analysis creation."""
    # Handle viewing/editing existing analysis
    analysis_id = request.args.get('analysis_id')
    existing_analysis = None
    
    if analysis_id and request.method == 'GET':
        try:
            # Get existing analysis
            response = get_analysis(analysis_id)
            if isinstance(response, tuple):
                return redirect(url_for('analyses.view_edit_analysis'))
            
            analysis_data = response.get_json()
            if not analysis_data or not analysis_data.get('success'):
                return redirect(url_for('analyses.view_edit_analysis'))
                
            existing_analysis = analysis_data['analysis']
            existing_analysis['edit_mode'] = True
            
        except Exception as e:
            logger.error(f"Error fetching analysis: {str(e)}")
            logger.error(traceback.format_exc())
            return redirect(url_for('analyses.view_edit_analysis'))

    if request.method == 'POST':
        try:
            analysis_data = request.get_json()
            if not analysis_data:
                raise ValueError("No analysis data provided")

            # Add metadata
            if not analysis_id:
                analysis_id = str(uuid.uuid4())
            analysis_data['id'] = analysis_id
            analysis_data['user_id'] = current_user.id
            analysis_data['created_at'] = datetime.now(tz=timezone.utc).isoformat()
            analysis_data['updated_at'] = analysis_data['created_at']

            # Create analysis object using the calculator service with renamed import
            analysis = create_analysis_calc(analysis_data)
            
            # Format results for storage/response
            results = {
                'id': analysis_id,
                'user_id': current_user.id,
                'created_at': analysis_data['created_at'],
                'updated_at': analysis_data['updated_at'],
                'analysis_type': analysis_data['analysis_type'],
                'analysis_name': analysis_data['analysis_name'],
                'property_address': analysis_data['property_address'],
                
                # Property details
                'purchase_price': str(analysis.purchase_price),
                'after_repair_value': str(analysis.after_repair_value),
                'renovation_costs': str(analysis.renovation_costs),
                'renovation_duration': analysis_data['renovation_duration'],
                
                # Cash flows
                'monthly_rent': str(analysis.monthly_rent),
                'monthly_cash_flow': str(analysis.calculate_monthly_cash_flow()),
                'annual_cash_flow': str(analysis.calculate_annual_cash_flow()),
                
                # Operating expenses
                'total_operating_expenses': str(analysis.operating_expenses.calculate_total()),
                'operating_expenses': {
                    'Property Taxes': str(analysis.operating_expenses.property_taxes),
                    'Insurance': str(analysis.operating_expenses.insurance),
                    'Management': str(analysis.operating_expenses.calculate_management_fee()),
                    'CapEx': str(analysis.operating_expenses.calculate_capex()),
                    'Vacancy': str(analysis.operating_expenses.calculate_vacancy())
                }
            }

            # Add BRRRR-specific results if applicable
            if analysis_data['analysis_type'] in ['BRRRR', 'PadSplit BRRRR']:
                results.update({
                    'initial_loan_amount': str(analysis.initial_loan.amount),
                    'initial_interest_rate': str(analysis.initial_loan.interest_rate),
                    'initial_loan_term': analysis.initial_loan.term_months,
                    'initial_monthly_payment': str(analysis.initial_loan.calculate_payment().total),
                    'initial_closing_costs': str(analysis.initial_loan.closing_costs),
                    
                    'refinance_loan_amount': str(analysis.refinance_loan.amount),
                    'refinance_interest_rate': str(analysis.refinance_loan.interest_rate),
                    'refinance_loan_term': analysis.refinance_loan.term_months,
                    'refinance_monthly_payment': str(analysis.refinance_loan.calculate_payment().total),
                    'refinance_closing_costs': str(analysis.refinance_loan.closing_costs),
                    
                    'equity_captured': str(analysis.calculate_equity_captured()),
                    'cash_recouped': str(analysis.calculate_cash_recouped()),
                    'total_project_costs': str(analysis.calculate_total_project_costs()),
                    'total_cash_invested': str(analysis.calculate_total_cash_invested()),
                    'cash_on_cash_return': analysis.calculate_cash_on_cash_return(),
                    'roi': analysis.calculate_roi(),
                    'total_monthly_expenses': str(analysis.calculate_total_monthly_expenses()),
                    
                    # Add holding costs
                    'holding_costs': str(analysis.holding_costs)
                })

            # Make sure analyses directory exists
            analyses_dir = os.path.join(Config.DATA_DIR, 'analyses')
            os.makedirs(analyses_dir, exist_ok=True)

            # Save analysis to file
            filename = f"{results['id']}_{current_user.id}.json"
            filepath = os.path.join(analyses_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(results, f, indent=2)

            return jsonify({
                "success": True,
                "message": "Analysis created successfully",
                "analysis": results
            })

        except Exception as e:
            logger.error(f"Error processing analysis: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                "success": False,
                "message": f"An error occurred: {str(e)}"
            }), 500

    # GET request - render the create/edit form
    template_data = {'analysis': existing_analysis} if existing_analysis else {}
    return render_template('analyses/create_analysis.html', **template_data)

@analyses_bp.route('/update_analysis', methods=['POST'])
@login_required
def update_analysis():
    """Handle updates to existing analyses."""
    try:
        analysis_data = request.get_json()
        if not analysis_data:
            raise ValueError("No analysis data provided")

        # Get and validate analysis ID
        analysis_id = analysis_data.get('id')
        if not analysis_id:
            return jsonify({"success": False, "message": "Analysis ID is required"}), 400

        # Find existing analysis file
        analyses_dir = os.path.join(Config.DATA_DIR, 'analyses')
        filepath = os.path.join(analyses_dir, f"{analysis_id}_{current_user.id}.json")

        if not os.path.exists(filepath):
            return jsonify({"success": False, "message": "Analysis not found"}), 404

        # Get original creation timestamp
        with open(filepath, 'r') as f:
            original_data = json.load(f)
            analysis_data['created_at'] = original_data.get('created_at')

        # Add metadata
        analysis_data['id'] = analysis_id  # Preserve ID
        analysis_data['user_id'] = current_user.id
        analysis_data['updated_at'] = datetime.now(tz=timezone.utc).isoformat()

        # Create analysis object and calculate results
        analysis = create_analysis_calc(analysis_data)
        
        # Format results for storage/response
        results = {
            'id': analysis_id,
            'user_id': current_user.id,
            'created_at': analysis_data['created_at'],
            'updated_at': analysis_data['updated_at'],
            'analysis_type': analysis_data['analysis_type'],
            'analysis_name': analysis_data['analysis_name'],
            'property_address': analysis_data['property_address'],
            
            # Property details with all fields
            'purchase_price': str(analysis.purchase_price),
            'after_repair_value': str(analysis.after_repair_value),
            'renovation_costs': str(analysis.renovation_costs),
            'renovation_duration': analysis_data['renovation_duration'],
            'home_square_footage': analysis_data.get('home_square_footage'),
            'lot_square_footage': analysis_data.get('lot_square_footage'),
            'year_built': analysis_data.get('year_built'),
            
            # Cash flows
            'monthly_rent': str(analysis.monthly_rent),
            'monthly_cash_flow': str(analysis.calculate_monthly_cash_flow()),
            'annual_cash_flow': str(analysis.calculate_annual_cash_flow()),
            
            # Operating expenses
            'total_operating_expenses': str(analysis.operating_expenses.calculate_total()),
            'operating_expenses': {
                'Property Taxes': str(analysis.operating_expenses.property_taxes),
                'Insurance': str(analysis.operating_expenses.insurance),
                'Management': str(analysis.operating_expenses.calculate_management_fee()),
                'CapEx': str(analysis.operating_expenses.calculate_capex()),
                'Vacancy': str(analysis.operating_expenses.calculate_vacancy())
            }
        }

        # Add BRRRR-specific results if applicable
        if analysis_data['analysis_type'] in ['BRRRR', 'PadSplit BRRRR']:
            results.update({
                # Initial loan details
                'initial_loan_amount': str(analysis.initial_loan.amount),
                'initial_interest_rate': str(analysis.initial_loan.interest_rate),
                'initial_interest_only': analysis.initial_loan.is_interest_only,
                'initial_loan_term': analysis.initial_loan.term_months,
                'initial_monthly_payment': str(analysis.initial_loan.calculate_payment().total),
                'initial_closing_costs': str(analysis.initial_loan.closing_costs),
                'initial_down_payment': str(analysis.initial_loan.down_payment),
                
                # Refinance details
                'refinance_loan_amount': str(analysis.refinance_loan.amount),
                'refinance_interest_rate': str(analysis.refinance_loan.interest_rate),
                'refinance_loan_term': analysis.refinance_loan.term_months,
                'refinance_monthly_payment': str(analysis.refinance_loan.calculate_payment().total),
                'refinance_closing_costs': str(analysis.refinance_loan.closing_costs),
                'refinance_down_payment': str(analysis.refinance_loan.down_payment),
                
                # Additional metrics
                'equity_captured': str(analysis.calculate_equity_captured()),
                'cash_recouped': str(analysis.calculate_cash_recouped()),
                'total_project_costs': str(analysis.calculate_total_project_costs()),
                'total_cash_invested': str(analysis.calculate_total_cash_invested()),
                'cash_on_cash_return': analysis.calculate_cash_on_cash_return(),
                'roi': analysis.calculate_roi(),
                'total_monthly_expenses': str(analysis.calculate_total_monthly_expenses()),
                'holding_costs': str(analysis.holding_costs)
            })

        # Save analysis to file
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)

        return jsonify({
            "success": True,
            "message": "Analysis updated successfully",
            "analysis": results
        })

    except Exception as e:
        logger.error(f"Error updating analysis: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "message": f"An error occurred: {str(e)}"
        }), 500

@analyses_bp.route('/get_analysis/<analysis_id>', methods=['GET'])
@login_required
def get_analysis(analysis_id):
    """Get a specific analysis by ID"""
    try:
        # Find analysis file
        analyses_dir = os.path.join(Config.DATA_DIR, 'analyses')
        analysis_file = None
        
        for filename in os.listdir(analyses_dir):
            if filename.startswith(f"{analysis_id}_") and filename.endswith(f"_{current_user.id}.json"):
                analysis_file = filename
                break

        if not analysis_file:
            return jsonify({"success": False, "message": "Analysis not found"}), 404

        filepath = os.path.join(analyses_dir, analysis_file)
        
        # Read and return the analysis data
        with open(filepath, 'r') as f:
            analysis_data = json.load(f)
            
        return jsonify({
            "success": True, 
            "analysis": analysis_data
        })
        
    except Exception as e:
        logger.error(f"Error retrieving analysis: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@analyses_bp.route('/view_analysis/<analysis_id>', methods=['GET'])
@login_required
def view_analysis(analysis_id):
    """View a single analysis"""
    try:
        analysis = get_analysis(analysis_id)
        if not analysis:
            flash_message('Analysis not found', 'error')
            return redirect(url_for('analyses.view_edit_analysis'))
            
        return render_template('analyses/view_analysis.html', analysis=analysis)
        
    except Exception as e:
        logger.error(f"Error viewing analysis: {str(e)}")
        flash_message('Error loading analysis', 'error')
        return redirect(url_for('analyses.view_edit_analysis'))

@analyses_bp.route('/view_edit_analysis')
@login_required
def view_edit_analysis():
    """View/edit analysis list page"""
    try:
        page = request.args.get('page', 1, type=int)
        analyses_per_page = 10
        
        analyses, total_pages = get_paginated_analyses(page, analyses_per_page)
        
        return render_template(
            'analyses/view_edit_analysis.html', 
            analyses=analyses, 
            current_page=page, 
            total_pages=total_pages
        )
    except Exception as e:
        logger.error(f"Error in view_edit_analysis: {str(e)}")
        logger.error(traceback.format_exc())
        flash_message('Error loading analyses', 'error')
        return redirect(url_for('dashboards.dashboards'))

def get_paginated_analyses(page: int, per_page: int) -> Tuple[List[Dict], int]:
    """Get paginated list of analyses for the current user."""
    try:
        analyses_dir = os.path.join(Config.DATA_DIR, 'analyses')
        if not os.path.exists(analyses_dir):
            return [], 0

        # Get all analyses for current user
        all_analyses = []
        for filename in os.listdir(analyses_dir):
            if filename.endswith(f"_{current_user.id}.json"):
                with open(os.path.join(analyses_dir, filename), 'r') as f:
                    analysis_data = json.load(f)
                    # Extract ID from filename
                    analysis_id = filename.split('_')[0]
                    analysis_data['id'] = analysis_id
                    # Get creation date from file if not in data
                    if 'created_at' not in analysis_data:
                        timestamp = os.path.getctime(os.path.join(analyses_dir, filename))
                        analysis_data['created_at'] = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
                    all_analyses.append(analysis_data)

        # Sort analyses by creation date, newest first
        all_analyses.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        # Calculate pagination
        total_analyses = len(all_analyses)
        total_pages = max((total_analyses + per_page - 1) // per_page, 1)
        
        # Adjust page number if out of bounds
        page = min(max(page, 1), total_pages)
        
        # Get the analyses for the current page
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total_analyses)
        
        return all_analyses[start_idx:end_idx], total_pages
        
    except Exception as e:
        logger.error(f"Error in get_paginated_analyses: {str(e)}")
        return [], 0

@analyses_bp.route('/generate_pdf/<analysis_id>', methods=['GET'])
@login_required
def generate_pdf(analysis_id):
    """Generate PDF report for an analysis"""
    try:
        logger.info(f"Starting PDF generation for analysis {analysis_id}")
        
        # Get analysis data
        analyses_dir = os.path.join(Config.DATA_DIR, 'analyses')
        analysis_file = None
        
        # Find the correct analysis file
        for filename in os.listdir(analyses_dir):
            if filename.startswith(f"{analysis_id}_") and filename.endswith(f"_{current_user.id}.json"):
                analysis_file = filename
                break

        if not analysis_file:
            logger.error(f"Analysis file not found for ID: {analysis_id}")
            return jsonify({'error': 'Analysis not found'}), 404

        filepath = os.path.join(analyses_dir, analysis_file)
        
        # Read and parse the analysis data
        with open(filepath, 'r') as f:
            try:
                analysis_data = json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {str(e)}")
                return jsonify({'error': f'Invalid analysis data: {str(e)}'}), 500

        # Validate the analysis data
        if not isinstance(analysis_data, dict):
            logger.error("Analysis data is not a dictionary")
            return jsonify({'error': 'Invalid analysis data format'}), 500

        # Create metrics calculator and generate report
        calculator = LenderMetricsCalculator(analysis_data)
        buffer = BytesIO()
        
        try:
            generate_lender_report(analysis_data, calculator, buffer)
        except Exception as e:
            logger.error(f"Error in report generation: {str(e)}")
            logger.exception("Full traceback:")
            return jsonify({'error': f'Error generating report: {str(e)}'}), 500
        
        # Prepare response
        buffer.seek(0)
        filename = f"{analysis_data.get('analysis_name', 'analysis')}_report.pdf"
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )

    except Exception as e:
        logger.error(f"Global error in generate_pdf: {str(e)}")
        logger.exception("Full traceback:")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

def create_table(data: List[List[str]]) -> Table:
    """Create a formatted table for PDF reports"""
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    return table