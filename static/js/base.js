// base.js - Contains the base initialization code
(function(window) {
    const baseModule = {
        init: function() {
            console.log('Initializing base module');
            this.initializeLibraries();
        },

        initializeLibraries: function() {
            // Check for jQuery
            if (typeof jQuery === 'undefined') {
                console.error('jQuery not loaded');
                return;
            }

            this.initializeBootstrapComponents();
        },

        initializeFlashMessages: function() {
            const messagesContainer = document.getElementById('flask-messages');
            if (messagesContainer) {
                try {
                    const messagesData = messagesContainer.dataset.messages;
                    console.log('Raw messages data:', messagesData);
                    
                    if (!messagesData || messagesData.trim() === '') {
                        console.log('No flash messages found');
                        return;
                    }
    
                    const messages = JSON.parse(messagesData);
                    console.log('Parsed messages:', messages);
    
                    if (Array.isArray(messages)) {
                        messages.forEach(([category, message]) => {
                            // Show messages in both positions
                            this.showNotification(message, category, 'both');
                        });
                    }
                } catch (error) {
                    console.error('Error processing flash messages:', error);
                }
            }
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
        }
    };

    // Expose the module and notification function
    window.baseModule = baseModule;
    window.showNotification = function(message, category, position = 'both') {
        baseModule.showNotification(message, category, position);
    };

})(window);