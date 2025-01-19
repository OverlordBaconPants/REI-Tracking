
// add_transactions.js

const addTransactionsModule = {
    categories: {},
    currentUser: '',
    reimbursementSection: null,

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

    createReimbursementSection: function() {
        // Find the form first
        if (!this.form) {
            console.error('Form not found when creating reimbursement section');
            return;
        }

        // Try different possible parent containers
        let parentContainer = this.form.querySelector('.form-groups') || 
                            this.form.querySelector('.form-group').parentElement ||
                            this.form;

        console.log('Parent container found:', parentContainer);

        // Create the reimbursement section
        this.reimbursementSection = document.createElement('div');
        this.reimbursementSection.id = 'reimbursement-section';
        this.reimbursementSection.className = 'form-group mt-4';

        // Create the content
        const content = `
            <h4>Reimbursement Details</h4>
            <div class="reimbursement-fields">
                <div class="mb-3">
                    <label for="reimbursement_status" class="form-label">Status</label>
                    <select class="form-select" id="reimbursement_status" name="reimbursement_status">
                        <option value="pending">Pending</option>
                        <option value="completed">Completed</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label for="date_shared" class="form-label">Date Shared</label>
                    <input type="date" class="form-control" id="date_shared" name="date_shared">
                </div>
                <div class="mb-3">
                    <label for="share_description" class="form-label">Share Description</label>
                    <input type="text" class="form-control" id="share_description" name="share_description">
                </div>
                <div class="mb-3">
                    <label for="reimbursement_documentation" class="form-label">Documentation</label>
                    <input type="file" class="form-control" id="reimbursement_documentation" name="reimbursement_documentation">
                </div>
                <div id="reimbursement-details" class="alert alert-info mt-3"></div>
            </div>
        `;

        this.reimbursementSection.innerHTML = content;

        // Find the submit button or another reference point
        const submitButton = this.form.querySelector('button[type="submit"]');
        if (submitButton) {
            // Insert before the submit button's parent container
            submitButton.parentElement.parentElement.insertBefore(
                this.reimbursementSection,
                submitButton.parentElement
            );
            console.log('Reimbursement section created and inserted');
        } else {
            // Fallback to appending to the parent container
            parentContainer.appendChild(this.reimbursementSection);
            console.log('Reimbursement section created and appended');
        }

        // Initialize any needed event listeners
        const reimbursementStatus = document.getElementById('reimbursement_status');
        if (reimbursementStatus) {
            reimbursementStatus.addEventListener('change', (event) => {
                if (event.target.value === 'completed') {
                    const formData = new FormData(this.form);
                    this.validateReimbursementStatus(formData);
                }
            });
        }

        return this.reimbursementSection;
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
                
                try {
                    const selectedOption = event.target.options[event.target.selectedIndex];
                    const propertyData = JSON.parse(selectedOption.dataset.property);
                    
                    // First create/update collector payer options
                    this.updateCollectorPayerOptions();
                    
                    // Then toggle reimbursement section
                    this.toggleReimbursementSection(propertyData);
                    
                    // Finally update reimbursement details
                    this.updateReimbursementDetails();
                } catch (error) {
                    console.error('Error handling property change:', error);
                }
            });
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

        const propertySelect = document.getElementById('property_id');
        if (propertySelect) {
            propertySelect.addEventListener('change', (event) => {
                console.log('Property selection changed');
                const selectedOption = event.target.options[event.target.selectedIndex];
                try {
                    const propertyData = JSON.parse(selectedOption.dataset.property);
                    this.toggleReimbursementSection(propertyData);
                    this.updateCollectorPayerOptions();
                    this.updateReimbursementDetails();
                } catch (error) {
                    console.error('Error handling property change:', error);
                }
            });

            // Also trigger initial state if property is already selected
            if (propertySelect.value) {
                const selectedOption = propertySelect.options[propertySelect.selectedIndex];
                try {
                    const propertyData = JSON.parse(selectedOption.dataset.property);
                    this.toggleReimbursementSection(propertyData);
                } catch (error) {
                    console.error('Error handling initial property state:', error);
                }
            }
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
        
        // Find or create reimbursement section
        let reimbursementSection = document.getElementById('reimbursement-section');
        if (!reimbursementSection) {
            console.log('Reimbursement section not found, creating it');
            reimbursementSection = this.createReimbursementSection();
            if (!reimbursementSection) {
                console.error('Failed to create reimbursement section');
                return;
            }
        }
    
        let hasOnlyOwner = false;
        if (propertyData?.partners) {
            // Check if there's only one partner with 100% equity
            hasOnlyOwner = propertyData.partners.length === 1 && 
                          Math.abs(propertyData.partners[0].equity_share - 100) < 0.01;
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
            
            // Preserve existing doc info
            const existingReimbursementDoc = document.querySelector('[data-existing-reimbursement-doc]')?.dataset.existingReimbursementDoc;
            
            if (dateSharedInput && dateInput) {
                dateSharedInput.value = dateInput.value;
                console.log('Set date_shared to:', dateInput.value);
            }
            if (reimbursementStatusInput) {
                reimbursementStatusInput.value = 'completed';
                console.log('Set reimbursement_status to: completed');
            }
            if (shareDescriptionInput) {
                shareDescriptionInput.value = existingReimbursementDoc 
                    ? shareDescriptionInput.value 
                    : 'Auto-completed - Single owner property';
                console.log('Set share_description');
            }
    
            // Hide reimbursement details as well
            const reimbursementDetails = document.getElementById('reimbursement-details');
            if (reimbursementDetails) {
                reimbursementDetails.style.display = 'none';
            }
    
            // If there's a reimbursement alert, show it
            const reimbursementAlert = document.createElement('div');
            reimbursementAlert.className = 'alert alert-info mt-3';
            reimbursementAlert.textContent = 'Reimbursement details are hidden because this property is wholly owned by one partner.';
            reimbursementSection.appendChild(reimbursementAlert);
        } else {
            console.log('Multiple owners or no owner data - showing reimbursement section');
            reimbursementSection.style.display = 'block';
            
            // Remove any existing alerts
            const existingAlerts = reimbursementSection.querySelectorAll('.alert');
            existingAlerts.forEach(alert => alert.remove());
            
            // Reset fields for multiple owners
            const reimbursementStatusInput = document.getElementById('reimbursement_status');
            const shareDescriptionInput = document.getElementById('share_description');
            const dateSharedInput = document.getElementById('date_shared');
            
            if (reimbursementStatusInput) {
                reimbursementStatusInput.value = 'pending';
            }
            if (shareDescriptionInput) {
                shareDescriptionInput.value = '';
            }
            if (dateSharedInput) {
                dateSharedInput.value = '';
            }
    
            // Show reimbursement details
            const reimbursementDetails = document.getElementById('reimbursement-details');
            if (reimbursementDetails) {
                reimbursementDetails.style.display = 'block';
            }
        }
    
        return reimbursementSection;
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
        console.log('=== Starting Form Validation ===');
        let isValid = true;
        let validationErrors = [];

        // 1. Transaction Type Validation
        console.log('\nChecking Transaction Type:');
        const typeRadios = document.querySelectorAll('input[type="radio"][name="type"]');
        
        console.log(`Found ${typeRadios.length} radio buttons`);
        typeRadios.forEach(radio => {
            console.log({
                id: radio.id,
                value: radio.value,
                checked: radio.checked,
                disabled: radio.disabled,
                inForm: radio.form === this.form
            });
        });

        const selectedType = Array.from(typeRadios).find(radio => radio.checked);
        console.log('Selected type:', selectedType?.value);

        if (!selectedType) {
            validationErrors.push('Transaction type is required');
            isValid = false;
            
            // Visual feedback for type selection
            const typeGroup = document.querySelector('.btn-group');
            if (typeGroup) {
                typeGroup.classList.add('is-invalid');
                // Add red outline to buttons
                const labels = typeGroup.querySelectorAll('label');
                labels.forEach(label => {
                    if (label.classList.contains('btn-outline-success')) {
                        label.classList.remove('btn-outline-success');
                        label.classList.add('btn-outline-danger');
                    }
                });
            }
        }

        // 2. Property Validation
        console.log('\nChecking Property:');
        const propertySelect = document.getElementById('property_id');
        if (!propertySelect?.value) {
            validationErrors.push('Property is required');
            isValid = false;
            if (propertySelect) propertySelect.classList.add('is-invalid');
        }

        // 3. Required Fields Validation
        console.log('\nChecking Required Fields:');
        const requiredFields = {
            'category': 'Category',
            'description': 'Description',
            'amount': 'Amount',
            'date': 'Date',
            'collector_payer': 'Collector/Payer'
        };

        for (const [fieldId, fieldName] of Object.entries(requiredFields)) {
            const element = document.getElementById(fieldId);
            if (!element?.value) {
                validationErrors.push(`${fieldName} is required`);
                isValid = false;
                if (element) element.classList.add('is-invalid');
            }
        }

        // 4. Amount Validation
        console.log('\nChecking Amount:');
        const amountInput = document.getElementById('amount');
        if (amountInput?.value) {
            const amount = parseFloat(amountInput.value);
            if (isNaN(amount) || amount <= 0) {
                validationErrors.push('Amount must be a positive number');
                isValid = false;
                amountInput.classList.add('is-invalid');
            }
        }

        // 5. Notes Length Validation
        console.log('\nChecking Notes:');
        const notesField = document.getElementById('notes');
        if (notesField?.value.length > 150) {
            validationErrors.push('Notes must not exceed 150 characters');
            isValid = false;
            notesField.classList.add('is-invalid');
        }

        // Log validation results
        console.log('\n=== Validation Results ===');
        console.log('Valid:', isValid);
        if (!isValid) {
            console.log('Validation errors:', validationErrors);
            // Show first error to user
            this.showFlashMessage(validationErrors[0], 'error');
        }

        return isValid;
    },
    
    handleSubmit: function(event) {
        event.preventDefault();
        console.log('=== Form Submission Started ===');
        
        // Log the initial form data
        const formData = new FormData(this.form);
        console.log('Initial form data:');
        for (let [key, value] of formData.entries()) {
            console.log(`${key}: ${value}`);
        }

        // Log the state of the radio buttons specifically
        const typeRadios = document.querySelectorAll('input[type="radio"][name="type"]');
        console.log('\nRadio button states:');
        typeRadios.forEach(radio => {
            console.log({
                id: radio.id,
                value: radio.value,
                checked: radio.checked,
                defaultChecked: radio.defaultChecked,
                label: document.querySelector(`label[for="${radio.id}"]`)?.textContent.trim()
            });
        });

        if (!this.validateForm()) {
            console.error('Form validation failed - see details above');
            return;
        }

        // Log form data after validation
        console.log('\nForm data after validation:');
        const finalFormData = new FormData(this.form);
        for (let [key, value] of finalFormData.entries()) {
            console.log(`${key}: ${value}`);
        }

        // Disable submit button and proceed with submission
        const submitButton = this.form.querySelector('button[type="submit"]');
        if (submitButton) submitButton.disabled = true;

        fetch('/transactions/add', {
            method: 'POST',
            body: finalFormData
        })
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            window.showNotification('Transaction added successfully', 'success');
            setTimeout(() => {
                window.location.href = '/transactions/add';
            }, 1500);
        })
        .catch(error => {
            console.error('Submission error:', error);
            window.showNotification('Error adding transaction: ' + error.message, 'error');
        })
        .finally(() => {
            if (submitButton) submitButton.disabled = false;
        });
    }
}
export default addTransactionsModule
