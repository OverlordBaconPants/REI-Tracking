#!/usr/bin/env python3
"""
Frontend Test Runner

This script provides a convenient way to run frontend tests with various options.
"""

import argparse
import os
import subprocess
import sys


def main():
    """Run frontend tests with the specified options."""
    parser = argparse.ArgumentParser(description='Run frontend tests')
    parser.add_argument('--test-file', help='Specific test file to run')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--headless', action='store_true', default=True, help='Run tests in headless mode')
    parser.add_argument('--no-headless', action='store_false', dest='headless', help='Run tests with browser visible')
    parser.add_argument('--browser', choices=['chrome', 'firefox'], default='chrome', help='Browser to use for testing')
    parser.add_argument('--html-report', action='store_true', help='Generate HTML report')
    parser.add_argument('--coverage', action='store_true', help='Generate coverage report')
    
    args = parser.parse_args()
    
    # Set environment variables
    os.environ['HEADLESS'] = str(args.headless).lower()
    os.environ['PYTEST_BROWSER'] = args.browser
    
    # Build the pytest command
    cmd = ['pytest']
    
    if args.verbose:
        cmd.append('-v')
    
    if args.test_file:
        cmd.append(args.test_file)
    
    if args.html_report:
        cmd.append('--html=report.html')
        cmd.append('--self-contained-html')
    
    if args.coverage:
        cmd.append('--cov=src/static/js')
        cmd.append('--cov-report=term')
        cmd.append('--cov-report=html:coverage_html')
    
    # Print the command being run
    print(f"Running: {' '.join(cmd)}")
    
    # Run the tests
    result = subprocess.run(cmd)
    
    # Return the exit code from pytest
    return result.returncode


if __name__ == '__main__':
    sys.exit(main())
