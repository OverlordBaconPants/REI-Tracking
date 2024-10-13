// edit_properties.js

const editPropertiesModule = {
    allPartners: new Set(), // Use a Set to store unique partner names

    init: function() {
        console.log('Initializing edit properties module');
        const propertySelect = document.getElementById('property_select');
        const form = document.getElementById('editPropertyForm');
        const propertyDetails = document.getElementById('propertyDetails');
        const addPartnerButton = document.getElementById('add-partner-button');
        
        if (propertySelect) {
            propertySelect.addEventListener('change', this.handlePropertySelect.bind(this));
            // Fetch partners for the initially selected property
            if (propertySelect.value) {
                this.fetchPartnersForProperty(propertySelect.value);
            }
        }

        if (form) {
            form.addEventListener('submit', this.handleSubmit.bind(this));
        }

        if (addPartnerButton) {
            addPartnerButton.addEventListener('click', () => this.addPartner());
        }

        this.initPartnersSection();
        this.checkFlashMessages();
    },

    checkFlashMessages: function() {
        const flashMessages = document.querySelectorAll('.flash-message');
        flashMessages.forEach(message => {
            alert(message.textContent);
            message.remove();
        });
    },

    handlePropertySelect: function(event) {
        const selectedAddress = event.target.value;
        if (selectedAddress) {
            this.fetchPropertyDetails(selectedAddress);
            this.fetchPartnersForProperty(selectedAddress);
        } else {
            this.clearForm();
        }
    },

    fetchPropertyDetails: function(address) {
        fetch(`/properties/get_property_details?address=${encodeURIComponent(address)}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                this.populateForm(data.property);
                document.getElementById('propertyDetails').classList.remove('hidden');
            } else {
                alert('Error fetching property details: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while fetching property details. Please check the console for more details.');
        });
    },

    fetchPartnersForProperty: function(propertyId) {
        return fetch(`/properties/get_partners_for_property?property_id=${encodeURIComponent(propertyId)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                this.allPartners.clear(); // Clear existing partners
                data.forEach(partner => this.allPartners.add(partner.name));
                this.updatePartnerSelects();
            })
            .catch(error => {
                console.error('Error fetching partners:', error);
                alert(`An error occurred while fetching partners: ${error.message}`);
            });
    },

    populateForm: function(property) {
        document.getElementById('purchase-date').value = property.purchase_date;
        document.getElementById('loan_amount').value = property.loan_amount;
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

        const partnersContainer = document.getElementById('partners-container');
        partnersContainer.innerHTML = '<h4>Partners</h4>';
        if (property.partners && Array.isArray(property.partners)) {
            property.partners.forEach((partner) => {
                this.addPartner(partner);
            });
        }
        this.updateTotalEquity();
    },

    clearForm: function() {
        const form = document.getElementById('editPropertyForm');
        if (form) form.reset();
        if (document.getElementById('partners-container')) {
            document.getElementById('partners-container').innerHTML = '<h4>Partners</h4>';
        }
        if (document.getElementById('total-equity')) {
            document.getElementById('total-equity').textContent = 'Total Equity: 0%';
        }
        if (document.getElementById('propertyDetails')) {
            document.getElementById('propertyDetails').classList.add('hidden');
        }
    },

    initPartnersSection: function() {
        const partnersContainer = document.getElementById('partners-container');
        if (partnersContainer) {
            partnersContainer.addEventListener('change', this.handlePartnerChange.bind(this));
            partnersContainer.addEventListener('input', this.updateTotalEquity.bind(this));
            partnersContainer.addEventListener('click', (event) => {
                if (event.target.classList.contains('remove-partner')) {
                    this.removePartner(event);
                }
            });
            console.log('Partners section initialized');
        } else {
            console.log('Partners container not found');
        }
    },

    addPartner: function(partner = {}) {
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
                                ${this.getPartnerOptions(partner.name)}
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
                            <input type="number" id="partner-equity-${partnerCount}" name="partners[${partnerCount}][equity_share]" class="form-control partner-equity" step="0.01" min="0" max="100" value="${partner.equity_share || ''}">
                        </div>
                    </div>
                    <div class="col-md-2">
                        <button type="button" class="btn btn-danger remove-partner">Remove</button>
                    </div>
                </div>
            </div>
        `;
        partnersContainer.insertAdjacentHTML('beforeend', newPartnerHtml);
        
        if (partner.name) {
            const partnerSelect = partnersContainer.querySelector(`#partner-select-${partnerCount}`);
            if (partnerSelect) {
                partnerSelect.value = partner.name;
            }
        }
        
        this.updateTotalEquity();
    },

    getPartnerOptions: function(selectedPartner = '') {
        const currentPartners = Array.from(document.querySelectorAll('.partner-select'))
            .map(select => select.value)
            .filter(value => value && value !== 'new');

        return Array.from(this.allPartners)
            .filter(partner => !currentPartners.includes(partner) || partner === selectedPartner)
            .map(partner => `<option value="${partner}" ${partner === selectedPartner ? 'selected' : ''}>${partner}</option>`)
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
        event.target.closest('.partner-entry').remove();
        this.updateTotalEquity();
        this.updatePartnerSelects();
    },

    updatePartnerSelects: function() {
        const partnerSelects = document.querySelectorAll('.partner-select');
        partnerSelects.forEach(select => {
            const currentValue = select.value;
            select.innerHTML = `
                <option value="">Select a partner</option>
                ${this.getPartnerOptions(currentValue)}
                <option value="new">Add new partner</option>
            `;
            select.value = currentValue;
        });
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

        const propertyData = {
            address: formData.get('property_select'),
            purchase_date: formData.get('purchase-date'),
            loan_amount: formData.get('loan_amount'),
            loan_start_date: formData.get('loan_start_date'),
            purchase_price: parseInt(formData.get('purchase_price')),
            down_payment: parseInt(formData.get('down_payment')),
            primary_loan_rate: parseFloat(formData.get('primary_loan_rate')),
            primary_loan_term: parseInt(formData.get('primary_loan_term')),
            seller_financing_amount: parseInt(formData.get('seller_financing_amount') || '0'),
            seller_financing_rate: parseFloat(formData.get('seller_financing_rate') || '0'),
            seller_financing_term: parseInt(formData.get('seller_financing_term') || '0'),
            closing_costs: parseInt(formData.get('closing_costs') || '0'),
            renovation_costs: parseInt(formData.get('renovation_costs') || '0'),
            marketing_costs: parseInt(formData.get('marketing_costs') || '0'),
            holding_costs: parseInt(formData.get('holding_costs') || '0'),
            partners: []
        };

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

        fetch('/properties/edit_properties', {
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
                alert('Property updated successfully!');
                window.location.reload();
            } else {
                alert('Error: ' + (data.message || 'Failed to update property'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while updating the property. Please check the console and server logs for more details.');
        });
    }
};

export default editPropertiesModule;