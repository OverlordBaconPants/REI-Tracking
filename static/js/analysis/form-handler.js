// form-handler.js
import UIHelpers from './ui-helpers.js';
import AnalysisCore from './core.js';

const FormHandler = {
    isSubmitting: false,
    
    validateNumericRange(value, min, max = Infinity) {
        const num = AnalysisCore.toRawNumber(value);
        return !isNaN(num) && num >= min && num <= max;
    },
    
    validateRequiredFields(form) {
        let isValid = true;
        
        const requiredFields = form.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                field.classList.add('is-invalid');
                this.addErrorMessage(field, 'This field is required');
            } else {
                field.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    },
    
    validatePercentageFields(form, fields) {
        let isValid = true;
        
        fields.forEach(fieldName => {
            const field = form.querySelector(`#${fieldName}`);
            if (field && field.value.trim()) {
                if (!this.validateNumericRange(field.value, 0, 100)) {
                    isValid = false;
                    field.classList.add('is-invalid');
                    this.addErrorMessage(field, 'Value must be between 0 and 100%');
                } else {
                    field.classList.remove('is-invalid');
                }
            }
        });
        
        return isValid;
    },
    
    addErrorMessage(field, message) {
        let errorDiv = field.nextElementSibling;
        if (!errorDiv || !errorDiv.classList.contains('invalid-feedback')) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            field.parentNode.insertBefore(errorDiv, field.nextSibling);
        }
        errorDiv.textContent = message;
    },
    
    submitForm(form, analysisId = null) {
        if (this.isSubmitting) {
            return Promise.reject(new Error('Form submission already in progress'));
        }
        
        this.isSubmitting = true;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        UIHelpers.setButtonLoading(submitBtn, true, analysisId ? 'Update Analysis' : 'Create Analysis');
        
        // Create form data
        const formData = new FormData(form);
        const analysisData = Object.fromEntries(formData.entries());
        
        // If editing, add ID
        if (analysisId) {
            analysisData.id = analysisId;
        }
        
        // Make API call
        const endpoint = analysisId ? '/analyses/update_analysis' : '/analyses/create_analysis';
        
        return fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(analysisData)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw err; });
            }
            return response.json();
        })
        .finally(() => {
            this.isSubmitting = false;
            UIHelpers.setButtonLoading(submitBtn, false, analysisId ? 'Update Analysis' : 'Create Analysis');
        });
    }
};

export default FormHandler;