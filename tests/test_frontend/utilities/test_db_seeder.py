"""
Test database seeding utilities.

This module provides functions to seed the test database with test persona data,
allowing for consistent test data across test runs.
"""
import json
import os
import shutil
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from tests.test_frontend.test_data.test_persona import TEST_PERSONA


def seed_test_database(app_data_path):
    """
    Seed the test database with test persona data.
    
    Args:
        app_data_path: Path to the application data directory
    """
    # Ensure data directory exists
    os.makedirs(app_data_path, exist_ok=True)
    
    # Write users data
    users_path = Path(app_data_path) / "users.json"
    with open(users_path, 'w') as f:
        json.dump({"users": [TEST_PERSONA["user"]]}, f, indent=2)
    
    # Write properties data
    properties_path = Path(app_data_path) / "properties.json"
    with open(properties_path, 'w') as f:
        json.dump({"properties": TEST_PERSONA["properties"]}, f, indent=2)
    
    # Write analyses data
    analyses_path = Path(app_data_path) / "analyses.json"
    with open(analyses_path, 'w') as f:
        json.dump({"analyses": TEST_PERSONA["analyses"]}, f, indent=2)
    
    # Write loans data
    loans_path = Path(app_data_path) / "loans.json"
    with open(loans_path, 'w') as f:
        json.dump({"loans": TEST_PERSONA["loans"]}, f, indent=2)
    
    # Write transactions data
    transactions_path = Path(app_data_path) / "transactions.json"
    with open(transactions_path, 'w') as f:
        json.dump({"transactions": TEST_PERSONA["transactions"]}, f, indent=2)


def generate_test_files(test_files_dir):
    """
    Generate test PDF files for transaction documentation.
    
    Args:
        test_files_dir: Path to the test files directory
    """
    # Ensure directories exist
    for subdir in ['receipts', 'leases', 'bank_statements', 'misc']:
        os.makedirs(os.path.join(test_files_dir, subdir), exist_ok=True)
    
    # Create receipt PDFs
    create_receipt_pdf(
        os.path.join(test_files_dir, 'receipts', 'plumbing_repair_receipt.pdf'),
        'Plumbing Repair', 750.00, '2023-03-15', 'ABC Plumbing Services'
    )
    
    create_receipt_pdf(
        os.path.join(test_files_dir, 'receipts', 'hvac_repair.pdf'),
        'HVAC Maintenance', 1200.00, '2023-05-10', 'Cool Air HVAC'
    )
    
    create_receipt_pdf(
        os.path.join(test_files_dir, 'receipts', 'contractor_invoice.pdf'),
        'Renovation Work', 15000.00, '2023-06-20', 'Quality Contractors Inc.'
    )
    
    create_receipt_pdf(
        os.path.join(test_files_dir, 'receipts', 'furniture_invoice.pdf'),
        'Room Furnishings', 9000.00, '2023-07-25', 'Modern Furniture Co.'
    )
    
    # Create lease PDFs
    create_lease_pdf(
        os.path.join(test_files_dir, 'leases', 'tenant_lease_agreement.pdf'),
        '123 Test Street', '2023-01-01', '2024-01-01', 2500.00
    )
    
    create_lease_pdf(
        os.path.join(test_files_dir, 'leases', 'option_agreement.pdf'),
        '101 Test Lane', '2023-02-01', '2025-02-01', 2200.00,
        is_option=True, option_fee=3000.00, strike_price=250000.00
    )
    
    create_lease_pdf(
        os.path.join(test_files_dir, 'leases', 'unit1_lease.pdf'),
        '456 Test Avenue, Unit 1', '2023-03-01', '2024-03-01', 2000.00
    )
    
    create_lease_pdf(
        os.path.join(test_files_dir, 'leases', 'unit2_lease.pdf'),
        '456 Test Avenue, Unit 2', '2023-03-01', '2024-03-01', 2000.00
    )
    
    # Create bank statement PDFs
    create_bank_statement_pdf(
        os.path.join(test_files_dir, 'bank_statements', 'september_bank_statement.pdf'),
        '2023-09', 'Test Property Account', 10000.00, 5000.00
    )


def create_receipt_pdf(filename, description, amount, date, vendor):
    """
    Create a receipt PDF.
    
    Args:
        filename: Path to save the PDF
        description: Description of the receipt
        amount: Amount of the receipt
        date: Date of the receipt
        vendor: Vendor name
    """
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, vendor)
    
    c.setFont("Helvetica", 12)
    c.drawString(100, 700, f"Date: {date}")
    c.drawString(100, 680, f"Description: {description}")
    c.drawString(100, 660, f"Amount: ${amount:.2f}")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, 620, "TEST RECEIPT - FOR TESTING PURPOSES ONLY")
    
    c.save()


def create_lease_pdf(filename, property_address, start_date, end_date, monthly_rent, 
                    is_option=False, option_fee=None, strike_price=None):
    """
    Create a lease PDF.
    
    Args:
        filename: Path to save the PDF
        property_address: Property address
        start_date: Lease start date
        end_date: Lease end date
        monthly_rent: Monthly rent amount
        is_option: Whether this is a lease option agreement
        option_fee: Option fee amount (for lease options)
        strike_price: Strike price (for lease options)
    """
    c = canvas.Canvas(filename, pagesize=letter)
    
    if is_option:
        title = "LEASE OPTION AGREEMENT"
    else:
        title = "RESIDENTIAL LEASE AGREEMENT"
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, title)
    
    c.setFont("Helvetica", 12)
    c.drawString(100, 700, f"Property Address: {property_address}")
    c.drawString(100, 680, f"Lease Term: {start_date} to {end_date}")
    c.drawString(100, 660, f"Monthly Rent: ${monthly_rent:.2f}")
    
    if is_option:
        c.drawString(100, 640, f"Option Fee: ${option_fee:.2f}")
        c.drawString(100, 620, f"Purchase Price: ${strike_price:.2f}")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, 580, "TEST DOCUMENT - FOR TESTING PURPOSES ONLY")
    
    c.save()


def create_bank_statement_pdf(filename, month, account_name, deposits, withdrawals):
    """
    Create a bank statement PDF.
    
    Args:
        filename: Path to save the PDF
        month: Statement month
        account_name: Account name
        deposits: Total deposits
        withdrawals: Total withdrawals
    """
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "BANK STATEMENT")
    
    c.setFont("Helvetica", 12)
    c.drawString(100, 700, f"Account: {account_name}")
    c.drawString(100, 680, f"Month: {month}")
    c.drawString(100, 660, f"Total Deposits: ${deposits:.2f}")
    c.drawString(100, 640, f"Total Withdrawals: ${withdrawals:.2f}")
    c.drawString(100, 620, f"Ending Balance: ${deposits - withdrawals:.2f}")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, 580, "TEST STATEMENT - FOR TESTING PURPOSES ONLY")
    
    c.save()


def setup_test_environment(app_data_path, test_files_dir):
    """
    Set up the test environment with test data and files.
    
    Args:
        app_data_path: Path to the application data directory
        test_files_dir: Path to the test files directory
    """
    # Seed the database
    seed_test_database(app_data_path)
    
    # Generate test files
    generate_test_files(test_files_dir)
    
    print(f"Test environment set up successfully.")
    print(f"Test database seeded at: {app_data_path}")
    print(f"Test files generated at: {test_files_dir}")


if __name__ == "__main__":
    # Default paths
    app_data_path = os.path.join(os.getcwd(), "data")
    test_files_dir = os.path.join(os.getcwd(), "tests", "test_frontend", "test_data", "test_files")
    
    # Set up the test environment
    setup_test_environment(app_data_path, test_files_dir)
