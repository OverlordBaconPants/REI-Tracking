const removePropertiesModule = {
    init: async function() {
        try {
            console.log('RemovePropertiesModule initialized');
            
            // Get current user info
            this.currentUser = window.currentUser;
            if (!this.currentUser) {
                throw new Error('User information not available');
            }
            
            const form = document.querySelector('#remove-property-form');
            if (form) {
                await this.initializeForm(form);
            } else {
                console.error('Remove properties form not found');
                window.showNotification('Form not found', 'error', 'both');
            }
        } catch (error) {
            console.error('Error initializing Remove Properties module:', error);
            window.showNotification('Error loading Remove Properties module: ' + error.message, 'error', 'both');
        }
    },

    initializeForm: async function(form) {
        const propertySelect = form.querySelector('#property_select');
        const confirmInput = form.querySelector('#confirm_input');
        const submitButton = form.querySelector('button[type="submit"]');
        
        if (propertySelect && confirmInput && submitButton) {
            propertySelect.addEventListener('change', async () => {
                try {
                    confirmInput.disabled = true;
                    submitButton.disabled = true;
                    
                    if (!propertySelect.value) {
                        return;
                    }

                    const selectedOption = propertySelect.options[propertySelect.selectedIndex];
                    const propertyData = JSON.parse(selectedOption.dataset.property);

                    const isManager = propertyData.partners?.some(partner => 
                        partner.name === this.currentUser.name && 
                        partner.is_property_manager
                    );

                    if (!isManager) {
                        window.showNotification('You must be a property manager to remove this property', 'error', 'both');
                        propertySelect.value = '';
                        return;
                    }

                    confirmInput.disabled = false;
                    submitButton.disabled = false;

                } catch (error) {
                    console.error('Error in property select change:', error);
                    window.showNotification(error.message, 'error', 'both');
                    propertySelect.value = '';
                }
            });

            form.addEventListener('submit', (event) => this.handleSubmit(event, propertySelect, confirmInput));
            await this.loadProperties(propertySelect);
        }
    },

    loadProperties: async function(propertySelect) {
        try {
            const response = await fetch('/properties/get_manageable_properties');
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.message || 'Failed to load properties');
            }

            // Clear existing options except first
            while (propertySelect.options.length > 1) {
                propertySelect.remove(1);
            }

            // Add only properties where user is manager
            data.properties.forEach(property => {
                if (property.partners?.some(p => 
                    p.name === this.currentUser.name && 
                    p.is_property_manager
                )) {
                    const option = new Option(property.address, property.address);
                    option.dataset.property = JSON.stringify(property);
                    propertySelect.add(option);
                }
            });

            if (propertySelect.options.length === 1) {
                window.showNotification('No properties available for removal', 'info', 'both');
            }

        } catch (error) {
            console.error('Error loading properties:', error);
            window.showNotification('Error loading properties: ' + error.message, 'error', 'both');
        }
    },

    checkPropertyManagerAccess: async function(propertyAddress) {
        try {
            const response = await fetch('/properties/get_property_details?address=' + encodeURIComponent(propertyAddress));
            const data = await response.json();
            
            if (!data.success || !data.property.is_property_manager) {
                window.location.href = '/403';
                throw new Error('Property manager access required');
            }
        } catch (error) {
            console.error('Error checking property manager access:', error);
            throw new Error('Error checking access: ' + error.message);
        }
    },

    handleSubmit: function(event, propertySelect, confirmInput) {
        event.preventDefault();
        
        // Log values for debugging
        console.log('Selected property:', propertySelect.value);
        console.log('Confirmation input:', confirmInput.value);
        
        // Validate selection
        if (!propertySelect.value) {
            window.showNotification('Please select a property to remove', 'error', 'both');
            return;
        }

        // Validate confirmation phrase
        const expectedPhrase = "I am sure I want to do this.";
        if (confirmInput.value !== expectedPhrase) {
            window.showNotification(`Please type exactly: "${expectedPhrase}"`, 'error', 'both');
            return;
        }

        // Show loading modal
        const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
        loadingModal.show();

        // Create FormData object and properly append data
        const formData = new FormData();
        formData.append('property_select', propertySelect.value);
        formData.append('confirm_input', confirmInput.value);

        // Disable form elements during submission
        propertySelect.disabled = true;
        confirmInput.disabled = true;

        fetch('/properties/remove_properties', {
            method: 'POST',
            body: formData
        })
        .then(async response => {
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.message || 'Server error occurred');
            }
            return data;
        })
        .then(data => {
            window.showNotification('Property successfully removed', 'success', 'both');
            // Wait 2 seconds before reloading
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        })
        .catch(error => {
            console.error('Error:', error);
            window.showNotification(error.message || 'An unexpected error occurred', 'error', 'both');
        })
        .finally(() => {
            loadingModal.hide();
            propertySelect.disabled = false;
            confirmInput.disabled = true;
        });
    }
};

export default removePropertiesModule;