from datetime import datetime
import logging
import os
import uuid
import json  # Add this import
import time  # Add this for retry delays
from typing import Dict, List, Optional, Union, Any, Tuple
import traceback
from services.report_generator import generate_report
from flask import current_app, session
from io import BytesIO
from utils.json_handler import read_json, write_json
from services.analysis_calculations import create_analysis
from utils.comps_handler import fetch_property_comps, update_analysis_comps, RentcastAPIError


logger = logging.getLogger(__name__)

class AnalysisService:
    """Service for handling property investment analyses with flat data structure."""

    ANALYSIS_SCHEMA = {
        # Core fields
        'id': {'type': 'string', 'format': 'uuid'},
        'user_id': {'type': 'string'},
        'created_at': {'type': 'string', 'format': 'datetime'},
        'updated_at': {'type': 'string', 'format': 'datetime'},
        'analysis_type': {'type': 'string'},
        'analysis_name': {'type': 'string'},

        # Property details
        'address': {'type': 'string'},
        'property_type': {'type': 'string', 'optional': True, 
            'allowed_values': [
                'Single Family',
                'Condo',
                'Townhouse',
                'Manufactured',
                'Multi-Family'
            ]
        },
        'square_footage': {'type': 'integer', 'optional': True},  # Add optional flag
        'lot_size': {'type': 'integer', 'optional': True},
        'year_built': {'type': 'integer', 'optional': True},
        'bedrooms': {'type': 'integer', 'optional': True},
        'bathrooms': {'type': 'float', 'optional': True},

        # Add comps data fields
        'comps_data': {
            'type': 'object',
            'optional': True,  # Not all analyses will have comps run
            'properties': {
                'last_run': {
                    'type': 'string',
                    'format': 'datetime',
                    'optional': True,
                    'description': 'ISO 8601 datetime when comps were last run'
                },
                'run_count': {
                    'type': 'integer',
                    'optional': True,
                    'description': 'Number of times comps have been run in current session'
                },
                'estimated_value': {
                    'type': 'integer',
                    'optional': True,
                    'description': 'Estimated value based on comps'
                },
                'value_range_low': {
                    'type': 'integer',
                    'optional': True,
                    'description': 'Lower bound of estimated value range'
                },
                'value_range_high': {
                    'type': 'integer',
                    'optional': True,
                    'description': 'Upper bound of estimated value range'
                },
                'comparables': {
                    'type': 'array',
                    'optional': True,
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'string'},
                            'formattedAddress': {'type': 'string'},
                            'city': {'type': 'string'},
                            'state': {'type': 'string'},
                            'zipCode': {'type': 'string'},
                            'propertyType': {'type': 'string'},
                            'bedrooms': {'type': 'integer'},
                            'bathrooms': {'type': 'float'},
                            'squareFootage': {'type': 'integer'},
                            'yearBuilt': {'type': 'integer'},
                            'price': {'type': 'integer'},
                            'listingType': {'type': 'string'},
                            'listedDate': {
                                'type': 'string',
                                'format': 'datetime'
                            },
                            'removedDate': {
                                'type': 'string',
                                'format': 'datetime',
                                'optional': True
                            },
                            'daysOnMarket': {'type': 'integer'},
                            'distance': {'type': 'float'},
                            'correlation': {'type': 'float'}
                        }
                    }
                }
            }
        },

        # Ballon Options
        'has_balloon_payment': {'type': 'boolean'},
        'balloon_due_date': {'type': 'string', 'format': 'date'},  # ISO format date
        'balloon_refinance_ltv_percentage': {'type': 'float'},
        'balloon_refinance_loan_amount': {'type': 'integer'},
        'balloon_refinance_loan_interest_rate': {'type': 'float'},
        'balloon_refinance_loan_term': {'type': 'integer'},
        'balloon_refinance_loan_down_payment': {'type': 'integer'},
        'balloon_refinance_loan_closing_costs': {'type': 'integer'},

        # Purchase details
        'purchase_price': {'type': 'integer'},
        'after_repair_value': {'type': 'integer'},
        'renovation_costs': {'type': 'integer'},
        'renovation_duration': {'type': 'integer'},
        'cash_to_seller': {'type': 'integer'},
        'closing_costs': {'type': 'integer'},
        'assignment_fee': {'type': 'integer'},
        'marketing_costs': {'type': 'integer'},
        'furnishing_costs': {'type': 'integer','optional': True},

        # Income
        'monthly_rent': {'type': 'integer'},

        # Operating expenses
        'property_taxes': {'type': 'integer'},
        'insurance': {'type': 'integer'},
        'hoa_coa_coop': {'type': 'integer'},
        'management_fee_percentage': {'type': 'float'},
        'capex_percentage': {'type': 'float'},
        'vacancy_percentage': {'type': 'float'},
        'repairs_percentage': {'type': 'float'},

        # Notes
        'notes': {
            'type': 'string',
            'maxLength': 1000,  # Limit to 1,000 characters
            'description': 'User notes about the analysis'
        },

        # PadSplit specific
        'utilities': {'type': 'integer'},
        'internet': {'type': 'integer'},
        'cleaning': {'type': 'integer'},
        'pest_control': {'type': 'integer'},
        'landscaping': {'type': 'integer'},
        'padsplit_platform_percentage': {'type': 'float'},

        # Loan fields
        'initial_loan_name': {'type': 'string'},
        'initial_loan_amount': {'type': 'integer'},
        'initial_loan_interest_rate': {'type': 'float'},
        'initial_interest_only': {'type': 'boolean'},
        'initial_loan_term': {'type': 'integer'},
        'initial_loan_down_payment': {'type': 'integer'},
        'initial_loan_closing_costs': {'type': 'integer'},

        'refinance_loan_name': {'type': 'string'},
        'refinance_loan_amount': {'type': 'integer'},
        'refinance_loan_interest_rate': {'type': 'float'},
        'refinance_loan_term': {'type': 'integer'},
        'refinance_loan_down_payment': {'type': 'integer'},
        'refinance_loan_closing_costs': {'type': 'integer'},

        'loan1_interest_only': {'type': 'boolean'},
        'loan2_interest_only': {'type': 'boolean'},
        'loan3_interest_only': {'type': 'boolean'},

        'loan1_loan_name': {'type': 'string'},
        'loan1_loan_amount': {'type': 'integer'},
        'loan1_loan_interest_rate': {'type': 'float'},
        'loan1_loan_term': {'type': 'integer'},
        'loan1_loan_down_payment': {'type': 'integer'},
        'loan1_loan_closing_costs': {'type': 'integer'},

        'loan2_loan_name': {'type': 'string'},
        'loan2_loan_amount': {'type': 'integer'},
        'loan2_loan_interest_rate': {'type': 'float'},
        'loan2_loan_term': {'type': 'integer'},
        'loan2_loan_down_payment': {'type': 'integer'},
        'loan2_loan_closing_costs': {'type': 'integer'},

        'loan3_loan_name': {'type': 'string'},
        'loan3_loan_amount': {'type': 'integer'},
        'loan3_loan_interest_rate': {'type': 'float'},
        'loan3_loan_term': {'type': 'integer'},
        'loan3_loan_down_payment': {'type': 'integer'},
        'loan3_loan_closing_costs': {'type': 'integer'},

        # New Lease Option fields
        'option_consideration_fee': {
            'type': 'integer',
            'optional': False,
            'description': 'Non-refundable upfront fee for lease option'
        },
        'option_term_months': {
            'type': 'integer',
            'optional': False,
            'description': 'Duration of option period in months'
        },
        'strike_price': {
            'type': 'integer',
            'optional': False,
            'description': 'Agreed upon future purchase price'
        },
        'monthly_rent_credit_percentage': {
            'type': 'float',
            'optional': False,
            'description': 'Percentage of monthly rent applied as credit'
        },
        'rent_credit_cap': {
            'type': 'integer',
            'optional': False,
            'description': 'Maximum total rent credit allowed'
        },

        # Multi-Family specific fields
        'total_units': {'type': 'integer', 'optional': False},
        'occupied_units': {'type': 'integer', 'optional': False},
        'floors': {'type': 'integer', 'optional': False},
        'other_income': {'type': 'integer', 'optional': True},
        'total_potential_income': {'type': 'integer', 'optional': True},

        # Multi-Family operating expenses
        'common_area_maintenance': {'type': 'integer', 'optional': False},
        'elevator_maintenance': {'type': 'integer', 'optional': True},
        'staff_payroll': {'type': 'integer', 'optional': False},
        'trash_removal': {'type': 'integer', 'optional': False},
        'common_utilities': {'type': 'integer', 'optional': False},

        # Unit Types array (will be handled as JSON string in storage)
        'unit_types': {
            'type': 'string',  # JSON string of unit type array
            'optional': False,
            'description': 'Array of unit types and their details'
        },
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        
        # Add mobile-specific configuration
        self.mobile_config = {
            'max_image_size': 800,  # Max dimension for mobile images
            'pagination_size': 10,   # Items per page on mobile
            'cache_duration': 300    # Cache duration in seconds
        }

    def run_property_comps(self, analysis_id: str, user_id: str) -> Optional[Dict]:
        """
        Run property comps for an analysis and update the analysis data
        
        Args:
            analysis_id: ID of the analysis
            user_id: ID of the user running comps
            
        Returns:
            Updated analysis dictionary or None if analysis not found
            
        Raises:
            RentcastAPIError: If API request fails
        """
        try:
            # Get the analysis
            analysis = self.get_analysis(analysis_id, user_id)
            if not analysis:
                logger.error(f"Analysis not found for ID: {analysis_id}")
                return None
                
            # Check run count in session
            session_key = f'comps_run_count_{analysis_id}'
            run_count = session.get(session_key, 0)
            
            # Log the current run count
            logger.debug(f"Current comps run count for {analysis_id}: {run_count}")
            
            # Get max runs from config using dictionary access
            max_runs = current_app.config['MAX_COMP_RUNS_PER_SESSION']
            if max_runs is None:
                max_runs = 3  # Default fallback
                logger.warning("MAX_COMP_RUNS_PER_SESSION not found in config, using default: 3")
            
            if run_count >= max_runs:
                raise RentcastAPIError(
                    f"Maximum comp runs ({max_runs}) reached for this session"
                )
            
            # Fetch comps from RentCast
            comps_data = fetch_property_comps(
                current_app.config,  # Pass the entire config object
                analysis['address'],
                analysis['property_type'],
                float(analysis['bedrooms']),
                float(analysis['bathrooms']),
                float(analysis['square_footage'])
            )
            
            # Increment run count
            run_count += 1
            session[session_key] = run_count
            logger.debug(f"Updated comps run count to: {run_count}")
            
            # Update analysis with comps data
            updated_analysis = update_analysis_comps(analysis, comps_data, run_count)
            
            # Save updated analysis
            self._save_analysis(updated_analysis, user_id)
            logger.debug(f"Successfully saved updated analysis with comps data")
            
            return updated_analysis
            
        except Exception as e:
            logger.error(f"Error running property comps: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def normalize_data(self, data: Dict, is_mobile: bool = False) -> Dict:
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
                if is_mobile and not value and field in self.MOBILE_OPTIONAL_FIELDS:
                    continue
                    
                # Convert value based on type
                if field_type == 'integer':
                    normalized[field] = self._convert_to_int(value)
                    
                elif field_type == 'float':
                    normalized[field] = self._convert_to_float(value)
                    
                elif field_type == 'string':
                    if value is not None:
                        normalized[field] = str(value)
                    else:
                        normalized[field] = ''
                        
                elif field_type == 'boolean':
                    if field == 'has_balloon_payment':
                        normalized[field] = bool(value)
                    else:
                        # Handle other boolean fields
                        if isinstance(value, str):
                            normalized[field] = value.lower() in ('true', '1', 'yes', 'on')
                        else:
                            normalized[field] = bool(value)
                
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

    def _optimize_metrics_for_mobile(self, metrics: Dict) -> Dict:
        """
        Optimize calculated metrics for mobile display.
        
        Args:
            metrics (Dict): Original metrics dictionary
            
        Returns:
            Dict: Optimized metrics for mobile
        """
        optimized = {}
        
        # Define precision for different metric types
        precision_map = {
            'percentage': 1,  # One decimal for percentages
            'currency': 0,    # No decimals for currency values
            'ratio': 2       # Two decimals for ratios
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
        
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                metric_type = metric_types.get(key, 'ratio')  # Default to ratio
                precision = precision_map.get(metric_type, 2)  # Default to 2 decimals
                
                # Round according to metric type
                if value is not None:
                    optimized[key] = round(float(value), precision)
            else:
                # Keep non-numeric values as-is
                optimized[key] = value
                
        return optimized
    
    def _get_value(self, data, field):
        """
        Safely get a value from the data dict, handling various formats.
        
        Args:
            data (dict): The data dictionary to get the value from
            field (str): The field name to get
            
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
        """Validate analysis data against schema."""
        try:
            logger.debug("Starting analysis data validation")
            
            # Validate required base fields
            required_fields = {
                'analysis_type': str,
                'analysis_name': str
            }

            # Add monthly_rent requirement only for non-Multi-Family analyses
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
            
            for field, expected_type in required_fields.items():
                value = data.get(field)
                if not value:
                    raise ValueError(f"Missing required field: {field}")
                if not isinstance(value, expected_type):
                    raise ValueError(f"Invalid type for {field}: expected {expected_type.__name__}")
            
            # Validate field types for non-required fields
            for field, value in data.items():
                if field in self.ANALYSIS_SCHEMA and value is not None:
                    field_def = self.ANALYSIS_SCHEMA[field]
                    # Skip validation for optional fields that are empty
                    if field_def.get('optional') and (value is None or value == ''):
                        continue
                    self._validate_field_type(field, value)
                        
            # Lease Option specific validation
            if data.get('analysis_type') == 'Lease Option':
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

                # Add loan validation for Lease Options
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

            logger.debug("Analysis data validation complete")
            
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected validation error: {str(e)}")
            logger.error(traceback.format_exc())
            raise ValueError(f"Validation failed: {str(e)}")

    def _validate_field_type(self, field: str, value: Any) -> None:
        """Validate a single field's type and format."""
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

    def _convert_to_int(self, value: Any) -> int:
        """Convert value to integer, handling empty values for optional fields."""
        if value is None or value == '':
            return None  # Return None for empty optional fields
        try:
            if isinstance(value, str):
                clean_value = value.replace('$', '').replace(',', '').strip()
                return int(float(clean_value))
            return int(float(value))
        except (ValueError, TypeError):
            raise ValueError(f"Cannot convert {value} to integer")

    def _convert_to_float(self, value: Any) -> float:
        """Convert value to float, handling empty values for optional fields."""
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
        """Create new analysis with validation and calculation."""
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
            logger.error(f"Error creating analysis: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def update_analysis(self, analysis_data: Dict, user_id: str) -> Dict:
        """Update existing analysis with validation and recalculation."""
        try:
            analysis_id = analysis_data.get('id')
            if not analysis_id:
                raise ValueError("Analysis ID required for updates")
            
            # Verify analysis exists
            current_analysis = self.get_analysis(analysis_id, user_id)
            if not current_analysis:
                raise ValueError("Analysis not found")
                
            # Normalize and validate new data
            normalized_data = self.normalize_data(analysis_data)
            
            # Preserve metadata
            normalized_data.update({
                'id': analysis_id,
                'user_id': user_id,
                'created_at': current_analysis['created_at'],
                'updated_at': datetime.now().strftime("%Y-%m-%d")
            })
            
            # Validate updated data
            self.validate_analysis_data(normalized_data)
            
            # Create Analysis object and get calculations
            analysis = create_analysis(normalized_data)
            metrics = analysis.get_report_data()['metrics']
            
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
            logger.error(f"Error updating analysis: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def get_analysis(self, analysis_id: str, user_id: str) -> Optional[Dict]:
        """Retrieve analysis with calculations."""
        try:
            filepath = self._get_analysis_filepath(analysis_id, user_id)
            if not os.path.exists(filepath):
                return None
                
            # Load stored data
            stored_data = read_json(filepath)
            
            # Handle field mapping
            if 'property_address' in stored_data and 'address' not in stored_data:
                stored_data['address'] = stored_data['property_address']
            
            # Create Analysis object for calculations
            analysis = create_analysis(stored_data)
            metrics = analysis.get_report_data()['metrics']
            
            return {
                **stored_data,
                'calculated_metrics': metrics
            }
            
        except Exception as e:
            logger.error(f"Error retrieving analysis: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def get_analyses_for_user(self, user_id: str, page: int = 1, per_page: int = 10) -> Tuple[List[Dict], int]:
        """Get paginated list of analyses for a user."""
        try:
            logger.info(f"A. Starting get_analyses_for_user for user {user_id}")
            
            analyses_dir = current_app.config['ANALYSES_DIR']
            os.makedirs(analyses_dir, exist_ok=True)
            
            logger.info(f"B. Looking in directory: {analyses_dir}")
            all_files = os.listdir(analyses_dir)
            logger.info(f"C. All files: {all_files}")
            
            # Get all analyses for user
            analyses = []
            for filename in all_files:
                logger.info(f"D. Checking file: {filename}")
                if filename.endswith(f"_{user_id}.json"):
                    logger.info(f"E. Found matching file: {filename}")
                    filepath = os.path.join(analyses_dir, filename)
                    analysis_data = read_json(filepath)
                    
                    logger.info(f"F. Raw analysis data from {filename}: {analysis_data}")
                    
                    if analysis_data:  # Only process if we got valid data
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
                        try:
                            analysis = create_analysis(analysis_data)
                            metrics = analysis.get_report_data()['metrics']
                            analyses.append({
                                **analysis_data,
                                'calculated_metrics': metrics
                            })
                            logger.info(f"G. Successfully processed analysis: {analysis_data['analysis_name']}")
                        except Exception as analysis_error:
                            logger.error(f"Error processing analysis {filename}: {str(analysis_error)}")
                            continue
            
            logger.info(f"H. Total analyses found: {len(analyses)}")
            
            # Sort by updated_at timestamp
            analyses.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
            
            # Calculate pagination
            total_analyses = len(analyses)
            total_pages = max((total_analyses + per_page - 1) // per_page, 1)
            
            # Get requested page
            start_idx = (page - 1) * per_page
            end_idx = min(start_idx + per_page, total_analyses)
            page_analyses = analyses[start_idx:end_idx]
            
            logger.info(f"I. Returning {len(page_analyses)} analyses for page {page} of {total_pages}")
            return page_analyses, total_pages
                
        except Exception as e:
            logger.error(f"Error retrieving analyses: {str(e)}")
            logger.error(traceback.format_exc())
            return [], 1

    def delete_analysis(self, analysis_id: str, user_id: str) -> bool:
        """Delete an analysis."""
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
        """Generate a PDF report for an analysis."""
        try:
            analysis_data = self.get_analysis(analysis_id, user_id)
            if not analysis_data:
                raise ValueError("Analysis not found")

            # Add current date to the analysis data
            analysis_data['generated_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
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
            max_retries = 3
            retry_delay = 1  # seconds
            
            for attempt in range(max_retries):
                try:
                    # Create temporary file
                    temp_filepath = f"{filepath}.temp"
                    
                    # Write to temporary file first using write_json utility
                    write_json(temp_filepath, storage_data)
                    
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

    def _validate_storage_data(self, data: Dict) -> None:
        """
        Validate data before storage.
        
        Args:
            data (Dict): Data to validate
            
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
        """Compress analysis data for mobile storage"""
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
        """Get filepath for analysis storage."""
        try:
            analyses_dir = current_app.config['ANALYSES_DIR']
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

    def _convert_value(self, value: Any, type_func: type) -> Any:
        """Convert value to specified type, handling various formats."""
        if value in (None, '', 'null'):
            return None
            
        try:
            if isinstance(value, str):
                # Remove any currency or percentage symbols and commas
                clean_value = value.replace('$', '').replace('%', '').replace(',', '').strip()
                return type_func(clean_value)
            return type_func(value)
        except (ValueError, TypeError):
            return None