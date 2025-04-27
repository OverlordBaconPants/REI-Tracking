from flask import Blueprint, request, jsonify
from datetime import date
import logging
from src.services.loan_service import LoanService
from src.utils.auth_middleware import login_required
from src.utils.calculations.loan_comparison import LoanComparison
from src.utils.money import Money

logger = logging.getLogger(__name__)

# Create Blueprint
loan_routes = Blueprint('loan_routes', __name__)

# Initialize services
loan_service = LoanService()

@loan_routes.route('/api/loans/property/<property_id>', methods=['GET'])
@login_required
def get_loans_by_property(property_id):
    """Get all loans for a property."""
    try:
        loans = loan_service.get_loans_by_property(property_id)
        return jsonify({
            'success': True,
            'loans': [loan.to_dict() for loan in loans]
        }), 200
    except Exception as e:
        logger.error(f"Error getting loans for property {property_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@loan_routes.route('/api/loans/property/<property_id>/active', methods=['GET'])
@login_required
def get_active_loans_by_property(property_id):
    """Get active loans for a property."""
    try:
        loans = loan_service.get_active_loans_by_property(property_id)
        return jsonify({
            'success': True,
            'loans': [loan.to_dict() for loan in loans]
        }), 200
    except Exception as e:
        logger.error(f"Error getting active loans for property {property_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@loan_routes.route('/api/loans/<loan_id>', methods=['GET'])
@login_required
def get_loan(loan_id):
    """Get a loan by ID."""
    try:
        loan = loan_service.get_loan_by_id(loan_id)
        if not loan:
            return jsonify({
                'success': False,
                'error': f"Loan with ID {loan_id} not found"
            }), 404
            
        return jsonify({
            'success': True,
            'loan': loan.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error getting loan {loan_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@loan_routes.route('/api/loans', methods=['POST'])
@login_required
def create_loan():
    """Create a new loan."""
    try:
        loan_data = request.json
        if not loan_data:
            return jsonify({
                'success': False,
                'error': "No loan data provided"
            }), 400
            
        loan = loan_service.create_loan(loan_data)
        return jsonify({
            'success': True,
            'loan': loan.to_dict(),
            'message': "Loan created successfully"
        }), 201
    except ValueError as e:
        logger.error(f"Validation error creating loan: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error creating loan: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@loan_routes.route('/api/loans/<loan_id>', methods=['PUT'])
@login_required
def update_loan(loan_id):
    """Update an existing loan."""
    try:
        loan_data = request.json
        if not loan_data:
            return jsonify({
                'success': False,
                'error': "No loan data provided"
            }), 400
            
        loan = loan_service.update_loan(loan_id, loan_data)
        if not loan:
            return jsonify({
                'success': False,
                'error': f"Loan with ID {loan_id} not found"
            }), 404
            
        return jsonify({
            'success': True,
            'loan': loan.to_dict(),
            'message': "Loan updated successfully"
        }), 200
    except ValueError as e:
        logger.error(f"Validation error updating loan {loan_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error updating loan {loan_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@loan_routes.route('/api/loans/<loan_id>', methods=['DELETE'])
@login_required
def delete_loan(loan_id):
    """Delete a loan."""
    try:
        success = loan_service.delete_loan(loan_id)
        if not success:
            return jsonify({
                'success': False,
                'error': f"Loan with ID {loan_id} not found"
            }), 404
            
        return jsonify({
            'success': True,
            'message': "Loan deleted successfully"
        }), 200
    except Exception as e:
        logger.error(f"Error deleting loan {loan_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@loan_routes.route('/api/loans/<loan_id>/refinance', methods=['POST'])
@login_required
def refinance_loan(loan_id):
    """Refinance a loan."""
    try:
        new_loan_data = request.json
        if not new_loan_data:
            return jsonify({
                'success': False,
                'error': "No loan data provided for refinance"
            }), 400
            
        new_loan = loan_service.refinance_loan(loan_id, new_loan_data)
        if not new_loan:
            return jsonify({
                'success': False,
                'error': f"Loan with ID {loan_id} not found"
            }), 404
            
        return jsonify({
            'success': True,
            'loan': new_loan.to_dict(),
            'message': "Loan refinanced successfully"
        }), 200
    except ValueError as e:
        logger.error(f"Validation error refinancing loan {loan_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error refinancing loan {loan_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@loan_routes.route('/api/loans/<loan_id>/payoff', methods=['POST'])
@login_required
def pay_off_loan(loan_id):
    """Mark a loan as paid off."""
    try:
        data = request.json or {}
        payoff_date_str = data.get('payoff_date')
        
        payoff_date = None
        if payoff_date_str:
            try:
                payoff_date = date.fromisoformat(payoff_date_str)
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': "Invalid payoff date format. Use YYYY-MM-DD."
                }), 400
                
        loan = loan_service.pay_off_loan(loan_id, payoff_date)
        if not loan:
            return jsonify({
                'success': False,
                'error': f"Loan with ID {loan_id} not found"
            }), 404
            
        return jsonify({
            'success': True,
            'loan': loan.to_dict(),
            'message': "Loan marked as paid off successfully"
        }), 200
    except Exception as e:
        logger.error(f"Error paying off loan {loan_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@loan_routes.route('/api/loans/<loan_id>/balance', methods=['GET'])
@login_required
def get_loan_balance(loan_id):
    """Get the current balance of a loan."""
    try:
        data = request.args
        as_of_date_str = data.get('as_of_date')
        
        as_of_date = None
        if as_of_date_str:
            try:
                as_of_date = date.fromisoformat(as_of_date_str)
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': "Invalid date format. Use YYYY-MM-DD."
                }), 400
                
        loan = loan_service.get_loan_by_id(loan_id)
        if not loan:
            return jsonify({
                'success': False,
                'error': f"Loan with ID {loan_id} not found"
            }), 404
            
        balance = loan.calculate_remaining_balance(as_of_date)
        
        return jsonify({
            'success': True,
            'loan_id': loan_id,
            'balance': str(balance),
            'as_of_date': as_of_date.isoformat() if as_of_date else date.today().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error getting balance for loan {loan_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@loan_routes.route('/api/loans/<loan_id>/update-balance', methods=['POST'])
@login_required
def update_loan_balance(loan_id):
    """Update the current balance of a loan."""
    try:
        data = request.json or {}
        as_of_date_str = data.get('as_of_date')
        
        as_of_date = None
        if as_of_date_str:
            try:
                as_of_date = date.fromisoformat(as_of_date_str)
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': "Invalid date format. Use YYYY-MM-DD."
                }), 400
                
        loan = loan_service.update_loan_balance(loan_id, as_of_date)
        if not loan:
            return jsonify({
                'success': False,
                'error': f"Loan with ID {loan_id} not found"
            }), 404
            
        return jsonify({
            'success': True,
            'loan': loan.to_dict(),
            'message': "Loan balance updated successfully"
        }), 200
    except Exception as e:
        logger.error(f"Error updating balance for loan {loan_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@loan_routes.route('/api/loans/property/<property_id>/total-debt', methods=['GET'])
@login_required
def get_total_debt(property_id):
    """Get the total debt for a property."""
    try:
        data = request.args
        as_of_date_str = data.get('as_of_date')
        
        as_of_date = None
        if as_of_date_str:
            try:
                as_of_date = date.fromisoformat(as_of_date_str)
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': "Invalid date format. Use YYYY-MM-DD."
                }), 400
                
        total_debt = loan_service.get_total_debt_for_property(property_id, as_of_date)
        
        return jsonify({
            'success': True,
            'property_id': property_id,
            'total_debt': str(total_debt),
            'as_of_date': as_of_date.isoformat() if as_of_date else date.today().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error getting total debt for property {property_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@loan_routes.route('/api/loans/property/<property_id>/monthly-payment', methods=['GET'])
@login_required
def get_total_monthly_payment(property_id):
    """Get the total monthly payment for a property."""
    try:
        total_payment = loan_service.get_total_monthly_payment_for_property(property_id)
        
        return jsonify({
            'success': True,
            'property_id': property_id,
            'total_monthly_payment': str(total_payment)
        }), 200
    except Exception as e:
        logger.error(f"Error getting total monthly payment for property {property_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@loan_routes.route('/api/loans/<loan_id>/amortization', methods=['GET'])
@login_required
def get_amortization_schedule(loan_id):
    """Get the amortization schedule for a loan."""
    try:
        data = request.args
        max_periods_str = data.get('max_periods')
        
        max_periods = None
        if max_periods_str:
            try:
                max_periods = int(max_periods_str)
                if max_periods <= 0:
                    return jsonify({
                        'success': False,
                        'error': "max_periods must be a positive integer"
                    }), 400
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': "max_periods must be a valid integer"
                }), 400
                
        schedule = loan_service.generate_amortization_schedule(loan_id, max_periods)
        if not schedule:
            return jsonify({
                'success': False,
                'error': f"Loan with ID {loan_id} not found"
            }), 404
            
        return jsonify({
            'success': True,
            'loan_id': loan_id,
            'schedule': schedule
        }), 200
    except Exception as e:
        logger.error(f"Error generating amortization schedule for loan {loan_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@loan_routes.route('/api/loans/compare', methods=['POST'])
@login_required
def compare_loans():
    """Compare multiple loan options."""
    try:
        data = request.json
        if not data or 'loan_options' not in data:
            return jsonify({
                'success': False,
                'error': "No loan options provided for comparison"
            }), 400
            
        loan_options = data['loan_options']
        if not isinstance(loan_options, list) or len(loan_options) < 1:
            return jsonify({
                'success': False,
                'error': "loan_options must be a list with at least one option"
            }), 400
            
        comparison = loan_service.compare_loans(loan_options)
        
        return jsonify({
            'success': True,
            'comparison': comparison
        }), 200
    except Exception as e:
        logger.error(f"Error comparing loans: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@loan_routes.route('/api/loans/<loan_id>/balloon', methods=['POST'])
@login_required
def update_balloon_payment(loan_id):
    """Update a loan with balloon payment details."""
    try:
        data = request.json
        if not data or 'balloon_term_months' not in data:
            return jsonify({
                'success': False,
                'error': "balloon_term_months is required"
            }), 400
            
        try:
            balloon_term_months = int(data['balloon_term_months'])
            if balloon_term_months <= 0:
                return jsonify({
                    'success': False,
                    'error': "balloon_term_months must be a positive integer"
                }), 400
        except ValueError:
            return jsonify({
                'success': False,
                'error': "balloon_term_months must be a valid integer"
            }), 400
            
        loan = loan_service.update_balloon_payment(loan_id, balloon_term_months)
        if not loan:
            return jsonify({
                'success': False,
                'error': f"Loan with ID {loan_id} not found"
            }), 404
            
        return jsonify({
            'success': True,
            'loan': loan.to_dict(),
            'message': "Balloon payment updated successfully"
        }), 200
    except ValueError as e:
        logger.error(f"Validation error updating balloon payment for loan {loan_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error updating balloon payment for loan {loan_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@loan_routes.route('/api/loans/<loan_id>/calculate-balloon', methods=['POST'])
@login_required
def calculate_balloon_payment(loan_id):
    """Calculate balloon payment details for a loan."""
    try:
        data = request.json
        if not data or 'balloon_term_months' not in data:
            return jsonify({
                'success': False,
                'error': "balloon_term_months is required"
            }), 400
            
        try:
            balloon_term_months = int(data['balloon_term_months'])
            if balloon_term_months <= 0:
                return jsonify({
                    'success': False,
                    'error': "balloon_term_months must be a positive integer"
                }), 400
        except ValueError:
            return jsonify({
                'success': False,
                'error': "balloon_term_months must be a valid integer"
            }), 400
            
        balloon_details = loan_service.calculate_balloon_payment(loan_id, balloon_term_months)
        if not balloon_details:
            return jsonify({
                'success': False,
                'error': f"Loan with ID {loan_id} not found"
            }), 404
            
        return jsonify({
            'success': True,
            'loan_id': loan_id,
            'balloon_details': balloon_details
        }), 200
    except Exception as e:
        logger.error(f"Error calculating balloon payment for loan {loan_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@loan_routes.route('/api/loans/refinance-analysis', methods=['POST'])
@login_required
def analyze_refinance():
    """Analyze potential savings from refinancing a loan."""
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': "No data provided for refinance analysis"
            }), 400
            
        required_fields = ['current_loan', 'new_loan', 'closing_costs']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f"Missing required field: {field}"
                }), 400
                
        # Convert closing costs to Money object
        try:
            closing_costs = Money(data['closing_costs'])
        except Exception:
            return jsonify({
                'success': False,
                'error': "Invalid closing_costs value"
            }), 400
            
        # Perform refinance analysis
        analysis = LoanComparison.calculate_refinance_savings(
            data['current_loan'],
            data['new_loan'],
            closing_costs
        )
        
        return jsonify({
            'success': True,
            'analysis': analysis
        }), 200
    except Exception as e:
        logger.error(f"Error analyzing refinance: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
