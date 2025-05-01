/**
 * brrrr.js
 * BRRRR (Buy, Renovate, Rent, Refinance, Repeat) strategy specific implementation
 */

import UIHelpers from './ui_helpers.js';
import Calculator from './calculator.js';
import AnalysisCore from './core.js';

const BRRRRHandler = {
  /**
   * Get the HTML template for BRRRR analysis
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
                <input type="number" class="form-control form-control-lg" id="purchase_price" 
                      name="purchase_price" placeholder="Sales price" required>
              </div>
            </div>
            <div class="col-12 col-md-6">
              <label for="closing_costs" class="form-label">Closing Costs</label>
              <div class="input-group">
                <span class="input-group-text">$</span>
                <input type="number" class="form-control form-control-lg" id="closing_costs" 
                      name="closing_costs" placeholder="Purchase closing costs" required>
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

      <!-- Initial Financing -->
      <div class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0">Initial Financing</h5>
        </div>
        <div class="card-body">
          <div class="row g-3">
            <div class="col-12 col-md-6">
              <label for="initial_loan_amount" class="form-label">Initial Loan Amount</label>
              <div class="input-group">
                <span class="input-group-text">$</span>
                <input type="number" class="form-control form-control-lg" id="initial_loan_amount" 
                      name="initial_loan_amount" placeholder="Purchase loan amount" required>
              </div>
            </div>
            <div class="col-12 col-md-6">
              <label for="initial_loan_down_payment" class="form-label">Initial Down Payment</label>
              <div class="input-group">
                <span class="input-group-text">$</span>
                <input type="number" class="form-control form-control-lg" id="initial_loan_down_payment" 
                      name="initial_loan_down_payment" placeholder="Down payment amount" required>
              </div>
            </div>
            <div class="col-md-6 mb-3">
              <label for="initial_loan_interest_rate" class="form-label">Initial Interest Rate (%)</label>
              <input type="number" class="form-control" id="initial_loan_interest_rate" 
                    name="initial_loan_interest_rate" placeholder="Interest rate" step="0.025" required>
              <div class="form-check mt-2">
                <input class="form-check-input" type="checkbox" id="initial_interest_only" 
                      name="initial_interest_only">
                <label class="form-check-label" for="initial_interest_only">
                  Interest Only
                </label>
              </div>
            </div>
            <div class="col-12 col-md-6">
              <label for="initial_loan_term" class="form-label">Initial Loan Term</label>
              <div class="input-group">
                <input type="number" class="form-control form-control-lg" id="initial_loan_term" 
                      name="initial_loan_term" placeholder="Loan duration" required>
                <span class="input-group-text">months</span>
              </div>
            </div>
            <div class="col-12 col-md-6">
              <label for="initial_loan_closing_costs" class="form-label">Initial Closing Costs</label>
              <div class="input-group">
                <span class="input-group-text">$</span>
                <input type="number" class="form-control form-control-lg" id="initial_loan_closing_costs" 
                       name="initial_loan_closing_costs" placeholder="Initial loan closing costs" required>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Refinance Details -->
      <div class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0">Refinance Details</h5>
        </div>
        <div class="card-body">
          <div class="row g-3">
            <div class="col-12 col-md-6">
              <label for="refinance_ltv_percentage" class="form-label">Refinance LTV (%)</label>
              <div class="input-group">
                <input type="number" class="form-control form-control-lg" id="refinance_ltv_percentage" 
                      name="refinance_ltv_percentage" value="75" step="0.5" min="0" max="100" placeholder="LTV percentage" required>
                <span class="input-group-text">%</span>
              </div>
            </div>
            <div class="col-12 col-md-6">
              <label for="refinance_loan_amount" class="form-label">Refinance Amount</label>
              <div class="input-group">
                <span class="input-group-text">$</span>
                <input type="number" class="form-control form-control-lg" id="refinance_loan_amount" 
                      name="refinance_loan_amount" placeholder="Expected refinance amount" required>
              </div>
            </div>
            <div class="col-12 col-md-6">
              <label for="refinance_loan_interest_rate" class="form-label">Refinance Rate</label>
              <div class="input-group">
                <input type="number" class="form-control form-control-lg" id="refinance_loan_interest_rate" 
                      name="refinance_loan_interest_rate" step="0.025" placeholder="Interest rate" required>
                <span class="input-group-text">%</span>
              </div>
            </div>
            <div class="col-12 col-md-6">
              <label for="refinance_loan_term" class="form-label">Refinance Term</label>
              <div class="input-group">
                <input type="number" class="form-control form-control-lg" id="refinance_loan_term" 
                      name="refinance_loan_term" placeholder="Loan duration" required>
                <span class="input-group-text">months</span>
              </div>
            </div>
            <div class="col-12 col-md-6">
              <label for="refinance_loan_closing_costs" class="form-label">Refinance Closing Costs</label>
              <div class="input-group">
                <span class="input-group-text">$</span>
                <input type="number" class="form-control form-control-lg" id="refinance_loan_closing_costs" 
                      name="refinance_loan_closing_costs" placeholder="Expected closing costs" required>
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

      <!-- Operating Expenses -->
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

      <!-- PadSplit-specific expenses -->
      <div class="card mb-4 padsplit-field" style="display: none;">
        <div class="card-header">
          <h5 class="mb-0">PadSplit Expenses</h5>
        </div>
        <div class="card-body">
          <div class="row g-3">
            <div class="col-12 col-md-6">
              <label for="utilities" class="form-label">Monthly Utilities</label>
              <div class="input-group">
                <span class="input-group-text">$</span>
                <input type="number" class="form-control form-control-lg" id="utilities" 
                      name="utilities" placeholder="Monthly utilities cost">
              </div>
            </div>
            <div class="col-12 col-md-6">
              <label for="internet" class="form-label">Monthly Internet</label>
              <div class="input-group">
                <span class="input-group-text">$</span>
                <input type="number" class="form-control form-control-lg" id="internet" 
                      name="internet" placeholder="Monthly internet cost">
              </div>
            </div>
            <div class="col-12 col-md-6">
              <label for="cleaning" class="form-label">Monthly Cleaning</label>
              <div class="input-group">
                <span class="input-group-text">$</span>
                <input type="number" class="form-control form-control-lg" id="cleaning" 
                      name="cleaning" placeholder="Monthly cleaning cost">
              </div>
            </div>
            <div class="col-12 col-md-6">
              <label for="pest_control" class="form-label">Monthly Pest Control</label>
              <div class="input-group">
                <span class="input-group-text">$</span>
                <input type="number" class="form-control form-control-lg" id="pest_control" 
                      name="pest_control" placeholder="Monthly pest control cost">
              </div>
            </div>
            <div class="col-12 col-md-6">
              <label for="landscaping" class="form-label">Monthly Landscaping</label>
              <div class="input-group">
                <span class="input-group-text">$</span>
                <input type="number" class="form-control form-control-lg" id="landscaping" 
                      name="landscaping" placeholder="Monthly landscaping cost">
              </div>
            </div>
            <div class="col-12 col-md-6">
              <label for="padsplit_platform_percentage" class="form-label">PadSplit Platform Fee</label>
              <div class="input-group">
                <input type="number" class="form-control form-control-lg" id="padsplit_platform_percentage" 
                      name="padsplit_platform_percentage" placeholder="Platform fee percentage" min="0" max="100" step="0.5" value="15">
                <span class="input-group-text">%</span>
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
   * Initialize BRRRR-specific handlers
   */
  async initHandlers() {
    this.initRefinanceCalculations();
    this.initPadSplitFields();
    this.initMaximumAllowableOfferCalc();
    this.initClosingCostSyncHandler();
  },

  /**
   * Initialize refinance calculations
   * Sets up automatic calculation of refinance loan details based on ARV and LTV
   */
  initRefinanceCalculations() {
    const arvInput = document.getElementById('after_repair_value');
    const ltvInput = document.getElementById('refinance_ltv_percentage');
    const loanAmountInput = document.getElementById('refinance_loan_amount');
    
    // Function to update refinance calculations
    const updateRefinanceCalcs = () => {
      const arv = UIHelpers.toRawNumber(arvInput?.value) || 0;
      let ltv = 75; // Default to 75% LTV if not specified
      
      // If LTV input exists, use its value
      if (ltvInput && ltvInput.value) {
        ltv = UIHelpers.toRawNumber(ltvInput.value);
      }
      
      // Calculate and set loan amount
      if (loanAmountInput) {
        const loanAmount = (arv * ltv) / 100;
        loanAmountInput.value = loanAmount.toFixed(2);
      }
    };
    
    // Add event listeners
    if (arvInput) {
      arvInput.addEventListener('input', updateRefinanceCalcs);
    }
    
    if (ltvInput) {
      ltvInput.addEventListener('input', updateRefinanceCalcs);
    }
    
    // Initial calculation
    updateRefinanceCalcs();
  },
  
  /**
   * Initialize Maximum Allowable Offer calculator
   * Provides a helper calculation for BRRRR investors
   */
  initMaximumAllowableOfferCalc() {
    // This function is now empty as the MAO button has been removed
    // MAO is now shown in the Comparable Properties and MAO card
  },

  initClosingCostSyncHandler() {
    const closingCostsInput = document.getElementById('closing_costs');
    const initialLoanClosingCostsInput = document.getElementById('initial_loan_closing_costs');
    
    if (closingCostsInput && initialLoanClosingCostsInput) {
      // Sync from closing_costs to initial_loan_closing_costs
      closingCostsInput.addEventListener('input', () => {
        initialLoanClosingCostsInput.value = closingCostsInput.value;
      });
      
      // Sync from initial_loan_closing_costs to closing_costs
      initialLoanClosingCostsInput.addEventListener('input', () => {
        closingCostsInput.value = initialLoanClosingCostsInput.value;
      });
    }
  },
  
  /**
   * Show the Maximum Allowable Offer calculator modal
   */
  showMAOCalculator() {
    // Get values from form
    const arv = UIHelpers.toRawNumber(document.getElementById('after_repair_value')?.value) || 0;
    const renovationCosts = UIHelpers.toRawNumber(document.getElementById('renovation_costs')?.value) || 0;
    const initialClosingCosts = UIHelpers.toRawNumber(document.getElementById('initial_loan_closing_costs')?.value) || 0;
    const refinanceClosingCosts = UIHelpers.toRawNumber(document.getElementById('refinance_loan_closing_costs')?.value) || 0;
    
    // Add PadSplit furnishing costs if applicable
    const isPadSplit = document.getElementById('analysis_type')?.value.includes('PadSplit') || false;
    const furnishingCosts = isPadSplit ? 
      (UIHelpers.toRawNumber(document.getElementById('furnishing_costs')?.value) || 0) : 0;
    
    // Set default values for calculator
    const ltv = 75; // 75% LTV is typical for BRRRR refi
    const profitTarget = 10000; // $10k minimum profit target
    
    // Calculate MAO
    const totalCosts = renovationCosts + initialClosingCosts + refinanceClosingCosts + furnishingCosts;
    const maxLoanAmount = (arv * ltv) / 100;
    const mao = maxLoanAmount - totalCosts - profitTarget;
    
    // Create and show modal
    const modalHtml = `
      <div class="modal fade" id="maoCalculatorModal" tabindex="-1" aria-labelledby="maoCalculatorModalLabel" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="maoCalculatorModalLabel">Maximum Allowable Offer (MAO)</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <div class="alert alert-primary">
                <h5 class="text-center">Estimated MAO: ${UIHelpers.formatDisplayValue(mao)}</h5>
              </div>
              
              <div class="table-responsive">
                <table class="table table-bordered">
                  <tr>
                    <td>After Repair Value (ARV)</td>
                    <td class="text-end">${UIHelpers.formatDisplayValue(arv)}</td>
                  </tr>
                  <tr>
                    <td>Loan-to-Value (LTV)</td>
                    <td class="text-end">${ltv}%</td>
                  </tr>
                  <tr>
                    <td>Refinance Loan Amount</td>
                    <td class="text-end">${UIHelpers.formatDisplayValue(maxLoanAmount)}</td>
                  </tr>
                  <tr>
                    <td>Renovation Costs</td>
                    <td class="text-end">${UIHelpers.formatDisplayValue(renovationCosts)}</td>
                  </tr>
                  <tr>
                    <td>Initial Closing Costs</td>
                    <td class="text-end">${UIHelpers.formatDisplayValue(initialClosingCosts)}</td>
                  </tr>
                  <tr>
                    <td>Refinance Closing Costs</td>
                    <td class="text-end">${UIHelpers.formatDisplayValue(refinanceClosingCosts)}</td>
                  </tr>
                  ${isPadSplit ? `
                  <tr>
                    <td>Furnishing Costs</td>
                    <td class="text-end">${UIHelpers.formatDisplayValue(furnishingCosts)}</td>
                  </tr>
                  ` : ''}
                  <tr>
                    <td>Minimum Profit Target</td>
                    <td class="text-end">${UIHelpers.formatDisplayValue(profitTarget)}</td>
                  </tr>
                </table>
              </div>
              
              <p class="text-muted small">MAO = Refinance Loan Amount - All Costs - Profit Target</p>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
              <button type="button" class="btn btn-primary" id="use-mao-btn">Use This Value</button>
            </div>
          </div>
        </div>
      </div>
    `;
    
    // Append modal to body
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Initialize modal
    const modal = new bootstrap.Modal(document.getElementById('maoCalculatorModal'));
    modal.show();
    
    // Handle "Use This Value" button
    const useBtn = document.getElementById('use-mao-btn');
    if (useBtn) {
      useBtn.addEventListener('click', () => {
        const purchasePriceInput = document.getElementById('purchase_price');
        if (purchasePriceInput) {
          purchasePriceInput.value = Math.round(mao);
          purchasePriceInput.dispatchEvent(new Event('input', { bubbles: true }));
        }
        modal.hide();
      });
    }
    
    // Clean up when modal is hidden
    const modalElement = document.getElementById('maoCalculatorModal');
    if (modalElement) {
      modalElement.addEventListener('hidden.bs.modal', function () {
        this.remove();
      });
    }
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
    // Check for BRRRR type and variants
    if (!analysis.analysis_type.includes('BRRRR')) {
      console.warn('Attempted to populate non-BRRRR analysis with BRRRR handler');
      return;
    }
    
    // Set purchase details
    AnalysisCore.setFieldValue('purchase_price', analysis.purchase_price);
    AnalysisCore.setFieldValue('closing_costs', analysis.initial_loan_closing_costs);
    AnalysisCore.setFieldValue('after_repair_value', analysis.after_repair_value);
    AnalysisCore.setFieldValue('renovation_costs', analysis.renovation_costs);
    AnalysisCore.setFieldValue('renovation_duration', analysis.renovation_duration);
    
    // Set initial loan details
    AnalysisCore.setFieldValue('initial_loan_amount', analysis.initial_loan_amount);
    AnalysisCore.setFieldValue('initial_loan_down_payment', analysis.initial_loan_down_payment);
    AnalysisCore.setFieldValue('initial_loan_interest_rate', analysis.initial_loan_interest_rate);
    AnalysisCore.setFieldValue('initial_loan_term', analysis.initial_loan_term);
    AnalysisCore.setFieldValue('initial_loan_closing_costs', analysis.initial_loan_closing_costs);
    AnalysisCore.setFieldValue('initial_interest_only', analysis.initial_interest_only);
    
    // Set refinance details
    AnalysisCore.setFieldValue('refinance_ltv_percentage', analysis.refinance_ltv_percentage);
    AnalysisCore.setFieldValue('refinance_loan_amount', analysis.refinance_loan_amount);
    AnalysisCore.setFieldValue('refinance_loan_interest_rate', analysis.refinance_loan_interest_rate);
    AnalysisCore.setFieldValue('refinance_loan_term', analysis.refinance_loan_term);
    AnalysisCore.setFieldValue('refinance_loan_closing_costs', analysis.refinance_loan_closing_costs);
    
    // Set monthly rent
    AnalysisCore.setFieldValue('monthly_rent', analysis.monthly_rent);
    
// Set operating expenses
AnalysisCore.setFieldValue('property_taxes', analysis.property_taxes);
AnalysisCore.setFieldValue('insurance', analysis.insurance);
AnalysisCore.setFieldValue('management_fee_percentage', analysis.management_fee_percentage);
AnalysisCore.setFieldValue('capex_percentage', analysis.capex_percentage);
AnalysisCore.setFieldValue('vacancy_percentage', analysis.vacancy_percentage);
AnalysisCore.setFieldValue('repairs_percentage', analysis.repairs_percentage);

// Set PadSplit-specific fields
if (analysis.analysis_type.includes('PadSplit')) {
  AnalysisCore.setFieldValue('furnishing_costs', analysis.furnishing_costs);
  AnalysisCore.setFieldValue('utilities', analysis.utilities);
  AnalysisCore.setFieldValue('internet', analysis.internet);
  AnalysisCore.setFieldValue('cleaning', analysis.cleaning);
  AnalysisCore.setFieldValue('pest_control', analysis.pest_control);
  AnalysisCore.setFieldValue('landscaping', analysis.landscaping);
  AnalysisCore.setFieldValue('padsplit_platform_percentage', analysis.padsplit_platform_percentage);
  
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

// Handle interest-only checkbox
analysisData.initial_interest_only = formData.get('initial_interest_only') === 'on';

// Handle PadSplit-specific fields
if (!isPadSplit) {
  analysisData.furnishing_costs = 0;
}


// Sync closing_costs to initial_loan_closing_costs in case they're not already synced
if ('closing_costs' in analysisData) {
  analysisData.initial_loan_closing_costs = analysisData.closing_costs;
}

// Handle numeric fields
const numericFields = [
  'purchase_price', 'after_repair_value', 'renovation_costs', 'renovation_duration',
  'initial_loan_amount', 'initial_loan_down_payment', 'initial_loan_interest_rate', 
  'initial_loan_term', 'initial_loan_closing_costs', 'closing_costs',
  'refinance_ltv_percentage', 'refinance_loan_amount', 'refinance_loan_interest_rate', 
  'refinance_loan_term', 'refinance_loan_closing_costs',
  'monthly_rent', 'property_taxes', 'insurance'
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

// Calculate additional BRRRR specific values if not provided in metrics
const initialInvestment = UIHelpers.toRawNumber(analysis.purchase_price) + 
                         UIHelpers.toRawNumber(analysis.renovation_costs) +
                         (analysis.analysis_type.includes('PadSplit') ? UIHelpers.toRawNumber(analysis.furnishing_costs) : 0);
                         
const initialLoanAmount = UIHelpers.toRawNumber(analysis.initial_loan_amount);
const refinanceLoanAmount = UIHelpers.toRawNumber(analysis.refinance_loan_amount);
const refinanceClosingCosts = UIHelpers.toRawNumber(analysis.refinance_loan_closing_costs);

// Calculate initial out-of-pocket before refinance
const initialOutOfPocket = Math.max(0, initialInvestment - initialLoanAmount);

// Calculate cash recouped after refinance
const cashRecouped = Math.max(0, refinanceLoanAmount - initialLoanAmount - refinanceClosingCosts);

// Calculate final investment after refinance
const finalInvestment = Math.max(0, initialOutOfPocket - cashRecouped);

// Calculate the actual cash-on-cash return based on final investment if not in metrics
const annualCashFlow = metrics.annual_cash_flow ? 
                      UIHelpers.toRawNumber(metrics.annual_cash_flow) : 
                      UIHelpers.toRawNumber(metrics.monthly_cash_flow || 0) * 12;
                      
const cashOnCashReturn = finalInvestment > 0 ? 
                        (annualCashFlow / finalInvestment) * 100 : 
                        999.99; // Cap at 999.99% for near-zero investments

// Build the report content
return `
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
      <h5 class="mb-0">Income & Returns</h5>
    </div>
    <div class="card-body">
      <div class="list-group list-group-flush">
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
          <span>Property Type</span>
          <strong>${analysis.property_type || 'Not Specified'}</strong>
        </div>
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
          <span>Monthly Rent</span>
          <strong>${UIHelpers.formatDisplayValue(analysis.monthly_rent)}</strong>
        </div>
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
          <span>Monthly Cash Flow</span>
          <strong>${metrics.monthly_cash_flow || '$0.00'}</strong>
        </div>
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
          <span>Annual Cash Flow</span>
          <strong>${metrics.annual_cash_flow || '$0.00'}</strong>
        </div>
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
          <span class="d-flex align-items-center">
            Cash-on-Cash Return
            <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" 
               title="Based on remaining invested capital after refinancing">
            </i>
          </span>
          <strong>${finalInvestment > 0 ? 
                  metrics.cash_on_cash_return || UIHelpers.formatDisplayValue(cashOnCashReturn, 'percentage') : 
                  '999.99%'}</strong>
        </div>
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
          <span>ROI</span>
          <strong>${metrics.roi || '0%'}</strong>
        </div>
      </div>
    </div>
  </div>

  <!-- BRRRR Strategy Details Card -->
  <div class="card mb-4">
    <div class="card-header">
      <h5 class="mb-0">BRRRR Strategy Analysis</h5>
    </div>
    <div class="card-body">
      <div class="list-group list-group-flush">
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
          <span>Initial Investment (Before Financing)</span>
          <strong>${UIHelpers.formatDisplayValue(initialInvestment)}</strong>
        </div>
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
          <span>Initial Loan Amount</span>
          <strong>${UIHelpers.formatDisplayValue(analysis.initial_loan_amount)}</strong>
        </div>
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
          <span class="d-flex align-items-center">
            Initial Out-of-Pocket
            <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" 
               title="Initial investment minus initial loan amount">
            </i>
          </span>
          <strong>${UIHelpers.formatDisplayValue(initialOutOfPocket)}</strong>
        </div>
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
          <span>Refinance Loan Amount</span>
          <strong>${UIHelpers.formatDisplayValue(analysis.refinance_loan_amount)}</strong>
        </div>
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
          <span>Refinance Closing Costs</span>
          <strong>${UIHelpers.formatDisplayValue(analysis.refinance_loan_closing_costs)}</strong>
        </div>
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
          <span class="d-flex align-items-center">
            Cash Recouped From Refinance
            <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" 
               title="Refinance amount minus initial loan payoff minus closing costs">
            </i>
          </span>
          <strong>${metrics.cash_recouped || UIHelpers.formatDisplayValue(cashRecouped)}</strong>
        </div>
        <div class="list-group-item d-flex justify-content-between align-items-center py-3 bg-light">
          <span class="d-flex align-items-center fw-bold">
            Final Cash Invested 
            <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" 
               title="Initial out-of-pocket minus cash recouped from refinance">
            </i>
          </span>
          <strong>${UIHelpers.formatDisplayValue(finalInvestment)}</strong>
        </div>
        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
          <span>Equity Captured</span>
          <strong>${metrics.equity_captured || UIHelpers.formatDisplayValue(
            Math.max(0, UIHelpers.toRawNumber(analysis.after_repair_value) - UIHelpers.toRawNumber(analysis.purchase_price) - UIHelpers.toRawNumber(analysis.renovation_costs))
          )}</strong>
        </div>
      </div>
    </div>
  </div>

  <!-- Financing Card -->
  <div class="card mb-4">
    <div class="card-header">
      <h5 class="mb-0">Financing Details</h5>
    </div>
    <div class="card-body">
      <div class="accordion" id="brrrFinancingAccordion">
        <!-- Initial Loan Section -->
        <div class="accordion-item">
          <h6 class="accordion-header">
            <button class="accordion-button" type="button" data-bs-toggle="collapse" 
                    data-bs-target="#initialLoanCollapse">
              Initial Hard Money Loan
            </button>
          </h6>
          <div id="initialLoanCollapse" class="accordion-collapse collapse show" 
               data-bs-parent="#brrrFinancingAccordion">
            <div class="accordion-body p-0">
              <div class="list-group list-group-flush">
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <span>Amount</span>
                  <strong>${UIHelpers.formatDisplayValue(analysis.initial_loan_amount)}</strong>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <span>Interest Rate</span>
                  <div>
                    <strong>${UIHelpers.formatDisplayValue(analysis.initial_loan_interest_rate, 'percentage')}</strong>
                    <span class="badge ${analysis.initial_interest_only ? 'bg-success' : 'bg-info'} ms-2">
                      ${analysis.initial_interest_only ? 'Interest Only' : 'Amortized'}
                    </span>
                  </div>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <span>Term</span>
                  <strong>${analysis.initial_loan_term} months</strong>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <span>Monthly Payment</span>
                  <strong>${metrics.initial_loan_payment || Calculator.calculateLoanPayment({
                    amount: analysis.initial_loan_amount,
                    interestRate: analysis.initial_loan_interest_rate,
                    term: analysis.initial_loan_term,
                    isInterestOnly: analysis.initial_interest_only
                  })}</strong>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <span>Down Payment</span>
                  <strong>${UIHelpers.formatDisplayValue(analysis.initial_loan_down_payment)}</strong>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <span>Closing Costs</span>
                  <strong>${UIHelpers.formatDisplayValue(analysis.initial_loan_closing_costs)}</strong>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Refinance Section -->
        <div class="accordion-item">
          <h6 class="accordion-header">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" 
                    data-bs-target="#refinanceCollapse">
              Refinance Loan
            </button>
          </h6>
          <div id="refinanceCollapse" class="accordion-collapse collapse" 
               data-bs-parent="#brrrFinancingAccordion">
            <div class="accordion-body p-0">
              <div class="list-group list-group-flush">
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <span>Amount</span>
                  <strong>${UIHelpers.formatDisplayValue(analysis.refinance_loan_amount)}</strong>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <span>Interest Rate</span>
                  <strong>${UIHelpers.formatDisplayValue(analysis.refinance_loan_interest_rate, 'percentage')}</strong>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <span>Term</span>
                  <strong>${analysis.refinance_loan_term} months</strong>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <span>Monthly Payment</span>
                  <strong>${metrics.refinance_loan_payment || Calculator.calculateLoanPayment({
                    amount: analysis.refinance_loan_amount,
                    interestRate: analysis.refinance_loan_interest_rate,
                    term: analysis.refinance_loan_term,
                    isInterestOnly: false // Refinance is typically amortized
                  })}</strong>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <span>LTV Percentage</span>
                  <strong>${UIHelpers.formatDisplayValue(analysis.refinance_ltv_percentage, 'percentage')}</strong>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <span>Closing Costs</span>
                  <strong>${UIHelpers.formatDisplayValue(analysis.refinance_loan_closing_costs)}</strong>
                </div>
              </div>
            </div>
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
              <span>Property Taxes</span>
              <strong>${UIHelpers.formatDisplayValue(analysis.property_taxes)}</strong>
            </div>
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
              <span>Insurance</span>
              <strong>${UIHelpers.formatDisplayValue(analysis.insurance)}</strong>
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
        
        ${analysis.analysis_type.includes('PadSplit') ? `
        <!-- PadSplit-specific expenses -->
        <div class="mt-3">
          <h6 class="mb-2">PadSplit-Specific Expenses</h6>
          <div class="row g-0">
            <div class="col-12 col-md-6">
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
            </div>
            <div class="col-12 col-md-6">
              <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                <span>Pest Control</span>
                <strong>${UIHelpers.formatDisplayValue(analysis.pest_control)}</strong>
              </div>
              <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                <span>Landscaping</span>
                <strong>${UIHelpers.formatDisplayValue(analysis.landscaping)}</strong>
              </div>
              <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                <span>PadSplit Platform Fee</span>
                <div class="text-end">
                  <div class="small text-muted">
                    ${UIHelpers.formatDisplayValue(analysis.padsplit_platform_percentage || 0, 'percentage')}
                  </div>
                  <strong>${UIHelpers.formatDisplayValue((analysis.monthly_rent * ((analysis.padsplit_platform_percentage || 0) / 100)))}</strong>
                </div>
              </div>
            </div>
          </div>
        </div>
        ` : ''}
      </div>
    </div>
  </div>

  ${this.createNotesSection(analysis.notes)}`;
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
export default BRRRRHandler;
