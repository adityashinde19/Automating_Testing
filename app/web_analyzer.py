from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
import base64
import json
import re
import logging
import time
logger = logging.getLogger(__name__)

class WebAnalyzer:
    def __init__(self, url):
        self.url = url
        self.driver = webdriver.Chrome()
        self.page_title = ""
        self.dom_html = ""
        self.page_elements = {
            'inputs': 0,
            'buttons': 0,
            'links': 0,
            'forms': 0
        }
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0,
            api_key="AIzaSyBApT_35QO7nqqjVsJYLpgKmAgtSBtzNpM",
            max_retries=2
        )

    def capture_page_info(self):
        """Capture screenshot, DOM, and page elements"""
        try:
            logger.info(f"Navigating to {self.url}")
            self.driver.get(self.url)
            time.sleep(2)  # Allow page to load
            
            # Capture page information
            self.page_title = self.driver.title
            self.dom_html = self.driver.page_source
            
            # Capture element counts
            self.page_elements['inputs'] = len(self.driver.find_elements(By.TAG_NAME, 'input'))
            self.page_elements['buttons'] = len(self.driver.find_elements(By.TAG_NAME, 'button'))
            self.page_elements['links'] = len(self.driver.find_elements(By.TAG_NAME, 'a'))
            self.page_elements['forms'] = len(self.driver.find_elements(By.TAG_NAME, 'form'))
            
            # Capture screenshot
            screenshot_path = 'screenshot.png'
            self.driver.save_screenshot(screenshot_path)
            with open(screenshot_path, 'rb') as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            return base64_image, self.dom_html
        except WebDriverException as e:
            logger.error(f"Browser error: {str(e)}")
            raise

    def generate_test_cases(self, dom_html): #base64_image
        """Generate test cases using Gemini with DOM analysis"""
        try:
            text_prompt = f"""
            Analyze this webpage DOM structure to generate precise test cases with element selectors.
            Current page title: {self.page_title}
            Page URL: {self.url}
            Key elements count: {self.page_elements}
            
            DOM Structure (simplified):
            {self._simplify_dom(dom_html)}
            
            Generate test cases with:
            - Exact element selectors (ID, name, XPath, CSS selector)
            - Realistic test data
            - Validation of element states
            Format response as JSON array with structure:
            {{
                "id": "TC-001",
                "title": "Test Case Title",
                "steps": [
                    {{
                        "action": "Action description",
                        "selector_type": "id/name/xpath/css",
                        "selector_value": "element-selector",
                        "value": "input-value (if applicable)"
                    }}
                ],
                "expected_results": ["Expected Result 1"],
                "priority": "High/Medium/Low"
            }}
            """
            
            messages = [
                SystemMessage(content="You are a QA automation expert. Generate precise test cases using DOM analysis."),
                HumanMessage(content=[
                    {
                        "type": "text",
                        "text": text_prompt
                    }
                    # {
                    #     "type": "image_url",
                    #     "image_url": {
                    #         "url": f"data:image/png;base64,{base64_image}"
                    #     }
                    # }
                ])
            ]
            
            logger.info("Generating test cases with DOM analysis...")
            response = self.llm(messages)
            cleaned_response = re.sub(r'```json|```', '', response.content).strip()
            print(cleaned_response)
            return json.loads(cleaned_response)
        except Exception as e:
            logger.error(f"LLM Error: {str(e)}")
            raise

    def _simplify_dom(self, dom_html):
        """Simplify DOM for LLM processing"""
        # Remove scripts and styles for brevity
        simplified = re.sub(r'<script\b[^>]*>.*?</script>', '', dom_html, flags=re.DOTALL)
        simplified = re.sub(r'<style\b[^>]*>.*?</style>', '', simplified, flags=re.DOTALL)
        print(simplified)
        return simplified  # Limit DOM size for LLM context