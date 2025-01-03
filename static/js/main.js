// main.js - Contains the module management system
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
            if (moduleName === null) {
                // Skip loading for pages that don't need a module
                return null;
            }

            try {
                console.log(`Attempting to load module: ${moduleName}`);
                
                // First try loading as a module
                try {
                    const module = await import(`/static/js/modules/${moduleName}.js`);
                    console.log(`Successfully loaded ${moduleName} as a module`);
                    return module.default;
                } catch (moduleError) {
                    console.log(`Module import failed, trying global object: ${moduleError}`);
                    
                    // If module import fails, check for global object
                    if (window[`${moduleName}Module`]) {
                        console.log(`Found ${moduleName} as global object`);
                        return window[`${moduleName}Module`];
                    }
                    
                    throw new Error(`Module ${moduleName} not found as import or global object`);
                }
            } catch (error) {
                console.error(`Error loading module ${moduleName}:`, error);
                // Only show notification if it's not a null module
                if (moduleName !== null) {
                    window.showNotification(`Failed to load module: ${moduleName}`, 'error','both');
                }
                return null;
            }
        },

        async initPage() {
            const body = document.body;
            const bodyClasses = Array.from(body.classList);
            console.log('Body classes:', bodyClasses);
    
            // Find the first matching module from body classes
            const moduleClass = bodyClasses.find(className => this.moduleMap.hasOwnProperty(className));
            const moduleToLoad = moduleClass ? this.moduleMap[moduleClass] : null;
    
            if (moduleToLoad !== undefined) {
                console.log(`Found matching module: ${moduleToLoad}`);
                
                // Only try loading if moduleToLoad is not null
                if (moduleToLoad !== null) {
                    // Try loading the module
                    const module = await this.loadModule(moduleToLoad);
                    
                    if (module && typeof module.init === 'function') {
                        console.log(`Initializing module: ${moduleToLoad}`);
                        try {
                            await module.init();
                            console.log(`Module ${moduleToLoad} initialized successfully`);
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
            baseModule.init();
            await moduleManager.initPage();
        } catch (error) {
            console.error('Error during initialization:', error);
            window.showNotification('Error initializing page', 'error', 'both');
        }
    }

    // Expose necessary functions and modules
    window.mainInit = init;
    window.moduleManager = moduleManager;

})(window);

// Initialize when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    if (window.mainInit) {
        window.mainInit();
    }
});