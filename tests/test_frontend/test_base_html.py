"""
Tests for the base.html template.

This module contains tests for the base.html template,
which provides the foundation for all pages in the application.
"""

import pytest
from bs4 import BeautifulSoup


def test_base_html_structure(client):
    """Test that the base.html template has the correct structure."""
    # Get the base template by rendering a simple page that extends it
    response = client.get('/')
    
    # Parse the HTML
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Check that the basic HTML structure is correct
    assert soup.html is not None
    assert soup.head is not None
    assert soup.body is not None
    
    # Check for required meta tags
    meta_charset = soup.find('meta', attrs={'charset': 'utf-8'})
    assert meta_charset is not None
    
    meta_viewport = soup.find('meta', attrs={'name': 'viewport'})
    assert meta_viewport is not None
    assert 'width=device-width' in meta_viewport.get('content', '')
    
    # Check for title tag
    assert soup.title is not None


def test_base_html_css_includes(client):
    """Test that the base.html template includes the necessary CSS files."""
    # Get the base template by rendering a simple page that extends it
    response = client.get('/')
    
    # Parse the HTML
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Check for Bootstrap CSS
    bootstrap_css = soup.find('link', attrs={'href': lambda href: href and 'bootstrap' in href.lower()})
    assert bootstrap_css is not None
    
    # Check for custom CSS
    custom_css = soup.find('link', attrs={'href': lambda href: href and 'styles.css' in href.lower()})
    assert custom_css is not None


def test_base_html_js_includes(client):
    """Test that the base.html template includes the necessary JavaScript files."""
    # Get the base template by rendering a simple page that extends it
    response = client.get('/')
    
    # Parse the HTML
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Check for jQuery
    jquery_script = soup.find('script', attrs={'src': lambda src: src and 'jquery' in src.lower()})
    assert jquery_script is not None
    
    # Check for Bootstrap JS
    bootstrap_script = soup.find('script', attrs={'src': lambda src: src and 'bootstrap' in src.lower()})
    assert bootstrap_script is not None
    
    # Check for custom JS files
    base_script = soup.find('script', attrs={'src': lambda src: src and 'base.js' in src.lower()})
    assert base_script is not None
    
    main_script = soup.find('script', attrs={'src': lambda src: src and 'main.js' in src.lower()})
    assert main_script is not None
    
    notifications_script = soup.find('script', attrs={'src': lambda src: src and 'notifications.js' in src.lower()})
    assert notifications_script is not None


def test_base_html_responsive_design(client):
    """Test that the base.html template has responsive design elements."""
    # Get the base template by rendering a simple page that extends it
    response = client.get('/')
    
    # Parse the HTML
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Check for responsive container
    container = soup.find(class_=lambda c: c and 'container' in c)
    assert container is not None
    
    # Check for responsive navigation
    navbar = soup.find(class_=lambda c: c and 'navbar' in c)
    assert navbar is not None
    
    # Check for mobile navigation toggle
    navbar_toggler = soup.find(class_=lambda c: c and 'navbar-toggler' in c)
    assert navbar_toggler is not None


def test_base_html_accessibility_features(client):
    """Test that the base.html template has accessibility features."""
    # Get the base template by rendering a simple page that extends it
    response = client.get('/')
    
    # Parse the HTML
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Check for language attribute
    assert soup.html.get('lang') is not None
    
    # Check for skip navigation link
    skip_link = soup.find('a', attrs={'href': '#content'})
    assert skip_link is not None
    
    # Check for ARIA attributes in navigation
    navbar_toggler = soup.find(attrs={'aria-expanded': lambda v: v is not None})
    assert navbar_toggler is not None
    
    # Check for main content area
    main_content = soup.find('main')
    assert main_content is not None
    assert main_content.get('id') == 'content'


def test_base_html_flash_messages(client):
    """Test that the base.html template handles flash messages."""
    # Create a route that sets a flash message
    with client.application.test_request_context():
        from flask import flash, render_template_string
        
        @client.application.route('/flash-test')
        def flash_test():
            flash('Test success message', 'success')
            flash('Test error message', 'error')
            return render_template_string('{% extends "base.html" %}{% block content %}Flash Test{% endblock %}')
    
    # Get the page with flash messages
    response = client.get('/flash-test')
    
    # Parse the HTML
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Check for flash message containers
    flash_containers = soup.find_all(class_=lambda c: c and 'alert' in c)
    assert len(flash_containers) >= 2
    
    # Check for success message
    success_message = soup.find(class_=lambda c: c and 'alert-success' in c)
    assert success_message is not None
    assert 'Test success message' in success_message.text
    
    # Check for error message
    error_message = soup.find(class_=lambda c: c and 'alert-danger' in c)
    assert error_message is not None
    assert 'Test error message' in error_message.text


def test_base_html_navigation(client):
    """Test that the base.html template has proper navigation structure."""
    # Get the base template by rendering a simple page that extends it
    response = client.get('/')
    
    # Parse the HTML
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Check for navigation bar
    navbar = soup.find('nav')
    assert navbar is not None
    
    # Check for navigation links
    nav_links = navbar.find_all('a', class_=lambda c: c and 'nav-link' in c)
    assert len(nav_links) > 0
    
    # Check for active link highlighting capability
    active_link = navbar.find('a', class_=lambda c: c and 'active' in c)
    assert active_link is not None


def test_base_html_footer(client):
    """Test that the base.html template has a footer."""
    # Get the base template by rendering a simple page that extends it
    response = client.get('/')
    
    # Parse the HTML
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Check for footer
    footer = soup.find('footer')
    assert footer is not None
    
    # Check for copyright information
    assert 'copyright' in footer.text.lower() or '©' in footer.text


def test_base_html_block_structure(client):
    """Test that the base.html template has the necessary block structure."""
    # Create a route that extends base.html with custom blocks
    with client.application.test_request_context():
        from flask import render_template_string
        
        @client.application.route('/block-test')
        def block_test():
            return render_template_string('''
                {% extends "base.html" %}
                {% block title %}Custom Title{% endblock %}
                {% block head %}
                    {{ super() }}
                    <meta name="test" content="test-value">
                {% endblock %}
                {% block content %}Custom Content{% endblock %}
                {% block scripts %}
                    {{ super() }}
                    <script>console.log('Custom script');</script>
                {% endblock %}
            ''')
    
    # Get the page with custom blocks
    response = client.get('/block-test')
    
    # Parse the HTML
    soup = BeautifulSoup(response.data, 'html.parser')
    
    # Check that the title was set
    assert soup.title.text == 'Custom Title'
    
    # Check that the head block was extended
    meta_test = soup.find('meta', attrs={'name': 'test', 'content': 'test-value'})
    assert meta_test is not None
    
    # Check that the content block was replaced
    main_content = soup.find('main', id='content')
    assert 'Custom Content' in main_content.text
    
    # Check that the scripts block was extended
    custom_script = soup.find('script', string=lambda s: s and 'Custom script' in s)
    assert custom_script is not None
