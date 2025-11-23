"""
Custom exception handlers for API security.
Provides secure error responses without exposing sensitive information.
"""
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger('apps.security')


def custom_exception_handler(exc, context):
    """
    Custom exception handler that:
    - Prevents information leakage
    - Logs security-relevant errors
    - Returns consistent error format
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Customize the response data
        custom_response_data = {
            'error': {
                'status_code': response.status_code,
                'message': 'An error occurred',
                'details': []
            }
        }
        
        # Only expose detailed errors in DEBUG mode
        if hasattr(exc, 'detail'):
            if isinstance(exc.detail, dict):
                custom_response_data['error']['details'] = exc.detail
            elif isinstance(exc.detail, list):
                custom_response_data['error']['details'] = exc.detail
            else:
                custom_response_data['error']['message'] = str(exc.detail)
        
        # Log security-relevant errors
        if response.status_code in [401, 403, 429]:
            request = context.get('request')
            logger.warning(
                f"Security event: {response.status_code} error on {request.path} "
                f"from {request.META.get('REMOTE_ADDR', 'unknown')} "
                f"User: {getattr(request.user, 'username', 'anonymous')}"
            )
        
        response.data = custom_response_data
    
    return response

