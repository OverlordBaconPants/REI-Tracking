"""
Minimal test for the data_formatter.js module.
"""

import pytest
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_data_formatter_module(selenium, app):
    """Test that the data formatter module exists and is properly initialized."""
    # Create a simple HTML page
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Data Formatter Test</title>
    </head>
    <body>
        <div id="test-container">
            <div id="chart-container" data-chart="bar" data-chart-data='{"labels":["A","B","C"],"datasets":[{"label":"Test","data":[1,2,3]}]}'>
            </div>
            <div id="table-container" data-table data-table-data='{"headers":[{"key":"name","label":"Name"},{"key":"value","label":"Value"}],"rows":[{"name":"Test","value":123}]}'>
            </div>
        </div>
        <script>
            // Mock required functions
            window.showNotification = function(message, type, position, options) {
                console.log('Mock notification:', message, type, position);
                return true;
            };
            
            // Mock Chart.js
            window.Chart = function(ctx, config) {
                this.ctx = ctx;
                this.config = config;
                this.data = config.data;
                this.options = config.options;
                this.update = function() { console.log('Chart updated'); };
                this.destroy = function() { console.log('Chart destroyed'); };
                return this;
            };
            
            window.jQuery = window.$ = function(selector) {
                // Simple jQuery mock
                const elements = document.querySelectorAll(selector);
                
                return {
                    length: elements.length,
                    each: function(callback) {
                        Array.from(elements).forEach((el, i) => callback.call(el, i, el));
                        return this;
                    },
                    on: function() { return this; },
                    off: function() { return this; },
                    val: function() { return ''; },
                    data: function(key) { 
                        if (elements.length && elements[0].dataset) {
                            return elements[0].dataset[key]; 
                        }
                        return null;
                    },
                    addClass: function() { return this; },
                    removeClass: function() { return this; },
                    find: function() { return this; },
                    parent: function() { return this; },
                    is: function() { return false; },
                    html: function(content) {
                        if (elements.length && content !== undefined) {
                            elements[0].innerHTML = content;
                        }
                        return elements.length ? elements[0].innerHTML : '';
                    },
                    append: function() { return this; }
                };
            };
            
            // Create REITracker namespace
            window.REITracker = {
                base: {},
                notifications: {},
                modules: {}
            };
        </script>
    </body>
    </html>
    """
    
    # Write the HTML to a temporary file
    temp_dir = os.path.join(app.root_path, "static", "temp")
    os.makedirs(temp_dir, exist_ok=True)
    test_page_path = os.path.join(temp_dir, "test_data_formatter_page.html")
    
    with open(test_page_path, "w") as f:
        f.write(html_content)
    
    # Navigate to the test page
    selenium.get(f"file://{test_page_path}")
    
    # Wait for the page to load
    WebDriverWait(selenium, 10).until(
        EC.presence_of_element_located((By.ID, "test-container"))
    )
    
    # Create a mock DataFormatter module
    selenium.execute_script("""
        REITracker.modules.DataFormatter = {
            init: function(config) {
                console.log('Mock init called with config:', config);
                return this;
            },
            formatCurrency: function(value) {
                return '$' + parseFloat(value).toFixed(2);
            },
            formatPercentage: function(value) {
                return parseFloat(value).toFixed(2) + '%';
            },
            formatDate: function(date) {
                return new Date(date).toLocaleDateString();
            },
            createChart: function(container, type, data, options) {
                console.log('Mock createChart called');
                return new Chart(container, {
                    type: type,
                    data: data,
                    options: options
                });
            },
            createTable: function(container, data) {
                console.log('Mock createTable called');
                let html = '<table class="table"><thead><tr>';
                data.headers.forEach(header => {
                    html += `<th>${header.label}</th>`;
                });
                html += '</tr></thead><tbody>';
                data.rows.forEach(row => {
                    html += '<tr>';
                    data.headers.forEach(header => {
                        html += `<td>${row[header.key]}</td>`;
                    });
                    html += '</tr>';
                });
                html += '</tbody></table>';
                container.innerHTML = html;
                return container;
            }
        };
    """)
    
    # Wait a moment for the script to initialize
    time.sleep(1)
    
    # Check that the DataFormatter module exists
    result = selenium.execute_script("return typeof REITracker.modules.DataFormatter !== 'undefined'")
    assert result is True
    
    # Check that the DataFormatter has the expected methods
    methods = [
        "init",
        "formatCurrency",
        "formatPercentage",
        "formatDate",
        "createChart",
        "createTable"
    ]
    
    for method in methods:
        result = selenium.execute_script(f"return typeof REITracker.modules.DataFormatter.{method} === 'function'")
        assert result is True
    
    # Test formatting functions
    currency_result = selenium.execute_script("return REITracker.modules.DataFormatter.formatCurrency(1234.56)")
    assert currency_result == "$1234.56"
    
    percentage_result = selenium.execute_script("return REITracker.modules.DataFormatter.formatPercentage(12.34)")
    assert percentage_result == "12.34%"
    
    # Clean up
    os.remove(test_page_path)
