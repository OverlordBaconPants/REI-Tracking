// main.js

(function(window) {
    const baseModule = {
        init: function() {
            console.log('Initializing base module');
            this.initializeToastr();
            this.initializeFlashMessages();
            this.initializeBootstrapComponents();
        },

        initializeToastr: function() {
            // Configure toastr options
            toastr.options = {
                "closeButton": true,
                "debug": false,
                "newestOnTop": true,
                "progressBar": true,
                "positionClass": "toast-bottom-right",
                "preventDuplicates": false,
                "showDuration": "300",
                "hideDuration": "1000",
                "timeOut": "5000",
                "extendedTimeOut": "1000",
                "showEasing": "swing",
                "hideEasing": "linear",
                "showMethod": "fadeIn",
                "hideMethod": "fadeOut",
                "onclick": null
            };
        },

        initializeFlashMessages: function() {
            const messagesContainer = document.getElementById('flask-messages');
            if (messagesContainer) {
                try {
                    const messagesData = messagesContainer.dataset.messages;
                    console.log('Raw messages data:', messagesData); // Debug log
                    
                    if (!messagesData || messagesData.trim() === '') {
                        console.log('No flash messages found');
                        return;
                    }
    
                    const messages = JSON.parse(messagesData);
                    console.log('Parsed messages:', messages); // Debug log
    
                    if (Array.isArray(messages)) {
                        messages.forEach(([category, message]) => {
                            // Map Flask categories to toastr types
                            let toastrType = 'info';
                            switch(category) {
                                case 'success':
                                    toastrType = 'success';
                                    break;
                                case 'error':
                                case 'danger':
                                    toastrType = 'error';
                                    break;
                                case 'warning':
                                    toastrType = 'warning';
                                    break;
                                default:
                                    toastrType = 'info';
                            }
                            
                            console.log(`Showing toastr: ${toastrType} - ${message}`); // Debug log
                            toastr[toastrType](message);
                        });
                    }
                } catch (error) {
                    console.error('Error processing flash messages:', error);
                    console.error('Messages container data:', messagesContainer.dataset.messages);
                }
            }
        },

        showNotification: function(message, category = 'info') {
            // Map Flask message categories to toastr methods
            const categoryMap = {
                'success': 'success',
                'info': 'info',
                'warning': 'warning',
                'error': 'error',
                'danger': 'error',
                'message': 'info',
                'default': 'info'
            };

            const toastrMethod = categoryMap[category] || categoryMap['default'];
            toastr[toastrMethod](message);
        },

        initializeBootstrapComponents: function() {
            // Initialize Bootstrap tooltips
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });

            // Initialize Bootstrap popovers
            const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
            popoverTriggerList.map(function (popoverTriggerEl) {
                return new bootstrap.Popover(popoverTriggerEl);
            });

            // Initialize Bootstrap accordions
            const accordionButtons = document.querySelectorAll('.accordion-button');
            accordionButtons.forEach(button => {
                button.addEventListener('click', function() {
                    const target = document.querySelector(this.getAttribute('data-bs-target'));
                    if (target) {
                        // Check if we're using Bootstrap's collapse component
                        if (bootstrap && bootstrap.Collapse) {
                            const bsCollapse = new bootstrap.Collapse(target, {
                                toggle: true
                            });
                        } else {
                            // Fallback to manual toggle
                            this.classList.toggle('collapsed');
                            target.classList.toggle('show');
                        }
                    }
                });
            });
        }
    };

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
            'analysis-page': 'analysis'
        },

        async loadModule(moduleName) {
            try {
                console.log(`Attempting to load module: ${moduleName}`);
                const module = await import(`/static/js/${moduleName}.js`);
                console.log(`Successfully loaded module: ${moduleName}`);
                return module.default;
            } catch (error) {
                console.error(`Error loading module ${moduleName}:`, error);
                baseModule.showNotification(`Failed to load module: ${moduleName}`, 'error');
                return null;
            }
        },

        async initPage() {
            const body = document.body;
            const bodyClasses = Array.from(body.classList);
            console.log('Body classes:', bodyClasses);

            // Find the first matching module from body classes
            const moduleClass = bodyClasses.find(className => this.moduleMap[className]);
            const moduleToLoad = moduleClass ? this.moduleMap[moduleClass] : null;

            if (moduleToLoad) {
                console.log(`Found matching module: ${moduleToLoad}`);
                const module = await this.loadModule(moduleToLoad);
                if (module && typeof module.init === 'function') {
                    console.log(`Initializing module: ${moduleToLoad}`);
                    try {
                        await module.init();
                        console.log(`Module ${moduleToLoad} initialized successfully`);
                    } catch (error) {
                        console.error(`Error initializing module ${moduleToLoad}:`, error);
                        baseModule.showNotification(`Error initializing page module: ${error.message}`, 'error');
                    }
                }
            } else {
                console.log('No specific module detected for this page');
            }
        }
    };

    async function init() {
        console.log('Main init function called');
        
        try {
            // Initialize base functionality
            baseModule.init();

            // Initialize page-specific module
            await moduleManager.initPage();
        } catch (error) {
            console.error('Error during initialization:', error);
            baseModule.showNotification('Error initializing page', 'error');
        }
    }

    // Expose necessary functions and modules to the global scope
    window.mainInit = init;
    window.baseModule = baseModule;
    window.showNotification = baseModule.showNotification.bind(baseModule);

})(window);

// Initialize when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    if (window.mainInit) {
        window.mainInit();
    }
});