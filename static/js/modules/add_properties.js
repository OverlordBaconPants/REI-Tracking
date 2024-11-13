
// add_properties.js

const addPropertiesModule = {
    init: async function() {
        if (this.initialized) {
            console.log('Module already initialized');
            return;
        }
        this.initialized = true;
        
        try {
            console.log('Initializing add properties module');
            const form = document.getElementById('add-property-form');
            
            if (form) {
                this.initAddressAutocomplete();
                this.initPartnersSection();
                this.initCalculations();
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
    
        this.updateNetIncome();
    },
    
    updateTotalExpenses: function() {
        let total = 0;
        let utilityTotal = 0;
    
        // Safely get rental income, default to 0 if element doesn't exist or has no value
        const rentalIncomeElement = document.getElementById('rental-income');
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
            
            // Update color based on positive/negative net income
            if (netIncome > 0) {
                netIncomeElement.classList.remove('text-danger');
                netIncomeElement.classList.add('text-success');
            } else {
                netIncomeElement.classList.remove('text-success');
                netIncomeElement.classList.add('text-danger');
            }
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
            window.showNotification('Maximum number of partners reached', 'warning');
            return;
        }
        const newPartnerHtml = `
            <div class="partner-entry mb-3">
                <div class="row align-items-end">
                    <div class="col-md-5">
                        <div class="form-group">
                            <label for="partner-select-${partnerCount}">Partner:</label>
                            <select id="partner-select-${partnerCount}" name="partners[${partnerCount}][name]" class="form-control partner-select">
                                <option value="">Select a partner</option>
                                ${this.getPartnerOptions()}
                                <option value="new">Add new partner</option>
                            </select>
                        </div>
                        <div class="form-group mt-2 new-partner-name" style="display: none;">
                            <label for="new-partner-name-${partnerCount}">New Partner Name:</label>
                            <input type="text" id="new-partner-name-${partnerCount}" name="partners[${partnerCount}][new_name]" class="form-control">
                        </div>
                    </div>
                    <div class="col-md-5">
                        <div class="form-group">
                            <label for="partner-equity-${partnerCount}">Equity Share (%):</label>
                            <input type="number" id="partner-equity-${partnerCount}" name="partners[${partnerCount}][equity_share]" class="form-control partner-equity" step="0.01" min="0" max="100">
                        </div>
                    </div>
                    <div class="col-md-2">
                        <button type="button" class="btn btn-danger remove-partner">Remove</button>
                    </div>
                </div>
            </div>
        `;
        partnersContainer.insertAdjacentHTML('beforeend', newPartnerHtml);
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
            } else {
                console.log('Existing partner selected, hiding input field');
                newPartnerNameInput.style.display = 'none';
            }
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
        totalEquityElement.textContent = `Total Equity: ${total.toFixed(2)}%`;
        totalEquityElement.className = 'mt-3 font-weight-bold';
        if (Math.abs(total - 100) < 0.01) {
            totalEquityElement.classList.add('text-success');
        } else {
            totalEquityElement.classList.add('text-danger');
        }
        totalEquityElement.style.fontSize = '1.2rem';
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
    
        // Helper function to safely get and parse numeric values
        const getNumericValue = (fieldName, defaultValue = 0) => {
            const value = formData.get(fieldName);
            if (value === null || value === '') {
                console.warn(`Field ${fieldName} is missing or empty, using default value: ${defaultValue}`);
                return defaultValue;
            }
            return isNaN(parseFloat(value)) ? defaultValue : parseFloat(value);
        };
    
        // Helper function to safely get string values
        const getStringValue = (fieldName, defaultValue = '') => {
            const value = formData.get(fieldName);
            return value === null ? defaultValue : value;
        };
    
        try {
            const propertyData = {
                address: getStringValue('property_address'),
                purchase_price: getNumericValue('purchase_price'),
                down_payment: getNumericValue('down_payment'),
                primary_loan_rate: getNumericValue('primary_loan_rate'),
                primary_loan_term: getNumericValue('primary_loan_term'),
                purchase_date: getStringValue('purchase_date'),
                loan_amount: getStringValue('loan_amount'),
                loan_start_date: getStringValue('loan_start_date'),
                seller_financing_amount: getNumericValue('seller_financing_amount'),
                seller_financing_rate: getNumericValue('seller_financing_rate'),
                seller_financing_term: getNumericValue('seller_financing_term'),
                closing_costs: getNumericValue('closing_costs'),
                renovation_costs: getNumericValue('renovation_costs'),
                marketing_costs: getNumericValue('marketing_costs'),
                holding_costs: getNumericValue('holding_costs'),
                monthly_income: {
                    rental_income: getNumericValue('monthly_income[rental_income]'),
                    parking_income: getNumericValue('monthly_income[parking_income]'),
                    laundry_income: getNumericValue('monthly_income[laundry_income]'),
                    other_income: getNumericValue('monthly_income[other_income]'),
                    income_notes: getStringValue('monthly_income[income_notes]')
                },
                monthly_expenses: {
                    property_tax: getNumericValue('monthly_expenses[property_tax]'),
                    insurance: getNumericValue('monthly_expenses[insurance]'),
                    repairs: getNumericValue('monthly_expenses[repairs]'),
                    capex: getNumericValue('monthly_expenses[capex]'),
                    property_management: getNumericValue('monthly_expenses[property_management]'),
                    hoa_fees: getNumericValue('monthly_expenses[hoa_fees]'),
                    utilities: {
                        water: getNumericValue('monthly_expenses[utilities][water]'),
                        electricity: getNumericValue('monthly_expenses[utilities][electricity]'),
                        gas: getNumericValue('monthly_expenses[utilities][gas]'),
                        trash: getNumericValue('monthly_expenses[utilities][trash]')
                    },
                    other_expenses: getNumericValue('monthly_expenses[other_expenses]'),
                    expense_notes: getStringValue('monthly_expenses[expense_notes]')
                },
                partners: []
            };
    
            // Collect partner data
            const partnerEntries = form.querySelectorAll('.partner-entry');
            partnerEntries.forEach((entry, index) => {
                const nameInput = entry.querySelector(`[name="partners[${index}][name]"]`);
                const equityInput = entry.querySelector(`[name="partners[${index}][equity_share]"]`);
                
                if (nameInput && equityInput) {
                    let name = nameInput.value.trim();
                    const equityShare = parseFloat(equityInput.value);
                    
                    if (name === 'new') {
                        const newPartnerNameInput = entry.querySelector(`[name="partners[${index}][new_name]"]`);
                        if (newPartnerNameInput) {
                            name = newPartnerNameInput.value.trim();
                        }
                    }
                    
                    if (name && !isNaN(equityShare)) {
                        propertyData.partners.push({ name, equity_share: equityShare });
                    }
                }
            });
    
            console.log('Sending property data:', JSON.stringify(propertyData, null, 2));
    
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
                    window.location.reload();
                } else {
                    window.showNotification('Error: ' + data.message, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                window.showNotification('An error occurred while adding the property. Please check the console for more details.', 'error');
            });
    
        } catch (error) {
            console.error('Error preparing property data:', error);
            window.showNotification('Error preparing property data: ' + error.message, 'error');
        }
    },

    validateForm: function(form) {
        let isValid = true;

        if (!form.property_address.value.trim()) {
            window.showNotification('Please enter a property address.', 'error');
            isValid = false;
        }

        if (!form.purchase_price.value || isNaN(form.purchase_price.value)) {
            window.showNotification('Please enter a valid purchase price.', 'error');
            isValid = false;
        }

        if (!form.down_payment.value || isNaN(form.down_payment.value)) {
            window.showNotification('Please enter a valid down payment amount.', 'error');
            isValid = false;
        }

        if (!form.primary_loan_rate.value || isNaN(form.primary_loan_rate.value)) {
            window.showNotification('Please enter a valid primary loan rate.', 'error');
            isValid = false;
        }

        if (!form.primary_loan_term.value || isNaN(form.primary_loan_term.value)) {
            window.showNotification('Please enter a valid primary loan term.', 'error');
            isValid = false;
        }

        const partners = form.querySelectorAll('.partner-entry');
        let totalEquity = 0;
        partners.forEach((partner, index) => {
            const nameInput = partner.querySelector(`[name="partners[${index}][name]"]`);
            const equityInput = partner.querySelector(`[name="partners[${index}][equity_share]"]`);
            
            if (!nameInput.value.trim()) {
                window.showNotification(`Please enter a name for partner ${index + 1}.`, 'error');
                isValid = false;
            }

            if (!equityInput.value || isNaN(equityInput.value)) {
                window.showNotification(`Please enter a valid equity share for partner ${index + 1}.`, 'error');
                isValid = false;
            } else {
                totalEquity += parseFloat(equityInput.value);
            }
        });

        if (Math.abs(totalEquity - 100) > 0.01) {
            window.showNotification(`Total equity must equal 100%. Current total: ${totalEquity.toFixed(2)}%`, 'error');
            isValid = false;
        }

        return isValid;
    },
};

export default addPropertiesModule;