// remove_properties.js

const removePropertiesModule = {
    init: function() {
        const form = document.querySelector('#remove-property-form');
        const propertySelect = document.querySelector('#property-select');
        const confirmInput = document.querySelector('#confirm-input');
        const removeButton = document.querySelector('#remove-button');

        if (form && propertySelect && confirmInput && removeButton) {
            form.addEventListener('submit', this.handleSubmit.bind(this));
            propertySelect.addEventListener('change', this.updateRemoveButton.bind(this));
            confirmInput.addEventListener('input', this.updateRemoveButton.bind(this));
        }
    },

    handleSubmit: function(event) {
        event.preventDefault();
        console.log('Form submission started');
        
        const form = event.target;
        const formData = new FormData(form);
        
        const propertyAddress = formData.get('property_select');
        const confirmPhrase = formData.get('confirm_input');

        if (!this.validateForm(propertyAddress, confirmPhrase)) {
            console.log('Form validation failed');
            return;
        }

        const removeData = {
            address: propertyAddress
        };

        console.log('Sending remove property data:', JSON.stringify(removeData, null, 2));

        fetch('/admin/remove_properties', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(removeData)
        })
        .then(response => response.json())
        .then(data => {
            console.log('Server response:', data);
            if (data.success) {
                alert('Property removed successfully!');
                window.location.reload();
            } else {
                alert('Error: ' + (data.message || 'Failed to remove property'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while removing the property. Please check the console for more details.');
        });
    },

    validateForm: function(propertyAddress, confirmPhrase) {
        if (!propertyAddress) {
            alert('Please select a property to remove.');
            return false;
        }

        if (confirmPhrase !== this.getConfirmPhrase()) {
            alert('Please enter the correct confirmation phrase.');
            return false;
        }

        return true;
    },

    updateRemoveButton: function() {
        const propertySelect = document.querySelector('#property-select');
        const confirmInput = document.querySelector('#confirm-input');
        const removeButton = document.querySelector('#remove-button');
        
        removeButton.disabled = !(propertySelect.value && confirmInput.value === this.getConfirmPhrase());
    },

    getConfirmPhrase: function() {
        return "I am sure I want to do this.";
    }
};

export default removePropertiesModule;