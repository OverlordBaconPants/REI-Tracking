const editTransactionsModule = {
    form: null,
    elements: {},
    initialValues: {},

    init: async function() {
        console.log('Form found, initializing components');
        this.form = document.getElementById('edit-transaction-form');
        
        if (this.form) {
            console.log('Starting module initialization');
            await this.initializeModule();
        } else {
            console.error('Edit transaction form not found');
        }
    },

    initializeModule: async function() {
        // Get form elements
        this.elements = {
            form: this.form,
            property: document.getElementById('property_id'),
            category: document.getElementById('category'),
            collectorPayer: document.getElementById('collector_payer'),
            type: document.querySelector('input[name="type"]:checked'),
            collectorPayerLabel: document.querySelector('label[for="collector_payer"]')
        };

        console.log('Initial elements:', this.elements);

        // Store initial values
        this.initialValues = {
            propertyValue: this.elements.property?.value || '',
            categoryValue: this.elements.category?.value || '',
            categoryDataset: this.elements.category?.dataset?.initialValue || '',
            collectorPayerValue: this.elements.collectorPayer?.value || '',
            collectorPayerDataset: this.elements.collectorPayer?.dataset?.initialValue || '',
            typeValue: this.elements.type?.value || ''
        };

        console.log('Initial values:', this.initialValues);

        // Populate initial data
        const initialType = this.initialValues.typeValue || 'expense';
        await this.populateCategories(initialType);
        this.updateCollectorPayerLabel(initialType);
        console.log('Categories populated');

        this.updateCollectorPayerOptions();
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

    populateCategories: async function(type) {
        console.log('Fetching categories for type:', type);
        try {
            const response = await fetch(`/api/categories?type=${type}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const categories = await response.json();
            const categorySelect = this.elements.category;
            
            if (categorySelect) {
                // Clear existing options
                categorySelect.innerHTML = '<option value="">Select a category</option>';
                
                // Add new options
                if (Array.isArray(categories)) {
                    categories.forEach(category => {
                        const option = document.createElement('option');
                        option.value = category;
                        option.textContent = category;
                        
                        // Select the option if it matches the initial value
                        if (category === this.initialValues.categoryDataset) {
                            option.selected = true;
                        }
                        
                        categorySelect.appendChild(option);
                    });
                }
            }
        } catch (error) {
            console.error('Error in populateCategories:', error);
        }
    },

    updateCollectorPayerLabel: function(type) {
        console.log('Updating collector/payer label for type:', type);
        if (this.elements.collectorPayerLabel) {
            this.elements.collectorPayerLabel.textContent = type === 'income' ? 'Received by:' : 'Paid by:';
        } else {
            console.error('Collector/Payer label element not found');
        }
    },

    toggleReimbursementSection: function(propertyData) {
        console.log('Toggling reimbursement section with property data:', JSON.stringify(propertyData, null, 2));
        
        const reimbursementSection = document.getElementById('reimbursement-section');
        if (!reimbursementSection) {
            console.error('Reimbursement section not found');
            return;
        }
    
        let hasOnlyOwner = false;
        if (propertyData?.partners) {
            // Check if there's only one partner with 100% equity
            hasOnlyOwner = propertyData.partners.length === 1 && 
                           propertyData.partners[0].equity_share === 100;
            console.log('Property has only one owner:', hasOnlyOwner);
        }
    
        if (hasOnlyOwner) {
            console.log('Single owner property - hiding reimbursement section');
            reimbursementSection.style.display = 'none';
            
            // Set hidden input values for submission
            const dateInput = document.getElementById('date');
            const dateSharedInput = document.getElementById('date_shared');
            const reimbursementStatusInput = document.getElementById('reimbursement_status');
            const shareDescriptionInput = document.getElementById('share_description');
            
            if (dateSharedInput && dateInput) {
                dateSharedInput.value = dateInput.value;
                console.log('Set date_shared to:', dateInput.value);
            }
            if (reimbursementStatusInput) {
                reimbursementStatusInput.value = 'completed';
                console.log('Set reimbursement_status to: completed');
            }
            if (shareDescriptionInput) {
                shareDescriptionInput.value = 'Auto-completed - Single owner property';
                console.log('Set share_description');
            }
        } else {
            console.log('Multiple owners or no owner data - showing reimbursement section');
            reimbursementSection.style.display = '';
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
        if (propertySelect.selectedIndex <= 0 || !propertySelect.value) {
            console.log('No property selected');
            return;
        }
    
        try {
            const propertyData = JSON.parse(selectedProperty.dataset.property);
            console.log('Parsed property data:', propertyData);
            
            // Toggle reimbursement section first
            this.toggleReimbursementSection(propertyData);
            
            const partners = propertyData.partners || [];
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
        } catch (error) {
            console.error('Error parsing property data:', error);
            console.log('Error details:', error.message);
            collectorPayerSelect.innerHTML = '<option value="">Error loading partners</option>';
        }
    },

    populatePartners: async function(propertyId) {
        if (!propertyId) return;
        
        console.log('Fetching partners for property:', propertyId);
        
        try {
            const response = await fetch(`/api/partners?property_id=${encodeURIComponent(propertyId)}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const partners = await response.json();
            const partnerSelect = this.elements.collectorPayer;
            
            if (partnerSelect) {
                // Clear existing options
                partnerSelect.innerHTML = '<option value="">Select a partner</option>';
                
                // Add new options
                partners.forEach(partner => {
                    const option = document.createElement('option');
                    option.value = partner;
                    option.textContent = partner;
                    
                    // Select the option if it matches the initial value
                    if (partner === this.initialValues.collectorPayerDataset) {
                        option.selected = true;
                    }
                    
                    partnerSelect.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error in populatePartners:', error);
        }
    },

    setupEventListeners: function() {
        // Type radio buttons change event
        const typeRadios = document.querySelectorAll('input[name="type"]');
        typeRadios.forEach(radio => {
            radio.addEventListener('change', (event) => {
                this.populateCategories(event.target.value);
                this.updateCollectorPayerLabel(event.target.value);
            });
        });

        // Add date input change listener to update hidden date_shared
        const dateInput = document.getElementById('date');
        if (dateInput) {
            dateInput.addEventListener('change', (event) => {
                const dateSharedInput = document.getElementById('date_shared');
                if (dateSharedInput && !this.hasPartners()) {
                    dateSharedInput.value = event.target.value;
                }
            });
        }

        // Property select change event
        if (this.elements.property) {
            this.elements.property.addEventListener('change', (event) => {
                console.log('Property selection changed');
                this.updateCollectorPayerOptions();
            });
        }

        // Form submission handling
        if (this.form) {
            this.form.addEventListener('submit', this.handleSubmit.bind(this));
        }
    },

    hasPartners: function() {
        const propertySelect = document.getElementById('property_id');
        if (!propertySelect || propertySelect.selectedIndex <= 0) return false;

        try {
            const selectedProperty = propertySelect.options[propertySelect.selectedIndex];
            const propertyData = JSON.parse(selectedProperty.dataset.property);
            return (propertyData.partners || []).length > 1;
        } catch (error) {
            console.error('Error checking for partners:', error);
            return false;
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