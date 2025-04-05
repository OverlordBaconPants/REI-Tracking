/**
 * ltr.js
 * Long-Term Rental specific implementation
 */

import UIHelpers from './ui-helpers.js';
import Calculator from './calculator.js';

const LTRHandler = {
  /**
   * Get the HTML template for LTR analysis
   * @returns {string} HTML template
   */
  getTemplate() {
    return `
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
                <input type="number" class="form-control form-control-lg" id="purchase_price" 
                      name="purchase_price" placeholder="Sales price" required>
              </div>
            </div>
            <div class="col-12 col-md-6">
              <label for="after_repair_value" class="form-label">After Repair Value</label>
              <div class="input-group">
                <span class="input-group-text">$</span>
                <input type="number" class="form-control form-control-lg" id="after_repair_value" 
                      name="after_repair_value" placeholder="Post-renovation value" required>
              </div>
            </div>
            <div class="col-12 col-md-6">
              <label for="renovation_costs" class="form-label">Renovation Costs</label>
              <div class="input-group">
                <span class="input-group-text">$</span>
                <input type="number" class="form-control form-control-lg" id="renovation_costs" 
                      name="renovation_costs" placeholder="Expected renovation costs" required>
              </div>
            </div>
            <div class="col-12 col-md-6">
              <label for="renovation_duration" class="form-label">Renovation Duration</label>
              <div class="input-group">
                <input type="number" class="form-control form-control-lg" id="renovation_duration" 
                      name="renovation_duration" placeholder="Duration" required>
                <span class="input-group-text">months</span>
              </div>
            </div>
            <!-- Add Cash to Seller field -->
            <div class="col-12 col-md-6">
              <label for="cash_to_seller" class="form-label">Cash to Seller</label>
              <div class="input-group">
                <span class="input-group-text">$</span>
                <input type="number" class="form-control form-control-lg" id="cash_to_seller" 
                      name="cash_to_seller" placeholder="Cash paid directly to seller">
              </div>
            </div>
            <!-- Add Assignment Fee field -->
            <div class="col-12 col-md-6">
              <label for="assignment_fee" class="form-label">Assignment Fee</label>
              <div class="input-group">
                <span class="input-group-text">$</span>
                <input type="number" class="form-control form-control-lg" id="assignment_fee" 
                      name="assignment_fee" placeholder="Assignment fee if any">
              </div>
            </div>
            <!-- Add Closing Costs field -->
            <div class="col-12 col-md-6">
              <label for="closing_costs" class="form-label">Closing Costs</label>
              <div class="input-group">
                <span class="input-group-text">$</span>
                <input type="number" class="form-control form-control-lg" id="closing_costs" 
                      name="closing_costs" placeholder="Base closing costs">
              </div>
            </div>
            <!-- Add Marketing Costs field -->
            <div class="col-12 col-md-6">
              <label for="marketing_costs" class="form-label">Marketing Costs</label>
              <div class="input-group">
                <span class="input-group-text">$</span>
                <input type="number" class="form-control form-control-lg" id="marketing_costs" 
                      name="marketing_costs" placeholder="Marketing costs if any">
              </div>
            </div>
            <!-- Add Furnishing Costs field for PadSplit -->
            <div class="col-12 col-md-6 padsplit-field" style="display: none;">
              <label for="furnishing_costs" class="form-label">Furnishing Costs</label>
              <div class="input-group">
                <span class="input-group-text">$</span>
                <input type="number" class="form-control form-control-lg" id="furnishing_costs" 
                  name="furnishing_costs" placeholder="PadSplit furnishing costs" required>
              </div>
            </div>
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
                      name="monthly_rent" placeholder="Expected monthly rent" required>
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

      <!-- Add Balloon Payment Section -->
      <div class="card mb-4" id="balloon-payment-section">
        <div class="card-header bg-primary">
          <div class="d-flex justify-content-between align-items-center">
            <h5 class="mb-0 text-white">Balloon Payment</h5>
            <div class="form-check form-switch">
              <input class="form-check-input" type="checkbox" id="has_balloon_payment" 
                    name="has_balloon_payment" role="switch">
              <label class="form-check-label text-white fw-bold" for="has_balloon_payment">
                Enable
              </label>
            </div>
          </div>
        </div>
        <div class="card-body" id="balloon-payment-details" style="display: none;">
          <div class="row g-3">
            <div class="col-12 col-md-6">
              <label for="balloon_due_date" class="form-label">Balloon Payment Due Date</label>
              <input type="date" class="form-control form-control-lg" id="balloon_due_date" 
                    name="balloon_due_date">
            </div>
            <div class="col-12 col-md-6">
              <label for="balloon_refinance_ltv_percentage" class="form-label">Refinance LTV (%)</label>
              <div class="input-group">
                <input type="number" class="form-control form-control-lg" id="balloon_refinance_ltv_percentage" 
                      name="balloon_refinance_ltv_percentage" step="0.01" min="0" max="100">
                <span class="input-group-text">%</span>
              </div>
            </div>
            <div class="col-12 col-md-6">
              <label for="balloon_refinance_loan_amount" class="form-label">Refinance Loan Amount</label>
              <div class="input-group">
                <span class="input-group-text">$</span>
                <input type="number" class="form-control form-control-lg" id="balloon_refinance_loan_amount" 
                      name="balloon_refinance_loan_amount">
              </div>
            </div>
            <div class="col-12 col-md-6">
              <label for="balloon_refinance_loan_interest_rate" class="form-label">Refinance Interest Rate (%)</label>
              <div class="input-group">
                <input type="number" class="form-control form-control-lg" id="balloon_refinance_loan_interest_rate" 
                      name="balloon_refinance_loan_interest_rate" step="0.025">
                <span class="input-group-text">%</span>
              </div>
            </div>
            <div class="col-12 col-md-6">
              <label for="balloon_refinance_loan_term" class="form-label">Refinance Loan Term (months)</label>
              <input type="number" class="form-control form-control-lg" id="balloon_refinance_loan_term" 
                    name="balloon_refinance_loan_term">
            </div>
            <div class="col-12 col-md-6">
              <label for="balloon_refinance_loan_down_payment" class="form-label">Refinance Down Payment</label>
              <div class="input-group">
                <span class="input-group-text">$</span>
                <input type="number" class="form-control form-control-lg" id="balloon_refinance_loan_down_payment" 
                      name="balloon_refinance_loan_down_payment">
              </div>
            </div>
            <div class="col-12 col-md-6">
              <label for="balloon_refinance_loan_closing_costs" class="form-label">Refinance Closing Costs</label>
              <div class="input-group">
                <span class="input-group-text">$</span>
                <input type="number" class="form-control form-control-lg" id="balloon_refinance_loan_closing_costs" 
                      name="balloon_refinance_loan_closing_costs">
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
          <div class="list-group list-group-flush">
            <div class="row g-0">
              <div class="col-12 col-md-6">
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <label for="property_taxes" class="form-label">Monthly Property Taxes</label>
                  <div class="input-group">
                    <span class="input-group-text">$</span>
                    <input type="number" class="form-control form-control-lg" id="property_taxes" 
                          name="property_taxes" placeholder="Monthly taxes" required>
                  </div>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <label for="insurance" class="form-label">Monthly Insurance</label>
                  <div class="input-group">
                    <span class="input-group-text">$</span>
                    <input type="number" class="form-control form-control-lg" id="insurance" 
                          name="insurance" placeholder="Monthly insurance" required>
                  </div>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <label for="hoa_coa_coop" class="form-label">HOA/COA/COOP</label>
                  <div class="input-group">
                    <span class="input-group-text">$</span>
                    <input type="number" class="form-control form-control-lg" id="hoa_coa_coop" 
                          name="hoa_coa_coop" placeholder="Monthly association fees" required>
                  </div>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <label for="management_fee_percentage" class="form-label">Management Fee</label>
                  <div class="input-group">
                    <input type="number" class="form-control form-control-lg" id="management_fee_percentage" 
                          name="management_fee_percentage" value="8" min="0" max="100" step="0.5" required>
                    <span class="input-group-text">%</span>
                  </div>
                </div>
              </div>
              <div class="col-12 col-md-6">
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <label for="capex_percentage" class="form-label">CapEx</label>
                  <div class="input-group">
                    <input type="number" class="form-control form-control-lg" id="capex_percentage" 
                          name="capex_percentage" value="2" min="0" max="100" step="1" required>
                    <span class="input-group-text">%</span>
                  </div>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <label for="vacancy_percentage" class="form-label">Vacancy Rate</label>
                  <div class="input-group">
                    <input type="number" class="form-control form-control-lg" id="vacancy_percentage" 
                          name="vacancy_percentage" value="4" min="0" max="100" step="1" required>
                    <span class="input-group-text">%</span>
                  </div>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <label for="repairs_percentage" class="form-label">Repairs</label>
                  <div class="input-group">
                    <input type="number" class="form-control form-control-lg" id="repairs_percentage" 
                          name="repairs_percentage" value="2" min="0" max="100" step="1" required>
                    <span class="input-group-text">%</span>
                  </div>
                </div>
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
  },
  
  /**
   * Get HTML template for a loan field set
   * @param {number} loanNumber - The loan number
   * @returns {string} HTML template
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
   * Initialize LTR-specific handlers
   */
  initHandlers() {
    this.initLoanHandlers();
    this.initBalloonPaymentHandlers();
    this.initPadSplitFields();
  },
  
  /**
   * Initialize loan management handlers
   */
  initLoanHandlers() {
    const addLoanBtn = document.getElementById('add-loan-btn');
    const loansContainer = document.getElementById('loans-container');
    
    if (!addLoanBtn || !loansContainer || addLoanBtn.hasAttribute('data-initialized')) {
      return;
    }

    // Mark as initialized
    addLoanBtn.setAttribute('data-initialized', 'true');
    
    // Add first loan by default if container is empty
    if (loansContainer.children.length === 0) {
      loansContainer.insertAdjacentHTML('beforeend', this.getLoanFieldsHTML(1));
    }
    
    // Event listener for adding loans
    addLoanBtn.addEventListener('click', () => {
      const loanCount = loansContainer.querySelectorAll('.loan-section').length + 1;
      
      if (loanCount <= 3) {  // Maximum 3 loans allowed
        loansContainer.insertAdjacentHTML('beforeend', this.getLoanFieldsHTML(loanCount));
        
        if (loanCount >= 3) {
          addLoanBtn.style.display = 'none';
        }
      }
    });

    // Event delegation for removing loans
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
   * Initialize balloon payment handlers
   */
  initBalloonPaymentHandlers() {
    const balloonToggle = document.getElementById('has_balloon_payment');
    const balloonDetails = document.getElementById('balloon-payment-details');
    
    if (!balloonToggle || !balloonDetails) {
      return;
    }

    // Remove any existing event listeners
    const newToggle = balloonToggle.cloneNode(true);
    balloonToggle.parentNode.replaceChild(newToggle, balloonToggle);
    
    // Set initial state
    if (newToggle.checked) {
      balloonDetails.style.display = 'block';
      this.setBalloonFieldsRequired(true);
    } else {
      this.clearBalloonPaymentFields();
      balloonDetails.style.display = 'none';
    }

    // Add event listener to toggle
    newToggle.addEventListener('change', (e) => {
      // Toggle display with animation
      if (e.target.checked) {
        balloonDetails.style.display = 'block';
        // Optional: add fade-in effect
        balloonDetails.style.opacity = '0';
        setTimeout(() => {
          balloonDetails.style.opacity = '1';
          balloonDetails.style.transition = 'opacity 0.3s ease-in-out';
        }, 0);
        
        this.setBalloonFieldsRequired(true);
      } else {
        balloonDetails.style.opacity = '0';
        setTimeout(() => {
          balloonDetails.style.display = 'none';
          // Clear fields when hiding
          this.clearBalloonPaymentFields();
        }, 300);
        
        this.setBalloonFieldsRequired(false);
      }
    });
  },
  
  /**
   * Set balloon payment fields as required or not
   * @param {boolean} required - Whether fields are required
   */
  setBalloonFieldsRequired(required) {
    const balloonInputs = document.querySelectorAll('#balloon-payment-details input:not([type="checkbox"])');
    balloonInputs.forEach(input => {
      input.required = required;
    });
  },
  
  /**
   * Clear balloon payment fields
   */
  clearBalloonPaymentFields() {
    const fields = [
      'balloon_due_date',
      'balloon_refinance_ltv_percentage',
      'balloon_refinance_loan_amount',
      'balloon_refinance_loan_interest_rate',
      'balloon_refinance_loan_term',
      'balloon_refinance_loan_down_payment',
      'balloon_refinance_loan_closing_costs'
    ];
    
    fields.forEach(fieldId => {
      const field = document.getElementById(fieldId);
      if (field) {
        field.value = '';
        field.required = false;
      }
    });
  },
  
  /**
   * Initialize PadSplit-specific fields
   */
  initPadSplitFields() {
    const analysisType = document.getElementById('analysis_type');
    if (!analysisType) return;
    
    const isPadSplit = analysisType.value.includes('PadSplit');
    const padSplitFields = document.querySelectorAll('.padsplit-field');
    
    padSplitFields.forEach(field => {
      field.style.display = isPadSplit ? 'block' : 'none';
      const inputs = field.querySelectorAll('input');
      inputs.forEach(input => {
        input.required = isPadSplit;
        if (!isPadSplit) {
          input.value = '';
        }
      });
    });
  },
  
  /**
   * Populate form fields with analysis data
   * @param {Object} analysis - Analysis data
   */
  populateFields(analysis) {
    // Check for LTR type and variants
    if (!analysis.analysis_type.includes('LTR') && analysis.analysis_type !== 'PadSplit LTR') {
      console.warn('Attempted to populate non-LTR analysis with LTR handler');
      return;
    }
    
    // Set purchase details
    UIHelpers.setFieldValue('purchase_price', analysis.purchase_price);
    UIHelpers.setFieldValue('after_repair_value', analysis.after_repair_value);
    UIHelpers.setFieldValue('renovation_costs', analysis.renovation_costs);
    UIHelpers.setFieldValue('renovation_duration', analysis.renovation_duration);
    UIHelpers.setFieldValue('cash_to_seller', analysis.cash_to_seller);
    UIHelpers.setFieldValue('assignment_fee', analysis.assignment_fee);
    UIHelpers.setFieldValue('closing_costs', analysis.closing_costs);
    UIHelpers.setFieldValue('marketing_costs', analysis.marketing_costs);
    
    // Set monthly rent
    UIHelpers.setFieldValue('monthly_rent', analysis.monthly_rent);
    
    // Set operating expenses
    UIHelpers.setFieldValue('property_taxes', analysis.property_taxes);
    UIHelpers.setFieldValue('insurance', analysis.insurance);
    UIHelpers.setFieldValue('hoa_coa_coop', analysis.hoa_coa_coop);
    UIHelpers.setFieldValue('management_fee_percentage', analysis.management_fee_percentage);
    UIHelpers.setFieldValue('capex_percentage', analysis.capex_percentage);
    UIHelpers.setFieldValue('vacancy_percentage', analysis.vacancy_percentage);
    UIHelpers.setFieldValue('repairs_percentage', analysis.repairs_percentage);
    
    // Set balloon payment fields
    const hasBalloon = analysis.has_balloon_payment;
    const balloonToggle = document.getElementById('has_balloon_payment');
    const balloonDetails = document.getElementById('balloon-payment-details');
    
    if (balloonToggle && balloonDetails) {
      balloonToggle.checked = hasBalloon;
      balloonDetails.style.display = hasBalloon ? 'block' : 'none';
      
      if (hasBalloon) {
        UIHelpers.setFieldValue('balloon_due_date', analysis.balloon_due_date);
        UIHelpers.setFieldValue('balloon_refinance_ltv_percentage', analysis.balloon_refinance_ltv_percentage);
        UIHelpers.setFieldValue('balloon_refinance_loan_amount', analysis.balloon_refinance_loan_amount);
        UIHelpers.setFieldValue('balloon_refinance_loan_interest_rate', analysis.balloon_refinance_loan_interest_rate);
        UIHelpers.setFieldValue('balloon_refinance_loan_term', analysis.balloon_refinance_loan_term);
        UIHelpers.setFieldValue('balloon_refinance_loan_down_payment', analysis.balloon_refinance_loan_down_payment);
        UIHelpers.setFieldValue('balloon_refinance_loan_closing_costs', analysis.balloon_refinance_loan_closing_costs);
        this.setBalloonFieldsRequired(true);
      } else {
        this.clearBalloonPaymentFields();
      }
    }
    
    // Set loan fields
    const loansContainer = document.getElementById('loans-container');
    if (loansContainer) {
      // Clear existing loans
      loansContainer.innerHTML = '';
      
      // Add each existing loan
      let loanCount = 0;
      for (let i = 1; i <= 3; i++) {
        const prefix = `loan${i}`;
        const amount = parseFloat(analysis[`${prefix}_loan_amount`] || 0);
        
        if (amount > 0) {
          loanCount++;
          // Insert loan HTML
          loansContainer.insertAdjacentHTML('beforeend', this.getLoanFieldsHTML(loanCount));
          
          // Populate loan fields
          UIHelpers.setFieldValue(`${prefix}_loan_name`, analysis[`${prefix}_loan_name`]);
          UIHelpers.setFieldValue(`${prefix}_loan_amount`, analysis[`${prefix}_loan_amount`]);
          UIHelpers.setFieldValue(`${prefix}_loan_interest_rate`, analysis[`${prefix}_loan_interest_rate`]);
          UIHelpers.setFieldValue(`${prefix}_loan_term`, analysis[`${prefix}_loan_term`]);
          UIHelpers.setFieldValue(`${prefix}_loan_down_payment`, analysis[`${prefix}_loan_down_payment`]);
          UIHelpers.setFieldValue(`${prefix}_loan_closing_costs`, analysis[`${prefix}_loan_closing_costs`]);
          UIHelpers.setFieldValue(`${prefix}_interest_only`, analysis[`${prefix}_interest_only`]);
        }
      }
      
      // If no loans, add a default one
      if (loanCount === 0) {
        loansContainer.insertAdjacentHTML('beforeend', this.getLoanFieldsHTML(1));
      }
      
      // Hide add loan button if max loans reached
      const addLoanBtn = document.getElementById('add-loan-btn');
      if (addLoanBtn) {
        addLoanBtn.style.display = loanCount >= 3 ? 'none' : 'block';
      }
    }
    
    // Set PadSplit-specific fields
    if (analysis.analysis_type === 'PadSplit LTR') {
      UIHelpers.setFieldValue('furnishing_costs', analysis.furnishing_costs);
      // Ensure PadSplit fields are visible
      document.querySelectorAll('.padsplit-field').forEach(field => {
        field.style.display = 'block';
      });
    }
  },
  
  /**
   * Process form data before submission
   * @param {FormData} formData - The form data
   * @param {Object} analysisData - The processed analysis data
   * @returns {Object} The processed analysis data
   */
  processFormData(formData, analysisData) {
    // Check for PadSplit type
    const isPadSplit = analysisData.analysis_type && analysisData.analysis_type.includes('PadSplit');
    
    // Handle balloon payment toggle
    const hasBalloon = formData.get('has_balloon_payment') === 'on';
    analysisData.has_balloon_payment = hasBalloon;
    
    // Clear balloon fields if not enabled
    if (!hasBalloon) {
      analysisData.balloon_due_date = null;
      analysisData.balloon_refinance_ltv_percentage = 0;
      analysisData.balloon_refinance_loan_amount = 0;
      analysisData.balloon_refinance_loan_interest_rate = 0;
      analysisData.balloon_refinance_loan_term = 0;
      analysisData.balloon_refinance_loan_down_payment = 0;
      analysisData.balloon_refinance_loan_closing_costs = 0;
    }
    
    // Handle interest-only checkboxes
    for (let i = 1; i <= 3; i++) {
      const interestOnlyField = `loan${i}_interest_only`;
      analysisData[interestOnlyField] = formData.get(interestOnlyField) === 'on';
    }
    
    // Handle PadSplit-specific fields
    if (!isPadSplit) {
      analysisData.furnishing_costs = 0;
    }
    
    // Handle numeric fields
    const numericFields = [
      'purchase_price', 'after_repair_value', 'renovation_costs', 'renovation_duration',
      'monthly_rent', 'property_taxes', 'insurance', 'hoa_coa_coop',
      'cash_to_seller', 'assignment_fee', 'closing_costs', 'marketing_costs',
      'balloon_refinance_ltv_percentage', 'balloon_refinance_loan_amount', 
      'balloon_refinance_loan_interest_rate', 'balloon_refinance_loan_term',
      'balloon_refinance_loan_down_payment', 'balloon_refinance_loan_closing_costs'
    ];
    
    numericFields.forEach(field => {
      if (field in analysisData) {
        analysisData[field] = UIHelpers.toRawNumber(analysisData[field]);
      }
    });
    
    // Handle percentage fields
    const percentageFields = [
      'management_fee_percentage', 'capex_percentage', 
      'vacancy_percentage', 'repairs_percentage'
    ];
    
    percentageFields.forEach(field => {
      if (field in analysisData) {
        analysisData[field] = UIHelpers.toRawNumber(analysisData[field]);
      }
    });
    
    // Handle loan fields
    for (let i = 1; i <= 3; i++) {
      const loanFields = [
        `loan${i}_loan_amount`, `loan${i}_loan_interest_rate`, `loan${i}_loan_term`,
        `loan${i}_loan_down_payment`, `loan${i}_loan_closing_costs`
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
    
    // Determine if this has balloon payment
    const hasBalloon = this.hasBalloonData(analysis);
    
    // Build the report content
    let reportContent = `
      <!-- Purchase Details Card -->
      <div class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0">Purchase Details</h5>
        </div>
        <div class="card-body">
          <div class="list-group list-group-flush">
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
              <span>Purchase Price</span>
              <strong>${UIHelpers.formatDisplayValue(analysis.purchase_price)}</strong>
            </div>
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
              <span>After Repair Value</span>
              <strong>${UIHelpers.formatDisplayValue(analysis.after_repair_value)}</strong>
            </div>
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
              <span>Renovation Costs</span>
              <strong>${UIHelpers.formatDisplayValue(analysis.renovation_costs)}</strong>
            </div>
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
              <span>Renovation Duration</span>
              <strong>${analysis.renovation_duration} months</strong>
            </div>
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
              <span>Cash to Seller</span>
              <strong>${UIHelpers.formatDisplayValue(analysis.cash_to_seller)}</strong>
            </div>
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
              <span>Closing Costs</span>
              <strong>${UIHelpers.formatDisplayValue(analysis.closing_costs)}</strong>
            </div>
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
              <span>Assignment Fee</span>
              <strong>${UIHelpers.formatDisplayValue(analysis.assignment_fee)}</strong>
            </div>
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
              <span>Marketing Costs</span>
              <strong>${UIHelpers.formatDisplayValue(analysis.marketing_costs)}</strong>
            </div>
            ${analysis.analysis_type.includes('PadSplit') ? `
              <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                <span>Furnishing Costs</span>
                <strong>${UIHelpers.formatDisplayValue(analysis.furnishing_costs)}</strong>
              </div>
            ` : ''}
          </div>
        </div>
      </div>
    
      <!-- Income & Returns Card -->
      <div class="card mb-4">
        <div class="card-header">
          <div class="d-flex justify-content-between align-items-center">
            <h5 class="mb-0">
              ${hasBalloon ? 'Pre-Balloon Financial Overview' : 'Income & Returns'}
            </h5>
            ${hasBalloon ? 
              `<span class="badge bg-primary">Balloon Due: ${new Date(analysis.balloon_due_date).toLocaleDateString()}</span>` 
              : ''}
          </div>
        </div>
        <div class="card-body">
          <div class="list-group list-group-flush">
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
              <span>Monthly Rent</span>
              <strong>${UIHelpers.formatDisplayValue(analysis.monthly_rent)}</strong>
            </div>
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
              <span class="d-flex align-items-center">
                Monthly Cash Flow
                <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" data-bs-html="true" 
                title="Monthly income after all operating expenses and ${hasBalloon ? 'initial ' : ''}loan payments">
                </i>
                </span>
              <strong>${hasBalloon ? 
                metrics.pre_balloon_monthly_cash_flow :
                metrics.monthly_cash_flow}</strong>
            </div>
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
              <span class="d-flex align-items-center">
                Annual Cash Flow
                <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" data-bs-html="true" 
                title="Monthly cash flow × 12 months">
                </i>
              </span>
              <strong>${hasBalloon ? 
                metrics.pre_balloon_annual_cash_flow :
                metrics.annual_cash_flow}</strong>
            </div>
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
              <span class="d-flex align-items-center">
                Cash-on-Cash Return
                <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" data-bs-html="true" 
                title="${hasBalloon ? 
                  'Based on initial investment before balloon refinance' : 
                  '(Annual Cash Flow ÷ Total Cash Invested) × 100'}">
                </i>
              </span>
              <strong>${metrics.cash_on_cash_return}</strong>
            </div>
          </div>
        </div>
      </div>

      <!-- Operating Expenses Card -->
      <div class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0">
            ${hasBalloon ? 'Pre-Balloon Operating Expenses' : 'Operating Expenses'}
          </h5>
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
                ${analysis.analysis_type.includes('PadSplit') ? `
                  <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                    <span>Utilities</span>
                    <strong>${UIHelpers.formatDisplayValue(analysis.utilities)}</strong>
                  </div>
                  <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                    <span>Internet</span>
                    <strong>${UIHelpers.formatDisplayValue(analysis.internet)}</strong>
                  </div>
                  <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                    <span>Cleaning</span>
                    <strong>${UIHelpers.formatDisplayValue(analysis.cleaning)}</strong>
                  </div>
                ` : ''}
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
                ${analysis.analysis_type.includes('PadSplit') ? `
                  <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                    <span>Pest Control</span>
                    <strong>${UIHelpers.formatDisplayValue(analysis.pest_control)}</strong>
                  </div>
                  <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                    <span>Landscaping</span>
                    <strong>${UIHelpers.formatDisplayValue(analysis.landscaping)}</strong>
                  </div>
                  <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                    <span class="d-flex align-items-center">
                      Platform Fee
                      <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" data-bs-html="true" 
                      title="PadSplit platform fee based on monthly rent">
                      </i>
                    </span>
                    <div class="text-end">
                      <div class="small text-muted">
                        ${UIHelpers.formatDisplayValue(analysis.padsplit_platform_percentage, 'percentage')}
                      </div>
                      <strong>${UIHelpers.formatDisplayValue(analysis.monthly_rent * (analysis.padsplit_platform_percentage / 100))}</strong>
                    </div>
                  </div>
                ` : ''}
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
          ${this.generateLoanDetailsContent(analysis)}
        </div>
      </div>
    `;
    
    // Add notes if present
    if (analysis.notes) {
      reportContent += `
        <div class="card mb-4">
          <div class="card-header">
            <h5 class="mb-0">Notes</h5>
          </div>
          <div class="card-body">
            <div class="notes-content">
              ${analysis.notes.replace(/\n/g, '<br>')}
            </div>
          </div>
        </div>
      `;
    }
    
    return reportContent;
  },
  
  /**
   * Generate loan details content for the report
   * @param {Object} analysis - The analysis data
   * @returns {string} HTML loan details content
   */
  generateLoanDetailsContent(analysis) {
    // Check for balloon payment
    if (this.hasBalloonData(analysis)) {
      return this.generateBalloonLoanContent(analysis);
    }
    
    // Regular loans
    const loanPrefixes = ['loan1', 'loan2', 'loan3'];
    let hasLoans = false;
    
    let html = '<div class="accordion" id="regularLoansAccordion">';
    
    for (const prefix of loanPrefixes) {
      // Check if loan exists by verifying amount is greater than 0
      const loanAmount = UIHelpers.toRawNumber(analysis[`${prefix}_loan_amount`]);
      if (loanAmount > 0) {
        hasLoans = true;
        
        // Get loan payment from calculated metrics
        const loanPayment = analysis.calculated_metrics?.[`${prefix}_loan_payment`];
        
        html += `
          <div class="accordion-item">
            <h6 class="accordion-header">
              <button class="accordion-button ${prefix !== 'loan1' ? 'collapsed' : ''}" type="button" 
                    data-bs-toggle="collapse" data-bs-target="#${prefix}Collapse">
                ${analysis[`${prefix}_loan_name`] || `Loan ${prefix.slice(-1)}`}
              </button>
            </h6>
            <div id="${prefix}Collapse" class="accordion-collapse collapse ${prefix === 'loan1' ? 'show' : ''}" 
                data-bs-parent="#regularLoansAccordion">
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
                      <span class="badge ${analysis[`${prefix}_interest_only`] ? 'bg-success' : 'bg-info'} ms-2">
                        ${analysis[`${prefix}_interest_only`] ? 'Interest Only' : 'Amortized'}
                      </span>
                    </div>
                  </div>
                  <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                    <span>Term</span>
                    <strong>${analysis[`${prefix}_loan_term`] || '0'} months</strong>
                  </div>
                  <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                    <span class="d-flex align-items-center">
                      Monthly Payment
                      <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" 
                        title="${analysis[`${prefix}_interest_only`] ? 
                            'Interest-only payment on loan' : 
                            'Fully amortized payment including principal and interest'}"></i>
                    </span>
                    <strong>${loanPayment || UIHelpers.formatDisplayValue(0)}</strong>
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
    html += '</div>';
    
    return hasLoans ? html : `
      <div class="text-center py-4">
        <p class="mb-0 text-muted">No loan details available</p>
      </div>`;
  },
  
  /**
   * Generate balloon loan content for the report
   * @param {Object} analysis - The analysis data
   * @returns {string} HTML balloon loan content
   */
  generateBalloonLoanContent(analysis) {
    // Get metrics
    const metrics = analysis.calculated_metrics || {};
    const preMonthlyPayment = metrics.pre_balloon_monthly_payment || 
                             metrics.loan1_loan_payment;
    const postMonthlyPayment = metrics.post_balloon_monthly_payment || 
                              metrics.refinance_loan_payment;
    
    // Get all loan prefixes with existing loans
    const existingLoans = [];
    ['loan1', 'loan2', 'loan3'].forEach(prefix => {
      const loanAmount = UIHelpers.toRawNumber(analysis[`${prefix}_loan_amount`]);
      if (loanAmount > 0) {
        existingLoans.push(prefix);
      }
    });
    
    // Generate HTML for all existing pre-balloon loans
    let preBallooonLoansHTML = '';
    existingLoans.forEach(prefix => {
      const loanPayment = metrics[`${prefix}_loan_payment`];
      preBallooonLoansHTML += `
        <div class="list-group list-group-flush">
          <div class="list-group-item d-flex justify-content-between align-items-center py-3">
            <span>Loan Name</span>
            <strong>${analysis[`${prefix}_loan_name`] || `Loan ${prefix.slice(-1)}`}</strong>
          </div>
          <div class="list-group-item d-flex justify-content-between align-items-center py-3">
            <span>Amount</span>
            <strong>${UIHelpers.formatDisplayValue(analysis[`${prefix}_loan_amount`])}</strong>
          </div>
          <div class="list-group-item d-flex justify-content-between align-items-center py-3">
            <span>Interest Rate</span>
            <div>
              <strong>${UIHelpers.formatDisplayValue(analysis[`${prefix}_loan_interest_rate`], 'percentage')}</strong>
              <span class="badge ${analysis[`${prefix}_interest_only`] ? 'bg-success' : 'bg-info'} ms-2">
                ${analysis[`${prefix}_interest_only`] ? 'Interest Only' : 'Amortized'}
              </span>
            </div>
          </div>
          <div class="list-group-item d-flex justify-content-between align-items-center py-3">
            <span>Term</span>
            <strong>${analysis[`${prefix}_loan_term`] || '0'} months</strong>
          </div>
          <div class="list-group-item d-flex justify-content-between align-items-center py-3">
            <span class="d-flex align-items-center">
              Monthly Payment
              <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" 
                title="${analysis[`${prefix}_interest_only`] ? 
                    'Interest-only payment on loan' : 
                    'Fully amortized payment including principal and interest'}"></i>
            </span>
            <strong>${loanPayment || UIHelpers.formatDisplayValue(0)}</strong>
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
        ${prefix !== existingLoans[existingLoans.length - 1] ? '<hr class="my-3">' : ''}
      `;
    });
    
    return `
      <div class="accordion" id="balloonLoanAccordion">
        <!-- Pre-Balloon Section -->
        <div class="accordion-item">
          <h6 class="accordion-header">
            <button class="accordion-button" type="button" data-bs-toggle="collapse" 
                  data-bs-target="#preBalloonCollapse">
              Original Loans (Pre-Balloon)
            </button>
          </h6>
          <div id="preBalloonCollapse" class="accordion-collapse collapse show" 
              data-bs-parent="#balloonLoanAccordion">
            <div class="accordion-body p-0">
              ${preBallooonLoansHTML}
              <div class="list-group-item d-flex justify-content-between align-items-center py-3 bg-light">
                <span class="fw-bold">Combined Monthly Payment</span>
                <strong>${preMonthlyPayment || UIHelpers.formatDisplayValue(0)}</strong>
              </div>
              <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                <span>Balloon Due Date</span>
                <strong>${new Date(analysis.balloon_due_date).toLocaleDateString()}</strong>
              </div>
            </div>
          </div>
        </div>

        <!-- Post-Balloon Section -->
        <div class="accordion-item">
          <h6 class="accordion-header">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" 
                  data-bs-target="#postBalloonCollapse">
              Balloon Refinance Terms
            </button>
          </h6>
          <div id="postBalloonCollapse" class="accordion-collapse collapse" 
              data-bs-parent="#balloonLoanAccordion">
            <div class="accordion-body p-0">
              <div class="list-group list-group-flush">
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <span>Refinance Amount</span>
                  <strong>${UIHelpers.formatDisplayValue(analysis.balloon_refinance_loan_amount)}</strong>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <span>Interest Rate</span>
                  <strong>${UIHelpers.formatDisplayValue(analysis.balloon_refinance_loan_interest_rate, 'percentage')}</strong>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <span>Term</span>
                  <strong>${analysis.balloon_refinance_loan_term} months</strong>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <span class="d-flex align-items-center">
                    Monthly Payment
                    <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" 
                      title="Monthly payment after balloon refinance"></i>
                  </span>
                  <strong>${postMonthlyPayment || UIHelpers.formatDisplayValue(0)}</strong>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <span>LTV</span>
                  <strong>${UIHelpers.formatDisplayValue(analysis.balloon_refinance_ltv_percentage, 'percentage')}</strong>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <span>Down Payment</span>
                  <strong>${UIHelpers.formatDisplayValue(analysis.balloon_refinance_loan_down_payment)}</strong>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <span>Closing Costs</span>
                  <strong>${UIHelpers.formatDisplayValue(analysis.balloon_refinance_loan_closing_costs)}</strong>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>`;
  },
  
  /**
   * Check if the analysis has balloon payment data
   * @param {Object} analysis - The analysis data
   * @returns {boolean} Whether the analysis has balloon payment data
   */
  hasBalloonData(analysis) {
    return analysis.has_balloon_payment || (
      UIHelpers.toRawNumber(analysis.balloon_refinance_loan_amount) > 0 && 
      analysis.balloon_due_date && 
      UIHelpers.toRawNumber(analysis.balloon_refinance_ltv_percentage) > 0
    );
  }
};

export default LTRHandler;
