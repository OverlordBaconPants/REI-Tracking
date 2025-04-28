"""
Tests for the main.js module.

This module contains tests for the main.js JavaScript module,
which provides the module manager and initialization functionality for the frontend.
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_main_module_exists(inject_scripts):
    """Test that the main module exists and is properly initialized."""
    driver = inject_scripts(["base.js", "main.js"])
    
    # Check that the REITracker object exists
    result = driver.execute_script("return typeof REITracker !== 'undefined'")
    assert result is True
    
    # Check that the main module exists
    result = driver.execute_script("return typeof REITracker.main !== 'undefined'")
    assert result is True
    
    # Check that the main module has the expected methods
    methods = [
        "init", 
        "registerModule", 
        "initializeModules", 
        "getModule"
    ]
    
    for method in methods:
        result = driver.execute_script(f"return typeof REITracker.main.{method} === 'function'")
        assert result is True


def test_module_registration(inject_scripts):
    """Test module registration functionality."""
    driver = inject_scripts(["base.js", "main.js"])
    
    # Register a test module
    driver.execute_script("""
        REITracker.main.registerModule('testModule', {
            name: 'Test Module',
            init: function() {
                this.initialized = true;
                return true;
            },
            testMethod: function() {
                return 'Test method called';
            }
        });
    """)
    
    # Check that the module was registered
    module_exists = driver.execute_script("return typeof REITracker.modules !== 'undefined' && typeof REITracker.modules.testModule !== 'undefined'")
    assert module_exists is True
    
    # Check that the module has the expected properties
    module_name = driver.execute_script("return REITracker.modules.testModule.name")
    assert module_name == "Test Module"
    
    # Check that the module has the expected methods
    method_exists = driver.execute_script("return typeof REITracker.modules.testModule.testMethod === 'function'")
    assert method_exists is True


def test_module_initialization(inject_scripts):
    """Test module initialization functionality."""
    driver = inject_scripts(["base.js", "main.js"])
    
    # Register test modules with dependencies
    driver.execute_script("""
        // Module with no dependencies
        REITracker.main.registerModule('moduleA', {
            name: 'Module A',
            init: function() {
                this.initialized = true;
                return true;
            }
        });
        
        // Module that depends on moduleA
        REITracker.main.registerModule('moduleB', {
            name: 'Module B',
            dependencies: ['moduleA'],
            init: function() {
                this.initialized = true;
                this.dependencyInitialized = REITracker.modules.moduleA.initialized;
                return true;
            }
        });
        
        // Module that depends on moduleB
        REITracker.main.registerModule('moduleC', {
            name: 'Module C',
            dependencies: ['moduleB'],
            init: function() {
                this.initialized = true;
                this.dependencyInitialized = REITracker.modules.moduleB.initialized;
                return true;
            }
        });
    """)
    
    # Initialize all modules
    driver.execute_script("REITracker.main.initializeModules()")
    
    # Check that all modules were initialized
    module_a_initialized = driver.execute_script("return REITracker.modules.moduleA.initialized")
    assert module_a_initialized is True
    
    module_b_initialized = driver.execute_script("return REITracker.modules.moduleB.initialized")
    assert module_b_initialized is True
    
    module_c_initialized = driver.execute_script("return REITracker.modules.moduleC.initialized")
    assert module_c_initialized is True
    
    # Check that dependencies were initialized before dependent modules
    module_b_dependency_initialized = driver.execute_script("return REITracker.modules.moduleB.dependencyInitialized")
    assert module_b_dependency_initialized is True
    
    module_c_dependency_initialized = driver.execute_script("return REITracker.modules.moduleC.dependencyInitialized")
    assert module_c_dependency_initialized is True


def test_module_retrieval(inject_scripts):
    """Test module retrieval functionality."""
    driver = inject_scripts(["base.js", "main.js"])
    
    # Register a test module
    driver.execute_script("""
        REITracker.main.registerModule('retrievalTest', {
            name: 'Retrieval Test Module',
            testValue: 42
        });
    """)
    
    # Get the module using getModule
    module_value = driver.execute_script("""
        var module = REITracker.main.getModule('retrievalTest');
        return module ? module.testValue : null;
    """)
    
    assert module_value == 42
    
    # Test retrieving a non-existent module
    non_existent_module = driver.execute_script("""
        var module = REITracker.main.getModule('nonExistentModule');
        return module !== null;
    """)
    
    assert non_existent_module is False


def test_page_specific_initialization(inject_scripts):
    """Test page-specific initialization functionality."""
    driver = inject_scripts(["base.js", "main.js"])
    
    # Add page-specific elements
    driver.execute_script("""
        // Add a body class to simulate a specific page
        document.body.classList.add('dashboard-page');
        
        // Add a data attribute to track initialization
        document.body.setAttribute('data-initialized', 'false');
        
        // Register modules
        REITracker.main.registerModule('commonModule', {
            name: 'Common Module',
            init: function() {
                this.initialized = true;
                return true;
            }
        });
        
        REITracker.main.registerModule('dashboardModule', {
            name: 'Dashboard Module',
            pageSpecific: '.dashboard-page',
            init: function() {
                this.initialized = true;
                document.body.setAttribute('data-initialized', 'true');
                return true;
            }
        });
        
        REITracker.main.registerModule('otherPageModule', {
            name: 'Other Page Module',
            pageSpecific: '.other-page',
            init: function() {
                this.initialized = true;
                return true;
            }
        });
    """)
    
    # Initialize all modules
    driver.execute_script("REITracker.main.initializeModules()")
    
    # Check that the common module was initialized
    common_module_initialized = driver.execute_script("return REITracker.modules.commonModule.initialized")
    assert common_module_initialized is True
    
    # Check that the dashboard module was initialized (since we're on a dashboard page)
    dashboard_module_initialized = driver.execute_script("return REITracker.modules.dashboardModule.initialized")
    assert dashboard_module_initialized is True
    
    # Check that the page was marked as initialized
    page_initialized = driver.execute_script("return document.body.getAttribute('data-initialized')")
    assert page_initialized == "true"
    
    # Check that the other page module was not initialized
    other_module_initialized = driver.execute_script("return REITracker.modules.otherPageModule.initialized")
    assert other_module_initialized is not True


def test_module_error_handling(inject_scripts):
    """Test error handling during module initialization."""
    driver = inject_scripts(["base.js", "main.js"])
    
    # Register modules with errors
    driver.execute_script("""
        // Create a tracker for errors
        window.initErrors = [];
        
        // Override console.error to track errors
        window.originalConsoleError = console.error;
        console.error = function(msg) {
            window.initErrors.push(msg);
            window.originalConsoleError.apply(console, arguments);
        };
        
        // Module with an error in init
        REITracker.main.registerModule('errorModule', {
            name: 'Error Module',
            init: function() {
                throw new Error('Test initialization error');
            }
        });
        
        // Module with a dependency on the error module
        REITracker.main.registerModule('dependentModule', {
            name: 'Dependent Module',
            dependencies: ['errorModule'],
            init: function() {
                this.initialized = true;
                return true;
            }
        });
    """)
    
    # Initialize all modules
    driver.execute_script("REITracker.main.initializeModules()")
    
    # Check that an error was logged
    error_count = driver.execute_script("return window.initErrors.length")
    assert error_count > 0
    
    # Check that the dependent module was not initialized
    dependent_initialized = driver.execute_script("""
        return REITracker.modules.dependentModule && 
               REITracker.modules.dependentModule.initialized === true;
    """)
    assert dependent_initialized is not True


def test_dom_ready_initialization(inject_scripts):
    """Test DOM ready initialization functionality."""
    driver = inject_scripts(["base.js", "main.js"])
    
    # Set up DOM ready tracking
    driver.execute_script("""
        // Add a tracker for DOM ready initialization
        window.domReadyInitialized = false;
        
        // Register a module
        REITracker.main.registerModule('domReadyModule', {
            name: 'DOM Ready Module',
            init: function() {
                window.domReadyInitialized = true;
                return true;
            }
        });
    """)
    
    # Initialize the main module (should be deferred since DOM is not ready)
    driver.execute_script("REITracker.main.init()")
    
    # Check that initialization hasn't happened yet
    dom_ready_initialized = driver.execute_script("return window.domReadyInitialized")
    assert dom_ready_initialized is False
    
    # Simulate DOM ready event
    driver.execute_script("REITracker.main.domReady = true; REITracker.main.domReadyCallback()")
    
    # Check that initialization happened after DOM ready
    dom_ready_initialized = driver.execute_script("return window.domReadyInitialized")
    assert dom_ready_initialized is True
