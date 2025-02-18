from typing import Dict, List, Optional
from datetime import datetime, date
import logging
from decimal import Decimal
import calendar

logger = logging.getLogger(__name__)

class PropertyKPIService:
    """Enhanced service for calculating property KPIs from actual transaction data."""
    
    # Categories that should NOT be included in operating expenses
    NON_OPERATING_CATEGORIES = {
        'Asset Acquisition',      # One-time acquisition costs
        'Capital Expenditures',   # Major improvements
        'Bank/Financial Fees',    # Financing costs
        'Legal/Professional Fees',# One-time costs
        'Marketing/Advertising',  # One-time costs
        'Mortgage'               # Handled separately for DSCR
    }
    
    # Categories that should NOT be included in income calculations
    NON_OPERATING_INCOME = {
        'Security Deposit',  # Not true income
        'Loan Repayment',   # Principal recovery
        'Insurance Refund', # One-time refunds
        'Escrow Refund'     # One-time refunds
    }
    
    @staticmethod
    def safe_json(obj):
        """Convert Decimals and handle infinity values before JSON serialization."""
        if isinstance(obj, Decimal):
            return float(obj) if obj != Decimal('Infinity') else None
        if isinstance(obj, dict):
            return {k: PropertyKPIService.safe_json(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [PropertyKPIService.safe_json(i) for i in obj]
        return obj

    def __init__(self, properties_data: List[Dict]):
        """Initialize with properties data including acquisition and loan details."""
        self.properties_data = {
            p['address']: p for p in properties_data
        }
    
    def get_kpi_dashboard_data(self, 
                             property_id: str,
                             transactions: List[Dict],
                             analysis_id: Optional[str] = None) -> Dict:
        """Get complete KPI dashboard data including YTD and Since Acquisition."""
        try:
            # Get YTD KPIs
            ytd_kpis = self.get_ytd_kpis(property_id, transactions)
            
            # Get Since Acquisition KPIs
            acquisition_kpis = self.get_since_acquisition_kpis(property_id, transactions)
            
            return {
                'year_to_date': ytd_kpis,
                'since_acquisition': acquisition_kpis,
                'analysis_comparison': None,
                'metadata': {
                    'has_complete_history': self._has_complete_history(property_id, transactions),
                    'available_analyses': []
                }
            }
        except Exception as e:
            logger.error(f"Error getting KPI dashboard data for {property_id}: {str(e)}")
            return self._get_empty_kpi_dict()

    def get_ytd_kpis(self, property_id: str, transactions: List[Dict]) -> Dict:
        """Calculate KPIs for year-to-date."""
        today = date.today()
        start_date = f"{today.year}-01-01"
        return self.calculate_property_kpis(
            property_id, 
            transactions,
            start_date=start_date,
            end_date=today.strftime('%Y-%m-%d')
        )

    def get_since_acquisition_kpis(self, property_id: str, transactions: List[Dict]) -> Dict:
        """Calculate KPIs since property acquisition."""
        property_details = self.properties_data.get(property_id)
        if not property_details or not property_details.get('purchase_date'):
            logger.error(f"Purchase date not found for property {property_id}")
            return self._get_empty_kpi_dict()
                
        return self.calculate_property_kpis(
            property_id,
            transactions,
            start_date=property_details['purchase_date'],
            end_date=date.today().strftime('%Y-%m-%d')
        )
    
    def calculate_property_kpis(self, property_id: str, transactions: List[Dict], 
                              start_date: Optional[str] = None, 
                              end_date: Optional[str] = None) -> Dict:
        """Calculate KPIs for a property based on actual transactions."""
        try:
            # Get property details
            property_details = self.properties_data.get(property_id)
            if not property_details:
                logger.error(f"Property details not found for {property_id}")
                return self._get_empty_kpi_dict()
            
            # Filter transactions
            filtered_transactions = self._filter_transactions_by_date(
                [t for t in transactions if t['property_id'] == property_id],
                start_date,
                end_date
            )
            
            if not filtered_transactions:
                logger.warning(f"No transactions found for property {property_id}")
                return self._get_empty_kpi_dict()
            
            # Calculate monthly averages
            monthly_metrics = self._calculate_monthly_metrics(filtered_transactions)
            
            # Calculate property metrics
            purchase_price = Decimal(str(property_details['purchase_price']))
            total_investment = self._calculate_total_investment(property_details)
            
            # Calculate monthly NOI and cash flow
            avg_monthly_noi = monthly_metrics['avg_monthly_noi']
            avg_monthly_cash_flow = avg_monthly_noi - monthly_metrics['avg_monthly_mortgage']
            
            # Calculate DSCR
            dscr = None
            if monthly_metrics['avg_monthly_mortgage'] > 0:
                dscr = avg_monthly_noi / monthly_metrics['avg_monthly_mortgage']
            
            # Calculate Cap Rate (using annualized NOI)
            annual_noi = avg_monthly_noi * Decimal('12')
            cap_rate = (annual_noi / purchase_price * Decimal('100')) if purchase_price else None
            
            # Calculate Cash on Cash Return
            annual_cash_flow = avg_monthly_cash_flow * Decimal('12')
            cash_on_cash = (annual_cash_flow / total_investment * Decimal('100')) if total_investment else None
            
            kpi_data = {
                'net_operating_income': {
                    'monthly': avg_monthly_noi,
                    'annual': annual_noi
                },
                'total_income': {
                    'monthly': monthly_metrics['avg_monthly_income'],
                    'annual': monthly_metrics['avg_monthly_income'] * Decimal('12')
                },
                'total_expenses': {
                    'monthly': monthly_metrics['avg_monthly_expenses'],
                    'annual': monthly_metrics['avg_monthly_expenses'] * Decimal('12')
                },
                'cap_rate': cap_rate,
                'cash_on_cash_return': cash_on_cash,
                'debt_service_coverage_ratio': dscr,
                'cash_invested': total_investment,
                'metadata': {
                    'has_complete_history': self._has_complete_history(property_id, filtered_transactions),
                    'data_quality': {
                        'confidence_level': 'high',
                        'refinance_info': self._calculate_refinance_impact(
                            property_id, filtered_transactions, start_date, end_date
                        )
                    }
                }
            }

            return self.safe_json(kpi_data)
                
        except Exception as e:
            logger.error(f"Error calculating KPIs for {property_id}: {str(e)}")
            return self._get_empty_kpi_dict()

    def _calculate_monthly_metrics(self, transactions: List[Dict]) -> Dict[str, Decimal]:
        """Calculate average monthly metrics from transactions."""
        monthly_income = {}
        monthly_expenses = {}
        monthly_mortgage = {}
        
        # Group transactions by month
        for transaction in transactions:
            month = transaction['date'][:7]  # YYYY-MM
            amount = Decimal(str(transaction['amount']))
            
            if transaction['type'] == 'income' and transaction['category'] not in self.NON_OPERATING_INCOME:
                monthly_income[month] = monthly_income.get(month, Decimal('0')) + amount
                
            elif transaction['type'] == 'expense':
                if transaction['category'] == 'Mortgage':
                    monthly_mortgage[month] = monthly_mortgage.get(month, Decimal('0')) + amount
                elif transaction['category'] not in self.NON_OPERATING_CATEGORIES:
                    monthly_expenses[month] = monthly_expenses.get(month, Decimal('0')) + amount
        
        # Calculate averages
        num_months = len(set(monthly_income.keys()) | set(monthly_expenses.keys()) | set(monthly_mortgage.keys()))
        if num_months == 0:
            return {
                'avg_monthly_income': Decimal('0'),
                'avg_monthly_expenses': Decimal('0'),
                'avg_monthly_mortgage': Decimal('0'),
                'avg_monthly_noi': Decimal('0')
            }
        
        avg_monthly_income = sum(monthly_income.values()) / Decimal(str(num_months))
        avg_monthly_expenses = sum(monthly_expenses.values()) / Decimal(str(num_months))
        avg_monthly_mortgage = sum(monthly_mortgage.values()) / Decimal(str(num_months))
        avg_monthly_noi = avg_monthly_income - avg_monthly_expenses
        
        return {
            'avg_monthly_income': avg_monthly_income,
            'avg_monthly_expenses': avg_monthly_expenses,
            'avg_monthly_mortgage': avg_monthly_mortgage,
            'avg_monthly_noi': avg_monthly_noi
        }

    def _calculate_total_investment(self, property_details: Dict) -> Decimal:
        """Calculate total cash invested in the property."""
        return sum([
            Decimal(str(property_details.get('down_payment', 0))),
            Decimal(str(property_details.get('closing_costs', 0))),
            Decimal(str(property_details.get('renovation_costs', 0))),
            Decimal(str(property_details.get('marketing_costs', 0))),
            Decimal(str(property_details.get('holding_costs', 0)))
        ])

    def _has_complete_history(self, property_id: str, transactions: List[Dict]) -> bool:
        """Check if we have complete transaction history for meaningful KPI calculation."""
        if not transactions:
            return False
            
        property_details = self.properties_data.get(property_id)
        if not property_details:
            return False
            
        purchase_date = datetime.strptime(property_details['purchase_date'], '%Y-%m-%d').date()
        today = date.today()
        
        transaction_dates = [
            datetime.strptime(t['date'], '%Y-%m-%d').date()
            for t in transactions
        ]
        
        if not transaction_dates:
            return False
            
        earliest_transaction = min(transaction_dates)
        latest_transaction = max(transaction_dates)
        
        MAX_START_GAP_DAYS = 30  # Allow 30 days gap from purchase
        MAX_END_GAP_DAYS = 45    # Allow 45 days gap to present
        
        has_start_coverage = (earliest_transaction - purchase_date).days <= MAX_START_GAP_DAYS
        has_end_coverage = (today - latest_transaction).days <= MAX_END_GAP_DAYS
        
        return has_start_coverage and has_end_coverage

    def _calculate_refinance_impact(self, property_id: str, transactions: List[Dict],
                                  start_date: Optional[str], end_date: Optional[str]) -> Dict:
        """Analyze impact of refinancing on debt service."""
        mortgage_transactions = [
            t for t in transactions
            if t['category'] == 'Mortgage'
        ]
        
        if not mortgage_transactions:
            return {
                'has_refinanced': False,
                'original_debt_service': 0,
                'current_debt_service': 0
            }
            
        # Sort by date and analyze patterns
        mortgage_transactions.sort(key=lambda x: x['date'])
        payments = [Decimal(str(t['amount'])) for t in mortgage_transactions]
        
        # Look for significant changes in payment amounts
        unique_payments = sorted(set(payments))
        if len(unique_payments) > 1:
            return {
                'has_refinanced': True,
                'original_debt_service': float(payments[0]),
                'current_debt_service': float(payments[-1])
            }
            
        return {
            'has_refinanced': False,
            'original_debt_service': float(payments[0]),
            'current_debt_service': float(payments[0])
        }

    def _filter_transactions_by_date(self, transactions: List[Dict],
                                   start_date: Optional[str] = None,
                                   end_date: Optional[str] = None) -> List[Dict]:
        """Filter transactions by date range."""
        filtered = transactions.copy()
        
        if start_date:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            filtered = [
                t for t in filtered
                if datetime.strptime(t['date'], '%Y-%m-%d').date() >= start
            ]
            
        if end_date:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            filtered = [
                t for t in filtered
                if datetime.strptime(t['date'], '%Y-%m-%d').date() <= end
            ]
            
        return filtered

    def _get_empty_kpi_dict(self) -> Dict:
        """Return dictionary with empty/zero KPI values."""
        return {
            'net_operating_income': {
                'monthly': 0,
                'annual': 0
            },
            'total_income': {
                'monthly': 0,
                'annual': 0
            },
            'total_expenses': {
                'monthly': 0,
                'annual': 0
            },
            'cap_rate': 0,
            'cash_on_cash_return': 0,
            'debt_service_coverage_ratio': 0,
            'cash_invested': 0,
            'metadata': {
                'has_complete_history': False,
                'data_quality': {
                    'confidence_level': 'low',
                    'refinance_info': {
                        'has_refinanced': False,
                        'original_debt_service': 0,
                        'current_debt_service': 0
                    }
                }
            }
        }