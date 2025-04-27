/**
 * notifications.js - Enhanced notification system
 * Provides a robust notification system with categorized messages and accessibility features
 */
(function(window) {
    // Constants
    const POSITIONS = {
        TOP: 'top',
        BOTTOM: 'bottom',
        BOTH: 'both'
    };
    
    const TYPES = {
        SUCCESS: 'success',
        ERROR: 'error',
        WARNING: 'warning',
        INFO: 'info'
    };
    
    const ICONS = {
        [TYPES.SUCCESS]: '<i class="bi bi-check-circle-fill"></i>',
        [TYPES.ERROR]: '<i class="bi bi-exclamation-circle-fill"></i>',
        [TYPES.WARNING]: '<i class="bi bi-exclamation-triangle-fill"></i>',
        [TYPES.INFO]: '<i class="bi bi-info-circle-fill"></i>'
    };
    
    const ARIA_LIVE = {
        [TYPES.ERROR]: 'assertive',
        [TYPES.WARNING]: 'assertive',
        [TYPES.SUCCESS]: 'polite',
        [TYPES.INFO]: 'polite'
    };

    const DEFAULT_OPTIONS = {
        closeButton: true,
        debug: false,
        newestOnTop: true,
        progressBar: true,
        preventDuplicates: true,
        showDuration: "300",
        hideDuration: "1000",
        timeOut: "5000",
        extendedTimeOut: "1000",
        showEasing: "swing",
        hideEasing: "linear",
        showMethod: "fadeIn",
        hideMethod: "fadeOut",
        tapToDismiss: true,
        escapeHtml: false
    };

    /**
     * Enhanced notification system with accessibility and mobile optimizations
     */
    class NotificationSystem {
        constructor() {
            this.initialized = false;
            this.containers = {
                top: null,
                bottom: null
            };
            this.notificationHistory = [];
            this.maxHistoryLength = 50;
            this.touchEnabled = 'ontouchstart' in window;
            this.init();
        }

        /**
         * Initialize the notification system
         */
        init() {
            if (this.initialized) return;

            this.containers.top = this.createContainer('top');
            this.containers.bottom = this.createContainer('bottom');
            
            // Create screen reader alert container
            this.screenReaderAlert = this.createScreenReaderAlert();

            // Initialize toastr instances if available
            if (typeof toastr !== 'undefined') {
                // Configure bottom toastr
                window.toastrBottom = toastr;
                toastrBottom.options = {
                    ...DEFAULT_OPTIONS,
                    positionClass: "toast-bottom-right",
                    target: "body"
                };

                // Configure top toastr
                window.toastrTop = Object.create(toastr);
                toastrTop.options = {
                    ...DEFAULT_OPTIONS,
                    positionClass: "toast-top-right",
                    target: "#toastr-top"
                };
                
                // Add custom options for mobile
                if (this.touchEnabled) {
                    toastrBottom.options.timeOut = 7000; // Longer display time on mobile
                    toastrTop.options.timeOut = 7000;
                    
                    if (window.innerWidth < 768) {
                        toastrBottom.options.positionClass = "toast-bottom-full-width";
                        toastrTop.options.positionClass = "toast-top-full-width";
                    }
                }
            }

            // Listen for theme changes
            this.setupThemeChangeListener();
            
            // Listen for visibility changes to manage notifications
            document.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));

            this.initialized = true;
        }

        /**
         * Create a container for notifications
         * @param {string} position - The position of the container (top or bottom)
         * @returns {HTMLElement} The container element
         */
        createContainer(position) {
            const containerId = `toastr-${position}`;
            let container = document.getElementById(containerId);
            
            if (!container) {
                container = document.createElement('div');
                container.id = containerId;
                container.className = `toast-${position}-right notification-container`;
                container.setAttribute('aria-live', 'polite');
                container.setAttribute('aria-atomic', 'true');
                document.body.appendChild(container);
            }
            
            return container;
        }
        
        /**
         * Create a screen reader alert container for accessibility
         * @returns {HTMLElement} The screen reader alert element
         */
        createScreenReaderAlert() {
            let alertContainer = document.getElementById('sr-alert-container');
            
            if (!alertContainer) {
                alertContainer = document.createElement('div');
                alertContainer.id = 'sr-alert-container';
                alertContainer.className = 'sr-only';
                alertContainer.setAttribute('aria-live', 'assertive');
                document.body.appendChild(alertContainer);
            }
            
            return alertContainer;
        }
        
        /**
         * Setup listener for theme changes
         */
        setupThemeChangeListener() {
            // Listen for dark/light mode changes
            const darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            
            const handleThemeChange = (e) => {
                const isDarkMode = e.matches;
                document.documentElement.classList.toggle('dark-theme', isDarkMode);
                document.documentElement.classList.toggle('light-theme', !isDarkMode);
                
                // Update notification styling if needed
                this.updateNotificationStyling(isDarkMode);
            };
            
            // Set initial theme
            handleThemeChange(darkModeMediaQuery);
            
            // Listen for changes
            if (darkModeMediaQuery.addEventListener) {
                darkModeMediaQuery.addEventListener('change', handleThemeChange);
            } else if (darkModeMediaQuery.addListener) {
                // Fallback for older browsers
                darkModeMediaQuery.addListener(handleThemeChange);
            }
        }
        
        /**
         * Update notification styling based on theme
         * @param {boolean} isDarkMode - Whether dark mode is active
         */
        updateNotificationStyling(isDarkMode) {
            // Implementation depends on styling needs
            console.log(`Theme changed to ${isDarkMode ? 'dark' : 'light'} mode`);
        }
        
        /**
         * Handle visibility change events
         */
        handleVisibilityChange() {
            if (document.visibilityState === 'hidden') {
                // Page is hidden, pause notifications
                this.pauseNotifications();
            } else {
                // Page is visible again, resume notifications
                this.resumeNotifications();
            }
        }
        
        /**
         * Pause notifications when page is hidden
         */
        pauseNotifications() {
            // Implementation depends on notification system
            console.log('Pausing notifications');
        }
        
        /**
         * Resume notifications when page becomes visible
         */
        resumeNotifications() {
            // Implementation depends on notification system
            console.log('Resuming notifications');
        }

        /**
         * Show a notification
         * @param {string} message - The message to display
         * @param {string} type - The type of notification (success, error, warning, info)
         * @param {string} position - The position to display the notification
         * @param {Object} options - Additional options for the notification
         */
        show(message, type = TYPES.INFO, position = POSITIONS.BOTH, options = {}) {
            if (!this.initialized) {
                this.init();
            }
            
            // Validate type
            if (!Object.values(TYPES).includes(type)) {
                console.warn(`Invalid notification type: ${type}. Using 'info' instead.`);
                type = TYPES.INFO;
            }
            
            // Add to history
            this.addToHistory(message, type);
            
            // Announce to screen readers
            this.announceToScreenReader(message, type);

            const positions = position === POSITIONS.BOTH 
                ? [POSITIONS.TOP, POSITIONS.BOTTOM] 
                : [position];

            positions.forEach(pos => {
                if (typeof toastr !== 'undefined') {
                    // Use toastr if available
                    const toastrInstance = pos === POSITIONS.TOP ? window.toastrTop : window.toastrBottom;
                    
                    // Format message with icon if HTML is allowed
                    let formattedMessage = message;
                    if (!options.escapeHtml && options.showIcon !== false) {
                        formattedMessage = `${ICONS[type]} ${message}`;
                    }
                    
                    // Show notification
                    toastrInstance[type](formattedMessage, options.title, {
                        ...toastrInstance.options,
                        ...options
                    });
                } else {
                    // Fallback to custom implementation
                    this.showCustomNotification(message, type, pos, options);
                }
            });
            
            // Return a unique ID for this notification (useful for programmatic dismissal)
            return Date.now().toString(36) + Math.random().toString(36).substr(2);
        }
        
        /**
         * Add notification to history
         * @param {string} message - The notification message
         * @param {string} type - The notification type
         */
        addToHistory(message, type) {
            const timestamp = new Date();
            
            this.notificationHistory.unshift({
                message,
                type,
                timestamp
            });
            
            // Trim history if needed
            if (this.notificationHistory.length > this.maxHistoryLength) {
                this.notificationHistory = this.notificationHistory.slice(0, this.maxHistoryLength);
            }
        }
        
        /**
         * Get notification history
         * @returns {Array} The notification history
         */
        getHistory() {
            return [...this.notificationHistory];
        }
        
        /**
         * Clear notification history
         */
        clearHistory() {
            this.notificationHistory = [];
        }
        
        /**
         * Announce notification to screen readers
         * @param {string} message - The message to announce
         * @param {string} type - The notification type
         */
        announceToScreenReader(message, type) {
            // Create a clean text version of the message (no HTML)
            const cleanMessage = message.replace(/<[^>]*>?/gm, '');
            
            // Set appropriate aria-live attribute based on notification type
            this.screenReaderAlert.setAttribute('aria-live', ARIA_LIVE[type] || 'polite');
            
            // Update content to trigger screen reader announcement
            this.screenReaderAlert.textContent = `${type}: ${cleanMessage}`;
            
            // Clear after a delay to allow for multiple notifications
            setTimeout(() => {
                this.screenReaderAlert.textContent = '';
            }, 3000);
        }

        /**
         * Show a custom notification when toastr is not available
         * @param {string} message - The message to display
         * @param {string} type - The type of notification
         * @param {string} position - The position to display the notification
         * @param {Object} options - Additional options for the notification
         */
        showCustomNotification(message, type, position, options = {}) {
            const container = this.containers[position];
            
            const toast = document.createElement('div');
            toast.className = `toast toast-${type} fadeIn`;
            toast.setAttribute('role', 'alert');
            toast.setAttribute('aria-live', ARIA_LIVE[type] || 'polite');
            
            // Add title if provided
            if (options.title) {
                const titleElement = document.createElement('div');
                titleElement.className = 'toast-title';
                titleElement.textContent = options.title;
                toast.appendChild(titleElement);
            }
            
            // Add message with icon
            const messageElement = document.createElement('div');
            messageElement.className = 'toast-message';
            
            if (options.escapeHtml !== false && options.showIcon !== false) {
                messageElement.innerHTML = `${ICONS[type]} ${message}`;
            } else {
                messageElement.textContent = message;
            }
            
            // Add close button
            const closeButton = document.createElement('button');
            closeButton.className = 'toast-close-button';
            closeButton.innerHTML = '×';
            closeButton.setAttribute('aria-label', 'Close notification');
            closeButton.onclick = () => this.removeToast(toast);
            
            toast.appendChild(closeButton);
            toast.appendChild(messageElement);
            
            // Add progress bar
            if (options.progressBar !== false) {
                const progressBar = document.createElement('div');
                progressBar.className = 'toast-progress';
                toast.appendChild(progressBar);
                
                // Animate progress bar
                let width = 100;
                const timeOut = options.timeOut || 5000;
                const interval = setInterval(() => {
                    width -= 100 / (timeOut / 100);
                    progressBar.style.width = `${width}%`;
                    
                    if (width <= 0) {
                        clearInterval(interval);
                    }
                }, 100);
            }
            
            // Add tap to dismiss
            if (options.tapToDismiss !== false) {
                toast.addEventListener('click', (e) => {
                    if (e.target !== closeButton) {
                        this.removeToast(toast);
                    }
                });
            }
            
            // Add to container
            if (options.newestOnTop !== false) {
                container.insertBefore(toast, container.firstChild);
            } else {
                container.appendChild(toast);
            }
            
            // Auto remove after timeout
            const timeOut = options.timeOut || 5000;
            setTimeout(() => this.removeToast(toast), timeOut);
            
            return toast;
        }

        /**
         * Remove a toast notification
         * @param {HTMLElement} toast - The toast element to remove
         */
        removeToast(toast) {
            if (!toast || !toast.parentElement) return;
            
            toast.classList.remove('fadeIn');
            toast.classList.add('fadeOut');
            
            setTimeout(() => {
                if (toast.parentElement) {
                    toast.parentElement.removeChild(toast);
                }
            }, 1000);
        }
        
        /**
         * Clear all notifications
         * @param {string} position - The position to clear (top, bottom, or both)
         */
        clearAll(position = POSITIONS.BOTH) {
            const positions = position === POSITIONS.BOTH 
                ? [POSITIONS.TOP, POSITIONS.BOTTOM] 
                : [position];
                
            positions.forEach(pos => {
                if (typeof toastr !== 'undefined') {
                    const toastrInstance = pos === POSITIONS.TOP ? window.toastrTop : window.toastrBottom;
                    toastrInstance.clear();
                } else {
                    const container = this.containers[pos];
                    while (container.firstChild) {
                        container.removeChild(container.firstChild);
                    }
                }
            });
        }
    }

    // Create the notification system instance
    const notificationSystem = new NotificationSystem();
    
    /**
     * Show a notification
     * @param {string} message - The message to display
     * @param {string} type - The type of notification (success, error, warning, info)
     * @param {string} position - The position to display the notification
     * @param {Object} options - Additional options for the notification
     * @returns {string} A unique ID for the notification
     */
    window.showNotification = function(message, type = TYPES.INFO, position = POSITIONS.BOTH, options = {}) {
        return notificationSystem.show(message, type, position, options);
    };
    
    /**
     * Show a success notification
     * @param {string} message - The message to display
     * @param {string} position - The position to display the notification
     * @param {Object} options - Additional options for the notification
     * @returns {string} A unique ID for the notification
     */
    window.showSuccess = function(message, position = POSITIONS.TOP, options = {}) {
        return notificationSystem.show(message, TYPES.SUCCESS, position, options);
    };
    
    /**
     * Show an error notification
     * @param {string} message - The message to display
     * @param {string} position - The position to display the notification
     * @param {Object} options - Additional options for the notification
     * @returns {string} A unique ID for the notification
     */
    window.showError = function(message, position = POSITIONS.TOP, options = {}) {
        return notificationSystem.show(message, TYPES.ERROR, position, options);
    };
    
    /**
     * Show a warning notification
     * @param {string} message - The message to display
     * @param {string} position - The position to display the notification
     * @param {Object} options - Additional options for the notification
     * @returns {string} A unique ID for the notification
     */
    window.showWarning = function(message, position = POSITIONS.TOP, options = {}) {
        return notificationSystem.show(message, TYPES.WARNING, position, options);
    };
    
    /**
     * Show an info notification
     * @param {string} message - The message to display
     * @param {string} position - The position to display the notification
     * @param {Object} options - Additional options for the notification
     * @returns {string} A unique ID for the notification
     */
    window.showInfo = function(message, position = POSITIONS.TOP, options = {}) {
        return notificationSystem.show(message, TYPES.INFO, position, options);
    };
    
    /**
     * Clear all notifications
     * @param {string} position - The position to clear (top, bottom, or both)
     */
    window.clearNotifications = function(position = POSITIONS.BOTH) {
        notificationSystem.clearAll(position);
    };
    
    /**
     * Get notification history
     * @returns {Array} The notification history
     */
    window.getNotificationHistory = function() {
        return notificationSystem.getHistory();
    };
    
    /**
     * Clear notification history
     */
    window.clearNotificationHistory = function() {
        notificationSystem.clearHistory();
    };

    // Export constants
    window.NOTIFICATION_POSITIONS = POSITIONS;
    window.NOTIFICATION_TYPES = TYPES;

})(window);
