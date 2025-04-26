"""
User repository module for the REI-Tracker application.

This module provides the UserRepository class for user data persistence
and retrieval.
"""

from typing import List, Optional

from src.config import current_config
from src.models.user import User
from src.repositories.base_repository import BaseRepository
from src.utils.logging_utils import get_logger

# Set up logger
logger = get_logger(__name__)


class UserRepository(BaseRepository[User]):
    """
    User repository for user data persistence and retrieval.
    
    This class provides methods for user-specific operations, such as
    finding users by email and authentication.
    """
    
    def __init__(self) -> None:
        """Initialize the user repository."""
        super().__init__(str(current_config.USERS_FILE), User)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.
        
        Args:
            email: Email of the user to get
            
        Returns:
            The user, or None if not found
        """
        try:
            email = email.lower()
            users = self.get_all()
            
            for user in users:
                if user.email.lower() == email:
                    return user
            
            return None
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            raise
    
    def email_exists(self, email: str) -> bool:
        """
        Check if a user with the given email exists.
        
        Args:
            email: Email to check
            
        Returns:
            True if a user with the email exists, False otherwise
        """
        return self.get_by_email(email) is not None
    
    def get_admins(self) -> List[User]:
        """
        Get all admin users.
        
        Returns:
            List of admin users
        """
        try:
            users = self.get_all()
            return [user for user in users if user.is_admin()]
        except Exception as e:
            logger.error(f"Error getting admin users: {str(e)}")
            raise
