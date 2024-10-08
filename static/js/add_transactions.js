// add_transactions.js

const addTransactionsModule = {
    categories: {},
    currentUser: '',

    init: function() {
        console.log('Initializing add transactions module');
        this.form = document.getElementById('add-transaction-form');
        if (this.form) {
            console.log('Add Transaction form found');
            this.fetchCategories().then(() => {
                this.initEventListeners();
                this.updateCategories('income'); // Default to income
                this.updateCollectorPayerLabel('income'); // Default to income
            });
        } else {
            console.error('Add Transaction form not found');
        }
    },

    fetchCategories: function() {
        console.log('Fetching categories');
        return fetch('/api/categories')
            .then(response => response.json())
            .then(data => {
                this.categories = data;
                console.log('Categories received:', this.categories);
            })
            .catch(error => console.error('Error fetching categories:', error));
    },

    initEventListeners: function() {
        console.log('Initializing event listeners');
        const elements = {
            typeRadios: document.querySelectorAll('input[name="type"]'),
            propertySelect: document.getElementById('property_id'),
            amountInput: document.getElementById('amount'),
            categorySelect: document.getElementById('category'),
            collectorPayerSelect: document.getElementById('collector_payer')
        };

        Object.entries(elements).forEach(([key, element]) => {
            if (element instanceof NodeList) {
                console.log(`${key}: ${element.length > 0 ? 'Found' : 'Not found'}`);
            } else {
                console.log(`${key}: ${element ? 'Found' : 'Not found'}`);
            }
        });

        if (elements.typeRadios.length > 0) {
            elements.typeRadios.forEach(radio => {
                radio.addEventListener('change', () => {
                    this.updateCategories(radio.value);
                    this.updateCollectorPayerLabel(radio.value);
                    this.updateReimbursementDetails();
                });
            });
        } else {
            console.error('Type radio buttons not found');
        }

        if (elements.propertySelect) {
            elements.propertySelect.addEventListener('change', (event) => {
                console.log('Property selection changed');
                console.log('Selected index:', event.target.selectedIndex);
                console.log('Selected value:', event.target.value);
                console.log('Selected option:', event.target.options[event.target.selectedIndex].text);
                this.updateCollectorPayerOptions();
                this.updateReimbursementDetails();
            });
        } else {
            console.error('Property select element not found');
        }

        if (elements.amountInput) {
            elements.amountInput.addEventListener('input', () => this.updateReimbursementDetails());
        } else {
            console.error('Amount input element not found');
        }

        if (this.form) {
            this.form.addEventListener('submit', this.handleSubmit.bind(this));
            this.updateCollectorPayerOptions();
        } else {
            console.error('Form element not found');
        }
    },

    updateCategories: function(type) {
        console.log('Updating categories for type:', type);
        const categorySelect = document.getElementById('category');
        if (categorySelect) {
            categorySelect.innerHTML = '<option value="">Select a category</option>';
            if (this.categories && this.categories[type]) {
                this.categories[type].forEach(category => {
                    const option = document.createElement('option');
                    option.value = category;
                    option.textContent = category;
                    categorySelect.appendChild(option);
                });
            } else {
                console.error('Categories not found for type:', type);
            }
        } else {
            console.error('Category select element not found');
        }
    },

    updateCollectorPayerLabel: function(type) {
        const label = document.querySelector('label[for="collector_payer"]');
        if (label) {
            label.textContent = type === 'income' ? 'Received by:' : 'Paid by:';
        } else {
            console.error('Collector/Payer label not found');
        }
    },

    updateCollectorPayerOptions: function() {
        console.log('Updating collector/payer options');
        const propertySelect = document.getElementById('property_id');
        const collectorPayerSelect = document.getElementById('collector_payer');
        
        if (!propertySelect || !collectorPayerSelect) {
            console.error('Property select or collector_payer select not found');
            return;
        }
    
        // Clear existing options
        collectorPayerSelect.innerHTML = '';
    
        const selectedProperty = propertySelect.options[propertySelect.selectedIndex];
        console.log('Selected property index:', propertySelect.selectedIndex);
        console.log('Selected property value:', propertySelect.value);
    
        if (propertySelect.selectedIndex <= 0 || !propertySelect.value) {
            console.log('No property selected');
            return;
        }
    
        console.log('Selected property text:', selectedProperty.text);
        console.log('Property dataset:', selectedProperty.dataset);
        
        try {
            // Log the raw data-property value
            console.log('Raw data-property value:', selectedProperty.dataset.property);
            
            // Attempt to parse the JSON
            const propertyData = JSON.parse(selectedProperty.dataset.property);
            console.log('Parsed property data:', propertyData);
            
            const partners = propertyData.partners || [];
            console.log('Parsed partners:', partners);
    
            if (partners.length === 0) {
                console.log('No partners found for selected property');
                collectorPayerSelect.innerHTML = '<option value="">No partners available</option>';
                return;
            }
    
            // Add partners as options
            partners.forEach(partner => {
                const option = document.createElement('option');
                option.value = partner.name;
                option.textContent = partner.name;
                collectorPayerSelect.appendChild(option);
                console.log('Added partner option:', partner.name);
            });
    
            console.log('Final collector/payer options:', collectorPayerSelect.innerHTML);
        } catch (error) {
            console.error('Error parsing property data:', error);
            console.log('Error details:', error.message);
            console.log('Raw property data:', selectedProperty.dataset.property);
            // Add a visible error message for the user
            collectorPayerSelect.innerHTML = '<option value="">Error loading partners</option>';
        }
    },

    updateReimbursementDetails: function() {
        console.log('Updating reimbursement details');
        const elements = {
            propertySelect: document.getElementById('property_id'),
            amountInput: document.getElementById('amount'),
            typeRadios: document.querySelectorAll('input[name="type"]'),
            reimbursementDetails: document.getElementById('reimbursement-details'),
            collectorPayerSelect: document.getElementById('collector_payer')
        };

        if (!elements.propertySelect || !elements.amountInput || elements.typeRadios.length === 0 || !elements.reimbursementDetails || !elements.collectorPayerSelect) {
            console.error('One or more required elements not found for updating reimbursement details');
            return;
        }

        const selectedProperty = elements.propertySelect.options[elements.propertySelect.selectedIndex];
        let partners = [];
        try {
            const propertyData = JSON.parse(selectedProperty.dataset.property || '{}');
            partners = propertyData.partners || [];
        } catch (error) {
            console.error('Error parsing partners data:', error);
        }

        const currentUser = elements.collectorPayerSelect.value;
        const amount = parseFloat(elements.amountInput.value) || 0;
        const transactionType = Array.from(elements.typeRadios).find(radio => radio.checked)?.value || 'income';

        console.log('Current user:', currentUser);
        console.log('Amount:', amount);
        console.log('Transaction type:', transactionType);
        console.log('Partners:', partners);

        let html = '<ul>';
        partners.forEach(partner => {
            if (partner.name !== currentUser) {
                const share = (partner.equity_share / 100) * amount;
                const shareText = transactionType === 'income' ? 'is owed' : 'owes';
                html += `<li><b>${partner.name} (${partner.equity_share}% equity) ${shareText} $${share.toFixed(2)}</b></li>`;
            }
        });
        html += '</ul>';

        console.log('Generated HTML:', html);
        elements.reimbursementDetails.innerHTML = html;
    },

    showFlashMessage: function(message, category) {
        const flashMessagesContainer = document.querySelector('.flash-messages');
        if (flashMessagesContainer) {
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${category} alert-dismissible fade show`;
            alertDiv.role = 'alert';

            // Apply specific styles based on the category
            if (category === 'success') {
                alertDiv.style.backgroundColor = '#d4edda';
                alertDiv.style.borderColor = '#c3e6cb';
                alertDiv.style.color = '#155724';
            } else if (category === 'danger' || category === 'error') {
                alertDiv.style.backgroundColor = '#f8d7da';
                alertDiv.style.borderColor = '#f5c6cb';
                alertDiv.style.color = '#721c24';
            }

            alertDiv.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            flashMessagesContainer.appendChild(alertDiv);         

            // Automatically remove the flash message after 5 seconds
            setTimeout(() => {
                alertDiv.remove();
            }, 5000);
        } else {
            console.error('Flash messages container not found');
        }
    },

    validateForm: function() {
        const propertySelect = document.getElementById('property_id');
        const documentationFile = document.getElementById('documentation_file');
    
        if (!propertySelect || !propertySelect.value) {
            console.error('Property not selected. propertySelect:', propertySelect);
            this.showFlashMessage('Please select a property.', 'error');
            return false;
        }
    
        if (!documentationFile || !documentationFile.files || documentationFile.files.length === 0) {
            console.error('No documentation file provided.');
            this.showFlashMessage('Please attach supporting documentation for the transaction.', 'error');
            return false;
        }
        // Add other validation checks here
        return true;
    },
    
    handleSubmit: function(event) {
        event.preventDefault();
        console.log('Form submission started');

        if (!this.validateForm()) {
            console.error('Form validation failed');
            return;
        }

        // Disable the submit button to prevent multiple submissions
        const submitButton = event.target.querySelector('button[type="submit"]');
        submitButton.disabled = true;

        const form = event.target;
        const formData = new FormData(form);

        console.log('Sending form data');

        fetch('/transactions/add', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            // Redirect to the same page to show the server-side flash message
            window.location.href = '/transactions/add';
        })
        .catch(error => {
            console.error('Error details:', error);
            this.showFlashMessage('An error occurred while adding the transaction: ' + error.message, 'error');
        })
        .finally(() => {
            // Re-enable the submit button
            submitButton.disabled = false;
        })
    }
}
export default addTransactionsModule