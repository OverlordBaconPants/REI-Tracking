// base.js - Mobile-first version
(function(window) {
    const baseModule = {
        processedMessageIds: new Set(),
        
        init: function() {
            console.log('Initializing base module');
            this.initializeLibraries();
            this.initializeFlashMessages();
            this.initializeMobileHandlers();
            
            // Add history state handler
            window.addEventListener('popstate', this.handleHistoryChange.bind(this));
            
            // Add resize handler for mobile/desktop transitions
            window.addEventListener('resize', this.handleResize.bind(this));
        },

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
        
            return true;
        },
        
        // Helper method to safely check if a library exists
        isLibraryLoaded: function(libraryName) {
            try {
                return eval(`typeof ${libraryName} !== 'undefined'`);
            } catch (e) {
                return false;
            }
        },

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
        },

        handleResize: function() {
            // Handle any necessary adjustments when switching between mobile/desktop
            const sidebar = document.getElementById('sidebarMenu');
            if (sidebar && window.innerWidth >= 768) {
                sidebar.classList.add('show');
            }
        },

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

        initializeToastr: function() {
            // Configure toastr for better mobile display
            toastr.options = {
                positionClass: window.innerWidth < 768 ? "toast-top-full-width" : "toast-top-right",
                preventDuplicates: true,
                newestOnTop: true,
                progressBar: true,
                timeOut: 3000,
                extendedTimeOut: 1000
            };
        },

        initializeBootstrapComponents: function() {
            // Initialize tooltips with touch-friendly configuration
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl, {
                    trigger: 'click hover' // Make tooltips touch-friendly
                });
            });

            // Initialize popovers with touch-friendly configuration
            const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
            popoverTriggerList.map(function (popoverTriggerEl) {
                return new bootstrap.Popover(popoverTriggerEl, {
                    trigger: 'click' // Make popovers touch-friendly
                });
            });
        },

        handleHistoryChange: function(event) {
            this.processedMessageIds.clear();
        }
    };

    // Initialize base module
    window.baseModule = baseModule;
    
    // Initialize when DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        baseModule.init();
    });

})(window);
