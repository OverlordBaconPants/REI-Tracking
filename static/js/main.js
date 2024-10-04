// main.js

// Immediately Invoked Function Expression (IIFE) to avoid polluting global scope
(function() {
    // Module for base functionality
    const baseModule = {
        init: function() {
            // Initialize accordion functionality
            const accordionButtons = document.querySelectorAll('.accordion-button');
            accordionButtons.forEach(button => {
                button.addEventListener('click', function() {
                    this.classList.toggle('collapsed');
                    const target = document.querySelector(this.getAttribute('data-bs-target'));
                    if (target) {
                        target.classList.toggle('show');
                    }
                });
            });
        }
    };

    // Module for add transactions page
    const addTransactionsModule = {
        categories: {
            income: ["Rent", "Loan Repayment", "Utility Reimbursement", "Escrow Refund", "Insurance Refund"],
            expense: ["Mortgage", "Utilities", "Repairs", "Capital Expenditures"]
        },
    
        init: function() {
            const form = document.getElementById('add-transaction-form');
            if (form) {
                this.initEventListeners();
                this.updateCategories('income'); // Default to income
                this.updateCollectorPayerLabel('income'); // Default to income
            }
        },
    
        initEventListeners: function() {
            const incomeRadio = document.getElementById('income-radio');
            const expenseRadio = document.getElementById('expense-radio');
            const propertySelect = document.getElementById('property-select');
            const amountInput = document.getElementById('amount');
    
            incomeRadio.addEventListener('change', () => {
                this.updateCategories('income');
                this.updateCollectorPayerLabel('income');
                this.updateReimbursementDetails();
            });
    
            expenseRadio.addEventListener('change', () => {
                this.updateCategories('expense');
                this.updateCollectorPayerLabel('expense');
                this.updateReimbursementDetails();
            });
    
            propertySelect.addEventListener('change', () => this.updateReimbursementDetails());
            amountInput.addEventListener('input', () => this.updateReimbursementDetails());
        },
    
        updateCategories: function(type) {
            const categorySelect = document.getElementById('category-select');
            categorySelect.innerHTML = '<option value="">Select a category</option>';
            this.categories[type].forEach(category => {
                const option = document.createElement('option');
                option.value = category;
                option.textContent = category;
                categorySelect.appendChild(option);
            });
        },
    
        updateCollectorPayerLabel: function(type) {
            const label = document.querySelector('label[for="collector_payer"]');
            label.textContent = type === 'income' ? 'Received by:' : 'Paid by:';
        },
    
        updateReimbursementDetails: function() {
            const propertySelect = document.getElementById('property-select');
            const amountInput = document.getElementById('amount');
            const incomeRadio = document.getElementById('income-radio');
            const reimbursementDetails = document.getElementById('reimbursement-details');
    
            const selectedProperty = propertySelect.options[propertySelect.selectedIndex];
            const partners = JSON.parse(selectedProperty.dataset.partners || '[]');
            const currentUser = document.body.dataset.currentUser;
            const amount = parseFloat(amountInput.value) || 0;
            const transactionType = incomeRadio.checked ? 'income' : 'expense';
    
            let html = '<ul>';
            partners.forEach(partner => {
                if (partner.name !== currentUser) {
                    const share = (partner.equity_share / 100) * amount;
                    const shareText = transactionType === 'income' ? 'is owed' : 'owes';
                    html += `<p><b>${partner.name} (${partner.equity_share}% equity) ${shareText} $${share.toFixed(2)}</b></p>`;
                }
            });
            html += '</ul>';
    
            reimbursementDetails.innerHTML = html;
        }
    };

    // Module for add properties page
    const addPropertiesModule = {
        init: function() {
            console.log('AddPropertiesModule initialized');
            const addPropertyForm = document.querySelector('#add-property-form');
            if (addPropertyForm) {
                console.log('Add Property form found');
                addPropertyForm.addEventListener('submit', this.handleSubmit.bind(this));
                this.initAddressAutocomplete();
                this.initPartnersSection();
            } else {
                console.log('Add Property form not found');
            }
        },
    
        handleSubmit: function(event) {
            event.preventDefault();
            console.log('Form submission started');
            
            // Get the form element
            const form = event.target;

            // Correctly initialize the FormData object
            const formData = new FormData(form);
            
            // Basic form validation
            if (!this.validateForm(form)) {
                console.log('Form validation failed');
                return;
            }

            // Log all form data
            for (let [key, value] of formData.entries()) {
                console.log(`Form data: ${key} = ${value}`);
            }
            
            // Collect form data
            const propertyData = {
                address: formData.get('property_address'),
                purchase_price: parseInt(formData.get('purchase_price')),
                down_payment: parseInt(formData.get('down_payment')),
                primary_loan_rate: parseFloat(formData.get('primary_loan_rate')),
                primary_loan_term: parseInt(formData.get('primary_loan_term')),
                purchase_date: formData.get('purchase_date'),
                loan_start_date: formData.get('loan_start_date'),
                seller_financing_amount: parseInt(formData.get('seller_financing_amount') || '0'),
                seller_financing_rate: parseFloat(formData.get('seller_financing_rate') || '0'),
                seller_financing_term: parseFloat(formData.get('seller_financing_term') || '0'),
                closing_costs: parseInt(formData.get('closing_costs') || '0'),
                renovation_costs: parseInt(formData.get('renovation_costs') || '0'),
                marketing_costs: parseInt(formData.get('marketing_costs') || '0'),
                holding_costs: parseInt(formData.get('holding_costs') || '0'),
                partners: []
            };

            console.log('Address from form data:', formData.get('address'));
            console.log('Address in propertyData:', propertyData.address);
            
            // Process partners data
            const partnerEntries = form.querySelectorAll('.partner-entry');
            console.log('Number of partner entries found:', partnerEntries.length);
            partnerEntries.forEach((entry, index) => {
                const nameInput = entry.querySelector(`[name="partners[${index}][name]"]`);
                const equityInput = entry.querySelector(`[name="partners[${index}][equity_share]"]`);
                
                if (nameInput && equityInput) {
                    let name = nameInput.value.trim();
                    const equityShare = parseFloat(equityInput.value);
                    
                    // If the partner is new, get the name from the new partner input
                    if (name === 'new') {
                        const newPartnerNameInput = entry.querySelector(`[name="partners[${index}][new_name]"]`);
                        if (newPartnerNameInput) {
                            name = newPartnerNameInput.value.trim();
                        }
                    }
                    
                    console.log(`Partner ${index + 1}:`, { name, equityShare });
                    
                    if (name && !isNaN(equityShare)) {
                        propertyData.partners.push({ name, equity_share: equityShare });
                    } else {
                        console.warn(`Invalid partner data for partner ${index + 1}`);
                    }
                } else {
                    console.warn(`Missing input fields for partner ${index + 1}`);
                }
            });
            
            console.log('Final partners data:', propertyData.partners);
            
            // Log the data being sent
            console.log('Sending property data:', JSON.stringify(propertyData, null, 2));
        
            // Send data to server
            fetch('/admin/add_properties', {
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
                    // Reload the page to display the flash message
                    window.location.reload();
                } else {
                    // Display the error message
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while adding the property. Please check the console for more details.');
            });
        },
    
        validateForm: function(form) {
            let isValid = true;
    
            // Validate property address
            if (!form.property_address.value.trim()) {
                alert('Please enter a property address.');
                isValid = false;
            }
    
            // Validate purchase price
            if (!form.purchase_price.value || isNaN(form.purchase_price.value)) {
                alert('Please enter a valid purchase price.');
                isValid = false;
            }
    
            // Validate down payment
            if (!form.down_payment.value || isNaN(form.down_payment.value)) {
                alert('Please enter a valid down payment amount.');
                isValid = false;
            }
    
            // Validate primary loan rate
            if (!form.primary_loan_rate.value || isNaN(form.primary_loan_rate.value)) {
                alert('Please enter a valid primary loan rate.');
                isValid = false;
            }
    
            // Validate primary loan term
            if (!form.primary_loan_term.value || isNaN(form.primary_loan_term.value)) {
                alert('Please enter a valid primary loan term.');
                isValid = false;
            }
    
            // Validate partners
            const partners = form.querySelectorAll('.partner-entry');
            let totalEquity = 0;
            partners.forEach((partner, index) => {
                const nameInput = partner.querySelector(`[name="partners[${index}][name]"]`);
                const equityInput = partner.querySelector(`[name="partners[${index}][equity_share]"]`);
                
                if (!nameInput.value.trim()) {
                    alert(`Please enter a name for partner ${index + 1}.`);
                    isValid = false;
                }
    
                if (!equityInput.value || isNaN(equityInput.value)) {
                    alert(`Please enter a valid equity share for partner ${index + 1}.`);
                    isValid = false;
                } else {
                    totalEquity += parseFloat(equityInput.value);
                }
            });
    
            if (Math.abs(totalEquity - 100) > 0.01) {
                alert(`Total equity must equal 100%. Current total: ${totalEquity.toFixed(2)}%`);
                isValid = false;
            }
    
            return isValid;
        },
        
        initAddressAutocomplete: function() {
            console.log('Initializing address autocomplete');
            const addressInput = document.getElementById('property_address');
            const resultsList = document.getElementById('autocomplete-results');
            let timeoutId;
    
            if (addressInput && resultsList) {
                console.log('Address input and results list found');
                addressInput.addEventListener('input', function() {
                    console.log('Input event triggered');
                    clearTimeout(timeoutId);
                    timeoutId = setTimeout(() => {
                        const query = this.value;
                        console.log('Query:', query);
                        if (query.length > 2) {
                            console.log('Making API call');
                            fetch(`/autocomplete?query=${encodeURIComponent(query)}`)
                                .then(response => response.json())
                                .then(data => {
                                    console.log('API response:', data);
                                    resultsList.innerHTML = '';
                                    data.forEach(result => {
                                        const li = document.createElement('li');
                                        li.textContent = result.formatted;
                                        li.classList.add('list-group-item');
                                        li.addEventListener('click', function() {
                                            addressInput.value = this.textContent;
                                            resultsList.innerHTML = '';
                                        });
                                        resultsList.appendChild(li);
                                    });
                                })
                                .catch(error => console.error('Error:', error));
                        } else {
                            resultsList.innerHTML = '';
                        }
                    }, 300);
                });

                // Close the autocomplete list when clicking outside
                document.addEventListener('click', function(e) {
                    if (e.target !== addressInput && e.target !== resultsList) {
                        resultsList.innerHTML = '';
                    }
                });
            }
            else {
                console.log('Address input or results list not found');
            }
        },

        initPartnersSection: function() {
            const partnersContainer = document.getElementById('partners-container');
            const addPartnerButton = document.getElementById('add-partner-button');
            
            if (partnersContainer && addPartnerButton) {
                addPartnerButton.addEventListener('click', this.addPartner.bind(this));
                partnersContainer.addEventListener('change', this.handlePartnerChange.bind(this));
                partnersContainer.addEventListener('input', this.updateTotalEquity.bind(this));
                partnersContainer.addEventListener('click', this.removePartner.bind(this));
                console.log('Partners section initialized');
            } else {
                console.log('Partners container or add partner button not found');
            }
        },
    
        addPartner: function() {
            const partnersContainer = document.getElementById('partners-container');
            const partnerCount = partnersContainer.querySelectorAll('.partner-entry').length;
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
            return Array.from(document.querySelector('.partner-select').options)
                .filter(option => option.value !== 'new')
                .map(option => `<option value="${option.value}">${option.textContent}</option>`)
                .join('');
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
            totalEquityElement.className = 'mt-3 font-weight-bold'; // Reset classes
            if (Math.abs(total - 100) < 0.01) {
                totalEquityElement.classList.add('text-success');
            } else {
                totalEquityElement.classList.add('text-danger');
            }
            totalEquityElement.style.fontSize = '1.2rem'; // Make text larger
        },
    };

    // Module for edit properties page
    // Function to initialize edit properties page
    function initEditPropertiesPage() {
        const propertySelect = document.getElementById('property_select');
        const form = document.getElementById('editPropertyForm');
        const propertyDetails = document.getElementById('propertyDetails');
        
        if (propertySelect) {
            propertySelect.addEventListener('change', function() {
                const selectedAddress = this.value;
                if (selectedAddress) {
                    fetchPropertyDetails(selectedAddress);
                } else {
                    clearForm();
                }
            });
        }

        function fetchPropertyDetails(address) {
            fetch(`/admin/get_property_details?address=${encodeURIComponent(address)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        populateForm(data.property);
                        propertyDetails.classList.remove('hidden');
                    } else {
                        alert('Error fetching property details');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred while fetching property details');
                });
        }

        function populateForm(property) {
            document.getElementById('purchase-date').value = property.purchase_date;
            document.getElementById('loan_start_date').value = property.loan_start_date;
            document.getElementById('purchase_price').value = property.purchase_price;
            document.getElementById('down_payment').value = property.down_payment;
            document.getElementById('primary_loan_rate').value = property.primary_loan_rate;
            document.getElementById('primary_loan_term').value = property.primary_loan_term;
            document.getElementById('seller_financing_amount').value = property.seller_financing_amount;
            document.getElementById('seller_financing_rate').value = property.seller_financing_rate;
            document.getElementById('seller_financing_term').value = property.seller_financing_term;
            document.getElementById('closing_costs').value = property.closing_costs;
            document.getElementById('renovation_costs').value = property.renovation_costs;
            document.getElementById('marketing_costs').value = property.marketing_costs;
            document.getElementById('holding_costs').value = property.holding_costs;

            // Handle partners
            const partnersContainer = document.getElementById('partners-container');
            partnersContainer.innerHTML = '<h4>Partners</h4>'; // Clear existing partners
            property.partners.forEach((partner, index) => {
                addPartnerFields(partner, index);
            });
            updateTotalEquity();
        }

        function clearForm() {
            if (form) form.reset();
            if (document.getElementById('partners-container')) {
                document.getElementById('partners-container').innerHTML = '<h4>Partners</h4>';
            }
            if (document.getElementById('total-equity')) {
                document.getElementById('total-equity').textContent = 'Total Equity: 0%';
            }
            if (propertyDetails) propertyDetails.classList.add('hidden');
        }

        function addPartnerFields(partner = {}, index) {
            const partnerDiv = document.createElement('div');
            partnerDiv.className = 'partner-entry';
            partnerDiv.innerHTML = `
                <div class="row">
                    <div class="col-md-5">
                        <div class="form-group mb-3">
                            <label for="partner-name-${index}">Partner:</label>
                            <input type="text" id="partner-name-${index}" name="partners[${index}][name]" class="form-control" value="${partner.name || ''}">
                        </div>
                    </div>
                    <div class="col-md-5">
                        <div class="form-group mb-3">
                            <label for="partner-equity-${index}">Equity Share (%):</label>
                            <input type="number" id="partner-equity-${index}" name="partners[${index}][equity_share]" class="form-control partner-equity" value="${partner.equity_share || ''}" step="0.01" min="0" max="100">
                        </div>
                    </div>
                    <div class="col-md-2">
                        <button type="button" class="btn btn-danger remove-partner">Remove</button>
                    </div>
                </div>
            `;
            document.getElementById('partners-container').appendChild(partnerDiv);
        }

        function updateTotalEquity() {
            const equityInputs = document.querySelectorAll('.partner-equity');
            let total = 0;
            equityInputs.forEach(input => {
                total += parseFloat(input.value) || 0;
            });
            document.getElementById('total-equity').textContent = `Total Equity: ${total.toFixed(2)}%`;
        }

        // Event listeners
        const addPartnerButton = document.getElementById('add-partner');
        if (addPartnerButton) {
            addPartnerButton.addEventListener('click', function() {
                const partnerCount = document.querySelectorAll('.partner-entry').length;
                addPartnerFields({}, partnerCount);
                updateTotalEquity();
            });
        }

        const partnersContainer = document.getElementById('partners-container');
        if (partnersContainer) {
            partnersContainer.addEventListener('click', function(e) {
                if (e.target.classList.contains('remove-partner')) {
                    e.target.closest('.partner-entry').remove();
                    updateTotalEquity();
                }
            });

            partnersContainer.addEventListener('input', function(e) {
                if (e.target.classList.contains('partner-equity')) {
                    updateTotalEquity();
                }
            });
        }
    }

    // Module to remove properties

    const removePropertiesModule = {
        init: function() {
            const form = document.querySelector('#remove-property-form');
            const propertySelect = document.querySelector('#property-select');
            const confirmInput = document.querySelector('#confirm-input');
            const removeButton = document.querySelector('#remove-button');
    
            if (form && propertySelect && confirmInput && removeButton) {
                form.addEventListener('submit', this.handleSubmit.bind(this));
                propertySelect.addEventListener('change', this.updateRemoveButton.bind(this));
                confirmInput.addEventListener('input', this.updateRemoveButton.bind(this));
            }
        },
    
        handleSubmit: function(event) {
            event.preventDefault();
            console.log('Form submission started');
            
            // Get the form element
            const form = event.target;
            
            // Basic form validation
            if (!this.validateForm(form)) {
                console.log('Form validation failed');
                return;
            }
            
            // Collect form data
            const formData = new FormData(form);
            
            // Log all form data
            for (let [key, value] of formData.entries()) {
                console.log(`${key}: ${value}`);
            }
            
            const propertyData = {
                address: formData.get('property_address'),
                purchase_price: parseInt(formData.get('purchase_price')),
                down_payment: parseInt(formData.get('down_payment')),
                primary_loan_rate: parseFloat(formData.get('primary_loan_rate')),
                primary_loan_term: parseInt(formData.get('primary_loan_term')),
                purchase_date: formData.get('purchase_date'),
                loan_start_date: formData.get('loan_start_date'),
                seller_financing_amount: parseInt(formData.get('seller_financing_amount') || '0'),
                seller_financing_rate: parseFloat(formData.get('seller_financing_rate') || '0'),
                seller_financing_term: parseFloat(formData.get('seller_financing_term') || '0'),
                closing_costs: parseInt(formData.get('closing_costs') || '0'),
                renovation_costs: parseInt(formData.get('renovation_costs') || '0'),
                marketing_costs: parseInt(formData.get('marketing_costs') || '0'),
                holding_costs: parseInt(formData.get('holding_costs') || '0'),
                partners: []
            };
            
            // Process partners data
            const partnerEntries = form.querySelectorAll('.partner-entry');
            partnerEntries.forEach((entry, index) => {
                const name = entry.querySelector(`[name="partners[${index}][name]"]`).value;
                const equityShare = parseFloat(entry.querySelector(`[name="partners[${index}][equity_share]"]`).value);
                propertyData.partners.push({ name, equity_share: equityShare });
            });
            
            // Log the final property data
            console.log('Sending property data:', JSON.stringify(propertyData, null, 2));
        
            // Check if address is present
            if (!propertyData.address) {
                console.error('Address is missing from the property data');
                alert('Please ensure you have selected a valid address from the autocomplete suggestions.');
                return;
            }
        
            // Send data to server
            fetch('/admin/add_properties', {
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
                    // Reload the page to display the flash message
                    window.location.reload();
                } else {
                    // Display the error message
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while adding the property. Please check the console for more details.');
            });
        },
    
        updateRemoveButton: function() {
            const propertySelect = document.querySelector('#property-select');
            const confirmInput = document.querySelector('#confirm-input');
            const removeButton = document.querySelector('#remove-button');
            
            removeButton.disabled = !(propertySelect.value && confirmInput.value === this.getConfirmPhrase());
        },
    
        getConfirmPhrase: function() {
            return "I am sure I want to do this.";
        }
    };

    // Function to initialize the appropriate functionality based on the current page
    function initPage() {
        const body = document.body;
        if (body.classList.contains('edit-properties-page')) {
            initEditPropertiesPage();
        }
        // Add other page initializations here as needed
    }

    // Call initPage when the DOM is fully loaded
    document.addEventListener('DOMContentLoaded', initPage);

    // Main init function
    function init() {
        console.log('Main init function called');
        console.log('Body classes:', document.body.className);
        baseModule.init();

        const body = document.body;
        if (body.classList.contains('add-transactions-page')) {
            addTransactionsModule.init();
        } else if (body.classList.contains('add-properties-page')) {
            console.log('Add properties page detected');
            addPropertiesModule.init();
        } else if (body.classList.contains('edit-properties-page')) {
            editPropertiesModule.init();
        } else if (body.classList.contains('remove-properties-page')) {
            removePropertiesModule.init()
        }
    }

    // Run the init function when the DOM is fully loaded
    document.addEventListener('DOMContentLoaded', init);
})();