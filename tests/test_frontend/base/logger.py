"""
Test logging utilities.
"""
import os
import logging
from datetime import datetime
from pathlib import Path

class TestLogger:
    """Logger for test execution."""
    
    @staticmethod
    def setup_logging(log_level=logging.INFO):
        """
        Set up logging configuration.
        
        Args:
            log_level: Logging level (default: INFO)
            
        Returns:
            Logger: Configured logger instance
        """
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Create a unique log file name with timestamp
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        log_file = log_dir / f"test_{timestamp}.log"
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        # Set selenium logging level to WARNING to reduce noise
        logging.getLogger("selenium").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        
        logger = logging.getLogger("ui_tests")
        logger.info(f"Logging initialized. Log file: {log_file}")
        
        return logger
    
    @staticmethod
    def log_test_start(logger, test_name):
        """Log the start of a test."""
        logger.info(f"{'=' * 20} TEST START: {test_name} {'=' * 20}")
    
    @staticmethod
    def log_test_end(logger, test_name, result="PASSED"):
        """Log the end of a test."""
        logger.info(f"{'=' * 20} TEST END: {test_name} - {result} {'=' * 20}")
    
    @staticmethod
    def log_step(logger, step_description):
        """Log a test step."""
        logger.info(f"STEP: {step_description}")
    
    @staticmethod
    def log_verification(logger, verification_description, result=True):
        """Log a verification step."""
        status = "PASSED" if result else "FAILED"
        logger.info(f"VERIFY: {verification_description} - {status}")
    
    @staticmethod
    def log_screenshot(logger, screenshot_path):
        """Log a screenshot capture."""
        logger.info(f"SCREENSHOT: {screenshot_path}")
    
    @staticmethod
    def log_browser_console(logger, console_logs):
        """Log browser console messages."""
        if console_logs:
            logger.info("BROWSER CONSOLE LOGS:")
            for log in console_logs:
                logger.info(f"  {log}")
        else:
            logger.info("BROWSER CONSOLE LOGS: None")

class PerformanceTracker:
    """Track UI performance metrics during tests."""
    
    def __init__(self, driver, logger):
        """
        Initialize the performance tracker.
        
        Args:
            driver: WebDriver instance
            logger: Logger instance
        """
        self.driver = driver
        self.logger = logger
    
    def measure_page_load_time(self, page_name):
        """
        Measure page load time.
        
        Args:
            page_name: Name of the page being loaded
            
        Returns:
            int: Page load time in milliseconds
        """
        # Using Navigation Timing API
        navigation_timing = self.driver.execute_script("""
            var performance = window.performance;
            var timingObj = performance.timing;
            return {
                navigationStart: timingObj.navigationStart,
                domComplete: timingObj.domComplete,
                loadEventEnd: timingObj.loadEventEnd
            };
        """)
        
        dom_load_time = navigation_timing["domComplete"] - navigation_timing["navigationStart"]
        page_load_time = navigation_timing["loadEventEnd"] - navigation_timing["navigationStart"]
        
        self.logger.info(f"Performance - {page_name} - DOM Load: {dom_load_time}ms, Full Load: {page_load_time}ms")
        return page_load_time
