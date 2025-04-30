from typing import List, Dict, Any, Optional, Tuple
from datetime import date
import logging
from src.utils.money import Money, Percentage
from src.utils.calculations.loan_details import LoanDetails
from src.models.loan import Loan, BalloonPayment

logger = logging.getLogger(__name__)

class LoanComparison:
    """
    Utility class for comparing different loan options.
    
    This class provides methods for comparing loans with different terms,
    interest rates, and payment structures, to help users make informed decisions.
    """
    
    @staticmethod
    def compare_loans(loan_options: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare multiple loan options and provide detailed analysis.
        
        Args:
            loan_options: List of dictionaries containing loan data for comparison
            
        Returns:
            Dict: Comparison results with metrics for each loan option
        """
        if not loan_options:
            return {}
            
        comparison = {
            'loans': [],
            'metrics': {},
            'recommendation': None
        }
        
        # Create temporary loan objects for each option
        loans = []
        for i, option_data in enumerate(loan_options):
            try:
                # Handle simplified loan options format from tests
                if 'loan_type' not in option_data and 'property_id' not in option_data:
                    # Create a minimal loan dictionary with required fields
                    loan_dict = {
                        'property_id': 'test_property',
                        'loan_type': 'initial',
                        'amount': option_data.get('amount'),
                        'interest_rate': option_data.get('interest_rate'),
                        'term_months': option_data.get('term_months'),
                        'start_date': option_data.get('start_date', date.today().isoformat()),
                        'is_interest_only': option_data.get('is_interest_only', False),
                        'name': option_data.get('name')
                    }
                else:
                    loan_dict = option_data.copy()
                
                # Create a loan object without saving to the repository
                loan = Loan.from_dict(loan_dict)
                loan_details = loan.to_loan_details()
                
                # Calculate key metrics
                monthly_payment = loan_details.calculate_payment().total
                amount_value = loan.get_amount_as_money().dollars
                total_payments = monthly_payment.dollars * loan.term_months
                total_interest = total_payments - amount_value
                
                # Calculate interest to principal ratio
                interest_to_principal_ratio = total_interest / amount_value
                
                # Calculate monthly payment as percentage of loan amount
                payment_to_amount_ratio = (monthly_payment.dollars * 12) / amount_value
                
                # Add to comparison
                loans.append(loan)
                comparison['loans'].append({
                    'id': i,
                    'name': loan.name or f"Option {i+1}",
                    'amount': str(loan.amount),
                    'interest_rate': str(loan.interest_rate),
                    'term_months': loan.term_months,
                    'term_years': round(loan.term_months / 12, 2),
                    'is_interest_only': loan.is_interest_only,
                    'has_balloon': loan.balloon_payment is not None,
                    'monthly_payment': monthly_payment,  # Keep as Money object
                    'annual_payment': f"${monthly_payment.dollars * 12:,.2f}",
                    'total_payments': f"${total_payments:,.2f}",
                    'total_interest': Money(total_interest),  # Keep as Money object
                    'interest_to_principal_ratio': f"{interest_to_principal_ratio:.2%}",
                    'payment_to_amount_ratio': f"{payment_to_amount_ratio:.2%}",
                    'balloon_details': LoanComparison._get_balloon_details(loan) if loan.balloon_payment else None
                })
            except Exception as e:
                # Log the error but continue processing other loans
                logger.error(f"Error processing loan option {i}: {str(e)}")
                continue
                
        # Calculate comparative metrics
        if len(loans) > 1:
            comparison['metrics'] = LoanComparison._calculate_comparative_metrics(comparison['loans'])
            comparison['recommendation'] = LoanComparison._generate_recommendation(comparison['loans'], comparison['metrics'])
            
        return comparison
    
    @staticmethod
    def _calculate_comparative_metrics(loan_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate comparative metrics between loan options.
        
        Args:
            loan_data: List of dictionaries containing loan metrics
            
        Returns:
            Dict: Comparative metrics
        """
        metrics = {
            'lowest_monthly_payment': {'id': None, 'value': float('inf')},
            'lowest_total_interest': {'id': None, 'value': float('inf')},
            'shortest_term': {'id': None, 'value': float('inf')},
            'lowest_interest_rate': {'id': None, 'value': float('inf')},
            'lowest_interest_to_principal_ratio': {'id': None, 'value': float('inf')}
        }
        
        for loan in loan_data:
            # Extract numeric values - handle both Money objects and formatted strings
            if isinstance(loan['monthly_payment'], Money):
                monthly_payment = loan['monthly_payment'].dollars
            else:
                monthly_payment = float(str(loan['monthly_payment']).replace('$', '').replace(',', ''))
                
            if isinstance(loan['total_interest'], Money):
                total_interest = loan['total_interest'].dollars
            else:
                total_interest = float(str(loan['total_interest']).replace('$', '').replace(',', ''))
                
            if isinstance(loan['interest_rate'], Percentage):
                interest_rate = loan['interest_rate'].value
            else:
                interest_rate = float(str(loan['interest_rate']).replace('%', ''))
                
            interest_to_principal = float(loan['interest_to_principal_ratio'].replace('%', '')) / 100
            
            # Update lowest monthly payment
            if monthly_payment < metrics['lowest_monthly_payment']['value']:
                metrics['lowest_monthly_payment']['id'] = loan['id']
                metrics['lowest_monthly_payment']['value'] = monthly_payment
                metrics['lowest_monthly_payment']['name'] = loan['name']
                
            # Update lowest total interest
            if total_interest < metrics['lowest_total_interest']['value']:
                metrics['lowest_total_interest']['id'] = loan['id']
                metrics['lowest_total_interest']['value'] = total_interest
                metrics['lowest_total_interest']['name'] = loan['name']
                
            # Update shortest term
            if loan['term_months'] < metrics['shortest_term']['value']:
                metrics['shortest_term']['id'] = loan['id']
                metrics['shortest_term']['value'] = loan['term_months']
                metrics['shortest_term']['name'] = loan['name']
                
            # Update lowest interest rate
            if interest_rate < metrics['lowest_interest_rate']['value']:
                metrics['lowest_interest_rate']['id'] = loan['id']
                metrics['lowest_interest_rate']['value'] = interest_rate
                metrics['lowest_interest_rate']['name'] = loan['name']
                
            # Update lowest interest to principal ratio
            if interest_to_principal < metrics['lowest_interest_to_principal_ratio']['value']:
                metrics['lowest_interest_to_principal_ratio']['id'] = loan['id']
                metrics['lowest_interest_to_principal_ratio']['value'] = interest_to_principal
                metrics['lowest_interest_to_principal_ratio']['name'] = loan['name']
                
        # Format values for display
        metrics['lowest_monthly_payment']['value'] = f"${metrics['lowest_monthly_payment']['value']:,.2f}"
        metrics['lowest_total_interest']['value'] = f"${metrics['lowest_total_interest']['value']:,.2f}"
        metrics['shortest_term']['value'] = f"{metrics['shortest_term']['value']} months ({metrics['shortest_term']['value']/12:.1f} years)"
        metrics['lowest_interest_rate']['value'] = f"{metrics['lowest_interest_rate']['value']:.3f}%"
        metrics['lowest_interest_to_principal_ratio']['value'] = f"{metrics['lowest_interest_to_principal_ratio']['value']:.2%}"
        
        return metrics
    
    @staticmethod
    def _generate_recommendation(loan_data: List[Dict[str, Any]], metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a recommendation based on loan comparison.
        
        Args:
            loan_data: List of dictionaries containing loan metrics
            metrics: Comparative metrics between loans
            
        Returns:
            Dict: Recommendation details
        """
        # Count which loan appears most frequently in the metrics
        loan_counts = {}
        for metric, data in metrics.items():
            loan_id = data['id']
            if loan_id is not None:
                loan_counts[loan_id] = loan_counts.get(loan_id, 0) + 1
                
        # Find the loan with the most favorable metrics
        best_loan_id = max(loan_counts.items(), key=lambda x: x[1])[0] if loan_counts else None
        
        if best_loan_id is None:
            return None
            
        # Find the loan data for the recommended loan
        recommended_loan = next((loan for loan in loan_data if loan['id'] == best_loan_id), None)
        
        if recommended_loan is None:
            return None
            
        # Generate recommendation details
        recommendation = {
            'loan_id': best_loan_id,
            'loan_name': recommended_loan['name'],
            'reasons': []
        }
        
        # Add reasons for the recommendation
        for metric, data in metrics.items():
            if data['id'] == best_loan_id:
                if metric == 'lowest_monthly_payment':
                    recommendation['reasons'].append(f"Lowest monthly payment ({data['value']})")
                elif metric == 'lowest_total_interest':
                    recommendation['reasons'].append(f"Lowest total interest paid ({data['value']})")
                elif metric == 'shortest_term':
                    recommendation['reasons'].append(f"Shortest loan term ({data['value']})")
                elif metric == 'lowest_interest_rate':
                    recommendation['reasons'].append(f"Lowest interest rate ({data['value']})")
                elif metric == 'lowest_interest_to_principal_ratio':
                    recommendation['reasons'].append(f"Best interest-to-principal ratio ({data['value']})")
                    
        return recommendation
    
    @staticmethod
    def _get_balloon_details(loan: Loan) -> Dict[str, Any]:
        """
        Get formatted balloon payment details for a loan.
        
        Args:
            loan: Loan object with balloon payment
            
        Returns:
            Dict: Formatted balloon payment details
        """
        if not loan.balloon_payment:
            return None
            
        balloon = loan.balloon_payment
        
        # Calculate the balloon date if not provided
        balloon_date = balloon.due_date
        if not balloon_date and balloon.term_months:
            # Calculate the balloon date based on start date and term
            balloon_date = loan.start_date
            years_to_add = balloon.term_months // 12
            months_to_add = balloon.term_months % 12
            
            balloon_year = balloon_date.year + years_to_add
            balloon_month = balloon_date.month + months_to_add
            
            if balloon_month > 12:
                balloon_year += 1
                balloon_month -= 12
                
            balloon_day = min(balloon_date.day, 28)  # Avoid invalid dates
            balloon_date = date(balloon_year, balloon_month, balloon_day)
            
        # Calculate the balloon amount if not provided
        balloon_amount = balloon.amount
        if not balloon_amount and balloon.term_months:
            # Calculate the remaining balance after the balloon term
            loan_details = loan.to_loan_details()
            balloon_amount = loan_details.calculate_remaining_balance(balloon.term_months)
            
        # Calculate monthly payment
        loan_details = loan.to_loan_details()
        monthly_payment = loan_details.calculate_payment().total
        
        # Calculate total payments before balloon
        total_payments = monthly_payment.dollars * (balloon.term_months or 0)
        
        return {
            'amount': str(balloon_amount) if balloon_amount else "Unknown",
            'due_date': balloon_date.isoformat() if balloon_date else "Unknown",
            'term_months': balloon.term_months or "Unknown",
            'monthly_payment': str(monthly_payment),
            'total_payments_before_balloon': f"${total_payments:,.2f}" if balloon.term_months else "Unknown"
        }
    
    @staticmethod
    def calculate_refinance_savings(
        current_loan: Dict[str, Any],
        new_loan: Dict[str, Any],
        closing_costs: Money
    ) -> Dict[str, Any]:
        """
        Calculate potential savings from refinancing a loan.
        
        Args:
            current_loan: Dictionary containing current loan data
            new_loan: Dictionary containing new loan data
            closing_costs: Closing costs for the refinance
            
        Returns:
            Dict: Refinance analysis results
        """
        # Handle simplified loan options format from tests
        if 'loan_type' not in current_loan and 'property_id' not in current_loan:
            current_loan_dict = {
                'property_id': 'test_property',
                'loan_type': 'initial',
                'amount': current_loan.get('amount'),
                'interest_rate': current_loan.get('interest_rate'),
                'term_months': current_loan.get('term_months'),
                'start_date': current_loan.get('start_date', date.today().isoformat()),
                'is_interest_only': current_loan.get('is_interest_only', False),
                'months_paid': current_loan.get('months_paid', 0)
            }
        else:
            current_loan_dict = current_loan.copy()
            
        if 'loan_type' not in new_loan and 'property_id' not in new_loan:
            new_loan_dict = {
                'property_id': 'test_property',
                'loan_type': 'refinance',
                'amount': new_loan.get('amount'),
                'interest_rate': new_loan.get('interest_rate'),
                'term_months': new_loan.get('term_months'),
                'start_date': new_loan.get('start_date', date.today().isoformat()),
                'is_interest_only': new_loan.get('is_interest_only', False)
            }
        else:
            new_loan_dict = new_loan.copy()
        
        # Create loan objects
        current = Loan.from_dict(current_loan_dict)
        new = Loan.from_dict(new_loan_dict)
        
        # Calculate current loan details
        current_details = current.to_loan_details()
        current_payment = current_details.calculate_payment().total
        
        # Calculate new loan details
        new_details = new.to_loan_details()
        new_payment = new_details.calculate_payment().total
        
        # Calculate monthly savings
        monthly_savings = current_payment.dollars - new_payment.dollars
        
        # Calculate break-even point (months)
        if monthly_savings <= 0:
            break_even_months = float('inf')
        else:
            break_even_months = closing_costs.dollars / monthly_savings
            
        # Calculate total interest for both loans
        current_amount_value = current.get_amount_as_money().dollars
        new_amount_value = new.get_amount_as_money().dollars
        current_total_interest = (current_payment.dollars * current.term_months) - current_amount_value
        new_total_interest = (new_payment.dollars * new.term_months) - new_amount_value
        
        # Calculate interest savings
        interest_savings = current_total_interest - new_total_interest
        
        # Calculate total cost comparison (including closing costs)
        current_total_cost = current_payment.dollars * current.term_months
        new_total_cost = (new_payment.dollars * new.term_months) + closing_costs.dollars
        total_cost_savings = current_total_cost - new_total_cost
        
        return {
            'monthly_payment_before': current_payment,  # Keep as Money object
            'monthly_payment_after': new_payment,  # Keep as Money object
            'monthly_payment_savings': Money(monthly_savings),  # Keep as Money object
            'monthly_savings': f"${monthly_savings:,.2f}",  # String format for display
            'annual_savings': f"${monthly_savings * 12:,.2f}",
            'closing_costs': closing_costs,  # Keep as Money object
            'break_even_months': round(break_even_months, 1) if break_even_months != float('inf') else "N/A",
            'break_even_years': round(break_even_months / 12, 2) if break_even_months != float('inf') else "N/A",
            'interest_savings': f"${interest_savings:,.2f}",
            'total_cost_savings': f"${total_cost_savings:,.2f}",
            'total_interest_savings': Money(interest_savings),  # Keep as Money object
            'is_recommended': total_cost_savings > 0,
            'recommendation': LoanComparison._get_refinance_recommendation(
                monthly_savings, break_even_months, total_cost_savings
            )
        }
    
    @staticmethod
    def _get_refinance_recommendation(
        monthly_savings: float,
        break_even_months: float,
        total_cost_savings: float
    ) -> str:
        """
        Generate a recommendation for refinancing.
        
        Args:
            monthly_savings: Monthly payment savings
            break_even_months: Months to break even on closing costs
            total_cost_savings: Total cost savings over the life of the loan
            
        Returns:
            str: Recommendation text
        """
        if monthly_savings <= 0:
            return "Not recommended - The new loan does not reduce your monthly payment."
            
        if total_cost_savings <= 0:
            return "Not recommended - The new loan will cost more in the long run when including closing costs."
            
        if break_even_months > 60:  # 5 years
            return f"Consider carefully - It will take {round(break_even_months/12, 1)} years to break even on closing costs."
            
        if break_even_months <= 24:  # 2 years
            return f"Strongly recommended - You'll break even in just {round(break_even_months, 1)} months and save ${total_cost_savings:,.2f} over the life of the loan."
            
        return f"Recommended - You'll break even in {round(break_even_months, 1)} months and save ${total_cost_savings:,.2f} over the life of the loan."
