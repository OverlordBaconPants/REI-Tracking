// edit_transactions.js

const editTransactionsModule = {
    init: function() {
        console.log('Initializing edit transactions module');
        const form = document.getElementById('editTransactionForm');
        const typeSelect = document.getElementById('type');
        
        if (form) {
            form.addEventListener('submit', this.handleSubmit.bind(this));
        }

        if (typeSelect) {
            typeSelect.addEventListener('change', this.handleTypeChange.bind(this));
            this.handleTypeChange({ target: typeSelect }); // Initialize categories
        }

        this.initializeForm();
        this.checkFlashMessages();
    },

    checkFlashMessages: function() {
        const flashMessages = document.querySelectorAll('.flash-message');
        flashMessages.forEach(message => {
            alert(message.textContent);
            message.remove();
        });
    },

    initializeForm: function() {
        // Initialize any form elements or set up additional event listeners
        const dateInput = document.getElementById('date');
        if (dateInput) {
            dateInput.valueAsDate = new Date(dateInput.value);
        }

        // Set up the initial state of the category dropdown
        const initialType = document.getElementById('type').value;
        this.updateCategoryOptions(initialType);
        this.updateCollectorPayerLabel(initialType);
    },

    handleTypeChange: function(event) {
        const transactionType = event.target.value;
        this.updateCategoryOptions(transactionType);
        this.updateCollectorPayerLabel(transactionType);
    },

    updateCategoryOptions: function(transactionType) {
        const categorySelect = document.getElementById('category');
        const currentCategory = categorySelect.value;
        categorySelect.innerHTML = ''; // Clear existing options

        const categories = transactionType === 'income' ? 
            ['Rent', 'Other Income'] : 
            ['Mortgage', 'Utilities', 'Maintenance', 'Taxes', 'Insurance', 'Other Expense'];

        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category.toLowerCase().replace(' ', '_');
            option.textContent = category;
            categorySelect.appendChild(option);
        });

        // Try to set the previously selected category, if it exists in the new list
        if (categories.map(c => c.toLowerCase().replace(' ', '_')).includes(currentCategory)) {
            categorySelect.value = currentCategory;
        }
    },

    updateCollectorPayerLabel: function(transactionType) {
        const label = document.getElementById('collector_payer_label');
        label.textContent = transactionType === 'income' ? 'Payer:' : 'Payee:';
    },

    handleSubmit: function(event) {
        // Perform any client-side validation here
        const form = event.target;
        const amount = parseFloat(form.amount.value);
        
        if (isNaN(amount) || amount <= 0) {
            event.preventDefault();
            alert('Please enter a valid positive number for the amount.');
            return;
        }

        // You can add more validations as needed

        console.log('Form submission started');
        // The form will submit normally, allowing server-side processing and flash messages
    },

    // Helper function to format currency (if needed)
    formatCurrency: function(number) {
        return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(number);
    }
};

export default editTransactionsModule;