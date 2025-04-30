/**
 * BulkImportModule - Handles bulk import of transaction data
 * Includes comprehensive validation, error handling, and logging
 */

const BulkImportModule = {
    // Keep existing configuration
    config: {
        maxFileSize: 5 * 1024 * 1024,
        allowedFileTypes: ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
        maxRowsToProcess: 1000,
        validDateFormats: ['YYYY-MM-DD', 'MM/DD/YYYY', 'DD/MM/YYYY'],
        amountRegex: /^-?\d*\.?\d+$/
    },

    // Keep existing properties
    validationErrors: [],
    categories: {},

    // Add dateUtils object here
    dateUtils: {
        normalizeDate: function(value) {
            if (!value) return null;

            try {
                // If already a Date object
                if (value instanceof Date) {
                    if (isNaN(value.getTime())) return null;
                    return value.toISOString().split('T')[0];
                }

                // If string, try direct Date parsing first
                if (typeof value === 'string') {
                    value = value.trim();
                    
                    // Try parsing as ISO string first
                    const isoDate = new Date(value);
                    if (!isNaN(isoDate.getTime())) {
                        return isoDate.toISOString().split('T')[0];
                    }

                    // Try parsing common formats
                    const formats = [
                        { regex: /^(\d{4})-(\d{2})-(\d{2})$/, order: [1, 2, 3] },             // YYYY-MM-DD
                        { regex: /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/, order: [3, 1, 2] },       // MM/DD/YYYY or DD/MM/YYYY
                        { regex: /^(\d{4})\.(\d{2})\.(\d{2})$/, order: [1, 2, 3] },           // YYYY.MM.DD
                        { regex: /^(\d{1,2})-(\d{1,2})-(\d{4})$/, order: [3, 1, 2] },         // MM-DD-YYYY or DD-MM-YYYY
                        { regex: /^(\d{4})\/(\d{2})\/(\d{2})$/, order: [1, 2, 3] },           // YYYY/MM/DD
                    ];

                    for (const format of formats) {
                        const match = value.match(format.regex);
                        if (match) {
                            const [year, month, day] = format.order.map(i => parseInt(match[i], 10));
                            const date = new Date(year, month - 1, day);
                            
                            // Validate the date is valid and components match
                            if (!isNaN(date.getTime()) && 
                                date.getFullYear() === year &&
                                date.getMonth() === month - 1 &&
                                date.getDate() === day) {
                                return date.toISOString().split('T')[0];
                            }
                        }
                    }

                    // Try parsing dates with month names
                    const monthNameFormats = [
                        /^([A-Za-z]{3,9})\s+(\d{1,2}),?\s+(\d{4})$/,  // Month DD YYYY
                        /^(\d{1,2})\s+([A-Za-z]{3,9})\s+(\d{4})$/     // DD Month YYYY
                    ];

                    const monthMap = {
                        jan: 0, feb: 1, mar: 2, apr: 3, may: 4, jun: 5,
                        jul: 6, aug: 7, sep: 8, oct: 9, nov: 10, dec: 11,
                        january: 0, february: 1, march: 2, april: 3, june: 5,
                        july: 6, august: 7, september: 8, october: 9, november: 10, december: 11
                    };

                    for (const format of monthNameFormats) {
                        const match = value.match(format);
                        if (match) {
                            let [_, part1, part2, year] = match;
                            year = parseInt(year, 10);
                            
                            // Determine if part1 is month or day
                            let month, day;
                            if (isNaN(parseInt(part1))) {
                                month = monthMap[part1.toLowerCase()];
                                day = parseInt(part2, 10);
                            } else {
                                day = parseInt(part1, 10);
                                month = monthMap[part2.toLowerCase()];
                            }
                            
                            if (month !== undefined && !isNaN(day) && !isNaN(year)) {
                                const date = new Date(year, month, day);
                                if (!isNaN(date.getTime())) {
                                    return date.toISOString().split('T')[0];
                                }
                            }
                        }
                    }
                }

                // If number, try Excel date number conversion
                if (typeof value === 'number' || !isNaN(value)) {
                    const excelDate = new Date((value - 25569) * 86400 * 1000);
                    if (!isNaN(excelDate.getTime())) {
                        return excelDate.toISOString().split('T')[0];
                    }
                }

            } catch (error) {
                console.error('Date normalization error:', error);
            }

            return null;
        }
    },

    /**
     * Initialize the module
     * Sets up event listeners and fetches required data
     */

    init: async function() {
        console.log('Initializing BulkImportModule');
        try {
            this.setupEventListeners();
            await this.fetchCategories();
            this.logEvent('init', 'Module initialized successfully');
            toastr.success('Bulk import module loaded successfully');
        } catch (error) {
            this.logError('init', error);
            toastr.error('Error initializing bulk import module. Check console for details.');
        }
    },

    /**
     * Fetch categories from the API
     * @throws {Error} If categories cannot be fetched
     */

    async fetchCategories() {
        try {
            const response = await fetch('/api/categories');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const categories = await response.json();
            
            // Validate categories structure
            if (!this.validateCategoriesStructure(categories)) {
                throw new Error('Invalid categories structure received from server');
            }
            
            this.categories = categories;
            this.logEvent('fetchCategories', `Fetched ${Object.keys(categories).length} category types`);
        } catch (error) {
            this.logError('fetchCategories', error);
            throw new Error('Failed to fetch categories: ' + error.message);
        }
    },

    /**
     * Validate the structure of received categories
     * @param {Object} categories - Categories object to validate
     * @returns {boolean} - Whether the structure is valid
     */

    validateCategoriesStructure(categories) {
        return categories 
            && typeof categories === 'object'
            && Array.isArray(categories.income)
            && Array.isArray(categories.expense);
    },

    /**
     * Set up event listeners for the module
     */

    setupEventListeners: function() {
        const fileInput = document.getElementById('file');
        const form = document.getElementById('bulk-import-form');

        if (fileInput) {
            fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        } else {
            this.logError('setupEventListeners', 'File input element not found');
        }

        if (form) {
            form.addEventListener('submit', this.handleFormSubmit.bind(this));
        } else {
            this.logError('setupEventListeners', 'Form element not found');
        }
    },

    // Field definitions with enhanced validation
    fields: [
        {
            name: 'Property',
            required: false,
            description: 'Property identifier',
            validate: function(value) {
                if (!value) return true; // Optional field
                return typeof value === 'string' && value.length <= 255;
            }
        },
        {
            name: 'Transaction Type',
            required: false,
            description: 'Income or Expense',
            validate: function(value) {
                if (!value) return true;
                const normalized = value.toLowerCase();
                return ['income', 'expense'].includes(normalized);
            },
            transform: value => {
                const normalized = value?.toLowerCase();
                return normalized === 'income' ? 'Income' : 
                       normalized === 'expense' ? 'Expense' : value;
            }
        },
        {
            name: 'Category',
            required: false,
            description: 'Transaction category',
            validate: function(value, row) {
                if (!value) return true;
                const type = row['Transaction Type']?.toLowerCase();
                const validCategories = type === 'income' ? 
                    this.categories?.income || [] : 
                    type === 'expense' ? 
                    this.categories?.expense || [] : 
                    [];
                const isValid = validCategories.includes(value);
                if (!isValid) {
                    this.validationErrors.push(`Invalid category '${value}' for type '${type}'`);
                }
                return isValid;
            }
        },
        {
            name: 'Item Description',
            required: false,
            description: 'Transaction description',
            validate: function(value) {
                if (!value) return true;
                return typeof value === 'string' && value.length <= 500;
            },
            transform: value => value?.trim()
        },
        {
            name: 'Amount',
            required: false,
            description: 'Transaction amount',
            validate: function(value) {
                if (!value) return true;
                const numValue = parseFloat(value.replace(/[^0-9.-]+/g, ''));
                return !isNaN(numValue) && numValue !== 0;
            },
            transform: value => {
                const numValue = parseFloat(value?.replace(/[^0-9.-]+/g, '')) || 0;
                return Number.isFinite(numValue) ? numValue : 0;
            }
        },
        {
            name: 'Date Received or Paid',
            required: false,
            description: 'Transaction date',
            validate: function(value) {
                if (!value) return true;
                const date = new Date(value);
                return date instanceof Date && !isNaN(date);
            },
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
            description: 'Transaction party',
            validate: function(value) {
                if (!value) return true;
                return typeof value === 'string' && value.length <= 255;
            },
            transform: value => value?.trim()
        }
    ],

    /**
     * Handle file selection
     * Validates file type and size before processing
     * @param {Event} e - File input change event
     */

    handleFileSelect: async function(e) {
        const file = e.target.files[0];
        if (!file) {
            this.logEvent('handleFileSelect', 'No file selected');
            return;
        }

        // Validate file type and size
        if (!this.validateFile(file)) {
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            this.logEvent('handleFileSelect', `Processing file: ${file.name}`);
            const response = await fetch('/transactions/get_columns', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                this.logError('handleFileSelect', `Server reported error: ${data.error}`);
                toastr.error(data.error);
            } else if (Array.isArray(data.columns)) {
                this.logEvent('handleFileSelect', `Received ${data.columns.length} columns`);
                this.createColumnMapping(data.columns);
                toastr.success('File processed successfully. Please map the columns.');
            } else {
                this.logError('handleFileSelect', 'Unexpected response format');
                toastr.error('Unexpected response format from server');
            }
        } catch (error) {
            this.logError('handleFileSelect', error);
            toastr.error(
                'An error occurred while processing the file. Please try again.',
                'File Processing Error',
                { timeOut: 0, closeButton: true }
            );
        }
    },

    /**
     * Validate uploaded file
     * @param {File} file - File to validate
     * @returns {boolean} - Whether the file is valid
     */

    validateFile: function(file) {
        if (!this.config.allowedFileTypes.includes(file.type)) {
            this.logError('validateFile', `Invalid file type: ${file.type}`);
            toastr.error('Please upload a CSV or Excel file');
            return false;
        }

        if (file.size > this.config.maxFileSize) {
            this.logError('validateFile', `File too large: ${file.size} bytes`);
            toastr.error('File size must be less than 5MB');
            return false;
        }

        return true;
    },

    /**
     * Create column mapping interface
     * @param {string[]} columns - Array of column names from uploaded file
     */

    createColumnMapping: function(columns) {
        const mappingDiv = document.getElementById('column-mapping');
        if (!mappingDiv) {
            this.logError('createColumnMapping', 'Mapping div not found');
            return;
        }

        this.logEvent('createColumnMapping', `Creating mapping for ${columns.length} columns`);

        // Create mapping interface HTML
        mappingDiv.innerHTML = this.createMappingHTML();
        
        // Create field mapping elements
        this.fields.forEach(field => {
            const containerDiv = this.createFieldMappingElement(field, columns);
            mappingDiv.appendChild(containerDiv);
        });

        // Add hidden input for mapping
        const mappingInput = document.createElement('input');
        mappingInput.type = 'hidden';
        mappingInput.name = 'column_mapping';
        mappingDiv.appendChild(mappingInput);

        // Setup change event listener
        mappingDiv.addEventListener('change', this.updateColumnMapping.bind(this));
        
        this.logEvent('createColumnMapping', 'Mapping interface created successfully');
    },

    /**
     * Create HTML for mapping interface
     * @returns {string} HTML for mapping interface
     */

    createMappingHTML: function() {
        return `
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
    },

    /**
     * Create field mapping element
     * @param {Object} field - Field definition
     * @param {string[]} columns - Available columns
     * @returns {HTMLElement} Field mapping container
     */

    createFieldMappingElement: function(field, columns) {
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
        
        return containerDiv;
    },

    /**
     * Update column mapping when selections change
     */

    updateColumnMapping: function() {
        const mapping = {};
        this.fields.forEach(field => {
            const select = document.querySelector(`select[name="mapping_${field.name}"]`);
            if (select && select.value) {  // Only include if there's a value
                mapping[field.name.replace(/\s+/g, ' ')] = select.value;
            }
        });
        
        const mappingInput = document.querySelector('input[name="column_mapping"]');
        if (mappingInput) {
            const mappingJson = JSON.stringify(mapping);
            mappingInput.value = mappingJson;
            this.logEvent('updateColumnMapping', `Mapping updated: ${mappingJson}`);
        } else {
            this.logError('updateColumnMapping', 'Mapping input not found');
        }
    },

    /**
     * Handle form submission
     * Validates data and sends to server
     * @param {Event} e - Form submit event
     */

    handleFormSubmit: async function(e) {
        e.preventDefault();
        
        const submitButton = e.target.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.innerHTML;
        
        try {
            // Validate mapping
            const mappingInput = document.querySelector('input[name="column_mapping"]');
            if (!mappingInput || !mappingInput.value) {
                toastr.error('Please map at least one column');
                return;
            }
    
            // Verify the mapping is valid JSON
            try {
                JSON.parse(mappingInput.value);
            } catch (error) {
                toastr.error('Invalid column mapping format');
                return;
            }
    
            // Update UI
            submitButton.disabled = true;
            submitButton.innerHTML = 'Importing...';
            
            // Create FormData
            const formData = new FormData(e.target);
            this.logEvent('handleFormSubmit', 'Sending import request');
            this.logEvent('handleFormSubmit', `Column mapping: ${mappingInput.value}`);
    
            // Send request
            const response = await this.sendImportRequest(formData);
            
            // Handle response
            await this.handleImportResponse(response);
            
        } catch (error) {
            this.logError('handleFormSubmit', error);
            toastr.error(
                error.message || 'An error occurred during import',
                'Import Error',
                { timeOut: 0, closeButton: true }
            );
        } finally {
            submitButton.disabled = false;
            submitButton.innerHTML = originalButtonText;
        }
    },

    /**
     * Validate column mapping
     * @returns {boolean} Whether mapping is valid
     */

    validateMapping: function() {
        const mappingInput = document.querySelector('input[name="column_mapping"]');
        if (!mappingInput || !mappingInput.value) {
            toastr.error('Please select a file and map at least one column');
            return false;
        }

        const mapping = JSON.parse(mappingInput.value);
        const mappedFields = Object.values(mapping).filter(Boolean);
        
        if (mappedFields.length === 0) {
            toastr.error('Please map at least one column');
            return false;
        }

        return true;
    },

    /**
     * Send import request to server
     * @param {FormData} formData - Form data to send
     * @returns {Response} Server response
     */

    sendImportRequest: async function(formData) {
        const response = await fetch('/transactions/bulk_import', {
            method: 'POST',
            body: formData
        });
        
        this.logEvent('sendImportRequest', `Response status: ${response.status}`);
        
        return response;
    },

    /**
     * Handle the server's response to the import request
     * @param {Response} response - Server response object
     * @throws {Error} If response processing fails
     */

    async handleImportResponse(response) {
        let result;
        try {
            const text = await response.text();
            this.logEvent('handleImportResponse', `Raw response: ${text}`);
            result = JSON.parse(text);
        } catch (error) {
            this.logError('handleImportResponse', `Parse error: ${error.message}`);
            throw new Error(`Failed to parse server response: ${error.message}`);
        }
        
        if (!response.ok) {
            throw new Error(result.error || `Server error: ${response.status}`);
        }
        
        if (result.success) {
            await this.handleSuccessfulImport(result);
        } else {
            throw new Error(result.error || 'Import failed');
        }
    },

    /**
     * Handle successful import result
     * @param {Object} result - Successful import result data
     */

    async handleSuccessfulImport(result) {
        this.logEvent('handleSuccessfulImport', 
            `Processed: ${result.stats.total_processed}, Saved: ${result.stats.total_saved}`
        );

        // Show success message
        toastr.success(
            `Successfully processed ${result.stats.total_processed} rows, saved ${result.stats.total_saved} transactions`,
            'Import Completed'
        );
        
        // Handle modifications if any
        if (result.modifications?.length > 0) {
            this.handleModifications(result.modifications);
        }
        
        // Calculate redirect delay based on number of modifications
        const redirectDelay = Math.min(2000, (result.modifications?.length || 0) * 500 || 2000);
        
        // Schedule redirect
        this.logEvent('handleSuccessfulImport', `Scheduling redirect in ${redirectDelay}ms`);
        setTimeout(() => {
            window.location.href = result.redirect;
        }, redirectDelay);
    },

    /**
     * Handle data modifications from import
     * @param {Array} modifications - Array of modification objects
     */

    handleModifications(modifications) {
        this.logEvent('handleModifications', `Processing ${modifications.length} modifications`);
        
        // Group modifications by row
        const groupedMods = modifications.reduce((acc, mod) => {
            if (!acc[mod.row]) {
                acc[mod.row] = [];
            }
            acc[mod.row].push(mod);
            return acc;
        }, {});
        
        // Show notifications for each row's modifications
        Object.entries(groupedMods).forEach(([row, mods]) => {
            const messages = mods.map(mod => mod.message);
            this.logEvent('handleModifications', `Row ${row} modifications: ${messages.join(', ')}`);
            
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
    },

    /**
     * Log an event for debugging purposes
     * @param {string} method - Method where event occurred
     * @param {string} message - Event message
     */
    logEvent: function(method, message) {
        const timestamp = new Date().toISOString();
        console.log(`[${timestamp}] [${method}] ${message}`);
        
        // Could be extended to send logs to server or analytics service
        if (window.debugMode) {
            const logElement = document.getElementById('debug-log');
            if (logElement) {
                logElement.innerHTML += `<div>[${timestamp}] [${method}] ${message}</div>`;
            }
        }
    },

    /**
     * Log an error for debugging purposes
     * @param {string} method - Method where error occurred
     * @param {Error|string} error - Error object or message
     */
    logError: function(method, error) {
        const timestamp = new Date().toISOString();
        const errorMessage = error instanceof Error ? error.message : error;
        const stackTrace = error instanceof Error ? error.stack : new Error().stack;
        
        console.error(`[${timestamp}] [${method}] Error: ${errorMessage}`);
        console.error('Stack trace:', stackTrace);
        
        // Could be extended to send errors to error tracking service
        if (window.debugMode) {
            const logElement = document.getElementById('debug-log');
            if (logElement) {
                logElement.innerHTML += `<div class="error">[${timestamp}] [${method}] Error: ${errorMessage}</div>`;
            }
        }
    },

    /**
     * Validate a transaction row
     * @param {Object} row - Transaction data row
     * @returns {Object} Validation result with errors array
     */
    validateRow: function(row) {
        const errors = [];
        
        this.fields.forEach(field => {
            const value = row[field.name];
            if (field.required && !value) {
                errors.push(`${field.name} is required`);
            } else if (value && field.validate) {
                try {
                    const isValid = field.validate.call(this, value, row);
                    if (!isValid) {
                        errors.push(`Invalid ${field.name}: ${value}`);
                    }
                } catch (error) {
                    this.logError('validateRow', `Validation error for ${field.name}: ${error.message}`);
                    errors.push(`Error validating ${field.name}`);
                }
            }
        });

        return {
            valid: errors.length === 0,
            errors: errors
        };
    }
};

export default BulkImportModule;