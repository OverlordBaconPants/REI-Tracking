from datetime import datetime
import logging
import os
import uuid
import json
import time
from typing import Dict, List, Optional, Union, Any, Tuple
import traceback
from io import BytesIO

from flask import current_app, session
from services.report_generator import generate_report
from utils.json_handler import read_json, write_json
from services.analysis_calculations import create_analysis
from utils.comps_handler import fetch_property_comps, update_analysis_comps, RentcastAPIError


logger = logging.getLogger(__name__)


class AnalysisService:
    """Service for handling property investment analyses with flat data structure."""

    # Schema moved to a separate file or class constant to reduce clutter
    from .analysis_schema import ANALYSIS_SCHEMA

    def __init__(self):
        """Initialize the AnalysisService."""
        self.logger = logger
        
        # Mobile-specific configuration
        self.mobile_config = {
            'max_image_size': 800,  # Max dimension for mobile images
            'pagination_size': 10,   # Items per page on mobile
            'cache_duration': 300    # Cache duration in seconds
        }

    def run_property_comps(self, analysis_id: str, user_id: str) -> Optional[Dict]:
        """
        Run property comps for an analysis and update it with the results.
        
        Args:
            analysis_id: ID of the analysis
            user_id: ID of the user
            
        Returns:
            Updated analysis with comps data or None if not found
        """
        try:
            # Get the full analysis data
            analysis = self.get_analysis(analysis_id, user_id)
            if not analysis:
                logger.error(f"Analysis not found for ID: {analysis_id}")
                return None
                
            # Extract property details
            address = analysis.get('address')
            property_type = analysis.get('property_type', 'Single Family')
            bedrooms = float(analysis.get('bedrooms', 0))
            bathrooms = float(analysis.get('bathrooms', 0))
            square_footage = float(analysis.get('square_footage', 0))
            
            # For multi-family, adjust property type
            if analysis.get('analysis_type') == 'Multi-Family':
                property_type = 'Multi-Family'
            
            # Validate required parameters
            if not address:
                logger.error("Missing address in analysis")
                raise ValueError("Property address is required to fetch comps")
            
            # Get property comps data
            from utils.comps_handler import fetch_property_comps, fetch_rental_comps, update_analysis_comps
            from flask import current_app, session
            
            try:
                comps_data = fetch_property_comps(
                    current_app.config,
                    address,
                    property_type,
                    bedrooms,
                    bathrooms,
                    square_footage,
                    analysis_data=analysis  # Pass full analysis data for MAO calculation
                )
                
                # Verify comps_data is valid and has required fields
                if not comps_data:
                    raise ValueError("No property comps data returned from API")
                    
                # Check for required fields
                required_fields = ['price', 'priceRangeLow', 'priceRangeHigh', 'comparables', 'last_run']
                missing_fields = [field for field in required_fields if field not in comps_data]
                if missing_fields:
                    logger.warning(f"Comps data missing fields: {missing_fields}")
                    # Fill in missing fields with defaults
                    for field in missing_fields:
                        if field == 'comparables':
                            comps_data[field] = []
                        elif field == 'last_run':
                            comps_data[field] = datetime.utcnow().isoformat()
                        else:
                            comps_data[field] = 0
            except RentcastAPIError as e:
                logger.error(f"RentCast API error: {str(e)}")
                raise ValueError(f"Could not find property comps: {str(e)}")
            
            # Get rental comps data
            rental_comps = None
            try:
                logger.debug("Fetching rental comps")
                rental_comps = fetch_rental_comps(
                    current_app.config,
                    address,
                    bedrooms,
                    bathrooms,
                    square_footage,
                    property_type
                )
                logger.debug(f"Rental comps fetched successfully: {rental_comps is not None}")
                
                # Validate rental comps data
                if rental_comps and 'estimated_rent' not in rental_comps:
                    logger.warning("Rental comps missing estimated_rent field")
                    rental_comps['estimated_rent'] = 0
                    
            except Exception as e:
                logger.error(f"Error fetching rental comps: {str(e)}")
                logger.exception("Full traceback:")
                # Continue with property comps even if rental comps fail
            
            # Update the run count from session
            session_key = f'comps_run_count_{address}'
            run_count = session.get(session_key, 0)
            
            # Make sure analysis['comps_data'] is initialized or reset if None
            if 'comps_data' not in analysis or analysis['comps_data'] is None:
                analysis['comps_data'] = {}
                
            # Add comps data to analysis with better error handling
            try:
                updated_analysis = update_analysis_comps(analysis, comps_data, rental_comps, run_count)
            except Exception as e:
                logger.error(f"Error in update_analysis_comps: {str(e)}")
                # Fallback: manually update the analysis instead of using update_analysis_comps
                analysis['comps_data'] = {
                    'last_run': comps_data.get('last_run', datetime.utcnow().isoformat()),
                    'run_count': run_count,
                    'estimated_value': comps_data.get('price', 0),
                    'value_range_low': comps_data.get('priceRangeLow', 0),
                    'value_range_high': comps_data.get('priceRangeHigh', 0),
                    'comparables': comps_data.get('comparables', [])
                }
                
                # Add MAO data if available
                if 'mao' in comps_data:
                    analysis['comps_data']['mao'] = comps_data['mao']
                
                # Add rental data if available
                if rental_comps:
                    analysis['comps_data']['rental_comps'] = rental_comps
                    
                updated_analysis = analysis
            
            # Save updated analysis to database
            self._save_analysis(updated_analysis, user_id)
            
            return updated_analysis
                
        except ValueError as e:
            # Provide more specific error message for common issues
            logger.error(f"Value error in run_property_comps: {str(e)}")
            raise RentcastAPIError(f"Could not find property comps: {str(e)}")
        except Exception as e:
            logger.error(f"Error in run_property_comps: {str(e)}")
            logger.exception("Full traceback:")
            raise
    
    def normalize_data(self, data: Dict, is_mobile: bool = False) -> Dict:
        """
        Normalize input data according to schema types.
        
        Args:
            data: Input data dictionary
            is_mobile: Whether request is from mobile client
            
        Returns:
            Normalized data dictionary
        """
        try:
            logger.debug("=== Starting Data Normalization ===")
            normalized = {}
            
            # First check if balloon payments are enabled
            has_balloon = data.get('has_balloon_payment', False)
            
            # Handle lease option fields
            lease_fields = {
                'option_consideration_fee': 0,
                'option_term_months': 0,
                'strike_price': 0,
                'monthly_rent_credit_percentage': 0.0,
                'rent_credit_cap': 0
            }

            # Process each field according to schema
            for field, field_def in self.ANALYSIS_SCHEMA.items():
                field_type = field_def['type']
                value = data.get(field)
                
                # Handle lease option fields
                if field in lease_fields and data.get('analysis_type') != 'Lease Option':
                    normalized[field] = lease_fields[field]
                    continue
                
                # Handle balloon payment fields
                if field.startswith('balloon_') and not has_balloon:
                    if field == 'balloon_due_date':
                        normalized[field] = None
                    else:
                        normalized[field] = 0
                    continue
                    
                # Skip empty mobile-optional fields on mobile
                if is_mobile and not value and field in getattr(self, 'MOBILE_OPTIONAL_FIELDS', []):
                    continue
                    
                # Convert value based on type
                if field_type == 'integer':
                    normalized[field] = self._convert_to_int(value)
                    
                elif field_type == 'float':
                    normalized[field] = self._convert_to_float(value)
                    
                elif field_type == 'string':
                    normalized[field] = str(value) if value is not None else ''
                        
                elif field_type == 'boolean':
                    if field == 'has_balloon_payment':
                        normalized[field] = bool(value)
                    else:
                        # Handle other boolean fields
                        normalized[field] = self._convert_to_bool(value)
                
                # Handle special formats
                if field_def.get('format') == 'uuid' and not value:
                    normalized[field] = str(uuid.uuid4())
                    
                elif field_def.get('format') == 'datetime' and not value:
                    normalized[field] = datetime.now().isoformat()
                    
                elif field_def.get('format') == 'date' and value:
                    try:
                        if has_balloon or not field.startswith('balloon_'):
                            parsed_date = datetime.strptime(value, "%Y-%m-%d")
                            normalized[field] = parsed_date.strftime("%Y-%m-%d")
                        else:
                            normalized[field] = None
                    except ValueError:
                        normalized[field] = None
                        logger.warning(f"Invalid date format for field {field}: {value}")
            
            logger.debug("=== Data Normalization Complete ===")
            return normalized
                
        except Exception as e:
            logger.error(f"Error normalizing data: {str(e)}")
            logger.error(traceback.format_exc())
            raise ValueError(f"Data normalization failed: {str(e)}")

    def _convert_to_bool(self, value: Any) -> bool:
        """Convert value to boolean, handling various formats."""
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value)

    def _optimize_metrics_for_mobile(self, metrics: Dict) -> Dict:
        """
        Optimize calculated metrics for mobile display.
        
        Args:
            metrics: Original metrics dictionary
            
        Returns:
            Optimized metrics for mobile
        """
        # Define precision for different metric types
        precision_map = {
            'percentage': 1,  # One decimal for percentages
            'currency': 0,    # No decimals for currency values
            'ratio': 2        # Two decimals for ratios
        }
        
        # Metric type mapping
        metric_types = {
            'cash_on_cash_return': 'percentage',
            'roi': 'percentage',
            'monthly_cash_flow': 'currency',
            'annual_cash_flow': 'currency',
            'vacancy_rate': 'percentage',
            'debt_service_ratio': 'ratio'
            # Add other metrics as needed
        }
        
        return {
            key: round(float(value), precision_map.get(metric_types.get(key, 'ratio'), 2))
            if isinstance(value, (int, float)) and value is not None else value
            for key, value in metrics.items()
        }
    
    def _get_value(self, data: Dict, field: str) -> Any:
        """
        Safely get a value from the data dict, handling various formats.
        
        Args:
            data: The data dictionary to get the value from
            field: The field name to get
            
        Returns:
            The value or None if not found
        """
        if field not in data:
            return None
            
        value = data[field]
            
        # Convert empty strings to None
        if value == '':
            return None
            
        # If it's already None, return it
        if value is None:
            return None
            
        # Clean up currency values
        if isinstance(value, str):
            value = value.replace('$', '').replace(',', '').strip()
            # Remove % symbol if present
            if value.endswith('%'):
                value = value[:-1]
                
        return value

    def validate_analysis_data(self, data: Dict) -> None:
        """
        Validate analysis data against schema.
        
        Args:
            data: Analysis data to validate
            
        Raises:
            ValueError: If validation fails
        """
        try:
            logger.debug("Starting analysis data validation")
            
            # Validate required base fields
            required_fields = {
                'analysis_type': str,
                'analysis_name': str
            }

            # Check for monthly rent requirement
            self._validate_rent_data(data)
            
            # Validate required fields
            self._validate_required_fields(data, required_fields)
            
            # Validate field types for non-required fields
            for field, value in data.items():
                if field in self.ANALYSIS_SCHEMA and value is not None:
                    field_def = self.ANALYSIS_SCHEMA[field]
                    # Skip validation for optional fields that are empty
                    if field_def.get('optional') and (value is None or value == ''):
                        continue
                    self._validate_field_type(field, value)
                        
            # Validate analysis-type specific data
            if data.get('analysis_type') == 'Lease Option':
                self._validate_lease_option(data)

            logger.debug("Analysis data validation complete")
            
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected validation error: {str(e)}")
            logger.error(traceback.format_exc())
            raise ValueError(f"Validation failed: {str(e)}")

    def _validate_rent_data(self, data: Dict) -> None:
        """Validate rent data based on analysis type."""
        if data.get('analysis_type') != 'Multi-Family':
            if 'monthly_rent' not in data or \
            not isinstance(data['monthly_rent'], (int, float)) or \
            data['monthly_rent'] <= 0:
                raise ValueError("Invalid monthly_rent: must be a positive number")
        else:
            # For Multi-Family, validate unit_types instead
            if 'unit_types' not in data:
                raise ValueError("Missing unit_types for Multi-Family analysis")
            try:
                unit_types = json.loads(data['unit_types'])
                if not isinstance(unit_types, list) or not unit_types:
                    raise ValueError("unit_types must be a non-empty array")
                    
                # Validate each unit type has required rent
                for unit in unit_types:
                    if 'rent' not in unit or \
                    not isinstance(unit['rent'], (int, float)) or \
                    unit['rent'] <= 0:
                        raise ValueError("Each unit type must have a positive rent value")
            except json.JSONDecodeError:
                raise ValueError("Invalid unit_types format")

    def _validate_required_fields(self, data: Dict, required_fields: Dict) -> None:
        """Validate required fields are present and of correct type."""
        for field, expected_type in required_fields.items():
            value = data.get(field)
            if not value:
                raise ValueError(f"Missing required field: {field}")
            if not isinstance(value, expected_type):
                raise ValueError(f"Invalid type for {field}: expected {expected_type.__name__}")

    def _validate_lease_option(self, data: Dict) -> None:
        """Validate lease option specific fields."""
        if float(self._get_value(data, 'strike_price') or 0) <= float(self._get_value(data, 'purchase_price') or 0):
            raise ValueError("Strike price must be greater than purchase price")

        option_fields = {
            'option_consideration_fee': "Option fee",
            'option_term_months': "Option term",
            'strike_price': "Strike price",
            'monthly_rent_credit_percentage': "Monthly rent credit percentage",
            'rent_credit_cap': "Rent credit cap"
        }

        for field, display_name in option_fields.items():
            value = self._get_value(data, field)
            if value is None or float(value) <= 0:
                raise ValueError(f"{display_name} must be greater than 0")

        rent_credit_pct = float(self._get_value(data, 'monthly_rent_credit_percentage') or 0)
        if not 0 <= rent_credit_pct <= 100:
            raise ValueError("Monthly rent credit percentage must be between 0 and 100")

        option_term = int(self._get_value(data, 'option_term_months') or 0)
        if option_term > 120:
            raise ValueError("Option term cannot exceed 120 months")

        # Validate loans for Lease Options
        self._validate_loans(data)

    def _validate_loans(self, data: Dict) -> None:
        """Validate loan data."""
        loan_prefixes = ['loan1', 'loan2', 'loan3']
        for prefix in loan_prefixes:
            loan_amount = self._get_value(data, f'{prefix}_loan_amount')
            if loan_amount and float(loan_amount) > 0:
                # Validate loan amount and terms
                interest_rate = float(self._get_value(data, f'{prefix}_loan_interest_rate') or 0)
                loan_term = int(self._get_value(data, f'{prefix}_loan_term') or 0)
                
                if interest_rate <= 0 or interest_rate > 30:
                    raise ValueError(f"{prefix}: Interest rate must be between 0% and 30%")
                
                if loan_term <= 0 or loan_term > 360:
                    raise ValueError(f"{prefix}: Loan term must be between 1 and 360 months")

    def _validate_field_type(self, field: str, value: Any) -> None:
        """
        Validate a single field's type and format.
        
        Args:
            field: Field name
            value: Field value
            
        Raises:
            ValueError: If field value is invalid
        """
        field_def = self.ANALYSIS_SCHEMA[field]
        field_type = field_def['type']
        
        try:
            if field_type == 'integer':
                self._convert_to_int(value)
            elif field_type == 'float':
                self._convert_to_float(value)
            elif field_type == 'string':
                if not isinstance(value, str):
                    value = str(value)
                
                # Validate special string formats
                if field_def.get('format') == 'uuid':
                    uuid.UUID(str(value))
                elif field_def.get('format') == 'datetime':
                    datetime.fromisoformat(str(value).replace('Z', '+00:00'))
            elif field_type == 'boolean':
                # Handle various boolean-like values
                if isinstance(value, str):
                    if value.lower() not in ('true', 'false', '1', '0'):
                        raise ValueError(f"Invalid boolean value: {value}")
                elif not isinstance(value, bool) and value not in (0, 1):
                    raise ValueError(f"Invalid boolean value: {value}")
                    
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid {field_type} value for field {field}: {str(e)}")

    def _convert_to_int(self, value: Any) -> Optional[int]:
        """
        Convert value to integer, handling empty values for optional fields.
        
        Args:
            value: Value to convert
            
        Returns:
            Converted integer value or None
            
        Raises:
            ValueError: If conversion fails
        """
        if value is None or value == '':
            return None  # Return None for empty optional fields
        try:
            if isinstance(value, str):
                clean_value = value.replace('$', '').replace(',', '').strip()
                return int(float(clean_value))
            return int(float(value))
        except (ValueError, TypeError):
            raise ValueError(f"Cannot convert {value} to integer")

    def _convert_to_float(self, value: Any) -> Optional[float]:
        """
        Convert value to float, handling empty values for optional fields.
        
        Args:
            value: Value to convert
            
        Returns:
            Converted float value or None
            
        Raises:
            ValueError: If conversion fails
        """
        if value is None or value == '':
            return None  # Return None for empty optional fields
        try:
            if isinstance(value, str):
                clean_value = value.replace('$', '').replace('%', '').replace(',', '').strip()
                return float(clean_value)
            return float(value)
        except (ValueError, TypeError):
            raise ValueError(f"Cannot convert {value} to float")

    def create_analysis(self, analysis_data: Dict, user_id: str) -> Dict:
        """
        Create new analysis with validation and calculation, ensuring metrics consistency.
        
        Args:
            analysis_data: Input analysis data
            user_id: User ID
            
        Returns:
            Created analysis with calculated metrics
        """
        try:
            logger.debug(f"Creating analysis for user {user_id}")
            
            # Normalize incoming data
            normalized_data = self.normalize_data(analysis_data)
            
            # Add metadata
            normalized_data.update({
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'created_at': datetime.now().strftime("%Y-%m-%d"),
                'updated_at': datetime.now().strftime("%Y-%m-%d")
            })
            
            # Validate data
            self.validate_analysis_data(normalized_data)
            
            # Create Analysis object and get calculations
            analysis = create_analysis(normalized_data)
            metrics = analysis.get_report_data()['metrics']
            
            # Utilize standardized metrics functions instead of MetricsHandler
            from utils.standardized_metrics import register_metrics
            register_metrics(normalized_data['id'], metrics)
            
            # Save to storage
            self._save_analysis(normalized_data, user_id)
            
            return {
                'success': True,
                'analysis': {
                    **normalized_data,
                    'calculated_metrics': metrics
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating analysis: {str(e)}", exc_info=True)
            raise

    def update_analysis(self, analysis_data: Dict, user_id: str) -> Dict:
        """
        Update existing analysis with validation and recalculation, ensuring metrics consistency.
        
        Args:
            analysis_data: Updated analysis data
            user_id: User ID
            
        Returns:
            Updated analysis with calculated metrics
            
        Raises:
            ValueError: If analysis ID missing or not found
        """
        try:
            analysis_id = analysis_data.get('id')
            if not analysis_id:
                raise ValueError("Analysis ID required for updates")
            
            # Verify analysis exists and get current data
            current_analysis = self.get_analysis(analysis_id, user_id)
            if not current_analysis:
                raise ValueError("Analysis not found")
            
            # Log balloon payment fields
            self._log_balloon_data(analysis_data)
            
            # Preserve comps data from current analysis if not in update data
            if not analysis_data.get('comps_data') and current_analysis.get('comps_data'):
                logger.debug("Preserving existing comps data")
                analysis_data['comps_data'] = current_analysis.get('comps_data')
                
            # Normalize and validate new data
            normalized_data = self.normalize_data(analysis_data)
            
            # Preserve metadata
            normalized_data.update({
                'id': analysis_id,
                'user_id': user_id,
                'created_at': current_analysis.get('created_at', datetime.now().strftime("%Y-%m-%d")),
                'updated_at': datetime.now().strftime("%Y-%m-%d"),
                'comps_data': analysis_data.get('comps_data', current_analysis.get('comps_data'))
            })
            
            # Validate updated data
            self.validate_analysis_data(normalized_data)
            
            # Create Analysis object and get calculations
            analysis = create_analysis(normalized_data)
            metrics = analysis.get_report_data().get('metrics', {})
            
            # Utilize standardized metrics functions instead of MetricsHandler
            from utils.standardized_metrics import register_metrics
            register_metrics(analysis_id, metrics)
            
            # Debug log for comps data
            self._log_comps_data(normalized_data)
            
            # Save to storage with explicit comps preservation
            self._save_analysis(normalized_data, user_id)
            
            return {
                'success': True,
                'analysis': {
                    **normalized_data,
                    'calculated_metrics': metrics
                }
            }
            
        except Exception as e:
            logger.error(f"Error updating analysis: {str(e)}", exc_info=True)
            raise

    def _log_balloon_data(self, analysis_data: Dict) -> None:
        """Log balloon payment fields for debugging."""
        logger.debug(f"Has balloon payment: {analysis_data.get('has_balloon_payment')}")
        if analysis_data.get('has_balloon_payment'):
            logger.debug("Balloon fields:")
            balloon_fields = [
                'balloon_due_date', 'balloon_refinance_ltv_percentage', 
                'balloon_refinance_loan_amount', 'balloon_refinance_loan_interest_rate',
                'balloon_refinance_loan_term', 'balloon_refinance_loan_down_payment',
                'balloon_refinance_loan_closing_costs'
            ]
            for field in balloon_fields:
                logger.debug(f"  {field}: {analysis_data.get(field)}")

    def _log_comps_data(self, data: Dict) -> None:
        """Log comps data for debugging."""
        logger.debug(f"Saving analysis with comps data present: {'comps_data' in data}")
        if data.get('comps_data') is not None:
            comparables = data['comps_data'].get('comparables', [])
            logger.debug(f"Comps data contains {len(comparables)} comparables")
        else:
            logger.debug("No comps data present")

    def get_analysis(self, analysis_id: str, user_id: str) -> Optional[Dict]:
        """
        Retrieve analysis with calculations and ensure metrics consistency.
        
        Args:
            analysis_id: Analysis ID
            user_id: User ID
            
        Returns:
            Analysis data with calculated metrics or None if not found
        """
        try:
            filepath = self._get_analysis_filepath(analysis_id, user_id)
            if not os.path.exists(filepath):
                return None
                
            # Load stored data
            stored_data = read_json(filepath)
            
            # Handle field mapping for backward compatibility
            if 'property_address' in stored_data and 'address' not in stored_data:
                stored_data['address'] = stored_data['property_address']
            
            # Create Analysis object for calculations
            analysis = create_analysis(stored_data)
            metrics = analysis.get_report_data()['metrics']
            
            # Utilize standardized metrics functions instead of MetricsHandler
            from utils.standardized_metrics import register_metrics
            register_metrics(analysis_id, metrics)
            
            return {
                **stored_data,
                'calculated_metrics': metrics
            }
            
        except Exception as e:
            logger.error(f"Error retrieving analysis: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def find_analysis_owner(self, analysis_id):
        """Find the user who owns a specific analysis"""
        # Implementation will depend on your storage structure
        # This is just a conceptual example
        
        # Check each user directory
        users_dir = os.path.join(current_app.config['DATA_DIR'], 'users')
        for user_id in os.listdir(users_dir):
            user_analyses_dir = os.path.join(users_dir, user_id, 'analyses')
            if os.path.exists(user_analyses_dir):
                analysis_path = os.path.join(user_analyses_dir, f"{analysis_id}.json")
                if os.path.exists(analysis_path):
                    return user_id
                    
        return None

    def get_analyses_for_user(self, user_id: str, page: int = 1, per_page: int = 10) -> Tuple[List[Dict], int]:
        """
        Get paginated list of analyses for a user.
        
        Args:
            user_id: User ID
            page: Page number (1-based)
            per_page: Items per page
            
        Returns:
            Tuple of (list of analyses, total pages)
        """
        try:
            logger.info(f"Starting get_analyses_for_user for user {user_id}")
            
            analyses_dir = current_app.config['ANALYSES_DIR']
            os.makedirs(analyses_dir, exist_ok=True)
            
            logger.info(f"Looking in directory: {analyses_dir}")
            all_files = os.listdir(analyses_dir)
            
            # Get all analyses for user
            analyses = []
            for filename in all_files:
                if filename.endswith(f"_{user_id}.json"):
                    logger.info(f"Found matching file: {filename}")
                    filepath = os.path.join(analyses_dir, filename)
                    analysis_data = read_json(filepath)
                    
                    if analysis_data:  # Only process if we got valid data
                        analysis_data = self._process_analysis_data(analysis_data, user_id, filename)
                        if analysis_data:
                            analyses.append(analysis_data)
            
            logger.info(f"Total analyses found: {len(analyses)}")
            
            # Sort by updated_at timestamp
            analyses.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
            
            # Paginate results
            return self._paginate_analyses(analyses, page, per_page)
                
        except Exception as e:
            logger.error(f"Error retrieving analyses: {str(e)}")
            logger.error(traceback.format_exc())
            return [], 1

    def _process_analysis_data(self, analysis_data: Dict, user_id: str, filename: str) -> Optional[Dict]:
        """Process a single analysis file."""
        try:
            # Handle field mapping
            if 'property_address' in analysis_data and 'address' not in analysis_data:
                analysis_data['address'] = analysis_data['property_address']
            
            # Update analysis data with required fields
            analysis_data.update({
                'user_id': user_id,
                'created_at': analysis_data.get('created_at') or datetime.now().strftime("%Y-%m-%d"),
                'updated_at': analysis_data.get('updated_at') or datetime.now().strftime("%Y-%m-%d"),
            })
            
            # Create Analysis object for calculations
            analysis = create_analysis(analysis_data)
            metrics = analysis.get_report_data()['metrics']
            processed_data = {
                **analysis_data,
                'calculated_metrics': metrics
            }
            logger.info(f"Successfully processed analysis: {analysis_data['analysis_name']}")
            return processed_data
        except Exception as analysis_error:
            logger.error(f"Error processing analysis {filename}: {str(analysis_error)}")
            return None

    def _paginate_analyses(self, analyses: List[Dict], page: int, per_page: int) -> Tuple[List[Dict], int]:
        """Paginate a list of analyses."""
        # Calculate pagination
        total_analyses = len(analyses)
        total_pages = max((total_analyses + per_page - 1) // per_page, 1)
        
        # Get requested page
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total_analyses)
        page_analyses = analyses[start_idx:end_idx]
        
        logger.info(f"Returning {len(page_analyses)} analyses for page {page} of {total_pages}")
        return page_analyses, total_pages

    def delete_analysis(self, analysis_id: str, user_id: str) -> bool:
        """
        Delete an analysis.
        
        Args:
            analysis_id: Analysis ID
            user_id: User ID
            
        Returns:
            True if successful
            
        Raises:
            ValueError: If analysis not found
        """
        try:
            logger.info(f"Attempting to delete analysis {analysis_id} for user {user_id}")
            
            filepath = self._get_analysis_filepath(analysis_id, user_id)
            if not os.path.exists(filepath):
                raise ValueError("Analysis not found")
                
            os.remove(filepath)
            logger.info(f"Successfully deleted analysis {analysis_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting analysis: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def generate_pdf_report(self, analysis_id: str, user_id: str) -> BytesIO:
        """
        Generate a PDF report for an analysis with consistent metrics.
        
        Args:
            analysis_id: Analysis ID
            user_id: User ID
            
        Returns:
            BytesIO buffer containing PDF data
            
        Raises:
            ValueError: If analysis not found
        """
        try:
            analysis_data = self.get_analysis(analysis_id, user_id)
            if not analysis_data:
                raise ValueError("Analysis not found")

            # Add current date to the analysis data
            analysis_data['generated_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Use standardized metrics directly
            from utils.standardized_metrics import extract_calculated_metrics, get_metrics

            # Check if metrics are already registered
            registered_metrics = get_metrics(analysis_id)
            
            if not registered_metrics:
                # Extract and register metrics if not already registered
                metrics = extract_calculated_metrics(analysis_data)
                from utils.standardized_metrics import register_metrics
                register_metrics(analysis_id, metrics)
            
            # Generate report using report generator
            buffer = generate_report(analysis_data, report_type='analysis')
            
            return buffer
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def _save_analysis(self, analysis_data: Dict, user_id: str, is_mobile: bool = False) -> None:
        """
        Save analysis data to storage with mobile optimization support.
        
        Args:
            analysis_data: Analysis data to save
            user_id: User ID
            is_mobile: Whether request is from mobile client
            
        Raises:
            ValueError: If validation fails
            IOError: If file operations fail
        """
        try:
            logger.debug(f"Starting analysis save operation for user {user_id}")
            logger.debug(f"Mobile optimization: {is_mobile}")
            
            # Get storage filepath
            filename = f"{analysis_data['id']}_{user_id}.json"
            filepath = os.path.join(current_app.config['ANALYSES_DIR'], filename)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Create a copy of the data for storage
            storage_data = analysis_data.copy()
            
            # Add metadata
            storage_data.update({
                'last_modified': datetime.now().isoformat(),
                'last_accessed': datetime.now().isoformat(),
                'storage_version': '2.0'  # Version tracking for schema changes
            })
            
            # Validate data before storage
            self._validate_storage_data(storage_data)
            
            # Implement retries for file operations
            self._save_with_retries(filepath, storage_data)
            
        except ValueError as e:
            logger.error(f"Validation error during save: {str(e)}")
            raise
        except IOError as e:
            logger.error(f"IO error during save: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during save: {str(e)}")
            logger.error(traceback.format_exc())
            raise ValueError(f"Failed to save analysis: {str(e)}")

    def _save_with_retries(self, filepath: str, data: Dict) -> None:
        """
        Save data to file with retry logic.
        
        Args:
            filepath: Path to save file
            data: Data to save
            
        Raises:
            IOError: If save fails after all retries
        """
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                # Create temporary file
                temp_filepath = f"{filepath}.temp"
                
                # Write to temporary file first using write_json utility
                write_json(temp_filepath, data)
                
                # Atomic rename for safe file replacement
                os.replace(temp_filepath, filepath)
                
                logger.debug(f"Analysis saved successfully to {filepath}")
                break
                
            except IOError as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Retry {attempt + 1}/{max_retries} after IOError: {str(e)}")
                    time.sleep(retry_delay)
                else:
                    raise IOError(f"Failed to save analysis after {max_retries} attempts: {str(e)}")
                    
            finally:
                # Cleanup temporary file if it exists
                if os.path.exists(temp_filepath):
                    try:
                        os.remove(temp_filepath)
                    except OSError:
                        pass

    def _validate_storage_data(self, data: Dict) -> None:
        """
        Validate data before storage.
        
        Args:
            data: Data to validate
            
        Raises:
            ValueError: If validation fails
        """
        required_fields = ['id', 'user_id', 'analysis_type', 'analysis_name']
        
        # Check required fields
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            raise ValueError(f"Missing required fields for storage: {', '.join(missing_fields)}")
        
        # Validate ID format
        try:
            uuid.UUID(str(data['id']))
        except ValueError:
            raise ValueError("Invalid analysis ID format")
        
        # Validate numeric fields
        numeric_fields = {
            'monthly_rent': int,
            'property_taxes': int,
            'insurance': int,
            'management_fee_percentage': float,
            'capex_percentage': float,
            'vacancy_percentage': float,
            'repairs_percentage': float
        }
        
        for field, field_type in numeric_fields.items():
            if field in data:
                value = data[field]
                if value is not None:
                    if not isinstance(value, (int, float)):
                        raise ValueError(f"Invalid type for {field}: expected {field_type.__name__}")
                    if field_type == float and field.endswith('_percentage'):
                        if not 0 <= value <= 100:
                            raise ValueError(f"Invalid percentage value for {field}: {value}")
                            
        # Validate dates
        if 'balloon_due_date' in data and data['balloon_due_date']:
            try:
                datetime.strptime(data['balloon_due_date'], "%Y-%m-%d")
            except ValueError:
                raise ValueError("Invalid balloon_due_date format")
            
    def _compress_analysis_data(self, data: Dict) -> Dict:
        """
        Compress analysis data for mobile storage.
        
        Args:
            data: Original data
            
        Returns:
            Compressed data for mobile
        """
        compressed = data.copy()
        
        # Remove unnecessary precision from numeric values
        for key, value in compressed.items():
            if isinstance(value, float):
                compressed[key] = round(value, 2)
                
        # Truncate long text fields
        if compressed.get('notes'):
            compressed['notes'] = compressed['notes'][:1000]
            
        return compressed

    def _get_analysis_filepath(self, analysis_id: str, user_id: str) -> str:
        """
        Get filepath for analysis storage.
        
        Args:
            analysis_id: Analysis ID
            user_id: User ID
            
        Returns:
            Full filepath for storage
            
        Raises:
            ValueError: If filepath cannot be determined
        """
        try:
            analyses_dir = current_app.config.get('ANALYSES_DIR')
            if not analyses_dir:
                raise ValueError("ANALYSES_DIR not configured")
                
            # Ensure directory exists
            os.makedirs(analyses_dir, exist_ok=True)
            
            # Sanitize components
            safe_analysis_id = str(analysis_id).replace('/', '_').replace('\\', '_')
            safe_user_id = str(user_id).replace('/', '_').replace('\\', '_')
            
            return os.path.join(analyses_dir, f"{safe_analysis_id}_{safe_user_id}.json")
            
        except Exception as e:
            logger.error(f"Error creating filepath: {str(e)}")
            raise ValueError(f"Could not determine filepath: {str(e)}")