"""
Validation service module for the REI-Tracker application.

This module provides validation services for various data types.
"""

from typing import Dict, Any, List, Optional, Type, TypeVar, Generic
import json
from datetime import datetime

from pydantic import BaseModel, ValidationError

from src.utils.validation_utils import ValidationResult
from src.utils.logging_utils import get_logger

# Set up logger
logger = get_logger(__name__)

T = TypeVar('T', bound=BaseModel)


class ModelValidator(Generic[T]):
    """
    Validator for Pydantic models.
    
    This class provides validation for Pydantic models with standardized
    error handling and formatting.
    """
    
    def __init__(self, model_class: Type[T]) -> None:
        """
        Initialize with a Pydantic model class.
        
        Args:
            model_class: The Pydantic model class to use for validation
        """
        self.model_class = model_class
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult[T]:
        """
        Validate the provided data using the Pydantic model.
        
        Args:
            data: The data to validate
            
        Returns:
            A validation result
        """
        try:
            # Preprocess data if needed
            processed_data = self._preprocess_data(data)
            
            # Validate using Pydantic
            validated_data = self.model_class.parse_obj(processed_data)
            
            return ValidationResult.success(validated_data)
        except ValidationError as e:
            # Convert Pydantic validation errors to our format
            errors: Dict[str, List[str]] = {}
            
            for error in e.errors():
                field = '.'.join(str(loc) for loc in error['loc'])
                message = error['msg']
                
                if field not in errors:
                    errors[field] = []
                
                errors[field].append(message)
            
            logger.warning(f"Validation error: {errors}")
            return ValidationResult.failure(errors)
        except Exception as e:
            logger.error(f"Unexpected validation error: {str(e)}")
            return ValidationResult.failure({"_general": [f"Validation error: {str(e)}"]})
    
    def _preprocess_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess data before validation.
        
        Args:
            data: The data to preprocess
            
        Returns:
            The preprocessed data
        """
        # Default implementation does nothing
        return data


class AnalysisValidator(ModelValidator):
    """
    Validator for Analysis models.
    
    This class provides validation for Analysis models with specialized
    preprocessing for analysis-specific fields.
    """
    
    def _preprocess_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess analysis data before validation.
        
        Args:
            data: The analysis data to preprocess
            
        Returns:
            The preprocessed analysis data
        """
        processed = data.copy()
        
        # Handle unit_types for MultiFamily analysis
        if processed.get('analysis_type') == 'MultiFamily' and 'unit_types' in processed:
            unit_types = processed['unit_types']
            
            # If unit_types is a string, try to parse it as JSON
            if isinstance(unit_types, str):
                try:
                    processed['unit_types'] = json.loads(unit_types)
                except json.JSONDecodeError:
                    logger.error(f"Invalid unit_types JSON: {unit_types}")
                    processed['unit_types'] = None
        
        # Handle comps_data
        if 'comps_data' in processed and processed['comps_data'] is not None:
            comps_data = processed['comps_data']
            
            # If comps_data is a string, try to parse it as JSON
            if isinstance(comps_data, str):
                try:
                    processed['comps_data'] = json.loads(comps_data)
                except json.JSONDecodeError:
                    logger.error(f"Invalid comps_data JSON: {comps_data}")
                    processed['comps_data'] = None
        
        # Ensure ID is present
        if 'id' not in processed or not processed['id']:
            from uuid import uuid4
            processed['id'] = str(uuid4())
        
        # Ensure timestamps are present
        now = datetime.now().isoformat()
        if 'created_at' not in processed or not processed['created_at']:
            processed['created_at'] = now
        if 'updated_at' not in processed or not processed['updated_at']:
            processed['updated_at'] = now
        
        return processed
