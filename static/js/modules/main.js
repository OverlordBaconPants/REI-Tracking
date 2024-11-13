// /static/js/modules/main.js

const mainModule = {
    init: async function() {
        console.log('Initializing main dashboard module');
        try {
            await this.initializeDashboard();
            window.showNotification('Dashboard loaded successfully', 'success');
        } catch (error) {
            console.error('Error initializing dashboard:', error);
            window.showNotification('Error initializing dashboard', 'error');
        }
    },

    initializeDashboard: async function() {
        this.setupEventListeners();
        this.initializeTooltips();
        this.updateTotalEquity();
        
        // Set up message handler for Dash callbacks
        this.setupMessageHandler();
    },

    setupMessageHandler: function() {
        window.addEventListener('message', (event) => {
            // Handle messages from Dash components
            if (event.data && event.data.type === 'dashboardUpdate') {
                this.handleDashboardUpdate(event.data);
            }
        });
    },

    handleDashboardUpdate: function(data) {
        if (data.target === 'totalEquity') {
            this.updateTotalEquity();
        }
    },

    setupEventListeners: function() {
        // Property row click handlers
        document.querySelectorAll('.property-row').forEach(row => {
            row.addEventListener('click', this.handlePropertyRowClick.bind(this));
        });

        // Transaction row click handlers
        document.querySelectorAll('.transaction-row').forEach(row => {
            row.addEventListener('click', this.handleTransactionRowClick.bind(this));
        });

        // Equity calculations
        document.querySelectorAll('.equity-input').forEach(input => {
            input.addEventListener('input', this.updateTotalEquity.bind(this));
        });

        // Handle refresh trigger for Dash
        const refreshTrigger = document.getElementById('refresh-trigger');
        if (refreshTrigger) {
            refreshTrigger.addEventListener('change', () => {
                // This will trigger Dash callback to refresh data
                if (window.dash_clientside) {
                    window.dash_clientside.no_update = Symbol('no_update');
                }
            });
        }
    },

    initializeTooltips: function() {
        // Initialize Bootstrap tooltips if available
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            const tooltipTriggerList = [].slice.call(
                document.querySelectorAll('[data-bs-toggle="tooltip"]')
            );
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    },

    handlePropertyRowClick: function(event) {
        const propertyId = event.currentTarget.dataset.propertyId;
        if (propertyId) {
            window.location.href = `/properties/details/${propertyId}`;
        }
    },

    handleTransactionRowClick: function(event) {
        const transactionId = event.currentTarget.dataset.transactionId;
        if (transactionId) {
            window.location.href = `/transactions/details/${transactionId}`;
        }
    },

    updateTotalEquity: function() {
        const equityInputs = document.querySelectorAll('.equity-input');
        let totalLastMonthEquity = 0;
        let totalEquityGained = 0;

        equityInputs.forEach(input => {
            const value = parseFloat(input.value) || 0;
            const type = input.dataset.equityType;
            
            if (type === 'last-month') {
                totalLastMonthEquity += value;
            } else if (type === 'gained') {
                totalEquityGained += value;
            }
        });

        // Update total displays
        const lastMonthElement = document.getElementById('total-last-month-equity');
        const gainedElement = document.getElementById('total-equity-gained');

        if (lastMonthElement) {
            lastMonthElement.textContent = this.formatCurrency(totalLastMonthEquity);
        }
        if (gainedElement) {
            gainedElement.textContent = this.formatCurrency(totalEquityGained);
        }

        // Trigger Dash callback if needed
        this.triggerDashUpdate({
            lastMonthEquity: totalLastMonthEquity,
            equityGained: totalEquityGained
        });
    },

    triggerDashUpdate: function(data) {
        // This will trigger any Dash callbacks listening for data changes
        const event = new CustomEvent('dashboardDataUpdate', { detail: data });
        window.dispatchEvent(event);
    },

    formatCurrency: function(value) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(value);
    },

    // Helper method to safely parse numeric values
    parseNumericValue: function(value) {
        if (typeof value === 'string') {
            value = value.replace(/[^0-9.-]+/g, '');
        }
        const parsed = parseFloat(value);
        return isNaN(parsed) ? 0 : parsed;
    }
};

export default mainModule;