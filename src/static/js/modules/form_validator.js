/**
 * form_validator.js - Enhanced form validation module
 * Provides comprehensive form validation with AJAX submission support
 */

/**
 * Form Validator Module
 * Handles form validation and submission
 */
const formValidatorModule = {
    /**
     * Initialize the form validator
     * @param {Object} config - Configuration options
     */
    init: function(config = {}) {
        console.log('Initializing form validator module');
        this.config = {
            validateOnBlur: true,
            validateOnInput: true,
            validateOnSubmit: true,
            showValidFeedback: true,
            ...config
        };
        
        this.initializeForms();
    },
    
    /**
     * Initialize all forms with data-validate attribute
     */
    initializeForms: function() {
        const forms = document.querySelectorAll('form[data-validate="true"]');
        forms.forEach(form => this.initializeForm(form));
    },
    
    /**
     * Initialize a specific form
     * @param {HTMLFormElement} form - The form to initialize
     */
    initializeForm: function(form) {
        // Add validation attributes
        form.setAttribute('novalidate', '');
        
        // Store original submit button text
        const submitButton = form.querySelector('[type="submit"]');
        if (submitButton && !submitButton.dataset.originalText) {
            submitButton.dataset.originalText = submitButton.innerHTML;
        }
        
        // Add submit handler
        if (this.config.validateOnSubmit) {
            form.removeEventListener('submit', this.handleSubmit);
            form.addEventListener('submit', this.handleSubmit.bind(this));
        }
        
        // Add input validation handlers
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            // Remove existing listeners to prevent duplicates
            input.removeEventListener('blur', this.handleBlur);
            input.removeEventListener('input', this.handleInput);
            
            // Add new listeners
            if (this.config.validateOnBlur) {
                input.addEventListener('blur', this.handleBlur.bind(this));
            }
            
            if (this.config.validateOnInput) {
                input.addEventListener('input', this.handleInput.bind(this));
            }
            
            // Add aria attributes for accessibility
            if (input.required) {
                input.setAttribute('aria-required', 'true');
            }
            
            // Add pattern description if available
            if (input.pattern) {
                const patternDesc = input.dataset.patternDescription;
                if (patternDesc) {
                    input.setAttribute('aria-describedby', `${input.id}-pattern-desc`);
                    
                    // Create description element if it doesn't exist
                    let descEl = document.getElementById(`${input.id}-pattern-desc`);
                    if (!descEl) {
                        descEl = document.createElement('div');
                        descEl.id = `${input.id}-pattern-desc`;
                        descEl.className = 'form-text text-muted';
                        descEl.textContent = patternDesc;
                        input.parentNode.insertBefore(descEl, input.nextSibling);
                    }
                }
            }
        });
    },
    
    /**
     * Handle form submission
     * @param {Event} e - The submit event
     */
    handleSubmit: function(e) {
        const form = e.target;
        
        // Validate all fields
        const isValid = this.validateForm(form);
        
        if (!isValid) {
            e.preventDefault();
            e.stopPropagation();
            
            // Show validation messages
            form.classList.add('was-validated');
            
            // Focus first invalid field
            const firstInvalid = form.querySelector(':invalid');
            if (firstInvalid) {
                firstInvalid.focus();
                
                // Scroll to first invalid field with smooth scrolling
                firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            
            // Show error notification
            if (window.showError) {
                window.showError('Please correct the errors in the form');
            }
            
            // Dispatch validation failed event
            form.dispatchEvent(new CustomEvent('validation:failed', {
                detail: { errors: this.getFormErrors(form) }
            }));
        } else {
            // If form has AJAX submission attribute, handle it
            if (form.dataset.ajax === 'true') {
                e.preventDefault();
                this.handleAjaxSubmit(form);
                
                // Dispatch validation success event
                form.dispatchEvent(new CustomEvent('validation:success'));
            }
        }
    },
    
    /**
     * Validate an entire form
     * @param {HTMLFormElement} form - The form to validate
     * @returns {boolean} Whether the form is valid
     */
    validateForm: function(form) {
        let isValid = true;
        
        // Validate all inputs
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            if (!this.validateInput(input)) {
                isValid = false;
            }
        });
        
        // Validate custom rules
        const customRules = this.getCustomRules(form);
        for (const rule of customRules) {
            if (!rule.validate()) {
                isValid = false;
                this.showCustomError(form, rule.field, rule.message);
            }
        }
        
        return isValid;
    },
    
    /**
     * Get custom validation rules for a form
     * @param {HTMLFormElement} form - The form to get rules for
     * @returns {Array} Array of custom validation rules
     */
    getCustomRules: function(form) {
        const rules = [];
        
        // Password confirmation rule
        const password = form.querySelector('input[type="password"]:not([data-confirm-password])');
        const confirmPassword = form.querySelector('input[data-confirm-password]');
        
        if (password && confirmPassword) {
            rules.push({
                field: confirmPassword,
                validate: () => !confirmPassword.value || confirmPassword.value === password.value,
                message: 'Passwords do not match'
            });
        }
        
        // Email confirmation rule
        const email = form.querySelector('input[type="email"]:not([data-confirm-email])');
        const confirmEmail = form.querySelector('input[data-confirm-email]');
        
        if (email && confirmEmail) {
            rules.push({
                field: confirmEmail,
                validate: () => !confirmEmail.value || confirmEmail.value === email.value,
                message: 'Email addresses do not match'
            });
        }
        
        // Date range rule
        const startDate = form.querySelector('input[data-date-start]');
        const endDate = form.querySelector('input[data-date-end]');
        
        if (startDate && endDate) {
            rules.push({
                field: endDate,
                validate: () => {
                    if (!startDate.value || !endDate.value) return true;
                    return new Date(endDate.value) >= new Date(startDate.value);
                },
                message: 'End date must be after start date'
            });
        }
        
        // Percentage total rule
        const percentageGroup = form.querySelector('[data-percentage-group]');
        if (percentageGroup) {
            const percentageInputs = percentageGroup.querySelectorAll('input[type="number"]');
            const groupName = percentageGroup.dataset.percentageGroup;
            
            rules.push({
                field: percentageGroup,
                validate: () => {
                    let total = 0;
                    percentageInputs.forEach(input => {
                        total += parseFloat(input.value || 0);
                    });
                    return Math.abs(total - 100) < 0.01; // Allow for floating point imprecision
                },
                message: `${groupName} percentages must total 100%`
            });
        }
        
        return rules;
    },
    
    /**
     * Show a custom error message
     * @param {HTMLFormElement} form - The form containing the field
     * @param {HTMLElement} field - The field with the error
     * @param {string} message - The error message
     */
    showCustomError: function(form, field, message) {
        if (field.setCustomValidity) {
            field.setCustomValidity(message);
        }
        
        // Create or update feedback message
        let feedback;
        if (field.classList.contains('form-control')) {
            feedback = field.nextElementSibling;
            if (!feedback || !feedback.classList.contains('invalid-feedback')) {
                feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                field.parentNode.insertBefore(feedback, field.nextSibling);
            }
        } else {
            // For field groups, add feedback after the group
            feedback = field.querySelector('.invalid-feedback');
            if (!feedback) {
                feedback = document.createElement('div');
                feedback.className = 'invalid-feedback d-block';
                field.appendChild(feedback);
            }
        }
        
        feedback.textContent = message;
        
        // Add invalid class
        if (field.classList) {
            field.classList.add('is-invalid');
        }
    },
    
    /**
     * Get all form errors
     * @param {HTMLFormElement} form - The form to get errors from
     * @returns {Object} Object with field names as keys and error messages as values
     */
    getFormErrors: function(form) {
        const errors = {};
        
        // Get errors from all inputs
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            if (input.name && !input.validity.valid) {
                errors[input.name] = input.validationMessage;
            }
        });
        
        return errors;
    },
    
    /**
     * Handle input blur event
     * @param {Event} e - The blur event
     */
    handleBlur: function(e) {
        const input = e.target;
        this.validateInput(input);
    },
    
    /**
     * Handle input change event
     * @param {Event} e - The input event
     */
    handleInput: function(e) {
        const input = e.target;
        
        // Clear custom validity
        input.setCustomValidity('');
        
        // If field was previously validated, revalidate on input
        if (input.classList.contains('is-invalid') || input.classList.contains('is-valid')) {
            this.validateInput(input);
        }
    },
    
    /**
     * Validate a single input field
     * @param {HTMLInputElement|HTMLSelectElement|HTMLTextAreaElement} input - The input to validate
     * @returns {boolean} Whether the input is valid
     */
    validateInput: function(input) {
        // Skip validation if input is disabled or readonly
        if (input.disabled || input.readOnly) {
            return true;
        }
        
        // Skip validation if input is empty and not required
        if (!input.value && !input.hasAttribute('required')) {
            this.clearValidation(input);
            return true;
        }
        
        // Perform custom validation based on type and attributes
        this.performCustomValidation(input);
        
        // Check browser validation API result
        const isValid = input.validity.valid;
        
        // Update validation UI
        if (isValid) {
            input.classList.remove('is-invalid');
            if (this.config.showValidFeedback) {
                input.classList.add('is-valid');
            }
            
            // Update aria attributes
            input.setAttribute('aria-invalid', 'false');
            if (input.hasAttribute('aria-describedby')) {
                const descId = input.getAttribute('aria-describedby');
                const errorEl = document.getElementById(descId);
                if (errorEl) {
                    errorEl.textContent = '';
                }
            }
        } else {
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
            
            // Create or update feedback message
            let feedback = input.nextElementSibling;
            if (!feedback || !feedback.classList.contains('invalid-feedback')) {
                feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                input.parentNode.insertBefore(feedback, input.nextSibling);
            }
            
            feedback.textContent = input.validationMessage;
            
            // Update aria attributes
            input.setAttribute('aria-invalid', 'true');
            
            // Create unique ID for error message if needed
            if (!input.id) {
                input.id = `input-${Math.random().toString(36).substr(2, 9)}`;
            }
            
            const errorId = `${input.id}-error`;
            feedback.id = errorId;
            input.setAttribute('aria-describedby', errorId);
        }
        
        return isValid;
    },
    
    /**
     * Perform custom validation based on input type and attributes
     * @param {HTMLInputElement|HTMLSelectElement|HTMLTextAreaElement} input - The input to validate
     */
    performCustomValidation: function(input) {
        // Skip if input is empty and not required
        if (!input.value && !input.hasAttribute('required')) {
            return;
        }
        
        // Validate based on type
        switch (input.type) {
            case 'email':
                this.validateEmail(input);
                break;
                
            case 'tel':
                this.validatePhone(input);
                break;
                
            case 'number':
            case 'range':
                this.validateNumber(input);
                break;
                
            case 'password':
                this.validatePassword(input);
                break;
                
            case 'url':
                this.validateUrl(input);
                break;
                
            case 'date':
            case 'datetime-local':
                this.validateDate(input);
                break;
        }
        
        // Validate based on attributes
        if (input.hasAttribute('pattern')) {
            this.validatePattern(input);
        }
        
        if (input.hasAttribute('minlength') || input.hasAttribute('maxlength')) {
            this.validateLength(input);
        }
        
        // Validate based on data attributes
        if (input.dataset.validate) {
            switch (input.dataset.validate) {
                case 'currency':
                    this.validateCurrency(input);
                    break;
                    
                case 'percentage':
                    this.validatePercentage(input);
                    break;
                    
                case 'zipcode':
                    this.validateZipCode(input);
                    break;
                    
                case 'creditcard':
                    this.validateCreditCard(input);
                    break;
            }
        }
    },
    
    /**
     * Validate email format
     * @param {HTMLInputElement} input - The email input
     */
    validateEmail: function(input) {
        if (!input.value) return;
        
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(input.value)) {
            input.setCustomValidity('Please enter a valid email address');
        } else {
            input.setCustomValidity('');
        }
    },
    
    /**
     * Validate phone number format
     * @param {HTMLInputElement} input - The phone input
     */
    validatePhone: function(input) {
        if (!input.value) return;
        
        // Allow various phone formats with optional country code
        const phoneRegex = /^\+?[0-9\s\-()]{10,20}$/;
        if (!phoneRegex.test(input.value)) {
            input.setCustomValidity('Please enter a valid phone number');
        } else {
            input.setCustomValidity('');
        }
    },
    
    /**
     * Validate number input
     * @param {HTMLInputElement} input - The number input
     */
    validateNumber: function(input) {
        if (!input.value) return;
        
        const value = parseFloat(input.value);
        const min = parseFloat(input.min);
        const max = parseFloat(input.max);
        const step = parseFloat(input.step) || 1;
        
        if (isNaN(value)) {
            input.setCustomValidity('Please enter a valid number');
            return;
        }
        
        if (!isNaN(min) && value < min) {
            input.setCustomValidity(`Value must be at least ${min}`);
            return;
        }
        
        if (!isNaN(max) && value > max) {
            input.setCustomValidity(`Value must be at most ${max}`);
            return;
        }
        
        // Check if value adheres to step
        if (step !== 'any' && !isNaN(step)) {
            const baseValue = isNaN(min) ? 0 : min;
            const remainder = Math.abs((value - baseValue) % step);
            
            if (remainder > 0.00001 && remainder < step - 0.00001) {
                input.setCustomValidity(`Value must be in increments of ${step}`);
                return;
            }
        }
        
        input.setCustomValidity('');
    },
    
    /**
     * Validate password strength
     * @param {HTMLInputElement} input - The password input
     */
    validatePassword: function(input) {
        if (!input.value) return;
        
        // Skip if no strength requirements are specified
        if (!input.dataset.passwordStrength) return;
        
        const strength = input.dataset.passwordStrength || 'medium';
        let regex;
        let message;
        
        switch (strength) {
            case 'strong':
                // At least 8 chars, uppercase, lowercase, number, and special char
                regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
                message = 'Password must be at least 8 characters and include uppercase, lowercase, number, and special character';
                break;
                
            case 'medium':
                // At least 8 chars, uppercase, lowercase, and number
                regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$/;
                message = 'Password must be at least 8 characters and include uppercase, lowercase, and number';
                break;
                
            case 'weak':
                // At least 6 chars
                regex = /^.{6,}$/;
                message = 'Password must be at least 6 characters';
                break;
                
            default:
                // Custom regex from data attribute
                try {
                    regex = new RegExp(strength);
                    message = input.dataset.passwordMessage || 'Password does not meet requirements';
                } catch (e) {
                    console.error('Invalid password regex:', e);
                    return;
                }
        }
        
        if (!regex.test(input.value)) {
            input.setCustomValidity(message);
        } else {
            input.setCustomValidity('');
        }
    },
    
    /**
     * Validate URL format
     * @param {HTMLInputElement} input - The URL input
     */
    validateUrl: function(input) {
        if (!input.value) return;
        
        try {
            new URL(input.value);
            input.setCustomValidity('');
        } catch (e) {
            input.setCustomValidity('Please enter a valid URL');
        }
    },
    
    /**
     * Validate date input
     * @param {HTMLInputElement} input - The date input
     */
    validateDate: function(input) {
        if (!input.value) return;
        
        const date = new Date(input.value);
        if (isNaN(date.getTime())) {
            input.setCustomValidity('Please enter a valid date');
            return;
        }
        
        // Check min date
        if (input.min) {
            const minDate = new Date(input.min);
            if (date < minDate) {
                input.setCustomValidity(`Date must be on or after ${input.min}`);
                return;
            }
        }
        
        // Check max date
        if (input.max) {
            const maxDate = new Date(input.max);
            if (date > maxDate) {
                input.setCustomValidity(`Date must be on or before ${input.max}`);
                return;
            }
        }
        
        input.setCustomValidity('');
    },
    
    /**
     * Validate input against pattern
     * @param {HTMLInputElement} input - The input with pattern
     */
    validatePattern: function(input) {
        if (!input.value) return;
        
        const pattern = new RegExp(input.pattern);
        if (!pattern.test(input.value)) {
            const message = input.dataset.patternMessage || 'Please match the requested format';
            input.setCustomValidity(message);
        } else {
            input.setCustomValidity('');
        }
    },
    
    /**
     * Validate input length
     * @param {HTMLInputElement|HTMLTextAreaElement} input - The input to validate
     */
    validateLength: function(input) {
        if (!input.value) return;
        
        const minLength = parseInt(input.getAttribute('minlength'));
        const maxLength = parseInt(input.getAttribute('maxlength'));
        
        if (!isNaN(minLength) && input.value.length < minLength) {
            input.setCustomValidity(`Please enter at least ${minLength} characters`);
            return;
        }
        
        if (!isNaN(maxLength) && input.value.length > maxLength) {
            input.setCustomValidity(`Please enter no more than ${maxLength} characters`);
            return;
        }
        
        input.setCustomValidity('');
    },
    
    /**
     * Validate currency format
     * @param {HTMLInputElement} input - The currency input
     */
    validateCurrency: function(input) {
        if (!input.value) return;
        
        const currencyRegex = /^-?\$?([0-9]{1,3},([0-9]{3},)*[0-9]{3}|[0-9]+)(\.[0-9]{1,2})?$/;
        if (!currencyRegex.test(input.value)) {
            input.setCustomValidity('Please enter a valid currency amount');
        } else {
            input.setCustomValidity('');
        }
    },
    
    /**
     * Validate percentage format
     * @param {HTMLInputElement} input - The percentage input
     */
    validatePercentage: function(input) {
        if (!input.value) return;
        
        const value = parseFloat(input.value);
        if (isNaN(value)) {
            input.setCustomValidity('Please enter a valid percentage');
            return;
        }
        
        const min = parseFloat(input.min || 0);
        const max = parseFloat(input.max || 100);
        
        if (value < min) {
            input.setCustomValidity(`Percentage must be at least ${min}%`);
            return;
        }
        
        if (value > max) {
            input.setCustomValidity(`Percentage must be at most ${max}%`);
            return;
        }
        
        input.setCustomValidity('');
    },
    
    /**
     * Validate ZIP code format
     * @param {HTMLInputElement} input - The ZIP code input
     */
    validateZipCode: function(input) {
        if (!input.value) return;
        
        // US ZIP code format (5 digits or 5+4)
        const zipRegex = /^\d{5}(-\d{4})?$/;
        if (!zipRegex.test(input.value)) {
            input.setCustomValidity('Please enter a valid ZIP code');
        } else {
            input.setCustomValidity('');
        }
    },
    
    /**
     * Validate credit card number format and checksum
     * @param {HTMLInputElement} input - The credit card input
     */
    validateCreditCard: function(input) {
        if (!input.value) return;
        
        // Remove spaces and dashes
        const cardNumber = input.value.replace(/[\s-]/g, '');
        
        // Check if it contains only digits
        if (!/^\d+$/.test(cardNumber)) {
            input.setCustomValidity('Credit card number can only contain digits');
            return;
        }
        
        // Check length (13-19 digits for most cards)
        if (cardNumber.length < 13 || cardNumber.length > 19) {
            input.setCustomValidity('Credit card number must be between 13 and 19 digits');
            return;
        }
        
        // Luhn algorithm (checksum)
        let sum = 0;
        let shouldDouble = false;
        
        for (let i = cardNumber.length - 1; i >= 0; i--) {
            let digit = parseInt(cardNumber.charAt(i));
            
            if (shouldDouble) {
                digit *= 2;
                if (digit > 9) {
                    digit -= 9;
                }
            }
            
            sum += digit;
            shouldDouble = !shouldDouble;
        }
        
        if (sum % 10 !== 0) {
            input.setCustomValidity('Please enter a valid credit card number');
            return;
        }
        
        input.setCustomValidity('');
    },
    
    /**
     * Clear validation state for an input
     * @param {HTMLInputElement|HTMLSelectElement|HTMLTextAreaElement} input - The input to clear
     */
    clearValidation: function(input) {
        input.setCustomValidity('');
        input.classList.remove('is-invalid');
        input.classList.remove('is-valid');
        
        // Remove feedback messages
        const feedback = input.nextElementSibling;
        if (feedback && (feedback.classList.contains('invalid-feedback') || feedback.classList.contains('valid-feedback'))) {
            feedback.textContent = '';
        }
    },
    
    /**
     * Handle AJAX form submission
     * @param {HTMLFormElement} form - The form to submit
     */
    async handleAjaxSubmit(form) {
        try {
            const submitButton = form.querySelector('[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Submitting...';
            }
            
            const formData = new FormData(form);
            const url = form.action;
            const method = form.method.toUpperCase();
            
            // Convert FormData to JSON if needed
            let body;
            if (form.dataset.format === 'json') {
                const data = {};
                formData.forEach((value, key) => {
                    data[key] = value;
                });
                body = JSON.stringify(data);
            } else {
                body = formData;
            }
            
            const response = await fetch(url, {
                method,
                body,
                headers: form.dataset.format === 'json' ? {
                    'Content-Type': 'application/json'
                } : {},
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                if (window.showSuccess) {
                    window.showSuccess(result.message || 'Form submitted successfully');
                }
                
                // Handle redirect if specified
                if (result.redirect) {
                    window.location.href = result.redirect;
                    return;
                }
                
                // Handle form reset if specified
                if (form.dataset.resetOnSuccess === 'true') {
                    form.reset();
                    form.classList.remove('was-validated');
                    
                    // Clear validation state
                    const inputs = form.querySelectorAll('input, select, textarea');
                    inputs.forEach(input => this.clearValidation(input));
                }
                
                // Trigger success event
                form.dispatchEvent(new CustomEvent('form:success', {
                    detail: result
                }));
            } else {
                if (window.showError) {
                    window.showError(result.message || 'Form submission failed');
                }
                
                // Handle field errors
                if (result.errors) {
                    Object.entries(result.errors).forEach(([field, error]) => {
                        const input = form.querySelector(`[name="${field}"]`);
                        if (input) {
                            input.setCustomValidity(error);
                            this.validateInput(input);
                        }
                    });
                    
                    // Focus first invalid field
                    const firstInvalid = form.querySelector('.is-invalid');
                    if (firstInvalid) {
                        firstInvalid.focus();
                    }
                }
                
                // Trigger error event
                form.dispatchEvent(new CustomEvent('form:error', {
                    detail: result
                }));
            }
        } catch (error) {
            console.error('Error submitting form:', error);
            if (window.showError) {
                window.showError('Error submitting form: ' + error.message);
            }
            
            // Trigger error event
            form.dispatchEvent(new CustomEvent('form:error', {
                detail: { error: error.message }
            }));
        } finally {
            // Re-enable submit button
            const submitButton = form.querySelector('[type="submit"]');
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.innerHTML = submitButton.dataset.originalText || 'Submit';
            }
        }
    }
};

// Register the module with REITracker namespace
if (typeof window.REITracker !== 'undefined') {
    window.REITracker.modules = window.REITracker.modules || {};
    window.REITracker.modules.formValidator = formValidatorModule;
}

// For ES6 module support
if (typeof module !== 'undefined' && module.exports) {
    module.exports = formValidatorModule;
}
