
// add_properties.js

import LoanTermToggle from './loan_term_toggle.js';

const addPropertiesModule = {

    getNumericValue: function(formData, fieldName, defaultValue = 0) {
        const value = formData.get(fieldName);
        if (value === null || value === '') {
            console.warn(`Field ${fieldName} is missing or empty, using default value: ${defaultValue}`);
            return defaultValue;
        }
        const numericValue = parseFloat(value);
        return isNaN(numericValue) ? defaultValue : numericValue;
    },

    init: async function() {
        if (this.initialized) {
            console.log('Module already initialized');
            return;
        }
        
        try {
            console.log('Initializing add properties module');
            const form = document.getElementById('add-property-form');
            
            if (form) {
                // Initialize existing functionality
                this.initAddressAutocomplete();
                this.initPartnersSection();
                this.initCalculations();
                
                // Initialize loan term toggles
                LoanTermToggle.init('primary_loan_term', 'secondary_loan_term');
                
                form.addEventListener('submit', this.handleSubmit.bind(this));
                console.log('Add Properties form initialized');
            } else {
                console.error('Add Properties form not found');
            }
        } catch (error) {
            console.error('Error initializing Add Properties module:', error);
        }
    },

    initAddressAutocomplete: function() {
        console.log('Initializing address autocomplete');
        const addressInput = document.getElementById('property_address');
        const resultsList = document.createElement('ul');
        resultsList.className = 'autocomplete-results list-group position-absolute w-100 shadow-sm';
        resultsList.style.zIndex = '1000';
        let timeoutId;
    
        if (addressInput) {
            // Insert the results list after the input
            addressInput.parentNode.appendChild(resultsList);
            
            addressInput.addEventListener('input', function() {
                clearTimeout(timeoutId);
                timeoutId = setTimeout(() => {
                    const query = this.value;
                    if (query.length > 2) {
                        console.log('Making API call for:', query);
                        resultsList.innerHTML = '<li class="list-group-item text-muted">Loading...</li>';
                        fetch(`/api/autocomplete?query=${encodeURIComponent(query)}`)
                            .then(response => {
                                if (!response.ok) {
                                    throw new Error(`HTTP error! status: ${response.status}`);
                                }
                                return response.json();
                            })
                            .then(data => {
                                console.log('API response:', data);
                                resultsList.innerHTML = '';
                                
                                if (data.status === 'success' && data.data && Array.isArray(data.data)) {
                                    data.data.forEach(result => {
                                        const li = document.createElement('li');
                                        li.className = 'list-group-item list-group-item-action';
                                        li.textContent = result.formatted;
                                        li.style.cursor = 'pointer';
                                        
                                        li.addEventListener('click', function() {
                                            addressInput.value = this.textContent;
                                            resultsList.innerHTML = '';
                                        });
                                        
                                        resultsList.appendChild(li);
                                    });
                                    
                                    if (data.data.length === 0) {
                                        const li = document.createElement('li');
                                        li.className = 'list-group-item disabled';
                                        li.textContent = 'No matches found';
                                        resultsList.appendChild(li);
                                    }
                                }
                            })
                            .catch(error => {
                                console.error('Error:', error);
                                resultsList.innerHTML = `
                                    <li class="list-group-item text-danger">
                                        Error fetching results: ${error.message}
                                    </li>
                                `;
                            });
                    } else {
                        resultsList.innerHTML = '';
                    }
                }, 300);
            });
    
            // Close suggestions when clicking outside
            document.addEventListener('click', function(e) {
                if (e.target !== addressInput && e.target !== resultsList) {
                    resultsList.innerHTML = '';
                }
            });
    
            // Prevent form submission when selecting from dropdown
            resultsList.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
            });
        } else {
            console.error('Property address input not found');
        }
    },

    initPartnersSection: function() {
        const partnersContainer = document.getElementById('partners-container');
        const addPartnerButton = document.getElementById('add-partner-button');
        
        if (partnersContainer && addPartnerButton) {
            // Remove existing event listeners for better cleanup
            addPartnerButton.replaceWith(addPartnerButton.cloneNode(true));
            const newAddPartnerButton = document.getElementById('add-partner-button');
            
            // Add single event listener for add partner button
            newAddPartnerButton.addEventListener('click', this.addPartner.bind(this));
            
            // Add delegated event listeners for the container
            partnersContainer.addEventListener('change', this.handlePartnerChange.bind(this));
            partnersContainer.addEventListener('input', this.updateTotalEquity.bind(this));
            partnersContainer.addEventListener('click', this.removePartner.bind(this));
    
            // Add initial partner if container is empty
            if (!partnersContainer.querySelector('.partner-entry')) {
                this.addPartner();
            }
    
            console.log('Partners section initialized');
        } else {
            console.error('Partners container or add partner button not found');
        }
    },

    initCalculations: function() {
        // Set up event listeners for income inputs
        document.querySelectorAll('.income-input').forEach(input => {
            input.addEventListener('input', this.updateTotalIncome.bind(this));
        });
    
        // Set up event listeners for expense inputs
        document.querySelectorAll('.expense-input').forEach(input => {
            input.addEventListener('input', this.updateTotalExpenses.bind(this));
        });
    
        // Only calculate totals if we have input fields
        if (document.querySelector('.income-input') || document.querySelector('.expense-input')) {
            this.updateTotalIncome();
            this.updateTotalExpenses();
        }
    },
    
    updateTotalIncome: function() {
        let total = 0;
        const incomeInputs = document.querySelectorAll('.income-input');
        
        incomeInputs.forEach(input => {
            const value = parseFloat(input.value) || 0;
            total += value;
        });
    
        const totalIncomeElement = document.getElementById('total-monthly-income');
        if (totalIncomeElement) {
            totalIncomeElement.textContent = total.toFixed(2);
        }
    },
    
    updateTotalExpenses: function() {
        let total = 0;
        let utilityTotal = 0;
    
        // Change rental-income to monthly_income[rental_income]
        const rentalIncomeElement = document.getElementById('monthly_income[rental_income]');
        const rentalIncome = rentalIncomeElement ? (parseFloat(rentalIncomeElement.value) || 0) : 0;
    
        // Calculate utilities (fixed amounts)
        const utilityInputs = document.querySelectorAll('.utility-input');
        utilityInputs.forEach(input => {
            const value = parseFloat(input.value) || 0;
            utilityTotal += value;
        });
    
        // Calculate percentage-based expenses
        const percentageInputs = document.querySelectorAll('.expense-percent');
        percentageInputs.forEach(input => {
            const percentage = parseFloat(input.value) || 0;
            const amount = (rentalIncome * percentage) / 100;
            total += amount;
        });
    
        // Calculate fixed amount expenses
        const fixedExpenseInputs = document.querySelectorAll('.expense-input:not(.utility-input):not(.expense-percent)');
        fixedExpenseInputs.forEach(input => {
            const value = parseFloat(input.value) || 0;
            total += value;
        });
    
        total += utilityTotal;
    
        const totalExpensesElement = document.getElementById('total-monthly-expenses');
        if (totalExpensesElement) {
            totalExpensesElement.textContent = total.toFixed(2);
        }
    },

    addPartner: function() {
        console.log('Adding new partner');
        const partnersContainer = document.getElementById('partners-container');
        if (!partnersContainer) {
            console.error('Partners container not found');
            return;
        }
    
        const existingPartners = partnersContainer.querySelectorAll('.partner-entry');
        const partnerCount = existingPartners.length;
    
        // Check if we've reached the maximum number of partners (optional)
        if (partnerCount >= 10) {
            window.showNotification('Maximum number of partners reached', 'warning', 'both');
            return;
        }
    
        const newPartnerHtml = `
            <div class="partner-entry card mt-3">
                <div class="card-body">
                    <div class="row g-3">
                        <div class="col-12 col-md-4">
                            <div class="form-group">
                                <label class="form-label" for="partners[${partnerCount}][name]">Partner</label>
                                <select class="form-select partner-select" id="partners[${partnerCount}][name]" name="partners[${partnerCount}][name]" required>
                                    <option value="">Select a partner</option>
                                    ${this.getPartnerOptions()}
                                    <option value="new">Add new partner</option>
                                </select>
                            <div class="form-group mt-2 new-partner-name" style="display: none;">
                                <label for="partners[${partnerCount}][new_name]">New Partner Name:</label>
                                <input type="text" id="partners[${partnerCount}][new_name]" name="partners[${partnerCount}][new_name]" class="form-control">
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="form-group">
                            <label for="partner-equity-${partnerCount}">Equity Share (%):</label>
                            <input type="number" id="partners[${partnerCount}][equity_share]" name="partners[${partnerCount}][equity_share]" class="form-control partner-equity" step="0.01" min="0" max="100" required>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="form-group">
                            <div class="form-check">
                                <input type="checkbox" id="partners[${partnerCount}][equity_share]" name="partners[${partnerCount}][is_property_manager]" class="form-check-input property-manager-check">
                                <label class="form-check-label" for="partners[${partnerCount}][equity_share]">
                                    Property Manager
                                </label>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-2">
                        <button type="button" class="btn btn-danger remove-partner">Remove</button>
                    </div>
                </div>
            </div>
        `;
    
        partnersContainer.insertAdjacentHTML('beforeend', newPartnerHtml);
        this.initPropertyManagerHandlers();
        this.updateTotalEquity();
        console.log('New partner entry added');
    },

    getPartnerOptions: function() {
        // Use partners from template
        const partnerSelects = document.querySelectorAll('.partner-select');
        if (partnerSelects.length > 0) {
            // If we have existing selects, use their options
            return Array.from(partnerSelects[0].options)
                .filter(option => option.value !== 'new')
                .map(option => `<option value="${option.value}">${option.textContent}</option>`)
                .join('');
        } else {
            // If no existing selects, use partners array from the page
            const partners = Array.from(document.querySelectorAll('#partners-list option'))
                .map(option => option.value)
                .filter(value => value && value !== 'new');
            return partners
                .map(partner => `<option value="${partner}">${partner}</option>`)
                .join('');
        }
    },

    handlePartnerChange: function(event) {
        if (event.target.classList.contains('partner-select')) {
            console.log('Partner select changed:', event.target.value);
            const partnerEntry = event.target.closest('.partner-entry');
            const newPartnerNameInput = partnerEntry.querySelector('.new-partner-name');
            
            if (event.target.value === 'new') {
                console.log('New partner selected, showing input field');
                newPartnerNameInput.style.display = 'block';
            } else if (event.target.value) {  // Only check if a partner is actually selected
                // Check for duplicates
                if (this.checkDuplicatePartner(event.target.value)) {
                    console.log('Duplicate partner selected:', event.target.value);
                    window.showNotification(`Partner "${event.target.value}" has already been selected. Each partner can only be added once.`, 'error', 'both');
                    event.target.value = ''; // Reset the selection
                    return;
                }
                console.log('Existing partner selected, hiding input field');
                newPartnerNameInput.style.display = 'none';
            }
        }
    },

    checkDuplicatePartner: function(selectedPartner) {
        const partnerSelects = document.querySelectorAll('.partner-select');
        let count = 0;
        
        partnerSelects.forEach(select => {
            if (select.value === selectedPartner) {
                count++;
            }
        });
        
        return count > 1;
    },

    removePartner: function(event) {
        if (event.target.classList.contains('remove-partner')) {
            event.target.closest('.partner-entry').remove();
            this.updateTotalEquity();
        }
    },

    initPropertyManagerHandlers: function() {
        const partnersContainer = document.getElementById('partners-container');
        if (!partnersContainer) return;
    
        // Add click handler for property Manager checkboxes
        partnersContainer.addEventListener('change', (event) => {
            if (event.target.classList.contains('property-manager-check')) {
                this.handlePropertyManagerChange(event.target);
            }
        });
    },
    
    handlePropertyManagerChange: function(checkbox) {
        const partnersContainer = document.getElementById('partners-container');
        const allCheckboxes = partnersContainer.querySelectorAll('.property-manager-check');
        const partnerEntry = checkbox.closest('.partner-entry');
        const partnerSelect = partnerEntry.querySelector('.partner-select');
        const partnerName = partnerSelect.value === 'new' 
            ? partnerEntry.querySelector('.new-partner-name input').value 
            : partnerSelect.options[partnerSelect.selectedIndex].text;
    
        if (checkbox.checked) {
            // Uncheck all other Property Manager checkboxes
            allCheckboxes.forEach(cb => {
                if (cb !== checkbox) {
                    cb.checked = false;
                }
            });
    
            // Show toastr notification
            if (partnerName) {
                window.showNotification(`${partnerName} has been designated Property Manager!`, 'success', 'both');
            }
        }
    
        // Ensure at least one checkbox is checked if this is the last one
        const anyChecked = Array.from(allCheckboxes).some(cb => cb.checked);
        if (!anyChecked) {
            checkbox.checked = true;
            window.showNotification('At least one partner must be designated as Property Manager', 'warning', 'both');
        }
    },

    updateTotalEquity: function() {
        const equityInputs = document.querySelectorAll('.partner-equity');
        let total = 0;
        equityInputs.forEach(input => {
            total += parseFloat(input.value) || 0;
        });
        const totalEquityElement = document.getElementById('total-equity');
        totalEquityElement.textContent = `${total.toFixed(2)}%`;
        totalEquityElement.classList.remove('text-success', 'text-danger');
        if (Math.abs(total - 100) < 0.01) {
            totalEquityElement.classList.add('text-success');
        } else {
            totalEquityElement.classList.add('text-danger'); 
        }
    },

    handleSubmit: function(event) {
        event.preventDefault();
        console.log('Form submission started');
        
        const form = event.target;
        const formData = new FormData(form);
        
        if (!this.validateForm(form)) {
            console.log('Form validation failed');
            return;
        }

    
        // Helper function to safely get string values
        const getStringValue = (fieldName, defaultValue = '') => {
            const value = formData.get(fieldName);
            return value === null ? defaultValue : value;
        };
    
        try {
            const propertyData = {
                // Basic Property Information
                address: getStringValue('property_address'),
                purchase_date: getStringValue('purchase_date'),
                purchase_price: this.getNumericValue(formData, 'purchase_price'),
                down_payment: this.getNumericValue(formData, 'down_payment'),
                closing_costs: this.getNumericValue(formData, 'closing_costs'),
                renovation_costs: this.getNumericValue(formData, 'renovation_costs'),
                marketing_costs: this.getNumericValue(formData, 'marketing_costs'),
                
                // Primary Loan Information
                primary_loan_amount: this.getNumericValue(formData, 'primary_loan_amount'),
                primary_loan_start_date: getStringValue('primary_loan_start_date'),
                primary_loan_rate: this.getNumericValue(formData, 'primary_loan_rate'),
                primary_loan_term: LoanTermToggle.getValueInMonths('primary_loan_term'),
                
                // Secondary Loan Information
                secondary_loan_amount: this.getNumericValue(formData, 'secondary_loan_amount'),
                secondary_loan_rate: this.getNumericValue(formData, 'secondary_loan_rate'),
                secondary_loan_term: LoanTermToggle.getValueInMonths('secondary_loan_term'),
                
                // Monthly Income
                monthly_income: {
                    rental_income: this.getNumericValue(formData, 'monthly_income[rental_income]'),
                    parking_income: this.getNumericValue(formData, 'monthly_income[parking_income]'),
                    laundry_income: this.getNumericValue(formData, 'monthly_income[laundry_income]'),
                    other_income: this.getNumericValue(formData, 'monthly_income[other_income]'),
                    income_notes: getStringValue('monthly_income[income_notes]')
                },
                
                // Monthly Expenses
                monthly_expenses: {
                    // Fixed Expenses
                    property_tax: this.getNumericValue(formData, 'monthly_expenses[property_tax]'),
                    insurance: this.getNumericValue(formData, 'monthly_expenses[insurance]'),
                    hoa_fees: this.getNumericValue(formData, 'monthly_expenses[hoa_fees]'),
                    
                    // Percentage Based Expenses
                    repairs: this.getNumericValue(formData, 'monthly_expenses[repairs]'),
                    capex: this.getNumericValue(formData, 'monthly_expenses[capex]'),
                    property_management: this.getNumericValue(formData, 'monthly_expenses[property_management]'),
                    
                    // Utilities
                    utilities: {
                        water: this.getNumericValue(formData, 'monthly_expenses[utilities][water]'),
                        electricity: this.getNumericValue(formData, 'monthly_expenses[utilities][electricity]'),
                        gas: this.getNumericValue(formData, 'monthly_expenses[utilities][gas]'),
                        trash: this.getNumericValue(formData, 'monthly_expenses[utilities][trash]')
                    },
                    
                    other_expenses: this.getNumericValue(formData, 'monthly_expenses[other_expenses]'),
                    expense_notes: getStringValue('monthly_expenses[expense_notes]')
                },
                partners: []
            };
    
            // Process partners data
            const partnerEntries = form.querySelectorAll('.partner-entry');
            partnerEntries.forEach((entry, index) => {
                const nameSelect = entry.querySelector(`[name="partners[${index}][name]"]`);
                const equityInput = entry.querySelector(`[name="partners[${index}][equity_share]"]`);
                const propertyManagerCheck = entry.querySelector(`[name="partners[${index}][is_property_manager]"]`);
                
                if (nameSelect && equityInput) {
                    let name = nameSelect.value.trim();
                    const equityShare = this.getNumericValue(formData, `partners[${index}][equity_share]`);
                    
                    // Handle new partner case
                    if (name === 'new') {
                        const newPartnerNameInput = entry.querySelector(`[name="partners[${index}][new_name]"]`);
                        if (newPartnerNameInput) {
                            name = newPartnerNameInput.value.trim();
                        }
                    }
                    
                    if (name && !isNaN(equityShare)) {
                        propertyData.partners.push({
                            name,
                            equity_share: equityShare,
                            is_property_manager: propertyManagerCheck ? propertyManagerCheck.checked : false
                        });
                    }
                }
            });
    
            console.log('Sending property data:', JSON.stringify(propertyData, null, 2));
    
            // Submit data to server
            fetch('/properties/add_properties', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(propertyData)
            })
            .then(response => response.json())
            .then(data => {
                console.log('Server response:', data);
                if (data.success) {
                    window.showNotification('Property successfully added!', 'success', 'both');
                    
                    // Wait briefly before redirecting
                    setTimeout(() => {
                        window.location.reload();
                    }, 2000);
                } else {
                    // Enhanced error handling
                    if (data.errors && Array.isArray(data.errors)) {
                        data.errors.forEach(error => {
                            // Convert backend validation messages to user-friendly messages
                            let userMessage = error;
                            
                            // Pattern matching for common validation messages
                            if (error.includes('must equal 100%')) {
                                userMessage = 'Partner equity shares must total exactly 100%';
                            } else if (error.includes('cannot be negative')) {
                                userMessage = error.replace('cannot be negative', 'must be a positive number');
                            } else if (error.includes('Invalid numeric value')) {
                                userMessage = error.replace('Invalid numeric value for', 'Please enter a valid number for');
                            } else if (error.includes('Invalid date format')) {
                                userMessage = 'Please enter dates in YYYY-MM-DD format';
                            } else if (error.includes('Missing required field')) {
                                userMessage = error.replace('Missing required field:', 'Please fill in the required field:');
                            }
                            
                            window.showNotification(userMessage, 'error', 'both');
                        });
                    } else if (data.message) {
                        window.showNotification(data.message, 'error', 'both');
                    } else {
                        window.showNotification('An error occurred while saving the property. Please check all fields and try again.', 'error', 'both');
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                window.showNotification('An unexpected error occurred. Please try again later.', 'error', 'both');
            });
    
        } catch (error) {
            console.error('Error preparing property data:', error);
            window.showNotification('Error preparing property data: ' + error.message, 'error', 'both');
        }
    },

    validateForm: function(form) {
        let isValid = true;
    
        // Required field validation - Updated field names to match HTML
        const requiredFields = [
            { name: 'property_address', label: 'property address' },
            { name: 'purchase_date', label: 'purchase date' },
            { name: 'purchase_price', label: 'purchase price' },
            { name: 'down_payment', label: 'down payment' },
            { name: 'primary_loan_amount', label: 'primary loan amount' },
            { name: 'primary_loan_start_date', label: 'primary loan start date' },
            { name: 'primary_loan_rate', label: 'primary loan rate' },
            { name: 'primary_loan_term', label: 'primary loan term' }
        ];
    
        requiredFields.forEach(field => {
            const input = form.querySelector(`[name="${field.name}"]`);
            if (!input || !input.value.trim()) {
                window.showNotification(`Please enter a valid ${field.label}.`, 'error', 'both');
                isValid = false;
            }
        });
    
        // Numeric field validation - Updated field names
        const numericFields = [
            { name: 'purchase_price', label: 'Purchase price' },
            { name: 'down_payment', label: 'Down payment' },
            { name: 'primary_loan_amount', label: 'Primary loan amount' },
            { name: 'primary_loan_rate', label: 'Primary loan rate' },
            { name: 'primary_loan_term', label: 'Primary loan term' },
            { name: 'closing_costs', label: 'Closing costs' },
            { name: 'renovation_costs', label: 'Renovation costs' },
            { name: 'marketing_costs', label: 'Marketing costs' }
        ];
    
        numericFields.forEach(field => {
            const input = form.querySelector(`[name="${field.name}"]`);
            if (input && input.value.trim()) {
                const value = parseFloat(input.value);
                if (isNaN(value) || value < 0) {
                    window.showNotification(`${field.label} must be a valid positive number.`, 'error', 'both');
                    isValid = false;
                }
            }
        });
    
        // Date field validation - Updated field names
        const dateFields = [
            { name: 'purchase_date', label: 'Purchase date' },
            { name: 'primary_loan_start_date', label: 'Primary loan start date' }
        ];
        const currentDate = new Date();
    
        dateFields.forEach(field => {
            const input = form.querySelector(`[name="${field.name}"]`);
            if (input && input.value) {
                const inputDate = new Date(input.value);
                if (isNaN(inputDate.getTime())) {
                    window.showNotification(`Please enter a valid date for ${field.label}.`, 'error', 'both');
                    isValid = false;
                }
                if (inputDate > currentDate) {
                    window.showNotification(`${field.label} cannot be in the future.`, 'warning', 'both');
                }
            }
        });
    
        // Partner validation - Updated selectors
        const partners = form.querySelectorAll('.partner-entry');
        let totalEquity = 0;
        const partnerNames = new Set();
        let propertyManagerCount = 0;
    
        partners.forEach((partner, index) => {
            const nameSelect = partner.querySelector('.partner-select');
            const equityInput = partner.querySelector('.partner-equity');
            const propertyManagerCheck = partner.querySelector('.property-manager-check');
            
            // Validate partner name
            if (nameSelect) {
                let name = nameSelect.value.trim();
                if (!name) {
                    window.showNotification(`Please enter a name for partner ${index + 1}.`, 'error', 'both');
                    isValid = false;
                } else if (name === 'new') {
                    const newPartnerNameInput = partner.querySelector('input[name^="partners"][name$="[new_name]"]');
                    name = newPartnerNameInput ? newPartnerNameInput.value.trim() : '';
                    if (!name) {
                        window.showNotification(`Please enter a name for the new partner ${index + 1}.`, 'error', 'both');
                        isValid = false;
                    }
                }
                
                if (name && name !== 'new') {
                    if (partnerNames.has(name)) {
                        window.showNotification(`Duplicate partner "${name}" found. Each partner can only be added once.`, 'error', 'both');
                        isValid = false;
                    }
                    partnerNames.add(name);
                }
            }
    
            // Validate equity share
            if (equityInput) {
                const equity = parseFloat(equityInput.value);
                if (isNaN(equity) || equity < 0 || equity > 100) {
                    window.showNotification(`Please enter a valid equity share (0-100) for partner ${index + 1}.`, 'error', 'both');
                    isValid = false;
                } else {
                    totalEquity += equity;
                }
            }
    
            // Count property managers
            if (propertyManagerCheck && propertyManagerCheck.checked) {
                propertyManagerCount++;
            }
        });
    
        // Validate total equity
        if (Math.abs(totalEquity - 100) > 0.01) {
            window.showNotification(`Total partner equity must equal 100%. Current total: ${totalEquity.toFixed(2)}%`, 'error', 'both');
            isValid = false;
        }
    
        // Validate property manager designation
        if (propertyManagerCount === 0) {
            window.showNotification('Please designate one partner as Property Manager.', 'error', 'both');
            isValid = false;
        } else if (propertyManagerCount > 1) {
            window.showNotification('Only one partner can be designated as Property Manager.', 'error', 'both');
            isValid = false;
        }
    
        // Loan amount validation - Updated to use querySelector
        const purchasePrice = parseFloat(form.querySelector('[name="purchase_price"]').value) || 0;
        const downPayment = parseFloat(form.querySelector('[name="down_payment"]').value) || 0;
        const primaryLoanAmount = parseFloat(form.querySelector('[name="primary_loan_amount"]').value) || 0;
        const secondaryLoanAmount = parseFloat(form.querySelector('[name="secondary_loan_amount"]').value) || 0;
        const totalLoanAmount = primaryLoanAmount + secondaryLoanAmount;
    
        if (Math.abs(purchasePrice - (downPayment + totalLoanAmount)) > 0.01) {
            window.showNotification('Purchase price must equal down payment plus total loan amounts.', 'error', 'both');
            isValid = false;
        }
    
        return isValid;
    }
};

export default addPropertiesModule;