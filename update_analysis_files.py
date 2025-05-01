#!/usr/bin/env python3
"""
Script to update analysis JSON files to conform to the current schema.
This will fix issues with older format files causing errors when accessed.
"""

import os
import json
import uuid
from datetime import datetime

def update_analysis_files(analyses_dir):
    """
    Update all analysis JSON files in the given directory to conform to the current schema.
    
    Args:
        analyses_dir: Path to the directory containing analysis JSON files
    """
    print(f"Scanning directory: {analyses_dir}")
    
    # Get all JSON files in the directory
    files = [f for f in os.listdir(analyses_dir) if f.endswith('.json')]
    print(f"Found {len(files)} JSON files")
    
    # Track statistics
    updated_count = 0
    already_updated_count = 0
    error_count = 0
    
    # Process each file
    for filename in files:
        filepath = os.path.join(analyses_dir, filename)
        print(f"\nProcessing: {filename}")
        
        try:
            # Read the file
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Check if this is an old format file
            needs_update = is_old_format(data)
            
            if needs_update:
                # Update the file to the new format
                updated_data = update_to_new_format(data, filename)
                
                # Write the updated data back to the file
                with open(filepath, 'w') as f:
                    json.dump(updated_data, f, indent=2)
                
                print(f"✅ Updated: {filename}")
                updated_count += 1
            else:
                print(f"✓ Already in new format: {filename}")
                already_updated_count += 1
                
        except Exception as e:
            print(f"❌ Error processing {filename}: {str(e)}")
            error_count += 1
    
    # Print summary
    print("\n=== Summary ===")
    print(f"Total files: {len(files)}")
    print(f"Updated: {updated_count}")
    print(f"Already in new format: {already_updated_count}")
    print(f"Errors: {error_count}")

def is_old_format(data):
    """
    Check if the data is in the old format.
    
    Args:
        data: Analysis data dictionary
        
    Returns:
        True if the data is in the old format, False otherwise
    """
    # Check for key indicators of old format
    if 'property_address' in data and 'address' not in data:
        return True
    
    # Check for missing required fields
    required_fields = [
        'user_id', 'created_at', 'updated_at', 'bedrooms', 'bathrooms',
        'has_balloon_payment', 'last_modified', 'last_accessed', 'storage_version'
    ]
    
    for field in required_fields:
        if field not in data:
            return True
    
    return False

def update_to_new_format(data, filename):
    """
    Update the data to the new format.
    
    Args:
        data: Analysis data dictionary
        filename: Original filename (used to extract user_id if needed)
        
    Returns:
        Updated data dictionary
    """
    # Create a new dictionary with the updated data
    updated = {}
    
    # Preserve the ID
    updated['id'] = data.get('id')
    
    # Extract user_id from filename if not present
    if 'user_id' not in data or not data['user_id']:
        # Extract from filename (format: id_user_id.json)
        parts = filename.split('_')
        if len(parts) > 1:
            user_id = '_'.join(parts[1:]).replace('.json', '')
        else:
            user_id = "bjmar867@gmail.com"  # Default if can't extract
        updated['user_id'] = user_id
    else:
        updated['user_id'] = data['user_id']
    
    # Add timestamps if missing
    now = datetime.now().strftime("%Y-%m-%d")
    updated['created_at'] = data.get('created_at', now)
    updated['updated_at'] = data.get('updated_at', now)
    
    # Copy analysis type and name
    updated['analysis_type'] = data.get('analysis_type')
    updated['analysis_name'] = data.get('analysis_name')
    
    # Handle address field
    if 'property_address' in data and 'address' not in data:
        updated['address'] = data['property_address']
    else:
        updated['address'] = data.get('address')
    
    # Add property details
    updated['square_footage'] = data.get('square_footage', 0)
    updated['lot_size'] = data.get('lot_size', 0)
    updated['year_built'] = data.get('year_built', 0)
    updated['bedrooms'] = data.get('bedrooms', 0)
    updated['bathrooms'] = data.get('bathrooms', 0.0)
    
    # Add balloon payment fields
    updated['has_balloon_payment'] = data.get('has_balloon_payment', False)
    updated['balloon_due_date'] = data.get('balloon_due_date')
    updated['balloon_refinance_ltv_percentage'] = data.get('balloon_refinance_ltv_percentage', 0)
    updated['balloon_refinance_loan_amount'] = data.get('balloon_refinance_loan_amount', 0)
    updated['balloon_refinance_loan_interest_rate'] = data.get('balloon_refinance_loan_interest_rate', 0)
    updated['balloon_refinance_loan_term'] = data.get('balloon_refinance_loan_term', 0)
    updated['balloon_refinance_loan_down_payment'] = data.get('balloon_refinance_loan_down_payment', 0)
    updated['balloon_refinance_loan_closing_costs'] = data.get('balloon_refinance_loan_closing_costs', 0)
    
    # Add purchase details
    updated['purchase_price'] = data.get('purchase_price')
    updated['after_repair_value'] = data.get('after_repair_value')
    updated['renovation_costs'] = data.get('renovation_costs')
    updated['renovation_duration'] = data.get('renovation_duration')
    updated['cash_to_seller'] = data.get('cash_to_seller')
    updated['closing_costs'] = data.get('closing_costs')
    updated['assignment_fee'] = data.get('assignment_fee')
    updated['marketing_costs'] = data.get('marketing_costs')
    
    # Add income and expense fields
    updated['monthly_rent'] = data.get('monthly_rent')
    updated['property_taxes'] = data.get('property_taxes')
    updated['insurance'] = data.get('insurance')
    updated['hoa_coa_coop'] = data.get('hoa_coa_coop', 0)
    updated['management_fee_percentage'] = data.get('management_fee_percentage', 0.0)
    updated['capex_percentage'] = data.get('capex_percentage', 0.0)
    updated['vacancy_percentage'] = data.get('vacancy_percentage', 0.0)
    updated['repairs_percentage'] = data.get('repairs_percentage', 0.0)
    
    # Add notes
    updated['notes'] = data.get('notes', '')
    
    # Add PadSplit specific fields
    updated['utilities'] = data.get('utilities')
    updated['internet'] = data.get('internet')
    updated['cleaning'] = data.get('cleaning')
    updated['pest_control'] = data.get('pest_control')
    updated['landscaping'] = data.get('landscaping')
    updated['padsplit_platform_percentage'] = data.get('padsplit_platform_percentage')
    updated['furnishing_costs'] = data.get('furnishing_costs')
    
    # Handle initial loan fields
    updated['initial_loan_name'] = data.get('initial_loan_name', '')
    updated['initial_loan_amount'] = data.get('initial_loan_amount')
    updated['initial_loan_interest_rate'] = data.get('initial_loan_interest_rate')
    
    # Handle the interest_only field name difference
    if 'initial_loan_interest_only' in data:
        updated['initial_interest_only'] = data['initial_loan_interest_only']
    else:
        updated['initial_interest_only'] = data.get('initial_interest_only', False)
    
    updated['initial_loan_term'] = data.get('initial_loan_term')
    updated['initial_loan_down_payment'] = data.get('initial_loan_down_payment')
    updated['initial_loan_closing_costs'] = data.get('initial_loan_closing_costs')
    
    # Add refinance loan fields
    updated['refinance_loan_name'] = data.get('refinance_loan_name', '')
    updated['refinance_loan_amount'] = data.get('refinance_loan_amount')
    updated['refinance_loan_interest_rate'] = data.get('refinance_loan_interest_rate')
    updated['refinance_loan_term'] = data.get('refinance_loan_term')
    updated['refinance_loan_down_payment'] = data.get('refinance_loan_down_payment')
    updated['refinance_loan_closing_costs'] = data.get('refinance_loan_closing_costs')
    
    # Add loan interest only flags
    updated['loan1_interest_only'] = data.get('loan1_interest_only', False)
    updated['loan2_interest_only'] = data.get('loan2_interest_only', False)
    updated['loan3_interest_only'] = data.get('loan3_interest_only', False)
    
    # Add loan1 fields
    updated['loan1_loan_name'] = data.get('loan1_loan_name', '')
    updated['loan1_loan_amount'] = data.get('loan1_loan_amount')
    updated['loan1_loan_interest_rate'] = data.get('loan1_loan_interest_rate')
    updated['loan1_loan_term'] = data.get('loan1_loan_term')
    updated['loan1_loan_down_payment'] = data.get('loan1_loan_down_payment')
    updated['loan1_loan_closing_costs'] = data.get('loan1_loan_closing_costs')
    
    # Add loan2 fields
    updated['loan2_loan_name'] = data.get('loan2_loan_name', '')
    updated['loan2_loan_amount'] = data.get('loan2_loan_amount')
    updated['loan2_loan_interest_rate'] = data.get('loan2_loan_interest_rate')
    updated['loan2_loan_term'] = data.get('loan2_loan_term')
    updated['loan2_loan_down_payment'] = data.get('loan2_loan_down_payment')
    updated['loan2_loan_closing_costs'] = data.get('loan2_loan_closing_costs')
    
    # Add loan3 fields
    updated['loan3_loan_name'] = data.get('loan3_loan_name', '')
    updated['loan3_loan_amount'] = data.get('loan3_loan_amount')
    updated['loan3_loan_interest_rate'] = data.get('loan3_loan_interest_rate')
    updated['loan3_loan_term'] = data.get('loan3_loan_term')
    updated['loan3_loan_down_payment'] = data.get('loan3_loan_down_payment')
    updated['loan3_loan_closing_costs'] = data.get('loan3_loan_closing_costs')
    
    # Add Lease Option fields
    updated['option_consideration_fee'] = data.get('option_consideration_fee', 0)
    updated['option_term_months'] = data.get('option_term_months', 0)
    updated['strike_price'] = data.get('strike_price', 0)
    updated['monthly_rent_credit_percentage'] = data.get('monthly_rent_credit_percentage', 0.0)
    updated['rent_credit_cap'] = data.get('rent_credit_cap', 0)
    
    # Add Multi-Family specific fields if needed
    if data.get('analysis_type') == 'Multi-Family':
        updated['total_units'] = data.get('total_units', 0)
        updated['occupied_units'] = data.get('occupied_units', 0)
        updated['floors'] = data.get('floors', 0)
        updated['other_income'] = data.get('other_income')
        updated['total_potential_income'] = data.get('total_potential_income')
        updated['common_area_maintenance'] = data.get('common_area_maintenance', 0)
        updated['elevator_maintenance'] = data.get('elevator_maintenance')
        updated['staff_payroll'] = data.get('staff_payroll', 0)
        updated['trash_removal'] = data.get('trash_removal', 0)
        updated['common_utilities'] = data.get('common_utilities', 0)
        updated['unit_types'] = data.get('unit_types', '[]')
    
    # Add comps data if present
    if 'comps_data' in data:
        updated['comps_data'] = data['comps_data']
    
    # Add calculated metrics if present
    if 'calculated_metrics' in data:
        updated['calculated_metrics'] = data['calculated_metrics']
    
    # Add storage metadata
    updated['last_modified'] = data.get('last_modified', datetime.now().isoformat())
    updated['last_accessed'] = data.get('last_accessed', datetime.now().isoformat())
    updated['storage_version'] = data.get('storage_version', '2.0')
    
    return updated

if __name__ == '__main__':
    # Path to the analyses directory
    analyses_dir = 'data/analyses'
    
    # Update all analysis files
    update_analysis_files(analyses_dir)
