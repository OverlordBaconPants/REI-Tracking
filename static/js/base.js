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

            // Wait for toastr to be available
            this.waitForToastr()
                .then(() => {
                    this.initializeToastr();
                    this.initializeFlashMessages();
                })
                .catch(error => {
                    console.error('Error initializing toastr:', error);
                });

            this.initializeBootstrapComponents();
        },

        waitForToastr: function(timeout = 2000) {
            return new Promise((resolve, reject) => {
                const startTime = Date.now();
                
                const checkToastr = () => {
                    if (typeof toastr !== 'undefined') {
                        resolve();
                    } else if (Date.now() - startTime >= timeout) {
                        reject(new Error('Toastr failed to load'));
                    } else {
                        setTimeout(checkToastr, 100);
                    }
                };
                
                checkToastr();
            });
        },

        initializeToastr: function() {
            if (typeof toastr === 'undefined') {
                console.error('Toastr not available');
                return;
            }

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
                "hideMethod": "fadeOut"
            };
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
                            this.showNotification(message, category);
                        });
                    }
                } catch (error) {
                    console.error('Error processing flash messages:', error);
                }
            }
        },

        showNotification: function(message, category = 'info') {
            if (typeof toastr === 'undefined') {
                console.warn('Toastr not available, falling back to alert');
                alert(message);
                return;
            }

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
        }
    };

    window.baseModule = baseModule;
    window.showNotification = baseModule.showNotification.bind(baseModule);

})(window);