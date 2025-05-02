/**
 * calculator.js
 * Financial calculations for property analysis
 */

const FinancialCalculator = {
    /**
     * Calculate monthly loan payment
     * @param {Object} loan - Loan details
     * @param {number} loan.amount - Loan amount
     * @param {number} loan.interestRate - Annual interest rate (as percentage)
     * @param {number} loan.term - Loan term in months
     * @param {boolean} loan.isInterestOnly - Whether the loan is interest-only
     * @returns {number} Monthly payment
     */
calculateLoanPayment(loan) {
      console.log("calculateLoanPayment called with:", loan);
      
      if (!loan || loan.amount <= 0 || loan.term <= 0) {
        console.log("calculateLoanPayment: Invalid loan parameters, returning 0");
        return 0;
      }

      const amount = parseFloat(loan.amount);
      const annualRate = parseFloat(loan.interestRate) / 100;
      const monthlyRate = annualRate / 12;
      const term = parseInt(loan.term);
      
      console.log("calculateLoanPayment: Parsed values:", { 
        amount, 
        annualRate, 
        monthlyRate, 
        term 
      });

      // Handle zero interest rate
      if (annualRate === 0) {
        console.log("calculateLoanPayment: Zero interest rate, dividing principal by term");
        const payment = amount / term;
        console.log("calculateLoanPayment: Calculated payment:", payment);
        return payment;
      }

      // Interest-only loan
      if (loan.isInterestOnly) {
        console.log("calculateLoanPayment: Interest-only loan");
        const payment = amount * monthlyRate;
        console.log("calculateLoanPayment: Calculated payment:", payment);
        return payment;
      }

      // Regular amortizing loan
      console.log("calculateLoanPayment: Regular amortizing loan");
      const factor = Math.pow(1 + monthlyRate, term);
      const payment = amount * (monthlyRate * factor) / (factor - 1);
      console.log("calculateLoanPayment: Calculated payment:", payment);
      return payment;
    },

    formatPercentageOrInfinite(value) {
      if (value === "Infinite") {
        return "Infinite";
      }
      
      // Check if it's a number
      const numValue = parseFloat(value);
      if (!isNaN(numValue)) {
        // Format with one decimal place
        return `${numValue.toFixed(1)}%`;
      }
      
      // Handle unexpected types
      return String(value);
    },

    /**
     * Format metric values for display with appropriate handling of special cases
     * @param {string} metricName - The name of the metric being formatted
     * @param {any} value - The value to format
     * @param {Object} options - Optional formatting options
     * @returns {string} Formatted value for display
     */
    formatMetric(metricName, value, options = {}) {
      // Default options
      const defaults = {
        decimalPlaces: 2,        // Default decimal places for numbers
        currency: true,          // Whether to format as currency
        percentageDecimalPlaces: 1, // Decimal places for percentages
        showPercentSymbol: true, // Whether to show % symbol
        showInfiniteFor: ['cash_on_cash_return', 'roi', 'option_roi'] // Metrics that can be "Infinite"
      };
      
      // Merge options with defaults
      const settings = { ...defaults, ...options };
      
      // Handle null/undefined values
      if (value === null || value === undefined) {
        return 'N/A';
      }
      
      // Handle "Infinite" special case for relevant metrics
      if (settings.showInfiniteFor.includes(metricName) && 
          (value === "Infinite" || 
          value === Infinity || 
          (typeof value === 'string' && value.toLowerCase() === 'infinite'))) {
        return "Infinite";
      }
      
      // Handle percentage metrics
      const percentageMetrics = [
        'cash_on_cash_return', 'roi', 'cap_rate', 'option_roi', 
        'operating_expense_ratio', 'expense_ratio', 'occupancy_rate',
        'vacancy_rate', 'management_fee_percentage', 'vacancy_percentage',
        'capex_percentage', 'repairs_percentage'
      ];
      
      if (percentageMetrics.includes(metricName)) {
        // Convert to number if it's a string
        let numValue;
        if (typeof value === 'string') {
          // Remove % sign if present
          const cleanValue = value.replace('%', '').trim();
          numValue = parseFloat(cleanValue);
        } else {
          numValue = parseFloat(value);
        }
        
        // Check if conversion succeeded
        if (!isNaN(numValue)) {
          const formattedValue = numValue.toFixed(settings.percentageDecimalPlaces);
          return settings.showPercentSymbol ? `${formattedValue}%` : formattedValue;
        }
        
        // If conversion failed, return the original value
        return String(value);
      }
      
      // Handle ratio metrics (DSCR, GRM)
      const ratioMetrics = ['dscr', 'gross_rent_multiplier'];
      if (ratioMetrics.includes(metricName)) {
        const numValue = parseFloat(value);
        if (!isNaN(numValue)) {
          return numValue.toFixed(2);
        }
        return String(value);
      }
      
      // Handle currency metrics (most other metrics)
      const nonCurrencyMetrics = [
        'renovation_duration', 'breakeven_months', 'total_units',
        'occupied_units', 'vacancy_units', 'loan_term'
      ];
      
      if (settings.currency && !nonCurrencyMetrics.includes(metricName)) {
        // Convert to number if it's a string
        let numValue;
        if (typeof value === 'string') {
          // Remove currency symbols and commas
          const cleanValue = value.replace(/[$,]/g, '').trim();
          numValue = parseFloat(cleanValue);
        } else {
          numValue = parseFloat(value);
        }
        
        // Check if conversion succeeded
        if (!isNaN(numValue)) {
          // Format as currency
          return `$${numValue.toFixed(settings.decimalPlaces).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
        }
        
        // If conversion failed, return the original value
        return String(value);
      }
      
      // Handle integer metrics
      if (nonCurrencyMetrics.includes(metricName)) {
        const numValue = parseFloat(value);
        if (!isNaN(numValue)) {
          return Math.round(numValue).toString();
        }
        return String(value);
      }
      
      // Default: return as string
      return String(value);
    },
    
    /**
     * Calculate net operating income (NOI)
     * @param {Object} analysis - Analysis data
     * @returns {number} Monthly NOI
     */
    calculateNOI(analysis) {
      // Get gross income
      let monthlyIncome = 0;
      
      if (analysis.analysis_type === 'Multi-Family') {
        // Calculate from unit types
        let unitTypes = [];
        try {
          unitTypes = JSON.parse(analysis.unit_types);
        } catch (e) {
          console.error('Error parsing unit types:', e);
          unitTypes = [];
        }
        
        // Get total potential rent from all units
        monthlyIncome = unitTypes.reduce((total, ut) => {
          return total + (ut.count * ut.rent);
        }, 0);
        
        // Add other income
        monthlyIncome += parseFloat(analysis.other_income || 0);
      } else {
        // Standard property: use monthly rent
        monthlyIncome = parseFloat(analysis.monthly_rent || 0);
      }
      
      // Calculate operating expenses
      const expenses = this.calculateOperatingExpenses(analysis, monthlyIncome);
      
      // Return NOI
      return monthlyIncome - expenses;
    },
    
    /**
     * Calculate operating expenses
     * @param {Object} analysis - Analysis data
     * @param {number} grossIncome - Monthly gross income
     * @returns {number} Monthly operating expenses
     */
    calculateOperatingExpenses(analysis, grossIncome) {
      if (grossIncome === undefined) {
        grossIncome = parseFloat(analysis.monthly_rent || 0);
        
        // For Multi-Family, calculate gross income
        if (analysis.analysis_type === 'Multi-Family') {
          try {
            const unitTypes = JSON.parse(analysis.unit_types);
            grossIncome = unitTypes.reduce((total, ut) => {
              return total + (ut.count * ut.rent);
            }, 0);
            grossIncome += parseFloat(analysis.other_income || 0);
          } catch (e) {
            console.error('Error calculating Multi-Family gross income:', e);
          }
        }
      }
      
      // Fixed expenses
      const fixedExpenses = [
        'property_taxes',
        'insurance',
        'hoa_coa_coop'
      ].reduce((total, field) => {
        return total + parseFloat(analysis[field] || 0);
      }, 0);
      
      // Multi-Family specific expenses
      let multiFamilyExpenses = 0;
      if (analysis.analysis_type === 'Multi-Family') {
        multiFamilyExpenses = [
          'common_area_maintenance',
          'elevator_maintenance',
          'staff_payroll',
          'trash_removal',
          'common_utilities'
        ].reduce((total, field) => {
          return total + parseFloat(analysis[field] || 0);
        }, 0);
      }
      
      // Percentage-based expenses
      const percentExpenses = [
        ['management_fee_percentage', grossIncome],
        ['capex_percentage', grossIncome],
        ['vacancy_percentage', grossIncome],
        ['repairs_percentage', grossIncome]
      ].reduce((total, [field, base]) => {
        const percentage = parseFloat(analysis[field] || 0) / 100;
        return total + (base * percentage);
      }, 0);
      
      // PadSplit-specific expenses
      let padSplitExpenses = 0;
      if (analysis.analysis_type && analysis.analysis_type.includes('PadSplit')) {
        // Fixed PadSplit expenses
        padSplitExpenses = [
          'utilities',
          'internet',
          'cleaning',
          'pest_control',
          'landscaping'
        ].reduce((total, field) => {
          return total + parseFloat(analysis[field] || 0);
        }, 0);
        
        // PadSplit platform fee
        const platformPercentage = parseFloat(analysis.padsplit_platform_percentage || 0) / 100;
        padSplitExpenses += grossIncome * platformPercentage;
      }
      
      return fixedExpenses + multiFamilyExpenses + percentExpenses + padSplitExpenses;
    },
    
    /**
     * Calculate monthly cash flow
     * @param {Object} analysis - Analysis data
     * @returns {number} Monthly cash flow
     */
    calculateMonthlyCashFlow(analysis) {
      // Calculate NOI
      const noi = this.calculateNOI(analysis);
      
      // Calculate debt service (loan payments)
      const debtService = this.calculateDebtService(analysis);
      
      // Return cash flow
      return noi - debtService;
    },
    
    /**
     * Calculate total debt service (monthly loan payments)
     * @param {Object} analysis - Analysis data
     * @returns {number} Total monthly debt service
     */
    calculateDebtService(analysis) {
      let totalPayment = 0;
      
      // Handle BRRRR-specific loans
      if (analysis.analysis_type && analysis.analysis_type.includes('BRRRR')) {
        // For BRRRR, ALWAYS use refinance loan for cash flow
        // This represents the permanent financing scenario after renovation
        const refinanceLoan = {
          amount: parseFloat(analysis.refinance_loan_amount || 0),
          interestRate: parseFloat(analysis.refinance_loan_interest_rate || 0),
          term: parseInt(analysis.refinance_loan_term || 0),
          isInterestOnly: false // Refinance loans are always amortizing
        };
        
        if (refinanceLoan.amount > 0) {
          totalPayment = this.calculateLoanPayment(refinanceLoan);
          console.log(`Using refinance loan payment for BRRRR cash flow: $${totalPayment.toFixed(2)}`);
        }
        
        // Calculate initial loan payment for reference only
        const initialLoan = {
          amount: parseFloat(analysis.initial_loan_amount || 0),
          interestRate: parseFloat(analysis.initial_loan_interest_rate || 0),
          term: parseInt(analysis.initial_loan_term || 0),
          isInterestOnly: Boolean(analysis.initial_interest_only)
        };
        
        if (initialLoan.amount > 0) {
          const initialPayment = this.calculateLoanPayment(initialLoan);
          console.log(`Initial loan payment (for reference only): $${initialPayment.toFixed(2)}`);
          // Store for display but don't use for cash flow calculation
          analysis.calculated_metrics = analysis.calculated_metrics || {};
          analysis.calculated_metrics.initial_loan_payment = initialPayment;
        }
      } else {
        // For standard loans, check each loan
        for (let i = 1; i <= 3; i++) {
          const prefix = `loan${i}`;
          const amount = parseFloat(analysis[`${prefix}_loan_amount`] || 0);
          
          if (amount > 0) {
            const loan = {
              amount: amount,
              interestRate: parseFloat(analysis[`${prefix}_loan_interest_rate`] || 0),
              term: parseInt(analysis[`${prefix}_loan_term`] || 0),
              isInterestOnly: Boolean(analysis[`${prefix}_interest_only`])
            };
            
            totalPayment += this.calculateLoanPayment(loan);
          }
        }
        
        // Handle balloon payment scenario
        if (analysis.has_balloon_payment) {
          // Check if we're using pre-balloon or post-balloon payment
          // Would need more logic to determine based on current date vs balloon due date
          // For now, just using standard loan payments
        }
      }
      
      return totalPayment;
    },
    
    /**
     * Calculate total cash invested
     * @param {Object} analysis - Analysis data
     * @returns {number} Total cash invested
     */
    calculateTotalCashInvested(analysis) {
      // For BRRRR, use special calculation
      if (analysis.analysis_type && analysis.analysis_type.includes('BRRRR')) {
        return this.calculateBRRRRCashInvested(analysis);
      }
      
      // Base investment (out of pocket costs)
      let totalCash = [
        'cash_to_seller',         // Cash paid directly to seller
        'renovation_costs',       // Renovation costs
        'closing_costs',          // Base closing costs
        'assignment_fee',         // Assignment fees
        'marketing_costs'         // Marketing costs
      ].reduce((total, field) => {
        return total + parseFloat(analysis[field] || 0);
      }, 0);
      
      // Add loan down payments and closing costs
      for (let i = 1; i <= 3; i++) {
        const prefix = `loan${i}`;
        const amount = parseFloat(analysis[`${prefix}_loan_amount`] || 0);
        
        if (amount > 0) {
          totalCash += parseFloat(analysis[`${prefix}_loan_down_payment`] || 0);
          totalCash += parseFloat(analysis[`${prefix}_loan_closing_costs`] || 0);
        }
      }
      
      // Add furnishing costs for PadSplit
      if (analysis.analysis_type && analysis.analysis_type.includes('PadSplit')) {
        totalCash += parseFloat(analysis.furnishing_costs || 0);
      }
      
      // Handle Lease Option specially
      if (analysis.analysis_type === 'Lease Option') {
        // For Lease Option, the main investment is the option fee
        totalCash = parseFloat(analysis.option_consideration_fee || 0);
      }
      
      return Math.max(0, totalCash);
    },
    
    /**
     * Calculate BRRRR-specific cash invested
     * @param {Object} analysis - Analysis data
     * @returns {number} Total cash invested for BRRRR
     */
    calculateBRRRRCashInvested(analysis) {
      // Step 1: Calculate initial investment (before financing)
      const initialInvestment = parseFloat(analysis.purchase_price || 0) + 
                               parseFloat(analysis.renovation_costs || 0) +
                               parseFloat(analysis.initial_loan_closing_costs || 0);
      

      
      // Add holding costs (calculated from renovation period)
      const monthlyHoldingCosts = 
        parseFloat(analysis.property_taxes || 0) +
        parseFloat(analysis.insurance || 0);
      
      // Calculate initial loan payment if interest-only during holding period
      let initialLoanAmount = parseFloat(analysis.initial_loan_amount || 0);
      let initialLoanRate = parseFloat(analysis.initial_loan_interest_rate || 0) / 100 / 12;
      let initialLoanPayment = initialLoanAmount * initialLoanRate;
      
      // Add holding costs using dedicated function
      const totalHoldingCosts = this.calculateHoldingCosts(analysis);
      
      // Add furnishing costs for PadSplit
      let furnishingCosts = 0;
      if (analysis.analysis_type.includes('PadSplit')) {
        furnishingCosts = parseFloat(analysis.furnishing_costs || 0);
      }
      
      const totalInitialInvestment = initialInvestment + totalHoldingCosts + furnishingCosts;
      
      // Step 2: Subtract initial financing to get out-of-pocket
      // Allow negative values for over-leveraged acquisitions
      const initialOutOfPocket = totalInitialInvestment - initialLoanAmount;
      
      // Step 3: Calculate cash recouped from refinance
      // Allow negative values for refinance shortfalls
      const refinanceLoanAmount = parseFloat(analysis.refinance_loan_amount || 0);
      const refinanceClosingCosts = parseFloat(analysis.refinance_loan_closing_costs || 0);
      
      const cashRecouped = refinanceLoanAmount - initialLoanAmount - refinanceClosingCosts;
      
      // Step 4: Calculate final out-of-pocket investment
      // Allow negative values to represent cash extracted beyond initial investment
      const finalInvestment = initialOutOfPocket - cashRecouped;
      
      return finalInvestment;
    },

    calculateHoldingCosts(analysis) {
      // Calculate monthly fixed expenses
      const monthlyFixedExpenses = 
        parseFloat(analysis.property_taxes || 0) +
        parseFloat(analysis.insurance || 0) +
        parseFloat(analysis.hoa_coa_coop || 0);
      
      // Calculate monthly interest on initial loan
      const initialLoanAmount = parseFloat(analysis.initial_loan_amount || 0);
      const initialLoanRate = parseFloat(analysis.initial_loan_interest_rate || 0) / 100 / 12;
      const monthlyLoanInterest = initialLoanAmount * initialLoanRate;
      
      // Calculate total monthly holding costs
      const monthlyHoldingCosts = monthlyFixedExpenses + monthlyLoanInterest;
      
      // Multiply by renovation duration
      const renovationDuration = parseInt(analysis.renovation_duration || 0);
      return monthlyHoldingCosts * renovationDuration;
    },
    
    /**
     * Calculate cash on cash return
     * @param {Object} analysis - Analysis data
     * @returns {number} Cash on cash return (as percentage)
     */
    calculateCashOnCashReturn(analysis) {
      // Calculate annual cash flow
      const monthlyCashFlow = this.calculateMonthlyCashFlow(analysis);
      const annualCashFlow = monthlyCashFlow * 12;
      
      // Calculate total cash invested
      const cashInvested = this.calculateTotalCashInvested(analysis);
      
      // Calculate cash on cash return
      if (cashInvested <= 0) {
        // Zero or negative cash invested means infinite return
        return "Infinite";
      }
      
      return (annualCashFlow / cashInvested) * 100;
    },
    
    /**
     * Calculate cap rate
     * @param {Object} analysis - Analysis data
     * @returns {number} Cap rate (as percentage)
     */
    calculateCapRate(analysis) {
      // Calculate annual NOI
      const monthlyNOI = this.calculateNOI(analysis);
      const annualNOI = monthlyNOI * 12;
      
      // Get property value (use after repair value if available)
      let propertyValue = parseFloat(analysis.after_repair_value || 0);
      if (propertyValue <= 0) {
        propertyValue = parseFloat(analysis.purchase_price || 0);
      }
      
      // Calculate cap rate
      if (propertyValue <= 0) {
        return 0;
      }
      
      return (annualNOI / propertyValue) * 100;
    },
    
    /**
     * Calculate debt service coverage ratio (DSCR)
     * @param {Object} analysis - Analysis data
     * @returns {number} DSCR value
     */
    calculateDSCR(analysis) {
      // Calculate monthly NOI
      const monthlyNOI = this.calculateNOI(analysis);
      
      // Calculate debt service
      const debtService = this.calculateDebtService(analysis);
      
      // Calculate DSCR
      if (debtService <= 0) {
        return 0; // Avoid division by zero
      }
      
      return monthlyNOI / debtService;
    },
    
    /**
     * Calculate operating expense ratio
     * @param {Object} analysis - Analysis data
     * @returns {number} Operating expense ratio (as percentage)
     */
    calculateOperatingExpenseRatio(analysis) {
      // Calculate gross income
      let grossIncome = 0;
      
      if (analysis.analysis_type === 'Multi-Family') {
        // Calculate from unit types
        try {
          const unitTypes = JSON.parse(analysis.unit_types);
          grossIncome = unitTypes.reduce((total, ut) => {
            return total + (ut.count * ut.rent);
          }, 0);
          grossIncome += parseFloat(analysis.other_income || 0);
        } catch (e) {
          console.error('Error calculating Multi-Family gross income:', e);
          grossIncome = 0;
        }
      } else {
        // Standard property: use monthly rent
        grossIncome = parseFloat(analysis.monthly_rent || 0);
      }
      
      if (grossIncome <= 0) {
        return 0; // Avoid division by zero
      }
      
      // Calculate operating expenses
      const operatingExpenses = this.calculateOperatingExpenses(analysis, grossIncome);
      
      // Calculate ratio
      return (operatingExpenses / grossIncome) * 100;
    },
    
    /**
     * Calculate maximum allowable offer (MAO) for BRRRR
     * @param {Object} analysis - Analysis data
     * @returns {number} MAO amount
     */
    calculateMAO(analysis) {
      if (!analysis.analysis_type || !analysis.analysis_type.includes('BRRRR')) {
        return 0; // MAO only applies to BRRRR
      }
      
      const arv = parseFloat(analysis.after_repair_value || 0);
      const renovationCosts = parseFloat(analysis.renovation_costs || 0);
      
      // Calculate holding costs
      const monthlyHoldingCosts = 
        parseFloat(analysis.property_taxes || 0) +
        parseFloat(analysis.insurance || 0);
      
      // Calculate initial loan payment if interest-only during holding period
      let initialLoanAmount = parseFloat(analysis.initial_loan_amount || 0);
      let initialLoanRate = parseFloat(analysis.initial_loan_interest_rate || 0) / 100 / 12;
      let initialLoanPayment = initialLoanAmount * initialLoanRate;
      
      const totalHoldingCosts = 
        (monthlyHoldingCosts + initialLoanPayment) * 
        parseInt(analysis.renovation_duration || 0);
      
      // Calculate closing costs
      const closingCosts = 
        parseFloat(analysis.initial_loan_closing_costs || 0) +
        parseFloat(analysis.refinance_loan_closing_costs || 0);
      
      // Add furnishing costs for PadSplit
      let furnishingCosts = 0;
      if (analysis.analysis_type.includes('PadSplit')) {
        furnishingCosts = parseFloat(analysis.furnishing_costs || 0);
      }
      
      // Typical BRRRR wants 75% ARV - costs
      const targetLoan = arv * 0.75;
      const mao = targetLoan - (renovationCosts + totalHoldingCosts + closingCosts + furnishingCosts);
      
      return Math.max(0, mao);
    },
    
    /**
     * Calculate all financial metrics for an analysis
     * @param {Object} analysis - Analysis data
     * @returns {Object} All calculated metrics
     */
    calculateAllMetrics(analysis) {
      // Basic return object
      const metrics = {};
      
      try {
        // Common metrics for all analysis types
        const monthlyNOI = this.calculateNOI(analysis);
        const monthlyCashFlow = this.calculateMonthlyCashFlow(analysis);
        
        // Set core metrics
        metrics.monthly_noi = monthlyNOI;
        metrics.annual_noi = monthlyNOI * 12;
        metrics.monthly_cash_flow = monthlyCashFlow;
        metrics.annual_cash_flow = monthlyCashFlow * 12;
        metrics.total_cash_invested = this.calculateTotalCashInvested(analysis);
        metrics.cash_on_cash_return = this.calculateCashOnCashReturn(analysis);
        metrics.operating_expense_ratio = this.calculateOperatingExpenseRatio(analysis);
        
        // Metrics that don't apply to Lease Option
        if (analysis.analysis_type !== 'Lease Option') {
          metrics.cap_rate = this.calculateCapRate(analysis);
          metrics.dscr = this.calculateDSCR(analysis);
        }
        
        // Add analysis-specific metrics
        if (analysis.analysis_type === 'Multi-Family') {
          this.addMultiFamilyMetrics(analysis, metrics);
        } else if (analysis.analysis_type === 'Lease Option') {
          this.addLeaseOptionMetrics(analysis, metrics);
        } else if (analysis.analysis_type && analysis.analysis_type.includes('BRRRR')) {
          this.addBRRRRMetrics(analysis, metrics);
        } else if (analysis.has_balloon_payment) {
          this.addBalloonPaymentMetrics(analysis, metrics);
        }
        
        // Add loan payment metrics
        this.addLoanPaymentMetrics(analysis, metrics);
        
      } catch (error) {
        console.error('Error calculating metrics:', error);
      }
      
      return metrics;
    },
    
    /**
     * Add Multi-Family specific metrics
     * @param {Object} analysis - Analysis data
     * @param {Object} metrics - Metrics object to add to
     */
    addMultiFamilyMetrics(analysis, metrics) {
      try {
        // Parse unit types
        const unitTypes = JSON.parse(analysis.unit_types || '[]');
        
        // Get total units
        const totalUnits = unitTypes.reduce((total, ut) => total + ut.count, 0) || 1;
        
        // Calculate gross potential rent
        const grossPotentialRent = unitTypes.reduce((total, ut) => {
          return total + (ut.count * ut.rent);
        }, 0);
        
        // Calculate actual gross income from occupied units
        const actualGrossIncome = unitTypes.reduce((total, ut) => {
          return total + (ut.occupied * ut.rent);
        }, 0) + parseFloat(analysis.other_income || 0);
        
        // Calculate NOI per unit
        const noiPerUnit = metrics.monthly_noi / totalUnits;
        
        // Add Multi-Family specific metrics
        metrics.noi = noiPerUnit; // Per unit for multi-family
        metrics.gross_potential_rent = grossPotentialRent;
        metrics.actual_gross_income = actualGrossIncome;
        metrics.price_per_unit = parseFloat(analysis.purchase_price || 0) / totalUnits;
        metrics.occupancy_rate = (parseFloat(analysis.occupied_units || 0) / totalUnits) * 100;
        
        // Add unit type summary
        metrics.unit_type_summary = unitTypes.reduce((summary, ut) => {
          summary[ut.type] = {
            count: ut.count,
            occupied: ut.occupied,
            avg_sf: ut.square_footage,
            rent: ut.rent,
            total_potential_rent: ut.count * ut.rent
          };
          return summary;
        }, {});
        
      } catch (error) {
        console.error('Error calculating Multi-Family metrics:', error);
      }
    },
    
    /**
     * Add Lease Option specific metrics
     * @param {Object} analysis - Analysis data
     * @param {Object} metrics - Metrics object to add to
     */
    addLeaseOptionMetrics(analysis, metrics) {
      try {
        // Calculate rent credits
        const monthlyRent = parseFloat(analysis.monthly_rent || 0);
        const creditPercentage = parseFloat(analysis.monthly_rent_credit_percentage || 0) / 100;
        const creditCap = parseFloat(analysis.rent_credit_cap || 0);
        const optionTerm = parseInt(analysis.option_term_months || 0);
        
        // Calculate monthly credit and total potential
        const monthlyCredit = monthlyRent * creditPercentage;
        const totalPotentialCredit = monthlyCredit * optionTerm;
        
        // Actual rent credits (capped at rent_credit_cap)
        const totalRentCredits = Math.min(totalPotentialCredit, creditCap);
        
        // Calculate effective purchase price
        const strikePrice = parseFloat(analysis.strike_price || 0);
        const effectivePurchasePrice = strikePrice - totalRentCredits;
        
        // Calculate option fee ROI
        const optionFee = parseFloat(analysis.option_consideration_fee || 0);
        const annualCashFlow = metrics.annual_cash_flow;
        let optionROI = 0;
        
        if (optionFee > 0) {
          optionROI = (annualCashFlow / optionFee) * 100;
        }
        
        // Calculate breakeven months
        let breakEvenMonths = Infinity;
        const monthlyCashFlow = metrics.monthly_cash_flow;
        
        if (monthlyCashFlow > 0) {
          breakEvenMonths = Math.ceil(optionFee / monthlyCashFlow);
        }
        
        // Add Lease Option specific metrics
        metrics.total_rent_credits = totalRentCredits;
        metrics.effective_purchase_price = effectivePurchasePrice;
        metrics.option_roi = optionROI;
        metrics.breakeven_months = breakEvenMonths;
        
      } catch (error) {
        console.error('Error calculating Lease Option metrics:', error);
      }
    },
    
    /**
     * Add BRRRR specific metrics
     * @param {Object} analysis - Analysis data
     * @param {Object} metrics - Metrics object to add to
     */
    addBRRRRMetrics(analysis, metrics) {
      try {
        // Calculate holding costs
        const monthlyHoldingCosts = 
          parseFloat(analysis.property_taxes || 0) +
          parseFloat(analysis.insurance || 0);
        
        // Calculate initial loan payment
        let initialLoanAmount = parseFloat(analysis.initial_loan_amount || 0);
        let initialLoanRate = parseFloat(analysis.initial_loan_interest_rate || 0) / 100 / 12;
        let initialLoanPayment = initialLoanAmount * initialLoanRate;
        
        const totalHoldingCosts = 
          (monthlyHoldingCosts + initialLoanPayment) * 
          parseInt(analysis.renovation_duration || 0);
        
        // Calculate total project costs
        const totalProjectCosts = 
          parseFloat(analysis.purchase_price || 0) +
          parseFloat(analysis.renovation_costs || 0) +
          totalHoldingCosts +
          parseFloat(analysis.initial_loan_closing_costs || 0) +
          parseFloat(analysis.refinance_loan_closing_costs || 0);
        
        // Calculate equity captured
        const arv = parseFloat(analysis.after_repair_value || 0);
        const totalCosts = 
          parseFloat(analysis.purchase_price || 0) +
          parseFloat(analysis.renovation_costs || 0);
        
        const equityCaptured = Math.max(0, arv - totalCosts);
        
        // Calculate cash recouped from refinance
        const refinanceLoanAmount = parseFloat(analysis.refinance_loan_amount || 0);
        const refinanceClosingCosts = parseFloat(analysis.refinance_loan_closing_costs || 0);
        
        const cashRecouped = Math.max(0, refinanceLoanAmount - initialLoanAmount - refinanceClosingCosts);
        
        // Add BRRRR specific metrics
        metrics.equity_captured = equityCaptured;
        metrics.holding_costs = totalHoldingCosts;
        metrics.total_project_costs = totalProjectCosts;
        metrics.cash_recouped = cashRecouped;
        metrics.maximum_allowable_offer = this.calculateMAO(analysis);
        
      } catch (error) {
        console.error('Error calculating BRRRR metrics:', error);
      }
    },
    
    /**
     * Add balloon payment specific metrics
     * @param {Object} analysis - Analysis data
     * @param {Object} metrics - Metrics object to add to
     */
    addBalloonPaymentMetrics(analysis, metrics) {
      try {
        // Calculate pre-balloon loan payments
        let preMonthlyPayment = 0;
        
        for (let i = 1; i <= 3; i++) {
          const prefix = `loan${i}`;
          const amount = parseFloat(analysis[`${prefix}_loan_amount`] || 0);
          
          if (amount > 0) {
            const loan = {
              amount: amount,
              interestRate: parseFloat(analysis[`${prefix}_loan_interest_rate`] || 0),
              term: parseInt(analysis[`${prefix}_loan_term`] || 0),
              isInterestOnly: Boolean(analysis[`${prefix}_interest_only`])
            };
            
            preMonthlyPayment += this.calculateLoanPayment(loan);
          }
        }
        
        // Calculate post-balloon refinance payment
        const postLoan = {
          amount: parseFloat(analysis.balloon_refinance_loan_amount || 0),
          interestRate: parseFloat(analysis.balloon_refinance_loan_interest_rate || 0),
          term: parseInt(analysis.balloon_refinance_loan_term || 0),
          isInterestOnly: false // Refinance is typically amortized
        };
        
        const postMonthlyPayment = this.calculateLoanPayment(postLoan);
        
        // Calculate payment difference
        const paymentDifference = postMonthlyPayment - preMonthlyPayment;
        
        // Calculate refinance costs
        const refinanceCosts = 
          parseFloat(analysis.balloon_refinance_loan_down_payment || 0) +
          parseFloat(analysis.balloon_refinance_loan_closing_costs || 0);
        
        // Add balloon specific metrics
        metrics.pre_balloon_monthly_payment = preMonthlyPayment;
        metrics.post_balloon_monthly_payment = postMonthlyPayment;
        metrics.monthly_payment_difference = paymentDifference;
        metrics.balloon_refinance_costs = refinanceCosts;
        
        // TODO: Calculate post-balloon cash flow
        // This requires more complex logic to account for rent/expense increases
        // over time until the balloon due date
        
      } catch (error) {
        console.error('Error calculating balloon payment metrics:', error);
      }
    },
    
    /**
     * Add loan payment metrics
     * @param {Object} analysis - Analysis data
     * @param {Object} metrics - Metrics object to add to
     */
    addLoanPaymentMetrics(analysis, metrics) {
      // Handle BRRRR loans
      if (analysis.analysis_type && analysis.analysis_type.includes('BRRRR')) {
        // Calculate initial loan payment
        const initialLoan = {
          amount: parseFloat(analysis.initial_loan_amount || 0),
          interestRate: parseFloat(analysis.initial_loan_interest_rate || 0),
          term: parseInt(analysis.initial_loan_term || 0),
          isInterestOnly: Boolean(analysis.initial_interest_only)
        };
        
        if (initialLoan.amount > 0) {
          metrics.initial_loan_payment = this.calculateLoanPayment(initialLoan);
        }
        
        // Calculate refinance loan payment
        const refinanceLoan = {
          amount: parseFloat(analysis.refinance_loan_amount || 0),
          interestRate: parseFloat(analysis.refinance_loan_interest_rate || 0),
          term: parseInt(analysis.refinance_loan_term || 0),
          isInterestOnly: false // Refinance loans are typically amortized
        };
        
        if (refinanceLoan.amount > 0) {
          metrics.refinance_loan_payment = this.calculateLoanPayment(refinanceLoan);
        }
      } else {
        // Regular loans (up to 3)
        for (let i = 1; i <= 3; i++) {
          const prefix = `loan${i}`;
          const amount = parseFloat(analysis[`${prefix}_loan_amount`] || 0);
          
          if (amount > 0) {
            const loan = {
              amount: amount,
              interestRate: parseFloat(analysis[`${prefix}_loan_interest_rate`] || 0),
              term: parseInt(analysis[`${prefix}_loan_term`] || 0),
              isInterestOnly: Boolean(analysis[`${prefix}_interest_only`])
            };
            
            metrics[`${prefix}_loan_payment`] = this.calculateLoanPayment(loan);
          }
        }
      }
    }
  };
  
  // Export the calculator
  export default FinancialCalculator;
