"""
Logging utilities for the REI-Tracker application.

This module provides logging configuration and utility functions for consistent
logging throughout the application.
"""

import logging
import logging.handlers
import os
from typing import Optional

from src.config import current_config


def setup_logger(
    name: str, 
    level: Optional[str] = None, 
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger with the specified name, level, and log file.
    
    Args:
        name: The name of the logger
        level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: The path to the log file
        
    Returns:
        A configured logger instance
    """
    # Get logger
    logger = logging.getLogger(name)
    
    # Set level from parameter or config
    log_level = level or current_config.LOG_LEVEL
    logger.setLevel(getattr(logging, log_level))
    
    # Create formatter
    formatter = logging.Formatter(current_config.LOG_FORMAT)
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Add file handler if specified
    if log_file:
        # Ensure directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Create rotating file handler (10 MB max, keep 5 backups)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# Create application logger
app_logger = setup_logger("rei_tracker", log_file=current_config.LOG_FILE)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.
    
    Args:
        name: The name of the module (typically __name__)
        
    Returns:
        A configured logger instance
    """
    return logging.getLogger(f"rei_tracker.{name}")


class AuditLogger:
    """
    Logger for audit events (user actions, data changes, etc.).
    
    This class provides methods for logging audit events with consistent
    formatting and additional context.
    """
    
    def __init__(self) -> None:
        """Initialize the audit logger."""
        self.logger = setup_logger(
            "rei_tracker.audit", 
            log_file=os.path.join(os.path.dirname(current_config.LOG_FILE), "audit.log")
        )
    
    def log_user_action(
        self, 
        user_id: str, 
        action: str, 
        resource_type: str, 
        resource_id: Optional[str] = None, 
        details: Optional[dict] = None
    ) -> None:
        """
        Log a user action.
        
        Args:
            user_id: The ID of the user performing the action
            action: The action performed (e.g., "create", "update", "delete")
            resource_type: The type of resource (e.g., "property", "analysis")
            resource_id: The ID of the resource (if applicable)
            details: Additional details about the action
        """
        message = f"USER_ACTION: {user_id} {action} {resource_type}"
        if resource_id:
            message += f" {resource_id}"
        
        if details:
            message += f" - {details}"
        
        self.logger.info(message)
    
    def log_system_event(
        self, 
        event_type: str, 
        component: str, 
        details: Optional[dict] = None
    ) -> None:
        """
        Log a system event.
        
        Args:
            event_type: The type of event (e.g., "startup", "shutdown", "error")
            component: The system component (e.g., "database", "api")
            details: Additional details about the event
        """
        message = f"SYSTEM_EVENT: {event_type} {component}"
        
        if details:
            message += f" - {details}"
        
        self.logger.info(message)


# Create audit logger instance
audit_logger = AuditLogger()
