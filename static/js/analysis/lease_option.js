/**
 * lease_option.js
 * Lease Option property strategy specific implementation
 */

import UIHelpers from './ui_helpers.js';
import Calculator from './calculator.js';
import AnalysisCore from './core.js';

const LeaseOptionHandler = {
  /**
   * Get the HTML template for Lease Option analysis
   * @returns {string} HTML template
   */
  getTemplate() {
    const baseTemplate = `
        <!-- Property Details Card -->
        <div class="card mb-4">
            <div class="card-header">
                <h5 class="mb-0">Property Details</h5>
            </div>
            <div class="card-body">
                <div class="row g-3">
                    <div class="col-12 col-md-6">
                        <label for="property_type" class="form-label">Property Type</label>
                        <select class="form-select form-select-lg" id="property_type" name="property_type" required>
                            <option value="">Select Property Type</option>
                            <option value="Single Family">Single Family</option>
                            <option value="Condo">Condo</option>
                            <option value="Townhouse">Townhouse</option>
                            <option value="Manufactured">Manufactured</option>
                        </select>
                    </div>
                    <div class="col-12 col-md-4">
                        <label for="square_footage" class="form-label">Square Footage</label>
                        <div class="input-group">
                            <input type="number" class="form-control form-control-lg" id="square_footage" 
                                name="square_footage" placeholder="Property square footage">
                            <span class="input-group-text">sq ft</span>
                        </div>
                    </div>
                    <div class="col-12 col-md-4">
                        <label for="lot_size" class="form-label">Lot Size</label>
                        <div class="input-group">
                            <input type="number" class="form-control form-control-lg" id="lot_size" 
                                name="lot_size" placeholder="Lot size">
                            <span class="input-group-text">sq ft</span>
                        </div>
                    </div>
                    <div class="col-12 col-md-4">
                        <label for="year_built" class="form-label">Year Built</label>
                        <input type="number" class="form-control form-control-lg" id="year_built" 
                            name="year_built" placeholder="Construction year">
                    </div>
                    <div class="col-12 col-md-6">
                        <label for="bedrooms" class="form-label">Bedrooms</label>
                        <input type="number" class="form-control form-control-lg" id="bedrooms" 
                            name="bedrooms" min="0" step="1" placeholder="Number of bedrooms">
                    </div>
                    <div class="col-12 col-md-6">
                        <label for="bathrooms" class="form-label">Bathrooms</label>
                        <input type="number" class="form-control form-control-lg" id="bathrooms" 
                            name="bathrooms" min="0" step="0.5" placeholder="Number of bathrooms">
                    </div>
                </div>
            </div>
        </div>

        <!-- Purchase Details Card -->
        <div class="card mb-4">
            <div class="card-header">
                <h5 class="mb-0">Purchase Details</h5>
            </div>
            <div class="card-body">
                <div class="row g-3">
                    <div class="col-12 col-md-6">
                        <label for="purchase_price" class="form-label">Purchase Price</label>
                        <div class="input-group">
                            <span class="input-group-text">$</span>
                            <input type="number" 
                                class="form-control form-control-lg" 
                                id="purchase_price" 
                                name="purchase_price" 
                                placeholder="Current market value/owner's purchase price" 
                                required
                                data-bs-toggle="tooltip"
                                data-bs-placement="top"
                                title="The current market value or price the owner paid for the property">
                        </div>
                    </div>
                    <div class="col-12 col-md-6">
                        <label for="strike_price" class="form-label">Strike Price</label>
                        <div class="input-group">
                            <span class="input-group-text">$</span>
                            <input type="number" class="form-control form-control-lg" id="strike_price" 
                                name="strike_price" placeholder="Agreed future purchase price" required>
                        </div>
                    </div>
                    <div class="col-12 col-md-6">
                        <label for="option_consideration_fee" class="form-label">Option Fee</label>
                        <div class="input-group">
                            <span class="input-group-text">$</span>
                            <input type="number" class="form-control form-control-lg" id="option_consideration_fee" 
                                name="option_consideration_fee" placeholder="Non-refundable option fee" required>
                        </div>
                    </div>
                    <div class="col-12 col-md-6">
                        <label for="option_term_months" class="form-label">Option Term</label>
                        <div class="input-group">
                            <input type="number" class="form-control form-control-lg" id="option_term_months" 
                                name="option_term_months" placeholder="Option period duration" required>
                            <span class="input-group-text">months</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Add Financing Section -->
        <div class="card mb-4">
            <div class="card-header">
                <h5 class="mb-0">Financing</h5>
            </div>
            <div class="card-body" id="financing-section">
                <div id="loans-container">
                    <!-- Existing loans will be inserted here -->
                </div>
                <div class="mt-3">
                    <button type="button" class="btn btn-primary" id="add-loan-btn">
                        <i class="bi bi-plus-circle me-2"></i>Add Loan
                    </button>
                </div>
            </div>
        </div>

        <!-- Rental Income Card -->
        <div class="card mb-4">
            <div class="card-header">
                <h5 class="mb-0">Rental Income</h5>
            </div>
            <div class="card-body">
                <div class="row g-3">
                    <div class="col-12 col-md-6">
                        <label for="monthly_rent" class="form-label">Monthly Rent</label>
                        <div class="input-group">
                            <span class="input-group-text">$</span>
                            <input type="number" class="form-control form-control-lg" id="monthly_rent" 
                                name="monthly_rent" placeholder="Monthly rent amount" required>
                        </div>
                    </div>
                    <div class="col-12 col-md-6">
                        <label for="monthly_rent_credit_percentage" class="form-label">Rent Credit</label>
                        <div class="input-group">
                            <input type="number" class="form-control form-control-lg" id="monthly_rent_credit_percentage" 
                                name="monthly_rent_credit_percentage" placeholder="Percentage of rent credited" required>
                            <span class="input-group-text">%</span>
                        </div>
                    </div>
                    <div class="col-12 col-md-6">
                        <label for="rent_credit_cap" class="form-label">Rent Credit Cap</label>
                        <div class="input-group">
                            <span class="input-group-text">$</span>
                            <input type="number" class="form-control form-control-lg" id="rent_credit_cap" 
                                name="rent_credit_cap" placeholder="Maximum total rent credit" required>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Operating Expenses Card -->
        <div class="card mb-4">
            <div class="card-header">
                <h5 class="mb-0">Operating Expenses</h5>
            </div>
            <div class="card-body">
                <div class="row g-3">
                    <div class="col-12 col-md-6">
                        <label for="property_taxes" class="form-label">Monthly Property Taxes</label>
                        <div class="input-group">
                            <span class="input-group-text">$</span>
                            <input type="number" class="form-control form-control-lg" id="property_taxes" 
                                name="property_taxes" placeholder="Monthly taxes" required>
                        </div>
                    </div>
                    <div class="col-12 col-md-6">
                        <label for="insurance" class="form-label">Monthly Insurance</label>
                        <div class="input-group">
                            <span class="input-group-text">$</span>
                            <input type="number" class="form-control form-control-lg" id="insurance" 
                                name="insurance" placeholder="Monthly insurance" required>
                        </div>
                    </div>
                    <div class="col-12 col-md-6">
                        <label for="management_fee_percentage" class="form-label">Management Fee</label>
                        <div class="input-group">
                            <input type="number" class="form-control form-control-lg" id="management_fee_percentage" 
                                name="management_fee_percentage" value="8" min="0" max="100" step="0.5" required>
                            <span class="input-group-text">%</span>
                        </div>
                    </div>
                    <div class="col-12 col-md-6">
                        <label for="capex_percentage" class="form-label">CapEx</label>
                        <div class="input-group">
                            <input type="number" class="form-control form-control-lg" id="capex_percentage" 
                                name="capex_percentage" value="2" min="0" max="100" step="1" required>
                            <span class="input-group-text">%</span>
                        </div>
                    </div>
                    <div class="col-12 col-md-6">
                        <label for="repairs_percentage" class="form-label">Repairs</label>
                        <div class="input-group">
                            <input type="number" class="form-control form-control-lg" id="repairs_percentage" 
                                name="repairs_percentage" value="2" min="0" max="100" step="1" required>
                            <span class="input-group-text">%</span>
                        </div>
                    </div>
                    <div class="col-12 col-md-6">
                        <label for="vacancy_percentage" class="form-label">Vacancy Rate</label>
                        <div class="input-group">
                            <input type="number" class="form-control form-control-lg" id="vacancy_percentage" 
                                name="vacancy_percentage" value="4" min="0" max="100" step="1" required>
                            <span class="input-group-text">%</span>
                        </div>
                    </div>
                    <div class="col-12 col-md-6">
                        <label for="hoa_coa_coop" class="form-label">HOA/COA/COOP</label>
                        <div class="input-group">
                            <span class="input-group-text">$</span>
                            <input type="number" class="form-control form-control-lg" id="hoa_coa_coop" 
                                name="hoa_coa_coop" placeholder="Monthly association fees" required>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Notes Card -->
        <div class="card mb-4">
            <div class="card-header">
                <h5 class="mb-0">Notes</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-12">
                        <textarea class="form-control" id="notes" name="notes" rows="4" 
                                maxlength="1000" placeholder="Enter any notes about this analysis (max 1,000 characters)"></textarea>
                        <div class="form-text text-end mt-2">
                            <span id="notes-counter">0</span>/1000 characters
                        </div>
                    </div>
                </div>
            </div>
        </div>
        `;
        const compsCardHTML = AnalysisCore.getCompsCardHTML();
        return baseTemplate + compsCardHTML;
  },
  
  /**
   * Return HTML template for a loan
   * @param {number} loanNumber - The loan number
   * @returns {string} HTML for loan section
   */
  getLoanFieldsHTML(loanNumber) {
    return `
    <div class="loan-section mb-4">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">Loan ${loanNumber}</h5>
                <button type="button" class="btn btn-danger btn-sm remove-loan-btn">
                    <i class="bi bi-trash me-2"></i>Remove
                </button>
            </div>
            <div class="card-body">
                <div class="row g-3">
                    <div class="col-12 col-md-6">
                        <label for="loan${loanNumber}_loan_name" class="form-label">Loan Name</label>
                        <input type="text" class="form-control form-control-lg" id="loan${loanNumber}_loan_name" 
                               name="loan${loanNumber}_loan_name" placeholder="Enter loan name" required>
                    </div>
                    <div class="col-12 col-md-6">
                        <label for="loan${loanNumber}_loan_amount" class="form-label">Loan Amount</label>
                        <div class="input-group">
                            <span class="input-group-text">$</span>
                            <input type="number" class="form-control form-control-lg" id="loan${loanNumber}_loan_amount" 
                                   name="loan${loanNumber}_loan_amount" placeholder="Enter loan amount" required>
                        </div>
                    </div>
                    <div class="col-12 col-md-6">
                        <label for="loan${loanNumber}_loan_down_payment" class="form-label">Down Payment</label>
                        <div class="input-group">
                            <span class="input-group-text">$</span>
                            <input type="number" class="form-control form-control-lg" id="loan${loanNumber}_loan_down_payment" 
                                   name="loan${loanNumber}_loan_down_payment" placeholder="Enter down payment" required>
                        </div>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label for="loan${loanNumber}_loan_interest_rate" class="form-label">Interest Rate (%)</label>
                        <input type="number" class="form-control" id="loan${loanNumber}_loan_interest_rate" 
                            name="loan${loanNumber}_loan_interest_rate" step="0.025" min="0" max="100" 
                            placeholder="Enter interest rate" required>
                        <div class="form-check mt-2">
                            <input class="form-check-input" type="checkbox" id="loan${loanNumber}_interest_only" 
                                name="loan${loanNumber}_interest_only">
                            <label class="form-check-label" for="loan${loanNumber}_interest_only">
                                Interest Only
                            </label>
                        </div>
                    </div>
                    <div class="col-12 col-md-6">
                        <label for="loan${loanNumber}_loan_term" class="form-label">Loan Term (months)</label>
                        <input type="number" class="form-control form-control-lg" id="loan${loanNumber}_loan_term" 
                               name="loan${loanNumber}_loan_term" min="1" placeholder="Enter loan term" required>
                    </div>
                    <div class="col-12 col-md-6">
                        <label for="loan${loanNumber}_loan_closing_costs" class="form-label">Closing Costs</label>
                        <div class="input-group">
                            <span class="input-group-text">$</span>
                            <input type="number" class="form-control form-control-lg" id="loan${loanNumber}_loan_closing_costs" 
                                   name="loan${loanNumber}_loan_closing_costs" placeholder="Enter closing costs" required>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    `;
  },
  
  /**
   * Initialize Lease Option specific handlers
   */
  async initHandlers() {
    // Initialize loan handlers
    this.initLoanHandlers();
    
    // Initialize rent credit calculator
    this.initRentCreditCalculator();
    
    // Initialize validation
    this.initLeaseOptionValidation();
  },
  
  /**
   * Initialize loan handlers
   */
  initLoanHandlers() {
    const addLoanBtn = document.getElementById('add-loan-btn');
    const loansContainer = document.getElementById('loans-container');
    
    if (!addLoanBtn || !loansContainer) {
      console.error('Loan section elements not found');
      return;
    }
    
    // Handle adding new loans
    addLoanBtn.addEventListener('click', () => {
      const loanCount = loansContainer.querySelectorAll('.loan-section').length + 1;
      
      if (loanCount <= 3) {  // Maximum 3 loans allowed
        loansContainer.insertAdjacentHTML('beforeend', this.getLoanFieldsHTML(loanCount));
        
        if (loanCount >= 3) {
          addLoanBtn.style.display = 'none';
        }
      }
    });
    
    // Event delegation for remove loan buttons
    loansContainer.addEventListener('click', (e) => {
      if (e.target.closest('.remove-loan-btn')) {
        const loanSection = e.target.closest('.loan-section');
        if (loanSection) {
          loanSection.remove();
          
          // Renumber remaining loans
          const remainingLoans = loansContainer.querySelectorAll('.loan-section');
          remainingLoans.forEach((loan, index) => {
            const newIndex = index + 1;
            const heading = loan.querySelector('h5');
            if (heading) {
              heading.textContent = `Loan ${newIndex}`;
            }
            
            // Update field IDs and names to match flat schema
            const inputs = loan.querySelectorAll('input');
            inputs.forEach(input => {
              const fieldType = input.id.split('_').pop(); // amount, interest_rate, etc.
              input.id = `loan${newIndex}_loan_${fieldType}`;
              input.name = `loan${newIndex}_loan_${fieldType}`;
            });
          });
          
          if (remainingLoans.length < 3) {
            addLoanBtn.style.display = 'block';
          }
        }
      }
    });
  },
  
  /**
   * Initialize rent credit calculator
   */
  initRentCreditCalculator() {
    const monthlyRentInput = document.getElementById('monthly_rent');
    const creditPercentageInput = document.getElementById('monthly_rent_credit_percentage');
    const creditCapInput = document.getElementById('rent_credit_cap');
    const optionTermInput = document.getElementById('option_term_months');
    
    // Function to update rent credit cap
    const updateRentCreditCap = () => {
      const monthlyRent = UIHelpers.toRawNumber(monthlyRentInput?.value) || 0;
      const creditPercentage = UIHelpers.toRawNumber(creditPercentageInput?.value) || 0;
      const optionTerm = parseInt(optionTermInput?.value) || 0;
      
      if (monthlyRent > 0 && creditPercentage > 0 && optionTerm > 0 && creditCapInput) {
        const monthlyCredit = monthlyRent * (creditPercentage / 100);
        const totalCredit = monthlyCredit * optionTerm;
        
        // Update the credit cap input with the suggested value
        if (!creditCapInput.value || UIHelpers.toRawNumber(creditCapInput.value) === 0) {
          creditCapInput.value = totalCredit.toFixed(2);
        }
      }
    };
    
    // Add event listeners
    if (monthlyRentInput) {
      monthlyRentInput.addEventListener('input', updateRentCreditCap);
    }
    
    if (creditPercentageInput) {
      creditPercentageInput.addEventListener('input', updateRentCreditCap);
    }
    
    if (optionTermInput) {
      optionTermInput.addEventListener('input', updateRentCreditCap);
    }
  },
  
  /**
   * Initialize validation specific to Lease Option properties
   */
  initLeaseOptionValidation() {
    const form = document.getElementById('analysisForm');
    if (!form) return;
    
    // Add validation for strike price > purchase price
    const purchasePriceInput = document.getElementById('purchase_price');
    const strikePriceInput = document.getElementById('strike_price');
    
    if (purchasePriceInput && strikePriceInput) {
      strikePriceInput.addEventListener('change', () => {
        const purchasePrice = UIHelpers.toRawNumber(purchasePriceInput.value);
        const strikePrice = UIHelpers.toRawNumber(strikePriceInput.value);
        
        if (strikePrice <= purchasePrice) {
          strikePriceInput.classList.add('is-invalid');
          
          // Add error message
          let errorDiv = strikePriceInput.parentNode.querySelector('.invalid-feedback');
          if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            strikePriceInput.parentNode.appendChild(errorDiv);
          }
          errorDiv.textContent = 'Strike price must be greater than purchase price';
          
          UIHelpers.showToast('warning', 'Strike price should be greater than purchase price');
        } else {
          strikePriceInput.classList.remove('is-invalid');
          
          // Remove error message
          const errorDiv = strikePriceInput.parentNode.querySelector('.invalid-feedback');
          if (errorDiv) {
            errorDiv.remove();
          }
        }
      });
    }
  },
  
  /**
   * Populate form fields with analysis data
   * @param {Object} analysis - Analysis data
   */
  populateFields(analysis) {
    // Check that this is a Lease Option analysis
    if (analysis.analysis_type !== 'Lease Option') {
      console.warn('Attempted to populate non-Lease Option analysis with Lease Option handler');
      return;
    }
    
    // Set property details
    AnalysisCore.setFieldValue('property_type', analysis.property_type);
    AnalysisCore.setFieldValue('square_footage', analysis.square_footage);
    AnalysisCore.setFieldValue('lot_size', analysis.lot_size);
    AnalysisCore.setFieldValue('year_built', analysis.year_built);
    AnalysisCore.setFieldValue('bedrooms', analysis.bedrooms);
    AnalysisCore.setFieldValue('bathrooms', analysis.bathrooms);
    
    // Set lease option details
    AnalysisCore.setFieldValue('purchase_price', analysis.purchase_price);
    AnalysisCore.setFieldValue('strike_price', analysis.strike_price);
    AnalysisCore.setFieldValue('option_consideration_fee', analysis.option_consideration_fee);
    AnalysisCore.setFieldValue('option_term_months', analysis.option_term_months);
    
    // Set rental income details
    AnalysisCore.setFieldValue('monthly_rent', analysis.monthly_rent);
    AnalysisCore.setFieldValue('monthly_rent_credit_percentage', analysis.monthly_rent_credit_percentage);
    AnalysisCore.setFieldValue('rent_credit_cap', analysis.rent_credit_cap);
    
    // Set operating expenses
    AnalysisCore.setFieldValue('property_taxes', analysis.property_taxes);
    AnalysisCore.setFieldValue('insurance', analysis.insurance);
    AnalysisCore.setFieldValue('hoa_coa_coop', analysis.hoa_coa_coop);
    AnalysisCore.setFieldValue('management_fee_percentage', analysis.management_fee_percentage);
    AnalysisCore.setFieldValue('capex_percentage', analysis.capex_percentage);
    AnalysisCore.setFieldValue('repairs_percentage', analysis.repairs_percentage);
    AnalysisCore.setFieldValue('vacancy_percentage', analysis.vacancy_percentage);
    
    // Handle existing loans
    const loansContainer = document.getElementById('loans-container');
    if (loansContainer) {
      // Clear existing loans
      loansContainer.innerHTML = '';
      
      // Add each existing loan
      for (let i = 1; i <= 3; i++) {
        const prefix = `loan${i}`;
        if (analysis[`${prefix}_loan_amount`] > 0) {
          // Insert loan HTML
          loansContainer.insertAdjacentHTML('beforeend', this.getLoanFieldsHTML(i));
          
          // Populate loan fields
          AnalysisCore.setFieldValue(`${prefix}_loan_name`, analysis[`${prefix}_loan_name`]);
          AnalysisCore.setFieldValue(`${prefix}_loan_amount`, analysis[`${prefix}_loan_amount`]);
          AnalysisCore.setFieldValue(`${prefix}_loan_interest_rate`, analysis[`${prefix}_loan_interest_rate`]);
          AnalysisCore.setFieldValue(`${prefix}_loan_term`, analysis[`${prefix}_loan_term`]);
          AnalysisCore.setFieldValue(`${prefix}_loan_down_payment`, analysis[`${prefix}_loan_down_payment`]);
          AnalysisCore.setFieldValue(`${prefix}_loan_closing_costs`, analysis[`${prefix}_loan_closing_costs`]);
          
          // Handle interest-only checkbox specifically
          AnalysisCore.setFieldValue(`${prefix}_interest_only`, analysis[`${prefix}_interest_only`]);
        }
      }
      
      // Hide add loan button if we have 3 loans
      const addLoanBtn = document.getElementById('add-loan-btn');
      if (addLoanBtn && loansContainer.querySelectorAll('.loan-section').length >= 3) {
        addLoanBtn.style.display = 'none';
      }
    }
  },
  
  /**
   * Process form data before submission
   * @param {FormData} formData - The form data
   * @param {Object} analysisData - The processed analysis data
   * @returns {Object} The processed analysis data
   */
  processFormData(formData, analysisData) {
    // Handle loan interest-only checkboxes
    for (let i = 1; i <= 3; i++) {
      const interestOnlyField = `loan${i}_interest_only`;
      if (interestOnlyField in analysisData) {
        analysisData[interestOnlyField] = (analysisData[interestOnlyField] === 'on');
      }
    }
    
    // Handle numeric fields
    const numericFields = [
      'square_footage', 'lot_size', 'year_built', 'bedrooms', 'bathrooms',
      'purchase_price', 'strike_price', 'option_consideration_fee', 'option_term_months',
      'monthly_rent', 'rent_credit_cap',
      'property_taxes', 'insurance', 'hoa_coa_coop'
    ];
    
    numericFields.forEach(field => {
      if (field in analysisData) {
        analysisData[field] = UIHelpers.toRawNumber(analysisData[field]);
      }
    });
    
    // Handle percentage fields
    const percentageFields = [
      'monthly_rent_credit_percentage', 'management_fee_percentage', 
      'capex_percentage', 'vacancy_percentage', 'repairs_percentage'
    ];
    
    percentageFields.forEach(field => {
      if (field in analysisData) {
        analysisData[field] = UIHelpers.toRawNumber(analysisData[field]);
      }
    });
    
    // Handle loan numeric fields
    for (let i = 1; i <= 3; i++) {
      const prefix = `loan${i}`;
      const loanFields = [
        `${prefix}_loan_amount`,
        `${prefix}_loan_interest_rate`,
        `${prefix}_loan_term`,
        `${prefix}_loan_down_payment`,
        `${prefix}_loan_closing_costs`
      ];
      
      loanFields.forEach(field => {
        if (field in analysisData) {
          analysisData[field] = UIHelpers.toRawNumber(analysisData[field]);
        }
      });
    }
    
    return analysisData;
  },
  
  /**
   * Generate report content for the analysis
   * @param {Object} analysis - The analysis data
   * @returns {string} HTML report content
   */
  generateReport(analysis) {
    // Get calculated metrics
    const metrics = analysis.calculated_metrics || {};
    
    // Calculate rent credits if not in metrics
    let totalRentCredits, effectivePurchasePrice;
    
    if (metrics.total_rent_credits && metrics.effective_purchase_price) {
      totalRentCredits = metrics.total_rent_credits;
      effectivePurchasePrice = metrics.effective_purchase_price;
    } else {
      // Calculate monthly rent credit
      const monthlyRent = UIHelpers.toRawNumber(analysis.monthly_rent);
      const creditPercentage = UIHelpers.toRawNumber(analysis.monthly_rent_credit_percentage) / 100;
      const optionTerm = UIHelpers.toRawNumber(analysis.option_term_months);
      const creditCap = UIHelpers.toRawNumber(analysis.rent_credit_cap);
      
      // Calculate total potential credits and apply cap
      const monthlyCredit = monthlyRent * creditPercentage;
      const totalPotentialCredit = monthlyCredit * optionTerm;
      totalRentCredits = Math.min(totalPotentialCredit, creditCap);
      
      // Calculate effective purchase price
      const strikePrice = UIHelpers.toRawNumber(analysis.strike_price);
      effectivePurchasePrice = strikePrice - totalRentCredits;
    }
    
    // Calculate option fee ROI if not in metrics
    let optionROI, breakEvenMonths;
    
    if (metrics.option_roi && metrics.breakeven_months) {
      optionROI = metrics.option_roi;
      breakEvenMonths = metrics.breakeven_months;
    } else {
    // Calculate option fee ROI
    const optionFee = UIHelpers.toRawNumber(analysis.option_consideration_fee);
    const annualCashFlow = metrics.annual_cash_flow ? 
                        UIHelpers.toRawNumber(metrics.annual_cash_flow) : 
                        UIHelpers.toRawNumber(metrics.monthly_cash_flow || 0) * 12;

    optionROI = optionFee > 0 ? (annualCashFlow / optionFee) * 100 : 0;

    // Calculate breakeven months
    const monthlyCashFlow = metrics.monthly_cash_flow ? 
                        UIHelpers.toRawNumber(metrics.monthly_cash_flow) : 
                        annualCashFlow / 12;

    breakEvenMonths = monthlyCashFlow > 0 ? Math.ceil(optionFee / monthlyCashFlow) : Infinity;
    }

    return `
    <!-- Lease Option Details Card -->
    <div class="card mb-4">
    <div class="card-header">
        <h5 class="mb-0">Lease Option Details</h5>
    </div>
    <div class="card-body">
        <div class="list-group list-group-flush">
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
            <span>Purchase Price</span>
            <strong>${UIHelpers.formatDisplayValue(analysis.purchase_price)}</strong>
        </div>
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
            <span>Strike Price</span>
            <strong>${UIHelpers.formatDisplayValue(analysis.strike_price)}</strong>
        </div>
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
            <span>Option Fee</span>
            <strong>${UIHelpers.formatDisplayValue(analysis.option_consideration_fee)}</strong>
        </div>
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
            <span>Option Term</span>
            <strong>${analysis.option_term_months} months</strong>
        </div>
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
            <span>Monthly Rent Credit %</span>
            <strong>${UIHelpers.formatDisplayValue(analysis.monthly_rent_credit_percentage, 'percentage')}</strong>
        </div>
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
            <span>Rent Credit Cap</span>
            <strong>${UIHelpers.formatDisplayValue(analysis.rent_credit_cap)}</strong>
        </div>
        </div>
    </div>
    </div>

    <!-- Property Details Card -->
    <div class="card mb-4">
    <div class="card-header">
        <h5 class="mb-0">Property Details</h5>
    </div>
    <div class="card-body">
        <div class="list-group list-group-flush">
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
            <span>Property Type</span>
            <strong>${analysis.property_type || 'Not Specified'}</strong>
        </div>
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
            <span>Square Footage</span>
            <strong>${analysis.square_footage ? analysis.square_footage.toLocaleString() + ' sq ft' : 'Not specified'}</strong>
        </div>
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
            <span>Lot Size</span>
            <strong>${analysis.lot_size ? analysis.lot_size.toLocaleString() + ' sq ft' : 'Not specified'}</strong>
        </div>
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
            <span>Year Built</span>
            <strong>${analysis.year_built || 'Not specified'}</strong>
        </div>
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
            <span>Bedrooms</span>
            <strong>${analysis.bedrooms || 'Not specified'}</strong>
        </div>
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
            <span>Bathrooms</span>
            <strong>${analysis.bathrooms || 'Not specified'}</strong>
        </div>
        </div>
    </div>
    </div>

    <!-- Financial Overview Card -->
    <div class="card mb-4">
    <div class="card-header">
        <h5 class="mb-0">Financial Overview</h5>
    </div>
    <div class="card-body">
        <div class="list-group list-group-flush">
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
            <span>Monthly Rent</span>
            <strong>${UIHelpers.formatDisplayValue(analysis.monthly_rent)}</strong>
        </div>
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
            <span>Monthly Cash Flow</span>
            <strong>${metrics.monthly_cash_flow || UIHelpers.formatDisplayValue(metrics.annual_cash_flow / 12 || 0)}</strong>
        </div>
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
            <span>Annual Cash Flow</span>
            <strong>${metrics.annual_cash_flow || UIHelpers.formatDisplayValue(metrics.monthly_cash_flow * 12 || 0)}</strong>
        </div>
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
            <span>Option Fee ROI (Annual)</span>
            <strong>${metrics.option_roi || UIHelpers.formatDisplayValue(optionROI, 'percentage')}</strong>
        </div>
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
            <span>Cash-on-Cash Return</span>
            <strong>${metrics.cash_on_cash_return || UIHelpers.formatDisplayValue(optionROI, 'percentage')}</strong>
        </div>
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
            <span class="d-flex align-items-center">
            Breakeven Period
            <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" 
                title="Number of months needed to recoup the option fee from cash flow">
            </i>
            </span>
            <strong>${metrics.breakeven_months || (breakEvenMonths === Infinity ? 'N/A' : `${breakEvenMonths} months`)}</strong>
        </div>
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
            <span>Total Rent Credits</span>
            <strong>${metrics.total_rent_credits || UIHelpers.formatDisplayValue(totalRentCredits)}</strong>
        </div>
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
            <span class="d-flex align-items-center">
            Effective Purchase Price
            <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" 
                title="Strike price minus total rent credits">
            </i>
            </span>
            <strong>${metrics.effective_purchase_price || UIHelpers.formatDisplayValue(effectivePurchasePrice)}</strong>
        </div>
        </div>
    </div>
    </div>

    <!-- Operating Expenses Card -->
    <div class="card mb-4">
    <div class="card-header">
        <h5 class="mb-0">Operating Expenses</h5>
    </div>
    <div class="card-body">
        <div class="list-group list-group-flush">
        <div class="row g-0">
            <div class="col-12 col-md-6">
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                <span>Property Taxes</span>
                <strong>${UIHelpers.formatDisplayValue(analysis.property_taxes)}</strong>
            </div>
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                <span>Insurance</span>
                <strong>${UIHelpers.formatDisplayValue(analysis.insurance)}</strong>
            </div>
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                <span>HOA/COA/COOP</span>
                <strong>${UIHelpers.formatDisplayValue(analysis.hoa_coa_coop)}</strong>
            </div>
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                <span>Management</span>
                <div class="text-end">
                <div class="small text-muted">
                    ${UIHelpers.formatDisplayValue(analysis.management_fee_percentage, 'percentage')}
                </div>
                <strong>${UIHelpers.formatDisplayValue(analysis.monthly_rent * (analysis.management_fee_percentage / 100))}</strong>
                </div>
            </div>
            </div>
            <div class="col-12 col-md-6">
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                <span>CapEx</span>
                <div class="text-end">
                <div class="small text-muted">
                    ${UIHelpers.formatDisplayValue(analysis.capex_percentage, 'percentage')}
                </div>
                <strong>${UIHelpers.formatDisplayValue(analysis.monthly_rent * (analysis.capex_percentage / 100))}</strong>
                </div>
            </div>
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                <span>Vacancy</span>
                <div class="text-end">
                <div class="small text-muted">
                    ${UIHelpers.formatDisplayValue(analysis.vacancy_percentage, 'percentage')}
                </div>
                <strong>${UIHelpers.formatDisplayValue(analysis.monthly_rent * (analysis.vacancy_percentage / 100))}</strong>
                </div>
            </div>
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                <span>Repairs</span>
                <div class="text-end">
                <div class="small text-muted">
                    ${UIHelpers.formatDisplayValue(analysis.repairs_percentage, 'percentage')}
                </div>
                <strong>${UIHelpers.formatDisplayValue(analysis.monthly_rent * (analysis.repairs_percentage / 100))}</strong>
                </div>
            </div>
            </div>
        </div>
        </div>
    </div>
    </div>

    <!-- Financing Details Card -->
    <div class="card mb-4">
    <div class="card-header">
        <h5 class="mb-0">Financing Details</h5>
    </div>
    <div class="card-body">
        <div class="accordion" id="leaseOptionLoansAccordion">
        ${this.generateLoanReportSections(analysis)}
        </div>
    </div>
    </div>

    ${this.createNotesSection(analysis.notes)}`;
    },

    /**
    * Generate loan details sections for the report
    * @param {Object} analysis - The analysis data
    * @returns {string} HTML for loan sections
    */
    generateLoanReportSections(analysis) {
    let html = '';
    let hasLoans = false;

    // Add each existing loan
    for (let i = 1; i <= 3; i++) {
    const prefix = `loan${i}`;
    const loanAmount = UIHelpers.toRawNumber(analysis[`${prefix}_loan_amount`]);

    if (loanAmount > 0) {
    hasLoans = true;
    const isInterestOnly = analysis[`${prefix}_interest_only`];
    const loanName = analysis[`${prefix}_loan_name`] || `Loan ${i}`;
    const loanPayment = analysis.calculated_metrics?.[`${prefix}_loan_payment`];
    
    html += `
        <div class="accordion-item">
        <h6 class="accordion-header">
            <button class="accordion-button ${i !== 1 ? 'collapsed' : ''}" type="button" 
                    data-bs-toggle="collapse" data-bs-target="#${prefix}Collapse">
            ${loanName}
            </button>
        </h6>
        <div id="${prefix}Collapse" class="accordion-collapse collapse ${i === 1 ? 'show' : ''}" 
            data-bs-parent="#leaseOptionLoansAccordion">
            <div class="accordion-body p-0">
            <div class="list-group list-group-flush">
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                <span>Amount</span>
                <strong>${UIHelpers.formatDisplayValue(loanAmount)}</strong>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                <span>Interest Rate</span>
                <div>
                    <strong>${UIHelpers.formatDisplayValue(analysis[`${prefix}_loan_interest_rate`], 'percentage')}</strong>
                    <span class="badge ${isInterestOnly ? 'bg-success' : 'bg-info'} ms-2">
                    ${isInterestOnly ? 'Interest Only' : 'Amortized'}
                    </span>
                </div>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                <span>Term</span>
                <strong>${analysis[`${prefix}_loan_term`] || '0'} months</strong>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                <span>Monthly Payment</span>
                <strong>${loanPayment || Calculator.calculateLoanPayment({
                    amount: loanAmount,
                    interestRate: analysis[`${prefix}_loan_interest_rate`],
                    term: analysis[`${prefix}_loan_term`],
                    isInterestOnly: isInterestOnly
                })}</strong>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                <span>Down Payment</span>
                <strong>${UIHelpers.formatDisplayValue(analysis[`${prefix}_loan_down_payment`])}</strong>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                <span>Closing Costs</span>
                <strong>${UIHelpers.formatDisplayValue(analysis[`${prefix}_loan_closing_costs`])}</strong>
                </div>
            </div>
            </div>
        </div>
        </div>`;
    }
    }

    if (!hasLoans) {
    return `
    <div class="text-center py-4">
        <p class="mb-0 text-muted">No loan details available</p>
    </div>`;
    }

    return html;
    },

    /**
    * Create notes section HTML if notes exist
    * @param {string} notes - The notes content
    * @returns {string} HTML for notes section
    */
    createNotesSection(notes) {
    if (!notes) return '';

    return `
    <div class="card mb-4">
    <div class="card-header">
        <h5 class="mb-0">Notes</h5>
    </div>
    <div class="card-body">
        <div class="notes-content">
        ${notes.replace(/\n/g, '<br>')}
        </div>
    </div>
    </div>`;
    }
};

// Export the handler
export default LeaseOptionHandler;