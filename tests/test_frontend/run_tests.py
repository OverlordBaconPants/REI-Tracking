#!/usr/bin/env python3
"""
Test runner script for frontend tests.
"""
import os
import sys
import argparse
import subprocess
from datetime import datetime

def setup_directories():
    """Set up directories for test artifacts."""
    os.makedirs("screenshots", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

def main():
    """Main function to run tests."""
    parser = argparse.ArgumentParser(description="Run frontend tests")
    parser.add_argument("--test-file", help="Specific test file to run")
    parser.add_argument("--test-module", help="Specific test module to run")
    parser.add_argument("--test-name", help="Specific test name to run")
    parser.add_argument("--browser", choices=["chrome", "firefox", "safari"], 
                        default="chrome", help="Browser to run tests in")
    parser.add_argument("--headless", action="store_true", default=True, 
                        help="Run browser in headless mode")
    parser.add_argument("--no-headless", action="store_false", dest="headless", 
                        help="Run browser in visible mode")
    parser.add_argument("--html-report", action="store_true", 
                        help="Generate HTML report")
    parser.add_argument("--parallel", type=int, default=1, 
                        help="Number of parallel test processes")
    parser.add_argument("--device", choices=["desktop", "tablet", "mobile"], 
                        default="desktop", help="Device size to emulate")
    parser.add_argument("--verbose", "-v", action="store_true", 
                        help="Verbose output")
    parser.add_argument("--coverage", action="store_true", 
                        help="Generate coverage report")
    args = parser.parse_args()
    
    # Set up directories
    setup_directories()
    
    # Build pytest command
    cmd = ["pytest"]
    
    if args.verbose:
        cmd.append("-v")
    
    if args.test_file:
        cmd.append(args.test_file)
    elif args.test_module:
        cmd.append(f"tests/test_{args.test_module}/")
    
    if args.test_name:
        cmd.append(f"-k {args.test_name}")
    
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    
    if args.html_report:
        report_path = f"reports/report-{timestamp}.html"
        cmd.append(f"--html={report_path}")
        cmd.append("--self-contained-html")
    
    if args.parallel > 1:
        cmd.append(f"-n {args.parallel}")
    
    if args.coverage:
        cmd.append("--cov=.")
        cmd.append("--cov-report=html:reports/coverage")
    
    # Pass arguments to pytest via environment variables
    os.environ["BROWSER"] = args.browser
    os.environ["HEADLESS"] = str(args.headless).lower()
    os.environ["DEVICE"] = args.device
    
    # Print command
    print(f"Running: {' '.join(cmd)}")
    
    # Execute command
    result = subprocess.run(" ".join(cmd), shell=True)
    
    # Print report location if generated
    if args.html_report:
        print(f"\nHTML report generated at: {report_path}")
    
    if args.coverage:
        print("\nCoverage report generated at: reports/coverage/index.html")
    
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
