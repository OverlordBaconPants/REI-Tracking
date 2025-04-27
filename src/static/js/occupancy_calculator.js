/**
 * Occupancy Rate Calculator JavaScript Module
 * 
 * This module handles the occupancy rate calculator functionality,
 * including form submission, calculations, and results display.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get form and result elements
    const form = document.getElementById('occupancy-calculator-form');
    const resultsContainer = document.getElementById('results-container');
    const noResultsContainer = document.getElementById('no-results-container');
    const occupancyRateResult = document.getElementById('occupancy-rate-result');
    const occupancyAlert = document.getElementById('occupancy-alert');
    const occupancyStatusMessage = document.getElementById('occupancy-status-message');
    const potentialRevenueResult = document.getElementById('potential-revenue-result');
    const actualRevenueResult = document.getElementById('actual-revenue-result');
    const revenueGapResult = document.getElementById('revenue-gap-result');
    const unitsNeededResult = document.getElementById('units-needed-result');
    const breakevenOccupancyResult = document.getElementById('breakeven-occupancy-result');
    const netIncomeResult = document.getElementById('net-income-result');
    const marketOccupancyBar = document.getElementById('market-occupancy-bar');
    const currentOccupancyBar = document.getElementById('current-occupancy-bar');
    const printResultsButton = document.getElementById('print-results');
    
    // Get property selector and related fields
    const propertySelector = document.getElementById('property-selector');
    const propertyNameInput = document.getElementById('property-name');
    const totalUnitsInput = document.getElementById('total-units');
    const occupiedUnitsInput = document.getElementById('occupied-units');
    
    // Add event listeners
    form.addEventListener('submit', handleFormSubmit);
    propertySelector.addEventListener('change', handlePropertySelection);
    printResultsButton.addEventListener('click', printResults);
    
    /**
     * Handle property selection change
     */
    function handlePropertySelection() {
        const selectedPropertyId = propertySelector.value;
        
        if (selectedPropertyId) {
            // In a real implementation, this would fetch property data from the server
            // For now, we'll simulate it with placeholder logic
            fetchPropertyData(selectedPropertyId)
                .then(propertyData => {
                    if (propertyData) {
                        // Populate form fields with property data
                        propertyNameInput.value = propertyData.address || '';
                        totalUnitsInput.value = propertyData.total_units || '';
                        occupiedUnitsInput.value = propertyData.occupied_units || '';
                    }
                })
                .catch(error => {
                    console.error('Error fetching property data:', error);
                    if (window.Notifications) {
                        window.Notifications.showError('Error', 'Failed to load property data');
                    }
                });
        }
    }
    
    /**
     * Fetch property data from the server
     * @param {string} propertyId - Property ID
     * @returns {Promise} Promise resolving to property data
     */
    function fetchPropertyData(propertyId) {
        // In a real implementation, this would make an API call to get property data
        // For now, we'll return a placeholder Promise
        return new Promise((resolve) => {
            // Simulate API call delay
            setTimeout(() => {
                // This would normally come from the server
                resolve({
                    id: propertyId,
                    address: 'Sample Property',
                    total_units: 10,
                    occupied_units: 8
                });
            }, 300);
        });
    }
    
    /**
     * Handle form submission
     * @param {Event} e - Form submit event
     */
    function handleFormSubmit(e) {
        e.preventDefault();
        
        // Show loading state
        const submitButton = form.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.innerHTML;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Calculating...';
        submitButton.disabled = true;
        
        // Get form data
        const formData = getFormData();
        
        // Calculate occupancy metrics
        const results = calculateOccupancyMetrics(formData);
        
        // Display results
        displayResults(results);
        
        // Reset button state
        submitButton.innerHTML = originalButtonText;
        submitButton.disabled = false;
    }
    
    /**
     * Get form data as an object
     * @returns {Object} Form data object
     */
    function getFormData() {
        return {
            propertyName: propertyNameInput.value,
            totalUnits: parseInt(totalUnitsInput.value) || 0,
            occupiedUnits: parseInt(occupiedUnitsInput.value) || 0,
            averageRent: parseFloat(document.getElementById('average-rent').value) || 0,
            targetOccupancy: parseFloat(document.getElementById('target-occupancy').value) || 95,
            monthlyFixedExpenses: parseFloat(document.getElementById('monthly-fixed-expenses').value) || 0,
            variableExpensePerUnit: parseFloat(document.getElementById('variable-expense-per-unit').value) || 0,
            marketOccupancy: parseFloat(document.getElementById('market-occupancy').value) || 90
        };
    }
    
    /**
     * Calculate occupancy metrics
     * @param {Object} data - Form data
     * @returns {Object} Calculation results
     */
    function calculateOccupancyMetrics(data) {
        // Calculate occupancy rate
        const occupancyRate = data.totalUnits > 0 ? (data.occupiedUnits / data.totalUnits) * 100 : 0;
        
        // Calculate potential and actual revenue
        const potentialRevenue = data.totalUnits * data.averageRent;
        const actualRevenue = data.occupiedUnits * data.averageRent;
        const revenueGap = potentialRevenue - actualRevenue;
        
        // Calculate units needed to reach target occupancy
        const targetUnits = Math.ceil((data.targetOccupancy / 100) * data.totalUnits);
        const unitsNeeded = Math.max(0, targetUnits - data.occupiedUnits);
        
        // Calculate expenses
        const totalFixedExpenses = data.monthlyFixedExpenses;
        const totalVariableExpenses = data.occupiedUnits * data.variableExpensePerUnit;
        const totalExpenses = totalFixedExpenses + totalVariableExpenses;
        
        // Calculate net income
        const netIncome = actualRevenue - totalExpenses;
        
        // Calculate breakeven occupancy
        let breakevenOccupancy = 0;
        if (data.averageRent > 0 && data.totalUnits > 0) {
            const breakevenRevenue = totalFixedExpenses;
            const revenuePerUnitAfterVariableExpenses = data.averageRent - data.variableExpensePerUnit;
            
            if (revenuePerUnitAfterVariableExpenses > 0) {
                const breakevenUnits = breakevenRevenue / revenuePerUnitAfterVariableExpenses;
                breakevenOccupancy = (breakevenUnits / data.totalUnits) * 100;
            } else {
                // If variable expenses exceed rent, can't break even
                breakevenOccupancy = 100;
            }
        }
        
        // Determine occupancy status
        let occupancyStatus = '';
        let alertClass = '';
        
        if (occupancyRate >= data.targetOccupancy) {
            occupancyStatus = 'Excellent! Your occupancy rate exceeds your target.';
            alertClass = 'alert-success';
        } else if (occupancyRate >= data.marketOccupancy) {
            occupancyStatus = 'Good. Your occupancy rate is above market average but below your target.';
            alertClass = 'alert-info';
        } else if (occupancyRate >= breakevenOccupancy) {
            occupancyStatus = 'Fair. Your occupancy rate is below market average but above breakeven.';
            alertClass = 'alert-warning';
        } else {
            occupancyStatus = 'Critical. Your occupancy rate is below the breakeven point.';
            alertClass = 'alert-danger';
        }
        
        return {
            occupancyRate,
            potentialRevenue,
            actualRevenue,
            revenueGap,
            unitsNeeded,
            breakevenOccupancy,
            netIncome,
            occupancyStatus,
            alertClass,
            marketOccupancy: data.marketOccupancy
        };
    }
    
    /**
     * Display calculation results
     * @param {Object} results - Calculation results
     */
    function displayResults(results) {
        // Update result elements
        occupancyRateResult.textContent = formatPercentage(results.occupancyRate);
        occupancyStatusMessage.textContent = results.occupancyStatus;
        occupancyAlert.className = `alert ${results.alertClass} mb-4`;
        
        potentialRevenueResult.textContent = formatCurrency(results.potentialRevenue);
        actualRevenueResult.textContent = formatCurrency(results.actualRevenue);
        revenueGapResult.textContent = formatCurrency(results.revenueGap);
        unitsNeededResult.textContent = results.unitsNeeded;
        breakevenOccupancyResult.textContent = formatPercentage(results.breakevenOccupancy);
        netIncomeResult.textContent = formatCurrency(results.netIncome);
        
        // Update progress bars
        marketOccupancyBar.style.width = `${results.marketOccupancy}%`;
        marketOccupancyBar.setAttribute('aria-valuenow', results.marketOccupancy);
        marketOccupancyBar.textContent = formatPercentage(results.marketOccupancy);
        
        currentOccupancyBar.style.width = `${results.occupancyRate}%`;
        currentOccupancyBar.setAttribute('aria-valuenow', results.occupancyRate);
        currentOccupancyBar.textContent = formatPercentage(results.occupancyRate);
        
        // Set progress bar color based on status
        if (results.alertClass === 'alert-success') {
            currentOccupancyBar.className = 'progress-bar bg-success';
        } else if (results.alertClass === 'alert-info') {
            currentOccupancyBar.className = 'progress-bar bg-info';
        } else if (results.alertClass === 'alert-warning') {
            currentOccupancyBar.className = 'progress-bar bg-warning';
        } else {
            currentOccupancyBar.className = 'progress-bar bg-danger';
        }
        
        // Show results
        resultsContainer.style.display = 'block';
        noResultsContainer.style.display = 'none';
    }
    
    /**
     * Print results
     */
    function printResults() {
        window.print();
    }
    
    /**
     * Format a number as currency
     * @param {number} value - Number to format
     * @returns {string} Formatted currency string
     */
    function formatCurrency(value) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(value);
    }
    
    /**
     * Format a number as percentage
     * @param {number} value - Number to format
     * @returns {string} Formatted percentage string
     */
    function formatPercentage(value) {
        return new Intl.NumberFormat('en-US', {
            style: 'percent',
            minimumFractionDigits: 1,
            maximumFractionDigits: 1
        }).format(value / 100);
    }
});
