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