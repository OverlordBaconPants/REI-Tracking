"""
Analysis routes module for the REI-Tracker application.

This module provides routes for analysis operations, including CRUD operations
and specialized analysis features.
"""

from typing import Dict, Any, List, Optional
import json
from flask import Blueprint, request, jsonify, current_app, session
from flask_login import login_required, current_user

from src.models.analysis import Analysis, UnitType, CompsData
from src.repositories.analysis_repository import AnalysisRepository
from src.services.validation_service import AnalysisValidator
from src.services.rentcast_service import RentcastService
from src.utils.calculations.analysis import create_analysis as create_analysis_calculator
from src.utils.logging_utils import get_logger

# Set up logger
logger = get_logger(__name__)

# Create blueprint
analysis_bp = Blueprint('analysis', __name__, url_prefix='/api/analysis')

# Initialize repository
analysis_repository = AnalysisRepository()

# Initialize validator
analysis_validator = AnalysisValidator(Analysis)

# Initialize RentcastService
rentcast_service = RentcastService()


@analysis_bp.route('/', methods=['GET'])
@login_required
def get_analyses():
    """
    Get all analyses for the current user.
    
    Returns:
        JSON response with analyses
    """
    try:
        # Get page and per_page parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Get analyses for the current user with pagination
        analyses, total_pages = analysis_repository.get_by_user_paginated(
            current_user.id, page, per_page
        )
        
        # Convert to dictionaries
        analyses_data = [analysis.dict() for analysis in analyses]
        
        return jsonify({
            'success': True,
            'analyses': analyses_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages,
                'total_items': len(analyses_data)
            }
        })
    except Exception as e:
        logger.error(f"Error getting analyses: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error getting analyses: {str(e)}"
        }), 500


@analysis_bp.route('/<analysis_id>', methods=['GET'])
@login_required
def get_analysis(analysis_id: str):
    """
    Get a specific analysis by ID.
    
    Args:
        analysis_id: ID of the analysis to get
        
    Returns:
        JSON response with the analysis
    """
    try:
        # Get the analysis
        analysis = analysis_repository.get_by_id(analysis_id)
        
        # Check if the analysis exists
        if not analysis:
            return jsonify({
                'success': False,
                'message': 'Analysis not found'
            }), 404
        
        # Check if the user has access to the analysis
        if analysis.user_id != current_user.id:
            return jsonify({
                'success': False,
                'message': 'You do not have access to this analysis'
            }), 403
        
        # Get calculated metrics
        calculator = create_analysis_calculator(analysis.dict())
        result = calculator.analyze()
        
        # Convert to dictionary
        analysis_data = analysis.dict()
        
        # Add calculated metrics
        analysis_data['calculated_metrics'] = {
            'monthly_cash_flow': float(result.monthly_cash_flow),
            'annual_cash_flow': float(result.annual_cash_flow),
            'cash_on_cash_return': float(result.cash_on_cash_return),
            'cap_rate': float(result.cap_rate),
            'roi': float(result.roi),
            'total_investment': float(result.total_investment),
            'monthly_income': float(result.monthly_income),
            'monthly_expenses': float(result.monthly_expenses),
            'debt_service_coverage_ratio': result.debt_service_coverage_ratio,
            'expense_ratio': float(result.expense_ratio),
            'gross_rent_multiplier': result.gross_rent_multiplier,
            'price_per_unit': float(result.price_per_unit) if analysis.analysis_type == 'MultiFamily' else None,
            'breakeven_occupancy': float(result.breakeven_occupancy)
        }
        
        return jsonify({
            'success': True,
            'analysis': analysis_data
        })
    except Exception as e:
        logger.error(f"Error getting analysis: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error getting analysis: {str(e)}"
        }), 500


@analysis_bp.route('/', methods=['POST'])
@login_required
def create_analysis():
    """
    Create a new analysis.
    
    Returns:
        JSON response with the created analysis
    """
    try:
        # Get the request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Add user ID to the data
        data['user_id'] = current_user.id
        
        # Validate the data
        validation_result = analysis_validator.validate(data)
        if not validation_result.is_valid:
            return jsonify({
                'success': False,
                'message': 'Validation failed',
                'errors': validation_result.errors
            }), 400
        
        # Create the analysis
        analysis = validation_result.data
        created_analysis = analysis_repository.create(analysis)
        
        # Get calculated metrics
        calculator = create_analysis_calculator(created_analysis.dict())
        result = calculator.analyze()
        
        # Convert to dictionary
        analysis_data = created_analysis.dict()
        
        # Add calculated metrics
        analysis_data['calculated_metrics'] = {
            'monthly_cash_flow': float(result.monthly_cash_flow),
            'annual_cash_flow': float(result.annual_cash_flow),
            'cash_on_cash_return': float(result.cash_on_cash_return),
            'cap_rate': float(result.cap_rate),
            'roi': float(result.roi),
            'total_investment': float(result.total_investment),
            'monthly_income': float(result.monthly_income),
            'monthly_expenses': float(result.monthly_expenses),
            'debt_service_coverage_ratio': result.debt_service_coverage_ratio,
            'expense_ratio': float(result.expense_ratio),
            'gross_rent_multiplier': result.gross_rent_multiplier,
            'price_per_unit': float(result.price_per_unit) if created_analysis.analysis_type == 'MultiFamily' else None,
            'breakeven_occupancy': float(result.breakeven_occupancy)
        }
        
        return jsonify({
            'success': True,
            'message': 'Analysis created successfully',
            'analysis': analysis_data
        })
    except Exception as e:
        logger.error(f"Error creating analysis: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error creating analysis: {str(e)}"
        }), 500


@analysis_bp.route('/<analysis_id>', methods=['PUT'])
@login_required
def update_analysis(analysis_id: str):
    """
    Update an existing analysis.
    
    Args:
        analysis_id: ID of the analysis to update
        
    Returns:
        JSON response with the updated analysis
    """
    try:
        # Get the request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Get the existing analysis
        existing_analysis = analysis_repository.get_by_id(analysis_id)
        if not existing_analysis:
            return jsonify({
                'success': False,
                'message': 'Analysis not found'
            }), 404
        
        # Check if the user has access to the analysis
        if existing_analysis.user_id != current_user.id:
            return jsonify({
                'success': False,
                'message': 'You do not have access to this analysis'
            }), 403
        
        # Ensure ID and user_id are preserved
        data['id'] = analysis_id
        data['user_id'] = current_user.id
        
        # Preserve created_at timestamp
        data['created_at'] = existing_analysis.created_at
        
        # Validate the data
        validation_result = analysis_validator.validate(data)
        if not validation_result.is_valid:
            return jsonify({
                'success': False,
                'message': 'Validation failed',
                'errors': validation_result.errors
            }), 400
        
        # Update the analysis
        analysis = validation_result.data
        updated_analysis = analysis_repository.update(analysis)
        
        # Get calculated metrics
        calculator = create_analysis_calculator(updated_analysis.dict())
        result = calculator.analyze()
        
        # Convert to dictionary
        analysis_data = updated_analysis.dict()
        
        # Add calculated metrics
        analysis_data['calculated_metrics'] = {
            'monthly_cash_flow': float(result.monthly_cash_flow),
            'annual_cash_flow': float(result.annual_cash_flow),
            'cash_on_cash_return': float(result.cash_on_cash_return),
            'cap_rate': float(result.cap_rate),
            'roi': float(result.roi),
            'total_investment': float(result.total_investment),
            'monthly_income': float(result.monthly_income),
            'monthly_expenses': float(result.monthly_expenses),
            'debt_service_coverage_ratio': result.debt_service_coverage_ratio,
            'expense_ratio': float(result.expense_ratio),
            'gross_rent_multiplier': result.gross_rent_multiplier,
            'price_per_unit': float(result.price_per_unit) if updated_analysis.analysis_type == 'MultiFamily' else None,
            'breakeven_occupancy': float(result.breakeven_occupancy)
        }
        
        return jsonify({
            'success': True,
            'message': 'Analysis updated successfully',
            'analysis': analysis_data
        })
    except Exception as e:
        logger.error(f"Error updating analysis: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error updating analysis: {str(e)}"
        }), 500


@analysis_bp.route('/<analysis_id>', methods=['DELETE'])
@login_required
def delete_analysis(analysis_id: str):
    """
    Delete an analysis.
    
    Args:
        analysis_id: ID of the analysis to delete
        
    Returns:
        JSON response with success status
    """
    try:
        # Get the existing analysis
        existing_analysis = analysis_repository.get_by_id(analysis_id)
        if not existing_analysis:
            return jsonify({
                'success': False,
                'message': 'Analysis not found'
            }), 404
        
        # Check if the user has access to the analysis
        if existing_analysis.user_id != current_user.id:
            return jsonify({
                'success': False,
                'message': 'You do not have access to this analysis'
            }), 403
        
        # Delete the analysis
        analysis_repository.delete(analysis_id)
        
        return jsonify({
            'success': True,
            'message': 'Analysis deleted successfully'
        })
    except Exception as e:
        logger.error(f"Error deleting analysis: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error deleting analysis: {str(e)}"
        }), 500


@analysis_bp.route('/types/<analysis_type>', methods=['GET'])
@login_required
def get_analyses_by_type(analysis_type: str):
    """
    Get analyses by type for the current user.
    
    Args:
        analysis_type: Type of analyses to get
        
    Returns:
        JSON response with analyses of the specified type
    """
    try:
        # Validate analysis type
        valid_types = ["LTR", "BRRRR", "LeaseOption", "MultiFamily", "PadSplit"]
        if analysis_type not in valid_types:
            return jsonify({
                'success': False,
                'message': f"Invalid analysis type. Must be one of: {', '.join(valid_types)}"
            }), 400
        
        # Get analyses by type for the current user
        analyses = analysis_repository.get_by_user_and_type(current_user.id, analysis_type)
        
        # Convert to dictionaries
        analyses_data = [analysis.dict() for analysis in analyses]
        
        return jsonify({
            'success': True,
            'analyses': analyses_data
        })
    except Exception as e:
        logger.error(f"Error getting analyses by type: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error getting analyses by type: {str(e)}"
        }), 500


@analysis_bp.route('/run_comps/<analysis_id>', methods=['POST'])
@login_required
def run_property_comps(analysis_id: str):
    """
    Run property comps for an analysis.
    
    Args:
        analysis_id: ID of the analysis to run comps for
        
    Returns:
        JSON response with the updated analysis
    """
    try:
        # Get the analysis
        analysis = analysis_repository.get_by_id(analysis_id)
        
        # Check if the analysis exists
        if not analysis:
            return jsonify({
                'success': False,
                'message': 'Analysis not found'
            }), 404
        
        # Check if the user has access to the analysis
        if analysis.user_id != current_user.id:
            return jsonify({
                'success': False,
                'message': 'You do not have access to this analysis'
            }), 403
        
        # Get max runs from config with default fallback
        max_runs = current_app.config.get('MAX_COMP_RUNS_PER_SESSION', 3)
        
        # Check session run count
        session_key = f'comps_run_count_{analysis_id}'
        run_count = session.get(session_key, 0)
        
        logger.debug(f"Current run count for {analysis_id}: {run_count}")
        logger.debug(f"Max runs allowed: {max_runs}")
        
        if run_count >= max_runs:
            return jsonify({
                'success': False,
                'message': f'Maximum comp runs ({max_runs}) reached for this session'
            }), 429  # Too Many Requests
        
        # Get property details from analysis
        address = analysis.address
        bedrooms = analysis.bedrooms or 3  # Default to 3 bedrooms if not specified
        bathrooms = analysis.bathrooms or 2  # Default to 2 bathrooms if not specified
        square_feet = analysis.square_footage or 1500  # Default to 1500 sq ft if not specified
        year_built = analysis.year_built or 2000  # Default to 2000 if not specified
        
        # Get property comparables
        property_comps = rentcast_service.get_property_comparables(
            address=address,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            square_feet=square_feet,
            radius_miles=1.0,
            limit=10
        )
        
        # Get rental estimate
        rental_estimate = rentcast_service.get_rental_estimate(
            address=address,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            square_feet=square_feet
        )
        
        # Get property value estimate
        property_value = rentcast_service.get_property_value_estimate(
            address=address,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            square_feet=square_feet,
            year_built=year_built
        )
        
        # Format comparables for analysis
        formatted_comps = rentcast_service.format_comparables_for_analysis(property_comps)
        
        # Update run count in formatted comps
        formatted_comps['run_count'] = run_count + 1
        
        # Add rental estimate data
        if rental_estimate:
            formatted_comps['rental_comps'] = {
                'estimated_rent': rental_estimate.get('rent', 0),
                'rent_range_low': rental_estimate.get('rentRangeLow', 0),
                'rent_range_high': rental_estimate.get('rentRangeHigh', 0),
                'comparable_rentals': rental_estimate.get('comparables', []),
                'confidence_score': rental_estimate.get('confidenceScore', 0)
            }
        
        # Create CompsData object
        comps_data = CompsData(
            last_run=formatted_comps['last_run'],
            run_count=formatted_comps['run_count'],
            estimated_value=formatted_comps['estimated_value'],
            value_range_low=formatted_comps['value_range_low'],
            value_range_high=formatted_comps['value_range_high'],
            comparables=formatted_comps['comparables']
        )
        
        # Update analysis with comps data
        analysis.comps_data = comps_data
        
        # Save updated analysis
        updated_analysis = analysis_repository.update(analysis)
        
        # Increment run count in session
        session[session_key] = run_count + 1
        
        # Return updated analysis
        return jsonify({
            'success': True,
            'message': 'Comps updated successfully',
            'analysis': updated_analysis.dict()
        })
    except Exception as e:
        logger.error(f"Error running property comps: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error running property comps: {str(e)}"
        }), 500

@analysis_bp.route('/calculate', methods=['POST'])
@login_required
def calculate_analysis():
    """
    Calculate analysis metrics without saving.
    
    Returns:
        JSON response with calculated metrics
    """
    try:
        # Get the request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Add user ID to the data
        data['user_id'] = current_user.id
        
        # Validate the data
        validation_result = analysis_validator.validate(data)
        if not validation_result.is_valid:
            return jsonify({
                'success': False,
                'message': 'Validation failed',
                'errors': validation_result.errors
            }), 400
        
        # Create analysis calculator
        calculator = create_analysis_calculator(validation_result.data.dict())
        
        # Calculate metrics
        result = calculator.analyze()
        
        # Convert to dictionary
        metrics = {
            'monthly_cash_flow': float(result.monthly_cash_flow),
            'annual_cash_flow': float(result.annual_cash_flow),
            'cash_on_cash_return': float(result.cash_on_cash_return),
            'cap_rate': float(result.cap_rate),
            'roi': float(result.roi),
            'total_investment': float(result.total_investment),
            'monthly_income': float(result.monthly_income),
            'monthly_expenses': float(result.monthly_expenses),
            'debt_service_coverage_ratio': result.debt_service_coverage_ratio,
            'expense_ratio': float(result.expense_ratio),
            'gross_rent_multiplier': result.gross_rent_multiplier,
            'price_per_unit': float(result.price_per_unit) if validation_result.data.analysis_type == 'MultiFamily' else None,
            'breakeven_occupancy': float(result.breakeven_occupancy)
        }
        
        return jsonify({
            'success': True,
            'metrics': metrics
        })
    except Exception as e:
        logger.error(f"Error calculating analysis: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error calculating analysis: {str(e)}"
        }), 500
