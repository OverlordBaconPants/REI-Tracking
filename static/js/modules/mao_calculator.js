const maoCalculator = {
    init: function() {
        const form = document.getElementById('maoForm');
        if (!form) return;

        const inputs = form.querySelectorAll('input');
        inputs.forEach(input => {
            input.addEventListener('input', () => this.updateCalculations());
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

    updateCalculations: function() {
        const values = {
            arv: parseFloat(document.getElementById('after_repair_value').value) || 0,
            maxCashLeft: parseFloat(document.getElementById('max_cash_left').value) || 0,
            renovationCosts: parseFloat(document.getElementById('renovation_costs').value) || 0,
            closingCosts: parseFloat(document.getElementById('closing_costs').value) || 0,
            renovationDuration: parseFloat(document.getElementById('renovation_duration').value) || 0,
            timeToRefinance: parseFloat(document.getElementById('time_to_refinance').value) || 0,
            utilities: parseFloat(document.getElementById('utilities').value) || 0,
            hoaCoa: parseFloat(document.getElementById('hoa_coa').value) || 0,
            maintenance: parseFloat(document.getElementById('maintenance').value) || 0,
            interestRate: parseFloat(document.getElementById('interest_rate').value) || 0,
            expectedLtv: parseFloat(document.getElementById('expected_ltv').value) || 75,
            isInterestOnly: document.getElementById('interest_only').checked
        };

        const baseMonthlyHoldingCosts = values.utilities + values.hoaCoa + values.maintenance;
        const totalMonths = values.renovationDuration + values.timeToRefinance;
        const initialLoanAmount = Math.round((values.arv * (values.expectedLtv / 100)) + values.renovationCosts);
        
        const monthlyInterestRate = values.interestRate / 100 / 12;
        const monthlyInterest = initialLoanAmount * monthlyInterestRate;
        
        const monthlyHoldingCosts = baseMonthlyHoldingCosts + monthlyInterest;
        const totalHoldingCosts = monthlyHoldingCosts * totalMonths;
        
        const totalProjectCosts = values.renovationCosts + values.closingCosts + totalHoldingCosts;
        const mao = values.arv - totalProjectCosts - values.maxCashLeft;

        // Update results
        document.getElementById('mao_result').textContent = this.formatCurrency(mao);
        document.getElementById('loan_amount').textContent = this.formatCurrency(initialLoanAmount);
        document.getElementById('monthly_holding_costs').textContent = this.formatCurrency(monthlyHoldingCosts);
        document.getElementById('total_project_costs').textContent = this.formatCurrency(totalProjectCosts);
    }
};

document.addEventListener('DOMContentLoaded', () => maoCalculator.init());

export default maoCalculator;