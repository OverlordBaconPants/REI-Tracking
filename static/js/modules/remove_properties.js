// remove_properties.js

const removePropertiesModule = {
    init: async function() {
        try {
            console.log('RemovePropertiesModule initialized');
            const form = document.querySelector('.remove-properties-container form');
            if (form) {
                this.initializeForm(form);
                window.showNotification('Remove Properties module loaded', 'success');
            } else {
                console.error('Remove properties form not found');
                window.showNotification('Form not found', 'error');
            }
        } catch (error) {
            console.error('Error initializing Remove Properties module:', error);
            window.showNotification('Error loading Remove Properties module: ' + error.message, 'error');
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
        
        // Validate selection
        if (!propertySelect.value) {
            window.showNotification('Please select a property to remove', 'error');
            return;
        }

        // Validate confirmation phrase
        const expectedPhrase = "I am sure I want to do this.";
        if (confirmInput.value !== expectedPhrase) {
            window.showNotification('Please enter the correct confirmation phrase', 'error');
            return;
        }

        // Create and submit form data
        const formData = new FormData();
        formData.append('property_select', propertySelect.value);
        formData.append('confirm_input', confirmInput.value);

        fetch('/properties/remove_properties', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                window.showNotification('Property successfully removed', 'success');
                // Reload page after a short delay to show the success message
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                window.showNotification(data.message || 'Error removing property', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            window.showNotification('Error removing property: ' + error.message, 'error');
        });
    }
};

// Single export at the end of the file
export default removePropertiesModule;