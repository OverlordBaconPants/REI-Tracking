/**
 * validator.js
 * Form validation utilities for the analysis module
 */

import UIHelpers from './ui-helpers.js';

const AnalysisValidator = {
  /**
   * Validate the analysis form
   * @param {HTMLFormElement} form - The form to validate
   * @returns {boolean} Whether the form is valid
   */
  validateForm(form) {
    let isValid = true;
    
    // Get analysis type and balloon payment state
    const analysisType = form.querySelector('#analysis_type')?.value;
    const hasBalloon = form.querySelector('#has_balloon_payment')?.checked || false;
    
    console.log('Starting form validation:', { analysisType, hasBalloon });
    
    // Validate required fields first
    const requiredFields = form.querySelectorAll('[required]');
    requiredFields.forEach(field => {
      if (!field.value.trim()) {
        isValid = false;
        this.markFieldInvalid(field, 'This field is required');
        console.log('Required field empty:', field.id);
      } else {
        this.markFieldValid(field);
      }
    });
    
    // Validate all numeric fields
    const numericFields = this.getNumericFieldsConfig(analysisType);
    
    Object.entries(numericFields).forEach(([fieldName, rules]) => {
      const field = form.querySelector(`#${fieldName}`);
      if (field && field.value.trim()) {
        if (!this.validateNumericRange(field.value, rules.min, rules.max)) {
          isValid = false;
          this.markFieldInvalid(field, rules.message);
          console.log(`Invalid numeric field: ${fieldName}`, {
            value: field.value,
            rules: rules
          });
        } else {
          this.markFieldValid(field);
        }
      }
    });
    
    // Validate percentage fields
    const percentageFields = this.getPercentageFieldsConfig(analysisType);
    
    Object.entries(percentageFields).forEach(([fieldName, rules]) => {
      const field = form.querySelector(`#${fieldName}`);
      if (field && field.value.trim()) {
        if (!this.validateNumericRange(field.value, rules.min, rules.max)) {
          isValid = false;
          this.markFieldInvalid(field, rules.message);
          console.log(`Invalid percentage field: ${fieldName}`, {
            value: field.value,
            rules: rules
          });
        } else {
          this.markFieldValid(field);
        }
      }
    });
    
    // Analysis type specific validation
    if (analysisType === 'Multi-Family') {
      isValid = this.validateMultiFamilyData(form) && isValid;
    } else if (analysisType === 'Lease Option') {
      isValid = this.validateLeaseOptionData(form) && isValid;
    } else if (analysisType && analysisType.includes('BRRRR')) {
      isValid = this.validateBRRRRData(form) && isValid;
    }
    
    // Validate balloon payment fields if enabled
    if (hasBalloon) {
      isValid = this.validateBalloonPaymentData(form) && isValid;
    }
    
    // Check for any invalid fields and show appropriate error message
    if (!isValid) {
      const invalidFields = form.querySelectorAll('.is-invalid');
      if (invalidFields.length > 0) {
        const fieldNames = Array.from(invalidFields)
          .map(f => f.labels?.[0]?.textContent || f.id)
          .filter(Boolean);
        UIHelpers.showToast('error', `Please check these fields: ${fieldNames.join(', ')}`);
      } else {
        UIHelpers.showToast('error', 'Please check all required fields');
      }
    }
    
    console.log('Form validation result:', isValid);
    return isValid;
  },
  
  /**
   * Validate that a value is within a numeric range
   * @param {string|number} value - The value to validate
   * @param {number} min - Minimum allowed value
   * @param {number} max - Maximum allowed value
   * @returns {boolean} Whether the value is valid
   */
  validateNumericRange(value, min, max = Infinity) {
    const num = UIHelpers.toRawNumber(value);
    return !isNaN(num) && num >= min && num <= max;
  },
  
  /**
   * Mark a field as invalid with an error message
   * @param {HTMLElement} field - The field to mark
   * @param {string} message - The error message
   */
  markFieldInvalid(field, message) {
    field.classList.add('is-invalid');
    
    // Add error message
    let errorDiv = field.nextElementSibling;
    if (!errorDiv || !errorDiv.classList.contains('invalid-feedback')) {
      errorDiv = document.createElement('div');
      errorDiv.className = 'invalid-feedback';
      field.parentNode.insertBefore(errorDiv, field.nextSibling);
    }
    errorDiv.textContent = message;
  },
  
  /**
   * Mark a field as valid
   * @param {HTMLElement} field - The field to mark
   */
  markFieldValid(field) {
    field.classList.remove('is-invalid');
  },
  
  /**
   * Get configuration for numeric fields based on analysis type
   * @param {string} analysisType - The analysis type
   * @returns {Object} Numeric fields configuration
   */
  getNumericFieldsConfig(analysisType) {
    // Base numeric fields that all analysis types need
    const baseFields = {
      'purchase_price': { min: 0, message: 'Purchase price must be greater than 0' },
      'monthly_rent': { min: 0, message: 'Monthly rent must be greater than 0' },
      'property_taxes': { min: 0, message: 'Property taxes must be greater than 0' },
      'insurance': { min: 0, message: 'Insurance must be greater than 0' },
      'hoa_coa_coop': { min: 0, message: 'HOA/COA/COOP must be greater than 0' },
      'square_footage': { min: 0, message: 'Square footage must be greater than 0' },
      'lot_size': { min: 0, message: 'Lot size must be greater than 0' },
      'year_built': { min: 1800, max: new Date().getFullYear(), message: 'Please enter a valid year' },
      'bedrooms': { min: 0, message: 'Number of bedrooms must be 0 or greater' },
      'bathrooms': { min: 0, message: 'Number of bathrooms must be 0 or greater' }
    };
    
    // Add fields specific to analysis types other than Lease Option
    if (analysisType !== 'Lease Option') {
      Object.assign(baseFields, {
        'renovation_costs': { min: 0, message: 'Renovation costs must be 0 or greater' },
        'renovation_duration': { min: 0, message: 'Renovation duration must be 0 or greater' },
        'after_repair_value': { min: 0, message: 'After repair value must be greater than 0' }
      });
    }
    
    // Add PadSplit-specific fields
    if (analysisType && analysisType.includes('PadSplit')) {
      Object.assign(baseFields, {
        'furnishing_costs': { min: 0, message: 'Furnishing costs must be 0 or greater' },
        'utilities': { min: 0, message: 'Utilities must be 0 or greater' },
        'internet': { min: 0, message: 'Internet must be 0 or greater' },
        'cleaning': { min: 0, message: 'Cleaning costs must be 0 or greater' },
        'pest_control': { min: 0, message: 'Pest control must be 0 or greater' },
        'landscaping': { min: 0, message: 'Landscaping must be 0 or greater' }
      });
    }
    
    // Add Multi-Family specific fields
    if (analysisType === 'Multi-Family') {
      Object.assign(baseFields, {
        'total_units': { min: 1, message: 'Total units must be at least 1' },
        'occupied_units': { min: 0, message: 'Occupied units must be 0 or greater' },
        'floors': { min: 1, message: 'Number of floors must be at least 1' },
        'other_income': { min: 0, message: 'Other income must be 0 or greater' },
        'common_area_maintenance': { min: 0, message: 'Common area maintenance must be 0 or greater' },
        'elevator_maintenance': { min: 0, message: 'Elevator maintenance must be 0 or greater' },
        'staff_payroll': { min: 0, message: 'Staff payroll must be 0 or greater' },
        'trash_removal': { min: 0, message: 'Trash removal must be 0 or greater' },
        'common_utilities': { min: 0, message: 'Common utilities must be 0 or greater' }
      });
    }
    
    // Add Lease Option specific fields
    if (analysisType === 'Lease Option') {
      Object.assign(baseFields, {
        'option_consideration_fee': { min: 0.01, message: 'Option fee must be greater than 0' },
        'option_term_months': { min: 1, max: 120, message: 'Option term must be between 1 and 120 months' },
        'strike_price': { min: 0, message: 'Strike price must be greater than 0' },
        'rent_credit_cap': { min: 0, message: 'Rent credit cap must be greater than 0' }
      });
    }
    
    return baseFields;
  },
  
  /**
   * Get configuration for percentage fields based on analysis type
   * @param {string} analysisType - The analysis type
   * @returns {Object} Percentage fields configuration
   */
  getPercentageFieldsConfig(analysisType) {
    // Base percentage fields
    const baseFields = {
      'management_fee_percentage': { min: 0, max: 100, message: 'Management fee must be between 0 and 100%' },
      'capex_percentage': { min: 0, max: 100, message: 'CapEx must be between 0 and 100%' },
      'vacancy_percentage': { min: 0, max: 100, message: 'Vacancy rate must be between 0 and 100%' },
      'repairs_percentage': { min: 0, max: 100, message: 'Repairs percentage must be between 0 and 100%' }
    };
    
    // Add PadSplit platform fee percentage
    if (analysisType && analysisType.includes('PadSplit')) {
      baseFields['padsplit_platform_percentage'] = { min: 0, max: 100, message: 'Platform fee must be between 0 and 100%' };
    }
    
    // Add Lease Option rent credit percentage
    if (analysisType === 'Lease Option') {
      baseFields['monthly_rent_credit_percentage'] = { min: 0, max: 100, message: 'Monthly rent credit percentage must be between 0 and 100%' };
    }
    
    return baseFields;
  },
  
  /**
   * Validate Multi-Family specific data
   * @param {HTMLFormElement} form - The form to validate
   * @returns {boolean} Whether the data is valid
   */
  validateMultiFamilyData(form) {
    try {
      // Get unit types
      const unitTypes = this.getUnitTypesData(form);
      let isValid = true;
      
      // 1. Validate unit types exist
      if (!unitTypes || unitTypes.length === 0) {
        UIHelpers.showToast('error', 'At least one unit type is required');
        isValid = false;
      } else {
        // 2. Validate each unit type
        unitTypes.forEach((ut, index) => {
          const section = form.querySelector(`.unit-type-section[data-unit-index="${index}"]`);
          
          // Clear previous validation states
          if (section) {
            section.querySelectorAll('.is-invalid').forEach(field => {
              field.classList.remove('is-invalid');
            });
          }

          // Basic unit type validation
          if (ut.count <= 0) {
            this.markFieldInvalid(section?.querySelector('.unit-count'), 'Number of units must be greater than 0');
            isValid = false;
          }

          if (ut.occupied > ut.count) {
            this.markFieldInvalid(section?.querySelector('.unit-occupied'), 'Occupied units cannot exceed total units');
            isValid = false;
          }

          if (ut.square_footage <= 0) {
            this.markFieldInvalid(
              section?.querySelector('input[name$="[square_footage]"]'),
              'Square footage must be greater than 0'
            );
            isValid = false;
          }

          if (ut.rent <= 0) {
            this.markFieldInvalid(section?.querySelector('.unit-rent'), 'Rent must be greater than 0');
            isValid = false;
          }
        });
      }

      // Check total/occupied units consistency
      const totalUnitsInput = form.querySelector('#total_units');
      const occupiedUnitsInput = form.querySelector('#occupied_units');
      
      if (totalUnitsInput && occupiedUnitsInput) {
        const totalUnits = parseInt(totalUnitsInput.value) || 0;
        const occupiedUnits = parseInt(occupiedUnitsInput.value) || 0;
        
        if (occupiedUnits > totalUnits) {
          this.markFieldInvalid(occupiedUnitsInput, 'Occupied units cannot exceed total units');
          isValid = false;
        }
      }
      
      return isValid;
    } catch (error) {
      console.error('Error validating Multi-Family data:', error);
      UIHelpers.showToast('error', 'Error validating Multi-Family data');
      return false;
    }
  },
  
  /**
   * Validate Lease Option specific data
   * @param {HTMLFormElement} form - The form to validate
   * @returns {boolean} Whether the data is valid
   */
  validateLeaseOptionData(form) {
    try {
      let isValid = true;
      
      // Validate strike price > purchase price
      const purchasePrice = UIHelpers.toRawNumber(form.querySelector('#purchase_price')?.value);
      const strikePrice = UIHelpers.toRawNumber(form.querySelector('#strike_price')?.value);
      
      if (strikePrice <= purchasePrice) {
        this.markFieldInvalid(
          form.querySelector('#strike_price'),
          'Strike price must be greater than purchase price'
        );
        isValid = false;
      }
      
      return isValid;
    } catch (error) {
      console.error('Error validating Lease Option data:', error);
      UIHelpers.showToast('error', 'Error validating Lease Option data');
      return false;
    }
  },
  
  /**
   * Validate BRRRR specific data
   * @param {HTMLFormElement} form - The form to validate
   * @returns {boolean} Whether the data is valid
   */
  validateBRRRRData(form) {
    try {
      let isValid = true;
      
      // Validate loan fields
      ['initial', 'refinance'].forEach(prefix => {
        const amountField = form.querySelector(`#${prefix}_loan_amount`);
        const interestField = form.querySelector(`#${prefix}_loan_interest_rate`);
        const termField = form.querySelector(`#${prefix}_loan_term`);
        
        if (amountField && interestField && termField) {
          const amount = UIHelpers.toRawNumber(amountField.value);
          
          if (amount > 0) {
            // Validate interest rate
            const interest = UIHelpers.toRawNumber(interestField.value);
            if (interest < 0 || interest > 30) {
              this.markFieldInvalid(interestField, 'Interest rate must be between 0 and 30%');
              isValid = false;
            } else {
              this.markFieldValid(interestField);
            }
            
            // Validate term
            const term = parseInt(termField.value);
            const maxTerm = prefix === 'initial' ? 24 : 360; // Initial loans typically shorter
            
            if (term < 1 || term > maxTerm) {
              this.markFieldInvalid(termField, `Term must be between 1 and ${maxTerm} months`);
              isValid = false;
            } else {
              this.markFieldValid(termField);
            }
          }
        }
      });
      
      // Validate ARV > purchase price + renovation costs
      const purchasePrice = UIHelpers.toRawNumber(form.querySelector('#purchase_price')?.value);
      const renovationCosts = UIHelpers.toRawNumber(form.querySelector('#renovation_costs')?.value);
      const arv = UIHelpers.toRawNumber(form.querySelector('#after_repair_value')?.value);
      
      if (arv <= (purchasePrice + renovationCosts)) {
        this.markFieldInvalid(
          form.querySelector('#after_repair_value'),
          'ARV must exceed purchase price plus renovation costs'
        );
        isValid = false;
      } else {
        this.markFieldValid(form.querySelector('#after_repair_value'));
      }
      
      return isValid;
    } catch (error) {
      console.error('Error validating BRRRR data:', error);
      UIHelpers.showToast('error', 'Error validating BRRRR data');
      return false;
    }
  },
  
  /**
   * Validate balloon payment fields
   * @param {HTMLFormElement} form - The form to validate
   * @returns {boolean} Whether the data is valid
   */
  validateBalloonPaymentData(form) {
    try {
      let isValid = true;
      
      // Validate balloon due date
      const dueDateField = form.querySelector('#balloon_due_date');
      if (dueDateField) {
        const dueDate = new Date(dueDateField.value);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        if (!dueDateField.value || dueDate <= today) {
          this.markFieldInvalid(dueDateField, 'Balloon due date must be in the future');
          isValid = false;
        } else {
          this.markFieldValid(dueDateField);
        }
      }
      
      // Validate balloon loan parameters
      const ltvField = form.querySelector('#balloon_refinance_ltv_percentage');
      const amountField = form.querySelector('#balloon_refinance_loan_amount');
      const interestField = form.querySelector('#balloon_refinance_loan_interest_rate');
      const termField = form.querySelector('#balloon_refinance_loan_term');
      
      if (ltvField) {
        const ltv = UIHelpers.toRawNumber(ltvField.value);
        if (ltv < 0 || ltv > 100) {
          this.markFieldInvalid(ltvField, 'LTV must be between 0 and 100%');
          isValid = false;
        } else {
          this.markFieldValid(ltvField);
        }
      }
      
      if (amountField) {
        const amount = UIHelpers.toRawNumber(amountField.value);
        if (amount <= 0) {
          this.markFieldInvalid(amountField, 'Loan amount must be greater than 0');
          isValid = false;
        } else {
          this.markFieldValid(amountField);
        }
      }
      
      if (interestField) {
        const interest = UIHelpers.toRawNumber(interestField.value);
        if (interest < 0 || interest > 30) {
          this.markFieldInvalid(interestField, 'Interest rate must be between 0 and 30%');
          isValid = false;
        } else {
          this.markFieldValid(interestField);
        }
      }
      
      if (termField) {
        const term = parseInt(termField.value);
        if (term < 1 || term > 360) {
          this.markFieldInvalid(termField, 'Term must be between 1 and 360 months');
          isValid = false;
        } else {
          this.markFieldValid(termField);
        }
      }
      
      return isValid;
    } catch (error) {
      console.error('Error validating balloon payment data:', error);
      UIHelpers.showToast('error', 'Error validating balloon payment data');
      return false;
    }
  },
  
  /**
   * Get unit types data from form
   * @param {HTMLFormElement} form - The form to get data from
   * @returns {Array} Array of unit type objects
   */
  getUnitTypesData(form) {
    const unitTypes = [];
    form.querySelectorAll('.unit-type-section').forEach(section => {
      unitTypes.push({
        type: section.querySelector('select').value,
        count: parseInt(section.querySelector('.unit-count').value) || 0,
        occupied: parseInt(section.querySelector('.unit-occupied').value) || 0,
        square_footage: parseInt(section.querySelector('input[name$="[square_footage]"]').value) || 0,
        rent: parseFloat(section.querySelector('.unit-rent').value) || 0
      });
    });
    return unitTypes;
  }
};

// Export the validator
export default AnalysisValidator;