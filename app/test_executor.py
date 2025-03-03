from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import os
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import logging

logger = logging.getLogger(__name__)

class TestExecutor:
    def __init__(self, url):
        self.driver = webdriver.Chrome()
        self.results = []
        self.start_time = time.time()
        self.url = url
        self.wait = WebDriverWait(self.driver, 10)  # Initialize the wait attribute

    def _find_element(self, selector_type, selector_value):
        """Improved element finding with explicit waits and iframe handling"""
        try:
            # Switch to iframe if necessary
            iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
            if iframes:
                self.driver.switch_to.frame(iframes[0])  # Switch to the first iframe

            if selector_type == "data-testid":
                return self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, f'[data-testid="{selector_value}"]'))
                )
            locators = {
                "id": By.ID,
                "name": By.NAME,
                "xpath": By.XPATH,
                "css": By.CSS_SELECTOR,
                "class": By.CLASS_NAME,
                "tag": By.TAG_NAME
            }
            return self.wait.until(
                EC.presence_of_element_located((locators[selector_type], selector_value)))
        except TimeoutException as e:
            logger.error(f"Element not found within timeout: {selector_type}={selector_value}")
            logger.error(f"Page source: {self.driver.page_source}")
            raise
        except NoSuchElementException as e:
            logger.error(f"Element not found: {selector_type}={selector_value}")
            raise
        except KeyError:
            raise ValueError(f"Invalid selector type: {selector_type}")
        finally:
            # Switch back to the default content
            self.driver.switch_to.default_content()

    def execute_test_case(self, test_case):
        """Enhanced test execution with better error handling"""
        logger.info(f"Executing {test_case['id']}: {test_case['title']}")
        try:
            self.driver.get(self.url)
            time.sleep(1)  # Initial page load

            for step in test_case["steps"]:
                logger.info(f"Executing step: {step['action']}")
                element = self._find_element(step["selector_type"], step["selector_value"])
                
                # Improved input handling
                if element.tag_name.lower() == "input":
                    element.clear()
                    value = step.get("value", "")
                    if element.get_attribute("type") == "password":
                        value = os.environ.get("TEST_PASSWORD", "defaultPassword123!")
                    element.send_keys(value)
                elif element.tag_name.lower() == "button":
                    element.click()
                elif element.tag_name.lower() == "a":
                    element.click()
                
                time.sleep(0.5)  # Wait for actions to complete

            # Add validation logic
            self._validate_results(test_case["expected_results"])
            
            self.results.append({
                **test_case,
                "status": "Passed",
                "error": None
            })
        except Exception as e:
            logger.error(f"Test execution failed: {str(e)}")
            self.results.append({
                **test_case,
                "status": "Failed",
                "error": str(e)
            })

    def _validate_results(self, expected_results):
        """Validate expected outcomes with robust error handling"""
        for expectation in expected_results:
            try:
                if "error message" in expectation.lower():
                    # Look for common error message selectors
                    error_selectors = [
                        '.error-message',  # Common class for error messages
                        '.alert-danger',  # Bootstrap danger alert
                        '[role="alert"]',  # ARIA role for alerts
                        'div.error',       # Generic error div
                        'p.error',         # Generic error paragraph
                        'span.error'       # Generic error span
                    ]
                    
                    error_found = False
                    for selector in error_selectors:
                        try:
                            error_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                            if error_element.is_displayed():
                                error_found = True
                                break
                        except NoSuchElementException:
                            continue
                    
                    if not error_found:
                        raise AssertionError("Expected error message not found")

                elif "success" in expectation.lower():
                    # Look for common success indicators
                    success_selectors = [
                        '.success-message',  # Common class for success messages
                        '.alert-success',    # Bootstrap success alert
                        '[role="status"]',   # ARIA role for status
                        'div.success',       # Generic success div
                        'p.success',         # Generic success paragraph
                        'span.success'       # Generic success span
                    ]
                    
                    success_found = False
                    for selector in success_selectors:
                        try:
                            success_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                            if success_element.is_displayed():
                                success_found = True
                                break
                        except NoSuchElementException:
                            continue
                    
                    if not success_found:
                        raise AssertionError("Expected success indicator not found")
                        
            except Exception as e:
                logger.error(f"Validation failed for expectation: {expectation}. Error: {str(e)}")
                raise