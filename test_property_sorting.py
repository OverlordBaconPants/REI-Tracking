import json
import os
import sys
from typing import Dict, List

def read_json(file_path):
    """Read JSON data from a file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading JSON file {file_path}: {str(e)}")
        return []

def format_address(address: str, format_type: str = 'full'):
    """
    Multi-purpose address formatter that handles different format requirements.
    
    Args:
        address (str): Full property address
        format_type (str): Type of formatting needed
            
    Returns:
        Formatted address
    """
    if not address:
        return ("", "") if format_type == 'full' else ""
        
    parts = [p.strip() for p in address.split(',')]
    street_address = parts[0].strip()
    
    if format_type in ['display', 'base']:
        return street_address
        
    return (street_address, address)

def _format_property_addresses(properties: List[Dict]) -> List[Dict]:
    """Format addresses for all properties and sort them alphabetically."""
    for prop in properties:
        if prop.get('address'):
            display_address, full_address = format_address(prop['address'], 'full')
            prop['display_address'] = display_address
            prop['full_address'] = full_address
    
    # Sort properties by address in ascending alphanumeric order
    return sorted(properties, key=lambda p: p.get('address', '').lower())

def main():
    # Use a sample properties list
    properties = [
        {"address": "123 Main St, City, State", "id": "1"},
        {"address": "456 Oak Ave, City, State", "id": "2"},
        {"address": "789 Pine Rd, City, State", "id": "3"},
        {"address": "321 Elm St, City, State", "id": "4"},
        {"address": "654 Maple Dr, City, State", "id": "5"},
        {"address": "987 Cedar Ln, City, State", "id": "6"},
        {"address": "10 Apple Way, City, State", "id": "7"},
        {"address": "20 Banana Ct, City, State", "id": "8"},
    ]
    
    print("Original property order:")
    for prop in properties:
        print(f"- {prop['address']}")
    
    sorted_properties = _format_property_addresses(properties)
    
    print("\nSorted property order:")
    for prop in sorted_properties:
        print(f"- {prop['address']} (display: {prop['display_address']})")

if __name__ == "__main__":
    main()
