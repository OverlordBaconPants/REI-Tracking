from datetime import datetime
import logging
import os
import uuid
from typing import Dict, List, Optional, Union, Any, Tuple
import traceback
from services.report_generator import generate_report
from flask import current_app
from io import BytesIO
from utils.json_handler import read_json, write_json
from utils.money import Money, Percentage
from services.analysis_calculations import create_analysis

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
        'square_footage': {'type': 'integer'},
        'lot_size': {'type': 'integer'},
        'year_built': {'type': 'integer'},

        # Purchase details
        'purchase_price': {'type': 'integer'},
        'after_repair_value': {'type': 'integer'},
        'renovation_costs': {'type': 'integer'},
        'renovation_duration': {'type': 'integer'},
        'cash_to_seller': {'type': 'integer'},
        'closing_costs': {'type': 'integer'},
        'assignment_fee': {'type': 'integer'},
        'marketing_costs': {'type': 'integer'},

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
        'loan3_loan_closing_costs': {'type': 'integer'}
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    def normalize_data(self, data: Dict) -> Dict:
        """Normalize data to match flat schema with appropriate types."""
        try:
            logger.debug("=== Starting Data Normalization ===")
            
            normalized = {}
            
            # Process each field according to schema
            for field, field_def in self.ANALYSIS_SCHEMA.items():
                field_type = field_def['type']
                value = data.get(field)
                
                # Convert value based on type
                if field_type == 'integer':
                    normalized[field] = self._convert_to_int(value)
                elif field_type == 'float':
                    normalized[field] = self._convert_to_float(value)
                elif field_type == 'string':
                    normalized[field] = str(value) if value is not None else ''
                elif field_def.get('format') == 'datetime' and not value:
                    # Try to parse date strings in YYYY-MM-DD format
                    try:
                        datetime.strptime(value, "%Y-%m-%d")
                    except (ValueError, TypeError):
                        value = datetime.now().strftime("%Y-%m-%d")
                    normalized[field] = value
                elif field_type == 'boolean':
                    # Handle various boolean-like values
                    if isinstance(value, str):
                        normalized[field] = value.lower() in ('true', '1')
                    else:
                        normalized[field] = bool(value)
                    
                # Handle special formats
                if field_def.get('format') == 'uuid' and not value:
                    normalized[field] = str(uuid.uuid4())
                elif field_def.get('format') == 'datetime' and not value:
                    normalized[field] = datetime.now().isoformat()
                    
            logger.debug("=== Data Normalization Complete ===")
            return normalized
        
        except Exception as e:
            logger.error(f"Error normalizing data: {str(e)}")
            logger.error(traceback.format_exc())
            raise ValueError(f"Data normalization failed: {str(e)}")

    def validate_analysis_data(self, data: Dict) -> None:
        """Validate analysis data against schema."""
        try:
            logger.debug("Starting analysis data validation")
            
            # Validate required base fields
            required_fields = {
                'analysis_type': str,
                'analysis_name': str,
                'address': str,
                'monthly_rent': int
            }
            
            for field, expected_type in required_fields.items():
                value = data.get(field)
                if value is None:
                    raise ValueError(f"Missing required field: {field}")
                if not isinstance(value, expected_type) and value is not None:
                    try:
                        if expected_type in (int, float):
                            self._convert_value(value, expected_type)
                        else:
                            raise TypeError
                    except (ValueError, TypeError):
                        raise ValueError(f"Field {field} must be of type {expected_type.__name__}")
            
            # Validate field types according to schema
            for field, value in data.items():
                if field in self.ANALYSIS_SCHEMA and value is not None:
                    self._validate_field_type(field, value)
                    
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
        """Convert value to integer, handling various formats."""
        if value is None:
            return 0
        try:
            if isinstance(value, str):
                clean_value = value.replace('$', '').replace(',', '').strip()
                return int(float(clean_value))
            return int(float(value))
        except (ValueError, TypeError):
            raise ValueError(f"Cannot convert {value} to integer")

    def _convert_to_float(self, value: Any) -> float:
        """Convert value to float, handling various formats."""
        if value is None:
            return 0.0
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

    def _save_analysis(self, analysis_data: Dict, user_id: str) -> None:
        """Save analysis data to storage."""
        try:
            filename = f"{analysis_data['id']}_{user_id}.json"
            filepath = os.path.join(current_app.config['ANALYSES_DIR'], filename)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Save normalized data
            write_json(filepath, analysis_data)
            
        except Exception as e:
            logger.error(f"Error saving analysis: {str(e)}")
            logger.error(traceback.format_exc())
            raise

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