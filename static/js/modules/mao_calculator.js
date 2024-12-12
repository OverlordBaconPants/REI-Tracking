const maoCalculator = {
    init: function() {
        const inputs = document.querySelectorAll('input[type="number"]');
        inputs.forEach(input => {
            input.addEventListener('input', () => this.updateCalculations());
            input.addEventListener('change', () => this.updateCalculations());
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

    calculateMAO: function(arv, ltv, renovationCosts, closingCosts, monthlyHoldingCosts, duration) {
        const loanAmount = arv * (ltv / 100);
        const totalHoldingCosts = monthlyHoldingCosts * duration;
        const mao = loanAmount - renovationCosts - closingCosts - totalHoldingCosts;
        return Math.max(0, mao);
    },

    updateCalculations: function() {
        const values = {
            arv: parseFloat(document.getElementById('after_repair_value').value) || 0,
            renovationCosts: parseFloat(document.getElementById('renovation_costs').value) || 0,
            closingCosts: parseFloat(document.getElementById('closing_costs').value) || 0,
            renovationDuration: parseFloat(document.getElementById('renovation_duration').value) || 0,
            expectedLtv: parseFloat(document.getElementById('expected_ltv').value) || 75,
            utilities: parseFloat(document.getElementById('utilities').value) || 0,
            hoaCoa: parseFloat(document.getElementById('hoa_coa').value) || 0,
            maintenance: parseFloat(document.getElementById('maintenance').value) || 0,
            acqRenoRate: parseFloat(document.getElementById('acq_reno_rate').value) || 12
        };

        const initialLoanAmount = values.arv * 0.75;  // Initial loan amount at 75% ARV
        
        const monthlyHoldingCosts = this.calculateMonthlyHoldingCosts(
            initialLoanAmount,
            values.acqRenoRate,
            values.utilities,
            values.hoaCoa,
            values.maintenance
        );

        const mao = this.calculateMAO(
            values.arv,
            values.expectedLtv,
            values.renovationCosts,
            values.closingCosts,
            monthlyHoldingCosts,
            values.renovationDuration
        );

        const totalHoldingCosts = monthlyHoldingCosts * values.renovationDuration;

        // Update results
        const updateElement = (id, value) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = this.formatCurrency(value);
            }
        };

        updateElement('mao_result', mao);
        updateElement('monthly_holding_costs', monthlyHoldingCosts);
        updateElement('total_holding_costs', totalHoldingCosts);
        updateElement('initial_loan', initialLoanAmount);
    }
};

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => maoCalculator.init());
} else {
    maoCalculator.init();
}

export default maoCalculator;