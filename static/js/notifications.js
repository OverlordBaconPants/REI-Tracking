// notifications.js
(function(window) {
    // Configuration object for different positions
    const POSITIONS = {
        TOP: 'top',
        BOTTOM: 'bottom',
        BOTH: 'both'
    };

    const DEFAULT_OPTIONS = {
        closeButton: true,
        debug: false,
        newestOnTop: true,
        progressBar: true,
        preventDuplicates: false,
        showDuration: "300",
        hideDuration: "1000",
        timeOut: "5000",
        extendedTimeOut: "1000",
        showEasing: "swing",
        hideEasing: "linear",
        showMethod: "fadeIn",
        hideMethod: "fadeOut"
    };

    class NotificationSystem {
        constructor() {
            this.initialized = false;
            this.containers = {
                top: null,
                bottom: null
            };
        }

        init() {
            if (this.initialized) return;

            // Create containers
            this.containers.top = this.createContainer('top');
            this.containers.bottom = this.createContainer('bottom');

            // Initialize toastr if available
            if (typeof toastr !== 'undefined') {
                // Configure bottom notifications
                window.toastrBottom = toastr;
                toastrBottom.options = {
                    ...DEFAULT_OPTIONS,
                    positionClass: "toast-bottom-right",
                    target: "body"
                };

                // Configure top notifications
                window.toastrTop = Object.create(toastr);
                toastrTop.options = {
                    ...DEFAULT_OPTIONS,
                    positionClass: "toast-top-right",
                    target: "#toastr-top"
                };
            }

            this.initialized = true;
        }

        createContainer(position) {
            const containerId = `toastr-${position}`;
            let container = document.getElementById(containerId);
            
            if (!container) {
                container = document.createElement('div');
                container.id = containerId;
                container.className = `toast-${position}-right`;
                document.body.appendChild(container);
            }
            
            return container;
        }

        show(message, type = 'info', position = POSITIONS.BOTH) {
            if (!this.initialized) {
                this.init();
            }

            const positions = position === POSITIONS.BOTH 
                ? [POSITIONS.TOP, POSITIONS.BOTTOM] 
                : [position];

            positions.forEach(pos => {
                if (typeof toastr !== 'undefined') {
                    // Use toastr if available
                    const toastrInstance = pos === POSITIONS.TOP ? window.toastrTop : window.toastrBottom;
                    toastrInstance[type](message);
                } else {
                    // Fallback to custom implementation
                    this.showCustomNotification(message, type, pos);
                }
            });
        }

        showCustomNotification(message, type, position) {
            const container = this.containers[position];
            
            const toast = document.createElement('div');
            toast.className = `toast toast-${type} fadeIn`;
            
            const messageElement = document.createElement('div');
            messageElement.className = 'toast-message';
            messageElement.textContent = message;
            
            const closeButton = document.createElement('button');
            closeButton.className = 'toast-close-button';
            closeButton.innerHTML = '×';
            closeButton.onclick = () => this.removeToast(toast);
            
            toast.appendChild(closeButton);
            toast.appendChild(messageElement);
            
            const progressBar = document.createElement('div');
            progressBar.className = 'toast-progress';
            toast.appendChild(progressBar);
            
            container.appendChild(toast);
            
            // Auto remove after 5 seconds
            setTimeout(() => this.removeToast(toast), 5000);
        }

        removeToast(toast) {
            if (toast.parentElement) {
                toast.classList.remove('fadeIn');
                toast.classList.add('fadeOut');
                setTimeout(() => toast.remove(), 1000);
            }
        }
    }

    // Create and expose the notification system
    const notificationSystem = new NotificationSystem();
    
    // Override the existing showNotification function
    window.showNotification = function(message, type, position) {
        notificationSystem.show(message, type, position);
    };

    // Initialize on DOM content loaded
    document.addEventListener('DOMContentLoaded', () => {
        notificationSystem.init();
    });

})(window);