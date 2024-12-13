from flask import Blueprint, render_template, request, jsonify, redirect, url_for, send_file, current_app
from flask_login import login_required, current_user
from services.analysis_service import AnalysisService
from utils.flash import flash_message
import logging
import traceback
import os

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
        editing_analysis=analysis_id is not None,
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
        # Add debug logging at each step
        analyses_dir = current_app.config['ANALYSES_DIR']
        logger.info(f"1. Using analyses directory: {analyses_dir}")
        logger.info(f"2. Current user ID: {current_user.id}")
        
        try:
            page = max(1, int(request.args.get('page', 1)))
            logger.info(f"3. Page number: {page}")
        except (TypeError, ValueError) as e:
            logger.warning(f"Invalid page parameter: {str(e)}")
            page = 1
        
        analyses_per_page = 10
        logger.info(f"4. Files in analyses directory: {os.listdir(analyses_dir)}")
            
        try:
            analyses, total_pages = analysis_service.get_analyses_for_user(
                current_user.id, 
                page, 
                analyses_per_page
            )
            
            logger.info(f"5. Found {len(analyses) if analyses else 0} analyses for user")
            if analyses:
                logger.info(f"6. First analysis: {analyses[0]['analysis_name']}")
            
            start_page = max(1, page - 2)
            end_page = min(total_pages, page + 2)
            page_range = list(range(start_page, end_page + 1))
            
            return render_template(
                'analyses/view_edit_analysis.html', 
                analyses=analyses, 
                current_page=page, 
                total_pages=total_pages,
                page_range=page_range,
                body_class='view-edit-analysis-page'
            )
            
        except Exception as e:
            logger.error(f"Error retrieving analyses from service: {str(e)}")
            logger.error(traceback.format_exc())
            raise
        
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

@analyses_bp.route('/generate_pdf/<analysis_id>')
def generate_pdf(analysis_id):
    """Generate and send PDF report for an analysis."""
    try:
        # Get user ID from current_user (Flask-Login)
        user_id = current_user.id
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401

        # Generate PDF
        buffer = analysis_service.generate_pdf_report(analysis_id, user_id)
        
        # Return the PDF file
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'analysis_{analysis_id}.pdf'
        )
        
    except Exception as e:
        current_app.logger.error(f"Error generating PDF: {str(e)}")
        return jsonify({'error': f'Error generating PDF: {str(e)}'}), 500
    
@analyses_bp.route('/mao-calculator')
@login_required
def mao_calculator():
    return render_template('analyses/mao_calculator.html')

@analyses_bp.route('/delete_analysis/<analysis_id>', methods=['DELETE'])
@login_required
def delete_analysis(analysis_id: str):
    """Delete an analysis by ID"""
    try:
        # Attempt to delete the analysis
        success = analysis_service.delete_analysis(analysis_id, current_user.id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Analysis deleted successfully"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Analysis not found"
            }), 404
            
    except Exception as e:
        logger.error(f"Error deleting analysis: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error deleting analysis: {str(e)}"
        }), 500