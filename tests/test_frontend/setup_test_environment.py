#!/usr/bin/env python
"""
Setup script for the test environment.

This script sets up the test environment by:
1. Creating the necessary directory structure
2. Generating test files (PDFs, etc.)
3. Seeding the test database with test persona data

Usage:
    python setup_test_environment.py [--data-path PATH] [--files-path PATH]

Options:
    --data-path PATH    Path to the application data directory
    --files-path PATH   Path to the test files directory
"""
import os
import sys
import argparse
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from tests.test_frontend.utilities.test_db_seeder import setup_test_environment


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Set up the test environment')
    parser.add_argument('--data-path', type=str, default=None,
                        help='Path to the application data directory')
    parser.add_argument('--files-path', type=str, default=None,
                        help='Path to the test files directory')
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    # Default paths
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    # Use provided paths or defaults
    app_data_path = args.data_path or os.path.join(project_root, "data")
    test_files_dir = args.files_path or os.path.join(project_root, "tests", "test_frontend", "test_data", "test_files")
    
    # Create directories for test screenshots and reports
    os.makedirs(os.path.join(project_root, "tests", "test_frontend", "screenshots"), exist_ok=True)
    os.makedirs(os.path.join(project_root, "tests", "test_frontend", "reports"), exist_ok=True)
    
    # Set up the test environment
    setup_test_environment(app_data_path, test_files_dir)
    
    print("\nTest environment setup complete!")
    print("You can now run the tests with:")
    print("  cd tests/test_frontend")
    print("  python run_tests.py")


if __name__ == "__main__":
    main()
