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
            this.initPropertyManagerHandlers();
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
                    property.partners.forEach(partner => {
                        this.addPartnerFields({
                            name: partner.name,
                            equity_share: partner.equity_share,
                            is_property_manager: partner.is_property_manager
                        });
                    });
                    this.updateTotalEquity();
                }
            }

            // If user is not Property Manager, disable editing
            if (!property.is_property_manager) {
                this.disableFormEditing();
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
    
    getPartnerOptions: function() {
        return this.availablePartners
            .map(partner => `<option value="${partner}">${partner}</option>`)
            .join('');
    },

    initPartnersSection: function() {
        // Store reference to 'this' for use in callbacks
        const self = this;
        const partnersContainer = document.getElementById('partners-container');
        const addPartnerButton = document.getElementById('add-partner-button');
        
        if (partnersContainer && addPartnerButton) {
            // Remove existing event listeners
            addPartnerButton.replaceWith(addPartnerButton.cloneNode(true));
            const newAddPartnerButton = document.getElementById('add-partner-button');
            
            // Add single event listener for add partner button using arrow function
            newAddPartnerButton.addEventListener('click', () => {
                self.addPartnerFields();
            });
            
            // Add delegated event listeners for the container using arrow functions
            partnersContainer.addEventListener('change', (event) => {
                if (event.target.classList.contains('partner-select')) {
                    self.handlePartnerChange(event);
                    self.updateTotalEquity();
                }
            });
            
            // Partner equity input handler
            partnersContainer.addEventListener('input', (event) => {
                if (event.target.classList.contains('partner-equity')) {
                    self.updateTotalEquity();
                }
            });
            
            // Remove partner button handler
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
                    <div class="col-md-5">
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
                    <div class="col-md-5">
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
                    <div class="col-md-3">
                            <div class="form-group">
                                <div class="form-check">
                                <input type="checkbox" 
                                    id="property-manager-${partnerCount}" 
                                    name="partners[${partnerCount}][is_property_manager]" 
                                    class="form-check-input property-manager-check"
                                    ${partner.is_property_manager ? 'checked' : ''}>
                                <label class="form-check-label" for="property-manager-${partnerCount}">
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
        console.log('Form submission started');
        
        // Get property select value
        const propertySelect = document.getElementById('property_select');
        if (!propertySelect || !propertySelect.value) {
            window.showNotification('Please select a property to edit', 'error', 'both');
            return;
        }

        // Validate required fields
        const requiredFields = {
            'purchase-date': 'Purchase date',
            'loan-amount': 'Loan amount',
            'loan-start-date': 'Loan start date',
            'purchase-price': 'Purchase price',
            'down-payment': 'Down payment',
            'primary-loan-rate': 'Primary loan rate',
            'primary-loan-term': 'Primary loan term'
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
            'purchase-price': 'Purchase price',
            'down-payment': 'Down payment',
            'loan-amount': 'Loan amount',
            'primary-loan-rate': 'Primary loan rate',
            'primary-loan-term': 'Primary loan term',
            'seller-financing-amount': 'Seller financing amount',
            'seller-financing-rate': 'Seller financing rate',
            'seller-financing-term': 'Seller financing term',
            'closing-costs': 'Closing costs',
            'renovation-costs': 'Renovation costs',
            'marketing-costs': 'Marketing costs',
            'holding-costs': 'Holding costs'
        };

        for (const [fieldId, fieldName] of Object.entries(numericFields)) {
            const field = document.getElementById(fieldId);
            const value = parseFloat(field?.value || '0');
            if (isNaN(value) || value < 0) {
                window.showNotification(`${fieldName} must be a positive number`, 'error', 'both');
                return;
            }
        }

        // Validate dates
        const dateFields = ['purchase-date', 'loan-start-date'];
        for (const fieldId of dateFields) {
            const field = document.getElementById(fieldId);
            if (!field || !this.isValidDate(field.value)) {
                window.showNotification(`Please enter a valid date in YYYY-MM-DD format for ${fieldId.replace(/-/g, ' ')}`, 'error', 'both');
                return;
            }
        }

        // Validate partners
        const partnerEntries = document.querySelectorAll('.partner-entry');
        if (partnerEntries.length === 0) {
            window.showNotification('At least one partner is required', 'error', 'both');
            return;
        }

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

        // Validate total equity
        const totalEquity = this.calculateTotalEquity();
        if (Math.abs(totalEquity - 100) > 0.01) {
            window.showNotification(`Total equity must equal 100%. Current total: ${totalEquity.toFixed(2)}%`, 'error', 'both');
            return;
        }

        // Collect and send the property data...
        const propertyData = this.collectPropertyData(propertySelect.value, partners);
        
        console.log('Sending property data:', propertyData);

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
            console.log('Server response:', data);
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

    // Helper function to validate date format
    isValidDate: function(dateString) {
        if (!/^\d{4}-\d{2}-\d{2}$/.test(dateString)) return false;
        const date = new Date(dateString);
        return date instanceof Date && !isNaN(date) && date.toISOString().slice(0, 10) === dateString;
    },

    // Helper function to collect property data
    collectPropertyData: function(address) {
        const propertyData = {
            address: address,
            purchase_date: document.getElementById('purchase-date').value,
            loan_amount: parseFloat(document.getElementById('loan-amount').value),
            loan_start_date: document.getElementById('loan-start-date').value,
            purchase_price: parseInt(document.getElementById('purchase-price').value),
            down_payment: parseInt(document.getElementById('down-payment').value),
            primary_loan_rate: parseFloat(document.getElementById('primary-loan-rate').value),
            primary_loan_term: parseInt(document.getElementById('primary-loan-term').value),
            seller_financing_amount: parseInt(document.getElementById('seller-financing-amount').value || '0'),
            seller_financing_rate: parseFloat(document.getElementById('seller-financing-rate').value || '0'),
            seller_financing_term: parseInt(document.getElementById('seller-financing-term').value || '0'),
            closing_costs: parseInt(document.getElementById('closing-costs').value || '0'),
            renovation_costs: parseInt(document.getElementById('renovation-costs').value || '0'),
            marketing_costs: parseInt(document.getElementById('marketing-costs').value || '0'),
            holding_costs: parseInt(document.getElementById('holding-costs').value || '0'),
            monthly_income: {
                rental_income: parseFloat(document.getElementById('rental-income').value || '0'),
                parking_income: parseFloat(document.getElementById('parking-income').value || '0'),
                laundry_income: parseFloat(document.getElementById('laundry-income').value || '0'),
                other_income: parseFloat(document.getElementById('other-income').value || '0'),
                income_notes: document.getElementById('income-notes').value
            },
            monthly_expenses: {
                property_tax: parseFloat(document.getElementById('property-tax').value || '0'),
                insurance: parseFloat(document.getElementById('insurance').value || '0'),
                repairs: parseFloat(document.getElementById('repairs').value || '0'),
                capex: parseFloat(document.getElementById('capex').value || '0'),
                property_management: parseFloat(document.getElementById('property-management').value || '0'),
                hoa_fees: parseFloat(document.getElementById('hoa-fees').value || '0'),
                utilities: {
                    water: parseFloat(document.getElementById('water').value || '0'),
                    electricity: parseFloat(document.getElementById('electricity').value || '0'),
                    gas: parseFloat(document.getElementById('gas').value || '0'),
                    trash: parseFloat(document.getElementById('trash').value || '0')
                },
                other_expenses: parseFloat(document.getElementById('other-expenses').value || '0'),
                expense_notes: document.getElementById('expense-notes').value
            },
            partners: []
        };
    
        // Get all partner entries
        const partnerEntries = document.querySelectorAll('.partner-entry');
        partnerEntries.forEach((entry) => {
            const nameSelect = entry.querySelector('.partner-select');
            const equityInput = entry.querySelector('.partner-equity');
            const propertyManagerCheck = entry.querySelector('.property-manager-check');
            
            let name = nameSelect.value;
            if (name === 'new') {
                const newNameInput = entry.querySelector('.new-partner-name input');
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