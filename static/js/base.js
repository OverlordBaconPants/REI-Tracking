// base.js - Modified version
(function(window) {
    const baseModule = {
        init: function() {
            console.log('Initializing base module');
            this.initializeLibraries();
            this.initializeFlashMessages();
        },

        initializeLibraries: function() {
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
                            window.showNotification(message, category, 'both');
                        });
                    }
                } catch (error) {
                    console.error('Error processing flash messages:', error);
                }
            }
        },

        initializeBootstrapComponents: function() {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });

            const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
            popoverTriggerList.map(function (popoverTriggerEl) {
                return new bootstrap.Popover(popoverTriggerEl);
            });
        }
    };

    // Only expose the baseModule
    window.baseModule = baseModule;

})(window);