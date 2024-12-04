from datetime import datetime
import logging
import os
import uuid
from typing import Dict, List, Tuple, Optional
import traceback
from services.report_generator import generate_report
from flask import current_app
from flask_login import current_user
from io import BytesIO
from utils.json_handler import read_json, write_json
from utils.money import Money, Percentage
from services.analysis_calculations import (
    Analysis,
    BRRRRAnalysis,
    LTRAnalysis, 
    PadSplitBRRRRAnalysis,
    PadSplitLTRAnalysis,
    Loan,
    LoanCollection,
    PropertyDetails,
    PurchaseDetails,
    OperatingExpenses,
    PadSplitOperatingExpenses
)

class AnalysisService:
    """Service for handling property investment analyses."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def create_analysis(self, analysis_data: Dict, user_id: int) -> Dict:
        """
        Create a new analysis.
        
        Args:
            analysis_data: Dictionary containing analysis parameters
            user_id: ID of the user creating the analysis
            
        Returns:
            Dictionary containing the calculated analysis results
        """

        """Add user_id from current_user"""
        analysis_data['user_id'] = current_user.id

        try:
            self.logger.info(f"Creating new analysis for user {user_id}")
            
            # Validate incoming data
            self.validate_analysis_data(analysis_data)
            
            # Add metadata
            analysis_data['id'] = str(uuid.uuid4())
            analysis_data['user_id'] = user_id
            analysis_data['created_at'] = datetime.now().isoformat()
            analysis_data['updated_at'] = analysis_data['created_at']

            # Standardize and calculate results
            standardized_data = self._create_standardized_analysis(analysis_data)

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
    
    def update_analysis(self, analysis_data: Dict, user_id: int) -> Dict:
        """Update an existing analysis or create a new one if type changes."""

        """Add user_id from current_user"""
        analysis_data['user_id'] = current_user.id

        try:
            analysis_id = analysis_data.get('id')
            if not analysis_id:
                raise ValueError("Analysis ID is required for updates")

            self.logger.info(f"Updating analysis {analysis_id} for user {user_id}")

            # Get existing analysis
            existing_analysis = self.get_analysis(analysis_id, user_id)
            if not existing_analysis:
                raise ValueError("Analysis not found or access denied")

            # Check if we should create a new analysis
            create_new = analysis_data.get('create_new', False)
            if create_new:
                # Check if analysis of new type already exists for this property
                property_analyses = self._get_analyses_by_property(analysis_data['property_address'])
                for analysis in property_analyses:
                    if analysis['analysis_type'] == analysis_data['analysis_type']:
                        raise ValueError(f"{analysis_data['analysis_type']} Analysis already exists for this property")

                # Create new analysis with new type
                analysis_data['id'] = str(uuid.uuid4())
                analysis_data['created_at'] = datetime.now().isoformat()
                analysis_data['updated_at'] = analysis_data['created_at']
            else:
                # Regular update
                analysis_data['created_at'] = existing_analysis['created_at']
                analysis_data['updated_at'] = datetime.now().isoformat()

            # Validate and standardize data
            self.validate_analysis_data(analysis_data)
            standardized_data = self._create_standardized_analysis(analysis_data)

            # Save analysis
            self._save_analysis(standardized_data, user_id)

            self.logger.info(f"Successfully {'created new' if create_new else 'updated'} analysis {standardized_data['id']}")
            return standardized_data

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