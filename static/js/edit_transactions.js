const editTransactionsModule = {
    init: async function() {
        try {
            console.log('Initializing edit transactions module');
            this.form = document.getElementById('edit-transaction-form');
            this.isSubmitting = false;
            
            if (this.form) {
                console.log('Form found, initializing components');
                await this.initializeModule();
                this.initEventListeners();
            } else {
                console.error('Edit Transaction form not found');
                toastr.error('Error loading form');
            }
        } catch (error) {
            console.error('Error initializing Edit Transactions module:', error);
            toastr.error('Error loading Edit Transactions module: ' + error.message);
        }
    },

    initializeModule: async function() {
        try {
            console.log('Starting module initialization');
            
            // Debug initial elements
            const elements = {
                form: document.getElementById('edit-transaction-form'),
                property: document.getElementById('property_id'),
                category: document.getElementById('category'),
                collectorPayer: document.getElementById('collector_payer'),
                type: document.querySelector('input[name="type"]:checked')
            };
            
            console.log('Initial elements:', elements);
            
            // Debug initial values
            const initialValues = {
                propertyValue: elements.property?.value,
                categoryValue: elements.category?.value,
                categoryDataset: elements.category?.dataset.currentValue,
                collectorPayerValue: elements.collectorPayer?.value,
                collectorPayerDataset: elements.collectorPayer?.dataset.currentValue,
                typeValue: elements.type?.value
            };
            
            console.log('Initial values:', initialValues);
    
            await this.populateCategories();
            console.log('Categories populated');
            
            await this.populatePartners();
            console.log('Partners populated');
            
            this.updateReimbursementDetails();
            this.updateCollectorPayerLabel();
            
            console.log('Module initialization complete');
        } catch (error) {
            console.error('Initialization error:', error);
            throw error;
        }
    },

    initEventListeners: function() {
        console.log('Initializing event listeners');
        
         // Update form submission handler
         const form = document.querySelector('form');
         if (form) {
             form.addEventListener('submit', (event) => this.handleSubmit(event));
         }
        
        // Type change
        const typeRadios = document.querySelectorAll('input[name="type"]');
        typeRadios.forEach(radio => {
            radio.addEventListener('change', () => {
                this.populateCategories();
                this.updateCollectorPayerLabel();
                this.updateReimbursementDetails();
            });
        });

        // Amount change
        const amountInput = document.getElementById('amount');
        if (amountInput) {
            amountInput.addEventListener('input', () => this.updateReimbursementDetails());
        }

        // Property change
        const propertySelect = document.getElementById('property_id');
        if (propertySelect) {
            propertySelect.addEventListener('change', () => {
                this.populatePartners();
                this.updateReimbursementDetails();
            });
        }

        // Reimbursement status change
        const reimbursementStatus = document.getElementById('reimbursement_status');
        if (reimbursementStatus) {
            reimbursementStatus.addEventListener('change', (event) => {
                if (event.target.value === 'completed') {
                    this.validateReimbursementStatus(new FormData(this.form));
                }
            });
        }

        // Collector/Payer change
        const collectorPayerSelect = document.getElementById('collector_payer');
        if (collectorPayerSelect) {
            collectorPayerSelect.addEventListener('change', () => this.updateReimbursementDetails());
        }

        // Update cancel button handler
        const cancelBtn = document.querySelector('.btn-secondary');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', (event) => {
                event.preventDefault();
                this.handleCancel();
            });
        }
    },

    populateCategories: async function() {
        try {
            const typeElement = document.querySelector('input[name="type"]:checked');
            if (!typeElement) {
                console.log('No transaction type selected, skipping category population');
                return;
            }
    
            console.log('Fetching categories for type:', typeElement.value);
            const response = await fetch(`/transactions/api/categories?type=${typeElement.value}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
    
            const categories = await response.json();
            console.log('Received categories:', categories);
    
            const categorySelect = document.getElementById('category');
            if (!categorySelect) {
                throw new Error('Category select element not found');
            }
    
            // Store current value and dataset value
            const currentValue = categorySelect.value || categorySelect.dataset.currentValue;
            
            console.log('Category values:', {
                currentValue: currentValue,
                datasetValue: categorySelect.dataset.currentValue,
                selectValue: categorySelect.value
            });
    
            // Clear and rebuild select
            categorySelect.innerHTML = '';
            
            // Add placeholder option
            const placeholderOption = document.createElement('option');
            placeholderOption.value = '';
            placeholderOption.textContent = 'Select a category';
            categorySelect.appendChild(placeholderOption);
    
            // Add category options
            categories.forEach(category => {
                const option = document.createElement('option');
                option.value = category;
                option.textContent = category;
                if (currentValue && category === currentValue) {
                    option.selected = true;
                    console.log('Selected category:', category);
                }
                categorySelect.appendChild(option);
            });
    
            categorySelect.disabled = false;
            console.log('Category population complete. Final value:', categorySelect.value);
        } catch (error) {
            console.error('Error in populateCategories:', error);
            toastr.error('Error loading categories: ' + error.message);
        }
    },

    updateCollectorPayerLabel: function() {
        const type = document.querySelector('input[name="type"]:checked')?.value;
        const label = document.getElementById('collector_payer_label');
        if (label && type) {
            label.textContent = type === 'income' ? 'Received by:' : 'Paid by:';
        }
    },

    populatePartners: async function() {
        try {
            const propertySelect = document.getElementById('property_id');
            if (!propertySelect || !propertySelect.value) {
                console.log('No property selected, skipping partner population');
                return;
            }
    
            console.log('Fetching partners for property:', propertySelect.value);
            const response = await fetch(`/transactions/api/partners?property_id=${encodeURIComponent(propertySelect.value)}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
    
            const partners = await response.json();
            console.log('Received partners:', partners);
    
            const collectorPayerSelect = document.getElementById('collector_payer');
            if (!collectorPayerSelect) {
                throw new Error('Collector/Payer select element not found');
            }
    
            // Store current value and dataset value
            const currentValue = collectorPayerSelect.value || collectorPayerSelect.dataset.currentValue;
    
            console.log('Collector/Payer values:', {
                currentValue: currentValue,
                datasetValue: collectorPayerSelect.dataset.currentValue,
                selectValue: collectorPayerSelect.value
            });
    
            // Clear and rebuild select
            collectorPayerSelect.innerHTML = '';
            
            // Add placeholder option
            const placeholderOption = document.createElement('option');
            placeholderOption.value = '';
            placeholderOption.textContent = 'Select a partner';
            collectorPayerSelect.appendChild(placeholderOption);
    
            // Add partner options
            partners.forEach(partner => {
                const option = document.createElement('option');
                option.value = partner.name;
                option.textContent = partner.name;
                if (currentValue && partner.name === currentValue) {
                    option.selected = true;
                    console.log('Selected partner:', partner.name);
                }
                collectorPayerSelect.appendChild(option);
            });
    
            collectorPayerSelect.disabled = false;
            console.log('Partner population complete. Final value:', collectorPayerSelect.value);
        } catch (error) {
            console.error('Error in populatePartners:', error);
            toastr.error('Error loading partners: ' + error.message);
        }
    },

    updateReimbursementDetails: function() {
        const amount = parseFloat(document.getElementById('amount')?.value) || 0;
        const collectorPayer = document.getElementById('collector_payer')?.value;
        const propertyId = document.getElementById('property_id')?.value;
        const type = document.querySelector('input[name="type"]:checked')?.value;

        if (!propertyId || !type) {
            return;
        }

        fetch(`/transactions/api/partners?property_id=${encodeURIComponent(propertyId)}`)
            .then(response => response.json())
            .then(partners => {
                const detailsContainer = document.getElementById('reimbursement-details');
                if (!detailsContainer) return;

                let html = '<ul>';
                partners.forEach(partner => {
                    if (partner.name !== collectorPayer) {
                        const share = (partner.equity_share / 100) * amount;
                        const shareText = type === 'income' ? 'is owed' : 'owes';
                        html += `<li><b>${partner.name} (${partner.equity_share}% equity) ${shareText} $${share.toFixed(2)}</b></li>`;
                    }
                });
                html += '</ul>';
                detailsContainer.innerHTML = html;
            })
            .catch(error => {
                console.error('Error updating reimbursement details:', error);
                toastr.error('Error calculating reimbursement details');
            });
    },

    validateForm: function() {
        console.log('Starting form validation');
        let isValid = true;
        let firstInvalidField = null;

        // Validate radio button group for type
        const typeRadios = this.form.querySelectorAll('input[name="type"]');
        const typeSelected = Array.from(typeRadios).some(radio => radio.checked);
        
        if (!typeSelected) {
            isValid = false;
            toastr.error('Transaction type is required');
            if (!firstInvalidField) {
                firstInvalidField = typeRadios[0];
            }
            typeRadios.forEach(radio => {
                radio.closest('.form-check').classList.add('is-invalid');
            });
        }

        // Validate other required fields
        const requiredFields = [
            'property_id',
            'category',
            'description',
            'amount',
            'date',
            'collector_payer'
        ];

        requiredFields.forEach(field => {
            const element = document.getElementById(field);
            if (!element || !element.value.trim()) {
                isValid = false;
                if (element) {
                    element.classList.add('is-invalid');
                    if (!firstInvalidField) {
                        firstInvalidField = element;
                    }
                    let errorDiv = element.nextElementSibling;
                    if (!errorDiv || !errorDiv.classList.contains('invalid-feedback')) {
                        errorDiv = document.createElement('div');
                        errorDiv.className = 'invalid-feedback';
                        element.parentNode.insertBefore(errorDiv, element.nextSibling);
                    }
                    errorDiv.textContent = `${field.replace('_', ' ')} is required`;
                }
                toastr.error(`${field.replace('_', ' ')} is required`);
            } else {
                if (element) {
                    element.classList.remove('is-invalid');
                    const errorDiv = element.nextElementSibling;
                    if (errorDiv && errorDiv.classList.contains('invalid-feedback')) {
                        errorDiv.remove();
                    }
                }
            }
        });

        // Amount validation
        const amountElement = document.getElementById('amount');
        if (amountElement && amountElement.value.trim()) {
            const amount = parseFloat(amountElement.value);
            if (isNaN(amount) || amount <= 0) {
                isValid = false;
                amountElement.classList.add('is-invalid');
                if (!firstInvalidField) {
                    firstInvalidField = amountElement;
                }
                toastr.error('Amount must be a positive number');
            }
        }

        if (firstInvalidField) {
            firstInvalidField.focus();
        }

        return isValid;
    },

    validateReimbursementStatus: function(formData) {
        const reimbursementStatus = formData.get('reimbursement_status');
        const reimbursementDoc = formData.get('reimbursement_documentation');
        const existingDoc = document.querySelector('[data-existing-reimbursement-doc]')?.dataset.existingReimbursementDoc;

        if (reimbursementStatus === 'completed' && !reimbursementDoc && !existingDoc) {
            toastr.error('Supporting documentation required for completed reimbursement');
            return false;
        }
        return true;
    },

    handleSubmit: async function(event) {
        event.preventDefault();
        
        if (this.isSubmitting) return;
        this.isSubmitting = true;
    
        try {
            if (!this.validateForm()) {
                this.isSubmitting = false;
                return;
            }
    
            const formData = new FormData(this.form);
            
            const response = await fetch(this.form.action, {
                method: 'POST',
                body: formData
            });
    
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
    
            // Get the current filters from the form's data attribute
            const filters = document.querySelector('form').dataset.filters || '{}';
    
            toastr.success('Transaction Successfully Edited', '', {
                timeOut: 2000,
                onHidden: () => {
                    const timestamp = new Date().getTime();
                    window.location.href = `/transactions/view/?filters=${encodeURIComponent(filters)}&refresh=${timestamp}`;
                }
            });
    
        } catch (error) {
            console.error('Error in form submission:', error);
            toastr.error('Error updating transaction: ' + error.message);
            this.isSubmitting = false;
        }
    },

    restoreFilters: function(filters) {
        // Update filter store to trigger refresh with filters
        const filterStore = document.getElementById('filter-options');
        if (filterStore) {
            filterStore.value = JSON.stringify(filters);
            filterStore.dispatchEvent(new Event('change'));
        }

        // Update refresh trigger
        const refreshTrigger = document.getElementById('refresh-trigger');
        if (refreshTrigger) {
            refreshTrigger.value = Date.now();
            refreshTrigger.dispatchEvent(new Event('change'));
        }
    },

    handleCancel: function() {
        // Get the current filters from the page
        const filters = document.querySelector('form').dataset.filters || '{}';

        // Show cancellation notification
        toastr.info('Transaction Edit Canceled. Refreshing Transactions...', '', {
            timeOut: 3000,
            onHidden: () => {
                // Add a timestamp to force cache refresh and trigger Dash update
                const timestamp = new Date().getTime();
                window.location.href = `/transactions/view/?filters=${encodeURIComponent(filters)}&refresh=${timestamp}`;
            }
        });
    }
};

// Initialize toastr options
toastr.options = {
    closeButton: true,
    progressBar: true,
    newestOnTop: false,
    positionClass: "toast-top-right",
    preventDuplicates: true,
    onclick: null,
    showDuration: "300",
    hideDuration: "1000",
    timeOut: "5000",
    extendedTimeOut: "1000",
    showEasing: "swing",
    hideEasing: "linear",
    showMethod: "fadeIn",
    hideMethod: "fadeOut"
};

// Initialize the module when the DOM is loaded
if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => {
        if (document.getElementById('edit-transaction-form')) {
            editTransactionsModule.init();
        }
    });
}

export default editTransactionsModule;