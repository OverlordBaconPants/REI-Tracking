const viewTransactionsModule = {
    touchStartX: 0,
    touchStartY: 0,
    lastTap: 0,
    isScrolling: false,
    hasHapticFeedback: false,

    init: async function() {
        try {
            console.log('Initializing view transactions module');
            
            // Check for haptic feedback support
            if ('vibrate' in navigator) {
                this.hasHapticFeedback = true;
            }
            
            this.initializeUrlParameters();
            this.initializeDashboard();
            this.initializeMessageHandler();
            this.initializeDeleteHandlers();
            this.initializeMobileHandlers();
            this.setupPullToRefresh();
            
        } catch (error) {
            console.error('Error initializing View Transactions module:', error);
            this.showNotification('Error loading View Transactions module: ' + error.message, 'error');
        }
    },

    initializeDashboard: function() {
        console.log('Initializing transactions dashboard');
        
        // Check for success message in URL
        const urlParams = new URLSearchParams(window.location.search);
        const successMessage = urlParams.get('success');
        if (successMessage) {
            this.showNotification(decodeURIComponent(successMessage), 'success');
        }
        
        // Initialize the iframe height adjustment
        this.adjustIframeHeight();
        window.addEventListener('resize', this.adjustIframeHeight.bind(this));
        window.addEventListener('orientationchange', this.adjustIframeHeight.bind(this));
        
        // Check for any flash messages
        const flashMessages = document.querySelectorAll('.flash-message');
        flashMessages.forEach(message => {
            const category = message.dataset.category || 'info';
            const text = message.textContent;
            
            this.showNotification(text, category.toLowerCase());
            message.remove();
        });
    },

    initializeUrlParameters: function() {
        const urlParams = new URLSearchParams(window.location.search);
        
        // Handle filters if present
        const filters = urlParams.get('filters');
        if (filters) {
            try {
                const filterState = JSON.parse(decodeURIComponent(filters));
                this.restoreFilters(filterState);
                
                // Check for refresh parameter
                const refresh = urlParams.get('refresh');
                if (refresh) {
                    setTimeout(() => {
                        this.forceDataRefresh();
                    }, 100);
                }
            } catch (e) {
                console.error('Error restoring filters:', e);
            }
        }
    },

    initializeMobileHandlers: function() {
        // Improve scroll handling on mobile
        const tableWrapper = document.querySelector('.table-responsive-sm');
        if (tableWrapper) {
            tableWrapper.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: true });
            tableWrapper.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: false });
            tableWrapper.addEventListener('touchend', this.handleTouchEnd.bind(this), { passive: true });

            // Double tap handler
            tableWrapper.addEventListener('touchend', this.handleDoubleTap.bind(this));
        }

        // Add orientation change handler
        window.addEventListener('orientationchange', () => {
            this.handleOrientationChange();
        });

        // Handle mobile keyboard
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('focus', () => {
                setTimeout(() => {
                    this.handleKeyboardShow(input);
                }, 300);
            });

            input.addEventListener('blur', () => {
                this.handleKeyboardHide();
            });
        });
    },

    handleTouchStart: function(e) {
        this.touchStartX = e.touches[0].clientX;
        this.touchStartY = e.touches[0].clientY;
        this.isScrolling = undefined;
    },

    handleTouchMove: function(e) {
        if (!this.touchStartX || !this.touchStartY) return;

        const diffX = e.touches[0].clientX - this.touchStartX;
        const diffY = e.touches[0].clientY - this.touchStartY;

        if (typeof this.isScrolling === 'undefined') {
            this.isScrolling = Math.abs(diffX) < Math.abs(diffY);
        }

        if (!this.isScrolling) {
            e.preventDefault();
        }
    },

    handleTouchEnd: function() {
        this.touchStartX = 0;
        this.touchStartY = 0;
        this.isScrolling = undefined;
    },

    handleDoubleTap: function(e) {
        const currentTime = new Date().getTime();
        const tapLength = currentTime - this.lastTap;

        if (tapLength < 500 && tapLength > 0) {
            e.preventDefault();
            if (this.hasHapticFeedback) {
                navigator.vibrate(50);
            }
        }

        this.lastTap = currentTime;
    },

    handleEditTransaction: function(id, description) {
        console.log('Editing transaction:', id, description);
        
        // Get current filters from URL
        const urlParams = new URLSearchParams(window.location.search);
        const filters = urlParams.get('filters') || '{}';
        
        // Navigate to edit page with filters preserved
        window.location.href = `/transactions/edit/${id}?filters=${encodeURIComponent(filters)}`;
        
        if (this.hasHapticFeedback) {
            navigator.vibrate(50); // Light feedback for edit action
        }
    },
    
    handleNavigateToAdd: function() {
        // Preserve filters when navigating to add transaction
        const urlParams = new URLSearchParams(window.location.search);
        const filters = urlParams.get('filters') || '{}';
        window.location.href = `/transactions/add?filters=${encodeURIComponent(filters)}`;
    },

    handleOrientationChange: function() {
        // Clear any visible toasts
        toastr.clear();

        // Update toast position
        toastr.options.positionClass = window.innerWidth < 768 ? 
            "toast-top-full-width" : "toast-top-right";

        // Refresh table layout
        setTimeout(() => {
            this.forceDataRefresh();
            this.adjustIframeHeight();
        }, 300);
    },

    adjustIframeHeight: function() {
        const navbar = document.querySelector('.navbar');
        const iframeWrapper = document.querySelector('.iframe-wrapper');
        
        if (navbar && iframeWrapper) {
            const navbarHeight = navbar.offsetHeight;
            const windowHeight = window.innerHeight;
            const wrapperTop = iframeWrapper.getBoundingClientRect().top;
            const availableHeight = windowHeight - wrapperTop;
            
            const minHeight = Math.max(400, availableHeight);
            iframeWrapper.style.height = `${minHeight}px`;
        }
    },

    handleKeyboardShow: function(input) {
        const wrapper = document.querySelector('.iframe-wrapper');
        if (!wrapper) return;

        const inputRect = input.getBoundingClientRect();
        const scrollNeeded = inputRect.bottom - window.innerHeight + 100;

        if (scrollNeeded > 0) {
            wrapper.scrollBy({
                top: scrollNeeded,
                behavior: 'smooth'
            });
        }
    },

    handleKeyboardHide: function() {
        const wrapper = document.querySelector('.iframe-wrapper');
        if (!wrapper) return;

        wrapper.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    },

    setupPullToRefresh: function() {
        let startY = 0;
        let refreshStarted = false;
        const threshold = 150;
        const wrapper = document.querySelector('.iframe-wrapper');

        if (!wrapper) return;

        wrapper.addEventListener('touchstart', (e) => {
            startY = e.touches[0].clientY;
            refreshStarted = false;
        }, { passive: true });

        wrapper.addEventListener('touchmove', (e) => {
            const y = e.touches[0].clientY;
            const diff = y - startY;

            if (diff > 0 && wrapper.scrollTop === 0 && !refreshStarted) {
                if (diff > threshold) {
                    refreshStarted = true;
                    this.handlePullToRefresh();
                }
            }
        }, { passive: true });
    },

    handlePullToRefresh: function() {
        if (this.hasHapticFeedback) {
            navigator.vibrate([20, 30, 20]);
        }

        this.showNotification('Refreshing...', 'info', 1000);
        this.forceDataRefresh();
    },

    initializeMessageHandler: function() {
        window.addEventListener('message', (event) => {
            console.log('Received message in view transactions:', event.data);
            
            if (event.data.type === 'notification') {
                this.showNotification(event.data.message, event.data.notificationType);
            }
        });
    },

    initializeDeleteHandlers: function() {
        document.addEventListener('click', (e) => {
            if (e.target.matches('.delete-transaction')) {
                const transactionId = e.target.dataset.transactionId;
                const description = e.target.dataset.description;
                this.handleDeleteTransaction(transactionId, description);
            }
        });
    },

    handleDeleteTransaction: function(transactionId, description) {
        const modalElement = document.getElementById('deleteConfirmModal');
        if (!modalElement) return;

        const modal = new bootstrap.Modal(modalElement);
        const confirmButton = modalElement.querySelector('#confirmDelete');
        const messageElement = modalElement.querySelector('.modal-body p');

        messageElement.textContent = `Are you sure you want to delete the transaction "${description}"? This action cannot be undone.`;

        // Remove existing event listeners
        const newConfirmButton = confirmButton.cloneNode(true);
        confirmButton.parentNode.replaceChild(newConfirmButton, confirmButton);

        // Add new event listener
        newConfirmButton.addEventListener('click', async () => {
            try {
                if (this.hasHapticFeedback) {
                    navigator.vibrate(100);
                }

                const response = await this.deleteTransaction(transactionId);
                modal.hide();

                if (response.success) {
                    this.showNotification('Transaction deleted successfully', 'success');
                    this.forceDataRefresh();
                } else {
                    this.showNotification(response.message || 'Error deleting transaction', 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                this.showNotification('Error deleting transaction', 'error');
            }
        });

        modal.show();
    },

    deleteTransaction: async function(transactionId) {
        const response = await fetch(`/transactions/delete/${transactionId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        return await response.json();
    },

    createTransactionUrl: function(filters) {
        const encodedFilters = encodeURIComponent(filters);
        return `/transactions/view/?filters=${encodedFilters}`;
    },

    showNotification: function(message, type = 'info', timeout = 3000) {
        // Update position based on screen size
        toastr.options.positionClass = window.innerWidth < 768 ? 
            "toast-top-full-width" : "toast-top-right";
        
        toastr.options.timeOut = timeout;

        toastr[type](message);

        if (this.hasHapticFeedback && (type === 'success' || type === 'error')) {
            navigator.vibrate(type === 'success' ? 50 : [100, 50, 100]);
        }
    },

    restoreFilters: function() {
        const urlParams = new URLSearchParams(window.location.search);
        let filters = urlParams.get('filters') || '{}';
        try {
            // Decode if needed
            filters = decodeURIComponent(filters);
            // Verify it's valid JSON
            JSON.parse(filters);
        } catch (e) {
            console.warn('Invalid filters format, using default');
            filters = '{}';
        }
        return filters;
    },

    forceDataRefresh: function() {
        console.log('Forcing data refresh');
        const refreshTrigger = document.getElementById('refresh-trigger');
        if (refreshTrigger) {
            refreshTrigger.value = Date.now();
            refreshTrigger.dispatchEvent(new Event('change'));
        }
    }
};

// Configure toastr options
toastr.options = {
    closeButton: true,
    progressBar: true,
    newestOnTop: false,
    positionClass: window.innerWidth < 768 ? "toast-top-full-width" : "toast-top-right",
    preventDuplicates: true,
    onclick: null,
    showDuration: "300",
    hideDuration: "1000",
    timeOut: "3000",
    extendedTimeOut: "1000",
    showEasing: "swing",
    hideEasing: "linear",
    showMethod: "fadeIn",
    hideMethod: "fadeOut",
    tapToDismiss: true,
    closeHtml: '<button class="toast-close-button" style="min-height:44px;min-width:44px;">&times;</button>'
};

window.viewTransactionsModule = viewTransactionsModule;

export default viewTransactionsModule;