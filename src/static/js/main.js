/**
 * main.js - Enhanced modular JavaScript architecture
 * Provides dynamic module loading and management for the application
 */
(function(window) {
    /**
     * Module Manager - Handles loading and initialization of page-specific modules
     */
    const moduleManager = {
        // Map of page classes to module names
        moduleMap: {
            // Core pages
            'main-page': 'main',
            'index-page': 'index',
            'landing-page': 'landing',
            'error-page': 'error',
            'welcome-page': 'welcome',
            'auth-page': 'auth',
            
            // Transaction pages
            'add-transactions-page': 'add_transactions',
            'view-transactions-page': 'view_transactions',
            'edit-transactions-page': 'edit_transactions',
            'bulk-import-page': 'bulk_import',
            
            // Property pages
            'add-properties-page': 'add_properties',
            'edit-properties-page': 'edit_properties',
            'remove-properties-page': 'remove_properties',
            
            // Analysis pages
            'analysis-page': 'analysis',
            'view-edit-analysis-page': 'view_edit_analysis',
            
            // Dashboard pages
            'dashboards-page': 'dashboards',
            'portfolio-page': 'portfolio',
            'kpi-dashboard-page': 'kpi_dashboard'
        },
        
        // Registry of loaded modules
        loadedModules: {},
        
        // Dependencies between modules
        dependencies: {
            'portfolio': ['charts'],
            'kpi_dashboard': ['charts', 'data_formatter'],
            'analysis': ['form_validator', 'charts'],
            'bulk_import': ['file_handler', 'data_validator']
        },
        
        // Common modules that should be loaded for all pages
        commonModules: ['form_validator', 'data_formatter'],
        
        /**
         * Load a module by name
         * @param {string} moduleName - The name of the module to load
         * @returns {Promise<Object>} The loaded module
         */
        async loadModule(moduleName) {
            if (!moduleName) {
                return null;
            }
            
            // Return cached module if already loaded
            if (this.loadedModules[moduleName]) {
                return this.loadedModules[moduleName];
            }
        
            try {
                console.log(`Attempting to load module: ${moduleName}`);
                
                // First check if it's already attached to window
                const windowModule = window[`${moduleName}Module`];
                if (windowModule) {
                    console.log(`Found ${moduleName} attached to window`);
                    this.loadedModules[moduleName] = windowModule;
                    return windowModule;
                }
                
                // If not on window, try loading as a module
                try {
                    const module = await import(`/static/js/modules/${moduleName}.js`);
                    console.log(`Successfully loaded ${moduleName} as a module`);
                    
                    // Check if the module added itself to window during import
                    if (window[`${moduleName}Module`]) {
                        console.log(`Module attached itself to window during import`);
                        this.loadedModules[moduleName] = window[`${moduleName}Module`];
                        return window[`${moduleName}Module`];
                    }
                    
                    // If not on window, cache and return the imported module
                    const moduleToCache = module.default || module;
                    this.loadedModules[moduleName] = moduleToCache;
                    return moduleToCache;
                } catch (moduleError) {
                    console.log(`Module import failed: ${moduleError}`);
                    throw new Error(`Module ${moduleName} not found`);
                }
            } catch (error) {
                console.error(`Error loading module ${moduleName}:`, error);
                if (moduleName !== null) {
                    window.showError(`Failed to load module: ${moduleName}`);
                }
                return null;
            }
        },
        
        /**
         * Load dependencies for a module
         * @param {string} moduleName - The name of the module
         * @returns {Promise<Array>} Array of loaded dependencies
         */
        async loadDependencies(moduleName) {
            const dependencies = this.dependencies[moduleName] || [];
            const loadPromises = dependencies.map(dep => this.loadModule(dep));
            return Promise.all(loadPromises);
        },
        
        /**
         * Load common modules used across the application
         * @returns {Promise<Array>} Array of loaded common modules
         */
        async loadCommonModules() {
            const loadPromises = this.commonModules.map(name => this.loadModule(name));
            return Promise.all(loadPromises);
        },

        /**
         * Initialize the page by loading and initializing the appropriate module
         * @returns {Promise<void>}
         */
        async initPage() {
            try {
                const body = document.body;
                const bodyClasses = Array.from(body.classList);
                console.log('Body classes:', bodyClasses);
                
                // Load common modules first
                await this.loadCommonModules();
        
                // Find the appropriate module for this page
                const moduleClass = bodyClasses.find(className => this.moduleMap.hasOwnProperty(className));
                const moduleToLoad = moduleClass ? this.moduleMap[moduleClass] : null;
        
                if (moduleToLoad !== undefined) {
                    console.log(`Found matching module: ${moduleToLoad}`);
                    
                    if (moduleToLoad !== null) {
                        // Load dependencies first
                        await this.loadDependencies(moduleToLoad);
                        
                        // Then load and initialize the module
                        const module = await this.loadModule(moduleToLoad);
                        
                        if (module && typeof module.init === 'function') {
                            console.log(`Initializing module: ${moduleToLoad}`);
                            try {
                                // Pass any configuration data from the page
                                const configElement = document.getElementById('page-config');
                                let config = {};
                                
                                if (configElement && configElement.dataset.config) {
                                    try {
                                        config = JSON.parse(configElement.dataset.config);
                                    } catch (e) {
                                        console.warn('Failed to parse page config:', e);
                                    }
                                }
                                
                                // Initialize the module with config
                                await module.init(config);
                                console.log(`Module ${moduleToLoad} initialized successfully`);
                                
                                // Handle post-initialization tasks
                                this.handlePostInit(module);
                                
                                // Dispatch event that module is ready
                                window.dispatchEvent(new CustomEvent('module:ready', {
                                    detail: { moduleName: moduleToLoad }
                                }));
                            } catch (error) {
                                console.error(`Error initializing module ${moduleToLoad}:`, error);
                                window.showError(`Error initializing page module: ${error.message}`);
                            }
                        } else if (moduleToLoad !== null) {
                            console.error(`Module ${moduleToLoad} not found or has no init function`);
                        }
                    }
                } else {
                    console.log('No specific module detected for this page');
                }
                
                // Always run common initialization
                this.initializeCommonFeatures();
            } catch (error) {
                console.error('Error in initPage:', error);
                window.showError('Error initializing page');
            }
        },
        
        /**
         * Initialize common features across all pages
         */
        initializeCommonFeatures() {
            // Initialize breadcrumbs
            this.initializeBreadcrumbs();
            
            // Initialize form validation
            this.initializeFormValidation();
            
            // Initialize data visualization components
            this.initializeDataVisualization();
            
            // Initialize document viewers
            this.initializeDocumentViewers();
        },
        
        /**
         * Initialize breadcrumbs navigation
         */
        initializeBreadcrumbs() {
            const breadcrumbContainer = document.querySelector('.breadcrumb');
            if (!breadcrumbContainer) return;
            
            // Make breadcrumbs responsive
            if (window.innerWidth < 768) {
                const items = breadcrumbContainer.querySelectorAll('.breadcrumb-item');
                if (items.length > 3) {
                    // Show only first and last two items on mobile
                    for (let i = 1; i < items.length - 2; i++) {
                        items[i].style.display = 'none';
                    }
                    
                    // Add ellipsis item
                    const ellipsis = document.createElement('li');
                    ellipsis.className = 'breadcrumb-item';
                    ellipsis.textContent = '...';
                    breadcrumbContainer.insertBefore(ellipsis, items[items.length - 2]);
                }
            }
        },
        
        /**
         * Initialize form validation
         */
        initializeFormValidation() {
            const forms = document.querySelectorAll('form[data-validate="true"]');
            forms.forEach(form => {
                // Add validation attributes
                form.setAttribute('novalidate', '');
                
                // Add submit handler
                form.addEventListener('submit', this.handleFormSubmit);
                
                // Add input validation handlers
                const inputs = form.querySelectorAll('input, select, textarea');
                inputs.forEach(input => {
                    input.addEventListener('blur', this.handleInputValidation);
                    input.addEventListener('input', this.handleInputChange);
                });
            });
        },
        
        /**
         * Handle form submission with validation
         * @param {Event} e - The submit event
         */
        handleFormSubmit(e) {
            if (!this.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                
                // Show validation messages
                this.classList.add('was-validated');
                
                // Focus first invalid field
                const firstInvalid = this.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                }
                
                // Show error notification
                window.showError('Please correct the errors in the form');
            } else {
                // If form has AJAX submission attribute, handle it
                if (this.dataset.ajax === 'true') {
                    e.preventDefault();
                    moduleManager.handleAjaxFormSubmit(this);
                }
            }
        },
        
        /**
         * Handle AJAX form submission
         * @param {HTMLFormElement} form - The form element
         */
        async handleAjaxFormSubmit(form) {
            try {
                const submitButton = form.querySelector('[type="submit"]');
                if (submitButton) {
                    submitButton.disabled = true;
                    submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Submitting...';
                }
                
                const formData = new FormData(form);
                const url = form.action;
                const method = form.method.toUpperCase();
                
                // Convert FormData to JSON if needed
                let body;
                if (form.dataset.format === 'json') {
                    const data = {};
                    formData.forEach((value, key) => {
                        data[key] = value;
                    });
                    body = JSON.stringify(data);
                } else {
                    body = formData;
                }
                
                const response = await fetch(url, {
                    method,
                    body,
                    headers: form.dataset.format === 'json' ? {
                        'Content-Type': 'application/json'
                    } : {},
                    credentials: 'same-origin'
                });
                
                if (!response.ok) {
                    throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
                }
                
                const result = await response.json();
                
                if (result.success) {
                    window.showSuccess(result.message || 'Form submitted successfully');
                    
                    // Handle redirect if specified
                    if (result.redirect) {
                        window.location.href = result.redirect;
                        return;
                    }
                    
                    // Handle form reset if specified
                    if (form.dataset.resetOnSuccess === 'true') {
                        form.reset();
                        form.classList.remove('was-validated');
                    }
                    
                    // Trigger success event
                    form.dispatchEvent(new CustomEvent('form:success', {
                        detail: result
                    }));
                } else {
                    window.showError(result.message || 'Form submission failed');
                    
                    // Handle field errors
                    if (result.errors) {
                        Object.entries(result.errors).forEach(([field, error]) => {
                            const input = form.querySelector(`[name="${field}"]`);
                            if (input) {
                                input.setCustomValidity(error);
                                input.reportValidity();
                            }
                        });
                    }
                    
                    // Trigger error event
                    form.dispatchEvent(new CustomEvent('form:error', {
                        detail: result
                    }));
                }
            } catch (error) {
                console.error('Error submitting form:', error);
                window.showError('Error submitting form: ' + error.message);
                
                // Trigger error event
                form.dispatchEvent(new CustomEvent('form:error', {
                    detail: { error: error.message }
                }));
            } finally {
                // Re-enable submit button
                const submitButton = form.querySelector('[type="submit"]');
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.innerHTML = submitButton.dataset.originalText || 'Submit';
                }
            }
        },
        
        /**
         * Handle input validation on blur
         * @param {Event} e - The blur event
         */
        handleInputValidation(e) {
            const input = e.target;
            
            // Skip validation if input is empty and not required
            if (!input.value && !input.hasAttribute('required')) {
                input.setCustomValidity('');
                return;
            }
            
            // Validate based on type
            switch (input.type) {
                case 'email':
                    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    if (!emailRegex.test(input.value)) {
                        input.setCustomValidity('Please enter a valid email address');
                    } else {
                        input.setCustomValidity('');
                    }
                    break;
                    
                case 'tel':
                    const phoneRegex = /^\+?[0-9\s\-()]{10,20}$/;
                    if (!phoneRegex.test(input.value)) {
                        input.setCustomValidity('Please enter a valid phone number');
                    } else {
                        input.setCustomValidity('');
                    }
                    break;
                    
                case 'number':
                    const min = parseFloat(input.min);
                    const max = parseFloat(input.max);
                    const value = parseFloat(input.value);
                    
                    if (!isNaN(min) && value < min) {
                        input.setCustomValidity(`Value must be at least ${min}`);
                    } else if (!isNaN(max) && value > max) {
                        input.setCustomValidity(`Value must be at most ${max}`);
                    } else {
                        input.setCustomValidity('');
                    }
                    break;
                    
                default:
                    // Use browser's built-in validation
                    break;
            }
            
            // Show validation feedback
            if (input.validity.valid) {
                input.classList.remove('is-invalid');
                input.classList.add('is-valid');
            } else {
                input.classList.remove('is-valid');
                input.classList.add('is-invalid');
                
                // Create or update feedback message
                let feedback = input.nextElementSibling;
                if (!feedback || !feedback.classList.contains('invalid-feedback')) {
                    feedback = document.createElement('div');
                    feedback.className = 'invalid-feedback';
                    input.parentNode.insertBefore(feedback, input.nextSibling);
                }
                
                feedback.textContent = input.validationMessage;
            }
        },
        
        /**
         * Handle input change to clear validation messages
         * @param {Event} e - The input event
         */
        handleInputChange(e) {
            const input = e.target;
            input.setCustomValidity('');
        },
        
        /**
         * Initialize data visualization components
         */
        initializeDataVisualization() {
            const chartContainers = document.querySelectorAll('[data-chart]');
            chartContainers.forEach(container => {
                const chartType = container.dataset.chart;
                const chartData = container.dataset.chartData;
                
                if (chartType && chartData) {
                    try {
                        const data = JSON.parse(chartData);
                        this.renderChart(container, chartType, data);
                    } catch (error) {
                        console.error('Error parsing chart data:', error);
                    }
                }
            });
        },
        
        /**
         * Render a chart
         * @param {HTMLElement} container - The container element
         * @param {string} type - The chart type
         * @param {Object} data - The chart data
         */
        renderChart(container, type, data) {
            // Implementation depends on charting library
            console.log(`Rendering ${type} chart with data:`, data);
            
            // Example implementation with Chart.js
            if (window.Chart) {
                new Chart(container, {
                    type,
                    data,
                    options: {
                        responsive: true,
                        maintainAspectRatio: false
                    }
                });
            }
        },
        
        /**
         * Initialize document viewers
         */
        initializeDocumentViewers() {
            const documentViewers = document.querySelectorAll('[data-document-viewer]');
            documentViewers.forEach(viewer => {
                const documentUrl = viewer.dataset.documentUrl;
                const documentType = viewer.dataset.documentType;
                
                if (documentUrl) {
                    this.initializeDocumentViewer(viewer, documentUrl, documentType);
                }
            });
        },
        
        /**
         * Initialize a document viewer
         * @param {HTMLElement} container - The container element
         * @param {string} url - The document URL
         * @param {string} type - The document type
         */
        initializeDocumentViewer(container, url, type) {
            // Implementation depends on document type
            switch (type) {
                case 'pdf':
                    this.initializePdfViewer(container, url);
                    break;
                case 'image':
                    this.initializeImageViewer(container, url);
                    break;
                case 'text':
                    this.initializeTextViewer(container, url);
                    break;
                default:
                    console.warn(`Unsupported document type: ${type}`);
                    break;
            }
        },
        
        /**
         * Initialize a PDF viewer
         * @param {HTMLElement} container - The container element
         * @param {string} url - The PDF URL
         */
        initializePdfViewer(container, url) {
            // Create iframe for PDF
            const iframe = document.createElement('iframe');
            iframe.src = url;
            iframe.className = 'w-100 h-100 border-0';
            iframe.title = 'PDF Document';
            container.appendChild(iframe);
        },
        
        /**
         * Initialize an image viewer
         * @param {HTMLElement} container - The container element
         * @param {string} url - The image URL
         */
        initializeImageViewer(container, url) {
            // Create image with zoom capability
            const img = document.createElement('img');
            img.src = url;
            img.className = 'img-fluid';
            img.alt = 'Document Image';
            img.dataset.action = 'zoom';
            container.appendChild(img);
            
            // Add zoom functionality
            img.addEventListener('click', () => {
                const modal = document.createElement('div');
                modal.className = 'modal fade';
                modal.innerHTML = `
                    <div class="modal-dialog modal-lg modal-dialog-centered">
                        <div class="modal-content">
                            <div class="modal-body p-0">
                                <img src="${url}" class="img-fluid w-100" alt="Document Image">
                            </div>
                        </div>
                    </div>
                `;
                document.body.appendChild(modal);
                
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
                
                modal.addEventListener('hidden.bs.modal', () => {
                    modal.remove();
                });
            });
        },
        
        /**
         * Initialize a text viewer
         * @param {HTMLElement} container - The container element
         * @param {string} url - The text URL
         */
        initializeTextViewer(container, url) {
            // Fetch and display text content
            fetch(url)
                .then(response => response.text())
                .then(text => {
                    const pre = document.createElement('pre');
                    pre.className = 'p-3 bg-light border rounded';
                    pre.textContent = text;
                    container.appendChild(pre);
                })
                .catch(error => {
                    console.error('Error loading text document:', error);
                    container.innerHTML = `<div class="alert alert-danger">Error loading document: ${error.message}</div>`;
                });
        },

        /**
         * Handle post-initialization tasks
         * @param {Object} module - The initialized module
         */
        handlePostInit(module) {
            // Ensure mobile responsiveness
            this.ensureMobileResponsiveness();
            
            // Call module's postInit method if it exists
            if (module && typeof module.postInit === 'function') {
                module.postInit();
            }
            
            // Initialize any lazy-loaded components
            this.initializeLazyComponents();
        },
        
        /**
         * Initialize lazy-loaded components
         */
        initializeLazyComponents() {
            // Initialize components marked for lazy loading
            const lazyComponents = document.querySelectorAll('[data-lazy-component]');
            lazyComponents.forEach(component => {
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            const componentName = component.dataset.lazyComponent;
                            this.loadModule(componentName)
                                .then(module => {
                                    if (module && typeof module.init === 'function') {
                                        module.init(component);
                                    }
                                })
                                .catch(error => {
                                    console.error(`Error loading lazy component ${componentName}:`, error);
                                });
                            
                            // Unobserve after loading
                            observer.unobserve(component);
                        }
                    });
                });
                
                observer.observe(component);
            });
        },

        /**
         * Ensure mobile responsiveness for dynamically loaded content
         */
        ensureMobileResponsiveness() {
            // Ensure any dynamically loaded content is mobile-friendly
            this.adjustDynamicTables();
            this.adjustDynamicForms();
            this.adjustDynamicImages();
        },

        /**
         * Make dynamically loaded tables responsive
         */
        adjustDynamicTables() {
            // Make any dynamically loaded tables responsive
            const tables = document.querySelectorAll('table:not(.responsive-handled)');
            tables.forEach(table => {
                if (!table.parentElement.classList.contains('table-responsive')) {
                    const wrapper = document.createElement('div');
                    wrapper.classList.add('table-responsive');
                    table.parentNode.insertBefore(wrapper, table);
                    wrapper.appendChild(table);
                }
                table.classList.add('responsive-handled');
            });
        },

        /**
         * Make dynamically loaded forms responsive
         */
        adjustDynamicForms() {
            // Ensure any dynamically loaded forms are mobile-friendly
            const forms = document.querySelectorAll('form:not(.responsive-handled)');
            forms.forEach(form => {
                const inputs = form.querySelectorAll('input, select, textarea');
                inputs.forEach(input => {
                    input.classList.add('form-control');
                });
                
                // Make form groups responsive
                const formGroups = form.querySelectorAll('.form-group, .mb-3');
                formGroups.forEach(group => {
                    if (window.innerWidth < 768) {
                        group.classList.add('mb-4');
                    }
                });
                
                form.classList.add('responsive-handled');
            });
        },
        
        /**
         * Make dynamically loaded images responsive
         */
        adjustDynamicImages() {
            // Make images responsive
            const images = document.querySelectorAll('img:not(.responsive-handled):not(.img-fluid)');
            images.forEach(img => {
                img.classList.add('img-fluid');
                img.classList.add('responsive-handled');
            });
        }
    };

    let initialized = false;

    /**
     * Initialize the application
     * @returns {Promise<void>}
     */
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
                window.showError('Error: Base module not found');
            }
        } catch (error) {
            console.error('Error during initialization:', error);
            window.showError('Error initializing page');
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
