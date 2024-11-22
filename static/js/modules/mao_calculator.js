const maoCalculator = {
    init: function() {
        const form = document.getElementById('maoForm');
        if (!form) return;

        const inputs = [
            'after_repair_value',
            'max_cash_left', 
            'renovation_costs', 
            'closing_costs',
            'renovation_duration',
            'expected_ltv',
            'time_to_refinance',
            'utilities',
            'hoa_coa',
            'maintenance',
            'interest_rate',
            'loan_amount'
        ];
        
        inputs.forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                input.addEventListener('input', () => {
                    this.updateCalculations();
                });
            }
        });

        const interestOnlyCheckbox = document.getElementById('interest_only');
        if (interestOnlyCheckbox) {
            interestOnlyCheckbox.addEventListener('change', () => {
                this.updateCalculations();
            });
        }

        const expected_ltv = document.getElementById('expected_ltv');
        if (expected_ltv) {
            expected_ltv.addEventListener('change', () => {
                this.updateCalculations();
            });
        }

        this.updateCalculations();
    },

    updateCalculations: function() {
        try {
            const values = {
                arv: parseFloat(document.getElementById('after_repair_value')?.value) || 0,
                maxCashLeft: parseFloat(document.getElementById('max_cash_left')?.value) || 0,
                renovationCosts: parseFloat(document.getElementById('renovation_costs')?.value) || 0,
                closingCosts: parseFloat(document.getElementById('closing_costs')?.value) || 0,
                renovationDuration: parseFloat(document.getElementById('renovation_duration')?.value) || 0,
                timeToRefinance: parseFloat(document.getElementById('time_to_refinance')?.value) || 0,
                utilities: parseFloat(document.getElementById('utilities')?.value) || 0,
                hoaCoa: parseFloat(document.getElementById('hoa_coa')?.value) || 0,
                maintenance: parseFloat(document.getElementById('maintenance')?.value) || 0,
                interestRate: parseFloat(document.getElementById('interest_rate')?.value) || 0,
                expectedLtv: parseFloat(document.getElementById('expected_ltv')?.value) || 80,
                isInterestOnly: document.getElementById('interest_only')?.checked || false
            };
    
            console.log('Input values:', values);
    
            const baseMonthlyHoldingCosts = values.utilities + values.hoaCoa + values.maintenance;
            console.log('Base monthly holding costs:', baseMonthlyHoldingCosts);
    
            const totalMonths = values.renovationDuration + values.timeToRefinance;
            console.log('Total months:', totalMonths);
            
            const initialLoanAmount = Math.round((values.arv * (values.expectedLtv / 100)) + values.renovationCosts);
            console.log('Initial loan amount:', initialLoanAmount);
            
            // Update loan amount input value instead of text content
            const loanAmountInput = document.getElementById('loan_amount');
            if (loanAmountInput) {
                loanAmountInput.value = initialLoanAmount.toFixed(2);
            }
    
            const monthlyInterestRate = values.interestRate / 100 / 12;
            const monthlyInterest = initialLoanAmount * monthlyInterestRate;
            console.log('Monthly interest:', monthlyInterest);
            
            const monthlyHoldingCosts = baseMonthlyHoldingCosts + monthlyInterest;
            console.log('Total monthly holding costs:', monthlyHoldingCosts);
    
            const totalHoldingCosts = monthlyHoldingCosts * totalMonths;
            console.log('Total holding costs:', totalHoldingCosts);
            
            const refinanceAmount = values.arv * (values.expectedLtv / 100);
            console.log('Refinance amount:', refinanceAmount);
    
            const totalProjectCosts = values.renovationCosts + values.closingCosts + totalHoldingCosts;
            console.log('Total project costs:', totalProjectCosts);
    
            const mao = values.arv - totalProjectCosts - values.maxCashLeft;
            console.log('MAO:', mao);
    
            const maoResult = document.getElementById('mao_result');
            if (maoResult) {
                maoResult.textContent = new Intl.NumberFormat('en-US', {
                    style: 'currency',
                    currency: 'USD',
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                }).format(mao);
            }
        } catch (error) {
            console.error('Error calculating MAO:', error);
        }
    }
};

export default maoCalculator;