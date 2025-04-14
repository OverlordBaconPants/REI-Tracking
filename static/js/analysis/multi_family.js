/**
 * multi_family.js
 * multi_family property strategy specific implementation
 */

import UIHelpers from './ui_helpers.js';
import Calculator from './calculator.js';
import AnalysisCore from './core.js';

const MultiFamilyHandler = {
  /**
   * Get the HTML template for multi_family analysis
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
                      <select class="form-select form-select-lg" id="property_type" name="property_type" disabled>
                          <option value="Multi-Family">Multi-Family</option>
                      </select>
                  </div>
                  <div class="col-12 col-md-4">
                      <label for="square_footage" class="form-label">Total Square Footage</label>
                      <div class="input-group">
                          <input type="number" class="form-control form-control-lg" id="square_footage" 
                              name="square_footage" placeholder="Total building square footage">
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
                  <div class="col-12 col-md-4">
                      <label for="total_units" class="form-label">Total Units</label>
                      <input type="number" class="form-control form-control-lg" id="total_units" 
                          name="total_units" min="2" placeholder="Number of units" required>
                  </div>
                  <div class="col-12 col-md-4">
                      <label for="occupied_units" class="form-label">Occupied Units</label>
                      <input type="number" class="form-control form-control-lg" id="occupied_units" 
                          name="occupied_units" min="0" placeholder="Currently occupied units" required>
                  </div>
                  <div class="col-12 col-md-4">
                      <label for="floors" class="form-label">Number of Floors</label>
                      <input type="number" class="form-control form-control-lg" id="floors" 
                          name="floors" min="1" placeholder="Number of floors" required>
                  </div>
              </div>
          </div>
      </div>

      <!-- Unit Mix Card -->
      <div class="card mb-4">
          <div class="card-header d-flex justify-content-between align-items-center">
              <h5 class="mb-0">Unit Mix</h5>
              <button type="button" class="btn btn-primary btn-sm" id="add-unit-type-btn">
                  <i class="bi bi-plus-circle me-2"></i>Add Unit Type
              </button>
          </div>
          <div class="card-body">
              <div id="unit-types-container">
                  <!-- Unit types will be added here dynamically -->
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
              </div>
          </div>
      </div>

      <!-- Building Income Card -->
      <div class="card mb-4">
          <div class="card-header">
              <h5 class="mb-0">Building Income</h5>
          </div>
          <div class="card-body">
              <div class="row g-3">
                  <div class="col-12 col-md-6">
                      <label for="other_income" class="form-label">Other Monthly Income</label>
                      <div class="input-group">
                          <span class="input-group-text">$</span>
                          <input type="number" class="form-control form-control-lg" id="other_income" 
                                name="other_income" placeholder="Parking, laundry, etc." required>
                      </div>
                  </div>
                  <div class="col-12 col-md-6">
                      <label for="total_potential_income" class="form-label">Total Potential Income</label>
                      <div class="input-group">
                          <span class="input-group-text">$</span>
                          <input type="number" class="form-control form-control-lg" id="total_potential_income" 
                                name="total_potential_income" readonly>
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

      <!-- Operating Expenses Card -->
      <div class="card mb-4">
          <div class="card-header">
              <h5 class="mb-0">Operating Expenses</h5>
          </div>
          <div class="card-body">
              <div class="row g-3">
                  <!-- Standard Expenses -->
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
                  
                  <!-- Multi-Family Specific Expenses -->
                  <div class="col-12 col-md-6">
                      <label for="common_area_maintenance" class="form-label">Common Area Maintenance</label>
                      <div class="input-group">
                          <span class="input-group-text">$</span>
                          <input type="number" class="form-control form-control-lg" id="common_area_maintenance" 
                                name="common_area_maintenance" placeholder="Monthly CAM costs" required>
                      </div>
                  </div>
                  <div class="col-12 col-md-6">
                      <label for="elevator_maintenance" class="form-label">Elevator Maintenance</label>
                      <div class="input-group">
                          <span class="input-group-text">$</span>
                          <input type="number" class="form-control form-control-lg" id="elevator_maintenance" 
                                name="elevator_maintenance" placeholder="Monthly maintenance">
                      </div>
                  </div>
                  <div class="col-12 col-md-6">
                      <label for="staff_payroll" class="form-label">Staff Payroll</label>
                      <div class="input-group">
                          <span class="input-group-text">$</span>
                          <input type="number" class="form-control form-control-lg" id="staff_payroll" 
                                name="staff_payroll" placeholder="Monthly payroll costs" required>
                      </div>
                  </div>
                  <div class="col-12 col-md-6">
                      <label for="trash_removal" class="form-label">Trash Removal</label>
                      <div class="input-group">
                          <span class="input-group-text">$</span>
                          <input type="number" class="form-control form-control-lg" id="trash_removal" 
                                name="trash_removal" placeholder="Monthly cost" required>
                      </div>
                  </div>
                  <div class="col-12 col-md-6">
                      <label for="common_utilities" class="form-label">Common Utilities</label>
                      <div class="input-group">
                          <span class="input-group-text">$</span>
                          <input type="number" class="form-control form-control-lg" id="common_utilities" 
                                name="common_utilities" placeholder="Monthly utilities" required>
                      </div>
                  </div>

                  <!-- Percentage-based expenses -->
                  <div class="col-12 col-md-6">
                      <label for="management_fee_percentage" class="form-label">Management Fee</label>
                      <div class="input-group">
                          <input type="number" class="form-control form-control-lg" id="management_fee_percentage" 
                                name="management_fee_percentage" value="4" min="0" max="100" step="0.5" required>
                          <span class="input-group-text">%</span>
                      </div>
                  </div>
                  <div class="col-12 col-md-6">
                      <label for="capex_percentage" class="form-label">CapEx</label>
                      <div class="input-group">
                          <input type="number" class="form-control form-control-lg" id="capex_percentage" 
                                name="capex_percentage" value="5" min="0" max="100" step="1" required>
                          <span class="input-group-text">%</span>
                      </div>
                  </div>
                  <div class="col-12 col-md-6">
                      <label for="repairs_percentage" class="form-label">Repairs</label>
                      <div class="input-group">
                          <input type="number" class="form-control form-control-lg" id="repairs_percentage" 
                                name="repairs_percentage" value="3" min="0" max="100" step="1" required>
                          <span class="input-group-text">%</span>
                      </div>
                  </div>
                  <div class="col-12 col-md-6">
                      <label for="vacancy_percentage" class="form-label">Vacancy Rate</label>
                      <div class="input-group">
                          <input type="number" class="form-control form-control-lg" id="vacancy_percentage" 
                                name="vacancy_percentage" value="7" min="0" max="100" step="1" required>
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
   * Return HTML template for a unit type
   * @param {number} index - Index for the unit type
   * @returns {string} HTML for unit type section
   */
  getUnitTypeHTML(index) {
    return `
    <div class="unit-type-section mb-4" data-unit-index="${index}">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h6 class="mb-0">Unit Type ${index + 1}</h6>
                <button type="button" class="btn btn-danger btn-sm remove-unit-type-btn">
                    <i class="bi bi-trash me-2"></i>Remove
                </button>
            </div>
            <div class="card-body">
                <div class="row g-3">
                    <div class="col-12 col-md-6">
                        <label class="form-label">Unit Type</label>
                        <select class="form-select form-select-lg" name="unit_types[${index}][type]" required>
                            <option value="studio">Studio</option>
                            <option value="1br">1 Bedroom</option>
                            <option value="2br">2 Bedrooms</option>
                            <option value="3br">3 Bedrooms</option>
                            <option value="4br">4 Bedrooms</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                    <div class="col-12 col-md-6">
                        <label class="form-label">Number of Units</label>
                        <input type="number" class="form-control form-control-lg unit-count" 
                               name="unit_types[${index}][count]" min="1" required>
                    </div>
                    <div class="col-12 col-md-6">
                        <label class="form-label">Square Footage per Unit</label>
                        <div class="input-group">
                            <input type="number" class="form-control form-control-lg" 
                                   name="unit_types[${index}][square_footage]" required>
                            <span class="input-group-text">sq ft</span>
                        </div>
                    </div>
                    <div class="col-12 col-md-6">
                        <label class="form-label">Monthly Rent per Unit</label>
                        <div class="input-group">
                            <span class="input-group-text">$</span>
                            <input type="number" class="form-control form-control-lg unit-rent" 
                                   name="unit_types[${index}][rent]" required>
                        </div>
                    </div>
                    <div class="col-12 col-md-6">
                        <label class="form-label">Number of Occupied Units</label>
                        <input type="number" class="form-control form-control-lg unit-occupied" 
                               name="unit_types[${index}][occupied]" min="0" required>
                    </div>
                </div>
            </div>
        </div>
    </div>
    `;
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
   * Initialize Multi-Family specific handlers
   */
  async initHandlers() {
    // Initialize unit type handlers
    this.initUnitTypeHandlers();
    
    // Initialize loan handlers
    this.initLoanHandlers();
    
    // Initialize unit type calculations
    this.initUnitTypeCalculations();
    
    // Initialize property validation
    this.initMultiFamilyValidation();
  },
  
  /**
   * Initialize unit type handlers
   */
  initUnitTypeHandlers() {
    const unitTypesContainer = document.getElementById('unit-types-container');
    const addUnitTypeBtn = document.getElementById('add-unit-type-btn');
    
    if (!unitTypesContainer || !addUnitTypeBtn) {
      console.error('Unit type elements not found');
      return;
    }
    
    // Initialize with one unit type if none exist
    if (!unitTypesContainer.children.length) {
      unitTypesContainer.insertAdjacentHTML('beforeend', this.getUnitTypeHTML(0));
    }
    
    // Handle adding new unit types
    addUnitTypeBtn.addEventListener('click', () => {
      const nextIndex = unitTypesContainer.children.length;
      if (nextIndex < 10) { // Limit to 10 unit types
        unitTypesContainer.insertAdjacentHTML('beforeend', this.getUnitTypeHTML(nextIndex));
        this.initUnitTypeCalculations();
      } else {
        UIHelpers.showToast('warning', 'Maximum of 10 unit types allowed');
      }
    });
    
    // Handle removing unit types
    unitTypesContainer.addEventListener('click', (e) => {
      if (e.target.closest('.remove-unit-type-btn')) {
        const unitSection = e.target.closest('.unit-type-section');
        if (unitTypesContainer.children.length > 1) {
          unitSection.remove();
          this.reindexUnitTypes();
          this.updateTotalUnits();
          this.updateTotalIncome();
        } else {
          UIHelpers.showToast('warning', 'At least one unit type is required');
        }
      }
    });
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
    
    // Add first loan if none exist
    if (!loansContainer.children.length) {
      loansContainer.insertAdjacentHTML('beforeend', this.getLoanFieldsHTML(1));
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
   * Initialize unit type calculations
   */
  initUnitTypeCalculations() {
    // Initialize listeners for unit count and rent changes
    const unitInputs = document.querySelectorAll('.unit-count, .unit-rent, .unit-occupied');
    unitInputs.forEach(input => {
      input.removeEventListener('input', this.updateTotalUnits);
      input.removeEventListener('input', this.updateTotalIncome);
      input.addEventListener('input', () => {
        this.updateTotalUnits();
        this.updateTotalIncome();
      });
    });
  },
  
  /**
   * Update the total units count
   */
  updateTotalUnits() {
    const totalUnitsInput = document.getElementById('total_units');
    const occupiedUnitsInput = document.getElementById('occupied_units');
    
    if (!totalUnitsInput || !occupiedUnitsInput) return;
    
    let totalUnits = 0;
    let occupiedUnits = 0;
    
    document.querySelectorAll('.unit-type-section').forEach(section => {
      const count = parseInt(section.querySelector('.unit-count').value) || 0;
      const occupied = parseInt(section.querySelector('.unit-occupied').value) || 0;
      totalUnits += count;
      occupiedUnits += Math.min(occupied, count); // Occupied cannot exceed total
    });
    
    totalUnitsInput.value = totalUnits;
    occupiedUnitsInput.value = occupiedUnits;
  },
  
  /**
   * Update the total income calculation
   */
  updateTotalIncome() {
    const totalPotentialIncomeInput = document.getElementById('total_potential_income');
    const otherIncomeInput = document.getElementById('other_income');
    
    if (!totalPotentialIncomeInput) return;
    
    let totalRent = 0;
    document.querySelectorAll('.unit-type-section').forEach(section => {
      const count = parseInt(section.querySelector('.unit-count').value) || 0;
      const rent = parseFloat(section.querySelector('.unit-rent').value) || 0;
      totalRent += count * rent;
    });
    
    const otherIncome = parseFloat(otherIncomeInput?.value) || 0;
    totalPotentialIncomeInput.value = (totalRent + otherIncome).toFixed(2);
  },
  
  /**
   * Reindex unit types after removing one
   */
  reindexUnitTypes() {
    const unitSections = document.querySelectorAll('.unit-type-section');
    unitSections.forEach((section, index) => {
      section.dataset.unitIndex = index;
      section.querySelector('.card-header h6').textContent = `Unit Type ${index + 1}`;
      
      // Update input names
      section.querySelectorAll('input, select').forEach(input => {
        const nameParts = input.name.split('[');
        if (nameParts.length >= 2) {
          const fieldName = nameParts[0];
          const fieldPart = nameParts[1].split(']')[1] || '';
          input.name = `${fieldName}[${index}]${fieldPart}`;
        }
      });
    });
  },
  
  /**
   * Initialize validation specific to Multi-Family properties
   */
  initMultiFamilyValidation() {
    const form = document.getElementById('analysisForm');
    if (!form) return;
    
    // Add validation for total/occupied units consistency
    const totalUnitsInput = document.getElementById('total_units');
    const occupiedUnitsInput = document.getElementById('occupied_units');
    
    if (totalUnitsInput && occupiedUnitsInput) {
      totalUnitsInput.addEventListener('change', () => {
        const totalUnits = parseInt(totalUnitsInput.value) || 0;
        const occupiedUnits = parseInt(occupiedUnitsInput.value) || 0;
        
        if (occupiedUnits > totalUnits) {
          occupiedUnitsInput.value = totalUnits;
        }
      });
      
      occupiedUnitsInput.addEventListener('change', () => {
        const totalUnits = parseInt(totalUnitsInput.value) || 0;
        const occupiedUnits = parseInt(occupiedUnitsInput.value) || 0;
        
        if (occupiedUnits > totalUnits) {
          occupiedUnitsInput.value = totalUnits;
          UIHelpers.showToast('warning', 'Occupied units cannot exceed total units');
        }
      });
    }
  },
  
/**
   * Get unit types data from the form
   * @returns {Array} Array of unit type objects
   */
getUnitTypesData() {
    const unitTypes = [];
    document.querySelectorAll('.unit-type-section').forEach(section => {
      unitTypes.push({
        type: section.querySelector('select').value,
        count: parseInt(section.querySelector('.unit-count').value) || 0,
        occupied: parseInt(section.querySelector('.unit-occupied').value) || 0,
        square_footage: parseInt(section.querySelector('input[name$="[square_footage]"]').value) || 0,
        rent: parseFloat(section.querySelector('.unit-rent').value) || 0
      });
    });
    return unitTypes;
  },
  
  /**
   * Populate form fields with analysis data
   * @param {Object} analysis - Analysis data
   */
  populateFields(analysis) {
    // Check that this is a Multi-Family analysis
    if (analysis.analysis_type !== 'Multi-Family') {
      console.warn('Attempted to populate non-Multi-Family analysis with Multi-Family handler');
      return;
    }
    
    // Set property details
    AnalysisCore.setFieldValue('property_type', 'Multi-Family'); // Should already be set and disabled
    AnalysisCore.setFieldValue('square_footage', analysis.square_footage);
    AnalysisCore.setFieldValue('lot_size', analysis.lot_size);
    AnalysisCore.setFieldValue('year_built', analysis.year_built);
    AnalysisCore.setFieldValue('total_units', analysis.total_units);
    AnalysisCore.setFieldValue('occupied_units', analysis.occupied_units);
    AnalysisCore.setFieldValue('floors', analysis.floors);
    
    // Set purchase details
    AnalysisCore.setFieldValue('purchase_price', analysis.purchase_price);
    AnalysisCore.setFieldValue('after_repair_value', analysis.after_repair_value);
    AnalysisCore.setFieldValue('renovation_costs', analysis.renovation_costs);
    AnalysisCore.setFieldValue('renovation_duration', analysis.renovation_duration);
    
    // Set income fields
    AnalysisCore.setFieldValue('other_income', analysis.other_income);
    AnalysisCore.setFieldValue('total_potential_income', analysis.total_potential_income);
    
    // Set operating expenses
    AnalysisCore.setFieldValue('property_taxes', analysis.property_taxes);
    AnalysisCore.setFieldValue('insurance', analysis.insurance);
    AnalysisCore.setFieldValue('common_area_maintenance', analysis.common_area_maintenance);
    AnalysisCore.setFieldValue('elevator_maintenance', analysis.elevator_maintenance);
    AnalysisCore.setFieldValue('staff_payroll', analysis.staff_payroll);
    AnalysisCore.setFieldValue('trash_removal', analysis.trash_removal);
    AnalysisCore.setFieldValue('common_utilities', analysis.common_utilities);
    AnalysisCore.setFieldValue('management_fee_percentage', analysis.management_fee_percentage);
    AnalysisCore.setFieldValue('capex_percentage', analysis.capex_percentage);
    AnalysisCore.setFieldValue('repairs_percentage', analysis.repairs_percentage);
    AnalysisCore.setFieldValue('vacancy_percentage', analysis.vacancy_percentage);
    
    // Handle unit types
    try {
      const unitTypesContainer = document.getElementById('unit-types-container');
      if (unitTypesContainer) {
        // Clear existing unit types
        unitTypesContainer.innerHTML = '';
        
        // Parse unit types from stored JSON string
        const unitTypes = JSON.parse(analysis.unit_types || '[]');
        
        // Add each unit type
        unitTypes.forEach((unitType, index) => {
          unitTypesContainer.insertAdjacentHTML('beforeend', this.getUnitTypeHTML(index));
          
          // Set values for this unit type
          const section = unitTypesContainer.children[index];
          if (section) {
            section.querySelector('select').value = unitType.type;
            section.querySelector('.unit-count').value = unitType.count;
            section.querySelector('.unit-occupied').value = unitType.occupied;
            section.querySelector('input[name$="[square_footage]"]').value = unitType.square_footage;
            section.querySelector('.unit-rent').value = unitType.rent;
          }
        });
        
        // Initialize calculations
        this.initUnitTypeCalculations();
      }
    } catch (error) {
      console.error('Error populating unit types:', error);
      UIHelpers.showToast('error', 'Error loading unit type data');
    }
    
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
    }
  },
  
  /**
   * Process form data before submission
   * @param {FormData} formData - The form data
   * @param {Object} analysisData - The processed analysis data
   * @returns {Object} The processed analysis data
   */
  processFormData(formData, analysisData) {
    // Get unit types data
    const unitTypes = this.getUnitTypesData();
    analysisData.unit_types = JSON.stringify(unitTypes);
    
    // Calculate total potential rent from unit types
    let totalPotentialRent = 0;
    unitTypes.forEach(unitType => {
      totalPotentialRent += (unitType.count * unitType.rent);
    });
    
    // Add other income to get total potential income
    const otherIncome = UIHelpers.toRawNumber(analysisData.other_income);
    analysisData.total_potential_income = totalPotentialRent + otherIncome;
    
    // Handle loan interest-only checkboxes
    for (let i = 1; i <= 3; i++) {
      const interestOnlyField = `loan${i}_interest_only`;
      if (interestOnlyField in analysisData) {
        analysisData[interestOnlyField] = (analysisData[interestOnlyField] === 'on');
      }
    }
    
    // Handle numeric fields
    const numericFields = [
      'square_footage', 'lot_size', 'year_built', 'total_units', 'occupied_units', 'floors',
      'purchase_price', 'after_repair_value', 'renovation_costs', 'renovation_duration',
      'other_income', 'total_potential_income',
      'property_taxes', 'insurance', 'common_area_maintenance', 'elevator_maintenance',
      'staff_payroll', 'trash_removal', 'common_utilities'
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
    // Parse unit types
    let unitTypes = [];
    try {
      unitTypes = JSON.parse(analysis.unit_types || '[]');
    } catch (error) {
      console.error('Error parsing unit types:', error);
    }
    
    // Get calculated metrics
    const metrics = analysis.calculated_metrics || {};
    
    // Calculate gross potential rent
    const grossPotentialRent = unitTypes.reduce((total, ut) => {
      return total + (ut.count * ut.rent);
    }, 0);
    
    // Calculate gross potential income including other income
    const grossPotentialIncome = grossPotentialRent + (analysis.other_income || 0);
    
    // Calculate management fee
    const managementFeePercentage = analysis.management_fee_percentage || 0;
    const monthlyManagementFee = grossPotentialRent * (managementFeePercentage / 100);
    
    return `
      <!-- Property Overview Card -->
      <div class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0">Property Overview</h5>
        </div>
        <div class="card-body">
          <div class="list-group list-group-flush">
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
              <span>Property Type</span>
              <strong>${analysis.property_type || 'Multi-Family'}</strong>
            </div>
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
              <span>Total Units</span>
              <strong>${analysis.total_units}</strong>
            </div>
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
              <span>Occupied Units</span>
              <div class="text-end">
                <strong>${analysis.occupied_units}</strong>
                <div class="small text-muted">
                  ${metrics.occupancy_rate || ((analysis.occupied_units / analysis.total_units * 100).toFixed(2) + '%')} Occupancy
                </div>
              </div>
            </div>
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
              <span>Purchase Price</span>
              <div class="text-end">
                <strong>${UIHelpers.formatDisplayValue(analysis.purchase_price)}</strong>
                <div class="small text-muted">
                  ${metrics.price_per_unit || UIHelpers.formatDisplayValue(analysis.purchase_price / analysis.total_units)} per unit
                </div>
              </div>
            </div>
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
              <span>Square Footage</span>
              <strong>${analysis.square_footage ? analysis.square_footage.toLocaleString() + ' sq ft' : 'Not specified'}</strong>
            </div>
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
              <span>Year Built</span>
              <strong>${analysis.year_built || 'Not specified'}</strong>
            </div>
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
              <span>Number of Floors</span>
              <strong>${analysis.floors || 'Not specified'}</strong>
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
          </div>
        </div>
      </div>

      <!-- Financial Performance Card -->
      <div class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0">Financial Performance</h5>
        </div>
        <div class="card-body">
          <div class="list-group list-group-flush">
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
              <span>Gross Potential Rent</span>
              <strong>${metrics.gross_potential_rent || UIHelpers.formatDisplayValue(grossPotentialRent)}</strong>
            </div>
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
              <span>Other Income</span>
              <strong>${UIHelpers.formatDisplayValue(analysis.other_income)}</strong>
            </div>
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
              <span>Total Potential Income</span>
              <strong>${UIHelpers.formatDisplayValue(analysis.total_potential_income)}</strong>
            </div>
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
              <span>Actual Gross Income</span>
              <strong>${metrics.actual_gross_income || UIHelpers.formatDisplayValue(
                grossPotentialRent * (analysis.occupied_units / analysis.total_units) + (analysis.other_income || 0)
              )}</strong>
            </div>
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
              <span class="d-flex align-items-center">
                Net Operating Income
                <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" 
                   title="Annual NOI before debt service">
                </i>
              </span>
              <strong>${metrics.annual_noi || UIHelpers.formatDisplayValue(metrics.monthly_noi * 12 || 0)}</strong>
            </div>
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
              <span class="d-flex align-items-center">
                Cap Rate
                <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip"
                   title="Annual NOI / Purchase Price">
                </i>
              </span>
              <strong>${metrics.cap_rate || '0.00%'}</strong>
            </div>
            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
              <span class="d-flex align-items-center">
                Cash-on-Cash Return
                <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip"
                   title="Annual Cash Flow / Total Cash Invested">
                </i>
              </span>
              <strong>${metrics.cash_on_cash_return || '0.00%'}</strong>
            </div>
          </div>
        </div>
      </div>

      <!-- Unit Mix Card -->
      <div class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0">Unit Mix</h5>
        </div>
        <div class="card-body">
          <div class="table-responsive">
            <table class="table table-bordered table-hover">
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Units</th>
                  <th>Occupied</th>
                  <th>Sq Ft</th>
                  <th>Rent</th>
                  <th>Total Potential</th>
                </tr>
              </thead>
              <tbody>
                ${unitTypes.map(ut => `
                  <tr>
                    <td>${ut.type}</td>
                    <td>${ut.count}</td>
                    <td>${ut.occupied}</td>
                    <td>${ut.square_footage}</td>
                    <td>${UIHelpers.formatDisplayValue(ut.rent)}</td>
                    <td>${UIHelpers.formatDisplayValue(ut.rent * ut.count)}</td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Operating Expenses Card -->
      <div class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0">Operating Expenses</h5>
        </div>
        <div class="card-body">
          <div class="row g-0">
            <div class="col-12 col-md-6">
              <div class="list-group list-group-flush">
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <span>Property Taxes</span>
                  <strong>${UIHelpers.formatDisplayValue(analysis.property_taxes)}</strong>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <span>Insurance</span>
                  <strong>${UIHelpers.formatDisplayValue(analysis.insurance)}</strong>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <span>Common Area Maintenance</span>
                  <strong>${UIHelpers.formatDisplayValue(analysis.common_area_maintenance)}</strong>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <span>Elevator Maintenance</span>
                  <strong>${UIHelpers.formatDisplayValue(analysis.elevator_maintenance)}</strong>
                </div>
              </div>
            </div>
            <div class="col-12 col-md-6">
              <div class="list-group list-group-flush">
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <span>Staff Payroll</span>
                  <strong>${UIHelpers.formatDisplayValue(analysis.staff_payroll)}</strong>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <span>Trash Removal</span>
                  <strong>${UIHelpers.formatDisplayValue(analysis.trash_removal)}</strong>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <span>Common Utilities</span>
                  <strong>${UIHelpers.formatDisplayValue(analysis.common_utilities)}</strong>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                  <span>Management Fee</span>
                  <div class="text-end">
                    <div class="small text-muted">
                      ${UIHelpers.formatDisplayValue(managementFeePercentage, 'percentage')}
                    </div>
                    <strong>${UIHelpers.formatDisplayValue(monthlyManagementFee)}</strong>
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
          <div class="accordion" id="multiFamilyLoansAccordion">
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
                 data-bs-parent="#multiFamilyLoansAccordion">
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
export default MultiFamilyHandler;