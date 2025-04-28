"""
Unit tests for Dash helper utility functions.

This module contains tests for the utility functions in src/utils/dash_helpers.py.
"""

import pytest
from decimal import Decimal
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd

from src.utils.dash_helpers import (
    create_responsive_chart,
    create_metric_card,
    update_chart_layouts_for_mobile,
    create_empty_response,
    generate_color_scale,
    create_mobile_button,
    format_currency,
    format_percentage,
    create_responsive_table
)

class TestCreateResponsiveChart:
    """Tests for the create_responsive_chart function."""
    
    def test_basic_chart(self):
        """Test with basic chart."""
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1, 2, 3], y=[4, 5, 6]))
        result = create_responsive_chart(fig, 'test')
        
        # Check that the result is a Div
        assert isinstance(result, html.Div)
        
        # Check that it contains a Graph component
        assert len(result.children) == 1
        assert isinstance(result.children[0], dcc.Graph)
        
        # Check that the Graph has the correct ID
        assert result.children[0].id == 'test-chart'
        
        # Check that the Graph has the correct figure
        assert result.children[0].figure == fig
        
        # Check that the Graph has the correct config
        assert result.children[0].config['displayModeBar'] is False
        assert result.children[0].config['responsive'] is True
        assert result.children[0].config['scrollZoom'] is False
        assert result.children[0].config['staticPlot'] is False
        assert result.children[0].config['doubleClick'] == 'reset'
        
        # Check that the Graph has the correct style
        assert 'height' in result.children[0].style
        assert 'minHeight' in result.children[0].style
        assert result.children[0].style['minHeight'] == '300px'
        
        # Check that the Div has the correct className
        assert result.className == 'chart-container mb-4'

class TestCreateMetricCard:
    """Tests for the create_metric_card function."""
    
    def test_basic_card(self):
        """Test with basic card."""
        result = create_metric_card('Test Title', 'test-id', 'text-primary')
        
        # Check that the result is a Card
        assert isinstance(result, dbc.Card)
        
        # Check that it contains a CardBody
        assert len(result.children) == 1
        assert isinstance(result.children[0], dbc.CardBody)
        
        # Check that the CardBody contains the title and value
        assert len(result.children[0].children) == 2
        assert isinstance(result.children[0].children[0], html.H5)
        assert isinstance(result.children[0].children[1], html.H3)
        
        # Check that the title has the correct text
        assert result.children[0].children[0].children == 'Test Title'
        
        # Check that the value has the correct ID and className
        assert result.children[0].children[1].id == 'test-id'
        assert 'text-primary' in result.children[0].children[1].className
        
        # Check that the Card has the correct className
        assert result.className == 'mb-3 shadow-sm'

class TestUpdateChartLayoutsForMobile:
    """Tests for the update_chart_layouts_for_mobile function."""
    
    def test_mobile_layout(self):
        """Test with mobile layout."""
        fig = go.Figure()
        result = update_chart_layouts_for_mobile(fig, is_mobile=True)
        
        # Check that the result is a Figure
        assert isinstance(result, go.Figure)
        
        # Check that the layout has been updated for mobile
        assert result.layout.margin.l == 10
        assert result.layout.margin.r == 10
        assert result.layout.margin.t == 30
        assert result.layout.margin.b == 30
        assert result.layout.height == 300
        assert result.layout.legend.orientation == 'h'
        assert result.layout.legend.y == -0.5
        assert result.layout.legend.x == 0.5
        assert result.layout.legend.xanchor == 'center'
        assert result.layout.legend.yanchor == 'top'
        assert result.layout.font.size == 12
        assert result.layout.hoverlabel.font.size == 14
    
    def test_desktop_layout(self):
        """Test with desktop layout."""
        fig = go.Figure()
        result = update_chart_layouts_for_mobile(fig, is_mobile=False)
        
        # Check that the result is a Figure
        assert isinstance(result, go.Figure)
        
        # Check that the layout has been updated for desktop
        assert result.layout.margin.l == 10
        assert result.layout.margin.r == 10
        assert result.layout.margin.t == 30
        assert result.layout.margin.b == 30
        assert result.layout.height == 400
        assert result.layout.legend.orientation == 'v'
        assert result.layout.legend.y == 0.5
        assert result.layout.legend.x == 1.0
        assert result.layout.legend.xanchor == 'left'
        assert result.layout.legend.yanchor == 'middle'
        assert result.layout.font.size == 14
        assert result.layout.hoverlabel.font.size == 14

class TestCreateEmptyResponse:
    """Tests for the create_empty_response function."""
    
    def test_basic_response(self):
        """Test with basic response."""
        result = create_empty_response('Test error message')
        
        # Check that the result is a tuple
        assert isinstance(result, tuple)
        
        # Check that the tuple has the correct length
        assert len(result) == 4
        
        # Check that the first element is a Div
        assert isinstance(result[0], html.Div)
        
        # Check that the second element is a Div containing a Graph
        assert isinstance(result[1], html.Div)
        assert isinstance(result[1].children[0], dcc.Graph)
        
        # Check that the third element is the error message
        assert result[2] == 'Test error message'
        
        # Check that the fourth element is a style dict
        assert isinstance(result[3], dict)
        assert result[3]['display'] == 'block'
        assert result[3]['color'] == 'red'

class TestGenerateColorScale:
    """Tests for the generate_color_scale function."""
    
    def test_empty_scale(self):
        """Test with empty scale."""
        result = generate_color_scale(0)
        assert result == []
    
    def test_single_color(self):
        """Test with single color."""
        result = generate_color_scale(1)
        assert result == ['#000080']
    
    def test_multiple_colors(self):
        """Test with multiple colors."""
        result = generate_color_scale(3)
        assert len(result) == 3
        assert result[0] == '#000080'  # Navy
        assert result[2] == '#e0ffff'  # Light cyan
        
        # Middle color should be between navy and light cyan
        assert result[1] != result[0]
        assert result[1] != result[2]
    
    def test_custom_colors(self):
        """Test with custom colors."""
        result = generate_color_scale(3, (255, 0, 0), (0, 255, 0))
        assert len(result) == 3
        assert result[0] == '#ff0000'  # Red
        assert result[2] == '#00ff00'  # Green
        
        # Middle color should be between red and green
        assert result[1] != result[0]
        assert result[1] != result[2]

class TestCreateMobileButton:
    """Tests for the create_mobile_button function."""
    
    def test_empty_link(self):
        """Test with empty link."""
        result = create_mobile_button('', 'Test', 'primary')
        assert result == ''
    
    def test_filename_link(self):
        """Test with filename link."""
        result = create_mobile_button('test.pdf', 'Test', 'primary')
        
        # Check that the result is a button
        assert '<button' in result
        assert '</button>' in result
        
        # Check that the button has the correct class
        assert 'btn-primary' in result
        
        # Check that the button has the correct text
        assert '>Test<' in result
        
        # Check that the button has the correct onclick
        assert "window.open('/transactions/artifact/test.pdf'" in result
    
    def test_artifact_link(self):
        """Test with artifact link."""
        result = create_mobile_button('/transactions/artifact/test.pdf', 'Test', 'primary')
        
        # Check that the result is a button
        assert '<button' in result
        assert '</button>' in result
        
        # Check that the button has the correct class
        assert 'btn-primary' in result
        
        # Check that the button has the correct text
        assert '>Test<' in result
        
        # Check that the button has the correct onclick
        assert "window.open('/transactions/artifact/test.pdf'" in result

class TestFormatCurrency:
    """Tests for the format_currency function."""
    
    def test_integer_value(self):
        """Test with integer value."""
        result = format_currency(1234)
        assert result == '$1,234.00'
    
    def test_float_value(self):
        """Test with float value."""
        result = format_currency(1234.56)
        assert result == '$1,234.56'
    
    def test_string_value(self):
        """Test with string value."""
        result = format_currency('1234.56')
        assert result == '$1,234.56'
    
    def test_negative_value(self):
        """Test with negative value."""
        result = format_currency(-1234.56)
        assert result == '$-1,234.56'
    
    def test_without_sign(self):
        """Test without dollar sign."""
        result = format_currency(1234.56, include_sign=False)
        assert result == '1,234.56'

class TestFormatPercentage:
    """Tests for the format_percentage function."""
    
    def test_integer_value(self):
        """Test with integer value."""
        result = format_percentage(12)
        assert result == '12.00%'
    
    def test_float_value(self):
        """Test with float value."""
        result = format_percentage(12.34)
        assert result == '12.34%'
    
    def test_string_value(self):
        """Test with string value."""
        result = format_percentage('12.34')
        assert result == '12.34%'
    
    def test_negative_value(self):
        """Test with negative value."""
        result = format_percentage(-12.34)
        assert result == '-12.34%'
    
    def test_without_sign(self):
        """Test without percent sign."""
        result = format_percentage(12.34, include_sign=False)
        assert result == '12.34'

class TestCreateResponsiveTable:
    """Tests for the create_responsive_table function."""
    
    def test_basic_table(self):
        """Test with basic table."""
        data = [{'id': 1, 'name': 'Test 1'}, {'id': 2, 'name': 'Test 2'}]
        columns = [{'id': 'id', 'name': 'ID'}, {'id': 'name', 'name': 'Name'}]
        result = create_responsive_table(data, columns)
        
        # Check that the result is a DataTable
        assert isinstance(result, dash.dash_table.DataTable)
        
        # Check that the table has the correct data and columns
        assert result.data == data
        assert result.columns == columns
        
        # Check that the table has the correct style
        assert 'overflowX' in result.style_table
        assert 'minWidth' in result.style_table
        assert result.style_table['overflowX'] == 'auto'
        assert result.style_table['minWidth'] == '100%'
        
        # Check that the table has the correct sort configuration
        assert result.sort_action == 'native'
        assert result.sort_mode == 'single'
        assert result.sort_by == [{'column_id': 'id', 'direction': 'desc'}]
    
    def test_mobile_table(self):
        """Test with mobile table."""
        data = [{'id': 1, 'name': 'Test 1'}, {'id': 2, 'name': 'Test 2'}]
        columns = [
            {'id': 'id', 'name': 'ID', 'mobile_visible': True},
            {'id': 'name', 'name': 'Name', 'mobile_visible': False}
        ]
        result = create_responsive_table(data, columns, is_mobile=True)
        
        # Check that the result is a DataTable
        assert isinstance(result, dash.dash_table.DataTable)
        
        # Check that the table has the correct data
        assert result.data == data
        
        # Check that the table has only the mobile-visible columns
        assert len(result.columns) == 1
        assert result.columns[0]['id'] == 'id'
        assert result.columns[0]['name'] == 'ID'
    
    def test_custom_sort(self):
        """Test with custom sort."""
        data = [{'id': 1, 'name': 'Test 1'}, {'id': 2, 'name': 'Test 2'}]
        columns = [{'id': 'id', 'name': 'ID'}, {'id': 'name', 'name': 'Name'}]
        sort_by = [{'column_id': 'name', 'direction': 'asc'}]
        result = create_responsive_table(data, columns, sort_by=sort_by)
        
        # Check that the table has the correct sort configuration
        assert result.sort_by == sort_by
