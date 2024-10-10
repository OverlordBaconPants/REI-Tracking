// add_properties.js

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
                        fetch(`/api/autocomplete?query=${encodeURIComponent(query)}`)
                            .then(response => {
                                console.log('Response status:', response.status);
                                if (!response.ok) {
                                    return response.text().then(text => {
                                        throw new Error(`HTTP error! status: ${response.status}, message: ${text}`);
                                    });
                                }
                                return response.json();
                            })
                            .then(data => {
                                console.log('API response:', data);
                                resultsList.innerHTML = '';
                                if (Array.isArray(data) && data.length > 0) {
                                    data.forEach(result => {
                                        const li = document.createElement('li');
                                        li.textContent = result.formatted;
                                        li.addEventListener('click', function() {
                                            addressInput.value = this.textContent;
                                            resultsList.innerHTML = '';
                                        });
                                        resultsList.appendChild(li);
                                    });
                                } else {
                                    resultsList.innerHTML = '<li>No results found</li>';
                                }
                            })
                            .catch(error => {
                                console.error('Error:', error);
                                resultsList.innerHTML = `<li>Error fetching results: ${error.message}</li>`;
                            });
                    } else {
                        resultsList.innerHTML = '';
                    }
                }, 300);
            });

            document.addEventListener('click', function(e) {
                if (e.target !== addressInput && e.target !== resultsList) {
                    resultsList.innerHTML = '';
                }
            });
        }
        else {
            console.error('Address input or results list not found');
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

        const propertyData = {
            address: formData.get('property_address'),
            purchase_price: parseInt(formData.get('purchase_price')),
            down_payment: parseInt(formData.get('down_payment')),
            primary_loan_rate: parseFloat(formData.get('primary_loan_rate')),
            primary_loan_term: parseInt(formData.get('primary_loan_term')),
            purchase_date: formData.get('purchase_date'),
            loan_amount: formData.get('loan_amount'),
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

        if (!form.property_address.value.trim()) {
            alert('Please enter a property address.');
            isValid = false;
        }

        if (!form.purchase_price.value || isNaN(form.purchase_price.value)) {
            alert('Please enter a valid purchase price.');
            isValid = false;
        }

        if (!form.down_payment.value || isNaN(form.down_payment.value)) {
            alert('Please enter a valid down payment amount.');
            isValid = false;
        }

        if (!form.primary_loan_rate.value || isNaN(form.primary_loan_rate.value)) {
            alert('Please enter a valid primary loan rate.');
            isValid = false;
        }

        if (!form.primary_loan_term.value || isNaN(form.primary_loan_term.value)) {
            alert('Please enter a valid primary loan term.');
            isValid = false;
        }

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
};

export default addPropertiesModule;