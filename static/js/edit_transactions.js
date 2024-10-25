const editTransactionsModule = {
    init: function() {
        console.log('Initializing edit transactions module');
        this.form = document.getElementById('edit-transaction-form');
        this.flashContainerTop = document.querySelector('.flash-messages-top');
        this.flashContainerBottom = document.querySelector('.flash-messages-bottom');

        if (this.form) {
            this.initEventListeners();
            this.populateCategories();
            this.updateCollectorPayerLabel();
            this.populatePartners();
            this.updateReimbursementDetails();
        } else {
            console.error('Edit Transaction form not found');
        }
    },

    initEventListeners: function() {
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
        document.getElementById('cancel-edit').addEventListener('click', this.handleCancel.bind(this));
        document.querySelectorAll('input[name="type"]').forEach(radio => {
            radio.addEventListener('change', this.handleTypeChange.bind(this));
        });
        document.getElementById('amount').addEventListener('input', this.updateReimbursementDetails.bind(this));
        document.getElementById('collector_payer').addEventListener('change', this.updateReimbursementDetails.bind(this));
        document.getElementById('property_id').addEventListener('change', this.populatePartners.bind(this));

        const reimbursementStatus = document.getElementById('reimbursement_status');
        if (reimbursementStatus) {
            reimbursementStatus.addEventListener('change', (event) => {
                if (event.target.value === 'completed') {
                    const formData = new FormData(this.form);
                    this.validateReimbursementStatus(formData);
                }
            });
        }
    },

    populateCategories: function() {
        const typeElement = document.querySelector('input[name="type"]:checked');
        if (!typeElement) {
            console.error('No transaction type selected');
            return;
        }
        const type = typeElement.value;
        
        fetch(`/transactions/api/categories?type=${type}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(categories => {
                const categorySelect = document.getElementById('category');
                if (!categorySelect) {
                    console.error('Category select element not found');
                    return;
                }
                categorySelect.innerHTML = '<option value="">Select a category</option>';
                categories.forEach(category => {
                    const option = document.createElement('option');
                    option.value = category;
                    option.textContent = category;
                    categorySelect.appendChild(option);
                });
                // Set the current category
                const currentCategory = this.form.querySelector('input[name="category"]');
                if (currentCategory && currentCategory.value) {
                    categorySelect.value = currentCategory.value;
                }
            })
            .catch(error => {
                console.error('Error fetching categories:', error);
                this.showFlashMessage('Error fetching categories. Please try again.', 'error');
            });
    },

    handleTypeChange: function(event) {
        this.populateCategories();
        this.updateCollectorPayerLabel();
        this.updateReimbursementDetails();
    },

    updateCollectorPayerLabel: function() {
        const type = document.querySelector('input[name="type"]:checked').value;
        const label = document.getElementById('collector_payer_label');
        label.textContent = type === 'income' ? 'Received by:' : 'Paid by:';
    },

    populatePartners: function() {
        const propertyIdElement = document.getElementById('property_id');
        if (!propertyIdElement) {
            console.error('Property ID element not found');
            return;
        }
        const propertyId = propertyIdElement.value;
        console.log('Populating partners for property:', propertyId);
        
        fetch(`/transactions/api/partners?property_id=${encodeURIComponent(propertyId)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(partners => {
                const collectorPayerSelect = document.getElementById('collector_payer');
                if (!collectorPayerSelect) {
                    console.error('Collector/Payer select element not found');
                    return;
                }
                collectorPayerSelect.innerHTML = '<option value="">Select a partner</option>';
                partners.forEach(partner => {
                    const option = document.createElement('option');
                    option.value = partner.name;
                    option.textContent = partner.name;
                    collectorPayerSelect.appendChild(option);
                });
                
                // Set the current collector/payer if it exists
                const currentCollectorPayer = this.form.querySelector('input[name="collector_payer"]');
                if (currentCollectorPayer && currentCollectorPayer.value) {
                    collectorPayerSelect.value = currentCollectorPayer.value;
                }
            })
            .catch(error => {
                console.error('Error fetching partners:', error);
                this.showFlashMessage('Error fetching partners. Please try again.', 'error');
            });
    },

    updateReimbursementDetails: function() {
        // Implement reimbursement details update logic here
        // This will be similar to the add_transactions.js implementation
    },

    validateForm: function() {
        // Add basic form validation
        const requiredFields = [
            'property_id',
            'type',
            'category',
            'description',
            'amount',
            'date',
            'collector_payer'
        ];

        let isValid = true;
        requiredFields.forEach(field => {
            const element = document.getElementById(field);
            if (!element || !element.value.trim()) {
                isValid = false;
                if (element) {
                    element.classList.add('is-invalid');
                }
            }
        });

        return isValid;
    },

    validateReimbursementStatus: function(formData) {
        const reimbursementStatus = formData.get('reimbursement_status');
        const reimbursementDoc = formData.get('reimbursement_documentation');
        const existingDoc = document.querySelector('[data-existing-reimbursement-doc]')?.dataset.existingReimbursementDoc;
    
        if (reimbursementStatus === 'completed' && !reimbursementDoc && !existingDoc) {
            this.showFlashMessage('Supporting reimbursement documentation required to mark this as Complete.', 'danger');
            return false;
        }
        return true;
    },

    handleSubmit: function(event) {
        event.preventDefault();
        console.log('Form submission started');
    
        if (!this.validateForm()) {
            console.log('Form validation failed');
            return;
        }
    
        const formData = new FormData(this.form);
        
        // Get filter options from URL
        const urlParams = new URLSearchParams(window.location.search);
        const filterOptionsStr = urlParams.get('filter_options') || '{}';
        
        let filterOptions = {};
        try {
            // Decode the URL-encoded string and parse it
            filterOptions = JSON.parse(decodeURIComponent(filterOptionsStr));
            console.log('Successfully parsed filter options:', filterOptions);
        } catch (e) {
            console.log('No valid filter options found, using empty object');
            filterOptions = {};
        }
    
        fetch(this.form.action, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Response data:', data);
            if (data.success) {
                // Show success message at both top and bottom
                this.showFlashMessage('Transaction updated successfully!', 'success', 'top');
                this.showFlashMessage('Transaction updated successfully!', 'success', 'bottom');
                
                // Pass the original filter options back
                setTimeout(() => {
                    window.parent.postMessage({
                        type: 'transactionUpdated',
                        shouldRefresh: true,
                        filterOptions: filterOptions
                    }, '*');
                }, 1000);
            } else {
                throw new Error(data.message || 'Unknown error occurred');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            this.showFlashMessage('Error updating transaction: ' + error.message, 'error');
        });
    },

    showFlashMessage: function(message, category, location = 'both') {
        const createAlertDiv = () => {
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${category} alert-dismissible fade show`;
            alertDiv.role = 'alert';
            alertDiv.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            return alertDiv;
        };
    
        if (location === 'top' || location === 'both') {
            if (this.flashContainerTop) {
                this.flashContainerTop.innerHTML = '';
                this.flashContainerTop.appendChild(createAlertDiv());
            }
        }
    
        if (location === 'bottom' || location === 'both') {
            if (this.flashContainerBottom) {
                this.flashContainerBottom.innerHTML = '';
                this.flashContainerBottom.appendChild(createAlertDiv());
            }
        }
    
        if (!this.flashContainerTop && !this.flashContainerBottom) {
            console.error('Flash containers not found');
        } else {
            console.log('Flash message displayed:', message);
        }
    },

    handleCancel: function() {
        this.sendFlashMessage('Transaction Edit Canceled', 'info');
        setTimeout(() => {
            window.parent.location.reload();
        }, 3000);
    },

    disableFormInputs: function() {
        const inputs = this.form.querySelectorAll('input, select, textarea, button');
        inputs.forEach(input => {
            input.disabled = true;
        });
    },

    sendFlashMessage: function(message, category) {
        window.parent.postMessage({
            type: 'flashMessage',
            message: message,
            category: category
        }, '*');
    }
};

export default editTransactionsModule;