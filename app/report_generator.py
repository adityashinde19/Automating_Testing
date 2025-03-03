from pathlib import Path
import webbrowser
import logging
import time

logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self, results, start_time):
        self.results = results
        self.start_time = start_time

    def generate_report(self):
        """Generate an interactive HTML report with detailed test case information"""
        # Generate table rows with expandable details
        table_rows = []
        for t in self.results:
            row_class = 'table-success' if t['status'] == 'Passed' else 'table-danger'
            
            # Extract credentials and other details
            credentials_used = []
            for step in t.get('steps', []):
                if step.get('value'):
                    credentials_used.append(f"{step['action']}: {step['value']}")
            
            # Generate detailed steps
            steps_html = "<ol>"
            for step in t.get('steps', []):
                steps_html += f"""
                <li>
                    <strong>Action:</strong> {step['action']}<br>
                    <strong>Selector:</strong> {step['selector_type']} = {step['selector_value']}<br>
                    <strong>Value:</strong> {step.get('value', 'N/A')}
                </li>
                """
            steps_html += "</ol>"
            
            # Generate expected results
            expected_results_html = "<ul>"
            for result in t.get('expected_results', []):
                expected_results_html += f"<li>{result}</li>"
            expected_results_html += "</ul>"
            
            # Generate error details
            error_details = t.get('error', 'No errors')
            
            # Build the details section
            details = f"""
            <div class="test-details">
                <h5>Credentials Used:</h5>
                <ul>
                    {"".join(f"<li>{cred}</li>" for cred in credentials_used)}
                </ul>
                <h5>Steps Executed:</h5>
                {steps_html}
                <h5>Expected Results:</h5>
                {expected_results_html}
                <h5>Error Details:</h5>
                <pre>{error_details}</pre>
            </div>
            """
            
            # Add the row to the table
            table_rows.append(f"""
            <tr class="{row_class}">
                <td>{t['id']}</td>
                <td>{t['title']}</td>
                <td>{t['status']}</td>
                <td>{t['priority']}</td>
                <td>
                    <button class="btn btn-sm btn-info toggle-details">View Details</button>
                </td>
            </tr>
            <tr class="details-row">
                <td colspan="5">{details}</td>
            </tr>
            """)

        # Create the HTML report with interactive features
        report_html = f"""
        <html>
        <head>
            <title>Test Automation Report</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                .test-details {{
                    padding: 15px;
                    background: #f8f9fa;
                    border-radius: 5px;
                    margin: 10px 0;
                }}
                .details-row {{
                    display: none;
                }}
                .toggle-details {{
                    margin: 2px;
                }}
                .chart-container {{
                    width: 100%;
                    max-width: 800px;
                    margin: 20px auto;
                }}
                pre {{
                    background: #e9ecef;
                    padding: 10px;
                    border-radius: 5px;
                }}
            </style>
        </head>
        <body class="container mt-4">
            <h1 class="mb-4">Test Automation Report</h1>
            
            <!-- Summary Section -->
            <div class="card mb-4">
                <div class="card-body">
                    <h5 class="card-title">Summary</h5>
                    <div class="row">
                        <div class="col-md-6">
                            <p>Total Tests: {len(self.results)}</p>
                            <p>Passed: {sum(1 for t in self.results if t['status'] == 'Passed')}</p>
                            <p>Failed: {sum(1 for t in self.results if t['status'] == 'Failed')}</p>
                            <p>Execution Time: {time.time() - self.start_time:.2f} seconds</p>
                        </div>
                        <div class="col-md-6 chart-container">
                            <canvas id="summaryChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Test Results Table -->
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Title</th>
                        <th>Status</th>
                        <th>Priority</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(table_rows)}
                </tbody>
            </table>

            <!-- JavaScript for Interactivity -->
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <script>
                // Toggle test details
                document.querySelectorAll('.toggle-details').forEach(button => {{
                    button.addEventListener('click', () => {{
                        const detailsRow = button.closest('tr').nextElementSibling;
                        detailsRow.style.display = detailsRow.style.display === 'none' ? 'table-row' : 'none';
                        button.textContent = button.textContent === 'Hide Details' ? 'Hide Details' : 'View Details';
                    }});
                }});

                // Summary chart
                const ctx = document.getElementById('summaryChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'doughnut',
                    data: {{
                        labels: ['Passed', 'Failed'],
                        datasets: [{{
                            label: 'Test Results',
                            data: [
                                {sum(1 for t in self.results if t['status'] == 'Passed')},
                                {sum(1 for t in self.results if t['status'] == 'Failed')}
                            ],
                            backgroundColor: [
                                'rgba(75, 192, 192, 0.2)',
                                'rgba(255, 99, 132, 0.2)'
                            ],
                            borderColor: [
                                'rgba(75, 192, 192, 1)',
                                'rgba(255, 99, 132, 1)'
                            ],
                            borderWidth: 1
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        plugins: {{
                            legend: {{
                                position: 'top',
                            }},
                            title: {{
                                display: true,
                                text: 'Test Results Summary'
                            }}
                        }}
                    }}
                }});
            </script>
        </body>
        </html>
        """
        
        # Save the report
        report_path = Path('test_report.html')
        report_path.write_text(report_html)
        
        # Generate a clickable link
        absolute_path = report_path.absolute()
        report_url = f"file://{absolute_path}"
        
        # Open the report in the default web browser
        webbrowser.open(report_url)
        
        return report_url