import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def calculate_mao(arv: float, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate Maximum Allowable Offer (MAO) based on ARV and analysis data.
    
    Args:
        arv: After Repair Value from comps
        analysis_data: Complete analysis data dictionary
        
    Returns:
        Dictionary containing MAO value and calculation components
    """
    try:
        # Extract values from analysis data with safe conversion
        renovation_costs = float(analysis_data.get('renovation_costs', 0) or 0)
        renovation_duration = float(analysis_data.get('renovation_duration', 0) or 0)
        closing_costs = float(analysis_data.get('closing_costs', 0) or 0)
        
        # Get loan parameters - defaults to standard 75% LTV if not found
        ltv_percentage = 75.0  # default
        
        # Adjust LTV based on analysis type
        analysis_type = analysis_data.get('analysis_type', '')
        if 'BRRRR' in analysis_type:
            # For BRRRR, use a standard 75% LTV if not specified
            ltv_percentage = 75.0
            # Check if there's an explicit refinance LTV percentage field
            if 'refinance_ltv_percentage' in analysis_data:
                ltv_percentage = float(analysis_data.get('refinance_ltv_percentage', 75.0) or 75.0)
        elif analysis_data.get('has_balloon_payment'):
            # Use balloon refinance LTV if balloon payment is enabled
            ltv_percentage = float(analysis_data.get('balloon_refinance_ltv_percentage', 75.0) or 75.0)
        
        # Calculate monthly holding costs
        monthly_holding_costs = calculate_monthly_holding_costs(analysis_data)
        
        # Calculate total holding costs
        total_holding_costs = monthly_holding_costs * renovation_duration
        
        logger.debug(f"MAO calculation inputs: arv={arv}, ltv_percentage={ltv_percentage}%, " +
                    f"renovation_costs={renovation_costs}, closing_costs={closing_costs}, " +
                    f"monthly_holding_costs={monthly_holding_costs}, holding_months={renovation_duration}")


        # Calculate loan amount based on LTV
        loan_amount = arv * (ltv_percentage / 100)
        logger.debug(f"Calculated loan amount: {loan_amount} based on {ltv_percentage}% of ARV {arv}")
        
        # Set max cash left in deal - could be configurable in the future
        max_cash_left = 10000  # $10k default
        
        # Calculate MAO using the formula
        mao = loan_amount - renovation_costs - closing_costs - total_holding_costs + max_cash_left
        logger.debug(f"Raw MAO calculation: {mao} = {loan_amount} - {renovation_costs} - {closing_costs} - {total_holding_costs} + {max_cash_left}")
        
        # Ensure MAO is not negative
        mao = max(0, mao)
        
        logger.debug(f"MAO calculation details: arv={arv}, ltv={ltv_percentage}%, loan_amount={loan_amount}, " +
                    f"renovation_costs={renovation_costs}, closing_costs={closing_costs}, " +
                    f"total_holding_costs={total_holding_costs}, max_cash_left={max_cash_left}, mao={mao}")
        
        # Return MAO value and calculation components for transparency
        return {
            'value': mao,
            'arv': arv,
            'ltv_percentage': ltv_percentage,
            'renovation_costs': renovation_costs,
            'closing_costs': closing_costs,
            'monthly_holding_costs': monthly_holding_costs,
            'total_holding_costs': total_holding_costs,
            'holding_months': renovation_duration,
            'max_cash_left': max_cash_left
        }
    except Exception as e:
        logger.error(f"Error calculating MAO: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {'value': 0, 'error': str(e)}

def calculate_monthly_holding_costs(analysis_data: Dict[str, Any]) -> float:
    """
    Calculate monthly holding costs during renovation period.
    
    Args:
        analysis_data: Analysis data dictionary
        
    Returns:
        Monthly holding cost amount
    """
    try:
        # Get basic property expenses
        property_taxes = float(analysis_data.get('property_taxes', 0) or 0)
        insurance = float(analysis_data.get('insurance', 0) or 0)
        utilities = float(analysis_data.get('utilities', 0) or 0)
        hoa_coa = float(analysis_data.get('hoa_coa_coop', 0) or 0)
        
        # Calculate loan interest - handle different analysis types
        loan_amount = 0
        interest_rate = 0
        
        if analysis_data.get('analysis_type', '').startswith('BRRRR'):
            # Use initial loan for BRRRR
            loan_amount = float(analysis_data.get('initial_loan_amount', 0) or 0)
            interest_rate = float(analysis_data.get('initial_loan_interest_rate', 0) or 0)
        else:
            # For other types, use loan1 as the primary loan
            loan_amount = float(analysis_data.get('loan1_loan_amount', 0) or 0)
            interest_rate = float(analysis_data.get('loan1_loan_interest_rate', 0) or 0)
        
        # Calculate monthly interest payment (interest-only during renovation)
        monthly_interest = loan_amount * (interest_rate / 100 / 12) if loan_amount > 0 and interest_rate > 0 else 0
        
        # Sum all monthly costs
        monthly_holding_costs = property_taxes + insurance + utilities + hoa_coa + monthly_interest
        
        logger.debug(f"Calculated monthly holding costs: {monthly_holding_costs}")
        return monthly_holding_costs
    except Exception as e:
        logger.error(f"Error calculating monthly holding costs: {str(e)}")
        return 0.0