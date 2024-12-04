from datetime import datetime
import logging
import os
import uuid
from typing import Dict, Optional
import traceback
from services.report_generator import generate_report
from flask import current_app
from flask_login import current_user
from io import BytesIO
from utils.json_handler import read_json, write_json
from utils.money import Money, Percentage
from services.analysis_calculations import create_analysis
from typing import Dict, List, Tuple, Optional

class AnalysisService:
    """Service for handling property investment analyses."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    def create_analysis(self, analysis_data: Dict, user_id: int) -> Dict:
        """
        Create a new analysis.
        
        Args:
            analysis_data: Dictionary containing analysis parameters
            user_id: ID of the user creating the analysis
            
        Returns:
            Dictionary containing the calculated analysis results
        """
        try:
            self.logger.info(f"Creating new analysis for user {user_id}")
            
            # Validate incoming data
            self.validate_analysis_data(analysis_data)
            
            # Add metadata
            analysis_data['id'] = str(uuid.uuid4())
            analysis_data['user_id'] = user_id
            analysis_data['created_at'] = datetime.now().isoformat()
            analysis_data['updated_at'] = analysis_data['created_at']

            # Create Analysis object and perform calculations
            analysis = create_analysis(analysis_data)
            
            # Get report data which includes all calculated values
            report_data = analysis.get_report_data()
            
            # Convert report data back to dict format for storage
            standardized_data = self._convert_report_data_to_dict(report_data, analysis_data)

            # Save to file
            self._save_analysis(standardized_data, user_id)

            self.logger.info(f"Successfully created analysis {standardized_data['id']}")
            return standardized_data

        except Exception as e:
            self.logger.error(f"Error creating analysis: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    def _get_analyses_by_property(self, property_address: str) -> List[Dict]:
        """Get all analyses for a given property address."""
        try:
            analyses_dir = current_app.config['ANALYSES_DIR']
            property_analyses = []
            
            for filename in os.listdir(analyses_dir):
                if filename.endswith('.json'):
                    analysis_data = read_json(os.path.join(analyses_dir, filename))
                    if analysis_data.get('property_address') == property_address:
                        property_analyses.append(analysis_data)
            
            return property_analyses
        except Exception as e:
            self.logger.error(f"Error getting analyses by property: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    def _create_standardized_analysis(self, analysis_data: Dict) -> Dict:
        """Create a standardized analysis object with all possible fields."""
        
        # Define defaults for all possible fields
        defaults = {
            # Basic property details
            'home_square_footage': 0,
            'lot_square_footage': 0,
            'year_built': 0,
            
            # Purchase/financial details
            'purchase_price': 0,
            'after_repair_value': 0,
            'renovation_costs': 0,
            'renovation_duration': 0,
            'cash_to_seller': 0,
            'closing_costs': 0,
            'assignment_fee': 0,
            'marketing_costs': 0,
            'monthly_rent': 0,
            'max_cash_left': 0,
            
            # Operating expenses
            'property_taxes': 0,
            'insurance': 0,
            'hoa_coa_coop': 0,
            'management_percentage': 0,
            'capex_percentage': 0,
            'vacancy_percentage': 0,
            'repairs_percentage': 0,
            
            # BRRRR-specific
            'initial_loan_amount': 0,
            'initial_down_payment': 0,
            'initial_interest_rate': 0,
            'initial_loan_term': 0,
            'initial_closing_costs': 0,
            'initial_interest_only': False,
            'refinance_loan_amount': 0,
            'refinance_down_payment': 0,
            'refinance_interest_rate': 0,
            'refinance_loan_term': 0,
            'refinance_closing_costs': 0,
            'refinance_ltv_percentage': 0,
            
            # PadSplit-specific
            'padsplit_platform_percentage': 0,
            'utilities': 0,
            'internet': 0,
            'cleaning_costs': 0,
            'pest_control': 0,
            'landscaping': 0
        }

        def safe_money(value) -> str:
            """Safely convert to Money string, defaulting to '$0.00'"""
            try:
                if isinstance(value, str):
                    # If already formatted as currency, return as is
                    if value.startswith('$'):
                        return value
                return str(Money(value))
            except (ValueError, TypeError):
                return '$0.00'

        def safe_percentage(value) -> str:
            """Safely convert to Percentage string, defaulting to '0.00%'"""
            try:
                if isinstance(value, str):
                    # If already formatted as percentage, return as is
                    if value.endswith('%'):
                        return value
                return str(Percentage(value))
            except (ValueError, TypeError):
                return '0.00%'

        def safe_int(value) -> int:
            """Safely convert to integer, defaulting to zero"""
            try:
                if isinstance(value, str):
                    # Handle case where string might be empty or 'null'
                    if not value or value.lower() == 'null':
                        return 0
                return int(float(str(value))) if value else 0
            except (ValueError, TypeError):
                return 0

        # Create flattened structure matching the JSON format
        standardized = {
            # Metadata
            'id': analysis_data.get('id'),
            'user_id': analysis_data.get('user_id'),
            'created_at': analysis_data.get('created_at'),
            'updated_at': analysis_data.get('updated_at'),
            'analysis_type': analysis_data.get('analysis_type'),
            'analysis_name': analysis_data.get('analysis_name'),
            'property_address': analysis_data.get('property_address'),

            # Property Details
            'home_square_footage': safe_int(analysis_data.get('home_square_footage')),
            'lot_square_footage': safe_int(analysis_data.get('lot_square_footage')),
            'year_built': safe_int(analysis_data.get('year_built')),

            # Purchase Details
            'purchase_price': safe_money(analysis_data.get('purchase_price')),
            'after_repair_value': safe_money(analysis_data.get('after_repair_value')),
            'renovation_costs': safe_money(analysis_data.get('renovation_costs')),
            'renovation_duration': safe_int(analysis_data.get('renovation_duration')),
            'cash_to_seller': safe_money(analysis_data.get('cash_to_seller')),
            'closing_costs': safe_money(analysis_data.get('closing_costs')),
            'assignment_fee': safe_money(analysis_data.get('assignment_fee')),
            'marketing_costs': safe_money(analysis_data.get('marketing_costs')),

            # Financial Metrics
            'monthly_rent': safe_money(analysis_data.get('monthly_rent')),
            'monthly_cash_flow': safe_money(analysis_data.get('monthly_cash_flow')),
            'annual_cash_flow': safe_money(analysis_data.get('annual_cash_flow')),
            'cash_on_cash_return': safe_percentage(analysis_data.get('cash_on_cash_return')),
            'roi': str(analysis_data.get('roi', 'Error')),  # Special handling for ROI
            'equity_captured': safe_money(analysis_data.get('equity_captured')),
            'cash_recouped': safe_money(analysis_data.get('cash_recouped')),
            'total_project_costs': safe_money(analysis_data.get('total_project_costs')),
            'total_cash_invested': safe_money(analysis_data.get('total_cash_invested')),
            'max_cash_left': safe_money(analysis_data.get('max_cash_left')),

            # Operating Expenses
            'property_taxes': safe_money(analysis_data.get('property_taxes')),
            'insurance': safe_money(analysis_data.get('insurance')),
            'hoa_coa_coop': safe_money(analysis_data.get('hoa_coa_coop')),
            'management_percentage': safe_percentage(analysis_data.get('management_percentage')),
            'capex_percentage': safe_percentage(analysis_data.get('capex_percentage')),
            'vacancy_percentage': safe_percentage(analysis_data.get('vacancy_percentage')),
            'repairs_percentage': safe_percentage(analysis_data.get('repairs_percentage')),
            'total_monthly_expenses': safe_money(analysis_data.get('total_operating_expenses')),

            # PadSplit-specific fields
            'padsplit_platform_percentage': safe_percentage(analysis_data.get('padsplit_platform_percentage')),
            'utilities': safe_money(analysis_data.get('utilities')),
            'internet': safe_money(analysis_data.get('internet')),
            'cleaning_costs': safe_money(analysis_data.get('cleaning_costs')),
            'pest_control': safe_money(analysis_data.get('pest_control')),
            'landscaping': safe_money(analysis_data.get('landscaping')),

            # Loan fields
            'initial_loan_amount': safe_money(analysis_data.get('initial_loan_amount')),
            'initial_down_payment': safe_money(analysis_data.get('initial_down_payment')),
            'initial_interest_rate': safe_percentage(analysis_data.get('initial_interest_rate')),
            'initial_loan_term': safe_int(analysis_data.get('initial_loan_term')),
            'initial_closing_costs': safe_money(analysis_data.get('initial_closing_costs')),
            'initial_interest_only': bool(analysis_data.get('initial_interest_only', False)),
            'initial_monthly_payment': safe_money(analysis_data.get('initial_monthly_payment')),

            'refinance_loan_amount': safe_money(analysis_data.get('refinance_loan_amount')),
            'refinance_down_payment': safe_money(analysis_data.get('refinance_down_payment')),
            'refinance_interest_rate': safe_percentage(analysis_data.get('refinance_interest_rate')),
            'refinance_loan_term': safe_int(analysis_data.get('refinance_loan_term')),
            'refinance_closing_costs': safe_money(analysis_data.get('refinance_closing_costs')),
            'refinance_monthly_payment': safe_money(analysis_data.get('refinance_monthly_payment')),
            'refinance_ltv_percentage': safe_percentage(analysis_data.get('refinance_ltv_percentage')),

            # Handle additional loans array
            'loans': self._process_additional_loans(analysis_data.get('loans', []))
        }

        # Apply defaults for any missing fields
        standardized = {**defaults, **analysis_data}

        return standardized

    def _process_additional_loans(self, loans_data: List) -> List[Dict]:
        """Process additional loans data."""
        if not loans_data or not isinstance(loans_data, list):
            return []
            
        processed_loans = []
        for loan in loans_data:
            processed_loan = {
                'name': loan.get('name', ''),
                'amount': str(Money(loan.get('amount', 0))),
                'interest_rate': str(Percentage(loan.get('interest_rate', 0))),
                'term': int(loan.get('term', 0)),
                'down_payment': str(Money(loan.get('down_payment', 0))),
                'closing_costs': str(Money(loan.get('closing_costs', 0)))
            }
            processed_loans.append(processed_loan)
        
        return processed_loans

    def _convert_report_data_to_dict(self, report_data: 'AnalysisReportData', original_data: Dict) -> Dict:
        """Convert report data to storage format while preserving original metadata."""
        self.logger.debug("=== Converting Report Data to Dict ===")
        self.logger.debug(f"Original loan data:")
        self.logger.debug(f"Initial loan amount: {original_data.get('initial_loan_amount')}")
        self.logger.debug(f"Refinance loan amount: {original_data.get('refinance_loan_amount')}")

        storage_data = {
            # Preserve metadata
            'id': original_data.get('id'),
            'user_id': original_data.get('user_id'),
            'created_at': original_data.get('created_at'),
            'updated_at': original_data.get('updated_at'),
            
            # Explicitly preserve all loan-related fields
            'initial_loan_amount': original_data.get('initial_loan_amount'),
            'initial_interest_rate': original_data.get('initial_interest_rate'),
            'initial_loan_term': original_data.get('initial_loan_term'),
            'initial_down_payment': original_data.get('initial_down_payment'),
            'initial_closing_costs': original_data.get('initial_closing_costs'),
            'initial_interest_only': original_data.get('initial_interest_only'),
            'initial_monthly_payment': original_data.get('initial_monthly_payment'),
            
            'refinance_loan_amount': original_data.get('refinance_loan_amount'),
            'refinance_interest_rate': original_data.get('refinance_interest_rate'),
            'refinance_loan_term': original_data.get('refinance_loan_term'),
            'refinance_down_payment': original_data.get('refinance_down_payment'),
            'refinance_closing_costs': original_data.get('refinance_closing_costs'),
            'refinance_ltv_percentage': original_data.get('refinance_ltv_percentage'),
            'refinance_monthly_payment': original_data.get('refinance_monthly_payment'),
            
            # Basic info
            'analysis_name': report_data.analysis_name,
            'analysis_type': report_data.analysis_type,
            'property_address': report_data.property_address,
            
            # Convert sections to flat structure
            **self._flatten_sections(report_data.sections)
        }
        
        self.logger.debug("=== Converted Data ===")
        self.logger.debug(f"Stored loan data:")
        self.logger.debug(f"Initial loan amount: {storage_data.get('initial_loan_amount')}")
        self.logger.debug(f"Refinance loan amount: {storage_data.get('refinance_loan_amount')}")
        
        return storage_data

    def _flatten_sections(self, sections: List['ReportSection']) -> Dict:
        """Convert report sections into a flat dictionary structure."""
        flattened = {}
        for section in sections:
            for label, value in section.data:
                # Convert label to snake_case for storage
                key = self._to_snake_case(label)
                flattened[key] = value
        return flattened

    @staticmethod
    def _to_snake_case(text: str) -> str:
        """Convert a label to snake_case for storage."""
        # Remove special characters and convert spaces to underscores
        return text.lower().replace(' ', '_').replace('/', '_').replace('-', '_')
    
    def update_analysis(self, analysis_data: Dict, user_id: int) -> Dict:
        try:
            analysis_id = analysis_data.get('id')
            if not analysis_id:
                raise ValueError("Analysis ID is required for updates")

            self.logger.debug("=== Starting Analysis Update ===")
            self.logger.debug(f"Incoming loan data:")
            self.logger.debug(f"Initial loan amount: {analysis_data.get('initial_loan_amount')}")
            self.logger.debug(f"Refinance loan amount: {analysis_data.get('refinance_loan_amount')}")
            self.logger.debug(f"Full analysis data: {analysis_data}")

            # Validate and create Analysis object
            self.validate_analysis_data(analysis_data)
            analysis = create_analysis(analysis_data)
            
            # Get report data with all calculations
            report_data = analysis.get_report_data()
            self.logger.debug(f"Generated report data: {report_data}")
            
            # Convert to storage format
            updated_data = self._convert_report_data_to_dict(report_data, analysis_data)
            self.logger.debug(f"Converted storage data: {updated_data}")
            
            updated_data['updated_at'] = datetime.now().isoformat()

            # Save analysis
            self._save_analysis(updated_data, user_id)

            self.logger.debug("=== Completed Analysis Update ===")
            self.logger.debug(f"Final data being returned: {updated_data}")

            return {
                'success': True,
                'message': 'Analysis updated successfully',
                'analysis': updated_data
            }

        except Exception as e:
            self.logger.error(f"Error updating analysis: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    def get_analysis(self, analysis_id: str, user_id: int) -> Optional[Dict]:
        """
        Get a specific analysis.
        
        Args:
            analysis_id: ID of the analysis to retrieve
            user_id: ID of the user requesting the analysis
            
        Returns:
            Dictionary containing the analysis data or None if not found
        """
        try:
            self.logger.debug(f"Retrieving analysis {analysis_id} for user {user_id}")
            
            filepath = self._get_analysis_filepath(analysis_id, user_id)
            if not os.path.exists(filepath):
                self.logger.warning(f"Analysis file not found: {filepath}")
                return None
                
            analysis_data = read_json(filepath)
            self.logger.debug(f"Successfully retrieved analysis {analysis_id}")
            return analysis_data

        except Exception as e:
            self.logger.error(f"Error retrieving analysis: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    def get_analyses_for_user(self, user_id: int, page: int = 1, per_page: int = 10) -> Tuple[List[Dict], int]:
        """
        Get paginated list of analyses for a user.
        
        Args:
            user_id: ID of the user
            page: Page number to retrieve
            per_page: Number of analyses per page
            
        Returns:
            Tuple of (list of analyses, total number of pages)
        """
        try:
            self.logger.debug(f"Retrieving analyses for user {user_id} (page {page})")
            
            analyses_dir = current_app.config['ANALYSES_DIR']
            if not os.path.exists(analyses_dir):
                return [], 0

            # Get all analyses for user
            analyses = []
            for filename in os.listdir(analyses_dir):
                if filename.endswith(f"_{user_id}.json"):
                    analysis_data = read_json(os.path.join(analyses_dir, filename))
                    analyses.append(analysis_data)

            # Sort by updated_at timestamp, newest first
            analyses.sort(key=lambda x: x.get('updated_at', ''), reverse=True)

            # Calculate pagination
            total_analyses = len(analyses)
            total_pages = max((total_analyses + per_page - 1) // per_page, 1)
            
            # Get requested page
            start_idx = (page - 1) * per_page
            end_idx = min(start_idx + per_page, total_analyses)
            
            return analyses[start_idx:end_idx], total_pages

        except Exception as e:
            self.logger.error(f"Error retrieving analyses: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    def delete_analysis(self, analysis_id: str, user_id: int) -> bool:
        """
        Delete an analysis.
        
        Args:
            analysis_id: ID of the analysis to delete
            user_id: ID of the user requesting deletion
            
        Returns:
            True if successful, raises exception otherwise
        """
        try:
            self.logger.info(f"Attempting to delete analysis {analysis_id} for user {user_id}")
            
            filepath = self._get_analysis_filepath(analysis_id, user_id)
            if not os.path.exists(filepath):
                raise ValueError("Analysis not found")
                
            os.remove(filepath)
            self.logger.info(f"Successfully deleted analysis {analysis_id}")
            return True

        except Exception as e:
            self.logger.error(f"Error deleting analysis: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    def generate_pdf_report(self, analysis_id: str, user_id: int) -> BytesIO:
        """
        Generate a PDF report for an analysis.
        
        Args:
            analysis_id: ID of the analysis
            user_id: ID of the user requesting the report
            
        Returns:
            BytesIO buffer containing the PDF
        """
        try:
            analysis_data = self.get_analysis(analysis_id, user_id)
            if not analysis_data:
                raise ValueError("Analysis not found")

            # Add current date to the analysis data
            analysis_data['generated_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Generate report using our new report generator
            buffer = generate_report(analysis_data, report_type='analysis')
            
            return buffer

        except Exception as e:
            self.logger.error(f"Error generating PDF report: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    def validate_analysis_data(self, data: Dict) -> bool:
        """Validate analysis input data."""
        try:
            # Required fields
            required_fields = ['analysis_type', 'analysis_name']
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

            # Type-specific required fields
            if data.get('analysis_type') in ['LTR', 'PadSplit LTR']:
                # Validate LTR-specific fields
                ltr_required = ['purchase_price', 'monthly_rent']
                missing_ltr = [field for field in ltr_required if not data.get(field)]
                if missing_ltr:
                    raise ValueError(f"Missing required LTR fields: {', '.join(missing_ltr)}")

            elif data.get('analysis_type') in ['BRRRR', 'PadSplit BRRRR']:
                # Validate BRRRR-specific fields
                brrrr_required = ['purchase_price', 'after_repair_value', 'renovation_costs']
                missing_brrrr = [field for field in brrrr_required if not data.get(field)]
                if missing_brrrr:
                    raise ValueError(f"Missing required BRRRR fields: {', '.join(missing_brrrr)}")

            # Validate PadSplit-specific fields if applicable
            defaults = {
                'padsplit_platform_percentage': 0,
                'utilities': 0,
                'internet': 0,
                'cleaning_costs': 0,
                'pest_control': 0,
                'landscaping': 0
            }

            for field, default in defaults.items():
                if field not in data:
                    data[field] = default

            # Validate all money fields are valid
            money_fields = [
                'purchase_price', 'after_repair_value', 'renovation_costs',
                'monthly_rent', 'property_taxes', 'insurance',
                'utilities', 'internet', 'cleaning_costs',
                'pest_control', 'landscaping'
            ]
            for field in money_fields:
                if field in data and data[field]:
                    try:
                        Money(data[field])
                    except ValueError:
                        raise ValueError(f"Invalid monetary value for {field}")

            # Validate all percentage fields
            percentage_fields = [
                'management_percentage', 'capex_percentage',
                'vacancy_percentage', 'repairs_percentage',
                'padsplit_platform_percentage', 'refinance_ltv_percentage'
            ]
            for field in percentage_fields:
                if field in data and data[field]:
                    try:
                        percentage = Percentage(data[field])
                        if percentage.value < 0 or percentage.value > 100:
                            raise ValueError(f"Percentage {field} must be between 0 and 100")
                    except ValueError:
                        raise ValueError(f"Invalid percentage value for {field}")

            return True

        except Exception as e:
            self.logger.error(f"Error validating analysis data: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    def _save_analysis(self, analysis_data: Dict, user_id: int) -> None:
        """
        Save analysis data to file.
        
        Args:
            analysis_data: Dictionary containing analysis data
            user_id: ID of the user owning the analysis
        """
        filename = f"{analysis_data['id']}_{user_id}.json"
        filepath = os.path.join(current_app.config['ANALYSES_DIR'], filename)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        write_json(filepath, analysis_data)

    def _get_analysis_filepath(self, analysis_id: str, user_id: int) -> str:
        """
        Get the filepath for an analysis.
        
        Args:
            analysis_id: ID of the analysis
            user_id: ID of the user owning the analysis
            
        Returns:
            Full filepath
        """
        return os.path.join(
            current_app.config['ANALYSES_DIR'],
            f"{analysis_id}_{user_id}.json"
        )