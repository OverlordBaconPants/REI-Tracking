// base.js - Fixed version
(function(window) {
    const baseModule = {
        processedMessageIds: new Set(),  // Track which messages we've processed

        init: function() {
            console.log('Initializing base module');
            this.initializeLibraries();
            this.initializeFlashMessages();
            
            // Add history state handler
            window.addEventListener('popstate', (event) => {
                this.handleHistoryChange(event);
            });
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
            if (!messagesContainer) return;

            try {
                const messagesData = messagesContainer.dataset.messages;
                if (!messagesData || messagesData.trim() === '') {
                    console.log('No flash messages found');
                    return;
                }

                const messages = JSON.parse(messagesData);
                console.log('Parsed messages:', messages);

                if (Array.isArray(messages)) {
                    messages.forEach(([category, message]) => {
                        // Generate a unique ID for this message
                        const messageId = btoa(category + message);
                        
                        // Only process if we haven't seen this message before
                        if (!this.processedMessageIds.has(messageId)) {
                            this.processedMessageIds.add(messageId);
                            window.showNotification(message, category, 'both');
                        }
                    });
                }
                
                // Clear the messages after processing
                messagesContainer.dataset.messages = '[]';
            } catch (error) {
                console.error('Error processing flash messages:', error);
            }
        },

        handleHistoryChange: function(event) {
            // Clear processed messages when navigating
            this.processedMessageIds.clear();
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