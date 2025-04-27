"""
Analysis repository module for the REI-Tracker application.

This module provides the AnalysisRepository class for analysis data persistence
and retrieval.
"""

from typing import List, Optional, Dict, Any, Tuple
import os
import json
from datetime import datetime

from src.config import current_config
from src.models.analysis import Analysis, UnitType
from src.repositories.base_repository import BaseRepository
from src.utils.file_utils import AtomicJsonFile
from src.utils.logging_utils import get_logger

# Set up logger
logger = get_logger(__name__)


class AnalysisRepository(BaseRepository[Analysis]):
    """
    Analysis repository for analysis data persistence and retrieval.
    
    This class provides methods for analysis-specific operations, such as
    finding analyses by user and type.
    """
    
    def __init__(self) -> None:
        """Initialize the analysis repository."""
        analyses_dir = current_config.ANALYSES_DIR
        os.makedirs(analyses_dir, exist_ok=True)
        
        # Initialize with a file path that will be used for each analysis
        super().__init__(os.path.join(analyses_dir, "analyses.json"), Analysis)
    
    def get_by_user(self, user_id: str) -> List[Analysis]:
        """
        Get analyses by user ID.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of analyses for the user
        """
        try:
            analyses = self.get_all()
            return [a for a in analyses if a.user_id == user_id]
        except Exception as e:
            logger.error(f"Error getting analyses by user: {str(e)}")
            raise
    
    def get_by_type(self, analysis_type: str) -> List[Analysis]:
        """
        Get analyses by type.
        
        Args:
            analysis_type: Type of analysis
            
        Returns:
            List of analyses of the specified type
        """
        try:
            analyses = self.get_all()
            return [a for a in analyses if a.analysis_type == analysis_type]
        except Exception as e:
            logger.error(f"Error getting analyses by type: {str(e)}")
            raise
    
    def get_by_user_and_type(self, user_id: str, analysis_type: str) -> List[Analysis]:
        """
        Get analyses by user ID and type.
        
        Args:
            user_id: ID of the user
            analysis_type: Type of analysis
            
        Returns:
            List of analyses for the user of the specified type
        """
        try:
            analyses = self.get_all()
            return [a for a in analyses if a.user_id == user_id and a.analysis_type == analysis_type]
        except Exception as e:
            logger.error(f"Error getting analyses by user and type: {str(e)}")
            raise
    
    def get_paginated(self, page: int = 1, per_page: int = 10) -> Tuple[List[Analysis], int]:
        """
        Get paginated list of analyses.
        
        Args:
            page: Page number (1-based)
            per_page: Items per page
            
        Returns:
            Tuple of (list of analyses, total pages)
        """
        try:
            analyses = self.get_all()
            
            # Sort by updated_at timestamp (newest first)
            analyses.sort(key=lambda x: x.updated_at, reverse=True)
            
            # Calculate pagination
            total_analyses = len(analyses)
            total_pages = max((total_analyses + per_page - 1) // per_page, 1)
            
            # Get requested page
            start_idx = (page - 1) * per_page
            end_idx = min(start_idx + per_page, total_analyses)
            page_analyses = analyses[start_idx:end_idx]
            
            return page_analyses, total_pages
        except Exception as e:
            logger.error(f"Error getting paginated analyses: {str(e)}")
            raise
    
    def get_by_user_paginated(self, user_id: str, page: int = 1, per_page: int = 10) -> Tuple[List[Analysis], int]:
        """
        Get paginated list of analyses for a user.
        
        Args:
            user_id: ID of the user
            page: Page number (1-based)
            per_page: Items per page
            
        Returns:
            Tuple of (list of analyses, total pages)
        """
        try:
            # Get all analyses for the user
            user_analyses = self.get_by_user(user_id)
            
            # Sort by updated_at timestamp (newest first)
            user_analyses.sort(key=lambda x: x.updated_at, reverse=True)
            
            # Calculate pagination
            total_analyses = len(user_analyses)
            total_pages = max((total_analyses + per_page - 1) // per_page, 1)
            
            # Get requested page
            start_idx = (page - 1) * per_page
            end_idx = min(start_idx + per_page, total_analyses)
            page_analyses = user_analyses[start_idx:end_idx]
            
            return page_analyses, total_pages
        except Exception as e:
            logger.error(f"Error getting paginated analyses for user: {str(e)}")
            raise
    
    def normalize_analysis_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize analysis data for storage.
        
        Args:
            data: Analysis data to normalize
            
        Returns:
            Normalized analysis data
        """
        try:
            normalized = {}
            
            # Process each field
            for field, value in data.items():
                # Handle unit_types specially
                if field == "unit_types" and value is not None:
                    if isinstance(value, list):
                        # Convert each unit type to a dictionary
                        normalized[field] = [
                            unit.dict() if hasattr(unit, "dict") else unit
                            for unit in value
                        ]
                    else:
                        # If it's a string (JSON), parse it
                        try:
                            normalized[field] = json.loads(value)
                        except (json.JSONDecodeError, TypeError):
                            normalized[field] = None
                # Handle comps_data specially
                elif field == "comps_data" and value is not None:
                    if hasattr(value, "dict"):
                        normalized[field] = value.dict()
                    else:
                        normalized[field] = value
                # Handle other fields
                else:
                    normalized[field] = value
            
            return normalized
        except Exception as e:
            logger.error(f"Error normalizing analysis data: {str(e)}")
            raise
    
    def create(self, analysis: Analysis) -> Analysis:
        """
        Create a new analysis.
        
        Args:
            analysis: Analysis to create
            
        Returns:
            The created analysis
        """
        try:
            # Normalize data if needed
            normalized_data = self.normalize_analysis_data(analysis.dict())
            
            # Create a new Analysis instance with normalized data
            normalized_analysis = Analysis.parse_obj(normalized_data)
            
            # Call the parent create method
            return super().create(normalized_analysis)
        except Exception as e:
            logger.error(f"Error creating analysis: {str(e)}")
            raise
    
    def update(self, analysis: Analysis) -> Analysis:
        """
        Update an existing analysis.
        
        Args:
            analysis: Analysis to update
            
        Returns:
            The updated analysis
            
        Raises:
            ValueError: If the analysis doesn't exist
        """
        try:
            # Check if analysis exists
            if not self.exists(analysis.id):
                raise ValueError(f"Analysis with ID {analysis.id} not found")
            
            # Normalize data if needed
            normalized_data = self.normalize_analysis_data(analysis.dict())
            
            # Create a new Analysis instance with normalized data
            normalized_analysis = Analysis.parse_obj(normalized_data)
            
            # Update the updated_at timestamp
            normalized_analysis.updated_at = datetime.now().isoformat()
            
            # Call the parent update method
            return super().update(normalized_analysis)
        except Exception as e:
            logger.error(f"Error updating analysis: {str(e)}")
            raise
