
// add_transactions.js

const addTransactionsModule = {
    categories: {},
    currentUser: '',

    init: async function() {
        try {
            console.log('Initializing add transactions module');
            this.form = document.getElementById('add-transaction-form');
            if (this.form) {
                console.log('Add Transaction form found');
                await this.fetchCategories();
                this.initEventListeners();
                this.initNotesCounter();
                
                // Check if we're editing a transaction by looking for a hidden input
                const transactionType = document.querySelector('input[name="type"]:checked');
                if (transactionType) {
                    // If editing, use the selected type to populate categories
                    console.log('Initial transaction type:', transactionType.value);
                    this.updateCategories(transactionType.value);
                    this.updateCollectorPayerLabel(transactionType.value);
                } else {
                    // Default to income for new transactions
                    this.updateCategories('income');
                    this.updateCollectorPayerLabel('income');
                }
                
                window.showNotification('Add Transactions module loaded', 'success');
            } else {
                console.error('Add Transaction form not found');
                window.showNotification('Form not found', 'error');
            }
        } catch (error) {
            console.error('Error initializing Add Transactions module:', error);
            window.showNotification('Error loading Add Transactions module: ' + error.message, 'error');
        }
    },

    initNotesCounter: function() {
        const notesField = document.getElementById('notes');
        const notesCounter = document.getElementById('notesCounter');
        
        if (notesField && notesCounter) {
            // Initial count
            const updateCount = () => {
                const remaining = 150 - notesField.value.length;
                notesCounter.textContent = `${remaining} characters remaining`;
                
                // Update color based on remaining characters
                if (remaining < 20) {
                    notesCounter.classList.add('text-danger');
                } else {
                    notesCounter.classList.remove('text-danger');
                }
            };
            
            // Add event listeners
            notesField.addEventListener('input', updateCount);
            notesField.addEventListener('paste', (e) => {
                // Allow paste event to complete, then truncate if necessary
                setTimeout(() => {
                    if (notesField.value.length > 150) {
                        notesField.value = notesField.value.substring(0, 150);
                    }
                    updateCount();
                }, 0);
            });
            
            // Initial count
            updateCount();
        }
    },

    fetchCategories: async function() {
        console.log('Fetching categories');
        try {
            const response = await fetch('/api/categories');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            if (data.status === 'success' && data.data) {
                this.categories = data.data;
            } else {
                this.categories = data; // Fallback for direct categories response
            }
            console.log('Categories received:', this.categories);
        } catch (error) {
            console.error('Error fetching categories:', error);
            throw error;
        }
    },

    updateCategories: function(type) {
        console.log('Updating categories for type:', type);
        const categorySelect = document.getElementById('category');
        if (categorySelect) {
            // Store the current value before clearing
            const currentValue = categorySelect.value;
            
            // Clear existing options
            categorySelect.innerHTML = '<option value="">Select a category</option>';
            
            if (this.categories && this.categories[type]) {
                this.categories[type].forEach(category => {
                    const option = document.createElement('option');
                    option.value = category;
                    option.textContent = category;
                    // If this was the previously selected category, mark it as selected
                    if (category === currentValue) {
                        option.selected = true;
                    }
                    categorySelect.appendChild(option);
                });
                
                // If editing and we have a preselected category in a hidden input
                const preselectedCategory = document.querySelector('input[name="preselected_category"]');
                if (preselectedCategory && preselectedCategory.value) {
                    // Find and select the matching option
                    const matchingOption = Array.from(categorySelect.options)
                        .find(option => option.value === preselectedCategory.value);
                    if (matchingOption) {
                        matchingOption.selected = true;
                    }
                }
            } else {
                console.error('Categories not found for type:', type);
            }
        } else {
            console.error('Category select element not found');
        }
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

        if (elements.collectorPayerSelect) {
            elements.collectorPayerSelect.addEventListener('change', () => {
                console.log('Collector/Payer selection changed');
                this.updateReimbursementDetails();
            });
        } else {
            console.error('Collector/Payer select element not found');
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

        if (this.form) {
            this.form.addEventListener('submit', this.handleSubmit.bind(this));
            this.updateCollectorPayerOptions();
        } else {
            console.error('Form element not found');
        }

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

    hasPartners: function() {
        const propertySelect = document.getElementById('property_id');
        if (!propertySelect || propertySelect.selectedIndex <= 0) return false;

        try {
            const selectedProperty = propertySelect.options[propertySelect.selectedIndex];
            const propertyData = JSON.parse(selectedProperty.dataset.property);
            console.log('Parsed property data:', propertyData);
            
            // Add address truncation for display
            if (propertyData.address) {
                const parts = propertyData.address.split(',');
                propertyData.displayAddress = parts.length >= 2 
                    ? parts.slice(0, 2).join(',').trim() 
                    : parts[0];
            }
        } catch (error) {
            console.error('Error checking for partners:', error);
            return false;
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
        // Replace this with window.showNotification
        window.showNotification(message, category === 'danger' ? 'error' : category);
    },

    validateReimbursementStatus: function(formData) {
        const reimbursementStatus = formData.get('reimbursement_status');
        const reimbursementDoc = formData.get('reimbursement_documentation');
        const existingDoc = document.querySelector('[data-existing-reimbursement-doc]')?.dataset.existingReimbursementDoc;
        const removeReimbDoc = formData.get('remove_reimbursement_documentation');
    
        // Only validate if status is 'completed' and document is being required
        if (reimbursementStatus === 'completed' && !removeReimbDoc) {
            if (!reimbursementDoc && !existingDoc) {
                this.showFlashMessage('Supporting reimbursement documentation required to mark this as Complete.', 'danger');
                return false;
            }
        }
        return true;
    },

    validateForm: function() {
        const propertySelect = document.getElementById('property_id');
        
        if (!propertySelect || !propertySelect.value) {
            console.error('Property not selected. propertySelect:', propertySelect);
            this.showFlashMessage('Please select a property.', 'error');
            return false;
        }
    
        // Ensure required fields are present
        const requiredFields = {
            'type': 'Transaction type',
            'category': 'Category',
            'description': 'Description',
            'amount': 'Amount',
            'date': 'Date',
            'collector_payer': 'Collector/Payer'
        };

        // Validate notes field
        const notesField = document.getElementById('notes');
        if (notesField) {
            const notes = notesField.value.trim();
            if (notes.length > 150) {
                isValid = false;
                notesField.classList.add('is-invalid');
                toastr.error('Notes must be 150 characters or less');
                if (!firstInvalidField) {
                    firstInvalidField = notesField;
                }
            } else {
                notesField.classList.remove('is-invalid');
            }
        }
    
        for (const [fieldId, fieldName] of Object.entries(requiredFields)) {
            const element = document.getElementById(fieldId);
            if (!element || !element.value) {
                this.showFlashMessage(`Please enter a ${fieldName.toLowerCase()}.`, 'error');
                return false;
            }
        }
    
        // Validate amount is a positive number
        const amountInput = document.getElementById('amount');
        if (amountInput && (isNaN(amountInput.value) || parseFloat(amountInput.value) <= 0)) {
            this.showFlashMessage('Please enter a valid positive amount.', 'error');
            return false;
        }
    
        return true;
    },
    
    handleSubmit: function(event) {
        event.preventDefault();
        console.log('Form submission started');

        if (!this.validateForm()) {
            console.error('Form validation failed');
            return;
        }

        const formData = new FormData(this.form);
        if (!this.validateReimbursementStatus(formData)) {
            return;
        }

        // Disable the submit button to prevent multiple submissions
        const submitButton = event.target.querySelector('button[type="submit"]');
        submitButton.disabled = true;

        console.log('Sending form data');

        fetch('/transactions/add', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            window.showNotification('Transaction added successfully', 'success');
            setTimeout(() => {
                window.location.href = '/transactions/add';
            }, 1500);
        })
        .catch(error => {
            console.error('Error details:', error);
            window.showNotification('Error adding transaction: ' + error.message, 'error');
        })
        .finally(() => {
            // Re-enable the submit button
            submitButton.disabled = false;
        });
    }
}
export default addTransactionsModule
