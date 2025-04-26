"""
File service module for the REI-Tracker application.

This module provides the FileService class for file operations, including
uploads, downloads, and file management.
"""

import os
import shutil
from typing import List, Optional, BinaryIO, Dict, Any
from pathlib import Path
import uuid

from src.config import current_config
from src.utils.file_utils import validate_file_extension, save_uploaded_file
from src.utils.logging_utils import get_logger

# Set up logger
logger = get_logger(__name__)


class FileService:
    """
    File service for file operations.
    
    This class provides methods for file operations, including uploads,
    downloads, and file management.
    """
    
    def __init__(self) -> None:
        """Initialize the file service."""
        self.uploads_dir = current_config.UPLOADS_DIR
        
        # Ensure directory exists
        os.makedirs(self.uploads_dir, exist_ok=True)
    
    def save_file(self, file_data: bytes, original_filename: str, prefix: Optional[str] = None) -> str:
        """
        Save a file to the uploads directory.
        
        Args:
            file_data: The file data
            original_filename: The original filename
            prefix: Optional prefix for the filename
            
        Returns:
            The saved filename
            
        Raises:
            ValueError: If the file extension is not allowed
        """
        try:
            # Validate file extension
            if not validate_file_extension(original_filename):
                raise ValueError(f"File extension not allowed: {original_filename}")
            
            # Generate filename with optional prefix
            if prefix:
                filename = f"{prefix}_{uuid.uuid4()}{os.path.splitext(original_filename)[1].lower()}"
            else:
                filename = f"{uuid.uuid4()}{os.path.splitext(original_filename)[1].lower()}"
            
            # Save file
            file_path = os.path.join(self.uploads_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            logger.info(f"File saved: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise
    
    def save_transaction_file(self, file_data: bytes, original_filename: str, transaction_id: str) -> str:
        """
        Save a transaction file to the uploads directory.
        
        Args:
            file_data: The file data
            original_filename: The original filename
            transaction_id: The transaction ID
            
        Returns:
            The saved filename
            
        Raises:
            ValueError: If the file extension is not allowed
        """
        return self.save_file(file_data, original_filename, f"trans_{transaction_id}")
    
    def save_reimbursement_file(self, file_data: bytes, original_filename: str, reimbursement_id: str) -> str:
        """
        Save a reimbursement file to the uploads directory.
        
        Args:
            file_data: The file data
            original_filename: The original filename
            reimbursement_id: The reimbursement ID
            
        Returns:
            The saved filename
            
        Raises:
            ValueError: If the file extension is not allowed
        """
        return self.save_file(file_data, original_filename, f"reimb_{reimbursement_id}")
    
    def get_file_path(self, filename: str) -> str:
        """
        Get the full path to a file in the uploads directory.
        
        Args:
            filename: The filename
            
        Returns:
            The full path to the file
            
        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        file_path = os.path.join(self.uploads_dir, filename)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {filename}")
        
        return file_path
    
    def get_file_data(self, filename: str) -> bytes:
        """
        Get the data of a file in the uploads directory.
        
        Args:
            filename: The filename
            
        Returns:
            The file data
            
        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        file_path = self.get_file_path(filename)
        
        with open(file_path, 'rb') as f:
            return f.read()
    
    def delete_file(self, filename: str) -> bool:
        """
        Delete a file from the uploads directory.
        
        Args:
            filename: The filename
            
        Returns:
            True if the file was deleted, False if not found
        """
        try:
            file_path = os.path.join(self.uploads_dir, filename)
            
            if not os.path.exists(file_path):
                return False
            
            os.remove(file_path)
            logger.info(f"File deleted: {filename}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            raise
    
    def list_files(self, prefix: Optional[str] = None) -> List[str]:
        """
        List files in the uploads directory.
        
        Args:
            prefix: Optional prefix to filter files
            
        Returns:
            List of filenames
        """
        try:
            files = os.listdir(self.uploads_dir)
            
            if prefix:
                return [f for f in files if f.startswith(prefix)]
            
            return files
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            raise
    
    def file_exists(self, filename: str) -> bool:
        """
        Check if a file exists in the uploads directory.
        
        Args:
            filename: The filename
            
        Returns:
            True if the file exists, False otherwise
        """
        file_path = os.path.join(self.uploads_dir, filename)
        return os.path.exists(file_path)
