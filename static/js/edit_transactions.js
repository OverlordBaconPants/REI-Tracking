const editTransactionsModule = {
    init: function() {
        console.log('Initializing edit transactions module');
        this.form = document.getElementById('edit-transaction-form');
        if (this.form) {
            this.initEventListeners();
            this.populateCategories();
            this.updateCollectorPayerLabel();
            this.populatePartners();
            this.updateReimbursementDetails();
        } else {
            console.error('Edit Transaction form not found');
        }
    },

    initEventListeners: function() {
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
        document.getElementById('cancel-edit').addEventListener('click', this.handleCancel.bind(this));
        document.querySelectorAll('input[name="type"]').forEach(radio => {
            radio.addEventListener('change', this.handleTypeChange.bind(this));
        });
        document.getElementById('amount').addEventListener('input', this.updateReimbursementDetails.bind(this));
        document.getElementById('collector_payer').addEventListener('change', this.updateReimbursementDetails.bind(this));
    },

    populateCategories: function() {
        const typeRadios = document.querySelectorAll('input[name="type"]');
        let type = '';
        for (let radio of typeRadios) {
            if (radio.checked) {
                type = radio.value;
                break;
            }
        }
        if (!type) {
            console.error('No transaction type selected');
            return;
        }
        fetch(`/transactions/api/categories?type=${type}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(categories => {
                const categorySelect = document.getElementById('category');
                categorySelect.innerHTML = '<option value="">Select a category</option>';
                categories.forEach(category => {
                    const option = document.createElement('option');
                    option.value = category;
                    option.textContent = category;
                    categorySelect.appendChild(option);
                });
                // Set the current category
                const currentCategory = this.form.querySelector('input[name="category"]').value;
                if (currentCategory) {
                    categorySelect.value = currentCategory;
                }
            })
            .catch(error => console.error('Error fetching categories:', error));
    },

    handleTypeChange: function(event) {
        this.populateCategories();
        this.updateCollectorPayerLabel();
        this.updateReimbursementDetails();
    },

    updateCollectorPayerLabel: function() {
        const type = document.querySelector('input[name="type"]:checked').value;
        const label = document.getElementById('collector_payer_label');
        label.textContent = type === 'income' ? 'Received by:' : 'Paid by:';
    },

    populatePartners: function() {
        const propertyId = encodeURIComponent(document.getElementById('property_id').value);
        fetch(`/transactions/api/partners?property_id=${propertyId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(partners => {
                const partnerSelect = document.getElementById('collector_payer');
                partnerSelect.innerHTML = '<option value="">Select a partner</option>';
                partners.forEach(partner => {
                    const option = document.createElement('option');
                    option.value = partner.name;
                    option.textContent = partner.name;
                    partnerSelect.appendChild(option);
                });
                // Set the current collector/payer
                const currentCollectorPayer = this.form.querySelector('input[name="collector_payer"]').value;
                if (currentCollectorPayer) {
                    partnerSelect.value = currentCollectorPayer;
                }
            })
            .catch(error => console.error('Error fetching partners:', error));
    },

    updateReimbursementDetails: function() {
        // Implement reimbursement details update logic here
        // This will be similar to the add_transactions.js implementation
    },

    handleSubmit: function(event) {
        event.preventDefault();
        console.log('Form submission started');
    
        const formData = new FormData(this.form);
        
        // Log form data
        for (let [key, value] of formData.entries()) {
            console.log(key, value);
        }
    
        fetch(this.form.action, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            console.log('Response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Response data:', data);
            if (data.success) {
                this.showFlashMessage('Transaction Changed Successfully!', 'success');
                setTimeout(() => {
                    if (window.parent && typeof window.parent.closeEditModal === 'function') {
                        window.parent.closeEditModal();
                    } else {
                        window.parent.location.reload();
                    }
                }, 2000);
            } else {
                this.showFlashMessage('Error updating transaction: ' + (data.message || 'Unknown error'), 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            this.showFlashMessage('An error occurred while updating the transaction', 'error');
        });
    },

    handleCancel: function() {
        this.showFlashMessage('Transaction Edit Canceled', 'success');
        setTimeout(() => {
            window.parent.location.reload();
        }, 3000);
    },

    showFlashMessage: function(message, category) {
        const flashMessagesContainer = document.querySelector('.flash-messages');
        if (flashMessagesContainer) {
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${category} alert-dismissible fade show`;
            alertDiv.role = 'alert';
            alertDiv.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            flashMessagesContainer.appendChild(alertDiv);
            setTimeout(() => {
                alertDiv.remove();
            }, 3000);
        } else {
            console.error('Flash messages container not found');
        }
    }
};

export default editTransactionsModule;