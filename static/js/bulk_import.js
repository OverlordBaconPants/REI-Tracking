const BulkImportModule = {
    init: async function() {
        try {
            this.setupEventListeners();
            // Fetch categories for validation
            const response = await fetch('/transactions/api/categories');
            this.categories = await response.json();
            toastr.success('Bulk import module loaded successfully');
        } catch (error) {
            console.error('Error initializing module:', error);
            toastr.error('Error initializing bulk import module');
        }
    },

    setupEventListeners: function() {
        const fileInput = document.getElementById('file');
        const form = document.getElementById('bulk-import-form');
        const mappingDiv = document.getElementById('column-mapping');

        if (fileInput) {
            fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        }
        if (form) {
            form.addEventListener('submit', this.handleFormSubmit.bind(this));
        }
    },

    // Fields are now optional
    fields: [
        {
            name: 'Property',
            required: false,
            description: 'Property identifier'
        },
        {
            name: 'Transaction Type',
            required: false,
            description: 'Income or Expense',
            transform: value => value?.toLowerCase() === 'income' ? 'Income' : 
                              value?.toLowerCase() === 'expense' ? 'Expense' : value
        },
        {
            name: 'Category',
            required: false,
            description: 'Transaction category',
            validate: function(value, row) {
                if (!value) return true; // Allow empty values
                const type = row['Transaction Type']?.toLowerCase();
                const validCategories = type === 'income' ? 
                    this.categories?.income || [] : 
                    type === 'expense' ? 
                    this.categories?.expense || [] : 
                    [];
                return validCategories.includes(value);
            }
        },
        {
            name: 'Item Description',
            required: false,
            description: 'Transaction description'
        },
        {
            name: 'Amount',
            required: false,
            description: 'Transaction amount',
            transform: value => parseFloat(value?.replace(/[^0-9.-]+/g, '')) || 0
        },
        {
            name: 'Date Received or Paid',
            required: false,
            description: 'Transaction date',
            transform: value => {
                if (!value) return '';
                const date = new Date(value);
                return date instanceof Date && !isNaN(date) ? 
                    date.toISOString().split('T')[0] : value;
            }
        },
        {
            name: 'Paid By',
            required: false,
            description: 'Transaction party'
        }
    ],

    handleFileSelect: async function(e) {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/transactions/get_columns', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                toastr.error(data.error);
            } else if (Array.isArray(data.columns)) {
                this.createColumnMapping(data.columns);
                toastr.success('File processed successfully. Please map the columns.');
            } else {
                toastr.error('Unexpected response format from server');
            }
        } catch (error) {
            console.error('Error:', error);
            toastr.error(
                'An error occurred while processing the file. Please try again.',
                'File Processing Error',
                { timeOut: 0, closeButton: true }
            );
        }
    },

    createColumnMapping: function(columns) {
        const mappingDiv = document.getElementById('column-mapping');
        if (!mappingDiv) return;

        mappingDiv.innerHTML = `
            <div class="alert alert-info">
                <h5>Column Mapping Instructions:</h5>
                <ul>
                    <li>Map your file columns to the appropriate fields</li>
                    <li>Fields can be left unmapped if data is not available</li>
                    <li>Category must match predefined values based on Transaction Type</li>
                    <li>Invalid categories will be flagged during import</li>
                </ul>
            </div>
        `;
        
        this.fields.forEach(field => {
            const containerDiv = document.createElement('div');
            containerDiv.className = 'mb-3';

            const label = document.createElement('label');
            label.innerHTML = `Map ${field.name} to: ${field.required ? '<span class="text-danger">*</span>' : ''}`;
            label.className = 'form-label';

            const select = document.createElement('select');
            select.name = `mapping_${field.name}`;
            select.className = 'form-select';
            select.innerHTML = `<option value="">Select column for ${field.name}</option>`;
            
            columns.forEach(col => {
                select.innerHTML += `<option value="${col}">${col}</option>`;
            });

            const description = document.createElement('small');
            description.className = 'form-text text-muted';
            description.textContent = field.description;

            containerDiv.appendChild(label);
            containerDiv.appendChild(select);
            containerDiv.appendChild(description);
            mappingDiv.appendChild(containerDiv);
        });

        // Add hidden input for complete mapping
        const mappingInput = document.createElement('input');
        mappingInput.type = 'hidden';
        mappingInput.name = 'column_mapping';
        mappingDiv.appendChild(mappingInput);

        // Setup change event listener
        mappingDiv.addEventListener('change', this.updateColumnMapping.bind(this));
    },

    updateColumnMapping: function() {
        const mapping = {};
        this.fields.forEach(field => {
            const select = document.querySelector(`select[name="mapping_${field.name}"]`);
            if (select) {
                mapping[field.name] = select.value;
            }
        });
        
        const mappingInput = document.querySelector('input[name="column_mapping"]');
        if (mappingInput) {
            mappingInput.value = JSON.stringify(mapping);
        }
    },

    handleFormSubmit: async function(e) {
        e.preventDefault();
        
        // Show loading indicator
        const submitButton = e.target.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.innerHTML;
        submitButton.disabled = true;
        submitButton.innerHTML = 'Importing...';
        
        try {
            const mappingInput = document.querySelector('input[name="column_mapping"]');
            if (!mappingInput || !mappingInput.value) {
                toastr.error('Please select a file and map at least one column');
                return;
            }

            const mapping = JSON.parse(mappingInput.value);
            const mappedFields = Object.values(mapping).filter(Boolean);
            
            if (mappedFields.length === 0) {
                toastr.error('Please map at least one column');
                return;
            }

            const formData = new FormData(e.target);
            
            console.log('Sending request with form data:', {
                file: formData.get('file'),
                mapping: formData.get('column_mapping')
            });

            const response = await fetch('/transactions/bulk_import', {
                method: 'POST',
                body: formData
            });
            
            // Log the response details for debugging
            console.log('Response status:', response.status);
            console.log('Response headers:', Object.fromEntries([...response.headers]));
            
            // Check content type
            const contentType = response.headers.get('content-type');
            console.log('Content-Type:', contentType);
            
            if (!contentType || !contentType.includes('application/json')) {
                console.error('Invalid content type:', contentType);
                throw new Error(`Unexpected response type: ${contentType}. Expected JSON.`);
            }

            let result;
            try {
                const text = await response.text();
                console.log('Response text:', text);
                result = JSON.parse(text);
            } catch (error) {
                console.error('Error parsing response:', error);
                throw new Error(`Failed to parse server response: ${error.message}`);
            }
            
            if (!response.ok) {
                throw new Error(result.error || `Server error: ${response.status}`);
            }
            
            if (result.success) {
                // Show success message with statistics
                toastr.success(
                    `Successfully processed ${result.stats.total_processed} rows, saved ${result.stats.total_saved} transactions`,
                    'Import Completed'
                );
                
                // Show modifications as warnings
                if (result.modifications && result.modifications.length > 0) {
                    // Group modifications by row
                    const groupedMods = result.modifications.reduce((acc, mod) => {
                        if (!acc[mod.row]) {
                            acc[mod.row] = [];
                        }
                        acc[mod.row].push(mod);
                        return acc;
                    }, {});
                    
                    // Show notifications for each row's modifications
                    Object.entries(groupedMods).forEach(([row, mods]) => {
                        const messages = mods.map(mod => mod.message);
                        toastr.warning(
                            `Row ${row}:<br>${messages.join('<br>')}`,
                            'Data Modifications',
                            { 
                                timeOut: 10000, 
                                extendedTimeOut: 5000,
                                closeButton: true,
                                progressBar: true,
                                newestOnTop: false,
                                preventDuplicates: true
                            }
                        );
                    });
                }
                
                // Redirect after showing notifications
                setTimeout(() => {
                    window.location.href = result.redirect;
                }, Math.min(2000, result.modifications?.length * 500 || 2000));
            } else {
                throw new Error(result.error || 'Import failed');
            }
        } catch (error) {
            console.error('Import error:', error);
            toastr.error(
                error.message || 'An error occurred during import',
                'Import Error',
                { 
                    timeOut: 0,
                    closeButton: true,
                    progressBar: false
                }
            );
        } finally {
            // Restore button state
            submitButton.disabled = false;
            submitButton.innerHTML = originalButtonText;
        }
    }
};

// Export the module for use in the main application
window.BulkImportModule = BulkImportModule;