/**
 * MAO Calculator JavaScript Module
 * 
 * This module handles the MAO (Maximum Allowable Offer) calculator functionality,
 * including form submission, API interaction, and results display.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get form and result elements
    const form = document.getElementById('mao-calculator-form');
    const resultsContainer = document.getElementById('results-container');
    const noResultsContainer = document.getElementById('no-results-container');
    const maoResult = document.getElementById('mao-result');
    const monthlyCashFlowResult = document.getElementById('monthly-cash-flow-result');
    const cashOnCashReturnResult = document.getElementById('cash-on-cash-return-result');
    const capRateResult = document.getElementById('cap-rate-result');
    const totalInvestmentResult = document.getElementById('total-investment-result');
    const calculationBreakdown = document.getElementById('calculation-breakdown');
    const printResultsButton = document.getElementById('print-results');
    
    // Get strategy-specific elements
    const analysisTypeSelect = document.getElementById('analysis-type');
    const brrrFields = document.getElementById('brrrr-fields');
    const ltrFields = document.getElementById('ltr-fields');
    const brrrResults = document.getElementById('brrrr-results');
    const refinanceLoanAmountResult = document.getElementById('refinance-loan-amount-result');
    const cashLeftInDealResult = document.getElementById('cash-left-in-deal-result');
    
    // Get loan term toggle button
    const loanTermToggle = document.querySelector('.loan-term-toggle');
    const loanTermInput = document.getElementById('loan-term');
    
    // Initialize loan term toggle
    initLoanTermToggle();
    
    // Add event listeners
    analysisTypeSelect.addEventListener('change', handleAnalysisTypeChange);
    form.addEventListener('submit', handleFormSubmit);
    printResultsButton.addEventListener('click', printResults);
    
    /**
     * Initialize the loan term toggle functionality
     */
    function initLoanTermToggle() {
        loanTermToggle.addEventListener('click', function() {
            const currentType = this.getAttribute('data-term-type');
            const currentValue = parseInt(loanTermInput.value) || 0;
            
            if (currentType === 'years') {
                // Convert years to months
                loanTermInput.value = currentValue * 12;
                this.setAttribute('data-term-type', 'months');
                this.textContent = 'Months';
            } else {
                // Convert months to years
                loanTermInput.value = Math.round(currentValue / 12);
                this.setAttribute('data-term-type', 'years');
                this.textContent = 'Years';
            }
        });
    }
    
    /**
     * Handle analysis type change to show/hide relevant fields
     */
    function handleAnalysisTypeChange() {
        const analysisType = analysisTypeSelect.value;
        
        // Hide all strategy-specific fields
        document.querySelectorAll('.strategy-fields').forEach(el => {
            el.style.display = 'none';
        });
        
        // Show fields based on selected strategy
        if (analysisType === 'BRRRR') {
            brrrFields.style.display = 'block';
        } else if (analysisType === 'LTR') {
            ltrFields.style.display = 'block';
        }
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
        
        // Call API to calculate MAO
        calculateMAO(formData)
            .then(displayResults)
            .catch(handleError)
            .finally(() => {
                // Reset button state
                submitButton.innerHTML = originalButtonText;
                submitButton.disabled = false;
            });
    }
    
    /**
     * Get form data as an object
     * @returns {Object} Form data object
     */
    function getFormData() {
        const analysisType = analysisTypeSelect.value;
        
        // Common fields
        const data = {
            analysis_type: analysisType,
            analysis_name: `MAO Calculation - ${new Date().toLocaleString()}`,
            address: document.getElementById('address').value,
            monthly_rent: parseFloat(document.getElementById('monthly-rent').value) || 0,
            property_taxes: parseFloat(document.getElementById('property-taxes').value) || 0,
            insurance: parseFloat(document.getElementById('insurance').value) || 0,
            closing_costs: parseFloat(document.getElementById('closing-costs').value) || 0,
            management_fee_percentage: parseFloat(document.getElementById('management-fee-percentage').value) || 0,
            vacancy_percentage: parseFloat(document.getElementById('vacancy-percentage').value) || 0,
            repairs_percentage: parseFloat(document.getElementById('repairs-percentage').value) || 0,
            capex_percentage: parseFloat(document.getElementById('capex-percentage').value) || 0
        };
        
        // Loan details
        const loanAmount = parseFloat(document.getElementById('loan-amount').value) || 0;
        const loanInterestRate = parseFloat(document.getElementById('loan-interest-rate').value) || 0;
        const loanTerm = parseInt(document.getElementById('loan-term').value) || 0;
        const isInterestOnly = document.getElementById('is-interest-only').checked;
        const termType = document.querySelector('.loan-term-toggle').getAttribute('data-term-type');
        
        // Convert loan term to months if in years
        const loanTermMonths = termType === 'years' ? loanTerm * 12 : loanTerm;
        
        if (loanAmount > 0) {
            data.initial_loan_amount = loanAmount;
            data.initial_loan_interest_rate = loanInterestRate;
            data.initial_loan_term = loanTermMonths;
            data.initial_loan_is_interest_only = isInterestOnly;
        }
        
        // Strategy-specific fields
        if (analysisType === 'BRRRR') {
            data.after_repair_value = parseFloat(document.getElementById('after-repair-value').value) || 0;
            data.renovation_costs = parseFloat(document.getElementById('renovation-costs').value) || 0;
            data.renovation_duration = parseInt(document.getElementById('renovation-duration').value) || 0;
            data.refinance_ltv_percentage = parseFloat(document.getElementById('refinance-ltv-percentage').value) || 75;
        } else if (analysisType === 'LTR') {
            data.target_monthly_cash_flow = parseFloat(document.getElementById('target-monthly-cash-flow').value) || 200;
            data.target_cap_rate = parseFloat(document.getElementById('target-cap-rate').value) || 8;
        }
        
        return data;
    }
    
    /**
     * Calculate MAO using the analysis API
     * @param {Object} data - Form data
     * @returns {Promise} Promise resolving to the calculation results
     */
    function calculateMAO(data) {
        return fetch('/api/analysis/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(responseData => {
            if (!responseData.success) {
                throw new Error(responseData.message || 'Error calculating MAO');
            }
            
            // Create a calculator object to calculate MAO
            return calculateMAOFromMetrics(data, responseData.metrics);
        });
    }
    
    /**
     * Calculate MAO from metrics based on analysis type
     * @param {Object} data - Form data
     * @param {Object} metrics - Calculated metrics from API
     * @returns {Object} MAO calculation results
     */
    function calculateMAOFromMetrics(data, metrics) {
        const analysisType = data.analysis_type;
        let mao = 0;
        let calculationSteps = [];
        
        if (analysisType === 'BRRRR') {
            // BRRRR MAO calculation
            const arv = data.after_repair_value;
            const renovationCosts = data.renovation_costs;
            const closingCosts = data.closing_costs || 0;
            const refinanceLtv = data.refinance_ltv_percentage / 100;
            const maxCashLeft = 10000; // Default $10k max cash left in deal
            
            // Calculate holding costs
            const monthlyHoldingCosts = (data.property_taxes / 12) + (data.insurance / 12);
            const holdingCosts = monthlyHoldingCosts * data.renovation_duration;
            
            // Calculate loan amount based on ARV and LTV
            const loanAmount = arv * refinanceLtv;
            
            // Calculate MAO
            mao = loanAmount - renovationCosts - closingCosts - holdingCosts + maxCashLeft;
            mao = Math.max(0, mao);
            
            // Calculate cash left in deal
            const cashLeftInDeal = renovationCosts + closingCosts + holdingCosts + mao - loanAmount;
            
            // Record calculation steps
            calculationSteps = [
                { label: 'After Repair Value (ARV)', value: formatCurrency(arv) },
                { label: 'Refinance Loan-to-Value (LTV)', value: `${data.refinance_ltv_percentage}%` },
                { label: 'Refinance Loan Amount', value: formatCurrency(loanAmount) },
                { label: 'Renovation Costs', value: formatCurrency(renovationCosts) },
                { label: 'Closing Costs', value: formatCurrency(closingCosts) },
                { label: 'Holding Costs', value: formatCurrency(holdingCosts) },
                { label: 'Max Cash Left in Deal', value: formatCurrency(maxCashLeft) },
                { label: 'MAO Calculation', value: `${formatCurrency(loanAmount)} - ${formatCurrency(renovationCosts)} - ${formatCurrency(closingCosts)} - ${formatCurrency(holdingCosts)} + ${formatCurrency(maxCashLeft)}` },
                { label: 'Maximum Allowable Offer (MAO)', value: formatCurrency(mao) },
                { label: 'Actual Cash Left in Deal', value: formatCurrency(cashLeftInDeal) }
            ];
            
            // Add BRRRR-specific results
            metrics.refinanceLoanAmount = loanAmount;
            metrics.cashLeftInDeal = cashLeftInDeal;
        } else if (analysisType === 'LTR') {
            // LTR MAO calculation
            const targetMonthlyCashFlow = data.target_monthly_cash_flow;
            const targetCapRate = data.target_cap_rate / 100;
            
            // Calculate based on cap rate
            const monthlyNOI = metrics.monthly_income - metrics.monthly_expenses;
            const annualNOI = monthlyNOI * 12;
            const capRateMAO = annualNOI / targetCapRate;
            
            // Calculate based on cash flow
            const loanPaymentPer100k = 500; // Approximate monthly payment per $100k at current rates
            const supportablePayment = monthlyNOI - targetMonthlyCashFlow;
            const supportableLoan = (supportablePayment / loanPaymentPer100k) * 100000;
            const cashFlowMAO = supportableLoan / 0.8; // Assume 80% LTV
            
            // Take the lower of the two MAOs
            mao = Math.min(capRateMAO, cashFlowMAO);
            mao = Math.max(0, mao);
            
            // Record calculation steps
            calculationSteps = [
                { label: 'Monthly Income', value: formatCurrency(metrics.monthly_income) },
                { label: 'Monthly Expenses', value: formatCurrency(metrics.monthly_expenses) },
                { label: 'Monthly NOI', value: formatCurrency(monthlyNOI) },
                { label: 'Annual NOI', value: formatCurrency(annualNOI) },
                { label: 'Target Cap Rate', value: `${data.target_cap_rate}%` },
                { label: 'Cap Rate MAO Calculation', value: `${formatCurrency(annualNOI)} ÷ ${data.target_cap_rate}%` },
                { label: 'Cap Rate MAO', value: formatCurrency(capRateMAO) },
                { label: 'Target Monthly Cash Flow', value: formatCurrency(targetMonthlyCashFlow) },
                { label: 'Supportable Payment', value: formatCurrency(supportablePayment) },
                { label: 'Supportable Loan', value: formatCurrency(supportableLoan) },
                { label: 'Cash Flow MAO (80% LTV)', value: formatCurrency(cashFlowMAO) },
                { label: 'Maximum Allowable Offer (MAO)', value: formatCurrency(mao) }
            ];
        } else {
            // Default MAO calculation for other strategies
            // For now, just use a simple cap rate calculation
            const monthlyNOI = metrics.monthly_income - metrics.monthly_expenses;
            const annualNOI = monthlyNOI * 12;
            const targetCapRate = 0.08; // Default 8% cap rate
            
            mao = annualNOI / targetCapRate;
            
            // Record calculation steps
            calculationSteps = [
                { label: 'Monthly Income', value: formatCurrency(metrics.monthly_income) },
                { label: 'Monthly Expenses', value: formatCurrency(metrics.monthly_expenses) },
                { label: 'Monthly NOI', value: formatCurrency(monthlyNOI) },
                { label: 'Annual NOI', value: formatCurrency(annualNOI) },
                { label: 'Target Cap Rate', value: '8%' },
                { label: 'MAO Calculation', value: `${formatCurrency(annualNOI)} ÷ 8%` },
                { label: 'Maximum Allowable Offer (MAO)', value: formatCurrency(mao) }
            ];
        }
        
        // Return results
        return {
            mao: mao,
            metrics: metrics,
            calculationSteps: calculationSteps
        };
    }
    
    /**
     * Display calculation results
     * @param {Object} results - Calculation results
     */
    function displayResults(results) {
        // Update result elements
        maoResult.textContent = formatCurrency(results.mao);
        monthlyCashFlowResult.textContent = formatCurrency(results.metrics.monthly_cash_flow);
        cashOnCashReturnResult.textContent = formatPercentage(results.metrics.cash_on_cash_return);
        capRateResult.textContent = formatPercentage(results.metrics.cap_rate);
        totalInvestmentResult.textContent = formatCurrency(results.metrics.total_investment);
        
        // Show/hide strategy-specific results
        const analysisType = analysisTypeSelect.value;
        document.querySelectorAll('.strategy-results').forEach(el => {
            el.style.display = 'none';
        });
        
        if (analysisType === 'BRRRR') {
            brrrResults.style.display = 'block';
            refinanceLoanAmountResult.textContent = formatCurrency(results.metrics.refinanceLoanAmount);
            cashLeftInDealResult.textContent = formatCurrency(results.metrics.cashLeftInDeal);
        }
        
        // Build calculation breakdown
        calculationBreakdown.innerHTML = '';
        results.calculationSteps.forEach(step => {
            const row = document.createElement('tr');
            const labelCell = document.createElement('td');
            const valueCell = document.createElement('td');
            
            labelCell.textContent = step.label;
            valueCell.textContent = step.value;
            valueCell.classList.add('text-end');
            
            row.appendChild(labelCell);
            row.appendChild(valueCell);
            calculationBreakdown.appendChild(row);
        });
        
        // Show results
        resultsContainer.style.display = 'block';
        noResultsContainer.style.display = 'none';
    }
    
    /**
     * Handle calculation error
     * @param {Error} error - Error object
     */
    function handleError(error) {
        console.error('Error calculating MAO:', error);
        
        // Show error notification
        if (window.Notifications) {
            window.Notifications.showError('Error calculating MAO', error.message);
        } else {
            alert(`Error calculating MAO: ${error.message}`);
        }
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
