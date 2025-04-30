# utils/response_handler.py

from typing import Optional, Union, Dict, Any
from flask import jsonify, redirect, request, Response
from utils.flash import flash_message
import logging

logger = logging.getLogger(__name__)

def handle_response(
    success: bool,
    message: str,
    redirect_url: Optional[str] = None,
    status_code: int = 200,
    data: Optional[Dict[str, Any]] = None,
    error_field: Optional[str] = None
) -> Union[Response, tuple]:
    """
    Unified response handler for both AJAX and regular requests.
    
    Args:
        success: Whether the operation was successful
        message: Message to display to the user
        redirect_url: URL to redirect to (if any)
        status_code: HTTP status code to return
        data: Additional data to include in JSON response
        error_field: Field name for validation errors
    
    Returns:
        Either a JSON response (for AJAX) or a redirect with flash message
    """
    try:
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if is_ajax:
            response_data = {
                'success': success,
                'message': message
            }
            
            if redirect_url:
                response_data['redirect'] = redirect_url
                
            if data:
                response_data.update(data)
                
            if error_field:
                response_data['field'] = error_field
                
            return jsonify(response_data), status_code if not success else 200
        else:
            # For regular requests, flash the message and redirect
            flash_message(message, 'success' if success else 'error')
            
            if redirect_url:
                return redirect(redirect_url)
            else:
                # If no redirect URL provided, return to previous page
                return redirect(request.referrer or '/')
                
    except Exception as e:
        logger.error(f"Error in handle_response: {str(e)}")
        if is_ajax:
            return jsonify({
                'success': False,
                'message': 'An unexpected error occurred.'
            }), 500
        else:
            flash_message('An unexpected error occurred.', 'error')
            return redirect(request.referrer or '/')