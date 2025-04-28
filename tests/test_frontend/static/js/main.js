/**
 * main.js - Main application module for the REI Tracker
 * Handles module registration, initialization, and page-specific functionality
 */
(function(window) {
    // Create main module
    const mainModule = {
        // Store registered modules
        modules: {},
        
        // Initialize the main module
        init: function() {
            console.log('Initializing main module');
            
            // Initialize all registered modules
            this.initializeModules();
            
            // Initialize page-specific functionality
            this.initializePage();
            
            return this;
        },
        
        // Register a module
        registerModule: function(name, module) {
            if (!name || !module) {
                console.error('Cannot register module: missing name or module');
                return false;
            }
            
            // Check if module already exists
            if (this.modules[name]) {
                console.warn(`Module '${name}' is already registered. Overwriting.`);
            }
            
            // Register the module
            this.modules[name] = module;
            console.log(`Module '${name}' registered successfully`);
            
            return true;
        },
        
        // Get a registered module
        getModule: function(name) {
            if (!this.modules[name]) {
                console.warn(`Module '${name}' not found`);
                return null;
            }
            
            return this.modules[name];
        },
        
        // Initialize all registered modules
        initializeModules: function() {
            console.log('Initializing all modules');
            
            // Initialize each module
            for (const name in this.modules) {
                if (this.modules.hasOwnProperty(name)) {
                    const module = this.modules[name];
                    
                    // Check if module is page-specific
                    if (module.pageSpecific) {
                        const selector = module.pageSpecific;
                        const matchingElements = document.querySelectorAll(selector);
                        
                        // Skip if no matching elements found
                        if (matchingElements.length === 0) {
                            console.log(`Skipping module '${name}' - no matching elements for selector '${selector}'`);
                            continue;
                        }
                    }
                    
                    // Check if module has dependencies
                    if (module.dependencies && Array.isArray(module.dependencies)) {
                        let dependenciesMet = true;
                        
                        // Check each dependency
                        for (const depName of module.dependencies) {
                            const dependency = this.modules[depName];
                            
                            // Skip if dependency not found or not initialized
                            if (!dependency || !dependency.initialized) {
                                console.log(`Skipping module '${name}' - dependency '${depName}' not initialized`);
                                dependenciesMet = false;
                                break;
                            }
                        }
                        
                        // Skip if dependencies not met
                        if (!dependenciesMet) {
                            continue;
                        }
                    }
                    
                    // Check if module has init function
                    if (typeof module.init === 'function') {
                        try {
                            module.init();
                            console.log(`Module '${name}' initialized successfully`);
                        } catch (error) {
                            console.error(`Error initializing module '${name}':`, error);
                        }
                    }
                }
            }
        },
        
        // Initialize page-specific functionality
        initializePage: function() {
            console.log('Initializing page-specific functionality');
            
            // Get the current page
            const page = document.body.dataset.page;
            if (!page) {
                console.log('No page identifier found');
                return;
            }
            
            console.log(`Current page: ${page}`);
            
            // Check if there's a page-specific module
            const pageModule = this.getModule(page);
            if (pageModule) {
                // Initialize the page module
                if (typeof pageModule.init === 'function') {
                    try {
                        pageModule.init();
                        console.log(`Page module '${page}' initialized successfully`);
                    } catch (error) {
                        console.error(`Error initializing page module '${page}':`, error);
                    }
                }
            }
        },
        
        // Handle errors
        handleError: function(error, context) {
            console.error(`Error in ${context || 'application'}:`, error);
            
            // Show error notification if available
            if (typeof window.showError === 'function') {
                window.showError(`An error occurred: ${error.message}`);
            }
            
            return false;
        }
    };
    
    // Expose the main module
    window.mainModule = mainModule;
    
    // Add to REITracker namespace if it exists
    if (window.REITracker) {
        window.REITracker.main = mainModule;
        window.REITracker.modules = mainModule.modules;
    }
    
    // Flag to track if DOM is ready
    mainModule.domReady = false;
    
    // Store the DOM ready callback
    mainModule.domReadyCallback = function() {
        // Set DOM ready flag
        mainModule.domReady = true;
        
        // Register base module if available
        if (window.baseModule) {
            mainModule.registerModule('base', window.baseModule);
        }
        
        // Register notifications module if available
        if (window.notificationsModule) {
            mainModule.registerModule('notifications', window.notificationsModule);
        }
        
        // Initialize main module
        mainModule.init();
    };
    
    // Initialize when the DOM is fully loaded
    document.addEventListener('DOMContentLoaded', mainModule.domReadyCallback);
    
    // Override init to check if DOM is ready
    const originalInit = mainModule.init;
    mainModule.init = function() {
        // If DOM is not ready, just register the call for later
        if (!mainModule.domReady) {
            console.log('DOM not ready, deferring initialization');
            return this;
        }
        
        // Call the original init method
        return originalInit.apply(this, arguments);
    };
    
})(window);
