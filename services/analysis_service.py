import json
import logging
import os
from datetime import datetime
import uuid
from flask import current_app
from utils.json_handler import read_json, write_json
import traceback

class AnalysisService:
    """Service for handling property investment analyses."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    # Public Methods
    def create_analysis(self, analysis_data, user_id):
        """Create a new analysis."""
        try:
            self.logger.info(f"Creating new analysis for user {user_id}")
            
            # Add metadata
            analysis_data['id'] = str(uuid.uuid4())
            analysis_data['user_id'] = user_id
            analysis_data['created_at'] = datetime.now().isoformat()
            analysis_data['updated_at'] = analysis_data['created_at']

            # Calculate results based on analysis type
            calculated_data = self._calculate_analysis(analysis_data)

            # Save analysis
            filename = f"{calculated_data['id']}_{user_id}.json"
            filepath = os.path.join(current_app.config['ANALYSES_DIR'], filename)
            
            os.makedirs(current_app.config['ANALYSES_DIR'], exist_ok=True)
            write_json(filepath, calculated_data)

            self.logger.info(f"Successfully created analysis {calculated_data['id']}")
            return calculated_data

        except Exception as e:
            self.logger.error(f"Error creating analysis: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    def update_analysis(self, analysis_data, user_id):
        """Update an existing analysis."""
        try:
            analysis_id = analysis_data.get('id')
            if not analysis_id:
                raise ValueError("Analysis ID is required for updates")

            self.logger.info(f"Updating analysis {analysis_id} for user {user_id}")

            # Verify ownership
            existing_analysis = self.get_analysis(analysis_id, user_id)
            if not existing_analysis:
                raise ValueError("Analysis not found or access denied")

            # Preserve creation date and update the updated_at timestamp
            analysis_data['created_at'] = existing_analysis['created_at']
            analysis_data['updated_at'] = datetime.now().isoformat()

            # Calculate results
            calculated_data = self._calculate_analysis(analysis_data)

            # Save updated analysis
            filename = f"{analysis_id}_{user_id}.json"
            filepath = os.path.join(current_app.config['ANALYSES_DIR'], filename)
            write_json(filepath, calculated_data)

            self.logger.info(f"Successfully updated analysis {analysis_id}")
            return calculated_data

        except Exception as e:
            self.logger.error(f"Error updating analysis: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    def get_analysis(self, analysis_id, user_id):
        """Get a specific analysis."""
        try:
            self.logger.debug(f"Retrieving analysis {analysis_id} for user {user_id}")
            
            filename = f"{analysis_id}_{user_id}.json"
            filepath = os.path.join(current_app.config['ANALYSES_DIR'], filename)
            
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

    def get_analyses_for_user(self, user_id, page=1, per_page=10):
        """Get paginated list of analyses for a user."""
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
            
            self.logger.debug(f"Found {total_analyses} analyses, returning page {page} of {total_pages}")
            return analyses[start_idx:end_idx], total_pages

        except Exception as e:
            self.logger.error(f"Error retrieving analyses: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    # Private Calculation Methods
    def _calculate_analysis(self, data):
        """Calculate analysis results based on type."""
        try:
            analysis_type = data.get('analysis_type')
            
            if not analysis_type:
                raise ValueError("Analysis type is required")

            self.logger.debug(f"Calculating analysis of type: {analysis_type}")

            # Get calculation functions based on type
            calculation_func = {
                'LTR': self._calculate_ltr,
                'BRRRR': self._calculate_brrrr,
                'PadSplit-LTR': self._calculate_padsplit_ltr,
                'PadSplit-BRRRR': self._calculate_padsplit_brrrr
            }.get(analysis_type)

            if not calculation_func:
                raise ValueError(f"Invalid analysis type: {analysis_type}")

            return calculation_func(data)

        except Exception as e:
            self.logger.error(f"Error calculating analysis: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    def _calculate_base_metrics(self, data):
        """Calculate metrics common to all analysis types."""
        try:
            self.logger.debug("Calculating base metrics")
            
            # Calculate income
            monthly_rent = float(data.get('monthly_rent', 0))
            other_monthly_income = float(data.get('other_monthly_income', 0))
            monthly_income = monthly_rent + other_monthly_income
            
            # Calculate base expenses
            property_taxes = float(data.get('property_taxes', 0))
            insurance = float(data.get('insurance', 0))
            
            # Calculate percentage-based expenses
            management_fee = monthly_rent * float(data.get('management_percentage', 0)) / 100
            capex = monthly_rent * float(data.get('capex_percentage', 0)) / 100
            vacancy = monthly_rent * float(data.get('vacancy_percentage', 0)) / 100
            
            operating_expenses = {
                'property_taxes': property_taxes,
                'insurance': insurance,
                'management': management_fee,
                'capex': capex,
                'vacancy': vacancy
            }
            
            total_operating_expenses = sum(operating_expenses.values())
            
            # Fixed the string formatting
            debug_data = {
                'monthly_rent': monthly_rent,
                'operating_expenses': operating_expenses,
                'total_operating_expenses': total_operating_expenses
            }
            self.logger.debug(f"Operating expenses calculation: {json.dumps(debug_data, indent=2)}")
            
            return {
                'monthly_income': monthly_income,
                'operating_expenses': operating_expenses,
                'total_operating_expenses': total_operating_expenses
            }
                
        except Exception as e:
            self.logger.error(f"Error calculating base metrics: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    def _calculate_ltr(self, data):
        try:
            self.logger.info("Starting LTR calculation")  # Changed to info for better visibility
            
            # Get base metrics
            base_metrics = self._calculate_base_metrics(data)
            loan_metrics = self._calculate_loan_metrics(data.get('loans', []))
            
            # Calculate monthly income and expenses
            monthly_income = base_metrics['monthly_income']
            monthly_rent = float(data.get('monthly_rent', 0))
            
            # Calculate repairs reserve
            repairs_reserve = monthly_rent * float(data.get('repairs_percentage', 0)) / 100

            # Add repairs and HOA to operating expenses
            operating_expenses = base_metrics['operating_expenses']
            operating_expenses['repairs_reserve'] = repairs_reserve
            operating_expenses['hoa_coa_coop'] = float(data.get('hoa_coa_coop', 0))

            # Calculate total monthly expenses
            total_monthly_expenses = (
                sum(operating_expenses.values()) + 
                loan_metrics['total_monthly_payment']
            )

            # Calculate cash flows
            monthly_cash_flow = monthly_income - total_monthly_expenses
            annual_cash_flow = monthly_cash_flow * 12

            # Log the calculations
            self.logger.info(f"""
            LTR Calculation Details:
            Monthly Income: {monthly_income}
            Total Monthly Expenses: {total_monthly_expenses}
            Monthly Cash Flow: {monthly_cash_flow}
            Annual Cash Flow: {annual_cash_flow}
            Operating Expenses: {operating_expenses}
            Loan Metrics: {loan_metrics}
            """)

            # Calculate total cash invested
            total_cash_invested = sum([
                float(data.get('renovation_costs', 0)),
                loan_metrics['total_down_payment'],
                loan_metrics['total_closing_costs'],
                float(data.get('cash_to_seller', 0)),
                float(data.get('assignment_fee', 0)),
                float(data.get('marketing_costs', 0))
            ])

            # Calculate returns
            cash_on_cash_return = (annual_cash_flow / total_cash_invested * 100) if total_cash_invested > 0 else 0

            # Create return object with all calculations
            result = {
                **data,
                'monthly_income': str(round(monthly_income, 2)),
                'monthly_cash_flow': str(round(monthly_cash_flow, 2)),  # Explicitly include monthly cash flow
                'annual_cash_flow': str(round(annual_cash_flow, 2)),
                'total_monthly_expenses': str(round(total_monthly_expenses, 2)),
                'operating_expenses': {k: str(round(v, 2)) for k, v in operating_expenses.items()},
                'total_cash_invested': str(round(total_cash_invested, 2)),
                'cash_on_cash_return': str(round(cash_on_cash_return, 2)),
                'loan_metrics': loan_metrics
            }

            self.logger.info(f"Final LTR result: {json.dumps(result, indent=2)}")
            return result

        except Exception as e:
            self.logger.error(f"Error in _calculate_ltr: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    def _calculate_brrrr(self, data):
        """Calculate BRRRR analysis."""
        try:
            self.logger.debug("Calculating BRRRR analysis")
            
            # Get base metrics
            base_metrics = self._calculate_base_metrics(data)
            
            # Purchase and renovation costs
            purchase_price = float(data.get('purchase_price', 0))
            renovation_costs = float(data.get('renovation_costs', 0))
            total_investment = purchase_price + renovation_costs
            after_repair_value = float(data.get('after_repair_value', 0))

            # Initial financing
            initial_loan_amount = float(data.get('initial_loan_amount', 0))
            initial_down_payment = float(data.get('initial_down_payment', 0))
            initial_interest_rate = float(data.get('initial_interest_rate', 0))
            initial_loan_term = int(data.get('initial_loan_term', 0))
            initial_closing_costs = float(data.get('initial_closing_costs', 0))
            initial_monthly_payment = self._calculate_monthly_payment(
                initial_loan_amount, initial_interest_rate, initial_loan_term
            )

            # Refinance
            refinance_loan_amount = float(data.get('refinance_loan_amount', 0))
            refinance_down_payment = float(data.get('refinance_down_payment', 0))
            refinance_interest_rate = float(data.get('refinance_interest_rate', 0))
            refinance_loan_term = int(data.get('refinance_loan_term', 0))
            refinance_closing_costs = float(data.get('refinance_closing_costs', 0))
            refinance_monthly_payment = self._calculate_monthly_payment(
                refinance_loan_amount, refinance_interest_rate, refinance_loan_term
            )

            # Calculate maintenance reserve
            monthly_rent = float(data.get('monthly_rent', 0))
            maintenance_reserve = monthly_rent * float(data.get('maintenance_percentage', 0)) / 100

            # Update operating expenses
            operating_expenses = base_metrics['operating_expenses']
            operating_expenses['maintenance_reserve'] = maintenance_reserve

            # Calculate total monthly expenses
            total_monthly_expenses = sum(operating_expenses.values()) + refinance_monthly_payment

            # Calculate cash flows
            monthly_cash_flow = base_metrics['monthly_income'] - total_monthly_expenses
            annual_cash_flow = monthly_cash_flow * 12

            # Calculate total cash invested
            total_cash_invested = (
                initial_down_payment + 
                renovation_costs + 
                initial_closing_costs + 
                refinance_down_payment + 
                refinance_closing_costs
            )

            # Calculate returns
            equity_captured = after_repair_value - total_investment
            cash_recouped = refinance_loan_amount - initial_loan_amount
            total_profit = equity_captured + annual_cash_flow
            roi = (total_profit / total_cash_invested * 100) if total_cash_invested > 0 else 0

            all_in_cost = purchase_price + renovation_costs + initial_closing_costs + refinance_closing_costs

            return {
                **data,  # Original data
                'monthly_income': base_metrics['monthly_income'],
                'operating_expenses': operating_expenses,
                'total_monthly_expenses': total_monthly_expenses,
                'monthly_cash_flow': monthly_cash_flow,
                'annual_cash_flow': annual_cash_flow,
                'total_cash_invested': total_cash_invested,
                'equity_captured': equity_captured,
                'cash_recouped': cash_recouped,
                'roi': roi,
                'all_in_cost': all_in_cost,
                'total_investment': total_investment,
                'initial_monthly_payment': initial_monthly_payment,
                'refinance_monthly_payment': refinance_monthly_payment
            }

        except Exception as e:
            self.logger.error(f"Error in _calculate_brrrr: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    def _calculate_padsplit_ltr(self, data):
        """Calculate PadSplit LTR analysis."""
        try:
            self.logger.debug("Calculating PadSplit LTR analysis")
            
            # Get base LTR calculations
            ltr_results = self._calculate_ltr(data)
            
            # Get PadSplit specific expenses
            padsplit_expenses = self._calculate_padsplit_expenses(data)
            
            # Update total expenses and cash flows
            total_monthly_expenses = ltr_results['total_monthly_expenses'] + sum(padsplit_expenses.values())
            monthly_cash_flow = ltr_results['monthly_income'] - total_monthly_expenses
            annual_cash_flow = monthly_cash_flow * 12
            
            # Calculate updated returns
            total_cash_invested = ltr_results['total_cash_invested']
            cash_on_cash_return = (annual_cash_flow / total_cash_invested * 100) if total_cash_invested > 0 else 0
            
            return {
                **ltr_results,  # Base LTR results
                'padsplit_expenses': padsplit_expenses,
                'total_monthly_expenses': total_monthly_expenses,
                'monthly_cash_flow': monthly_cash_flow,
                'annual_cash_flow': annual_cash_flow,
                'cash_on_cash_return': cash_on_cash_return
            }
            
        except Exception as e:
            self.logger.error(f"Error in _calculate_padsplit_ltr: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    def _calculate_padsplit_brrrr(self, data):
        """Calculate PadSplit BRRRR analysis."""
        try:
            self.logger.debug("Calculating PadSplit BRRRR analysis")
            
            # Get base BRRRR calculations
            brrrr_results = self._calculate_brrrr(data)
            
            # Get PadSplit specific expenses
            padsplit_expenses = self._calculate_padsplit_expenses(data)
            
            # Update total expenses and cash flows
            total_monthly_expenses = brrrr_results['total_monthly_expenses'] + sum(padsplit_expenses.values())
            monthly_cash_flow = brrrr_results['monthly_income'] - total_monthly_expenses
            annual_cash_flow = monthly_cash_flow * 12
            
            # Calculate updated returns
            total_cash_invested = brrrr_results['total_cash_invested']
            total_profit = brrrr_results['equity_captured'] + annual_cash_flow
            roi = (total_profit / total_cash_invested * 100) if total_cash_invested > 0 else 0
            
            return {
                **brrrr_results,  # Base BRRRR results
                'padsplit_expenses': padsplit_expenses,
                'total_monthly_expenses': total_monthly_expenses,
                'monthly_cash_flow': monthly_cash_flow,
                'annual_cash_flow': annual_cash_flow,
                'roi': roi
            }
            
        except Exception as e:
            self.logger.error(f"Error in _calculate_padsplit_brrrr: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    def _calculate_padsplit_expenses(self, data):
        """Calculate PadSplit-specific expenses."""
        try:
            self.logger.debug("Calculating PadSplit expenses")
            
            monthly_rent = float(data.get('monthly_rent', 0))
            platform_percentage = float(data.get('padsplit_platform_percentage', 12))  # Default 12%
            
            # Calculate each expense
            platform_fee = monthly_rent * platform_percentage / 100
            utilities = float(data.get('utilities', 0))
            internet = float(data.get('internet', 0))
            cleaning_costs = float(data.get('cleaning_costs', 0))
            pest_control = float(data.get('pest_control', 0))
            landscaping = float(data.get('landscaping', 0))
            
            padsplit_expenses = {
                'platform_fee': platform_fee,
                'utilities': utilities,
                'internet': internet,
                'cleaning_costs': cleaning_costs,
                'pest_control': pest_control,
                'landscaping': landscaping
            }
            
            return padsplit_expenses

        except Exception as e:
            self.logger.error(f"Error calculating PadSplit expenses: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    def _calculate_loan_metrics(self, loans):
        """Calculate metrics for multiple loans."""
        try:
            self.logger.debug("Calculating loan metrics")
            
            total_monthly_payment = 0
            total_down_payment = 0
            total_closing_costs = 0
            loan_details = []
            
            for loan in loans:
                loan_amount = float(loan.get('amount', 0))
                interest_rate = float(loan.get('interest_rate', 0))
                term = int(loan.get('term', 0))
                down_payment = float(loan.get('down_payment', 0))
                closing_costs = float(loan.get('closing_costs', 0))
                
                if loan_amount > 0 and term > 0:
                    monthly_payment = self._calculate_monthly_payment(loan_amount, interest_rate, term)
                    total_monthly_payment += monthly_payment
                    loan_details.append({
                        'name': loan.get('name', 'Unnamed Loan'),
                        'amount': loan_amount,
                        'monthly_payment': monthly_payment,
                        'interest_rate': interest_rate,
                        'term': term,
                        'down_payment': down_payment,
                        'closing_costs': closing_costs
                    })
                
                total_down_payment += down_payment
                total_closing_costs += closing_costs
        
            return {
                'total_monthly_payment': total_monthly_payment,
                'total_down_payment': total_down_payment,
                'total_closing_costs': total_closing_costs,
                'loan_details': loan_details
            }

        except Exception as e:
            self.logger.error(f"Error calculating loan metrics: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    def _calculate_monthly_payment(self, loan_amount, annual_rate, term_months):
        """Calculate monthly loan payment."""
        try:
            if loan_amount <= 0 or term_months <= 0:
                return 0
                
            monthly_rate = (annual_rate / 100) / 12  # Convert annual rate to monthly decimal
            
            # Use the standard mortgage payment formula
            monthly_payment = loan_amount * (
                monthly_rate * (1 + monthly_rate) ** term_months
            ) / (
                (1 + monthly_rate) ** term_months - 1
            )
            
            return round(monthly_payment, 2)
        
        except Exception as e:
            self.logger.error(f"Error calculating monthly payment: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    def delete_analysis(self, analysis_id, user_id):
        """Delete an analysis."""
        try:
            self.logger.info(f"Attempting to delete analysis {analysis_id} for user {user_id}")
            
            filename = f"{analysis_id}_{user_id}.json"
            filepath = os.path.join(current_app.config['ANALYSES_DIR'], filename)
            
            if not os.path.exists(filepath):
                raise ValueError("Analysis not found")
                
            os.remove(filepath)
            self.logger.info(f"Successfully deleted analysis {analysis_id}")
            
            return True

        except Exception as e:
            self.logger.error(f"Error deleting analysis: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    def validate_analysis_data(self, data):
        """Validate analysis input data."""
        try:
            required_fields = ['analysis_type', 'analysis_name', 'property_address']
            missing_fields = [field for field in required_fields if not data.get(field)]
            
            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
            
            # Validate numeric fields
            numeric_fields = [
                'purchase_price', 'after_repair_value', 'monthly_rent',
                'property_taxes', 'insurance', 'management_percentage',
                'capex_percentage', 'vacancy_percentage'
            ]
            
            for field in numeric_fields:
                if field in data:
                    try:
                        value = float(data[field])
                        if value < 0:
                            raise ValueError(f"Field {field} cannot be negative")
                    except (ValueError, TypeError):
                        raise ValueError(f"Invalid numeric value for field {field}")
            
            # Validate percentage fields are between 0 and 100
            percentage_fields = [
                'management_percentage', 'capex_percentage',
                'vacancy_percentage', 'repairs_percentage',
                'maintenance_percentage', 'padsplit_platform_percentage'
            ]
            
            for field in percentage_fields:
                if field in data:
                    value = float(data[field])
                    if value < 0 or value > 100:
                        raise ValueError(f"Percentage field {field} must be between 0 and 100")
            
            return True

        except Exception as e:
            self.logger.error(f"Error validating analysis data: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise