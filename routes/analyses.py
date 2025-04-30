from flask import Blueprint, render_template, request, jsonify, redirect, url_for, send_file, current_app, session
from flask_login import login_required, current_user
from services.analysis_service import AnalysisService
from utils.flash import flash_message
import logging
import json
import traceback
from utils.comps_handler import RentcastAPIError

analyses_bp = Blueprint('analyses', __name__)
logger = logging.getLogger(__name__)
analysis_service = AnalysisService()

@analyses_bp.route('/run_comps/<analysis_id>', methods=['POST'])
@login_required
def run_property_comps(analysis_id):
    try:
        # Get user ID from current user
        user_id = current_user.get_id()
        
        # Get max runs from config with default fallback
        max_runs = current_app.config.get('MAX_COMP_RUNS_PER_SESSION', 3)
        
        # Check session run count
        session_key = f'comps_run_count_{analysis_id}'
        run_count = session.get(session_key, 0)
        
        # Log current state
        current_app.logger.debug(f"Current run count for {analysis_id}: {run_count}")
        current_app.logger.debug(f"Max runs allowed: {max_runs}")
        
        if run_count >= max_runs:
            return jsonify({
                'success': False,
                'message': f'Maximum comp runs ({max_runs}) reached for this session'
            }), 429  # Too Many Requests
        
        # Run comps using analysis service
        analysis_service = AnalysisService()
        updated_analysis = analysis_service.run_property_comps(analysis_id, user_id)
        
        if not updated_analysis:
            return jsonify({
                'success': False,
                'message': 'Analysis not found'
            }), 404
            
        # Increment run count
        session[session_key] = run_count + 1
        current_app.logger.debug(f"Updated run count to: {run_count + 1}")
            
        return jsonify({
            'success': True,
            'analysis': updated_analysis,
            'message': 'Comps updated successfully'
        })
        
    except RentcastAPIError as e:
        error_msg = str(e)
        # Make user-friendly error messages
        if "Failed to fetch property comps" in error_msg:
            user_msg = "Unable to find comparable properties for this address. Please verify the address is correct."
        elif "Maximum comp runs" in error_msg:
            user_msg = error_msg  # This is already user-friendly
        elif "'NoneType' object has no attribute" in error_msg:
            user_msg = "Unable to process property comps. The property address may not be recognized."
        else:
            user_msg = f"Error running comps: {error_msg}"
            
        current_app.logger.error(f'RentcastAPIError: {str(e)}')
        return jsonify({
            'success': False,
            'message': user_msg
        }), 500
    except Exception as e:
        current_app.logger.error(f'Error in run_property_comps: {str(e)}')
        current_app.logger.exception('Full traceback:')
        return jsonify({
            'success': False,
            'message': 'Error running comps: The property address may not be recognized by our data provider.'
        }), 500

@analyses_bp.route('/create_analysis', methods=['GET', 'POST']) 
@login_required
def create_analysis():
    """Handle both GET and POST requests for analysis creation."""
    if request.method == 'POST':
        try:
            analysis_data = request.get_json()
            if not analysis_data:
                return jsonify({"success": False, "message": "No analysis data provided"}), 400

            # Add detailed logging for Multi-Family analysis
            if analysis_data.get('analysis_type') == 'Multi-Family':
                logger.debug("=== Processing Multi-Family Analysis ===")
                logger.debug(f"Analysis data keys: {list(analysis_data.keys())}")
                logger.debug(f"Unit types present: {'unit_types' in analysis_data}")
                if 'unit_types' in analysis_data:
                    logger.debug(f"Unit types type: {type(analysis_data['unit_types'])}")
                    logger.debug(f"Unit types data: {analysis_data['unit_types']}")
                    try:
                        # Verify unit types can be parsed
                        parsed_units = json.loads(analysis_data['unit_types']) if isinstance(analysis_data['unit_types'], str) else None
                        logger.debug(f"Parsed unit types: {parsed_units}")
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing unit types JSON: {e}")
                        return jsonify({
                            "success": False,
                            "message": f"Invalid unit types data format: {str(e)}"
                        }), 400
                else:
                    logger.error("No unit_types found in Multi-Family analysis data")

            # Get the analysis results
            results = analysis_service.create_analysis(analysis_data, current_user.id)
            
            # Extract the analysis data from results
            analysis_data = results.get('analysis') if isinstance(results, dict) else results
            
            return jsonify({
                "success": True,
                "message": "Analysis created successfully",
                "analysis": analysis_data  # Return just the analysis data
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
    editing = False  # Add explicit editing flag
    
    if analysis_id:
        try:
            existing_analysis = analysis_service.get_analysis(analysis_id, current_user.id)
            if existing_analysis:
                editing = True  # Set editing flag if we found an analysis
            else:
                flash_message('Analysis not found', 'error')
                return redirect(url_for('analyses.view_edit_analysis'))
        except Exception as e:
            logger.error(f"Error fetching analysis: {str(e)}")
            logger.error(traceback.format_exc())
            flash_message('Error loading analysis', 'error')
            return redirect(url_for('analyses.view_edit_analysis'))

    return render_template(
        'analyses/create_analysis.html',
        analysis=existing_analysis,
        editing_analysis=editing,  # Pass explicit editing flag to template
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
    """View/edit analysis list page with mobile-friendly loading"""
    try:
        # Handle pagination
        try:
            page = max(1, int(request.args.get('page', 1)))
        except (TypeError, ValueError):
            page = 1
            
        analyses_per_page = 10
        
        # Get analyses for the current page
        analyses, total_pages = analysis_service.get_analyses_for_user(
            current_user.id, 
            page, 
            analyses_per_page
        )
        
        # Calculate page range for pagination
        start_page = max(1, page - 2)
        end_page = min(total_pages, page + 2)
        page_range = list(range(start_page, end_page + 1))
        
        # For AJAX requests (mobile loading), return only the analyses cards
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render_template(
                'analyses/_analysis_cards.html',  # Create this partial template
                analyses=analyses,
                current_page=page,
                total_pages=total_pages,
                page_range=page_range
            )
            
        # For regular requests, return the full page
        return render_template(
            'analyses/view_edit_analysis.html',
            analyses=analyses,
            current_page=page,
            total_pages=total_pages,
            page_range=page_range,
            body_class='view-edit-analysis-page'
        )
            
    except Exception as e:
        logger.error(f"Error in view_edit_analysis: {str(e)}")
        logger.error(traceback.format_exc())
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

@analyses_bp.route('/generate_pdf/<analysis_id>')
def generate_pdf(analysis_id):
    """Generate and send PDF report for an analysis."""
    try:
        # Get user ID from current_user (Flask-Login)
        user_id = current_user.id
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401

        # First, get the analysis data
        analysis_data = analysis_service.get_analysis(analysis_id, user_id)
        if not analysis_data:
            return jsonify({'error': 'Analysis not found'}), 404

        # Generate PDF using the report generator directly
        try:
            # Import at route level to avoid circular imports
            from services.report_generator import generate_report
            buffer = generate_report(analysis_data)
        except Exception as e:
            current_app.logger.error(f"PDF Generation error: {str(e)}")
            return jsonify({'error': f'Error generating PDF: {str(e)}'}), 500
        
        # Return the PDF file
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'analysis_{analysis_id}.pdf'
        )
        
    except Exception as e:
        current_app.logger.error(f"Route error: {str(e)}")
        return jsonify({'error': f'Error processing request: {str(e)}'}), 500
    
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