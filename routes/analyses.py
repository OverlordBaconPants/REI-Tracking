from flask import Blueprint, render_template, request, jsonify, redirect, url_for, send_file
from flask_login import login_required, current_user
from services.analysis_service import AnalysisService
from utils.flash import flash_message
import logging
from typing import Dict, Any
import traceback

analyses_bp = Blueprint('analyses', __name__)
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
    """Handle updates to existing analyses."""
    try:
        analysis_data = request.get_json()
        if not analysis_data:
            return jsonify({"success": False, "message": "No analysis data provided"}), 400

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
        page = request.args.get('page', 1, type=int)
        analyses_per_page = 10
        
        analyses, total_pages = analysis_service.get_analyses_for_user(
            current_user.id, 
            page, 
            analyses_per_page
        )
        
        return render_template(
            'analyses/view_edit_analysis.html', 
            analyses=analyses, 
            current_page=page, 
            total_pages=total_pages
        )
    except Exception as e:
        logger.error(f"Error in view_edit_analysis: {str(e)}")
        flash_message('Error loading analyses', 'error')
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
            as_attachment=True,
            download_name=f"analysis_{analysis_id}_report.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        return jsonify({'error': f'Error generating PDF: {str(e)}'}), 500