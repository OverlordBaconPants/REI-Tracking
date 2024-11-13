from datetime import datetime
import logging
import os
import uuid
from typing import Dict, List, Tuple, Optional
import traceback

from flask import current_app
from utils.json_handler import read_json, write_json
from utils.money import Money, Percentage
from services.analysis_calculations import create_analysis
from reportlab.platypus import SimpleDocTemplate
from io import BytesIO

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
        try:
            self.logger.info(f"Creating new analysis for user {user_id}")
            
            # Validate incoming data
            self.validate_analysis_data(analysis_data)
            
            # Add metadata
            analysis_data['id'] = str(uuid.uuid4())
            analysis_data['user_id'] = user_id
            analysis_data['created_at'] = datetime.now().isoformat()
            analysis_data['updated_at'] = analysis_data['created_at']

            # Calculate results using analysis_calculations module
            analysis = create_analysis(analysis_data)
            results = self._format_analysis_results(analysis)

            # Save to file
            self._save_analysis(results, user_id)

            self.logger.info(f"Successfully created analysis {results['id']}")
            return results

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
        
        def safe_money(value) -> Money:
            """Safely convert to Money object, defaulting to zero"""
            try:
                return Money(value)
            except (ValueError, TypeError):
                return Money(0)

        def safe_percentage(value) -> Percentage:
            """Safely convert to Percentage object, defaulting to zero"""
            try:
                return Percentage(value)
            except (ValueError, TypeError):
                return Percentage(0)

        def safe_int(value) -> int:
            """Safely convert to integer, defaulting to zero"""
            try:
                return int(float(str(value))) if value else 0
            except (ValueError, TypeError):
                return 0

        standardized = {
            # Metadata fields (keep as strings)
            'id': analysis_data.get('id'),
            'user_id': analysis_data.get('user_id'),
            'created_at': analysis_data.get('created_at'),
            'updated_at': analysis_data.get('updated_at'),
            'analysis_type': analysis_data.get('analysis_type'),
            'analysis_name': analysis_data.get('analysis_name'),
            'property_address': analysis_data.get('property_address'),
            
            # Money fields
            'purchase_price': safe_money(analysis_data.get('purchase_price')),
            'after_repair_value': safe_money(analysis_data.get('after_repair_value')),
            'renovation_costs': safe_money(analysis_data.get('renovation_costs')),
            'monthly_rent': safe_money(analysis_data.get('monthly_rent')),
            'property_taxes': safe_money(analysis_data.get('property_taxes')),
            'insurance': safe_money(analysis_data.get('insurance')),
            'hoa_coa_coop': safe_money(analysis_data.get('hoa_coa_coop')),
            
            # Integer fields
            'renovation_duration': safe_int(analysis_data.get('renovation_duration')),
            'home_square_footage': safe_int(analysis_data.get('home_square_footage')),
            'lot_square_footage': safe_int(analysis_data.get('lot_square_footage')),
            'year_built': safe_int(analysis_data.get('year_built')),
            
            # Percentage fields
            'management_percentage': safe_percentage(analysis_data.get('management_percentage')),
            'capex_percentage': safe_percentage(analysis_data.get('capex_percentage')),
            'vacancy_percentage': safe_percentage(analysis_data.get('vacancy_percentage')),
            'refinance_ltv_percentage': safe_percentage(analysis_data.get('refinance_ltv_percentage')),
            
            # BRRRR Money fields
            'initial_loan_amount': safe_money(analysis_data.get('initial_loan_amount')),
            'initial_down_payment': safe_money(analysis_data.get('initial_down_payment')),
            'initial_closing_costs': safe_money(analysis_data.get('initial_closing_costs')),
            'refinance_loan_amount': safe_money(analysis_data.get('refinance_loan_amount')),
            'refinance_down_payment': safe_money(analysis_data.get('refinance_down_payment')),
            'refinance_closing_costs': safe_money(analysis_data.get('refinance_closing_costs')),
            'max_cash_left': safe_money(analysis_data.get('max_cash_left')),
            
            # BRRRR Percentage fields
            'initial_interest_rate': safe_percentage(analysis_data.get('initial_interest_rate')),
            'refinance_interest_rate': safe_percentage(analysis_data.get('refinance_interest_rate')),
            
            # BRRRR Integer fields
            'initial_loan_term': safe_int(analysis_data.get('initial_loan_term')),
            'refinance_loan_term': safe_int(analysis_data.get('refinance_loan_term')),
            
            # Boolean fields
            'initial_interest_only': bool(analysis_data.get('initial_interest_only', False)),
            
            # PadSplit fields
            'padsplit_platform_percentage': safe_percentage(analysis_data.get('padsplit_platform_percentage')),
            'utilities': safe_money(analysis_data.get('utilities')),
            'internet': safe_money(analysis_data.get('internet')),
            'cleaning_costs': safe_money(analysis_data.get('cleaning_costs')),
            'pest_control': safe_money(analysis_data.get('pest_control')),
            'landscaping': safe_money(analysis_data.get('landscaping')),
            
            # Arrays and objects
            'loans': analysis_data.get('loans', []),
            'operating_expenses': analysis_data.get('operating_expenses', {})
        }
        
        return standardized
    
    def update_analysis(self, analysis_data: Dict, user_id: int) -> Dict:
        """Update an existing analysis or create a new one if type changes."""
        try:
            analysis_id = analysis_data.get('id')
            if not analysis_id:
                raise ValueError("Analysis ID is required for updates")

            self.logger.info(f"Updating analysis {analysis_id} for user {user_id}")

            # Get existing analysis
            existing_analysis = self.get_analysis(analysis_id, user_id)
            if not existing_analysis:
                raise ValueError("Analysis not found or access denied")

            # Check if analysis type is changing
            if analysis_data['analysis_type'] != existing_analysis['analysis_type']:
                # Check if analysis of new type already exists for this property
                property_analyses = self._get_analyses_by_property(analysis_data['property_address'])
                for analysis in property_analyses:
                    if analysis['analysis_type'] == analysis_data['analysis_type']:
                        raise ValueError(f"{analysis_data['analysis_type']} Analysis already exists for this property")

                # Create new analysis with new type
                analysis_data['id'] = str(uuid.uuid4())  # Generate new ID
                analysis_data['created_at'] = datetime.now().isoformat()
                analysis_data['updated_at'] = analysis_data['created_at']
            else:
                # Regular update
                analysis_data['created_at'] = existing_analysis['created_at']
                analysis_data['updated_at'] = datetime.now().isoformat()

            # Validate and standardize data
            self.validate_analysis_data(analysis_data)
            standardized_data = self._create_standardized_analysis(analysis_data)

            # Calculate results
            analysis = create_analysis(standardized_data)
            results = self._format_analysis_results(analysis)

            # Save analysis
            self._save_analysis(results, user_id)

            self.logger.info(f"Successfully {'created new' if analysis_id != results['id'] else 'updated'} analysis {results['id']}")
            return results

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

            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer)
            
            # Generate report content here
            # This would need to be implemented based on your reporting requirements
            
            return buffer

        except Exception as e:
            self.logger.error(f"Error generating PDF report: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    def validate_analysis_data(self, data: Dict) -> bool:
        """
        Validate analysis input data.
        
        Args:
            data: Dictionary containing analysis data to validate
            
        Returns:
            True if valid, raises ValueError if invalid
        """
        try:
            # Required fields
            required_fields = ['analysis_type', 'analysis_name', 'property_address']
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

            # Monetary fields
            monetary_fields = [
                'purchase_price', 'after_repair_value', 'monthly_rent',
                'property_taxes', 'insurance'
            ]
            for field in monetary_fields:
                if field in data:
                    try:
                        Money(data[field])
                    except ValueError:
                        raise ValueError(f"Invalid monetary value for {field}")

            # Percentage fields
            percentage_fields = [
                'management_percentage', 'capex_percentage',
                'vacancy_percentage', 'repairs_percentage',
                'repairs_percentage', 'padsplit_platform_percentage'
            ]
            for field in percentage_fields:
                if field in data:
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

    def _format_analysis_results(self, analysis) -> Dict:
        """Format analysis results for storage/response."""
        try:
            # Create base dictionary with all possible fields
            results = {
                # Metadata
                'id': analysis.data['id'],
                'user_id': analysis.data['user_id'],
                'created_at': analysis.data['created_at'],
                'updated_at': analysis.data['updated_at'],
                'analysis_type': analysis.data['analysis_type'],
                'analysis_name': analysis.data['analysis_name'],
                'property_address': analysis.data['property_address'],
                
                # Property Details
                'home_square_footage': analysis.data.get('home_square_footage'),
                'lot_square_footage': analysis.data.get('lot_square_footage'),
                'year_built': analysis.data.get('year_built'),
                
                # Purchase Details
                'purchase_price': str(analysis.purchase_price) if analysis.purchase_price else None,
                'after_repair_value': str(analysis.after_repair_value) if analysis.after_repair_value else None,
                'renovation_costs': str(analysis.renovation_costs) if analysis.renovation_costs else None,
                'renovation_duration': analysis.data.get('renovation_duration'),
                'cash_to_seller': str(Money(analysis.data.get('cash_to_seller', 0))),
                'closing_costs': str(Money(analysis.data.get('closing_costs', 0))),
                'assignment_fee': str(Money(analysis.data.get('assignment_fee', 0))),
                'marketing_costs': str(Money(analysis.data.get('marketing_costs', 0))),
                
                # Income & Operating Details
                'monthly_rent': str(analysis.monthly_rent) if analysis.monthly_rent else None,
                'monthly_cash_flow': str(analysis.calculate_monthly_cash_flow()),
                'annual_cash_flow': str(analysis.annual_cash_flow),
                'total_operating_expenses': str(analysis.operating_expenses.total),
                'property_taxes': str(Money(analysis.data.get('property_taxes', 0))),
                'insurance': str(Money(analysis.data.get('insurance', 0))),
                'hoa_coa_coop': str(Money(analysis.data.get('hoa_coa_coop', 0))),
                
                # Operating Percentages
                'management_percentage': str(Percentage(analysis.data.get('management_percentage', 0))),
                'capex_percentage': str(Percentage(analysis.data.get('capex_percentage', 0))),
                'vacancy_percentage': str(Percentage(analysis.data.get('vacancy_percentage', 0))),
                'repairs_percentage': str(Percentage(analysis.data.get('repairs_percentage', 0))),
                
                # BRRRR-specific fields
                'initial_loan_amount': str(Money(analysis.data.get('initial_loan_amount', 0))),
                'initial_down_payment': str(Money(analysis.data.get('initial_down_payment', 0))),
                'initial_interest_rate': str(Percentage(analysis.data.get('initial_interest_rate', 0))),
                'initial_loan_term': analysis.data.get('initial_loan_term', 0),
                'initial_closing_costs': str(Money(analysis.data.get('initial_closing_costs', 0))),
                'initial_interest_only': analysis.data.get('initial_interest_only', False),
                'initial_monthly_payment': str(Money(analysis.data.get('initial_monthly_payment', 0))),
                
                'refinance_loan_amount': str(Money(analysis.data.get('refinance_loan_amount', 0))),
                'refinance_down_payment': str(Money(analysis.data.get('refinance_down_payment', 0))),
                'refinance_interest_rate': str(Percentage(analysis.data.get('refinance_interest_rate', 0))),
                'refinance_loan_term': analysis.data.get('refinance_loan_term', 0),
                'refinance_closing_costs': str(Money(analysis.data.get('refinance_closing_costs', 0))),
                'refinance_monthly_payment': str(Money(analysis.data.get('refinance_monthly_payment', 0))),
                'refinance_ltv_percentage': str(Percentage(analysis.data.get('refinance_ltv_percentage', 0))),
                'max_cash_left': str(Money(analysis.data.get('max_cash_left', 0))),
                
                # Performance metrics
                'equity_captured': str(analysis.equity_captured) if hasattr(analysis, 'equity_captured') else None,
                'cash_recouped': str(analysis.cash_recouped) if hasattr(analysis, 'cash_recouped') else None,
                'total_project_costs': str(analysis.total_project_costs) if hasattr(analysis, 'total_project_costs') else None,
                'total_cash_invested': str(analysis.total_cash_invested) if hasattr(analysis, 'total_cash_invested') else None,
                'cash_on_cash_return': str(analysis.cash_on_cash_return) if hasattr(analysis, 'cash_on_cash_return') else None,
                'roi': str(analysis.roi),
                
                # PadSplit-specific fields
                'padsplit_platform_percentage': str(Percentage(analysis.data.get('padsplit_platform_percentage', 0))),
                'utilities': str(Money(analysis.data.get('utilities', 0))),
                'internet': str(Money(analysis.data.get('internet', 0))),
                'cleaning_costs': str(Money(analysis.data.get('cleaning_costs', 0))),
                'pest_control': str(Money(analysis.data.get('pest_control', 0))),
                'landscaping': str(Money(analysis.data.get('landscaping', 0))),
                
                # Arrays and objects
                'loans': analysis.data.get('loans', []),
                'operating_expenses': analysis.data.get('operating_expenses', {})
            }

            # Remove empty or null values only for arrays and objects
            for key in ['loans', 'operating_expenses']:
                if not results[key]:
                    results[key] = None

            return results

        except Exception as e:
            self.logger.error(f"Error formatting analysis results: {str(e)}")
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