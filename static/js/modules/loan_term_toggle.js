const LoanTermToggle = {
    init: function(primaryInputId, secondaryInputId) {
        this.setupToggle(primaryInputId);
        if (secondaryInputId) {
            this.setupToggle(secondaryInputId);
        }
    },

    setupToggle: function(inputId) {
        const originalInput = document.getElementById(inputId);
        if (!originalInput) return;

        // Create container div
        const container = document.createElement('div');
        container.className = 'input-group';
        originalInput.parentNode.insertBefore(container, originalInput);

        // Create number input
        const numberInput = document.createElement('input');
        numberInput.type = 'number';
        numberInput.className = 'form-control';
        numberInput.name = originalInput.name;
        numberInput.id = originalInput.id;
        numberInput.required = originalInput.required;
        numberInput.value = originalInput.value;
        numberInput.min = '0';

        // Create toggle button
        const toggleButton = document.createElement('button');
        toggleButton.type = 'button';
        toggleButton.className = 'btn btn-outline-secondary';
        toggleButton.textContent = 'Months';
        toggleButton.dataset.mode = 'months';

        // Add elements to container
        container.appendChild(numberInput);
        container.appendChild(toggleButton);

        // Remove original input
        originalInput.remove();

        // Add event listeners
        toggleButton.addEventListener('click', function() {
            const currentValue = parseFloat(numberInput.value) || 0;
            const isMonths = toggleButton.dataset.mode === 'months';

            if (isMonths) {
                // Converting from months to years
                numberInput.value = Math.round(currentValue / 12);
                toggleButton.textContent = 'Years';
                toggleButton.dataset.mode = 'years';
            } else {
                // Converting from years to months
                numberInput.value = currentValue * 12;
                toggleButton.textContent = 'Months';
                toggleButton.dataset.mode = 'months';
            }

            // Trigger change event for form validation
            const event = new Event('input', { bubbles: true });
            numberInput.dispatchEvent(event);
        });

        numberInput.addEventListener('input', function() {
            // Ensure value is non-negative
            if (this.value < 0) this.value = 0;
        });

        return container;
    },

    // Helper function to get value in months
    getValueInMonths: function(inputId) {
        const container = document.getElementById(inputId).parentNode;
        const input = document.getElementById(inputId);
        const toggle = container.querySelector('button');
        const value = parseFloat(input.value) || 0;

        return toggle.dataset.mode === 'years' ? value * 12 : value;
    },

    // Helper function to set value (in months)
    setValue: function(inputId, monthsValue) {
        const container = document.getElementById(inputId).parentNode;
        const input = document.getElementById(inputId);
        const toggle = container.querySelector('button');
        
        if (toggle.dataset.mode === 'years') {
            input.value = Math.round(monthsValue / 12);
        } else {
            input.value = monthsValue;
        }
    }
};

export default LoanTermToggle;