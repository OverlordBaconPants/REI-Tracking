"""
Base page object with common methods.
"""
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

class BasePage:
    """Base page object with common methods for all pages."""
    
    def __init__(self, driver):
        """
        Initialize the base page object.
        
        Args:
            driver: WebDriver instance
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.url = None  # To be defined by subclasses
    
    def get_full_url(self):
        """Get the full URL for this page."""
        base_url = "http://localhost:5000"  # Default, can be overridden
        if self.url.startswith("http"):
            return self.url
        return f"{base_url}{self.url}"
    
    def navigate_to(self):
        """Navigate to this page."""
        self.driver.get(self.get_full_url())
        self.wait_for_page_load()
        return self
    
    def wait_for_page_load(self):
        """Wait for the page to load."""
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        return self
    
    def wait_and_click(self, locator):
        """Wait for an element to be clickable and click it."""
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()
        return self
    
    def wait_and_send_keys(self, locator, text):
        """Wait for an element to be visible and send keys to it."""
        element = self.wait.until(EC.visibility_of_element_located(locator))
        element.clear()
        element.send_keys(text)
        return self
    
    def wait_for_visibility(self, locator):
        """Wait for an element to be visible."""
        return self.wait.until(EC.visibility_of_element_located(locator))
    
    def wait_for_invisibility(self, locator):
        """Wait for an element to be invisible."""
        return self.wait.until(EC.invisibility_of_element_located(locator))
    
    def wait_for_presence(self, locator):
        """Wait for an element to be present in the DOM."""
        return self.wait.until(EC.presence_of_element_located(locator))
    
    def find_element(self, locator):
        """Find an element by locator."""
        try:
            return self.driver.find_element(*locator)
        except NoSuchElementException:
            return None
    
    def find_elements(self, locator):
        """Find elements by locator."""
        return self.driver.find_elements(*locator)
    
    def is_element_present(self, locator):
        """Check if an element is present."""
        try:
            self.driver.find_element(*locator)
            return True
        except NoSuchElementException:
            return False
    
    def is_element_visible(self, locator):
        """Check if an element is visible."""
        try:
            element = self.wait_for_visibility(locator)
            return element.is_displayed()
        except TimeoutException:
            return False
    
    def get_text(self, locator):
        """Get the text of an element."""
        element = self.wait_for_visibility(locator)
        return element.text
    
    def get_attribute(self, locator, attribute):
        """Get an attribute of an element."""
        element = self.wait_for_presence(locator)
        return element.get_attribute(attribute)
    
    def hover_over(self, locator):
        """Hover over an element."""
        element = self.wait_for_visibility(locator)
        ActionChains(self.driver).move_to_element(element).perform()
        return self
    
    def scroll_to(self, locator):
        """Scroll to an element."""
        element = self.wait_for_presence(locator)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        return self
    
    def scroll_to_top(self):
        """Scroll to the top of the page."""
        self.driver.execute_script("window.scrollTo(0, 0);")
        return self
    
    def scroll_to_bottom(self):
        """Scroll to the bottom of the page."""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        return self
    
    def press_key(self, key):
        """Press a key."""
        ActionChains(self.driver).send_keys(key).perform()
        return self
    
    def press_enter(self):
        """Press the Enter key."""
        return self.press_key(Keys.ENTER)
    
    def press_escape(self):
        """Press the Escape key."""
        return self.press_key(Keys.ESCAPE)
    
    def press_tab(self):
        """Press the Tab key."""
        return self.press_key(Keys.TAB)
    
    def get_page_title(self):
        """Get the page title."""
        return self.driver.title
    
    def get_current_url(self):
        """Get the current URL."""
        return self.driver.current_url
    
    def refresh_page(self):
        """Refresh the page."""
        self.driver.refresh()
        self.wait_for_page_load()
        return self
    
    def go_back(self):
        """Go back to the previous page."""
        self.driver.back()
        self.wait_for_page_load()
        return self
    
    def go_forward(self):
        """Go forward to the next page."""
        self.driver.forward()
        self.wait_for_page_load()
        return self
    
    def switch_to_alert(self):
        """Switch to an alert."""
        return self.wait.until(EC.alert_is_present())
    
    def switch_to_frame(self, locator):
        """Switch to a frame."""
        frame = self.wait_for_presence(locator)
        self.driver.switch_to.frame(frame)
        return self
    
    def switch_to_default_content(self):
        """Switch back to the default content."""
        self.driver.switch_to.default_content()
        return self
    
    def execute_script(self, script, *args):
        """Execute JavaScript."""
        return self.driver.execute_script(script, *args)
