/**
 * base.js - Enhanced mobile-first base module
 * Provides core functionality for the application
 */
(function(window) {
    const baseModule = {
        processedMessageIds: new Set(),
        touchEnabled: 'ontouchstart' in window,
        viewportWidth: window.innerWidth,
        viewportHeight: window.innerHeight,
        
        // Device detection sub-module
        device: {
            isMobile: false,
            isTablet: false,
            isDesktop: false,
            
            /**
             * Detect device type based on viewport size
             */
            detectDeviceType: function() {
                const width = window.innerWidth;
                this.isMobile = width < 768;
                this.isTablet = width >= 768 && width < 992;
                this.isDesktop = width >= 992;
                return {
                    isMobile: this.isMobile,
                    isTablet: this.isTablet,
                    isDesktop: this.isDesktop
                };
            }
        },
        
        // Formatting sub-module
        format: {
            /**
             * Format currency value
             * @param {number} value - The value to format
             * @param {string} currency - The currency code (default: USD)
             * @returns {string} Formatted currency string
             */
            currency: function(value, currency = 'USD') {
                return new Intl.NumberFormat('en-US', {
                    style: 'currency',
                    currency: currency,
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                }).format(value);
            },
            
            /**
             * Format percentage value
             * @param {number} value - The value to format
             * @param {number} decimals - Number of decimal places (default: 2)
             * @returns {string} Formatted percentage string
             */
            percentage: function(value, decimals = 2) {
                return new Intl.NumberFormat('en-US', {
                    style: 'percent',
                    minimumFractionDigits: decimals,
                    maximumFractionDigits: decimals
                }).format(value);
            },
            
            /**
             * Format date value
             * @param {Date} date - The date to format
             * @param {string} format - The format to use (default: MM/DD/YYYY)
             * @returns {string} Formatted date string
             */
            date: function(date, format = 'MM/DD/YYYY') {
                const d = new Date(date);
                const month = String(d.getMonth() + 1).padStart(2, '0');
                const day = String(d.getDate()).padStart(2, '0');
                const year = d.getFullYear();
                
                return `${month}/${day}/${year}`;
            },
            
            /**
             * Format phone number
             * @param {string} phone - The phone number to format
             * @returns {string} Formatted phone number
             */
            phone: function(phone) {
                const cleaned = ('' + phone).replace(/\D/g, '');
                const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
                if (match) {
                    return '(' + match[1] + ') ' + match[2] + '-' + match[3];
                }
                return phone;
            }
        },
        
        // Utilities sub-module
        utils: {
            /**
             * Set a cookie
             * @param {string} name - Cookie name
             * @param {string} value - Cookie value
             * @param {number} days - Days until expiration
             */
            setCookie: function(name, value, days) {
                let expires = '';
                if (days) {
                    const date = new Date();
                    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
                    expires = '; expires=' + date.toUTCString();
                }
                document.cookie = name + '=' + encodeURIComponent(value) + expires + '; path=/';
            },
            
            /**
             * Get a cookie value
             * @param {string} name - Cookie name
             * @returns {string|null} Cookie value or null if not found
             */
            getCookie: function(name) {
                const nameEQ = name + '=';
                const ca = document.cookie.split(';');
                for (let i = 0; i < ca.length; i++) {
                    let c = ca[i];
                    while (c.charAt(0) === ' ') c = c.substring(1, c.length);
                    if (c.indexOf(nameEQ) === 0) return decodeURIComponent(c.substring(nameEQ.length, c.length));
                }
                return null;
            },
            
            /**
             * Generate a random ID
             * @param {number} length - Length of the ID
             * @returns {string} Random ID
             */
            generateId: function(length = 8) {
                const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
                let result = '';
                for (let i = 0; i < length; i++) {
                    result += chars.charAt(Math.floor(Math.random() * chars.length));
                }
                return result;
            },
            
            /**
             * Validate email format
             * @param {string} email - Email to validate
             * @returns {boolean} Whether the email is valid
             */
            validateEmail: function(email) {
                const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
                return re.test(String(email).toLowerCase());
            },
            
            /**
             * Validate phone number format
             * @param {string} phone - Phone number to validate
             * @returns {boolean} Whether the phone number is valid
             */
            validatePhone: function(phone) {
                const re = /^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$/;
                return re.test(String(phone));
            }
        },
        
        /**
         * Initialize the base module
         */
        init: function() {
            console.log('Initializing base module');
            this.detectEnvironment();
            this.initializeLibraries();
            this.initializeFlashMessages();
            this.initializeMobileHandlers();
            this.initializeAccessibility();
            
            // Add history state handler
            window.addEventListener('popstate', this.handleHistoryChange.bind(this));
            
            // Add resize handler for mobile/desktop transitions
            window.addEventListener('resize', this.handleResize.bind(this));
            
            // Add visibility change handler for performance optimization
            document.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
        },
        
        /**
         * Detect environment capabilities
         */
        detectEnvironment: function() {
            // Detect touch capability
            document.documentElement.classList.toggle('touch-device', this.touchEnabled);
            document.documentElement.classList.toggle('no-touch', !this.touchEnabled);
            
            // Detect reduced motion preference
            const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
            document.documentElement.classList.toggle('reduced-motion', prefersReducedMotion);
            
            // Detect high contrast mode
            const highContrast = window.matchMedia('(forced-colors: active)').matches;
            document.documentElement.classList.toggle('high-contrast', highContrast);
            
            // Log environment details
            console.log('Environment detected:', {
                touchEnabled: this.touchEnabled,
                viewportWidth: this.viewportWidth,
                viewportHeight: this.viewportHeight,
                prefersReducedMotion,
                highContrast
            });
        },

        /**
         * Initialize required libraries and dependencies
         */
        initializeLibraries: function() {
            // Check for required libraries
            const requiredLibraries = {
                'jQuery': typeof jQuery !== 'undefined',
                'bootstrap': typeof bootstrap !== 'undefined',
                'toastr': typeof toastr !== 'undefined',
                'lodash': typeof _ !== 'undefined'
            };
        
            // Log library status
            console.log('Checking required libraries:', requiredLibraries);
        
            // Check if any required libraries are missing
            const missingLibraries = Object.entries(requiredLibraries)
                .filter(([, loaded]) => !loaded)
                .map(([name]) => name);
        
            if (missingLibraries.length > 0) {
                console.error('Required libraries not loaded:', missingLibraries.join(', '));
                window.showNotification(`Required libraries missing: ${missingLibraries.join(', ')}`, 'error', 'both');
                return false;
            }
        
            // Initialize Bootstrap components if available
            if (requiredLibraries.bootstrap) {
                this.initializeBootstrapComponents();
            }
        
            // Initialize Toastr if available
            if (requiredLibraries.toastr) {
                this.initializeToastr();
            }
            
            // Initialize Lodash if available
            if (requiredLibraries.lodash) {
                // Configure Lodash settings if needed
                _.templateSettings.interpolate = /{{([\s\S]+?)}}/g;
            }
        
            return true;
        },
        
        /**
         * Helper method to safely check if a library exists
         * @param {string} libraryName - The name of the library to check
         * @returns {boolean} Whether the library is loaded
         */
        isLibraryLoaded: function(libraryName) {
            try {
                return eval(`typeof ${libraryName} !== 'undefined'`);
            } catch (e) {
                return false;
            }
        },

        /**
         * Initialize mobile-specific handlers and optimizations
         */
        initializeMobileHandlers: function() {
            // Handle sidebar link clicks on mobile
            const sidebarMenu = document.getElementById('sidebarMenu');
            if (sidebarMenu) {
                const sidebarLinks = sidebarMenu.querySelectorAll('a');
                sidebarLinks.forEach(link => {
                    link.addEventListener('click', () => {
                        if (window.innerWidth < 768) {
                            const bsCollapse = bootstrap.Collapse.getInstance(sidebarMenu);
                            if (bsCollapse) {
                                bsCollapse.hide();
                            }
                        }
                    });
                });
            }
            
            // Handle clicks outside sidebar to close it on mobile
            document.addEventListener('click', (event) => {
                if (window.innerWidth < 768) {
                    const sidebar = document.getElementById('sidebarMenu');
                    const toggler = document.querySelector('.navbar-toggler');
                    if (sidebar && toggler) {
                        const isClickInside = sidebar.contains(event.target) || toggler.contains(event.target);
                        if (!isClickInside && sidebar.classList.contains('show')) {
                            const bsCollapse = bootstrap.Collapse.getInstance(sidebar);
                            if (bsCollapse) {
                                bsCollapse.hide();
                            }
                        }
                    }
                }
            });
            
            // Optimize touch interactions
            this.optimizeTouchInteractions();
            
            // Handle mobile keyboard
            this.handleMobileKeyboard();
            
            // Make tables responsive
            this.makeTablesResponsive();
        },
        
        /**
         * Optimize touch interactions for mobile devices
         */
        optimizeTouchInteractions: function() {
            if (!this.touchEnabled) return;
            
            // Add touch feedback to interactive elements
            const interactiveElements = document.querySelectorAll(
                '.btn, .nav-link, .list-group-item, .accordion-button'
            );
            
            interactiveElements.forEach(element => {
                // Remove existing listeners to prevent duplicates
                element.removeEventListener('touchstart', this.touchFeedbackStart);
                element.removeEventListener('touchend', this.touchFeedbackEnd);
                
                // Add touch feedback
                element.addEventListener('touchstart', this.touchFeedbackStart);
                element.addEventListener('touchend', this.touchFeedbackEnd);
                element.addEventListener('touchcancel', this.touchFeedbackEnd);
            });
        },
        
        /**
         * Touch feedback start handler
         * @param {Event} e - The touch event
         */
        touchFeedbackStart: function(e) {
            this.classList.add('touch-active');
        },
        
        /**
         * Touch feedback end handler
         * @param {Event} e - The touch event
         */
        touchFeedbackEnd: function(e) {
            this.classList.remove('touch-active');
        },
        
        /**
         * Handle mobile keyboard appearance
         */
        handleMobileKeyboard: function() {
            if (!this.touchEnabled) return;
            
            const originalHeight = window.innerHeight;
            
            window.addEventListener('resize', _.debounce(() => {
                // If height significantly decreased, keyboard is likely visible
                if (window.innerHeight < originalHeight * 0.75) {
                    document.body.classList.add('keyboard-visible');
                } else {
                    document.body.classList.remove('keyboard-visible');
                }
            }, 100));
            
            // Improve input fields for mobile
            const inputs = document.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                // Ensure proper input types for mobile
                if (input.type === 'number') {
                    input.addEventListener('focus', function() {
                        if (window.innerWidth < 768) {
                            // Better numeric keyboard on mobile
                            this.setAttribute('inputmode', 'decimal');
                        }
                    });
                }
                
                // Add touch-friendly padding
                if (this.touchEnabled && !input.classList.contains('touch-optimized')) {
                    input.classList.add('touch-optimized');
                }
            });
        },
        
        /**
         * Make tables responsive
         */
        makeTablesResponsive: function() {
            const tables = document.querySelectorAll('table:not(.responsive-handled)');
            tables.forEach(table => {
                if (!table.parentElement.classList.contains('table-responsive')) {
                    const wrapper = document.createElement('div');
                    wrapper.className = 'table-responsive';
                    table.parentNode.insertBefore(wrapper, table);
                    wrapper.appendChild(table);
                }
                table.classList.add('responsive-handled');
            });
        },

        /**
         * Handle window resize events
         */
        handleResize: function() {
            // Update viewport dimensions
            this.viewportWidth = window.innerWidth;
            this.viewportHeight = window.innerHeight;
            
            // Handle any necessary adjustments when switching between mobile/desktop
            const sidebar = document.getElementById('sidebarMenu');
            if (sidebar && window.innerWidth >= 768) {
                sidebar.classList.add('show');
            }
            
            // Update responsive tables
            this.makeTablesResponsive();
            
            // Update tooltips for the new viewport size
            this.updateTooltips();
            
            // Dispatch custom event for modules to respond to resize
            window.dispatchEvent(new CustomEvent('app:resize', {
                detail: {
                    width: this.viewportWidth,
                    height: this.viewportHeight,
                    isMobile: this.viewportWidth < 768
                }
            }));
        },
        
        /**
         * Handle visibility change events (page shown/hidden)
         */
        handleVisibilityChange: function() {
            const isVisible = document.visibilityState === 'visible';
            
            // Dispatch custom event for modules to respond to visibility change
            window.dispatchEvent(new CustomEvent('app:visibilitychange', {
                detail: { isVisible }
            }));
            
            // Optimize performance when page is not visible
            if (!isVisible) {
                // Pause non-essential animations or polling
                this.pauseNonEssentialOperations();
            } else {
                // Resume operations when page becomes visible again
                this.resumeOperations();
            }
        },
        
        /**
         * Pause non-essential operations when page is hidden
         */
        pauseNonEssentialOperations: function() {
            // Implementation depends on what operations need pausing
            console.log('Pausing non-essential operations');
        },
        
        /**
         * Resume operations when page becomes visible
         */
        resumeOperations: function() {
            // Implementation depends on what operations need resuming
            console.log('Resuming operations');
        },

        /**
         * Initialize flash messages from Flask
         */
        initializeFlashMessages: function() {
            const messagesContainer = document.getElementById('flask-messages');
            if (!messagesContainer) return;

            try {
                const messagesData = messagesContainer.dataset.messages;
                if (!messagesData || messagesData.trim() === '') {
                    console.log('No flash messages found');
                    return;
                }

                const messages = JSON.parse(messagesData);
                if (Array.isArray(messages)) {
                    messages.forEach(([category, message]) => {
                        const messageId = btoa(category + message);
                        if (!this.processedMessageIds.has(messageId)) {
                            this.processedMessageIds.add(messageId);
                            window.showNotification(message, category, 'both');
                        }
                    });
                }
                
                messagesContainer.dataset.messages = '[]';
            } catch (error) {
                console.error('Error processing flash messages:', error);
            }
        },

        /**
         * Initialize Toastr notification library
         */
        initializeToastr: function() {
            // Configure toastr for better mobile display
            toastr.options = {
                positionClass: window.innerWidth < 768 ? "toast-top-full-width" : "toast-top-right",
                preventDuplicates: true,
                newestOnTop: true,
                progressBar: true,
                timeOut: 3000,
                extendedTimeOut: 1000,
                closeButton: true,
                tapToDismiss: true,
                showEasing: "swing",
                hideEasing: "linear",
                showMethod: "fadeIn",
                hideMethod: "fadeOut"
            };
        },

        /**
         * Initialize Bootstrap components with accessibility and mobile optimizations
         */
        initializeBootstrapComponents: function() {
            // Initialize tooltips with touch-friendly configuration
            this.updateTooltips();

            // Initialize popovers with touch-friendly configuration
            const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
            popoverTriggerList.map(function (popoverTriggerEl) {
                return new bootstrap.Popover(popoverTriggerEl, {
                    trigger: 'click', // Make popovers touch-friendly
                    container: 'body',
                    html: true,
                    sanitize: false // Be careful with this setting - ensure content is safe
                });
            });
            
            // Make modals more accessible
            const modals = document.querySelectorAll('.modal');
            modals.forEach(modal => {
                modal.addEventListener('shown.bs.modal', function() {
                    // Focus the first focusable element
                    const focusable = modal.querySelectorAll(
                        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                    );
                    if (focusable.length) {
                        focusable[0].focus();
                    }
                });
            });
            
            // Make dropdowns more touch-friendly
            const dropdowns = document.querySelectorAll('.dropdown');
            dropdowns.forEach(dropdown => {
                if (this.touchEnabled) {
                    dropdown.classList.add('dropdown-touch');
                }
            });
        },
        
        /**
         * Update tooltips with appropriate configuration based on device
         */
        updateTooltips: function() {
            // Remove existing tooltips
            const existingTooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
            existingTooltips.forEach(element => {
                const tooltip = bootstrap.Tooltip.getInstance(element);
                if (tooltip) {
                    tooltip.dispose();
                }
            });
            
            // Initialize tooltips with appropriate configuration
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map((tooltipTriggerEl) => {
                return new bootstrap.Tooltip(tooltipTriggerEl, {
                    trigger: this.touchEnabled ? 'click' : 'hover focus', // Touch-friendly on mobile
                    boundary: 'viewport',
                    placement: window.innerWidth < 768 ? 'bottom' : 'auto'
                });
            });
        },

        /**
         * Initialize accessibility features
         */
        initializeAccessibility: function() {
            // Add skip to content link
            this.addSkipToContentLink();
            
            // Ensure proper ARIA attributes
            this.ensureAriaAttributes();
            
            // Make focus visible for keyboard users
            this.enhanceFocusVisibility();
            
            // Add keyboard navigation for custom components
            this.enhanceKeyboardNavigation();
        },
        
        /**
         * Add skip to content link for keyboard users
         */
        addSkipToContentLink: function() {
            if (document.getElementById('skip-to-content')) return;
            
            const skipLink = document.createElement('a');
            skipLink.id = 'skip-to-content';
            skipLink.href = '#main-content';
            skipLink.className = 'visually-hidden-focusable';
            skipLink.textContent = 'Skip to main content';
            
            document.body.insertBefore(skipLink, document.body.firstChild);
            
            // Add id to main content if not present
            const main = document.querySelector('main');
            if (main && !main.id) {
                main.id = 'main-content';
            }
        },
        
        /**
         * Ensure proper ARIA attributes on interactive elements
         */
        ensureAriaAttributes: function() {
            // Add missing aria-labels to buttons without text
            const iconButtons = document.querySelectorAll('button:not([aria-label])');
            iconButtons.forEach(button => {
                if (!button.textContent.trim() && button.querySelector('i, .bi')) {
                    // Try to infer label from icon class
                    const icon = button.querySelector('i, .bi');
                    const iconClass = Array.from(icon.classList)
                        .find(cls => cls.startsWith('bi-'));
                    
                    if (iconClass) {
                        const label = iconClass.replace('bi-', '').replace(/-/g, ' ');
                        button.setAttribute('aria-label', label);
                    } else {
                        button.setAttribute('aria-label', 'Button');
                    }
                }
            });
            
            // Ensure form inputs have associated labels
            const inputs = document.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                if (!input.id) return;
                
                const hasLabel = document.querySelector(`label[for="${input.id}"]`);
                if (!hasLabel && !input.hasAttribute('aria-label')) {
                    // Try to use placeholder as fallback
                    if (input.placeholder) {
                        input.setAttribute('aria-label', input.placeholder);
                    }
                }
            });
        },
        
        /**
         * Enhance focus visibility for keyboard users
         */
        enhanceFocusVisibility: function() {
            // Add class to body when using keyboard navigation
            document.body.addEventListener('keydown', function(e) {
                if (e.key === 'Tab') {
                    document.body.classList.add('keyboard-user');
                }
            });
            
            // Remove class when using mouse
            document.body.addEventListener('mousedown', function() {
                document.body.classList.remove('keyboard-user');
            });
        },
        
        /**
         * Enhance keyboard navigation for custom components
         */
        enhanceKeyboardNavigation: function() {
            // Make custom dropdowns keyboard accessible
            const customDropdowns = document.querySelectorAll('.custom-dropdown');
            customDropdowns.forEach(dropdown => {
                const trigger = dropdown.querySelector('.dropdown-toggle');
                const menu = dropdown.querySelector('.dropdown-menu');
                
                if (trigger && menu) {
                    trigger.setAttribute('aria-haspopup', 'true');
                    trigger.setAttribute('aria-expanded', 'false');
                    
                    trigger.addEventListener('keydown', function(e) {
                        if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault();
                            this.click();
                        }
                    });
                }
            });
        },
        
        /**
         * Handle history change events
         */
        handleHistoryChange: function(event) {
            this.processedMessageIds.clear();
            
            // Dispatch custom event for modules to respond to history change
            window.dispatchEvent(new CustomEvent('app:historychange', {
                detail: { state: event.state }
            }));
        },
        
        /**
         * Format currency value
         * @param {number} value - The value to format
         * @param {string} currency - The currency code (default: USD)
         * @returns {string} Formatted currency string
         */
        formatCurrency: function(value, currency = 'USD') {
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: currency,
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }).format(value);
        },
        
        /**
         * Format percentage value
         * @param {number} value - The value to format
         * @param {number} decimals - Number of decimal places (default: 2)
         * @returns {string} Formatted percentage string
         */
        formatPercentage: function(value, decimals = 2) {
            return new Intl.NumberFormat('en-US', {
                style: 'percent',
                minimumFractionDigits: decimals,
                maximumFractionDigits: decimals
            }).format(value);
        },
        
        /**
         * Parse numeric value from string
         * @param {string} value - The string to parse
         * @returns {number} The parsed number
         */
        parseNumericValue: function(value) {
            if (typeof value === 'number') return value;
            if (!value) return 0;
            
            // Remove currency symbols, commas, etc.
            const cleanValue = value.toString().replace(/[^0-9.-]/g, '');
            const parsedValue = parseFloat(cleanValue);
            return isNaN(parsedValue) ? 0 : parsedValue;
        }
    };

    // Initialize base module
    window.baseModule = baseModule;
    
    // Initialize when DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        baseModule.init();
    });

})(window);
