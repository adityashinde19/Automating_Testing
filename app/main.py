import argparse
import logging
from web_analyzer import WebAnalyzer
from test_executor import TestExecutor
from report_generator import ReportGenerator
import time

logger = logging.getLogger(__name__)

def main(url):
    try:
        # Phase 1: Analyze and Generate Test Cases
        #alright
        analyzer = WebAnalyzer(url)
        screenshot, dom_html = analyzer.capture_page_info()
        test_cases = analyzer.generate_test_cases(dom_html)
        
        # Phase 2: Execute Tests
        executor = TestExecutor(url)
        for case in test_cases:
            executor.execute_test_case(case)
        
        # Phase 3: Generate Report
        report_generator = ReportGenerator(executor.results, executor.start_time)
        report_url = report_generator.generate_report()
        logger.info(f"Report generated and opened in browser: {report_url}")
        
        # Keep browser open
        input("Press Enter to exit...")
        executor.driver.quit()
        analyzer.driver.quit()
        
    except Exception as e:
        logger.error(f"Main execution failed: {str(e)}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='DOM-based Test Automation')
    parser.add_argument('url', help='URL to test')
    args = parser.parse_args()
    main(args.url)