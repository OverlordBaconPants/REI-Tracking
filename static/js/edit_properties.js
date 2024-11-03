// edit_properties.js

const editPropertiesModule = {
    // Add this as a class property
    availablePartners: [],

    init: async function() {
        try {
            console.log('Initializing edit properties module');
            await this.fetchAvailablePartners();
            this.initializeForm();
            window.showNotification('Edit Properties module loaded', 'success');
        } catch (error) {
            console.error('Error initializing Edit Properties module:', error);
            window.showNotification('Error loading Edit Properties module: ' + error.message, 'error');
        }
    },

    initializeForm: function() {
        // Get all the elements we need
        const propertySelect = document.getElementById('property_select');
        const propertyDetails = document.getElementById('propertyDetails');
        const addPartnerButton = document.getElementById('add-partner-button');
        const partnersContainer = document.getElementById('partners-container');
        const form = document.getElementById('editPropertyForm');
        
        console.log('Form element found:', form !== null);

        // Add property select handler
        if (propertySelect) {
            propertySelect.addEventListener('change', (event) => this.handlePropertySelect(event));
            console.log('Property select initialized');
        }

        // Add form submit handler
        if (form) {
            form.addEventListener('submit', (event) => this.handleSubmit(event));
            // Also add click handler to the submit button as backup
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

        // Add partner button handler
        if (addPartnerButton) {
            addPartnerButton.addEventListener('click', () => this.addPartnerFields());
            console.log('Add partner button initialized');
        }

        // Initialize partners section if it exists
        if (partnersContainer) {
            this.initPartnersSection();
            console.log('Partners section initialized');
        }
    },

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
                    window.showNotification('Property details loaded successfully', 'success');
                } else {
                    throw new Error(data.message || 'Unknown error occurred');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                window.showNotification(error.message || 'Error loading property details', 'error');
                if (propertyDetails) {
                    propertyDetails.classList.add('hidden');
                }
                this.clearForm();
            });
    },

    populateForm: function(property) {
        try {
            // Helper function to safely set input values
            const setInputValue = (id, value) => {
                const element = document.getElementById(id);
                if (element) {
                    element.value = value ?? '';
                } else {
                    console.warn(`Element with id '${id}' not found`);
                }
            };

            // Set values for all fields
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

            // Handle partners
            const partnersContainer = document.getElementById('partners-container');
            if (partnersContainer) {
                partnersContainer.innerHTML = ''; // Clear existing partners
                if (property.partners && Array.isArray(property.partners)) {
                    property.partners.forEach(partner => this.addPartnerFields(partner));
                }
                this.updateTotalEquity();
            }

            console.log('Form populated successfully');
        } catch (error) {
            console.error('Error populating form:', error);
            window.showNotification('Error populating form fields', 'error');
            throw error; // Re-throw to be caught by the caller
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
    },

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
            window.showNotification('Error loading available partners', 'error');
            throw error;
        }
    },
    
    getPartnerOptions: function() {
        return this.availablePartners
            .map(partner => `<option value="${partner}">${partner}</option>`)
            .join('');
    },

    initPartnersSection: function() {
        const partnersContainer = document.getElementById('partners-container');
        const addPartnerButton = document.getElementById('add-partner-button');
        
        if (partnersContainer && addPartnerButton) {
            // Add partner button handler
            addPartnerButton.addEventListener('click', () => this.addPartnerFields());
            
            // Partner select change handler
            partnersContainer.addEventListener('change', (event) => {
                this.handlePartnerChange(event);
                this.updateTotalEquity();
            });
            
            // Partner equity input handler
            partnersContainer.addEventListener('input', (event) => {
                if (event.target.classList.contains('partner-equity')) {
                    this.updateTotalEquity();
                }
            });
            
            // Remove partner button handler
            partnersContainer.addEventListener('click', (event) => {
                if (event.target.classList.contains('remove-partner')) {
                    event.target.closest('.partner-entry').remove();
                    this.updateTotalEquity();
                }
            });

            console.log('Partners section initialized');
        } else {
            console.warn('Partners container or add partner button not found');
        }
    },

    addPartnerFields: function(partner = {}) {
        const partnersContainer = document.getElementById('partners-container');
        if (!partnersContainer) return;

        if (!this.availablePartners.length) {
            window.showNotification('Partner list not available', 'error');
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
                    <div class="col-md-2">
                        <button type="button" class="btn btn-danger remove-partner">Remove</button>
                    </div>
                </div>
            </div>
        `;
        partnersContainer.insertAdjacentHTML('beforeend', partnerHtml);
        
        // If we're adding an existing partner, set the select value
        if (partner.name) {
            const select = partnersContainer.querySelector(`#partner-select-${partnerCount}`);
            if (select) {
                select.value = partner.name;
            }
        }

        // Add change event listener for this new partner select
        const newSelect = partnersContainer.querySelector(`#partner-select-${partnerCount}`);
        if (newSelect) {
            newSelect.addEventListener('change', (event) => this.handlePartnerSelectChange(event));
        }
        
        this.updateTotalEquity();
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

    initPartnersSection: function() {
        const partnersContainer = document.getElementById('partners-container');
        if (partnersContainer) {
            partnersContainer.addEventListener('input', this.updateTotalEquity.bind(this));
            partnersContainer.addEventListener('click', this.removePartner.bind(this));
            console.log('Partners section initialized');
        } else {
            console.log('Partners container not found');
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

    collectPartnerData: function() {
        const partners = [];
        const partnerEntries = document.querySelectorAll('.partner-entry');

        partnerEntries.forEach(entry => {
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

            const equityShare = parseFloat(equityInput.value);

            if (partnerName && !isNaN(equityShare)) {
                partners.push({
                    name: partnerName,
                    equity_share: equityShare
                });
            }
        });

        return partners;
    },

    handleSubmit: function(event) {
        event.preventDefault();
        console.log('Form submission started');
        
        // Validate total equity
        const totalEquity = this.calculateTotalEquity();
        console.log('Total equity:', totalEquity);
        if (Math.abs(totalEquity - 100) > 0.01) {
            window.showNotification('Total equity must equal 100%', 'error');
            return;
        }

        // Get property select value
        const propertySelect = document.getElementById('property_select');
        if (!propertySelect || !propertySelect.value) {
            window.showNotification('No property selected', 'error');
            return;
        }

        // Collect the property data
        const propertyData = {
            address: propertySelect.value,
            purchase_date: document.getElementById('purchase-date').value,
            loan_amount: document.getElementById('loan-amount').value,
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
            partners: []
        };

        console.log('Collected property data:', propertyData);

        // Collect partner data
        const partnerEntries = document.querySelectorAll('.partner-entry');
        partnerEntries.forEach((entry, index) => {
            console.log(`Processing partner entry ${index}`);
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

            const equityShare = parseFloat(equityInput.value);

            if (partnerName && !isNaN(equityShare)) {
                propertyData.partners.push({
                    name: partnerName,
                    equity_share: equityShare
                });
                console.log(`Added partner: ${partnerName} with equity: ${equityShare}`);
            }
        });

        console.log('Final property data to submit:', propertyData);

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
            return response.json();
        })
        .then(data => {
            console.log('Server response:', data);
            if (data.success) {
                window.showNotification('Property updated successfully', 'success');
                setTimeout(() => window.location.reload(), 1500);
            } else {
                throw new Error(data.message || 'Error updating property');
            }
        })
        .catch(error => {
            console.error('Error updating property:', error);
            window.showNotification('Error updating property: ' + error.message, 'error');
        });
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