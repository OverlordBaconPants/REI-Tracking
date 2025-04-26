"""
Analysis repository module for the REI-Tracker application.

This module provides the AnalysisRepository class for analysis data persistence
and retrieval.
"""

from typing import List, Optional, Dict, Any
import os

from src.config import current_config
from src.models.analysis import Analysis
from src.repositories.base_repository import BaseRepository
from src.utils.file_utils import AtomicJsonFile
from src.utils.logging_utils import get_logger

# Set up logger
logger = get_logger(__name__)


class AnalysisRepository:
    """
    Analysis repository for analysis data persistence and retrieval.
    
    This class provides methods for analysis-specific operations, such as
    finding analyses by user and type.
    """
    
    def __init__(self) -> None:
        """Initialize the analysis repository."""
        self.analyses_dir = current_config.ANALYSES_DIR
        
        # Ensure directory exists
        os.makedirs(self.analyses_dir, exist_ok=True)
    
    def get_all(self) -> List[Analysis]:
        """
        Get all analyses.
        
        Returns:
            List of all analyses
        """
        try:
            analyses = []
            
            # Iterate through files in the analyses directory
            for filename in os.listdir(self.analyses_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(self.analyses_dir, filename)
                    json_file = AtomicJsonFile[Dict[str, Any]](file_path)
                    
                    try:
                        data = json_file.read()
                        analysis = Analysis.from_dict(data)
                        analyses.append(analysis)
                    except Exception as e:
                        logger.error(f"Error parsing analysis file {filename}: {str(e)}")
            
            return analyses
        except Exception as e:
            logger.error(f"Error getting all analyses: {str(e)}")
            raise
    
    def get_by_id(self, analysis_id: str) -> Optional[Analysis]:
        """
        Get an analysis by ID.
        
        Args:
            analysis_id: ID of the analysis to get
            
        Returns:
            The analysis, or None if not found
        """
        try:
            # Check all files in the analyses directory
            for filename in os.listdir(self.analyses_dir):
                if filename.startswith(f"{analysis_id}_") and filename.endswith(".json"):
                    file_path = os.path.join(self.analyses_dir, filename)
                    json_file = AtomicJsonFile[Dict[str, Any]](file_path)
                    
                    try:
                        data = json_file.read()
                        return Analysis.from_dict(data)
                    except Exception as e:
                        logger.error(f"Error parsing analysis file {filename}: {str(e)}")
            
            return None
        except Exception as e:
            logger.error(f"Error getting analysis by ID: {str(e)}")
            raise
    
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
    
    def create(self, analysis: Analysis) -> Analysis:
        """
        Create a new analysis.
        
        Args:
            analysis: Analysis to create
            
        Returns:
            The created analysis
        """
        try:
            # Generate filename
            filename = f"{analysis.id}_{analysis.user_id}.json"
            file_path = os.path.join(self.analyses_dir, filename)
            
            # Check if file already exists
            if os.path.exists(file_path):
                raise ValueError(f"Analysis with ID {analysis.id} already exists")
            
            # Write to file
            json_file = AtomicJsonFile[Dict[str, Any]](file_path)
            json_file.write(analysis.dict())
            
            return analysis
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
            # Find the file
            filename = None
            for fname in os.listdir(self.analyses_dir):
                if fname.startswith(f"{analysis.id}_") and fname.endswith(".json"):
                    filename = fname
                    break
            
            if not filename:
                raise ValueError(f"Analysis with ID {analysis.id} not found")
            
            # Update the file
            file_path = os.path.join(self.analyses_dir, filename)
            json_file = AtomicJsonFile[Dict[str, Any]](file_path)
            json_file.write(analysis.dict())
            
            return analysis
        except Exception as e:
            logger.error(f"Error updating analysis: {str(e)}")
            raise
    
    def delete(self, analysis_id: str) -> bool:
        """
        Delete an analysis by ID.
        
        Args:
            analysis_id: ID of the analysis to delete
            
        Returns:
            True if the analysis was deleted, False if not found
        """
        try:
            # Find the file
            filename = None
            for fname in os.listdir(self.analyses_dir):
                if fname.startswith(f"{analysis_id}_") and fname.endswith(".json"):
                    filename = fname
                    break
            
            if not filename:
                return False
            
            # Delete the file
            file_path = os.path.join(self.analyses_dir, filename)
            os.remove(file_path)
            
            return True
        except Exception as e:
            logger.error(f"Error deleting analysis: {str(e)}")
            raise
    
    def exists(self, analysis_id: str) -> bool:
        """
        Check if an analysis exists by ID.
        
        Args:
            analysis_id: ID of the analysis to check
            
        Returns:
            True if the analysis exists, False otherwise
        """
        try:
            for filename in os.listdir(self.analyses_dir):
                if filename.startswith(f"{analysis_id}_") and filename.endswith(".json"):
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking if analysis exists: {str(e)}")
            raise
