"""
Custom security middleware for OWASP best practices.
Adds security headers and request logging.
"""
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('apps.security')


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to all responses.
    Implements OWASP security best practices.
    """
    
    def process_response(self, request, response):
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        
        # X-Content-Type-Options
        response['X-Content-Type-Options'] = 'nosniff'
        
        # X-Frame-Options (already set in settings, but ensuring it's here too)
        response['X-Frame-Options'] = 'DENY'
        
        # X-XSS-Protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy
        response['Permissions-Policy'] = (
            'geolocation=(), '
            'microphone=(), '
            'camera=(), '
            'payment=(), '
            'usb=()'
        )
        
        # Log security-relevant requests
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            logger.info(
                f"Security event: {request.method} {request.path} "
                f"from {request.META.get('REMOTE_ADDR', 'unknown')} "
                f"User: {getattr(request.user, 'username', 'anonymous')}"
            )
        
        return response

