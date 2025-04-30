const dashboardsModule = {
    init: async function() {
        console.log('Initializing dashboards module');
        try {
            await this.loadPropertyData();
            this.initializeCharts();
            this.setupEventListeners();
            window.showNotification('Dashboard initialized successfully', 'success');
        } catch (error) {
            console.error('Error initializing dashboard:', error);
            window.showNotification('Error initializing dashboard', 'error');
        }
    },

    loadPropertyData: async function() {
        try {
            const response = await fetch('/api/properties');
            if (!response.ok) {
                throw new Error('Failed to fetch property data');
            }
            this.propertyData = await response.json();
            logger.debug(`Loaded ${this.propertyData.length} properties`);
        } catch (error) {
            console.error('Error loading property data:', error);
            throw error;
        }
    },

    calculateTotalExpenses: function(expenses) {
        if (!expenses) return 0;
        
        const fixedExpenses = [
            'property_tax',
            'insurance',
            'repairs',
            'capex',
            'property_management',
            'hoa_fees',
            'other_expenses'
        ].reduce((sum, key) => sum + (expenses[key] || 0), 0);
        
        const utilities = Object.values(expenses.utilities || {})
            .reduce((sum, val) => sum + (val || 0), 0);
            
        return fixedExpenses + utilities;
    },

    initializeCharts: function() {
        if (!this.propertyData) return;
        
        // Initialize charts
        this.charts = [];
        this.initEquityChart();
        this.initCashFlowChart();
        this.initIncomeChart();
        this.initExpensesChart();
    },

    setupEventListeners: function() {
        // Add responsive design handlers
        window.addEventListener('resize', () => {
            this.updateChartsResponsiveness();
        });
        
        // Add other event listeners as needed
    },

    updateChartsResponsiveness: function() {
        const isMobile = window.innerWidth < 768;
        // Update chart layouts for mobile/desktop
        if (this.charts && this.charts.length) {
            this.charts.forEach(chart => {
                chart.updateLayout({
                    height: isMobile ? 300 : 400,
                    legend: {
                        orientation: isMobile ? 'h' : 'v',
                        y: isMobile ? -0.5 : 0.5
                    }
                });
            });
        }
    }
};

export default dashboardsModule;