"""
File utilities for the REI-Tracker application.

This module provides utility functions for file operations, including
reading and writing JSON files, handling uploads, and managing file paths.
"""

import json
import os
import shutil
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, TypeVar, Generic

from src.config import current_config
from src.utils.logging_utils import get_logger

# Set up logger
logger = get_logger(__name__)

# Type variable for generic JSON data
T = TypeVar('T')


class AtomicJsonFile(Generic[T]):
    """
    Class for atomic operations on JSON files.
    
    This class ensures that file operations are atomic, preventing data corruption
    in case of failures during read/write operations.
    """
    
    def __init__(self, file_path: Union[str, Path]) -> None:
        """
        Initialize with the path to the JSON file.
        
        Args:
            file_path: Path to the JSON file
        """
        self.file_path = Path(file_path)
        self.temp_path = self.file_path.with_suffix('.tmp.json')
        self.backup_path = self.file_path.with_suffix('.bak.json')
    
    def read(self, default: Optional[T] = None) -> T:
        """
        Read data from the JSON file.
        
        Args:
            default: Default value to return if the file doesn't exist
            
        Returns:
            The parsed JSON data
            
        Raises:
            FileNotFoundError: If the file doesn't exist and no default is provided
            json.JSONDecodeError: If the file contains invalid JSON
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            if default is not None:
                return default
            raise
        except json.JSONDecodeError as e:
            # Try to recover from backup
            if self.backup_path.exists():
                logger.warning(f"Recovering {self.file_path} from backup due to JSON decode error")
                with open(self.backup_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            raise
    
    def write(self, data: T) -> None:
        """
        Write data to the JSON file atomically.
        
        Args:
            data: The data to write
            
        Raises:
            IOError: If the write operation fails
        """
        # Ensure directory exists
        os.makedirs(self.file_path.parent, exist_ok=True)
        
        # Create backup if file exists
        if self.file_path.exists():
            shutil.copy2(self.file_path, self.backup_path)
        
        # Write to temporary file
        with open(self.temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        
        # Rename temporary file to target file (atomic operation)
        os.replace(self.temp_path, self.file_path)
    
    def append(self, item: Any, key: Optional[str] = None) -> None:
        """
        Append an item to a JSON array or add/update a key in a JSON object.
        
        Args:
            item: The item to append or the value to set
            key: The key to set (for objects)
            
        Raises:
            TypeError: If the file contains data that is not compatible with the operation
            IOError: If the write operation fails
        """
        try:
            data = self.read(default=[] if key is None else {})
            
            if key is not None:
                # Update object
                if not isinstance(data, dict):
                    raise TypeError(f"Cannot update key in non-object JSON data: {self.file_path}")
                data[key] = item
            else:
                # Append to array
                if not isinstance(data, list):
                    raise TypeError(f"Cannot append to non-array JSON data: {self.file_path}")
                data.append(item)
            
            self.write(data)
        except Exception as e:
            logger.error(f"Error appending to {self.file_path}: {str(e)}")
            raise


def generate_secure_filename(original_filename: str) -> str:
    """
    Generate a secure filename for uploaded files.
    
    Args:
        original_filename: The original filename
        
    Returns:
        A secure filename with a UUID prefix
    """
    # Get file extension
    _, ext = os.path.splitext(original_filename)
    
    # Generate UUID
    file_uuid = str(uuid.uuid4())
    
    # Create secure filename
    return f"{file_uuid}{ext.lower()}"


def validate_file_extension(filename: str, allowed_extensions: Optional[List[str]] = None) -> bool:
    """
    Validate that a file has an allowed extension.
    
    Args:
        filename: The filename to validate
        allowed_extensions: List of allowed extensions (defaults to config)
        
    Returns:
        True if the file extension is allowed, False otherwise
    """
    if allowed_extensions is None:
        allowed_extensions = current_config.UPLOAD_EXTENSIONS
    
    return os.path.splitext(filename)[1].lower() in allowed_extensions


def save_uploaded_file(
    file_data: bytes, 
    original_filename: str, 
    directory: Optional[Path] = None,
    secure_name: bool = True
) -> str:
    """
    Save an uploaded file to the specified directory.
    
    Args:
        file_data: The file data
        original_filename: The original filename
        directory: The directory to save to (defaults to uploads directory)
        secure_name: Whether to generate a secure filename
        
    Returns:
        The path to the saved file (relative to the directory)
        
    Raises:
        ValueError: If the file extension is not allowed
    """
    # Validate file extension
    if not validate_file_extension(original_filename):
        raise ValueError(f"File extension not allowed: {original_filename}")
    
    # Determine directory
    if directory is None:
        directory = current_config.UPLOADS_DIR
    
    # Ensure directory exists
    os.makedirs(directory, exist_ok=True)
    
    # Generate filename
    if secure_name:
        filename = generate_secure_filename(original_filename)
    else:
        filename = os.path.basename(original_filename)
    
    # Save file
    file_path = os.path.join(directory, filename)
    with open(file_path, 'wb') as f:
        f.write(file_data)
    
    return filename
