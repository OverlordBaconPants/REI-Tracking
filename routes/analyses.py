from flask import Blueprint, render_template, request, jsonify, redirect, url_for, send_file
from flask_login import login_required, current_user
from services.analysis_service import AnalysisService
from services.analysis_calculations import ActualPerformanceMetrics
from services.transaction_service import get_transactions_for_user, get_properties_for_user
from utils.flash import flash_message
import logging
from typing import Dict, Any
import traceback

analyses_bp = Blueprint('analyses', __name__, url_prefix='/analyses')  # Add url_prefix
logger = logging.getLogger(__name__)
analysis_service = AnalysisService()

@analyses_bp.route('/create_analysis', methods=['GET', 'POST']) 
@login_required
def create_analysis():
    """Handle both GET and POST requests for analysis creation."""
    if request.method == 'POST':
        try:
            analysis_data = request.get_json()
            if not analysis_data:
                return jsonify({"success": False, "message": "No analysis data provided"}), 400

            results = analysis_service.create_analysis(analysis_data, current_user.id)
            return jsonify({
                "success": True,
                "message": "Analysis created successfully",
                "analysis": results
            })
        except Exception as e:
            logger.error(f"Error creating analysis: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                "success": False,
                "message": f"An error occurred: {str(e)}"
            }), 500

    # GET request - handle existing analysis editing
    analysis_id = request.args.get('analysis_id')
    existing_analysis = None
    if analysis_id:
        try:
            existing_analysis = analysis_service.get_analysis(analysis_id, current_user.id)
            if existing_analysis:
                existing_analysis['edit_mode'] = True
            else:
                flash_message('Analysis not found', 'error')
                return redirect(url_for('analyses.view_edit_analysis'))
        except Exception as e:
            logger.error(f"Error fetching analysis: {str(e)}")
            flash_message('Error loading analysis', 'error')
            return redirect(url_for('analyses.view_edit_analysis'))

    return render_template(
        'analyses/create_analysis.html',
        analysis=existing_analysis,
        body_class='analysis-page'
    )

@analyses_bp.route('/update_analysis', methods=['POST'])
@login_required
def update_analysis():
    try:
        analysis_data = request.get_json()
        if not analysis_data:
            return jsonify({"success": False, "message": "No analysis data provided"}), 400

        # Convert string money values to float
        for key in ['monthly_rent', 'total_operating_expenses', 'monthly_cash_flow', 'annual_cash_flow']:
            if key in analysis_data and isinstance(analysis_data[key], str):
                analysis_data[key] = float(analysis_data[key].replace('$', '').replace(',', ''))

        # Clean loan data
        if 'loans' in analysis_data:
            for loan in analysis_data['loans']:
                for key in ['amount', 'down_payment', 'closing_costs']:
                    if key in loan and isinstance(loan[key], str):
                        loan[key] = float(loan[key].replace('$', '').replace(',', ''))

        results = analysis_service.update_analysis(analysis_data, current_user.id)
        return jsonify({
            "success": True,
            "message": "Analysis updated successfully",
            "analysis": results
        })
    except Exception as e:
        logger.error(f"Error updating analysis: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"An error occurred: {str(e)}"
        }), 500

@analyses_bp.route('/get_analysis/<analysis_id>', methods=['GET'])
@login_required
def get_analysis(analysis_id: str):
    """Get a specific analysis by ID"""
    try:
        analysis = analysis_service.get_analysis(analysis_id, current_user.id)
        if not analysis:
            return jsonify({"success": False, "message": "Analysis not found"}), 404
            
        return jsonify({
            "success": True, 
            "analysis": analysis
        })
    except Exception as e:
        logger.error(f"Error retrieving analysis: {str(e)}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@analyses_bp.route('/view_edit_analysis')
@login_required
def view_edit_analysis():
    """View/edit analysis list page"""
    try:
        # Get page parameter with error handling
        try:
            page = max(1, int(request.args.get('page', 1)))
        except (TypeError, ValueError) as e:
            logger.warning(f"Invalid page parameter: {str(e)}")
            page = 1

        analyses_per_page = 10
        
        logger.info(f"Fetching analyses for user {current_user.id}, page {page}")
        
        # Get analyses with explicit error handling
        try:
            analyses, total_pages = analysis_service.get_analyses_for_user(
                current_user.id, 
                page, 
                analyses_per_page
            )
            
            logger.debug(f"Retrieved {len(analyses) if analyses else 0} analyses")
            
            return render_template(
                'analyses/view_edit_analysis.html', 
                analyses=analyses, 
                current_page=page, 
                total_pages=total_pages,
                body_class='view-edit-analysis-page'  # Add this line
            )
            
        except Exception as e:
            logger.error(f"Error retrieving analyses from service: {str(e)}")
            logger.error(traceback.format_exc())
            raise  # Re-raise to be caught by outer try block
        
    except Exception as e:
        logger.error(f"Error in view_edit_analysis: {str(e)}")
        logger.error(traceback.format_exc())
        flash_message('Error loading analyses: ' + str(e), 'error')
        return redirect(url_for('dashboards.dashboards'))

@analyses_bp.route('/view_analysis/<analysis_id>', methods=['GET'])
@login_required
def view_analysis(analysis_id: str):
    """View a single analysis"""
    try:
        analysis = analysis_service.get_analysis(analysis_id, current_user.id)
        if not analysis:
            flash_message('Analysis not found', 'error')
            return redirect(url_for('analyses.view_edit_analysis'))
            
        return render_template('analyses/view_analysis.html', analysis=analysis)
    except Exception as e:
        logger.error(f"Error viewing analysis: {str(e)}")
        flash_message('Error loading analysis', 'error')
        return redirect(url_for('analyses.view_edit_analysis'))

@analyses_bp.route('/generate_pdf/<analysis_id>', methods=['GET'])
@login_required
def generate_pdf(analysis_id: str):
    """Generate PDF report for an analysis"""
    try:
        pdf_buffer = analysis_service.generate_pdf_report(analysis_id, current_user.id)
        if not pdf_buffer:
            return jsonify({'error': 'Failed to generate PDF'}), 500

        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"analysis_{analysis_id}_report.pdf"
        )
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        return jsonify({'error': f'Error generating PDF: {str(e)}'}), 500
    
@analyses_bp.route('/kpi-comparison')
@login_required
def kpi_comparison():
    try:
        analysis_service = AnalysisService()
        properties = get_properties_for_user(
            current_user.id, 
            current_user.name
        )
        return render_template('analyses/kpi_comparison.html', properties=properties)
    except Exception as e:
        logger.error(f"Error in kpi_comparison: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analyses_bp.route('/api/kpi-data/<path:property_id>')
@login_required
def get_kpi_data(property_id):
    try:
        from urllib.parse import unquote
        property_id = unquote(property_id)
        
        # First try exact match
        analyses = analysis_service._get_analyses_by_property(property_id)
        
        # If no match, try with normalized address
        if not analyses:
            base_address = property_id.split(', United States of America')[0]
            analyses = analysis_service._get_analyses_by_property(base_address + ", United States of America")
        
        if not analyses:
            return jsonify({'error': 'No analyses found for property'}), 404
            
        # Sort by updated_at if available, otherwise use created_at or fallback to first analysis
        try:
            latest_analysis = max(analyses, key=lambda x: x.get('updated_at', x.get('created_at', '')))
        except Exception:
            latest_analysis = analyses[0]
        
        transactions = get_transactions_for_user(
            current_user.id,
            property_id=property_id
        )
        
        actual_metrics = ActualPerformanceMetrics(property_id, transactions)
        actual_kpis = actual_metrics.get_metrics()
        
        return jsonify({
            'planned': {
                'monthly_income': latest_analysis.get('monthly_rent', 0),
                'monthly_expenses': latest_analysis.get('total_operating_expenses', 0),
                'monthly_cash_flow': latest_analysis.get('monthly_cash_flow', 0),
                'annual_cash_flow': latest_analysis.get('annual_cash_flow', 0),
                'cash_on_cash_return': latest_analysis.get('cash_on_cash_return', 0)
            },
            'actual': actual_kpis
        })
    except Exception as e:
        logger.error(f"Error in get_kpi_data: {str(e)}\nAnalyses: {analyses if 'analyses' in locals() else 'Not found'}")
        return jsonify({'error': str(e)}), 500
    
@analyses_bp.route('/mao-calculator')
@login_required
def mao_calculator():
    """Render the MAO calculator page"""
    return render_template('analyses/mao_calculator.html', body_class='mao-calculator-page')

@analyses_bp.route('/api/properties')
@login_required
def get_properties():
    try:
        properties = get_properties_for_user(
            current_user.id,
            current_user.name
        )
        return jsonify({
            'success': True,
            'properties': properties
        })
    except Exception as e:
        logger.error(f"Error fetching properties: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500