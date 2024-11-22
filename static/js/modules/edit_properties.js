// @ts-nocheck

// edit_properties.js

const editPropertiesModule = {
    // Class property for available partners
    availablePartners: [],

    // Initialization
    init: async function() {
        if (this.initialized) {
            console.log('Module already initialized');
            return;
        }

        try {
            console.log('Initializing edit properties module');
            await this.fetchAvailablePartners();
            this.initializeForm();
            this.initialized = true;
            window.showNotification('Edit Properties module loaded', 'success', 'both');
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
            propertySelect.addEventListener('change', function(event) {
                self.handlePropertySelect(event);
            });
            propertySelect.addEventListener('change', function() {
                setTimeout(() => {
                    self.updateTotalIncome();
                    self.updateTotalExpenses();
                }, 100);
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

        this.updateNetIncome();
    },

    updateTotalExpenses: function() {
        let total = 0;
        let utilityTotal = 0;
        let rentalIncome = parseFloat(document.getElementById('rental-income').value) || 0;
    
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
    
        this.updateNetIncome();
    },

    updateNetIncome: function() {
        const totalIncomeElement = document.getElementById('total-monthly-income');
        const totalExpensesElement = document.getElementById('total-monthly-expenses');
        const netIncomeElement = document.getElementById('net-monthly-income');

        if (totalIncomeElement && totalExpensesElement && netIncomeElement) {
            const totalIncome = parseFloat(totalIncomeElement.textContent) || 0;
            const totalExpenses = parseFloat(totalExpensesElement.textContent) || 0;
            const netIncome = totalIncome - totalExpenses;

            netIncomeElement.textContent = netIncome.toFixed(2);
            
            if (netIncome > 0) {
                netIncomeElement.classList.remove('text-danger');
                netIncomeElement.classList.add('text-success');
            } else {
                netIncomeElement.classList.remove('text-success');
                netIncomeElement.classList.add('text-danger');
            }
        }
    },

    // Property Selection and Details
    handlePropertySelect: function(event) {
        const selectedAddress = event.target.value;
        const propertyDetails = document.getElementById('propertyDetails');

        if (selectedAddress) {
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
            const setInputValue = (id, value) => {
                const element = document.getElementById(id);
                if (element) {
                    element.value = value ?? '';
                } else {
                    console.warn(`Element with id '${id}' not found`);
                }
            };

            setInputValue('purchase-date', property.purchase_date);
            setInputValue('loan-amount', property.loan_amount);
            setInputValue('loan-start-date', property.loan_start_date);
            setInputValue('purchase-price', property.purchase_price);
            setInputValue('down-payment', property.down_payment);
            setInputValue('primary-loan-rate', property.primary_loan_rate);
            setInputValue('primary-loan-term', property.primary_loan_term);
            setInputValue('seller-financing-amount', property.seller_financing_amount);
            setInputValue('seller-financing-rate', property.seller_financing_rate);
            setInputValue('seller-financing-term', property.seller_financing_term);
            setInputValue('closing-costs', property.closing_costs);
            setInputValue('renovation-costs', property.renovation_costs);
            setInputValue('marketing-costs', property.marketing_costs);
            setInputValue('holding-costs', property.holding_costs);

            // Monthly Income
            if (property.monthly_income) {
                setInputValue('rental-income', property.monthly_income.rental_income);
                setInputValue('parking-income', property.monthly_income.parking_income);
                setInputValue('laundry-income', property.monthly_income.laundry_income);
                setInputValue('other-income', property.monthly_income.other_income);
                setInputValue('income-notes', property.monthly_income.income_notes);
            }

            // Monthly Expenses
            if (property.monthly_expenses) {
                setInputValue('property-tax', property.monthly_expenses.property_tax);
                setInputValue('insurance', property.monthly_expenses.insurance);
                setInputValue('repairs', property.monthly_expenses.repairs);
                setInputValue('capex', property.monthly_expenses.capex);
                setInputValue('property-management', property.monthly_expenses.property_management);
                setInputValue('hoa-fees', property.monthly_expenses.hoa_fees);
                
                if (property.monthly_expenses.utilities) {
                    setInputValue('water', property.monthly_expenses.utilities.water);
                    setInputValue('electricity', property.monthly_expenses.utilities.electricity);
                    setInputValue('gas', property.monthly_expenses.utilities.gas);
                    setInputValue('trash', property.monthly_expenses.utilities.trash);
                }
                
                setInputValue('other-expenses', property.monthly_expenses.other_expenses);
                setInputValue('expense-notes', property.monthly_expenses.expense_notes);
            }

            const partnersContainer = document.getElementById('partners-container');
            if (partnersContainer) {
                partnersContainer.innerHTML = '';
                if (property.partners && Array.isArray(property.partners)) {
                    property.partners.forEach(partner => this.addPartnerFields(partner));
                }
                this.updateTotalEquity();
            }

            // Update all totals
            this.updateTotalIncome();
            this.updateTotalExpenses();

            console.log('Form populated successfully');
        } catch (error) {
            console.error('Error populating form:', error);
            window.showNotification('Error populating form fields', 'error', 'both');
            throw error;
        }
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
    
    getPartnerOptions: function() {
        return this.availablePartners
            .map(partner => `<option value="${partner}">${partner}</option>`)
            .join('');
    },

    initPartnersSection: function() {
        const self = this;
        const partnersContainer = document.getElementById('partners-container');
        const addPartnerButton = document.getElementById('add-partner-button');
        
        if (partnersContainer && addPartnerButton) {
            addPartnerButton.replaceWith(addPartnerButton.cloneNode(true));
            const newAddPartnerButton = document.getElementById('add-partner-button');
            
            newAddPartnerButton.addEventListener('click', () => {
                self.addPartnerFields();
            });
            
            partnersContainer.addEventListener('change', (event) => {
                if (event.target.classList.contains('partner-select')) {
                    self.handlePartnerChange(event);
                    self.updateTotalEquity();
                } else if (event.target.classList.contains('property-manager-checkbox')) {
                    self.handlePropertyManagerSelect(event);
                }
            });
            
            partnersContainer.addEventListener('input', (event) => {
                if (event.target.classList.contains('partner-equity')) {
                    self.updateTotalEquity();
                }
            });
            
            partnersContainer.addEventListener('click', (event) => {
                if (event.target.classList.contains('remove-partner')) {
                    event.target.closest('.partner-entry').remove();
                    self.updateTotalEquity();
                }
            });

            console.log('Partners section initialized');
        } else {
            console.warn('Partners container or add partner button not found');
        }
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
            <div class="partner-entry mb-3">
                <div class="row align-items-end">
                    <div class="col-md-4">
                        <div class="form-group">
                            <label for="partner-select-${partnerCount}">Partner:</label>
                            <select id="partner-select-${partnerCount}" 
                                    name="partners[${partnerCount}][name]" 
                                    class="form-control partner-select" 
                                    required>
                                <option value="">Select a partner</option>
                                ${this.getPartnerOptions()}
                                <option value="new">Add new partner</option>
                            </select>
                            <div class="new-partner-input mt-2" style="display: none;">
                                <label for="new-partner-name-${partnerCount}">New Partner Name:</label>
                                <input type="text" 
                                       id="new-partner-name-${partnerCount}" 
                                       name="partners[${partnerCount}][new_name]" 
                                       class="form-control"
                                       placeholder="Enter new partner name">
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="form-group">
                            <label for="partner-equity-${partnerCount}">Equity Share (%):</label>
                            <input type="number" 
                                   id="partner-equity-${partnerCount}" 
                                   name="partners[${partnerCount}][equity_share]" 
                                   class="form-control partner-equity" 
                                   step="0.01" 
                                   min="0" 
                                   max="100" 
                                   value="${partner.equity_share || ''}"
                                   required>
                        </div>
                    </div>
                    <div class="col-md-2">
                        <div class="form-group">
                            <div class="form-check d-flex align-items-center">
                                <input type="checkbox" 
                                       id="property-manager-${partnerCount}" 
                                       name="partners[${partnerCount}][is_property_manager]" 
                                       class="form-check-input property-manager-checkbox"
                                       ${partner.is_property_manager ? 'checked' : ''}>
                                <label class="form-check-label mx-2" for="property-manager-${partnerCount}">Property Manager</label>
                                <i class="bi bi-info-circle" 
                                   data-bs-toggle="tooltip" 
                                   data-bs-placement="top" 
                                   title="Property Managers have additional privileges including:
                                   • Ability to edit property details
                                   • Ability to delete properties
                                   • Full transaction management rights">
                                </i>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-2">
                        <button type="button" class="btn btn-danger remove-partner">Remove</button>
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

        // Initialize tooltip for the new partner entry
        const tooltipTriggerList = [].slice.call(partnersContainer.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });

        const newSelect = partnersContainer.querySelector(`#partner-select-${partnerCount}`);
        if (newSelect) {
            newSelect.addEventListener('change', (event) => this.handlePartnerSelectChange(event));
        }
        
        this.updateTotalEquity();
        console.log('New partner fields added');
    },

    // Add property manager selection handler
    handlePropertyManagerSelect: function(event) {
        if (event.target.classList.contains('property-manager-checkbox')) {
            const checkboxes = document.querySelectorAll('.property-manager-checkbox');
            checkboxes.forEach(checkbox => {
                if (checkbox !== event.target) {
                    checkbox.checked = false;
                }
            });
        }
    },

    handlePartnerChange: function(event) {
        if (event.target.classList.contains('partner-select')) {
            this.handlePartnerSelectChange(event);
        }
    },

    handlePartnerSelectChange: function(event) {
        const select = event.target;
        const partnerEntry = select.closest('.partner-entry');
        const newPartnerInput = partnerEntry.querySelector('.new-partner-input');
        const newPartnerNameInput = newPartnerInput.querySelector('input');

        if (select.value === 'new') {
            newPartnerInput.style.display = 'block';
            newPartnerNameInput.required = true;
        } else {
            newPartnerInput.style.display = 'none';
            newPartnerNameInput.required = false;
            newPartnerNameInput.value = '';
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
        const totalEquityElement = document.getElementById('total-equity');
        if (!totalEquityElement) return;

        let total = 0;
        equityInputs.forEach(input => {
            total += parseFloat(input.value) || 0;
        });

        totalEquityElement.textContent = `Total Equity: ${total.toFixed(2)}%`;
        totalEquityElement.className = total === 100 ? 'text-success' : 'text-danger';
    },

    handleSubmit: function(event) {
        event.preventDefault();
        console.log('Form submission started');

        // Helper functions for number conversions
        const toFloat = (value) => {
            if (!value || value === '') return 0.0;
            // Remove any formatting characters
            const cleaned = value.toString().replace(/[$,%\s]/g, '');
            const num = parseFloat(cleaned);
            return isNaN(num) ? 0.0 : num;
        };

        const toInt = (value) => {
            if (!value || value === '') return 0;
            // Remove any formatting characters
            const cleaned = value.toString().replace(/[$,%\s]/g, '');
            const num = parseInt(cleaned, 10);
            return isNaN(num) ? 0 : num;
        };

        // Get property select value
        const propertySelect = document.getElementById('property_select');
        if (!propertySelect || !propertySelect.value) {
            window.showNotification('No property selected', 'error', 'both');
            return;
        }

        try {
            // Collect the property data with strict type handling
            const propertyData = {
                address: propertySelect.value.trim(),
                purchase_date: document.getElementById('purchase-date').value,
                loan_amount: toFloat(document.getElementById('loan-amount').value),
                loan_start_date: document.getElementById('loan-start-date').value,
                purchase_price: toFloat(document.getElementById('purchase-price').value),
                down_payment: toFloat(document.getElementById('down-payment').value),
                primary_loan_rate: toFloat(document.getElementById('primary-loan-rate').value),
                primary_loan_term: toInt(document.getElementById('primary-loan-term').value),
                seller_financing_amount: toFloat(document.getElementById('seller-financing-amount').value),
                seller_financing_rate: toFloat(document.getElementById('seller-financing-rate').value),
                seller_financing_term: toInt(document.getElementById('seller-financing-term').value),
                closing_costs: toFloat(document.getElementById('closing-costs').value),
                renovation_costs: toFloat(document.getElementById('renovation-costs').value),
                marketing_costs: toFloat(document.getElementById('marketing-costs').value),
                holding_costs: toFloat(document.getElementById('holding-costs').value),
                monthly_income: {
                    rental_income: toFloat(document.getElementById('rental-income').value),
                    parking_income: toFloat(document.getElementById('parking-income').value),
                    laundry_income: toFloat(document.getElementById('laundry-income').value),
                    other_income: toFloat(document.getElementById('other-income').value),
                    income_notes: document.getElementById('income-notes').value || ''
                },
                monthly_expenses: {
                    property_tax: toFloat(document.getElementById('property-tax').value),
                    insurance: toFloat(document.getElementById('insurance').value),
                    repairs: toFloat(document.getElementById('repairs').value),
                    capex: toFloat(document.getElementById('capex').value),
                    property_management: toFloat(document.getElementById('property-management').value),
                    hoa_fees: toFloat(document.getElementById('hoa-fees').value),
                    utilities: {
                        water: toFloat(document.getElementById('water').value),
                        electricity: toFloat(document.getElementById('electricity').value),
                        gas: toFloat(document.getElementById('gas').value),
                        trash: toFloat(document.getElementById('trash').value)
                    },
                    other_expenses: toFloat(document.getElementById('other-expenses').value),
                    expense_notes: document.getElementById('expense-notes').value || ''
                },
                partners: []
            };

            // Collect partner data
            const partnerEntries = document.querySelectorAll('.partner-entry');
            partnerEntries.forEach((entry, index) => {
                const select = entry.querySelector('.partner-select');
                const equityInput = entry.querySelector('.partner-equity');
                let partnerName;

                if (select.value === 'new') {
                    const newNameInput = entry.querySelector('.new-partner-input input');
                    if (newNameInput && newNameInput.value.trim()) {
                        partnerName = newNameInput.value.trim();
                    }
                } else {
                    partnerName = select.value;
                }

                const equityShare = toFloat(equityInput.value);

                if (partnerName && !isNaN(equityShare)) {
                    propertyData.partners.push({
                        name: partnerName,
                        equity_share: equityShare,
                        is_property_manager: entry.querySelector('.property-manager-checkbox').checked
                    });
                }
            });

            // Log complete data before sending
            console.log('Complete property data:', JSON.stringify(propertyData, null, 2));

            // Send the POST request
            fetch('/properties/edit_properties', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(propertyData)
            })
            .then(response => {
                console.log('Response status:', response.status);
                return response.json().then(data => {
                    if (!response.ok) {
                        console.error('Server validation errors:', data.errors);
                        throw new Error(Array.isArray(data.errors) ? data.errors.join('\n') : data.message);
                    }
                    return data;
                });
            })
            .then(data => {
                console.log('Server response:', data);
                if (data.success) {
                    window.showNotification('Property updated successfully', 'success', 'both');
                    setTimeout(() => {
                        window.location.href = '/properties/edit_properties';
                    }, 2000);
                } else {
                    throw new Error(data.message || 'Error updating property');
                }
            })
            .catch(error => {
                console.error('Error updating property:', error);
                window.showNotification('Error updating property: ' + error.message, 'error', 'both');
            });

        } catch (error) {
            console.error('Error preparing property data:', error);
            window.showNotification('Error preparing property data: ' + error.message, 'error', 'both');
        }
    },

    // Add property manager validation
    validateForm: function(form) {
        let isValid = true;

        // Validate required fields
        if (!form.querySelector('#property_select').value) {
            window.showNotification('Please select a property.', 'error', 'both');
            isValid = false;
        }

        // Validate partners
        const partners = form.querySelectorAll('.partner-entry');
        let totalEquity = 0;

        partners.forEach((partner, index) => {
            const nameSelect = partner.querySelector('.partner-select');
            const equityInput = partner.querySelector('.partner-equity');
            
            if (!nameSelect.value) {
                window.showNotification(`Please select a partner for entry ${index + 1}.`, 'error', 'both');
                isValid = false;
            }

            if (!equityInput.value || isNaN(equityInput.value)) {
                window.showNotification(`Please enter a valid equity share for partner ${index + 1}.`, 'error', 'both');
                isValid = false;
            } else {
                totalEquity += parseFloat(equityInput.value);
            }
        });

        // Validate property manager selection
        const propertyManagerSelected = Array.from(form.querySelectorAll('.property-manager-checkbox'))
            .some(checkbox => checkbox.checked);
        
        if (!propertyManagerSelected) {
            window.showNotification('Please designate one partner as Property Manager.', 'error', 'both');
            isValid = false;
        }

        if (Math.abs(totalEquity - 100) > 0.01) {
            window.showNotification(`Total equity must equal 100%. Current total: ${totalEquity.toFixed(2)}%`, 'error', 'both');
            isValid = false;
        }

        return isValid;
    },

    calculateTotalEquity: function() {
        const equityInputs = document.querySelectorAll('.partner-equity');
        let total = 0;
        equityInputs.forEach(input => {
            total += parseFloat(input.value) || 0;
        });
        return total;
    }
};

export default editPropertiesModule;