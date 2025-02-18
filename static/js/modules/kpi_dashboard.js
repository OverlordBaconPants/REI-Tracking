// /static/js/modules/kpi_dashboard.js

const kpiDashboardModule = {
    init: function() {
        this.setupEventListeners();
        this.initializePropertySelector();
    },
    
    setupEventListeners: function() {
        const propertySelector = document.getElementById('property-selector');
        if (propertySelector) {
            propertySelector.addEventListener('change', (e) => {
                const propertyId = e.target.value;
                this.displayKPIs(propertyId);
            });
        }
    },

    initializePropertySelector: function() {
        const selector = document.getElementById('property-selector');
        if (!selector) return;
        
        // Clear existing options
        selector.innerHTML = '<option value="">Select Property</option>';
        
        // Add properties
        if (window.propertyData) {
            Object.keys(window.propertyData).forEach(propertyId => {
                const option = document.createElement('option');
                option.value = propertyId;
                // Truncate the address to just show house number and street
                const shortAddress = propertyId.split(',')[0];
                option.textContent = shortAddress;
                selector.appendChild(option);
            });
        }
    },
    
    initializeAnalysisSelector: function() {
        const selector = document.getElementById('analysis-selector');
        if (!selector) return;
        
        // Clear existing options
        selector.innerHTML = '<option value="">Select Analysis for Comparison</option>';
        
        console.log("Property data:", window.propertyData); // Debug line
        
        // Add available analyses
        if (window.propertyData && 
            window.propertyData.metadata && 
            Array.isArray(window.propertyData.metadata.available_analyses)) {
            
            console.log("Available analyses:", window.propertyData.metadata.available_analyses); // Debug line
            
            window.propertyData.metadata.available_analyses.forEach(analysis => {
                const option = document.createElement('option');
                option.value = analysis.filename;
                option.textContent = `${analysis.analysis_type} - ${new Date(analysis.date).toLocaleDateString()}`;
                selector.appendChild(option);
            });
        }
    },

    displayKPIs: function(propertyId) {
        if (!propertyId || !window.propertyData || !window.propertyData[propertyId]) {
            this.clearKPIs();
            return;
        }

        const propertyData = window.propertyData[propertyId];
        
        // Display YTD KPIs
        if (propertyData.year_to_date) {
            this.updateKPIValue('noi-ytd', propertyData.year_to_date.net_operating_income.monthly, 'currency');
            this.updateKPIValue('cap-rate-ytd', propertyData.year_to_date.cap_rate, 'percentage');
            this.updateKPIValue('coc-ytd', propertyData.year_to_date.cash_on_cash_return, 'percentage');
            this.updateKPIValue('dscr-ytd', propertyData.year_to_date.debt_service_coverage_ratio, 'ratio');
        }

        // Display Since Acquisition KPIs
        if (propertyData.since_acquisition) {
            this.updateKPIValue('noi-acquisition', propertyData.since_acquisition.net_operating_income.monthly, 'currency');
            this.updateKPIValue('cap-rate-acquisition', propertyData.since_acquisition.cap_rate, 'percentage');
            this.updateKPIValue('coc-acquisition', propertyData.since_acquisition.cash_on_cash_return, 'percentage');
            this.updateKPIValue('dscr-acquisition', propertyData.since_acquisition.debt_service_coverage_ratio, 'ratio');
        }

        // Update data quality information
        this.updateDataQualityInfo(propertyData);
    },

    displayProjectedKPIs: function(propertyId, analysisId) {
        if (!propertyId || !analysisId || !window.propertyData[propertyId]) {
            this.clearProjectedKPIs();
            return;
        }

        const propertyData = window.propertyData[propertyId];
        if (propertyData.analysis_comparison && propertyData.analysis_comparison[analysisId]) {
            const projected = propertyData.analysis_comparison[analysisId];
            this.updateKPIValue('noi-projected', projected.net_operating_income.monthly, 'currency');
            this.updateKPIValue('cap-rate-projected', projected.cap_rate, 'percentage');
            this.updateKPIValue('coc-projected', projected.cash_on_cash_return, 'percentage');
            this.updateKPIValue('dscr-projected', projected.debt_service_coverage_ratio, 'ratio');
        }
    },

    clearKPIs: function() {
        const kpiIds = ['noi', 'cap-rate', 'coc', 'dscr'];
        const periods = ['ytd', 'acquisition'];
        
        kpiIds.forEach(kpi => {
            periods.forEach(period => {
                this.updateKPIValue(`${kpi}-${period}`, null, '');
            });
        });
    },

    clearProjectedKPIs: function() {
        const projectedElements = document.querySelectorAll('[id$="-projected"]');
        projectedElements.forEach(element => {
            element.style.display = 'none';
        });
    },

    updateAnalysisSelector: function(propertyId) {
        const selector = document.getElementById('analysis-selector');
        if (!selector) return;
        
        // Clear existing options
        selector.innerHTML = '<option value="">Select Analysis for Comparison</option>';
        
        // Add available analyses for the selected property
        if (window.propertyData && propertyId && window.propertyData[propertyId]) {
            const propertyData = window.propertyData[propertyId];
            console.log("Property data for", propertyId, ":", propertyData); // Debug line
            
            if (propertyData.metadata && Array.isArray(propertyData.metadata.available_analyses)) {
                console.log("Available analyses:", propertyData.metadata.available_analyses); // Debug line
                
                propertyData.metadata.available_analyses.forEach(analysis => {
                    const option = document.createElement('option');
                    option.value = analysis.filename;
                    option.textContent = `${analysis.analysis_type} - ${new Date(analysis.date).toLocaleDateString()}`;
                    selector.appendChild(option);
                });
            }
        }
    },
    
    updateKPIs: function(data) {
        if (!data) return;
        
        // Update YTD values
        this.updateKPIValue('noi-ytd', data.year_to_date.net_operating_income.monthly, 'currency');
        this.updateKPIValue('cap-rate-ytd', data.year_to_date.cap_rate, 'percentage');
        this.updateKPIValue('coc-ytd', data.year_to_date.cash_on_cash_return, 'percentage');
        this.updateKPIValue('dscr-ytd', data.year_to_date.debt_service_coverage_ratio, 'ratio');
        
        // Update Since Acquisition values
        this.updateKPIValue('noi-acquisition', data.since_acquisition.net_operating_income.monthly, 'currency');
        this.updateKPIValue('cap-rate-acquisition', data.since_acquisition.cap_rate, 'percentage');
        this.updateKPIValue('coc-acquisition', data.since_acquisition.cash_on_cash_return, 'percentage');
        this.updateKPIValue('dscr-acquisition', data.since_acquisition.debt_service_coverage_ratio, 'ratio');
        
        // Update data quality information
        this.updateDataQualityInfo(data);
        
        // Clear projected values
        this.clearProjectedValues();
    },
    
    updateKPIValue: function(elementId, value, format) {
        const element = document.getElementById(elementId);
        if (!element) {
            console.log(`Element not found: ${elementId}`);
            return;
        }
        
        const valueSpan = element.querySelector('.value');
        if (!valueSpan) {
            console.log(`Value span not found in element: ${elementId}`);
            return;
        }
        
        console.log(`Updating KPI ${elementId}:`, {
            value: value,
            type: typeof value,
            isNull: value === null,
            isUndefined: value === undefined,
            isNaN: isNaN(value)
        });
        
        if (value === null || value === undefined || isNaN(value)) {
            console.log(`Setting ${elementId} to N/A due to invalid value`);
            valueSpan.textContent = 'N/A';
            return;
        }
        
        let formattedValue;
        switch (format) {
            case 'currency':
                formattedValue = new Intl.NumberFormat('en-US', {
                    style: 'currency',
                    currency: 'USD'
                }).format(value);
                break;
            case 'percentage':
                formattedValue = `${value.toFixed(2)}%`;
                break;
            case 'ratio':
                formattedValue = value.toFixed(2);
                break;
            default:
                formattedValue = value.toString();
        }
        
        console.log(`Formatted value for ${elementId}: ${formattedValue}`);
        valueSpan.textContent = formattedValue;
    },
    
    updateDataQualityInfo: function(propertyData) {
        const alert = document.getElementById('data-quality-alert');
        const message = document.getElementById('data-quality-message');
        if (!alert || !message) return;
        
        // Check if we have metadata
        if (!propertyData || !propertyData.metadata) {
            alert.className = 'alert alert-warning';
            message.textContent = 'No data quality information available.';
            return;
        }

        const quality = propertyData.metadata;
        let messageText = '';
        
        if (quality.has_complete_history) {
            alert.className = 'alert alert-success';
            messageText = 'Complete transaction history available for accurate KPI calculation.';
        } else {
            alert.className = 'alert alert-warning';
            messageText = 'Incomplete transaction history may affect KPI accuracy. Some values may be marked as N/A.';
        }
        
        message.textContent = messageText;
    },
    
    updateProjectedValues: function(analysisId) {
        if (!analysisId) {
            this.clearProjectedValues();
            return;
        }
        
        // Show projected value containers
        ['noi', 'cap-rate', 'coc', 'dscr'].forEach(kpi => {
            const container = document.getElementById(`${kpi}-projected`);
            if (container) container.style.display = 'block';
        });
        
        // Update projected values if analysis comparison exists
        if (window.propertyData && window.propertyData.analysis_comparison) {
            const projected = window.propertyData.analysis_comparison.projected;
            
            this.updateKPIValue('noi-projected', projected.net_operating_income.monthly, 'currency');
            this.updateKPIValue('cap-rate-projected', projected.cap_rate, 'percentage');
            this.updateKPIValue('coc-projected', projected.cash_on_cash_return, 'percentage');
            this.updateKPIValue('dscr-projected', projected.debt_service_coverage_ratio, 'ratio');
        }
    },
    
    clearProjectedValues: function() {
        ['noi', 'cap-rate', 'coc', 'dscr'].forEach(kpi => {
            const container = document.getElementById(`${kpi}-projected`);
            if (container) container.style.display = 'none';
        });
    }
};

export default kpiDashboardModule;