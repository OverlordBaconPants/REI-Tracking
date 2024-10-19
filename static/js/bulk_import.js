document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('file');
    const form = document.getElementById('bulk-import-form');
    const mappingDiv = document.getElementById('column-mapping');
    const requiredFields = ['Property', 'Transaction Type', 'Category', 'Item Description', 'Amount', 'Date Received or Paid', 'Paid By'];

    fileInput.addEventListener('change', handleFileSelect);
    form.addEventListener('submit', handleFormSubmit);

    function handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('file', file);

            fetch('/transactions/get_columns', { method: 'POST', body: formData })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        showError(data.error);
                    } else if (Array.isArray(data.columns)) {
                        createColumnMapping(data.columns);
                    } else {
                        showError('Unexpected response format from server');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showError('An error occurred while processing the file. Please try again.');
                });
        }
    }

    function createColumnMapping(columns) {
        mappingDiv.innerHTML = '';
        
        requiredFields.forEach(field => {
            const select = document.createElement('select');
            select.name = `mapping_${field}`;
            select.className = 'form-select mb-2';
            select.innerHTML = `<option value="">Select column for ${field}</option>`;
            columns.forEach(col => {
                select.innerHTML += `<option value="${col}">${col}</option>`;
            });
            const label = document.createElement('label');
            label.innerHTML = `Map ${field} to:`;
            label.className = 'form-label';
            mappingDiv.appendChild(label);
            mappingDiv.appendChild(select);
        });

        // Add a hidden input to store the complete mapping
        const mappingInput = document.createElement('input');
        mappingInput.type = 'hidden';
        mappingInput.name = 'column_mapping';
        mappingDiv.appendChild(mappingInput);

        // Update the hidden input whenever a select changes
        mappingDiv.addEventListener('change', updateColumnMapping);
    }

    function updateColumnMapping() {
        const mapping = {};
        requiredFields.forEach(field => {
            mapping[field] = document.querySelector(`select[name="mapping_${field}"]`).value;
        });
        const mappingInput = document.querySelector('input[name="column_mapping"]');
        mappingInput.value = JSON.stringify(mapping);
    }

    function handleFormSubmit(e) {
        e.preventDefault();
        
        // Validate that all required fields are mapped
        const mapping = JSON.parse(document.querySelector('input[name="column_mapping"]').value);
        const missingFields = requiredFields.filter(field => !mapping[field]);
        
        if (missingFields.length > 0) {
            showError(`Please map all required fields. Missing: ${missingFields.join(', ')}`);
            return;
        }

        // If all fields are mapped, submit the form
        this.submit();
    }

    function showError(message) {
        // You can implement this function to show error messages to the user
        // For example, you could create a new div element and add it to the page
        // or use a modal or toast notification system
        alert(message);  // For simplicity, we're using an alert here
    }
});