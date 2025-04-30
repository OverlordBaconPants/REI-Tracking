# utils/standardized_metrics.py

import logging
from functools import lru_cache
import json
import threading

logger = logging.getLogger(__name__)

# In-memory cache for storing metrics by analysis ID
# Use a thread-safe dictionary for multi-thread access
_metrics_cache = {}
_cache_lock = threading.RLock()

def register_metrics(analysis_id, metrics):
    """
    Register metrics for an analysis in the global registry.
    
    Args:
        analysis_id: Analysis ID
        metrics: Dictionary of metrics
    """
    logger.debug(f"Registering metrics for analysis {analysis_id}")
    if not analysis_id:
        logger.warning("Cannot register metrics without an analysis ID")
        return
    
    # Thread-safe update of the cache
    with _cache_lock:
        _metrics_cache[analysis_id] = metrics.copy()

def get_metrics(analysis_id):
    """
    Get metrics for an analysis from the registry.
    
    Args:
        analysis_id: Analysis ID
        
    Returns:
        Dictionary of metrics or None if not found
    """
    # Thread-safe read from the cache
    with _cache_lock:
        return _metrics_cache.get(analysis_id)

# Set up caching for KPI calculations (5 minutes)
# This prevents recalculating the same KPIs repeatedly
@lru_cache(maxsize=100)
def cached_generate_kpi_data(analysis_json):
    """Cache KPI generation based on input data hash."""
    # Convert to dictionary if it's a string
    if isinstance(analysis_json, str):
        analysis = json.loads(analysis_json)
    else:
        analysis = analysis_json
        
    # Generate KPIs without caching
    return _generate_kpi_data_impl(analysis)

def generate_kpi_data(analysis):
    """Centralized KPI data generation function.
    
    This is the main entry point for all KPI calculations.
    """
    try:
        # First ensure all required metrics are calculated and available
        analysis = extract_calculated_metrics(analysis)
        
        # Convert analysis to JSON string for caching
        if not isinstance(analysis, str):
            analysis_json = json.dumps(analysis)
        else:
            analysis_json = analysis
            
        # Use the cached function
        return cached_generate_kpi_data(analysis_json)
    except Exception as e:
        logger.error(f"Error generating KPI data: {str(e)}", exc_info=True)
        # Return fallback KPI data with error flags
        return get_fallback_kpi_data()

def extract_calculated_metrics(analysis):
    """Extract all calculated metrics needed for KPIs.
    
    This ensures all required metrics are available before KPI calculation.
    """
    # Standardized approach to extract or calculate metrics
    try:
        # Clone the analysis to avoid modifying the original
        if isinstance(analysis, str):
            analysis_dict = json.loads(analysis)
        else:
            analysis_dict = dict(analysis)
            
        # Make sure metrics exist
        if 'metrics' not in analysis_dict:
            analysis_dict['metrics'] = {}
            
        # Calculate missing metrics if needed
        metrics = analysis_dict['metrics']
        
        # NOI calculations
        if 'noi' not in metrics:
            # Calculate Net Operating Income if missing
            metrics['noi'] = calculate_noi(analysis_dict)
            
        # Cap Rate
        if 'cap_rate' not in metrics:
            metrics['cap_rate'] = calculate_cap_rate(analysis_dict)
            
        # Cash on Cash Return
        if 'cash_on_cash' not in metrics:
            metrics['cash_on_cash'] = calculate_cash_on_cash(analysis_dict)
            
        # DSCR
        if 'dscr' not in metrics:
            metrics['dscr'] = calculate_dscr(analysis_dict)
            
        # Expense Ratio
        if 'expense_ratio' not in metrics:
            metrics['expense_ratio'] = calculate_expense_ratio(analysis_dict)
            
        return analysis_dict
    except Exception as e:
        logger.error(f"Error extracting calculated metrics: {str(e)}", exc_info=True)
        # Return the original analysis without modifications
        return analysis

def _generate_kpi_data_impl(analysis):
    """Implementation of KPI data generation.
    
    This is the actual implementation that calculates KPIs.
    All KPI calculations should happen here.
    """
    # Get metrics from analysis
    metrics = analysis.get('metrics', {})
    
    # Extract values with proper defaults
    noi = metrics.get('noi', 0)
    cap_rate = metrics.get('cap_rate', 0)
    cash_on_cash = metrics.get('cash_on_cash', 0)
    dscr = metrics.get('dscr', 0)
    expense_ratio = metrics.get('expense_ratio', 0)
    
    # Define target thresholds
    noi_target = 800  # Example: $800 monthly
    cap_rate_min = 0.06  # 6%
    cap_rate_max = 0.12  # 12%
    cash_on_cash_target = 0.10  # 10%
    dscr_target = 1.25
    expense_ratio_target = 0.40  # 40%
    
    # Determine if metrics are favorable
    noi_favorable = noi >= noi_target
    cap_rate_favorable = cap_rate_min <= cap_rate <= cap_rate_max
    cash_on_cash_favorable = cash_on_cash >= cash_on_cash_target
    dscr_favorable = dscr >= dscr_target
    expense_ratio_favorable = expense_ratio <= expense_ratio_target
    
    # Format the data for KPI display
    kpi_data = {
        'noi': noi,
        'noi_target': f'≥ ${noi_target:.2f}',
        'noi_favorable': noi_favorable,
        
        'cap_rate': cap_rate,
        'cap_rate_target': f'{cap_rate_min*100:.1f}% - {cap_rate_max*100:.1f}%',
        'cap_rate_favorable': cap_rate_favorable,
        
        'cash_on_cash': cash_on_cash,
        'cash_on_cash_target': f'≥ {cash_on_cash_target*100:.1f}%',
        'cash_on_cash_favorable': cash_on_cash_favorable,
        
        'dscr': dscr,
        'dscr_target': f'≥ {dscr_target:.2f}',
        'dscr_favorable': dscr_favorable,
        
        'expense_ratio': expense_ratio,
        'expense_ratio_target': f'≤ {expense_ratio_target*100:.1f}%',
        'expense_ratio_favorable': expense_ratio_favorable
    }
    
    return kpi_data

def format_kpi_values_for_display(kpi_data):
    """Format KPI values for display in UI or reports."""
    # Create a copy to avoid modifying the original
    formatted_data = dict(kpi_data)
    
    # Format numeric values
    if 'noi' in formatted_data and not isinstance(formatted_data['noi'], str):
        formatted_data['noi'] = f'${formatted_data["noi"]:.2f}'
        
    if 'cap_rate' in formatted_data and not isinstance(formatted_data['cap_rate'], str):
        formatted_data['cap_rate'] = f'{formatted_data["cap_rate"]*100:.1f}%'
        
    if 'cash_on_cash' in formatted_data and not isinstance(formatted_data['cash_on_cash'], str):
        formatted_data['cash_on_cash'] = f'{formatted_data["cash_on_cash"]*100:.1f}%'
        
    if 'dscr' in formatted_data and not isinstance(formatted_data['dscr'], str):
        formatted_data['dscr'] = f'{formatted_data["dscr"]:.2f}'
        
    if 'expense_ratio' in formatted_data and not isinstance(formatted_data['expense_ratio'], str):
        formatted_data['expense_ratio'] = f'{formatted_data["expense_ratio"]*100:.1f}%'
    
    return formatted_data

def get_fallback_kpi_data():
    """Return fallback KPI data when calculation fails."""
    return {
        'noi': 0,
        'noi_target': '≥ $800.00',
        'noi_favorable': False,
        'cap_rate': 0,
        'cap_rate_target': '6.0% - 12.0%',
        'cap_rate_favorable': False,
        'cash_on_cash': 0,
        'cash_on_cash_target': '≥ 10.0%',
        'cash_on_cash_favorable': False,
        'dscr': 0,
        'dscr_target': '≥ 1.25',
        'dscr_favorable': False,
        'expense_ratio': 0,
        'expense_ratio_target': '≤ 40.0%',
        'expense_ratio_favorable': False,
        'error': True
    }

# Actual calculation methods
from utils.financial_calculator import FinancialCalculator
from utils.money import Money, Percentage

def calculate_noi(analysis):
    """Calculate Net Operating Income."""
    try:
        income = get_total_income(analysis)
        expenses = get_total_expenses(analysis)
        
        # Use the centralized financial calculator
        return FinancialCalculator.calculate_noi(
            income=Money(income),
            expenses=Money(expenses)
        ).dollars
    except Exception as e:
        logger.error(f"Error calculating NOI: {str(e)}")
        return 0

def calculate_cap_rate(analysis):
    """Calculate Capitalization Rate."""
    try:
        noi = analysis.get('metrics', {}).get('noi', 0)
        if not noi:
            noi = calculate_noi(analysis)
            
        # Annualize NOI if it's monthly
        annual_noi = noi * 12
        
        # Get property value
        property_value = analysis.get('property', {}).get('value', 0)
        if not property_value or property_value == 0:
            return 0
        
        # Use the centralized financial calculator
        return FinancialCalculator.calculate_cap_rate(
            annual_noi=Money(annual_noi),
            property_value=Money(property_value)
        ).as_decimal()
    except Exception as e:
        logger.error(f"Error calculating cap rate: {str(e)}")
        return 0

def calculate_cash_on_cash(analysis):
    """Calculate Cash-on-Cash Return."""
    try:
        noi = analysis.get('metrics', {}).get('noi', 0)
        if not noi:
            noi = calculate_noi(analysis)
            
        # Annualize NOI if it's monthly
        annual_noi = noi * 12
        
        # Get annual debt service
        debt_service = get_annual_debt_service(analysis)
        
        # Calculate annual cash flow
        annual_cash_flow = annual_noi - debt_service
        
        # Get total cash invested
        total_investment = analysis.get('investment', {}).get('total_cash_invested', 0)
        if not total_investment or total_investment == 0:
            return 0
        
        # Use the centralized financial calculator
        result = FinancialCalculator.calculate_cash_on_cash_return(
            annual_cash_flow=Money(annual_cash_flow),
            total_investment=Money(total_investment)
        )
        
        # Handle the case where result is "Infinite"
        if isinstance(result, str) and result == "Infinite":
            return float('inf')
            
        return result.as_decimal()
    except Exception as e:
        logger.error(f"Error calculating cash on cash: {str(e)}")
        return 0

def calculate_dscr(analysis):
    """Calculate Debt Service Coverage Ratio."""
    try:
        noi = analysis.get('metrics', {}).get('noi', 0)
        if not noi:
            noi = calculate_noi(analysis)
            
        # Get monthly debt service
        monthly_debt_service = get_monthly_debt_service(analysis)
        if not monthly_debt_service or monthly_debt_service == 0:
            return 0
        
        # Use the centralized financial calculator
        return FinancialCalculator.calculate_dscr(
            noi=Money(noi),
            debt_service=Money(monthly_debt_service)
        )
    except Exception as e:
        logger.error(f"Error calculating DSCR: {str(e)}")
        return 0

def calculate_expense_ratio(analysis):
    """Calculate Expense Ratio."""
    try:
        expenses = get_total_expenses(analysis)
        income = get_total_income(analysis)
        
        if not income or income == 0:
            return 0
        
        # Use the centralized financial calculator
        return FinancialCalculator.calculate_expense_ratio(
            expenses=Money(expenses),
            income=Money(income)
        ).as_decimal()
    except Exception as e:
        logger.error(f"Error calculating expense ratio: {str(e)}")
        return 0

# Helper functions for accessing data
def get_total_income(analysis):
    """Get total income from analysis data."""
    # Implementation depends on your data structure
    return analysis.get('financials', {}).get('income', {}).get('total', 0)

def get_total_expenses(analysis):
    """Get total expenses from analysis data."""
    # Implementation depends on your data structure
    return analysis.get('financials', {}).get('expenses', {}).get('total', 0)

def get_monthly_debt_service(analysis):
    """Get monthly debt service from analysis data."""
    # Implementation depends on your data structure
    return analysis.get('financing', {}).get('monthly_payment', 0)

def get_annual_debt_service(analysis):
    """Get annual debt service from analysis data."""
    monthly = get_monthly_debt_service(analysis)
    return monthly * 12
