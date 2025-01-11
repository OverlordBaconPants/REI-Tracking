const removePropertiesModule = {
    init: async function() {
        try {
            console.log('RemovePropertiesModule initialized');
            const form = document.querySelector('.remove-properties-container form');
            if (form) {
                await this.checkPropertyManagerAccess();
                this.initializeForm(form);
                window.showNotification('Remove Properties module loaded', 'success', 'both');
            } else {
                console.error('Remove properties form not found');
                window.showNotification('Form not found', 'error', 'both');
            }
        } catch (error) {
            console.error('Error initializing Remove Properties module:', error);
            window.showNotification('Error loading Remove Properties module: ' + error.message, 'error', 'both');
        }
    },

    checkPropertyManagerAccess: async function() {
        const response = await fetch('/properties/get_property_details?address=' + encodeURIComponent(propertySelect.value));
        const data = await response.json();
        
        if (!data.success || !data.property.is_property_manager) {
            window.location.href = '/403';
            throw new Error('Property manager access required');
        }
    },

    initializeForm: function(form) {
        const propertySelect = form.querySelector('select[name="property_select"]');
        const confirmInput = form.querySelector('input[name="confirm_input"]');
        
        if (propertySelect && confirmInput) {
            // Add change listener to property select
            propertySelect.addEventListener('change', () => {
                confirmInput.disabled = !propertySelect.value;
                confirmInput.value = '';
            });

            // Add form submit handler
            form.addEventListener('submit', (event) => this.handleSubmit(event, propertySelect, confirmInput));
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
            const contentType = response.headers.get('content-type');
            if (!response.ok) {
                // Try to get JSON error message if available
                if (contentType && contentType.includes('application/json')) {
                    const errorData = await response.json();
                    throw new Error(errorData.message || 'Server error occurred');
                }
                throw new Error(`Server error: ${response.status}`);
            }
            // Parse JSON response
            const data = await response.json();
            // Check for specific error messages in the response
            if (!data.success) {
                throw new Error(data.message || 'Operation failed');
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
            window.showNotification(
                'Error removing property: ' + (error.message || 'An unexpected error occurred'),
                'error', 
                'both'
            );
        })
        .finally(() => {
            // Re-enable form elements
            propertySelect.disabled = false;
            confirmInput.disabled = false;
        });
    }
};

export default removePropertiesModule;