from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Union
from decimal import Decimal
from utils.money import Money, Percentage, MonthlyPayment
from datetime import datetime
import logging
import uuid
import traceback

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create console handler if it doesn't exist
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

@dataclass
class AnalysisReport:
    """Container for complete analysis report data matching flat schema"""
    # Core metadata
    id: str
    user_id: str
    analysis_name: str
    analysis_type: str
    address: str
    generated_date: str
    
    # Property details
    square_footage: int
    lot_size: int
    year_built: int
    
    # Financial details
    purchase_price: int
    after_repair_value: int
    renovation_costs: int
    renovation_duration: int
    monthly_rent: int
    
    # Operating expenses
    property_taxes: int
    insurance: int
    hoa_coa_coop: int
    management_fee_percentage: float
    capex_percentage: float
    vacancy_percentage: float
    repairs_percentage: float
    
    # Calculated metrics
    metrics: Dict

    def to_dict(self) -> Dict:
        """Convert report to dictionary format."""
        return {
            # Core metadata
            'id': self.id,
            'user_id': self.user_id,
            'analysis_name': self.analysis_name,
            'analysis_type': self.analysis_type,
            'address': self.address,
            'generated_date': self.generated_date,
            
            # Property details
            'square_footage': self.square_footage,
            'lot_size': self.lot_size,
            'year_built': self.year_built,
            
            # Financial details
            'purchase_price': self.purchase_price,
            'after_repair_value': self.after_repair_value,
            'renovation_costs': self.renovation_costs,
            'renovation_duration': self.renovation_duration,
            'monthly_rent': self.monthly_rent,
            
            # Operating expenses
            'property_taxes': self.property_taxes,
            'insurance': self.insurance,
            'hoa_coa_coop': self.hoa_coa_coop,
            'management_fee_percentage': self.management_fee_percentage,
            'capex_percentage': self.capex_percentage,
            'vacancy_percentage': self.vacancy_percentage,
            'repairs_percentage': self.repairs_percentage,
            
            # Calculated metrics
            'metrics': self.metrics
        }

    @classmethod
    def from_analysis(cls, analysis: 'Analysis') -> 'AnalysisReport':
        """Create report from analysis instance."""
        return cls(
            # Core metadata
            id=analysis.data['id'],
            user_id=analysis.data['user_id'],
            analysis_name=analysis.data['analysis_name'],
            analysis_type=analysis.data['analysis_type'],
            address=analysis.data['address'],
            generated_date=datetime.now().isoformat(),
            
            # Property details
            square_footage=analysis.data.get('square_footage', 0),
            lot_size=analysis.data.get('lot_size', 0),
            year_built=analysis.data.get('year_built', 0),
            
            # Financial details
            purchase_price=analysis.data.get('purchase_price', 0),
            after_repair_value=analysis.data.get('after_repair_value', 0),
            renovation_costs=analysis.data.get('renovation_costs', 0),
            renovation_duration=analysis.data.get('renovation_duration', 0),
            monthly_rent=analysis.data.get('monthly_rent', 0),
            
            # Operating expenses
            property_taxes=analysis.data.get('property_taxes', 0),
            insurance=analysis.data.get('insurance', 0),
            hoa_coa_coop=analysis.data.get('hoa_coa_coop', 0),
            management_fee_percentage=analysis.data.get('management_fee_percentage', 0.0),
            capex_percentage=analysis.data.get('capex_percentage', 0.0),
            vacancy_percentage=analysis.data.get('vacancy_percentage', 0.0),
            repairs_percentage=analysis.data.get('repairs_percentage', 0.0),
            
            # Get calculated metrics
            metrics=analysis.get_report_data()['metrics']
        )

    def get_type_specific_data(self) -> Dict:
        """Get additional data specific to analysis type."""
        if 'BRRRR' in self.analysis_type:
            return {
                'equity_captured': self.metrics.get('equity_captured'),
                'cash_recouped': self.metrics.get('cash_recouped'),
                'total_project_costs': self.metrics.get('total_project_costs'),
                'holding_costs': self.metrics.get('holding_costs')
            }
        if 'PadSplit' in self.analysis_type:
            return {
                'utilities': self.metrics.get('utilities'),
                'internet': self.metrics.get('internet'),
                'cleaning': self.metrics.get('cleaning'),
                'pest_control': self.metrics.get('pest_control'),
                'landscaping': self.metrics.get('landscaping'),
                'platform_fee': self.metrics.get('platform_fee')
            }
        return {}

class Analysis(ABC):
    """Base class for all property investment analysis types."""
    
    def __init__(self, data: Dict):
        """Initialize analysis with flat data structure."""
        self.data = data
        self._validate_base_requirements()

    def _validate_base_requirements(self) -> None:
        """Validate base requirements common to all analysis types."""
        try:
            # 1. Validate metadata fields
            required_meta = {
                'id': str,
                'user_id': str,
                'created_at': str,
                'updated_at': str,
                'analysis_type': str,
                'analysis_name': str,
                'address': str
            }
            for field, expected_type in required_meta.items():
                value = self.data.get(field)
                if not value:
                    raise ValueError(f"Missing required metadata field: {field}")
                if not isinstance(value, expected_type):
                    raise TypeError(f"Field {field} must be type {expected_type.__name__}")

            # 2. Validate core calculation fields
            for field in ['monthly_rent']:
                value = self.data.get(field)
                if not value or not isinstance(value, (int, float)) or value < 0:
                    raise ValueError(f"Invalid {field}: must be a positive number")

            # 3. Validate percentage fields
            percentage_fields = [
                'management_fee_percentage',
                'capex_percentage',
                'vacancy_percentage',
                'repairs_percentage'
            ]
            for field in percentage_fields:
                value = self.data.get(field, 0)
                if not isinstance(value, (int, float)) or value < 0 or value > 100:
                    raise ValueError(f"Invalid {field}: must be between 0 and 100")

            # 4. Validate date formats
            for date_field in ['created_at', 'updated_at']:
                try:
                    datetime.fromisoformat(self.data[date_field].replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    raise ValueError(f"Invalid datetime format for {date_field}")

            # 5. Validate UUID
            try:
                uuid.UUID(str(self.data['id']))
            except ValueError:
                raise ValueError("Invalid UUID format for id field")

        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def _get_money(self, field: str) -> Money:
        """Safely get a money value from data."""
        return Money(self.data.get(field, 0))

    def _get_percentage(self, field: str) -> Percentage:
        """Safely get a percentage value from data."""
        return Percentage(self.data.get(field, 0))

    def calculate_monthly_cash_flow(self) -> Money:
        """Calculate monthly cash flow."""
        try:
            logger.debug("=== Starting Monthly Cash Flow Calculation ===")
            
            # Get income
            monthly_income = self._get_money('monthly_rent')
            logger.debug(f"Monthly income: {monthly_income}")
            
            # Calculate expenses
            operating_expenses = self._calculate_operating_expenses()
            logger.debug(f"Operating expenses: {operating_expenses}")
            
            # Calculate loan payments
            loan_payments = self._calculate_loan_payments()
            logger.debug(f"Loan payments: {loan_payments}")
            
            # Calculate final cash flow
            cash_flow = monthly_income - operating_expenses - loan_payments
            logger.debug(f"Final monthly cash flow: {cash_flow}")
            
            return cash_flow
        except Exception as e:
            logger.error(f"Error calculating monthly cash flow: {str(e)}")
            raise

    def _calculate_operating_expenses(self) -> Money:
        """Calculate total monthly operating expenses."""
        # Fixed expenses
        fixed_expenses = sum([
            self._get_money('property_taxes'),
            self._get_money('insurance'),
            self._get_money('hoa_coa_coop')
        ], Money(0))
        
        # Percentage-based expenses
        monthly_rent = self._get_money('monthly_rent')
        rent_based_expenses = sum([
            monthly_rent * self._get_percentage('management_fee_percentage'),
            monthly_rent * self._get_percentage('capex_percentage'),
            monthly_rent * self._get_percentage('vacancy_percentage'),
            monthly_rent * self._get_percentage('repairs_percentage')
        ], Money(0))
        
        # PadSplit-specific expenses if applicable
        padsplit_expenses = Money(0)
        if 'PadSplit' in self.data.get('analysis_type', ''):
            padsplit_expenses = sum([
                self._get_money('utilities'),
                self._get_money('internet'),
                self._get_money('cleaning'),
                self._get_money('pest_control'),
                self._get_money('landscaping'),
                monthly_rent * self._get_percentage('padsplit_platform_percentage')
            ], Money(0))
        
        return fixed_expenses + rent_based_expenses + padsplit_expenses

    def _calculate_loan_payments(self) -> Money:
        """Calculate total monthly loan payments."""
        try:
            # For BRRRR, we only want the refinance loan payment
            if 'BRRRR' in self.data.get('analysis_type', ''):
                refinance_payment = self._calculate_single_loan_payment(
                    amount=self._get_money('refinance_loan_amount'),
                    interest_rate=self._get_percentage('refinance_loan_interest_rate'),
                    term=self.data.get('refinance_loan_term', 0),
                    is_interest_only=False
                )
                logger.debug(f"BRRRR refinance payment: ${refinance_payment.dollars:.2f}")
                return refinance_payment
            
            # For LTR/PadSplit LTR, calculate all loan payments
            total_payments = Money(0)
            loan_prefixes = ['loan1', 'loan2', 'loan3']
            
            for prefix in loan_prefixes:
                amount = self._get_money(f'{prefix}_loan_amount')
                if amount.dollars > 0:
                    payment = self._calculate_single_loan_payment(
                        amount=amount,
                        interest_rate=self._get_percentage(f'{prefix}_loan_interest_rate'),
                        term=self.data.get(f'{prefix}_loan_term', 0),
                        is_interest_only=self.data.get(f'{prefix}_interest_only', False)
                    )
                    total_payments += payment
                    logger.debug(f"Loan {prefix} payment: ${payment.dollars:.2f}")
                    
            return total_payments
            
        except Exception as e:
            logger.error(f"Error calculating loan payments: {str(e)}")
            logger.error(traceback.format_exc())
            return Money(0)

    def _calculate_single_loan_payment(self, amount: Money, interest_rate: Percentage, 
                                 term: int, is_interest_only: bool = False) -> Money:
        """Calculate monthly payment for a single loan."""
        if amount.dollars <= 0 or term <= 0:
            return Money(0)
            
        try:
            # Convert to decimal for precise calculation
            loan_amount = Decimal(str(amount.dollars))
            annual_rate = Decimal(str(interest_rate.as_decimal()))
            monthly_rate = annual_rate / Decimal('12')
            term_months = Decimal(str(term))
            
            # Handle zero interest rate
            if annual_rate == 0:
                # For 0% loans, always divide principal by term (whether interest-only or not)
                # This effectively makes it a principal-only payment
                payment = float(loan_amount / term_months)
                logger.debug(f"Calculated principal-only payment: ${payment:.2f} for 0% loan amount: ${amount.dollars:.2f}")
                return Money(payment)
                
            # Handle normal interest-bearing loans
            if is_interest_only:
                # For interest-only, calculate the monthly interest
                payment = float(loan_amount * monthly_rate)
                logger.debug(f"Calculated interest-only payment: ${payment:.2f} for loan amount: ${amount.dollars:.2f}")
                return Money(payment)
                
            # For regular amortizing loans
            factor = (1 + monthly_rate) ** term_months
            payment = float(loan_amount * (monthly_rate * factor / (factor - 1)))
            logger.debug(f"Calculated amortized payment: ${payment:.2f} for loan amount: ${amount.dollars:.2f}")
            return Money(payment)
            
        except Exception as e:
            logger.error(f"Error calculating loan payment: {str(e)}")
            logger.error(traceback.format_exc())
            return Money(0)

    def calculate_total_cash_invested(self) -> Money:
        """
        Calculate total cash invested in the project.
        Only counts actual out-of-pocket expenses, regardless of financing type.
        """
        try:
            logger.debug("=== Starting Total Cash Invested Calculation ===")
            
            # Base investment (out of pocket costs)
            total_cash = sum([
                self._get_money('cash_to_seller'),          # Any cash paid directly to seller
                self._get_money('renovation_costs'),        # Renovation costs
                self._get_money('closing_costs'),           # Base closing costs
                self._get_money('assignment_fee'),          # Any assignment fees
                self._get_money('marketing_costs')          # Marketing costs
            ], Money(0))
            
            # Add loan down payments and closing costs for all loans
            for prefix in ['loan1', 'loan2', 'loan3']:
                total_cash += sum([
                    self._get_money(f'{prefix}_loan_down_payment'),
                    self._get_money(f'{prefix}_loan_closing_costs')
                ], Money(0))
            
            # For BRRRR deals, calculate net cash position
            if 'BRRRR' in self.data.get('analysis_type', ''):
                # Add initial costs
                initial_costs = sum([
                    self._get_money('initial_loan_amount'),
                    self._get_money('initial_loan_closing_costs')
                ], Money(0))
                logger.debug(f"Initial costs: ${initial_costs.dollars}")
                
                # Add refinance costs and subtract loan amount
                refinance_costs = self._get_money('refinance_loan_closing_costs')
                refinance_loan = self._get_money('refinance_loan_amount')
                total_cash = initial_costs + refinance_costs - refinance_loan
                logger.debug(f"Final total cash invested: ${total_cash.dollars}")
                
            return Money(max(0, float(total_cash.dollars)))
            
        except Exception as e:
            logger.error(f"Error calculating total cash invested: {str(e)}")
            logger.error(traceback.format_exc())
            return Money(0)

    @property
    def annual_cash_flow(self) -> Money:
        """Calculate annual cash flow."""
        return self.calculate_monthly_cash_flow() * 12

    @property
    def cash_on_cash_return(self) -> Percentage:
        """Calculate Cash on Cash return."""
        cash_invested = self.calculate_total_cash_invested()
        annual_cf = float(self.annual_cash_flow.dollars)
        
        return Percentage((annual_cf / float(cash_invested.dollars)) * 100) if cash_invested.dollars > 0 else Percentage(0)

    @property
    def roi(self) -> Percentage:
        """Calculate ROI including equity and cash flow."""
        try:
            cash_invested = self.calculate_total_cash_invested()
            if cash_invested.dollars <= 0:
                return Percentage(0)
            
            annual_cf = float(self.annual_cash_flow.dollars)
            
            equity_captured = 0
            if 'BRRRR' in self.data.get('analysis_type', ''):
                arv = self._get_money('after_repair_value')
                total_costs = sum([
                    self._get_money('purchase_price'),
                    self._get_money('renovation_costs')
                ], Money(0))
                equity_captured = float((arv - total_costs).dollars)
            
            total_return = annual_cf + equity_captured
            return Percentage((total_return / float(cash_invested.dollars)) * 100)
            
        except Exception as e:
            logger.error(f"Error calculating ROI: {str(e)}")
            return Percentage(0)

    def get_report_data(self) -> Dict:
        """Get analysis report data with calculated metrics."""
        try:
            # Calculate cash flow first for debugging
            monthly_cf = self.calculate_monthly_cash_flow()
            logger.debug(f"Calculated monthly cash flow: {monthly_cf}")
            
            metrics = {
                'monthly_cash_flow': str(monthly_cf),
                'annual_cash_flow': str(self.annual_cash_flow),
                'total_cash_invested': str(self.calculate_total_cash_invested()),
                'cash_on_cash_return': str(self.cash_on_cash_return),
                'roi': str(self.roi)
            }
            
            if 'BRRRR' in self.data.get('analysis_type', ''):
                # Calculate and log both loan payments
                initial_payment = self._calculate_single_loan_payment(
                    amount=self._get_money('initial_loan_amount'),
                    interest_rate=self._get_percentage('initial_loan_interest_rate'),
                    term=self.data.get('initial_loan_term', 0),
                    is_interest_only=self.data.get('initial_interest_only', False)
                )
                logger.debug(f"Calculated initial loan payment: {initial_payment}")

                refinance_payment = self._calculate_single_loan_payment(
                    amount=self._get_money('refinance_loan_amount'),
                    interest_rate=self._get_percentage('refinance_loan_interest_rate'),
                    term=self.data.get('refinance_loan_term', 0),
                    is_interest_only=False
                )
                logger.debug(f"Calculated refinance loan payment: {refinance_payment}")

                arv = self._get_money('after_repair_value')
                total_costs = sum([
                    self._get_money('purchase_price'),
                    self._get_money('renovation_costs')
                ], Money(0))

                metrics.update({
                    'equity_captured': str(arv - total_costs),
                    'cash_recouped': str(self._get_money('refinance_loan_amount')),
                    'initial_loan_payment': str(initial_payment),
                    'refinance_loan_payment': str(refinance_payment)
                })
                
                # Log the final metrics for debugging
                logger.debug(f"Final metrics: {metrics}")
            
            return {
                'metrics': metrics
            }
            
        except Exception as e:
            logger.error(f"Error generating report data: {str(e)}")
            raise

class LTRAnalysis(Analysis):
    """Long-term rental analysis implementation."""
    
    def __init__(self, data: Dict):
        """Initialize with validation for LTR-specific requirements."""
        if data.get('analysis_type') not in ['LTR', 'PadSplit LTR']:
            raise ValueError("Invalid analysis type for LTR analysis")
            
        super().__init__(data)
        self._validate_ltr_requirements()

    def _calculate_loan_payments(self) -> Money:
        """Calculate total monthly loan payments considering balloon scenarios."""
        try:
            if not self.data.get('has_balloon_payment'):
                return super()._calculate_loan_payments()

            # For balloon scenarios, use original loan payment until balloon date
            now = datetime.now()
            balloon_date = datetime.fromisoformat(self.data['balloon_due_date'])
            
            if now > balloon_date:
                # Past balloon date, use refinanced terms
                return self._calculate_single_loan_payment(
                    amount=self._get_money('balloon_refinance_loan_amount'),
                    interest_rate=self._get_percentage('balloon_refinance_loan_interest_rate'),
                    term=self.data.get('balloon_refinance_loan_term', 0),
                    is_interest_only=False  # Refinanced balloon typically amortizes
                )
            else:
                # Before balloon date, use original terms
                return super()._calculate_loan_payments()
                
        except Exception as e:
            logger.error(f"Error calculating loan payments: {str(e)}")
            logger.error(traceback.format_exc())
            return Money(0)

    def validate_balloon_payment(self) -> None:
        """Validate balloon payment specific fields."""
        if not self.data.get('has_balloon_payment'):
            return

        try:
            # Validate balloon date
            balloon_date = datetime.fromisoformat(self.data['balloon_due_date'])
            if balloon_date <= datetime.now():
                raise ValueError("Balloon due date must be in the future")

            # Validate LTV percentage
            ltv = self._get_percentage('balloon_refinance_ltv_percentage').value
            if ltv <= 0 or ltv > 100:
                raise ValueError("Balloon refinance LTV must be between 0% and 100%")

            # Validate refinance loan parameters
            refinance_amount = self._get_money('balloon_refinance_loan_amount')
            if refinance_amount.dollars <= 0:
                raise ValueError("Balloon refinance loan amount must be greater than 0")

            interest_rate = self._get_percentage('balloon_refinance_loan_interest_rate')
            if interest_rate.value <= 0 or interest_rate.value >= 30:
                raise ValueError("Balloon refinance interest rate must be between 0% and 30%")

            term = self.data.get('balloon_refinance_loan_term', 0)
            if term <= 0 or term > 360:  # Max 30 years
                raise ValueError("Balloon refinance term must be between 1 and 360 months")

        except ValueError as e:
            raise
        except Exception as e:
            raise ValueError(f"Invalid balloon payment parameters: {str(e)}")
    
    def _validate_ltr_requirements(self) -> None:
        """Validate fields specific to LTR analysis."""
        try:
            # Validate required numeric fields
            ltr_fields = {
                'purchase_price': 'Purchase price',
                'monthly_rent': 'Monthly rent',
                'property_taxes': 'Property taxes',
                'insurance': 'Insurance'
            }
            
            for field, display_name in ltr_fields.items():
                value = self._get_money(field)
                if value.dollars <= 0:
                    raise ValueError(f"{display_name} must be greater than 0")

            # Validate balloon payment fields if present
            if self.data.get('has_balloon_payment'):
                balloon_fields = {
                    'balloon_due_date': 'Balloon payment due date',
                    'balloon_refinance_ltv_percentage': 'Balloon refinance LTV percentage',
                    'balloon_refinance_loan_amount': 'Balloon refinance loan amount',
                    'balloon_refinance_loan_interest_rate': 'Balloon refinance interest rate',
                    'balloon_refinance_loan_term': 'Balloon refinance term'
                }
                
                for field, display_name in balloon_fields.items():
                    value = self.data.get(field)
                    if not value:
                        raise ValueError(f"{display_name} is required when balloon payment is enabled")

                # Validate LTV percentage
                ltv = float(self._get_percentage('balloon_refinance_ltv_percentage').value)
                if ltv <= 0 or ltv > 100:
                    raise ValueError("Balloon refinance LTV percentage must be between 0% and 100%")

                # Validate balloon due date format
                try:
                    datetime.fromisoformat(self.data['balloon_due_date'])
                except (ValueError, TypeError):
                    raise ValueError("Invalid balloon payment due date format")

            # Validate percentage fields have reasonable values
            percentage_fields = {
                'management_fee_percentage': (0, 15),  # Typical range 0-15%
                'capex_percentage': (0, 10),          # Typical range 0-10%
                'vacancy_percentage': (0, 15),        # Typical range 0-15%
                'repairs_percentage': (0, 15)         # Typical range 0-15%
            }
            
            for field, (min_val, max_val) in percentage_fields.items():
                value = float(self._get_percentage(field).value)
                if value < 0 or value > max_val:
                    raise ValueError(f"{field} should be between {min_val}% and {max_val}%")

        except Exception as e:
            logger.error(f"LTR validation error: {str(e)}")
            raise ValueError(f"LTR validation failed: {str(e)}")
        
    def _calculate_pre_balloon_loan_payments(self) -> Money:
        """Calculate total monthly loan payments before balloon payment."""
        try:
            total_payments = Money(0)
            loan_prefixes = ['loan1', 'loan2', 'loan3']
            
            for prefix in loan_prefixes:
                amount = self._get_money(f'{prefix}_loan_amount')
                if amount.dollars > 0:
                    payment = self._calculate_single_loan_payment(
                        amount=amount,
                        interest_rate=self._get_percentage(f'{prefix}_loan_interest_rate'),
                        term=self.data.get(f'{prefix}_loan_term', 0),
                        is_interest_only=self.data.get(f'{prefix}_interest_only', False)
                    )
                    total_payments += payment
                    logger.debug(f"Pre-balloon {prefix} payment: ${payment.dollars:.2f}")
                        
            return total_payments
                
        except Exception as e:
            logger.error(f"Error calculating pre-balloon loan payments: {str(e)}")
            logger.error(traceback.format_exc())
            return Money(0)

    def _calculate_post_balloon_loan_payment(self) -> Money:
        """Calculate monthly loan payment after balloon refinance."""
        try:
            if not self.data.get('has_balloon_payment') and not (
                self.data.get('balloon_refinance_loan_amount', 0) > 0 and
                self.data.get('balloon_due_date') and
                self.data.get('balloon_refinance_ltv_percentage', 0) > 0
            ):
                return Money(0)

            # Calculate refinance payment
            payment = self._calculate_single_loan_payment(
                amount=self._get_money('balloon_refinance_loan_amount'),
                interest_rate=self._get_percentage('balloon_refinance_loan_interest_rate'),
                term=self.data.get('balloon_refinance_loan_term', 0),
                is_interest_only=False  # Balloon refinances typically amortize
            )
            
            logger.debug(f"Calculated post-balloon payment: {payment}")
            return payment
            
        except Exception as e:
            logger.error(f"Error calculating post-balloon loan payment: {str(e)}")
            logger.error(traceback.format_exc())
            return Money(0)

    def calculate_pre_balloon_monthly_cash_flow(self) -> Money:
        """Calculate monthly cash flow before balloon payment."""
        try:
            logger.debug("=== Starting Pre-Balloon Monthly Cash Flow Calculation ===")
            
            # Get income
            monthly_income = self._get_money('monthly_rent')
            logger.debug(f"Monthly income: {monthly_income}")
            
            # Calculate expenses
            operating_expenses = self._calculate_operating_expenses()
            logger.debug(f"Operating expenses: {operating_expenses}")
            
            # Calculate pre-balloon loan payments
            loan_payments = self._calculate_pre_balloon_loan_payments()
            logger.debug(f"Pre-balloon loan payments: {loan_payments}")
            
            # Calculate final cash flow
            cash_flow = monthly_income - operating_expenses - loan_payments
            logger.debug(f"Final pre-balloon monthly cash flow: {cash_flow}")
            
            return cash_flow
        except Exception as e:
            logger.error(f"Error calculating pre-balloon monthly cash flow: {str(e)}")
            raise

    def _calculate_post_balloon_monthly_cash_flow(self) -> Money:
        """Calculate monthly cash flow after balloon refinance."""
        try:
            monthly_income = self._get_money('monthly_rent')  # $1,775
            operating_expenses = self._calculate_operating_expenses()  # $499
            loan_payment = self._calculate_post_balloon_loan_payment()  # $809.05
            
            logger.debug(f"""
                Post-Balloon Cash Flow Calculation:
                Monthly Income: {monthly_income}
                Operating Expenses: {operating_expenses}
                Loan Payment: {loan_payment}
                Expected Cash Flow: {monthly_income - operating_expenses - loan_payment}
            """)
            
            return monthly_income - operating_expenses - loan_payment
        except Exception as e:
            logger.error(f"Error in post-balloon cash flow calculation: {e}")
            raise  # Raise the error instead of returning 0

    def calculate_balloon_refinance_costs(self) -> Money:
        """Calculate total costs associated with balloon payment refinance."""
        try:
            if not self.data.get('has_balloon_payment'):
                return Money(0)

            return sum([
                self._get_money('balloon_refinance_loan_down_payment'),
                self._get_money('balloon_refinance_loan_closing_costs')
            ], Money(0))
        except Exception as e:
            logger.error(f"Error calculating balloon refinance costs: {str(e)}")
            raise

    def _calculate_balloon_metrics(self) -> Dict:
        """Calculate metrics specific to balloon payment scenarios."""
        try:
            # Pre-balloon payment calculations
            pre_balloon_payment = self._calculate_pre_balloon_loan_payments()
            monthly_income = self._get_money('monthly_rent')
            operating_expenses = self._calculate_operating_expenses()
            
            # Calculate pre-balloon cash flows
            pre_balloon_monthly_cf = monthly_income - operating_expenses - pre_balloon_payment
            pre_balloon_annual_cf = pre_balloon_monthly_cf * 12
            
            # Post-balloon payment calculations
            post_balloon_payment = self._calculate_post_balloon_loan_payment()
            post_balloon_monthly_cf = monthly_income - operating_expenses - post_balloon_payment
            post_balloon_annual_cf = post_balloon_monthly_cf * 12
            
            # Calculate costs and differences
            refinance_costs = self.calculate_balloon_refinance_costs()
            monthly_payment_difference = post_balloon_payment - pre_balloon_payment
            
            return {
                'pre_balloon_monthly_payment': str(pre_balloon_payment),
                'post_balloon_monthly_payment': str(post_balloon_payment),
                'pre_balloon_monthly_cash_flow': str(pre_balloon_monthly_cf),
                'pre_balloon_annual_cash_flow': str(pre_balloon_annual_cf),
                'post_balloon_monthly_cash_flow': str(post_balloon_monthly_cf),
                'post_balloon_annual_cash_flow': str(post_balloon_annual_cf),
                'balloon_refinance_costs': str(refinance_costs),
                'monthly_payment_difference': str(monthly_payment_difference)
            }
        except Exception as e:
            logger.error(f"Error calculating balloon metrics: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def get_balloon_metrics(self) -> Dict:
        """Get metrics specific to balloon payment scenario."""
        try:
            if not self.data.get('has_balloon_payment'):
                return {}

            # Calculate pre-balloon cash flows
            pre_balloon_monthly_cf = self.calculate_monthly_cash_flow()  # Uses original loan terms
            pre_balloon_annual_cf = pre_balloon_monthly_cf * 12

            # Calculate post-balloon metrics
            post_balloon_monthly_cf = self._calculate_post_balloon_monthly_cash_flow()
            post_balloon_annual_cf = post_balloon_monthly_cf * 12

            # Calculate refinance costs
            refinance_costs = sum([
                self._get_money('balloon_refinance_loan_down_payment'),
                self._get_money('balloon_refinance_loan_closing_costs')
            ], Money(0))

            # Calculate monthly payment difference
            monthly_payment_difference = post_balloon_monthly_cf - pre_balloon_monthly_cf

            return {
                'pre_balloon_monthly_cash_flow': str(pre_balloon_monthly_cf),
                'pre_balloon_annual_cash_flow': str(pre_balloon_annual_cf),
                'post_balloon_monthly_cash_flow': str(post_balloon_monthly_cf),
                'post_balloon_annual_cash_flow': str(post_balloon_annual_cf),
                'balloon_refinance_costs': str(refinance_costs),
                'monthly_payment_difference': str(monthly_payment_difference)
            }

        except Exception as e:
            logger.error(f"Error calculating balloon metrics: {str(e)}")
            raise
    
    def get_report_data(self) -> Dict:
        """Get analysis report data with calculated metrics."""
        try:
            # Calculate monthly cash flows
            pre_balloon_monthly_cf = self.calculate_pre_balloon_monthly_cash_flow()
            post_balloon_monthly_cf = self._calculate_post_balloon_monthly_cash_flow()
            
            # Calculate loan payments
            pre_balloon_payment = self._calculate_pre_balloon_loan_payments()
            post_balloon_payment = self._calculate_post_balloon_loan_payment()
            
            # Calculate monthly payment difference
            payment_difference = post_balloon_payment - pre_balloon_payment
            
            # Calculate refinance costs
            refinance_costs = sum([
                self._get_money('balloon_refinance_loan_down_payment'),
                self._get_money('balloon_refinance_loan_closing_costs')
            ], Money(0))
            
            metrics = {
                'monthly_cash_flow': str(pre_balloon_monthly_cf),
                'annual_cash_flow': str(pre_balloon_monthly_cf * 12),
                'pre_balloon_monthly_cash_flow': str(pre_balloon_monthly_cf),
                'pre_balloon_annual_cash_flow': str(pre_balloon_monthly_cf * 12),
                'post_balloon_monthly_cash_flow': str(post_balloon_monthly_cf),
                'post_balloon_annual_cash_flow': str(post_balloon_monthly_cf * 12),
                'pre_balloon_monthly_payment': str(pre_balloon_payment),
                'post_balloon_monthly_payment': str(post_balloon_payment),
                'monthly_payment_difference': str(payment_difference),
                'balloon_refinance_costs': str(refinance_costs),
                'total_cash_invested': str(self.calculate_total_cash_invested()),
                'cash_on_cash_return': str(self.cash_on_cash_return),
                'roi': str(self.roi)
            }
            
            logger.debug(f"Final metrics: {metrics}")
            return {'metrics': metrics}
            
        except Exception as e:
            logger.error(f"Error generating report data: {str(e)}")
            logger.error(traceback.format_exc())
            raise

class BRRRRAnalysis(Analysis):
    """BRRRR strategy analysis implementation."""
    
    def __init__(self, data: Dict):
        """Initialize with validation for BRRRR-specific requirements."""
        if data.get('analysis_type') not in ['BRRRR', 'PadSplit BRRRR']:
            raise ValueError("Invalid analysis type for BRRRR analysis")
            
        super().__init__(data)
        self._validate_brrrr_requirements()

    def _validate_brrrr_requirements(self) -> None:
        """Validate fields specific to BRRRR analysis."""
        try:
            # Validate required BRRRR fields
            required_fields = {
                'purchase_price': 'Purchase price',
                'after_repair_value': 'After repair value',
                'renovation_costs': 'Renovation costs',
                'renovation_duration': 'Renovation duration',
                'initial_loan_amount': 'Initial loan amount',
                'refinance_loan_amount': 'Refinance loan amount'
            }
            
            for field, display_name in required_fields.items():
                value = self._get_money(field) if field != 'renovation_duration' else self.data.get(field, 0)
                if not value or (hasattr(value, 'dollars') and value.dollars <= 0) or (isinstance(value, (int, float)) and value <= 0):
                    raise ValueError(f"{display_name} must be greater than 0")

            # Validate loan parameters
            self._validate_loan_parameters('initial_loan', is_initial=True)
            self._validate_loan_parameters('refinance_loan')

            # Validate renovation duration
            renovation_duration = self.data.get('renovation_duration', 0)
            if renovation_duration <= 0 or renovation_duration > 24:  # Assuming max 24 months renovation
                raise ValueError("Renovation duration must be between 1 and 24 months")

            # Validate ARV is greater than purchase price + renovation costs
            arv = self._get_money('after_repair_value')
            total_cost = self._get_money('purchase_price') + self._get_money('renovation_costs')
            if arv <= total_cost:
                raise ValueError("After repair value must be greater than purchase price plus renovation costs")
            
            # Validate initial_interest_only is boolean if present
            initial_interest_only = self.data.get('initial_interest_only')
            if initial_interest_only is not None and not isinstance(initial_interest_only, bool):
                try:
                    # Convert string values to boolean
                    if isinstance(initial_interest_only, str):
                        self.data['initial_interest_only'] = initial_interest_only.lower() in ('true', '1')
                    else:
                        self.data['initial_interest_only'] = bool(initial_interest_only)
                except (ValueError, TypeError):
                    raise ValueError("initial_interest_only must be a boolean value")

        except Exception as e:
            logger.error(f"BRRRR validation error: {str(e)}")
            raise ValueError(f"BRRRR validation failed: {str(e)}")

    def _validate_loan_parameters(self, loan_prefix: str, is_initial: bool = False) -> None:
        """Validate loan parameters for a given loan type."""
        try:
            # Validate loan amount
            loan_amount = self._get_money(f'{loan_prefix}_amount')
            if loan_amount.dollars <= 0:
                raise ValueError(f"{loan_prefix} amount must be greater than 0")

            # Validate interest rate
            interest_rate = self._get_percentage(f'{loan_prefix}_interest_rate')
            if interest_rate.value <= 0 or interest_rate.value >= 30:  # Assuming max 30% interest
                raise ValueError(f"{loan_prefix} interest rate must be between 0% and 30%")

            # Validate loan term
            loan_term = self.data.get(f'{loan_prefix}_term', 0)
            if is_initial:
                if loan_term <= 0 or loan_term > 24:  # Initial loan typically 3-24 months
                    raise ValueError("Initial loan term must be between 1 and 24 months")
            else:
                if loan_term <= 0 or loan_term > 360:  # Long-term loan typically up to 30 years
                    raise ValueError("Refinance loan term must be between 1 and 360 months")

        except Exception as e:
            logger.error(f"Loan validation error: {str(e)}")
            raise ValueError(f"Loan validation failed: {str(e)}")

    @property
    def holding_costs(self) -> Money:
        """Calculate holding costs during renovation period."""
        monthly_costs = sum([
            self._get_money('property_taxes'),
            self._get_money('insurance'),
            self._calculate_single_loan_payment(
                amount=self._get_money('initial_loan_amount'),
                interest_rate=self._get_percentage('initial_loan_interest_rate'),
                term=self.data.get('initial_loan_term', 0),
                is_interest_only=True
            )
        ], Money(0))
        
        renovation_duration = self.data.get('renovation_duration', 0)
        return monthly_costs * renovation_duration

    @property
    def total_project_costs(self) -> Money:
        """Calculate total project costs including holding costs."""
        return sum([
            self._get_money('purchase_price'),
            self._get_money('renovation_costs'),
            self.holding_costs,
            self._get_money('initial_loan_closing_costs'),
            self._get_money('refinance_loan_closing_costs')
        ], Money(0))

    def calculate_mao(self) -> Money:
        """Calculate Maximum Allowable Offer."""
        try:
            arv = self._get_money('after_repair_value')
            renovation_costs = self._get_money('renovation_costs')
            holding_costs = self.holding_costs
            closing_costs = sum([
                self._get_money('initial_loan_closing_costs'),
                self._get_money('refinance_loan_closing_costs')
            ], Money(0))
            
            # Typical BRRRR wants 75% ARV - costs
            target_loan = arv * Percentage(75)
            mao = target_loan - (renovation_costs + holding_costs + closing_costs)
            
            return Money(max(0, float(mao.dollars)))
            
        except Exception as e:
            logger.error(f"Error calculating MAO: {str(e)}")
            raise

def create_analysis(data: Dict) -> Analysis:
    """Factory function to create appropriate analysis instance"""
    analysis_types = {
        'LTR': LTRAnalysis,
        'BRRRR': BRRRRAnalysis,
        'PadSplit LTR': LTRAnalysis,  # PadSplit handling now in base class
        'PadSplit BRRRR': BRRRRAnalysis  # PadSplit handling now in base class
    }
    
    analysis_type = data.get('analysis_type')
    analysis_class = analysis_types.get(analysis_type)
    
    if not analysis_class:
        raise ValueError(f"Invalid analysis type: {analysis_type}")
        
    return analysis_class(data)