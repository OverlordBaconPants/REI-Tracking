#utils/json_handler.py

import json
import os
import logging

def read_json(file_path):
    if not os.path.exists(file_path):
        logging.warning(f"File not found: {file_path}. Returning empty list.")
        return []
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            if not content:
                logging.warning(f"Empty file: {file_path}. Returning empty list.")
                return []
            return json.loads(content)
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from {file_path}: {str(e)}. Returning empty list.")
        return []

def write_json(file_path, data):
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)
    except Exception as e:
        logging.error(f"Error writing JSON to {file_path}: {str(e)}")
        raise

def validate_analysis_file(filepath):
    """
    Validate that a file exists and contains valid JSON data.
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        tuple: (data, error_message)
        If successful, data contains the parsed JSON and error_message is None
        If unsuccessful, data is None and error_message contains the error description
    """
    try:
        if not os.path.exists(filepath):
            logging.error(f"File not found: {filepath}")
            return None, "File does not exist"
            
        with open(filepath, 'r') as f:
            content = f.read()
            if not content:
                logging.error(f"Empty file: {filepath}")
                return None, "File is empty"
                
            try:
                data = json.loads(content)
                if not isinstance(data, dict):
                    logging.error(f"Invalid data format in {filepath}: not a dictionary")
                    return None, "Invalid data format"
                    
                # Validate required fields
                required_fields = ['analysis_name', 'analysis_type']
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    logging.error(f"Missing required fields in {filepath}: {missing_fields}")
                    return None, f"Missing required fields: {', '.join(missing_fields)}"
                    
                return data, None
                
            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON from {filepath}: {str(e)}")
                return None, f"Invalid JSON format: {str(e)}"
                
    except IOError as e:
        logging.error(f"Error reading file {filepath}: {str(e)}")
        return None, f"File read error: {str(e)}"
    except Exception as e:
        logging.error(f"Unexpected error processing {filepath}: {str(e)}")
        return None, f"Unexpected error: {str(e)}"