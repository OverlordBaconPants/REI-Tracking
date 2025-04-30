"""
Browser setup and management utilities.
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.safari.options import Options as SafariOptions

class BrowserFactory:
    """Factory for creating WebDriver instances."""
    
    @staticmethod
    def create_browser(browser_name, headless=True, device="desktop"):
        """
        Create a WebDriver instance for the specified browser.
        
        Args:
            browser_name (str): Name of the browser (chrome, firefox, safari)
            headless (bool): Whether to run in headless mode
            device (str): Device to emulate (desktop, tablet, mobile)
            
        Returns:
            WebDriver: Configured WebDriver instance
            
        Raises:
            ValueError: If an unsupported browser is specified
        """
        if browser_name.lower() == "chrome":
            return BrowserFactory._create_chrome_driver(headless, device)
        elif browser_name.lower() == "firefox":
            return BrowserFactory._create_firefox_driver(headless)
        elif browser_name.lower() == "safari":
            return BrowserFactory._create_safari_driver()
        else:
            raise ValueError(f"Unsupported browser: {browser_name}")
    
    @staticmethod
    def _create_chrome_driver(headless, device):
        """Create a Chrome WebDriver instance."""
        options = ChromeOptions()
        
        if headless:
            options.add_argument("--headless")
        
        # Common Chrome options for stability
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        # Set device emulation
        if device != "desktop":
            device_metrics = {
                "tablet": {"width": 1024, "height": 768, "pixelRatio": 2.0},
                "mobile": {"width": 375, "height": 812, "pixelRatio": 3.0}
            }
            metrics = device_metrics.get(device)
            options.add_experimental_option("mobileEmulation", {
                "deviceMetrics": metrics
            })
        
        return webdriver.Chrome(options=options)
    
    @staticmethod
    def _create_firefox_driver(headless):
        """Create a Firefox WebDriver instance."""
        options = FirefoxOptions()
        
        if headless:
            options.add_argument("--headless")
        
        return webdriver.Firefox(options=options)
    
    @staticmethod
    def _create_safari_driver():
        """Create a Safari WebDriver instance."""
        options = SafariOptions()
        return webdriver.Safari(options=options)
