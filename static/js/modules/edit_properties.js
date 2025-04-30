// edit_properties.js

import LoanTermToggle from './loan_term_toggle.js';

function truncateAddress(address) {
    const commaIndex = address.indexOf(',');
    return commaIndex > -1 ? address.substring(0, commaIndex) : address;
}

const editPropertiesModule = {
    availablePartners: [],
    initialized: false,

    init: async function() {
        if (this.initialized) {
            console.log('Module already initialized');
            return;
        }
    
        try {
            console.log('Initializing edit properties module');
            
            // First fetch available partners
            await this.fetchAvailablePartners();
            
            // Then initialize the form
            this.initializeForm();
    
            // Initialize loan term toggles
            this.initializeLoanTerms();
            
            // After form is initialized, initialize the partners section
            await this.initPartnersSection();
            
            this.initialized = true;
            console.log('Edit Properties module fully initialized');
        } catch (error) {
            console.error('Error initializing Edit Properties module:', error);
            window.showNotification('Error loading Edit Properties module: ' + error.message, 'error', 'both');
        }
    },

    // Form initialization and setup
    initializeForm: function() {
        const propertySelect = document.getElementById('property_select');
        const propertyDetails = document.getElementById('propertyDetails');
        const addPartnerButton = document.getElementById('add-partner-button');
        const partnersContainer = document.getElementById('partners-container');
        const form = document.getElementById('editPropertyForm');
        
        console.log('Form element found:', form !== null);
    
        // Bind 'this' to preserve context
        const self = this;
    
        if (propertySelect) {
            // Remove any existing event listeners
            const newSelect = propertySelect.cloneNode(true);
            propertySelect.parentNode.replaceChild(newSelect, propertySelect);
            
            // Modify existing options to show truncated addresses
            Array.from(newSelect.options).forEach(option => {
                if (option.value) { // Skip the empty/default option
                    option.textContent = truncateAddress(option.value);
                }
            });
            
            // Add event listener
            newSelect.addEventListener('change', (event) => {
                this.handlePropertySelect(event);
            });
            
            console.log('Property select initialized');
        }
    
        if (form) {
            form.addEventListener('submit', (event) => this.handleSubmit(event));
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.addEventListener('click', (event) => {
                    console.log('Submit button clicked');
                    this.handleSubmit(event);
                });
            }
            console.log('Form submit handler initialized');
        } else {
            console.error('Edit property form not found');
        }
    
        if (addPartnerButton) {
            addPartnerButton.addEventListener('click', () => this.addPartnerFields());
            console.log('Add partner button initialized');
        }
    
        if (partnersContainer) {
            this.initPartnersSection();
            console.log('Partners section initialized');
        }
    
        this.initCalculations();
        console.log('Income/expense calculations initialized');
    },

    initializeLoanTerms: function() {
        // Add the required HTML structure if it doesn't exist
        this.ensureLoanTermStructure('primary_loan_term');
        this.ensureLoanTermStructure('secondary_loan_term');
        
        // Initialize the toggle functionality
        LoanTermToggle.init('primary_loan_term', 'secondary_loan_term');
    },

    ensureLoanTermStructure: function(termId) {
        const input = document.getElementById(termId);
        if (!input) {
            console.error(`${termId} input not found`);
            return;
        }
    
        // Check if container already exists
        let container = document.getElementById(`${termId}-container`);
        if (!container) {
            // Create container
            container = document.createElement('div');
            container.id = `${termId}-container`;
            container.className = 'loan-term-container';
    
            // Create years input
            const yearsInput = document.createElement('input');
            yearsInput.type = 'number';
            yearsInput.id = `${termId}-years`;
            yearsInput.className = 'form-control';
            yearsInput.min = '0';
            yearsInput.step = '0.1';
            yearsInput.value = input.value ? (parseFloat(input.value) / 12).toString() : '0';
    
            // Create months input
            const monthsInput = document.createElement('input');
            monthsInput.type = 'number';
            monthsInput.id = `${termId}-months`;
            monthsInput.className = 'form-control';
            monthsInput.min = '0';
            monthsInput.step = '1';
            monthsInput.value = input.value || '0';
    
            // Create toggle button
            const toggleBtn = document.createElement('button');
            toggleBtn.type = 'button';
            toggleBtn.id = `${termId}-toggle`;
            toggleBtn.className = 'btn btn-secondary mt-2';
            toggleBtn.textContent = 'Switch to Months';
    
            // Add elements to container
            container.appendChild(yearsInput);
            container.appendChild(monthsInput);
            container.appendChild(toggleBtn);
    
            // Replace original input with container
            input.parentNode.replaceChild(container, input);
        }
    },

    // Income and Expense Calculations
    initCalculations: function() {
        document.querySelectorAll('.income-input').forEach(input => {
            input.addEventListener('input', this.updateTotalIncome.bind(this));
        });

        document.querySelectorAll('.expense-input').forEach(input => {
            input.addEventListener('input', this.updateTotalExpenses.bind(this));
        });

        this.updateTotalIncome();
        this.updateTotalExpenses();
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
        let rentalIncome = parseFloat(document.querySelector('[name="monthly_income[rental_income]"]').value) || 0;
    
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

    // Property Selection and Details
    handlePropertySelect: function(event) {
        const selectedAddress = event.target.value;
        const propertyDetails = document.getElementById('propertyDetails');

        if (selectedAddress) {
            if (propertyDetails) {
                propertyDetails.classList.remove('hidden');
            }
            this.fetchPropertyDetails(selectedAddress);
        } else {
            if (propertyDetails) {
                propertyDetails.classList.add('hidden');
            }
            this.clearForm();
        }
    },

    fetchPropertyDetails: function(address) {
        const propertyDetails = document.getElementById('propertyDetails');
        
        fetch(`/properties/get_property_details?address=${encodeURIComponent(address)}`)
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(data.message || `HTTP error! status: ${response.status}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    console.log('Received property data:', data.property);
                    if (data.property.partners) {
                        console.log('Partners found:', data.property.partners);
                    } else {
                        console.warn('No partners array in property data');
                    }
                    
                    this.populateForm(data.property);
                    if (propertyDetails) {
                        propertyDetails.classList.remove('hidden');
                    }
                    window.showNotification('Property details loaded successfully', 'success', 'both');
                } else {
                    throw new Error(data.message || 'Unknown error occurred');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                window.showNotification(error.message || 'Error loading property details', 'error', 'both');
                if (propertyDetails) {
                    propertyDetails.classList.add('hidden');
                }
                this.clearForm();
            });
    },

    populateForm: function(property) {
        try {
            console.log('Starting to populate form with property:', property);
    
            // Add the property select handling
            const propertySelect = document.getElementById('property_select');
            if (propertySelect) {
                const options = propertySelect.options;
                for (let i = 0; i < options.length; i++) {
                    if (options[i].value === property.address) {
                        propertySelect.selectedIndex = i;
                        break;
                    }
                }
            }
            
            const setInputValue = (id, value) => {
                const element = document.getElementById(id);
                if (element) {
                    element.value = value ?? '';
                } else {
                    console.warn(`Element with id '${id}' not found`);
                }
            };
     
            // Basic Property Information
            setInputValue('purchase_date', property.purchase_date);
            setInputValue('purchase_price', property.purchase_price);
            setInputValue('down_payment', property.down_payment);
            setInputValue('closing_costs', property.closing_costs);
            setInputValue('renovation_costs', property.renovation_costs);
            setInputValue('marketing_costs', property.marketing_costs);
            
            // Primary Loan Information
            setInputValue('primary_loan_amount', property.primary_loan_amount);
            setInputValue('primary_loan_start_date', property.primary_loan_start_date);
            setInputValue('primary_loan_rate', property.primary_loan_rate);
            
            // Initialize loan terms
            try {
                // Ensure the containers exist first
                this.ensureLoanTermStructure('primary_loan_term');
                this.ensureLoanTermStructure('secondary_loan_term');
                
                // First, set the values
                LoanTermToggle.setValue('primary_loan_term', property.primary_loan_term || 0);
                LoanTermToggle.setValue('secondary_loan_term', property.secondary_loan_term || 0);

                // Then reinitialize the toggle functionality
                LoanTermToggle.init('primary_loan_term', 'secondary_loan_term');
            } catch (e) {
                console.error('Error setting loan terms:', e);
            }
            
            // Secondary Loan Information
            setInputValue('secondary_loan_amount', property.secondary_loan_amount);
            setInputValue('secondary_loan_rate', property.secondary_loan_rate);
     
            // Monthly Income
            if (property.monthly_income) {
                setInputValue('monthly_income[rental_income]', property.monthly_income.rental_income);
                setInputValue('monthly_income[parking_income]', property.monthly_income.parking_income);
                setInputValue('monthly_income[laundry_income]', property.monthly_income.laundry_income);
                setInputValue('monthly_income[other_income]', property.monthly_income.other_income);
                setInputValue('monthly_income[income_notes]', property.monthly_income.income_notes);
            }
     
            // Monthly Expenses
            if (property.monthly_expenses) {
                // Fixed Expenses
                setInputValue('monthly_expenses[property_tax]', property.monthly_expenses.property_tax);
                setInputValue('monthly_expenses[insurance]', property.monthly_expenses.insurance);
                setInputValue('monthly_expenses[hoa_fees]', property.monthly_expenses.hoa_fees);
                
                // Percentage Based Expenses
                setInputValue('monthly_expenses[repairs]', property.monthly_expenses.repairs);
                setInputValue('monthly_expenses[capex]', property.monthly_expenses.capex);
                setInputValue('monthly_expenses[property_management]', property.monthly_expenses.property_management);
                
                // Utilities
                if (property.monthly_expenses.utilities) {
                    setInputValue('monthly_expenses[utilities][water]', property.monthly_expenses.utilities.water);
                    setInputValue('monthly_expenses[utilities][electricity]', property.monthly_expenses.utilities.electricity);
                    setInputValue('monthly_expenses[utilities][gas]', property.monthly_expenses.utilities.gas);
                    setInputValue('monthly_expenses[utilities][trash]', property.monthly_expenses.utilities.trash);
                }
                
                setInputValue('monthly_expenses[other_expenses]', property.monthly_expenses.other_expenses);
                setInputValue('monthly_expenses[expense_notes]', property.monthly_expenses.expense_notes);
            }
     
            // Partners Section
            // First clear the partners container
            const partnersContainer = document.getElementById('partners-container');
            if (partnersContainer) {
                partnersContainer.innerHTML = '';
            }
            
            // Handle partners
            if (property.partners && Array.isArray(property.partners)) {
                console.log('Processing partners:', property.partners);
                const partnersContainer = document.getElementById('partners-container');
                if (!partnersContainer) {
                    console.error('Partners container not found');
                    return;
                }
    
                // Clear existing partners
                partnersContainer.innerHTML = '';
    
                // Add each partner with their data
                property.partners.forEach((partner, index) => {
                    console.log(`Adding partner ${index}:`, partner);
                    const partnerHtml = `
                        <div class="partner-entry card mt-3">
                            <div class="card-body">
                                <div class="row g-3">
                                    <div class="col-12 col-md-4">
                                        <div class="form-group">
                                            <label class="form-label" for="partners[${index}][name]">Partner</label>
                                            <select class="form-select partner-select" 
                                                    id="partners[${index}][name]" 
                                                    name="partners[${index}][name]" 
                                                    required>
                                                <option value="">Select a partner</option>
                                                ${this.availablePartners.map(p => 
                                                    `<option value="${p}" ${p === partner.name ? 'selected' : ''}>${p}</option>`
                                                ).join('')}
                                                <option value="new">Add new partner</option>
                                            </select>
                                            <div class="form-group mt-2 new-partner-name" style="display: none;">
                                                <label class="form-label" for="partners[${index}][new_name]">New Partner Name</label>
                                                <input type="text" 
                                                    id="partners[${index}][new_name]" 
                                                    name="partners[${index}][new_name]" 
                                                    class="form-control">
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-12 col-md-3">
                                        <div class="form-group">
                                            <label class="form-label" for="partners[${index}][equity_share]">Equity Share</label>
                                            <div class="input-group">
                                                <input type="number" 
                                                    id="partners[${index}][equity_share]" 
                                                    name="partners[${index}][equity_share]" 
                                                    class="form-control partner-equity" 
                                                    value="${partner.equity_share}"
                                                    step="0.01" min="0" max="100" required>
                                                <span class="input-group-text">%</span>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-12 col-md-3">
                                        <div class="form-group">
                                            <div class="form-check">
                                                <input type="checkbox" 
                                                    id="partners[${index}][is_property_manager]" 
                                                    name="partners[${index}][is_property_manager]" 
                                                    class="form-check-input property-manager-check"
                                                    ${partner.is_property_manager ? 'checked' : ''}>
                                                <label class="form-check-label" for="partners[${index}][is_property_manager]">
                                                    Property Manager
                                                </label>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-12 col-md-2">
                                        <button type="button" class="btn btn-danger remove-partner">
                                            <i class="bi bi-trash me-2"></i>Remove
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                    partnersContainer.insertAdjacentHTML('beforeend', partnerHtml);
                });
    
                // Update total equity after all partners are added
                this.updateTotalEquity();
            }
    
            // Update calculations after all fields are populated
            this.updateTotalIncome();
            this.updateTotalExpenses();
    
            console.log('Form population complete');
        } catch (error) {
            console.error('Error populating form:', error);
            throw error;
        }
    },

    addPartnerFields: function(partner = {}) {
        console.log('Adding new partner fields with data:', partner);
        const partnersContainer = document.getElementById('partners-container');
        if (!partnersContainer) {
            console.error('Partners container not found');
            return;
        }
    
        const partnerCount = partnersContainer.querySelectorAll('.partner-entry').length;
        console.log(`Current partner count: ${partnerCount}`);
    
        // First, ensure we have the partner options available
        const partnerOptions = this.getPartnerOptions();
        console.log('Available partner options:', partnerOptions);
        
        const partnerHtml = `
            <div class="partner-entry card mt-3">
                <div class="card-body">
                    <div class="row g-3">
                        <div class="col-12 col-md-4">
                            <div class="form-group">
                                <label class="form-label" for="partners[${partnerCount}][name]">Partner</label>
                                <select class="form-select partner-select" 
                                        id="partners[${partnerCount}][name]" 
                                        name="partners[${partnerCount}][name]" 
                                        required>
                                    <option value="">Select a partner</option>
                                    ${partnerOptions}
                                    <option value="new">Add new partner</option>
                                </select>
                                <div class="form-group mt-2 new-partner-name" style="display: none;">
                                    <label class="form-label" for="partners[${partnerCount}][new_name]">New Partner Name</label>
                                    <input type="text" 
                                           id="partners[${partnerCount}][new_name]" 
                                           name="partners[${partnerCount}][new_name]" 
                                           class="form-control">
                                </div>
                            </div>
                        </div>
                        <div class="col-12 col-md-3">
                            <div class="form-group">
                                <label class="form-label" for="partners[${partnerCount}][equity_share]">Equity Share</label>
                                <div class="input-group">
                                    <input type="number" 
                                           id="partners[${partnerCount}][equity_share]" 
                                           name="partners[${partnerCount}][equity_share]" 
                                           class="form-control partner-equity" 
                                           step="0.01" min="0" max="100" required>
                                    <span class="input-group-text">%</span>
                                </div>
                            </div>
                        </div>
                        <div class="col-12 col-md-3">
                            <div class="form-group">
                                <label class="d-block"></label>
                                <div class="form-check">
                                    <input type="checkbox" 
                                           id="partners[${partnerCount}][is_property_manager]" 
                                           name="partners[${partnerCount}][is_property_manager]" 
                                           class="form-check-input project-manager-check">
                                    <label class="form-check-label" for="partners[${partnerCount}][is_property_manager]">
                                        Property Manager
                                    </label>
                                </div>
                            </div>
                        </div>
                        <div class="col-12 col-md-2">
                            <label class="d-block"></label>
                            <button type="button" class="btn btn-danger remove-partner">
                                <i class="bi bi-trash me-2"></i>Remove
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    
        // Add the HTML to the container
        partnersContainer.insertAdjacentHTML('beforeend', partnerHtml);
        console.log('Partner HTML added to container');
    
        // Get the newly added partner entry
        const newEntry = partnersContainer.lastElementChild;
        if (!newEntry) {
            console.error('Failed to add new partner entry');
            return;
        }
    
        if (partner && partner.name) {
            console.log('Setting values for partner:', partner);
    
            // Get form elements
            const select = newEntry.querySelector('.partner-select');
            const equityInput = newEntry.querySelector('.partner-equity');
            const propertyManagerCheck = newEntry.querySelector('.project-manager-check');
    
            // Set partner name in select
            if (select) {
                console.log('Found select element, setting partner name:', partner.name);
                // First check if the option exists
                let option = Array.from(select.options).find(opt => opt.value === partner.name);
                if (!option) {
                    console.log('Partner option not found, adding new option');
                    option = new Option(partner.name, partner.name);
                    // Add it before the "Add new partner" option
                    const newPartnerOption = select.querySelector('option[value="new"]');
                    select.insertBefore(option, newPartnerOption);
                }
                select.value = partner.name;
                console.log('Select value set to:', select.value);
            } else {
                console.error('Partner select element not found');
            }
    
            // Set equity share
            if (equityInput) {
                console.log('Setting equity share:', partner.equity_share);
                equityInput.value = partner.equity_share;
                console.log('Equity input value set to:', equityInput.value);
            } else {
                console.error('Equity input not found');
            }
    
            // Set property manager status
            if (propertyManagerCheck) {
                console.log('Setting property manager status:', partner.is_property_manager);
                propertyManagerCheck.checked = partner.is_property_manager;
                console.log('Property manager checkbox set to:', propertyManagerCheck.checked);
            } else {
                console.error('Property manager checkbox not found');
            }
        }
    
        this.updateTotalEquity();
        console.log('Partner fields completely added and populated');
    },

    // Add method to disable form editing for non-Property Managers
    disableFormEditing: function() {
        const form = document.getElementById('editPropertyForm');
        if (!form) return;

        // Disable all inputs except those needed for viewing
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.disabled = true;
        });

        // Hide action buttons
        const actionButtons = form.querySelectorAll('button[type="submit"], #add-partner-button');
        actionButtons.forEach(button => {
            button.style.display = 'none';
        });

        // Add notice to user
        const notice = document.createElement('div');
        notice.className = 'alert alert-warning mt-3';
        notice.textContent = 'Only the designated Property Manager can edit property details.';
        form.appendChild(notice);
    },

    clearForm: function() {
        const form = document.getElementById('editPropertyForm');
        if (form) {
            form.reset();
        }

        const partnersContainer = document.getElementById('partners-container');
        if (partnersContainer) {
            partnersContainer.innerHTML = '';
        }

        this.updateTotalEquity();
        this.updateTotalIncome();
        this.updateTotalExpenses();
    },

    // Partners Management
    fetchAvailablePartners: async function() {
        try {
            const response = await fetch('/properties/get_available_partners');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            if (data.success) {
                this.availablePartners = data.partners;
                console.log('Available partners loaded:', this.availablePartners);
            } else {
                throw new Error(data.message || 'Failed to fetch partners');
            }
        } catch (error) {
            console.error('Error fetching partners:', error);
            window.showNotification('Error loading available partners', 'error', 'both');
            throw error;
        }
    },
    
    // Helper function to get partner options
    getPartnerOptions: function() {
        console.log('Available partners:', this.availablePartners);
        return this.availablePartners
            .map(partner => {
                console.log('Creating option for partner:', partner);
                return `<option value="${partner}">${partner}</option>`;
            })
            .join('');
    },

    initPartnersSection: function() {
        console.log('Initializing partners section');
        const partnersContainer = document.getElementById('partners-container');

        if (!partnersContainer) {
            console.error('Partners container not found during initialization');
            return;
        }
        
        if (partnersContainer) {
            // Clear any existing content
            partnersContainer.innerHTML = '';
            
            // Add event listeners for the container
            partnersContainer.addEventListener('change', (event) => {
                if (event.target.classList.contains('partner-select')) {
                    this.handlePartnerSelectChange(event);
                }
                if (event.target.classList.contains('partner-equity')) {
                    this.updateTotalEquity();
                }
                if (event.target.classList.contains('project-manager-check')) {
                    this.handlePropertyManagerChange(event.target);
                }
            });

            console.log('Partners section initialized successfully');
            return true;
        } else {
            console.error('Partners container not found');
            return false;
        }
    },

    debugPartnerData: function(property) {
        console.group('Partner Data Debug');
        console.log('Raw property data:', property);
        console.log('Partners array:', property.partners);
        if (property.partners) {
            property.partners.forEach((partner, index) => {
                console.log(`Partner ${index + 1}:`, {
                    name: partner.name,
                    equity_share: partner.equity_share,
                    is_property_manager: partner.is_property_manager
                });
            });
        }
        console.groupEnd();
    },

    addPartnerFields: function(partner = {}) {
        console.log('Adding new partner fields');
        const partnersContainer = document.getElementById('partners-container');
        if (!partnersContainer) {
            console.error('Partners container not found');
            return;
        }

        if (!this.availablePartners.length) {
            console.warn('Partner list not available');
            window.showNotification('Partner list not available', 'error', 'both');
            return;
        }

        const partnerCount = partnersContainer.querySelectorAll('.partner-entry').length;
        const partnerHtml = `
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
                                    <label class="form-label" for="partners[${partnerCount}][new_name]">New Partner Name</label>
                                    <input type="text" id="partners[${partnerCount}][new_name]" name="partners[${partnerCount}][new_name]" class="form-control">
                                </div>
                            </div>
                        </div>
                        <div class="col-12 col-md-3">
                            <div class="form-group">
                                <label class="form-label" for="partners[${partnerCount}][equity_share]">Equity Share</label>
                                <div class="input-group">
                                    <input type="number" id="partners[${partnerCount}][equity_share]" name="partners[${partnerCount}][equity_share]" class="form-control partner-equity" step="0.01" min="0" max="100" required>
                                    <span class="input-group-text">%</span>
                                </div>
                            </div>
                        </div>
                        <div class="col-12 col-md-3">
                            <div class="form-group">
                                <div class="form-check">
                                    <input type="checkbox" id="partners[${partnerCount}][is_property_manager]" name="partners[${partnerCount}][is_property_manager]" class="form-check-input property-manager-check">
                                    <label class="form-check-label" for="partners[${partnerCount}][is_property_manager]">Property Manager</label>
                                </div>
                            </div>
                        </div>
                        <div class="col-12 col-md-2">
                            <button type="button" class="btn btn-danger remove-partner">Remove</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        partnersContainer.insertAdjacentHTML('beforeend', partnerHtml);
        
        if (partner.name) {
            const select = partnersContainer.querySelector(`#partner-select-${partnerCount}`);
            if (select) {
                select.value = partner.name;
            }
        }

        const newSelect = partnersContainer.querySelector(`#partner-select-${partnerCount}`);
        if (newSelect) {
            newSelect.addEventListener('change', (event) => this.handlePartnerSelectChange(event));
        }
        
        this.updateTotalEquity();
        console.log('New partner fields added');
    },

    handlePartnerSelectChange: function(event) {
        const select = event.target;
        const partnerEntry = select.closest('.partner-entry');
        const newPartnerNameDiv = partnerEntry.querySelector('.new-partner-name');  // Fixed selector
        
        if (select.value === 'new') {
            newPartnerNameDiv.style.display = 'block';
        } else {
            newPartnerNameDiv.style.display = 'none';
        }
    },

    removePartner: function(event) {
        if (event.target.classList.contains('remove-partner')) {
            event.target.closest('.partner-entry').remove();
            this.updateTotalEquity();
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

    initPropertyManagerHandlers: function() {
        const partnersContainer = document.getElementById('partners-container');
        if (!partnersContainer) return;
    
        // Add click handler for Property Manager checkboxes
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
    
        const anyChecked = Array.from(allCheckboxes).some(cb => cb.checked);
        if (!anyChecked) {
            checkbox.checked = true;
            window.showNotification('At least one partner must be designated as Property Manager', 'warning', 'both');
        }
    },

    handleSubmit: function(event) {
        event.preventDefault();
        
        // Get property select value
        const propertySelect = document.getElementById('property_select');
        if (!propertySelect || !propertySelect.value) {
            window.showNotification('Please select a property to edit', 'error', 'both');
            return;
        }
    
        // Validate required fields
        const requiredFields = {
            'purchase_date': 'Purchase date',
            'primary_loan_amount': 'Primary loan amount',
            'primary_loan_start_date': 'Primary loan start date',
            'purchase_price': 'Purchase price',
            'down_payment': 'Down payment',
            'primary_loan_rate': 'Primary loan rate',
            'primary_loan_term': 'Primary loan term'
        };
    
        for (const [fieldId, fieldName] of Object.entries(requiredFields)) {
            const field = document.getElementById(fieldId);
            if (!field || !field.value.trim()) {
                window.showNotification(`Please enter a value for ${fieldName}`, 'error', 'both');
                return;
            }
        }
    
        // Validate numeric fields are positive
        const numericFields = {
            'purchase_price': 'Purchase price',
            'down_payment': 'Down payment',
            'primary_loan_amount': 'Primary loan amount',
            'primary_loan_rate': 'Primary loan rate',
            'primary_loan_term': 'Primary loan term',
            'secondary_loan_amount': 'Secondary loan amount',
            'secondary_loan_rate': 'Secondary loan rate',
            'secondary_loan_term': 'Secondary loan term',
            'closing_costs': 'Closing costs',
            'renovation_costs': 'Renovation costs',
            'marketing_costs': 'Marketing costs'
        };
    
        for (const [fieldId, fieldName] of Object.entries(numericFields)) {
            const field = document.getElementById(fieldId);
            const value = parseFloat(field?.value || '0');
            if (isNaN(value) || value < 0) {
                window.showNotification(`${fieldName} must be a positive number`, 'error', 'both');
                return;
            }
        }
    
        // Validate partners
        const partnerEntries = document.querySelectorAll('.partner-entry');
        if (partnerEntries.length === 0) {
            window.showNotification('At least one partner is required', 'error', 'both');
            return;
        }
    
        // Validate partner information
        const partners = [];
        const partnerNames = new Set();
    
        for (const entry of partnerEntries) {
            const select = entry.querySelector('.partner-select');
            const equityInput = entry.querySelector('.partner-equity');
            let partnerName;
    
            if (select.value === 'new') {
                const newNameInput = entry.querySelector('.new-partner-input input');
                if (!newNameInput || !newNameInput.value.trim()) {
                    window.showNotification('Please enter a name for the new partner', 'error', 'both');
                    return;
                }
                partnerName = newNameInput.value.trim();
            } else if (!select.value) {
                window.showNotification('Please select or enter a partner name', 'error', 'both');
                return;
            } else {
                partnerName = select.value;
            }
    
            if (partnerNames.has(partnerName)) {
                window.showNotification(`Duplicate partner name: ${partnerName}. Each partner can only be added once.`, 'error', 'both');
                return;
            }
            partnerNames.add(partnerName);
    
            const equityShare = parseFloat(equityInput.value);
            if (isNaN(equityShare) || equityShare <= 0 || equityShare > 100) {
                window.showNotification(`Please enter a valid equity share (between 0 and 100) for partner ${partnerName}`, 'error', 'both');
                return;
            }
    
            partners.push({ name: partnerName, equity_share: equityShare });
        }
    
        // Validate total equity equals 100%
        const totalEquityElement = document.getElementById('total-equity');
        const totalEquity = parseFloat(totalEquityElement.textContent);
        if (Math.abs(totalEquity - 100) > 0.01) {
            window.showNotification(`Total equity must equal 100%. Current total: ${totalEquity.toFixed(2)}%`, 'error', 'both');
            return;
        }
    
        // Collect and send the property data
        const propertyData = this.collectPropertyData(propertySelect.value);
        
        // Send the POST request
        fetch('/properties/edit_properties', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(propertyData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.showNotification('Property updated successfully', 'success', 'both');
                setTimeout(() => window.location.reload(), 2000);
            } else {
                if (data.errors && Array.isArray(data.errors)) {
                    data.errors.forEach(error => {
                        window.showNotification(error, 'error', 'both');
                    });
                } else {
                    window.showNotification(data.message || 'Error updating property', 'error', 'both');
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            window.showNotification('An unexpected error occurred while updating the property', 'error', 'both');
        });
    },

    // Helper function to collect property data
    collectPropertyData: function(address) {
        const propertyData = {
            address: address,
            // Basic Property Information
            purchase_date: document.getElementById('purchase_date').value,
            purchase_price: parseInt(document.getElementById('purchase_price').value),
            down_payment: parseInt(document.getElementById('down_payment').value),
            closing_costs: parseInt(document.getElementById('closing_costs').value || '0'),
            renovation_costs: parseInt(document.getElementById('renovation_costs').value || '0'),
            marketing_costs: parseInt(document.getElementById('marketing_costs').value || '0'),
            
            // Loan Information
            primary_loan_amount: parseFloat(document.getElementById('primary_loan_amount').value),
            primary_loan_start_date: document.getElementById('primary_loan_start_date').value,
            primary_loan_rate: parseFloat(document.getElementById('primary_loan_rate').value),
            primary_loan_term: LoanTermToggle.getValueInMonths('primary_loan_term'),
            secondary_loan_amount: parseInt(document.getElementById('secondary_loan_amount').value || '0'),
            secondary_loan_rate: parseFloat(document.getElementById('secondary_loan_rate').value || '0'),
            secondary_loan_term: LoanTermToggle.getValueInMonths('secondary_loan_term'),
    
            // Monthly Income
            monthly_income: {
                rental_income: parseFloat(document.querySelector('[name="monthly_income[rental_income]"]').value || '0'),
                parking_income: parseFloat(document.querySelector('[name="monthly_income[parking_income]"]').value || '0'),
                laundry_income: parseFloat(document.querySelector('[name="monthly_income[laundry_income]"]').value || '0'),
                other_income: parseFloat(document.querySelector('[name="monthly_income[other_income]"]').value || '0'),
                income_notes: document.querySelector('[name="monthly_income[income_notes]"]').value
            },
    
            // Monthly Expenses
            monthly_expenses: {
                property_tax: parseFloat(document.querySelector('[name="monthly_expenses[property_tax]"]').value || '0'),
                insurance: parseFloat(document.querySelector('[name="monthly_expenses[insurance]"]').value || '0'),
                repairs: parseFloat(document.querySelector('[name="monthly_expenses[repairs]"]').value || '0'),
                capex: parseFloat(document.querySelector('[name="monthly_expenses[capex]"]').value || '0'),
                property_management: parseFloat(document.querySelector('[name="monthly_expenses[property_management]"]').value || '0'),
                hoa_fees: parseFloat(document.querySelector('[name="monthly_expenses[hoa_fees]"]').value || '0'),
                utilities: {
                    water: parseFloat(document.querySelector('[name="monthly_expenses[utilities][water]"]').value || '0'),
                    electricity: parseFloat(document.querySelector('[name="monthly_expenses[utilities][electricity]"]').value || '0'),
                    gas: parseFloat(document.querySelector('[name="monthly_expenses[utilities][gas]"]').value || '0'),
                    trash: parseFloat(document.querySelector('[name="monthly_expenses[utilities][trash]"]').value || '0')
                },
                other_expenses: parseFloat(document.querySelector('[name="monthly_expenses[other_expenses]"]').value || '0'),
                expense_notes: document.querySelector('[name="monthly_expenses[expense_notes]"]').value
            },
            partners: []
        };
    
        // Collect partner information
        const partnerEntries = document.querySelectorAll('.partner-entry');
        partnerEntries.forEach((entry) => {
            const nameSelect = entry.querySelector('.partner-select');
            const equityInput = entry.querySelector('.partner-equity');
            const propertyManagerCheck = entry.querySelector('.project-manager-check'); // Updated class name
            
            let name = nameSelect.value;
            if (name === 'new') {
                const newNameInput = entry.querySelector('[name$="[new_name]"]');
                name = newNameInput.value.trim();
            }
            
            const equityShare = parseFloat(equityInput.value);
            
            if (name && !isNaN(equityShare)) {
                propertyData.partners.push({
                    name: name,
                    equity_share: equityShare,
                    is_property_manager: propertyManagerCheck ? propertyManagerCheck.checked : false
                });
            }
        });
        
        return propertyData;
    }
};

export default editPropertiesModule;