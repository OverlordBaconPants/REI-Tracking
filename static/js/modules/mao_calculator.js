const maoCalculator = {
    init: function() {
        const inputs = document.querySelectorAll('input[type="number"]');
        inputs.forEach(input => {
            input.addEventListener('input', () => this.updateCalculations());
            input.addEventListener('change', () => this.updateCalculations());
        });

        // Add specific listeners for ARV and renovation costs
        ['after_repair_value', 'renovation_costs'].forEach(id => {
            document.getElementById(id)?.addEventListener('input', () => this.updateSuggestedLoanAmount());
        });

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

    calculateMonthlyInterestOnly: function(loanAmount, annualRate) {
        return loanAmount * (annualRate / 100 / 12);
    },

    calculateMonthlyHoldingCosts: function(loanAmount, annualRate, utilities, hoaCoa, maintenance) {
        const monthlyLoanPayment = this.calculateMonthlyInterestOnly(loanAmount, annualRate);
        return monthlyLoanPayment + utilities + hoaCoa + maintenance;
    },

    calculateAcquisitionLoanAmount: function(arv, renovationCosts) {
        // Calculate as 60% of ARV plus renovation costs
        return (arv * 0.60) + renovationCosts;
    },

    calculateMAO: function(arv, ltv, renovationCosts, closingCosts, monthlyHoldingCosts, totalHoldingMonths, maxCashLeft) {
        // Calculate loan amount based on LTV
        const loanAmount = arv * (ltv / 100);
        
        // Calculate total holding costs based on total holding months
        const totalHoldingCosts = monthlyHoldingCosts * totalHoldingMonths;
        
        // Calculate base MAO
        let mao = loanAmount - renovationCosts - closingCosts - totalHoldingCosts;
        
        // Simply add maxCashLeft to MAO since this represents additional cash willing to be left in deal
        mao += maxCashLeft;
        
        return Math.max(0, mao);
    },

    updateSuggestedLoanAmount: function() {
        const arv = parseFloat(document.getElementById('after_repair_value').value) || 0;
        const renovationCosts = parseFloat(document.getElementById('renovation_costs').value) || 0;
        const suggestedAmount = this.calculateAcquisitionLoanAmount(arv, renovationCosts);
        
        const acquisitionLoanInput = document.getElementById('acquisition_loan_amount');
        // Only update if the field hasn't been manually edited
        if (!acquisitionLoanInput.dataset.userEdited) {
            acquisitionLoanInput.value = suggestedAmount.toFixed(2);
        }
    },

    updateCalculations: function() {
        const values = {
            arv: parseFloat(document.getElementById('after_repair_value').value) || 0,
            renovationCosts: parseFloat(document.getElementById('renovation_costs').value) || 0,
            closingCosts: parseFloat(document.getElementById('closing_costs').value) || 0,
            timeToRefinance: parseFloat(document.getElementById('time_to_refinance').value) || 0,
            renovationDuration: parseFloat(document.getElementById('renovation_duration').value) || 0,
            expectedLtv: parseFloat(document.getElementById('expected_ltv').value) || 75,
            utilities: parseFloat(document.getElementById('utilities').value) || 0,
            hoaCoa: parseFloat(document.getElementById('hoa_coa').value) || 0,
            maintenance: parseFloat(document.getElementById('maintenance').value) || 0,
            acqRenoRate: parseFloat(document.getElementById('acq_reno_rate').value) || 12,
            maxCashLeft: parseFloat(document.getElementById('max_cash_left').value) || 0
        };

        // Update suggested loan amount
        this.updateSuggestedLoanAmount();

        // Get actual loan amount from input
        const acquisitionLoanAmount = parseFloat(document.getElementById('acquisition_loan_amount').value) || 0;

        const monthlyHoldingCosts = this.calculateMonthlyHoldingCosts(
            acquisitionLoanAmount,
            values.acqRenoRate,
            values.utilities,
            values.hoaCoa,
            values.maintenance
        );

        // Total holding months is sum of renovation duration and time to refinance
        const totalHoldingMonths = values.renovationDuration + values.timeToRefinance;

        const mao = this.calculateMAO(
            values.arv,
            values.expectedLtv,
            values.renovationCosts,
            values.closingCosts,
            monthlyHoldingCosts,
            totalHoldingMonths,
            values.maxCashLeft
        );

        const totalHoldingCosts = monthlyHoldingCosts * totalHoldingMonths;
        const monthlyLoanPayment = this.calculateMonthlyInterestOnly(acquisitionLoanAmount, values.acqRenoRate);

        // Update results
        const updateElement = (id, value) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = this.formatCurrency(value);
            }
        };

        updateElement('mao_result', mao);
        updateElement('monthly_loan_payment', monthlyLoanPayment);
        updateElement('monthly_holding_costs', monthlyHoldingCosts);
        updateElement('total_holding_costs', totalHoldingCosts);
        updateElement('acquisition_loan_amount', acquisitionLoanAmount);
    }
};

// Add event listener for manual edits
document.getElementById('acquisition_loan_amount')?.addEventListener('input', function() {
    this.dataset.userEdited = 'true';
});

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => maoCalculator.init());
} else {
    maoCalculator.init();
}

export default maoCalculator;