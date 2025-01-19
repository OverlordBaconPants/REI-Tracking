const editTransactionsModule = {
    // Add reimbursementSection property
    form: null,
    elements: {},
    initialValues: {},
    documentRemovalModal: null,
    pendingDocumentRemoval: null,
    reimbursementSection: null,

    init: async function() {
        console.log('Form found, initializing components');
        this.form = document.getElementById('edit-transaction-form');
        this.reimbursementSection = document.getElementById('reimbursement-section');
        
        // Initialize Bootstrap modal first
        const modalElement = document.getElementById('documentRemovalModal');
        if (modalElement) {
            this.documentRemovalModal = new bootstrap.Modal(modalElement);
            console.log('Modal initialized successfully');
        } else {
            console.error('Modal element not found');
        }
        
        if (this.form) {
            console.log('Starting module initialization');
            await this.initializeModule();
            this.initDocumentRemovalHandlers();
            this.initNotesCounter();
        } else {
            console.error('Edit transaction form not found');
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

    initializeModule: async function() {
        // Get form elements
        this.elements = {
            form: this.form,
            property: document.getElementById('property_id'),
            category: document.getElementById('category'),
            collectorPayer: document.getElementById('collector_payer'),
            type: document.querySelector('input[name="type"]:checked'),
            collectorPayerLabel: document.querySelector('label[for="collector_payer"]'),
            typeRadios: document.querySelectorAll('input[name="type"]'),
            removeButtons: document.querySelectorAll('.document-remove-btn'),
            confirmDocumentRemoval: document.getElementById('confirmDocumentRemoval')
        };
    
        console.log('Found remove buttons:', this.elements.removeButtons);
    
        // Add click handlers for remove buttons
        this.elements.removeButtons.forEach(button => {
            console.log('Adding click handler to button:', button);
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const documentType = button.dataset.documentType;
                console.log('Remove button clicked for:', documentType);
                this.handleDocumentRemoval(documentType);
            });
        });

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

        // Add type change event listeners
        this.elements.typeRadios.forEach(radio => {
            radio.addEventListener('change', async (event) => {
                const selectedType = event.target.value;
                console.log('Type changed to:', selectedType);
                await this.populateCategories(selectedType);
                this.updateCollectorPayerLabel(selectedType);
                this.updateReimbursementDetails();
            });
        });

        // Populate initial data
        const initialType = this.initialValues.typeValue || 'expense';
        await this.populateCategories(initialType);
        this.updateCollectorPayerLabel(initialType);
        await this.updateCollectorPayerOptions();
        
        // Set initial collector/payer value if it exists
        if (this.initialValues.collectorPayerDataset) {
            this.elements.collectorPayer.value = this.initialValues.collectorPayerDataset;
        }
        
        this.updateReimbursementDetails();
        this.initEventListeners();
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

        // Add property change handler for reimbursement toggling
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
        if (!type) {
            type = document.querySelector('input[name="type"]:checked')?.value || 'expense';
        }
        
        console.log('Fetching categories for type:', type);
        try {
            const response = await fetch(`/api/categories?type=${type}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const categories = await response.json();
            const categorySelect = document.getElementById('category');
            
            if (categorySelect) {
                // Clear existing options
                categorySelect.innerHTML = '<option value="">Select a category</option>';
                
                // Add new options
                categories.forEach(category => {
                    const option = document.createElement('option');
                    option.value = category;
                    option.textContent = category;
                    categorySelect.appendChild(option);
                });
                
                // Restore initial value if exists and matches available options
                if (this.initialValues.categoryDataset) {
                    const matchingOption = Array.from(categorySelect.options)
                        .find(option => option.value === this.initialValues.categoryDataset);
                    if (matchingOption) {
                        categorySelect.value = this.initialValues.categoryDataset;
                    }
                }
            } else {
                console.error('Category select element not found');
            }
        } catch (error) {
            console.error('Error in populateCategories:', error);
            toastr.error('Error loading categories');
        }
    },

    updateCollectorPayerLabel: function(type) {
        if (!type) {
            type = document.querySelector('input[name="type"]:checked')?.value || 'expense';
        }
        
        console.log('Updating collector/payer label for type:', type);
        const label = document.querySelector('label[for="collector_payer"]');
        if (label) {
            label.textContent = type === 'income' ? 'Received by:' : 'Paid by:';
        } else {
            console.error('Collector/Payer label element not found');
        }
    },

    createReimbursementSection: function() {
        // Check if section already exists
        let section = document.getElementById('reimbursement-section');
        if (section) {
            console.log('Found existing reimbursement section');
            return section;
        }
    
        // In edit mode, we should always find an existing section
        if (document.getElementById('edit-transaction-form')) {
            console.warn('Reimbursement section not found in edit mode - this should not happen');
            return null;
        }
        
        // Create new section for add mode
        console.log('Creating new reimbursement section for add mode');
        section = document.createElement('div');
        section.id = 'reimbursement-section';
        section.className = 'mb-3';
    
        // Create the HTML structure for reimbursement section
        section.innerHTML = `
            <h4 class="mb-3">Reimbursement Details</h4>
            <div class="row g-3">
                <div class="col-12 col-md-6">
                    <label for="date_shared" class="form-label">Date Shared</label>
                    <input type="date" class="form-control" id="date_shared" name="date_shared">
                </div>
                <div class="col-12 col-md-6">
                    <label for="reimbursement_status" class="form-label">Status</label>
                    <select class="form-select" id="reimbursement_status" name="reimbursement_status">
                        <option value="pending">Pending</option>
                        <option value="completed">Completed</option>
                    </select>
                </div>
                <div class="col-12">
                    <label for="share_description" class="form-label">Share Description</label>
                    <textarea class="form-control" id="share_description" name="share_description" rows="2"></textarea>
                </div>
                <div class="col-12">
                    <label for="reimbursement_documentation" class="form-label">Documentation</label>
                    <input type="file" class="form-control" id="reimbursement_documentation" name="reimbursement_documentation">
                </div>
                <div class="col-12">
                    <div id="reimbursement-details" class="border rounded p-3 mt-2">
                        <!-- Reimbursement breakdown will be populated here -->
                    </div>
                </div>
            </div>
        `;
    
        // Find the appropriate place to insert the section (after the main transaction form fields)
        const formGroup = document.querySelector('.form-group') || document.querySelector('form > div');
        if (formGroup) {
            formGroup.parentNode.insertBefore(section, formGroup.nextSibling);
        } else {
            this.form.appendChild(section);
        }
    
        return section;
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
        console.log('Updating reimbursement details');
        const amount = parseFloat(document.getElementById('amount')?.value) || 0;
        const collectorPayerSelect = document.getElementById('collector_payer');
        const collectorPayer = collectorPayerSelect?.value;
        const propertyId = document.getElementById('property_id')?.value;
        const type = document.querySelector('input[name="type"]:checked')?.value;
        
        console.log('Current values:', {
            amount,
            collectorPayer,
            propertyId,
            type
        });
    
        if (!propertyId || !type || !amount) {
            console.log('Missing required fields for reimbursement calculation');
            return;
        }
    
        if (!collectorPayer) {
            console.log('No collector/payer selected');
            return;
        }
    
        try {
            const propertyData = JSON.parse(
                document.getElementById('property_id')
                    .options[document.getElementById('property_id').selectedIndex]
                    .dataset.property
            );
    
            const partners = propertyData.partners || [];
            const detailsContainer = document.getElementById('reimbursement-details');
            
            if (!detailsContainer || partners.length < 2) {
                console.log('No details container or insufficient partners');
                return;
            }
    
            // Filter out the collector/payer first
            const otherPartners = partners.filter(partner => {
                const isCollectorPayer = partner.name === collectorPayer;
                console.log(`Checking partner ${partner.name} against collector/payer ${collectorPayer}: ${isCollectorPayer}`);
                return !isCollectorPayer;
            });
    
            console.log('Partners after filtering:', otherPartners);
    
            let html = '<div class="reimbursement-breakdown mt-3">';
            
            if (otherPartners.length === 0) {
                html += '<p class="text-muted">No reimbursements needed - single partner transaction</p>';
            } else {
                html += '<ul class="list-unstyled">';
                otherPartners.forEach(partner => {
                    const equityShare = partner.equity_share / 100;
                    const share = equityShare * amount;
                    const shareText = type === 'income' ? 'is owed' : 'owes';
                    const amountClass = type === 'income' ? 'text-success' : 'text-danger';
                    
                    html += `
                        <li class="mb-2">
                            <strong>${partner.name}</strong> (${partner.equity_share}% equity) 
                            ${shareText} <span class="${amountClass}">$${share.toFixed(2)}</span>
                        </li>`;
                });
                html += '</ul>';
                html += `<p class="text-muted small mt-2">
                    Based on equity shares and a total ${type} of $${amount.toFixed(2)}
                </p>`;
            }
    
            html += '</div>';
            detailsContainer.innerHTML = html;
    
        } catch (error) {
            console.error('Error updating reimbursement details:', error);
            toastr.error('Error calculating reimbursement details');
        }
    },

    validateForm: function() {
        console.log('Starting form validation');
        let isValid = true;
        let firstInvalidField = null;

        // Validate required fields
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

        // Validate type selection
        const typeRadios = document.querySelectorAll('input[name="type"]');
        const typeSelected = Array.from(typeRadios).some(radio => radio.checked);
        if (!typeSelected) {
            isValid = false;
            toastr.error('Transaction type is required');
            typeRadios.forEach(radio => {
                radio.closest('.form-check').classList.add('is-invalid');
            });
        }

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

    initDocumentRemovalHandlers: function() {
        console.log('Initializing document removal handlers');
        
        // Clean up existing event listeners first
        const oldConfirmButton = document.getElementById('confirmDocumentRemoval');
        const newConfirmButton = oldConfirmButton.cloneNode(true);
        oldConfirmButton.parentNode.replaceChild(newConfirmButton, oldConfirmButton);
        
        // Add new click listener to confirm button
        newConfirmButton.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('Confirm button clicked');
            this.confirmDocumentRemoval();
        });
        console.log('Added click listener to confirm button');

        // Clean up and reinitialize remove buttons
        document.querySelectorAll('.document-remove-btn').forEach(button => {
            const newButton = button.cloneNode(true);
            button.parentNode.replaceChild(newButton, button);
            
            newButton.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const documentType = newButton.getAttribute('data-document-type');
                console.log('Remove button clicked for:', documentType);
                this.handleDocumentRemoval(documentType);
            });

            // Remove the inline onclick attribute
            newButton.removeAttribute('onclick');
        });
    },

    handleDocumentRemoval: function(documentType) {
        console.log(`handleDocumentRemoval called for ${documentType}`);
        
        // Validate document type
        if (!['transaction', 'reimbursement'].includes(documentType)) {
            console.error('Invalid document type:', documentType);
            return;
        }

        if (!this.documentRemovalModal) {
            console.error('Modal not initialized');
            // Try to initialize modal if it wasn't done earlier
            const modalElement = document.getElementById('documentRemovalModal');
            if (modalElement) {
                this.documentRemovalModal = new bootstrap.Modal(modalElement);
                console.log('Modal initialized on demand');
            } else {
                console.error('Modal element still not found');
                return;
            }
        }

        // Store the document type for later use
        this.pendingDocumentRemoval = documentType;
        
        // Update modal text to be more specific
        const modalBody = document.querySelector('#documentRemovalModal .modal-body');
        if (modalBody) {
            modalBody.textContent = `Are you sure you want to remove this ${documentType} document?`;
        }

        console.log('Showing modal');
        this.documentRemovalModal.show();
    },

    confirmDocumentRemoval: function() {
        console.log('confirmDocumentRemoval called');
        console.log('Pending document removal:', this.pendingDocumentRemoval);
        
        if (!this.pendingDocumentRemoval) {
            console.warn('No pending document removal');
            return;
        }
    
        const documentType = this.pendingDocumentRemoval;
        console.log('Processing removal for:', documentType);
        
        // Get the hidden input field
        let removeField = document.querySelector(`input[name="remove_${documentType}_documentation"]`);
        if (!removeField) {
            removeField = document.createElement('input');
            removeField.type = 'hidden';
            removeField.name = `remove_${documentType}_documentation`;
            removeField.id = `remove_${documentType}_documentation`;
            this.form.appendChild(removeField);
            console.log('Created missing remove field:', removeField);
        }
        console.log('Remove field found/created:', removeField);
        
        // Set the value and verify
        removeField.value = 'true';
        removeField.defaultValue = 'true'; // Set default value as well
        console.log(`Set remove_${documentType}_documentation to:`, removeField.value);
        
        // Log all hidden fields
        const allFields = {
            transaction: document.querySelector('input[name="remove_transaction_documentation"]')?.value,
            reimbursement: document.querySelector('input[name="remove_reimbursement_documentation"]')?.value
        };
        console.log('All remove field values:', allFields);

        // Find and hide the document container
        const documentContainer = document.querySelector(`.current-file:has(button[data-document-type="${documentType}"])`);
        if (documentContainer) {
            documentContainer.style.display = 'none';
            console.log('Hidden document container:', documentType);

            // Clear associated file input
            const fileInput = document.getElementById(documentType === 'transaction' ? 'documentation_file' : 'reimbursement_documentation');
            if (fileInput) {
                fileInput.value = '';
                console.log(`Cleared ${documentType} file input:`, fileInput.id);
            }
        } else {
            console.warn(`${documentType} document container not found`);
        }

        // Debug form state
        const formData = new FormData(this.form);
        console.log('Form field names:', [...formData.keys()]);
        console.log('Form field values:', Object.fromEntries(formData));
    
        // Update reimbursement status if needed
        if (documentType === 'reimbursement') {
            const statusSelect = document.getElementById('reimbursement_status');
            if (statusSelect && statusSelect.value === 'completed') {
                statusSelect.value = 'pending';
                console.log('Updated reimbursement status to pending');
            }
        }
    
        // Show success message
        toastr.success(`${documentType.charAt(0).toUpperCase() + documentType.slice(1)} document marked for removal`);
        
        // Hide modal and log final state
        this.documentRemovalModal.hide();
        console.log('Final form state:', {
            formFields: [...new FormData(this.form).keys()],
            removeFields: {
                transaction: document.querySelector('input[name="remove_transaction_documentation"]')?.value,
                reimbursement: document.querySelector('input[name="remove_reimbursement_documentation"]')?.value
            }
        });
        
        this.pendingDocumentRemoval = null;
        console.log('Document removal process completed for:', documentType);
    },

    validateReimbursementStatus: function(formData) {
        const reimbursementStatus = formData.get('reimbursement_status');
        const reimbursementDoc = formData.get('reimbursement_documentation');
        const existingDoc = document.querySelector('[data-existing-reimbursement-doc]')?.dataset.existingReimbursementDoc;
        const removeReimbDoc = formData.get('remove_reimbursement_documentation');
    
        // Only validate if status is 'completed' and document is being required
        if (reimbursementStatus === 'completed' && !removeReimbDoc) {
            if (!reimbursementDoc && !existingDoc) {
                toastr.error('Supporting reimbursement documentation required to mark this as Complete');
                return false;
            }
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
            timeOut: 1200,
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
    const initializeWhenReady = () => {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                // Ensure Bootstrap is loaded
                if (typeof bootstrap !== 'undefined') {
                    if (document.getElementById('edit-transaction-form')) {
                        editTransactionsModule.init();
                    }
                } else {
                    console.error('Bootstrap not loaded');
                }
            });
        } else {
            // Ensure Bootstrap is loaded
            if (typeof bootstrap !== 'undefined') {
                if (document.getElementById('edit-transaction-form')) {
                    editTransactionsModule.init();
                }
            } else {
                console.error('Bootstrap not loaded');
            }
        }
    };
    
    initializeWhenReady();
}

export default editTransactionsModule;