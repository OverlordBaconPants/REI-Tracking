"""
Tests for the data_formatter.js module.

This module contains tests for the data_formatter.js JavaScript module,
which provides data formatting and visualization functionality for the frontend.
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_data_formatter_module_exists(inject_scripts):
    """Test that the data formatter module exists and is properly initialized."""
    driver = inject_scripts(["base.js", "modules/data_formatter.js"])
    
    # Check that the module exists
    result = driver.execute_script("return typeof REITracker.modules !== 'undefined' && typeof REITracker.modules.dataFormatter !== 'undefined'")
    assert result is True
    
    # Check that the module has the expected methods
    methods = [
        "init", 
        "formatCurrency", 
        "formatPercentage", 
        "formatDate", 
        "formatNumber",
        "createChart",
        "createTable",
        "createDataGrid"
    ]
    
    for method in methods:
        result = driver.execute_script(f"return typeof REITracker.modules.dataFormatter.{method} === 'function'")
        assert result is True


def test_data_formatting_functions(inject_scripts):
    """Test the data formatting functions."""
    driver = inject_scripts(["base.js", "modules/data_formatter.js"])
    
    # Initialize the module
    driver.execute_script("REITracker.modules.dataFormatter.init()")
    
    # Test currency formatting
    currency_result = driver.execute_script("return REITracker.modules.dataFormatter.formatCurrency(1234.56)")
    assert "$1,234.56" in currency_result
    
    # Test negative currency formatting
    neg_currency_result = driver.execute_script("return REITracker.modules.dataFormatter.formatCurrency(-1234.56)")
    assert "-$1,234.56" in neg_currency_result or "$-1,234.56" in neg_currency_result
    
    # Test percentage formatting
    percentage_result = driver.execute_script("return REITracker.modules.dataFormatter.formatPercentage(0.1234)")
    assert "12.34%" in percentage_result
    
    # Test date formatting
    date_result = driver.execute_script("return REITracker.modules.dataFormatter.formatDate('2025-04-27')")
    assert "Apr 27, 2025" in date_result or "April 27, 2025" in date_result
    
    # Test number formatting
    number_result = driver.execute_script("return REITracker.modules.dataFormatter.formatNumber(1234.56, 1)")
    assert "1,234.6" in number_result


def test_chart_creation(inject_scripts):
    """Test chart creation functionality."""
    driver = inject_scripts(["base.js", "modules/data_formatter.js"])
    
    # Initialize the module
    driver.execute_script("REITracker.modules.dataFormatter.init()")
    
    # Create a container for the chart
    driver.execute_script("""
        var container = document.createElement('div');
        container.id = 'chart-test-container';
        document.body.appendChild(container);
        
        // Mock Chart.js
        window.Chart = function(ctx, config) {
            this.type = config.type;
            this.data = config.data;
            this.options = config.options;
            this.ctx = ctx;
            
            // Store the chart instance for testing
            window.testChart = this;
        };
    """)
    
    # Create a chart
    driver.execute_script("""
        REITracker.modules.dataFormatter.createChart('chart-test-container', 'bar', {
            labels: ['January', 'February', 'March'],
            datasets: [{
                label: 'Test Dataset',
                data: [10, 20, 30],
                backgroundColor: 'rgba(75, 192, 192, 0.2)'
            }]
        }, {
            responsive: true,
            maintainAspectRatio: false
        });
    """)
    
    # Check that the chart was created with the correct type
    chart_type = driver.execute_script("return window.testChart.type")
    assert chart_type == "bar"
    
    # Check that the chart data was set correctly
    chart_data_length = driver.execute_script("return window.testChart.data.labels.length")
    assert chart_data_length == 3
    
    # Check that the chart options were set correctly
    chart_responsive = driver.execute_script("return window.testChart.options.responsive")
    assert chart_responsive is True


def test_table_creation(inject_scripts):
    """Test table creation functionality."""
    driver = inject_scripts(["base.js", "modules/data_formatter.js"])
    
    # Initialize the module
    driver.execute_script("REITracker.modules.dataFormatter.init()")
    
    # Create a container for the table
    driver.execute_script("""
        var container = document.createElement('div');
        container.id = 'table-test-container';
        document.body.appendChild(container);
    """)
    
    # Create a table
    driver.execute_script("""
        REITracker.modules.dataFormatter.createTable('table-test-container', {
            headers: [
                { key: 'name', label: 'Name' },
                { key: 'value', label: 'Value' },
                { key: 'date', label: 'Date' }
            ],
            rows: [
                { name: 'Item 1', value: 100, date: '2025-01-01' },
                { name: 'Item 2', value: 200, date: '2025-02-01' },
                { name: 'Item 3', value: 300, date: '2025-03-01' }
            ]
        }, {
            tableClass: 'table table-striped',
            responsive: true,
            formatters: {
                value: function(value) {
                    return '$' + value.toFixed(2);
                },
                date: function(value) {
                    return new Date(value).toLocaleDateString();
                }
            }
        });
    """)
    
    # Check that the table was created
    table_exists = driver.execute_script("return document.querySelector('#table-test-container table') !== null")
    assert table_exists is True
    
    # Check that the table has the correct number of headers
    header_count = driver.execute_script("return document.querySelectorAll('#table-test-container th').length")
    assert header_count == 3
    
    # Check that the table has the correct number of rows
    row_count = driver.execute_script("return document.querySelectorAll('#table-test-container tbody tr').length")
    assert row_count == 3
    
    # Check that the formatters were applied
    first_value_cell = driver.execute_script("return document.querySelector('#table-test-container tbody tr:first-child td:nth-child(2)').textContent")
    assert "$" in first_value_cell


def test_data_grid_creation(inject_scripts):
    """Test data grid creation functionality."""
    driver = inject_scripts(["base.js", "modules/data_formatter.js"])
    
    # Initialize the module
    driver.execute_script("REITracker.modules.dataFormatter.init()")
    
    # Create a container for the grid
    driver.execute_script("""
        var container = document.createElement('div');
        container.id = 'grid-test-container';
        document.body.appendChild(container);
    """)
    
    # Create a data grid
    driver.execute_script("""
        REITracker.modules.dataFormatter.createDataGrid('grid-test-container', {
            items: [
                { name: 'Property 1', value: 100000, roi: 0.08 },
                { name: 'Property 2', value: 200000, roi: 0.10 },
                { name: 'Property 3', value: 300000, roi: 0.12 }
            ],
            layout: {
                columns: 3,
                cardClass: 'card mb-3'
            },
            cardTemplate: function(item) {
                return `
                    <div class="card-body">
                        <h5 class="card-title">${item.name}</h5>
                        <p class="card-text">Value: ${REITracker.base.formatMoney(item.value)}</p>
                        <p class="card-text">ROI: ${REITracker.base.formatPercent(item.roi)}</p>
                    </div>
                `;
            }
        });
    """)
    
    # Check that the grid was created
    grid_exists = driver.execute_script("return document.querySelector('#grid-test-container .row') !== null")
    assert grid_exists is True
    
    # Check that the grid has the correct number of cards
    card_count = driver.execute_script("return document.querySelectorAll('#grid-test-container .card').length")
    assert card_count == 3
    
    # Check that the card template was applied correctly
    first_card_title = driver.execute_script("return document.querySelector('#grid-test-container .card:first-child .card-title').textContent")
    assert "Property 1" in first_card_title
    
    # Check that the formatters were applied in the template
    first_card_value = driver.execute_script("return document.querySelector('#grid-test-container .card:first-child .card-text:first-of-type').textContent")
    assert "$100,000" in first_card_value or "$100000" in first_card_value


def test_accessibility_features(inject_scripts):
    """Test accessibility features of the data formatter."""
    driver = inject_scripts(["base.js", "modules/data_formatter.js"])
    
    # Initialize the module
    driver.execute_script("REITracker.modules.dataFormatter.init()")
    
    # Create a container for the table
    driver.execute_script("""
        var container = document.createElement('div');
        container.id = 'accessibility-test-container';
        document.body.appendChild(container);
    """)
    
    # Create a table with accessibility features
    driver.execute_script("""
        REITracker.modules.dataFormatter.createTable('accessibility-test-container', {
            headers: [
                { key: 'name', label: 'Name' },
                { key: 'value', label: 'Value' }
            ],
            rows: [
                { name: 'Item 1', value: 100 },
                { name: 'Item 2', value: 200 }
            ]
        }, {
            tableClass: 'table',
            responsive: true,
            accessibility: {
                caption: 'Test Table Caption',
                summary: 'This is a test table for accessibility features',
                labelledBy: 'table-heading'
            }
        });
        
        // Add a heading for the aria-labelledby attribute
        var heading = document.createElement('h2');
        heading.id = 'table-heading';
        heading.textContent = 'Accessibility Test Table';
        container.insertBefore(heading, container.firstChild);
    """)
    
    # Check that the table has a caption
    caption_exists = driver.execute_script("return document.querySelector('#accessibility-test-container table caption') !== null")
    assert caption_exists is True
    
    # Check that the table has the correct aria attributes
    aria_labelledby = driver.execute_script("return document.querySelector('#accessibility-test-container table').getAttribute('aria-labelledby')")
    assert aria_labelledby == "table-heading"
    
    # Check that the table has a summary
    summary = driver.execute_script("return document.querySelector('#accessibility-test-container table').getAttribute('summary')")
    assert "test table for accessibility features" in summary
