// main.js - Mobile-compatible version
(function(window) {
    const moduleManager = {
        moduleMap: {
            'main-page': 'main',
            'add-transactions-page': 'add_transactions',
            'add-properties-page': 'add_properties',
            'view-transactions-page': 'view_transactions',
            'remove-properties-page': 'remove_properties',
            'edit-transactions-page': 'edit_transactions',
            'edit-properties-page': 'edit_properties',
            'bulk-import-page': 'bulk_import',
            'dashboards-page': 'dashboards',
            'analysis-page': 'analysis',
            'view-edit-analysis-page': 'view_edit_analysis',
            'portfolio-page': null,
            'auth-page': 'auth',           
            'index-page': 'index',        
            'landing-page': 'landing', 
            'error-page': 'error',
            'welcome-page': 'welcome' 
        },

        async loadModule(moduleName) {
            if (!moduleName) {
                return null;
            }
        
            try {
                console.log(`Attempting to load module: ${moduleName}`);
                
                // First check if it's already attached to window
                const windowModule = window[`${moduleName}Module`];
                if (windowModule) {
                    console.log(`Found ${moduleName} attached to window`);
                    return windowModule;
                }
                
                // If not on window, try loading as a module
                try {
                    const module = await import(`/static/js/modules/${moduleName}.js`);
                    console.log(`Successfully loaded ${moduleName} as a module`);
                    
                    // Check if the module added itself to window during import
                    if (window[`${moduleName}Module`]) {
                        console.log(`Module attached itself to window during import`);
                        return window[`${moduleName}Module`];
                    }
                    
                    // If not on window, return the imported module
                    return module.default || module;
                } catch (moduleError) {
                    console.log(`Module import failed: ${moduleError}`);
                    throw new Error(`Module ${moduleName} not found`);
                }
            } catch (error) {
                console.error(`Error loading module ${moduleName}:`, error);
                if (moduleName !== null) {
                    window.showNotification(`Failed to load module: ${moduleName}`, 'error', 'both');
                }
                return null;
            }
        },

        async initPage() {
            try {
                const body = document.body;
                const bodyClasses = Array.from(body.classList);
                console.log('Body classes:', bodyClasses);
        
                const moduleClass = bodyClasses.find(className => this.moduleMap.hasOwnProperty(className));
                const moduleToLoad = moduleClass ? this.moduleMap[moduleClass] : null;
        
                if (moduleToLoad !== undefined) {
                    console.log(`Found matching module: ${moduleToLoad}`);
                    
                    if (moduleToLoad !== null) {
                        const module = await this.loadModule(moduleToLoad);
                        
                        if (module && typeof module.init === 'function') {
                            console.log(`Initializing module: ${moduleToLoad}`);
                            try {
                                await module.init();
                                console.log(`Module ${moduleToLoad} initialized successfully`);
                                this.handlePostInit();
                            } catch (error) {
                                console.error(`Error initializing module ${moduleToLoad}:`, error);
                                window.showNotification(`Error initializing page module: ${error.message}`, 'error', 'both');
                            }
                        } else if (moduleToLoad !== null) {
                            console.error(`Module ${moduleToLoad} not found or has no init function`);
                        }
                    }
                } else {
                    console.log('No specific module detected for this page');
                }
            } catch (error) {
                console.error('Error in initPage:', error);
                window.showNotification('Error initializing page', 'error', 'both');
            }
        },

        handlePostInit() {
            // Handle any post-initialization tasks
            this.ensureMobileResponsiveness();
        },

        ensureMobileResponsiveness() {
            // Ensure any dynamically loaded content is mobile-friendly
            this.adjustDynamicTables();
            this.adjustDynamicForms();
        },

        adjustDynamicTables() {
            // Make any dynamically loaded tables responsive
            const tables = document.querySelectorAll('table:not(.responsive-handled)');
            tables.forEach(table => {
                if (!table.parentElement.classList.contains('table-responsive')) {
                    const wrapper = document.createElement('div');
                    wrapper.classList.add('table-responsive');
                    table.parentElement.insertBefore(wrapper, table);
                    wrapper.appendChild(table);
                }
                table.classList.add('responsive-handled');
            });
        },

        adjustDynamicForms() {
            // Ensure any dynamically loaded forms are mobile-friendly
            const forms = document.querySelectorAll('form:not(.responsive-handled)');
            forms.forEach(form => {
                const inputs = form.querySelectorAll('input, select, textarea');
                inputs.forEach(input => {
                    input.classList.add('form-control');
                });
                form.classList.add('responsive-handled');
            });
        }
    };

    let initialized = false;

    async function init() {
        if (initialized) {
            return;
        }
        initialized = true;

        console.log('Main init function called');
        try {
            if (window.baseModule) {
                await moduleManager.initPage();
            } else {
                console.error('Base module not found');
                window.showNotification('Error: Base module not found', 'error', 'both');
            }
        } catch (error) {
            console.error('Error during initialization:', error);
            window.showNotification('Error initializing page', 'error', 'both');
        }
    }

    // Expose necessary functions and modules
    window.mainInit = init;
    window.moduleManager = moduleManager;

    // Initialize when the DOM is fully loaded
    document.addEventListener('DOMContentLoaded', function() {
        if (window.mainInit) {
            window.mainInit();
        }
    });

})(window);