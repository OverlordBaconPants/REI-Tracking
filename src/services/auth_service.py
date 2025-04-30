"""
Authentication service module for the REI-Tracker application.

This module provides the AuthService class for user authentication,
session management, and security features.
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, Any
from flask import session, request
import json
from passlib.hash import pbkdf2_sha256
from werkzeug.security import check_password_hash

from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.utils.logging_utils import get_logger, audit_logger

# Set up logger
logger = get_logger(__name__)

# Constants for session management
SESSION_TIMEOUT = 3600  # 1 hour in seconds
EXTENDED_SESSION_TIMEOUT = 2592000  # 30 days in seconds
MAX_LOGIN_ATTEMPTS = 5
LOGIN_COOLDOWN_PERIOD = 300  # 5 minutes in seconds


class AuthService:
    """
    Authentication service for user authentication and session management.
    
    This class provides methods for user authentication, session management,
    and security features.
    """
    
    def __init__(self, user_repository: Optional[UserRepository] = None) -> None:
        """
        Initialize the authentication service.
        
        Args:
            user_repository: The user repository to use
        """
        self.user_repository = user_repository or UserRepository()
        self._login_attempts: Dict[str, Dict[str, Any]] = {}
    
    def authenticate(self, email: str, password: str) -> Tuple[bool, Optional[User], Optional[str]]:
        """
        Authenticate a user with email and password.
        
        Args:
            email: The user's email
            password: The user's password
            
        Returns:
            A tuple containing:
            - Whether authentication was successful
            - The authenticated user, or None if authentication failed
            - An error message, or None if authentication was successful
        """
        # Check if the user is rate limited
        if self._is_rate_limited(email):
            logger.warning(f"Login attempt for rate-limited user: {email}")
            return False, None, "Too many failed login attempts. Please try again later."
        
        # Get the user by email
        user = self.user_repository.get_by_email(email)
        if not user:
            self._record_failed_attempt(email)
            logger.warning(f"Login attempt for non-existent user: {email}")
            return False, None, "Invalid email or password"
        
        # Verify the password
        # Check if the password is in Werkzeug format (starts with pbkdf2:sha256:)
        if user.password.startswith('pbkdf2:sha256:'):
            # Use Werkzeug's check_password_hash for Werkzeug-formatted hashes
            if not check_password_hash(user.password, password):
                self._record_failed_attempt(email)
                logger.warning(f"Failed login attempt for user: {email}")
                return False, None, "Invalid email or password"
        else:
            # Use passlib's verify for passlib-formatted hashes
            if not pbkdf2_sha256.verify(password, user.password):
                self._record_failed_attempt(email)
                logger.warning(f"Failed login attempt for user: {email}")
                return False, None, "Invalid email or password"
        
        # Reset login attempts on successful login
        self._reset_login_attempts(email)
        
        # Log successful login
        logger.info(f"User authenticated successfully: {email}")
        audit_logger.log_user_action(
            user_id=user.id,
            action="login",
            resource_type="session"
        )
        
        return True, user, None
    
    def create_session(self, user: User, remember: bool = False) -> None:
        """
        Create a session for the authenticated user.
        
        Args:
            user: The authenticated user
            remember: Whether to create an extended session
        """
        # Set session data
        session['user_id'] = user.id
        session['user_email'] = user.email
        session['user_role'] = user.role
        session['login_time'] = datetime.now().isoformat()
        
        # Set session expiration
        if remember:
            # Set session as permanent if it's a Flask session object
            if hasattr(session, 'permanent'):
                session.permanent = True
            session['remember'] = True
            session['expires_at'] = (datetime.now() + timedelta(seconds=EXTENDED_SESSION_TIMEOUT)).isoformat()
        else:
            # Set session as non-permanent if it's a Flask session object
            if hasattr(session, 'permanent'):
                session.permanent = False
            session['remember'] = False
            session['expires_at'] = (datetime.now() + timedelta(seconds=SESSION_TIMEOUT)).isoformat()
        
        logger.info(f"Session created for user: {user.email}, remember: {remember}")
    
    def validate_session(self) -> Tuple[bool, Optional[str]]:
        """
        Validate the current session.
        
        Returns:
            A tuple containing:
            - Whether the session is valid
            - An error message, or None if the session is valid
        """
        # Check if user is logged in
        if 'user_id' not in session:
            return False, "Not logged in"
        
        # Check if session has expired
        if 'expires_at' in session:
            expires_at = datetime.fromisoformat(session['expires_at'])
            if datetime.now() > expires_at:
                self.end_session()
                return False, "Session expired"
        
        # Extend session if needed
        self._refresh_session()
        
        return True, None
    
    def end_session(self) -> None:
        """End the current session."""
        if 'user_id' in session:
            user_id = session['user_id']
            audit_logger.log_user_action(
                user_id=user_id,
                action="logout",
                resource_type="session"
            )
            logger.info(f"Session ended for user ID: {user_id}")
        
        # Clear session
        session.clear()
    
    def get_current_user(self) -> Optional[User]:
        """
        Get the current authenticated user.
        
        Returns:
            The current user, or None if not authenticated
        """
        # Check if user is logged in
        if 'user_id' not in session:
            return None
        
        # Get user by ID
        user = self.user_repository.get_by_id(session['user_id'])
        if not user:
            # Clear session if user not found
            self.end_session()
            return None
        
        return user
    
    def add_security_headers(self, response: Any) -> Any:
        """
        Add security headers to a response.
        
        Args:
            response: The response to add headers to
            
        Returns:
            The response with added headers
        """
        # Content Security Policy
        csp = "; ".join([
            # Default fallback
            "default-src 'self'",
            
            # Script sources
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
            "https://code.jquery.com "
            "https://cdn.jsdelivr.net "
            "https://cdnjs.cloudflare.com",
            
            # Style sources
            "style-src 'self' 'unsafe-inline' "
            "https://cdn.jsdelivr.net "
            "https://cdnjs.cloudflare.com",
            
            # Font sources
            "font-src 'self' "
            "https://cdn.jsdelivr.net "
            "https://cdnjs.cloudflare.com",
            
            # Image sources
            "img-src 'self' data: https:",
            
            # Connect sources
            "connect-src 'self'",
            
            # Object sources
            "object-src 'none'",
            
            # Media sources
            "media-src 'self'",
            
            # Frame sources
            "frame-src 'self'"
        ])
        
        # Add security headers
        response.headers.update({
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': csp,
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        })
        
        return response
    
    def _refresh_session(self) -> None:
        """Refresh the session expiration time."""
        if 'remember' in session and session['remember']:
            session['expires_at'] = (datetime.now() + timedelta(seconds=EXTENDED_SESSION_TIMEOUT)).isoformat()
        else:
            session['expires_at'] = (datetime.now() + timedelta(seconds=SESSION_TIMEOUT)).isoformat()
    
    def _record_failed_attempt(self, email: str) -> None:
        """
        Record a failed login attempt.
        
        Args:
            email: The email used in the attempt
        """
        current_time = time.time()
        
        if email not in self._login_attempts:
            self._login_attempts[email] = {
                'count': 1,
                'first_attempt': current_time,
                'last_attempt': current_time
            }
        else:
            # Reset count if cooldown period has passed
            if current_time - self._login_attempts[email]['last_attempt'] > LOGIN_COOLDOWN_PERIOD:
                self._login_attempts[email] = {
                    'count': 1,
                    'first_attempt': current_time,
                    'last_attempt': current_time
                }
            else:
                self._login_attempts[email]['count'] += 1
                self._login_attempts[email]['last_attempt'] = current_time
        
        # Log if approaching or exceeding limit
        if self._login_attempts[email]['count'] >= MAX_LOGIN_ATTEMPTS:
            logger.warning(f"User {email} has been rate limited after {MAX_LOGIN_ATTEMPTS} failed login attempts")
    
    def _reset_login_attempts(self, email: str) -> None:
        """
        Reset login attempts for a user.
        
        Args:
            email: The user's email
        """
        if email in self._login_attempts:
            del self._login_attempts[email]
    
    def _is_rate_limited(self, email: str) -> bool:
        """
        Check if a user is rate limited.
        
        Args:
            email: The user's email
            
        Returns:
            Whether the user is rate limited
        """
        if email not in self._login_attempts:
            return False
        
        current_time = time.time()
        attempts = self._login_attempts[email]
        
        # Check if cooldown period has passed
        if current_time - attempts['last_attempt'] > LOGIN_COOLDOWN_PERIOD:
            return False
        
        # Check if max attempts reached
        return attempts['count'] >= MAX_LOGIN_ATTEMPTS
