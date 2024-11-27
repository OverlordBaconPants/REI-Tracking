// /static/js/modules/auth.js

const authModule = {
    init: async function() {
        console.log('Initializing auth module');
        try {
            await this.initializePasswordValidation();
            this.setupFormValidation();
            this.setupPasswordStrengthMeter();
            console.log('Auth module initialized successfully');
        } catch (error) {
            console.error('Error initializing auth module:', error);
        }
    },

    initializePasswordValidation: async function() {
        try {
            // Import the password validator module
            const passwordValidator = await import('./password_validation.js');
            
            // Initialize password validation if we're on a page with password fields
            const passwordInput = document.getElementById('password');
            const confirmPasswordInput = document.getElementById('confirm_password');
            const requirementsElement = document.getElementById('password-requirements');
            const strengthElement = document.getElementById('password-strength');
            
            if (passwordInput && requirementsElement) {
                passwordValidator.default.init(
                    'password',
                    'confirm_password',
                    'password-requirements',
                    'password-strength'
                );
            }
        } catch (error) {
            console.error('Error initializing password validation:', error);
        }
    },

    setupFormValidation: function() {
        const form = document.querySelector('form');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (this.validateForm(form)) {
                // Store the submit button reference
                const submitButton = form.querySelector('button[type="submit"]');
                const originalText = submitButton?.innerHTML || 'Submit';
                
                try {
                    // Update button state
                    if (submitButton) {
                        submitButton.disabled = true;
                        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
                    }

                    // Submit the form
                    const response = await fetch(form.action, {
                        method: form.method,
                        body: new FormData(form),
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    });

                    const data = await response.json();

                    if (data.success) {
                        window.showNotification(data.message || 'Success!', 'success');
                        if (data.redirect) {
                            setTimeout(() => {
                                window.location.href = data.redirect;
                            }, 1500);
                        }
                    } else {
                        throw new Error(data.message || 'An error occurred');
                    }
                } catch (error) {
                    console.error('Form submission error:', error);
                    window.showNotification(error.message || 'An error occurred. Please try again.', 'error');
                    
                    // Re-enable the submit button
                    if (submitButton) {
                        submitButton.disabled = false;
                        submitButton.innerHTML = originalText;
                    }
                }
            }
        });
    },

    validateForm: function(form) {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');

        // Remove any existing error messages
        form.querySelectorAll('.invalid-feedback').forEach(el => el.remove());
        form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));

        // Check each required field
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                field.classList.add('is-invalid');
                
                // Add error message
                const errorDiv = document.createElement('div');
                errorDiv.className = 'invalid-feedback';
                errorDiv.textContent = 'This field is required';
                field.parentNode.appendChild(errorDiv);
            }
        });

        // Email validation
        const emailField = form.querySelector('input[type="email"]');
        if (emailField && emailField.value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(emailField.value)) {
                isValid = false;
                emailField.classList.add('is-invalid');
                
                const errorDiv = document.createElement('div');
                errorDiv.className = 'invalid-feedback';
                errorDiv.textContent = 'Please enter a valid email address';
                emailField.parentNode.appendChild(errorDiv);
            }
        }

        // Password validation for signup/reset
        const passwordField = form.querySelector('input[name="password"]');
        const confirmPasswordField = form.querySelector('input[name="confirm_password"]');
        if (passwordField && confirmPasswordField) {
            if (passwordField.value !== confirmPasswordField.value) {
                isValid = false;
                confirmPasswordField.classList.add('is-invalid');
                
                const errorDiv = document.createElement('div');
                errorDiv.className = 'invalid-feedback';
                errorDiv.textContent = 'Passwords do not match';
                confirmPasswordField.parentNode.appendChild(errorDiv);
            }
        }

        return isValid;
    },

    setupPasswordStrengthMeter: function() {
        const passwordInput = document.getElementById('password');
        const strengthMeter = document.querySelector('.progress-bar');
        const strengthText = document.querySelector('.strength-text');
        
        if (!passwordInput || !strengthMeter || !strengthText) return;

        passwordInput.addEventListener('input', () => {
            const strength = this.calculatePasswordStrength(passwordInput.value);
            
            // Update progress bar
            strengthMeter.style.width = `${strength.score}%`;
            strengthMeter.className = `progress-bar ${strength.class}`;
            
            // Update text
            strengthText.textContent = strength.label;
        });
    },

    setupFormValidation: function() {
        const form = document.querySelector('form');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (this.validateForm(form)) {
                // Store the submit button reference
                const submitButton = form.querySelector('button[type="submit"]');
                const originalText = submitButton?.innerHTML || 'Submit';
                
                try {
                    // Update button state
                    if (submitButton) {
                        submitButton.disabled = true;
                        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
                    }

                    // Submit the form
                    const response = await fetch(form.action, {
                        method: form.method,
                        body: new FormData(form),
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    });

                    // Check if the response redirects (success case)
                    if (response.redirected) {
                        window.location.href = response.url;
                        return;
                    }

                    // Check content type
                    const contentType = response.headers.get('content-type');
                    if (contentType && contentType.includes('application/json')) {
                        // Handle JSON response
                        const data = await response.json();
                        if (data.success) {
                            window.showNotification(data.message || 'Success!', 'success');
                            if (data.redirect) {
                                setTimeout(() => {
                                    window.location.href = data.redirect;
                                }, 1500);
                            }
                        } else {
                            throw new Error(data.message || 'An error occurred');
                        }
                    } else {
                        // Handle non-JSON response (likely HTML)
                        const text = await response.text();
                        
                        // Check if it's a successful response with redirect
                        if (response.ok) {
                            // If there's a success message in a data attribute or similar
                            const successMsg = form.dataset.successMessage || 'Success!';
                            window.showNotification(successMsg, 'success');
                            
                            // Allow the form's natural submission to handle redirect
                            setTimeout(() => {
                                form.submit();
                            }, 1500);
                        } else {
                            // Extract error message from HTML if possible
                            let errorMsg = 'An error occurred';
                            const errorElement = new DOMParser()
                                .parseFromString(text, 'text/html')
                                .querySelector('.alert-danger');
                            
                            if (errorElement) {
                                errorMsg = errorElement.textContent.trim();
                            }
                            throw new Error(errorMsg);
                        }
                    }
                } catch (error) {
                    console.error('Form submission error:', error);
                    window.showNotification(error.message || 'An error occurred. Please try again.', 'error');
                    
                    // Re-enable the submit button
                    if (submitButton) {
                        submitButton.disabled = false;
                        submitButton.innerHTML = originalText;
                    }
                }
            }
        });
    },

    calculatePasswordStrength: function(password) {
        if (!password) {
            return { score: 0, label: 'Not set', class: 'bg-secondary' };
        }

        let score = 0;
        
        // Length check
        if (password.length >= 12) score += 25;
        else if (password.length >= 8) score += 15;
        
        // Complexity checks
        if (/[A-Z]/.test(password)) score += 15;
        if (/[a-z]/.test(password)) score += 15;
        if (/[0-9]/.test(password)) score += 15;
        if (/[^A-Za-z0-9]/.test(password)) score += 15;
        
        // Additional complexity
        if (password.length >= 16) score += 15;

        // Cap at 100
        score = Math.min(score, 100);

        // Determine label and class
        if (score >= 80) {
            return { score, label: 'Strong', class: 'bg-success' };
        } else if (score >= 60) {
            return { score, label: 'Good', class: 'bg-info' };
        } else if (score >= 40) {
            return { score, label: 'Moderate', class: 'bg-warning' };
        } else {
            return { score, label: 'Weak', class: 'bg-danger' };
        }
    }
};

export default authModule;