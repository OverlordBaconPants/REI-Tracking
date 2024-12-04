const maoCalculator = {
    init: function() {
        console.log('Initializing calculator...');
        // Instead of looking for a specific form, attach listeners to all inputs
        const inputs = document.querySelectorAll('input[type="number"]');
        console.log(`Found ${inputs.length} number inputs`);
        
        inputs.forEach(input => {
            input.addEventListener('input', () => {
                console.log(`Input changed: ${input.id}`);
                this.updateCalculations();
            });
            input.addEventListener('change', () => {
                console.log(`Input changed (change event): ${input.id}`);
                this.updateCalculations();
            });
        });

        // Initial calculation
        this.updateCalculations();
    },

    formatCurrency: function(value) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(value);
    },

    calculateAcqRenoLoan: function(arv, renovationCosts) {
        return Math.round(renovationCosts + (arv * 0.75));
    },

    calculateMonthlyInterestOnly: function(loanAmount, annualRate) {
        return loanAmount * (annualRate / 100 / 12);
    },

    updateCalculations: function() {
        console.log('Updating calculations...');
        
        // Get all values and log them
        const values = {
            arv: parseFloat(document.getElementById('after_repair_value').value) || 0,
            renovationCosts: parseFloat(document.getElementById('renovation_costs').value) || 0,
            maxCashLeft: parseFloat(document.getElementById('max_cash_left').value) || 0,
            closingCosts: parseFloat(document.getElementById('closing_costs').value) || 0,
            renovationDuration: parseFloat(document.getElementById('renovation_duration').value) || 0,
            timeToRefinance: parseFloat(document.getElementById('time_to_refinance').value) || 0,
            utilities: parseFloat(document.getElementById('utilities').value) || 0,
            hoaCoa: parseFloat(document.getElementById('hoa_coa').value) || 0,
            maintenance: parseFloat(document.getElementById('maintenance').value) || 0,
            expectedLtv: parseFloat(document.getElementById('expected_ltv').value) || 75,
            acqRenoRate: parseFloat(document.getElementById('acq_reno_rate').value) || 12
        };
        
        console.log('Current values:', values);

        // Calculate Acquisition/Renovation Loan Amount
        const acqRenoLoan = this.calculateAcqRenoLoan(values.arv, values.renovationCosts);
        console.log('Calculated acqRenoLoan:', acqRenoLoan);
        
        // Update the loan amount field
        const acqRenoLoanEl = document.getElementById('acq_reno_loan');
        if (acqRenoLoanEl) {
            acqRenoLoanEl.value = acqRenoLoan.toFixed(2);
        }

        // Calculate Monthly Costs
        const monthlyLoanPayment = this.calculateMonthlyInterestOnly(acqRenoLoan, values.acqRenoRate);
        const monthlyExpenses = values.utilities + values.hoaCoa + values.maintenance;
        const totalMonthlyHoldingCosts = monthlyLoanPayment + monthlyExpenses;

        // Calculate Total Duration
        const totalMonths = values.renovationDuration + values.timeToRefinance;

        // Calculate MAO
        const expectedValue = values.arv * (values.expectedLtv / 100);
        const totalHoldingCosts = totalMonthlyHoldingCosts * totalMonths;
        const mao = expectedValue - totalHoldingCosts - values.closingCosts - values.maxCashLeft;

        console.log('Calculated values:', {
            monthlyLoanPayment,
            totalMonthlyHoldingCosts,
            totalHoldingCosts,
            mao
        });

        // Update results
        const updateElement = (id, value) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = this.formatCurrency(value);
            } else {
                console.warn(`Element with id ${id} not found`);
            }
        };

        updateElement('mao_result', mao);
        updateElement('monthly_loan_payment', monthlyLoanPayment);
        updateElement('monthly_holding_costs', totalMonthlyHoldingCosts);
        updateElement('total_holding_costs', totalHoldingCosts);
    }
};

// Make sure DOM is loaded before initializing
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('DOM loaded, initializing calculator...');
        maoCalculator.init();
    });
} else {
    console.log('DOM already loaded, initializing calculator...');
    maoCalculator.init();
}

export default maoCalculator;