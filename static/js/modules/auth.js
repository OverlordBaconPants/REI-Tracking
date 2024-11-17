// /static/js/modules/auth.js

const authModule = {
    init: async function() {
        console.log('Initializing auth module');
        try {
            await this.initializePasswordValidation();
            this.setupFormValidation();
            this.setupPasswordStrengthMeter();
            this.setupPasswordToggle();
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

        // Remove any existing event listeners
        const newForm = form.cloneNode(true);
        form.parentNode.replaceChild(newForm, form);
        
        newForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (this.validateForm(newForm)) {
                const submitButton = newForm.querySelector('button[type="submit"]');
                const originalText = submitButton?.innerHTML || 'Submit';
                
                try {
                    if (submitButton) {
                        submitButton.disabled = true;
                        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
                    }

                    const response = await fetch(newForm.action, {
                        method: newForm.method,
                        body: new FormData(newForm),
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    });

                    const text = await response.text();
                    
                    // Check if login was successful
                    if (text.includes('Logged in successfully')) {
                        // Clean up before redirect
                        const cleanupAndRedirect = () => {
                            // Remove all event listeners from the form
                            newForm.replaceWith(newForm.cloneNode(true));
                            
                            // Remove toastr containers
                            const toastrContainers = document.querySelectorAll('#toast-container, #toastr-top');
                            toastrContainers.forEach(container => {
                                if (container && container.parentNode) {
                                    container.parentNode.removeChild(container);
                                }
                            });

                            // Remove any bootstrap components
                            const bootstrapElements = document.querySelectorAll('[data-bs-toggle]');
                            bootstrapElements.forEach(element => {
                                const tooltip = bootstrap.Tooltip.getInstance(element);
                                if (tooltip) {
                                    tooltip.dispose();
                                }
                                const popover = bootstrap.Popover.getInstance(element);
                                if (popover) {
                                    popover.dispose();
                                }
                            });

                            // Parse the URL from the response
                            const parser = new DOMParser();
                            const doc = parser.parseFromString(text, 'text/html');
                            const redirectMeta = doc.querySelector('meta[http-equiv="refresh"]');
                            const redirectUrl = redirectMeta ? 
                                redirectMeta.content.split('URL=')[1] : 
                                '/';

                            // Navigate to new page
                            window.location.assign(redirectUrl);
                        };

                        // Show success notification and redirect
                        window.showNotification('Logged in successfully.', 'success', 'both');
                        setTimeout(cleanupAndRedirect, 1000);
                    } else {
                        // Handle error responses
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(text, 'text/html');
                        const errorMessages = Array.from(doc.querySelectorAll('.alert-danger, .error-message'))
                            .map(el => el.textContent.trim())
                            .filter(msg => msg);

                        if (errorMessages.length > 0) {
                            window.showNotification(errorMessages[0], 'error', 'both');
                        } else if (text.includes('error')) {
                            window.showNotification('An error occurred during login.', 'error', 'both');
                        }
                        
                        // Update the page content
                        document.body.innerHTML = text;
                        // Reinitialize components
                        if (window.mainInit) {
                            window.mainInit();
                        }
                    }
                } catch (error) {
                    console.error('Form submission error:', error);
                    window.showNotification('An error occurred. Please try again.', 'error', 'both');
                } finally {
                    // Reset button state if not redirecting
                    if (!text?.includes('Logged in successfully')) {
                        if (submitButton) {
                            submitButton.disabled = false;
                            submitButton.innerHTML = originalText;
                        }
                    }
                }
            }
        });
    },

    setupPasswordToggle: function() {
        const passwordFields = document.querySelectorAll('input[type="password"]');
        
        passwordFields.forEach(passwordField => {
            // Create wrapper div if it doesn't exist
            let wrapper = passwordField.parentElement;
            if (!wrapper.classList.contains('password-toggle-wrapper')) {
                wrapper = document.createElement('div');
                wrapper.className = 'password-toggle-wrapper position-relative';
                passwordField.parentNode.insertBefore(wrapper, passwordField);
                wrapper.appendChild(passwordField);
            }

            // Create and add toggle button
            const toggleBtn = document.createElement('button');
            toggleBtn.type = 'button';
            toggleBtn.className = 'btn btn-link position-absolute top-50 end-0 translate-middle-y text-decoration-none pe-2';
            toggleBtn.style.zIndex = '10';
            toggleBtn.innerHTML = '<i class="bi bi-eye-slash"></i>';
            
            // Add aria label for accessibility
            toggleBtn.setAttribute('aria-label', 'Toggle password visibility');
            
            // Add click handler
            toggleBtn.addEventListener('click', (e) => {
                e.preventDefault();
                const icon = toggleBtn.querySelector('i');
                if (passwordField.type === 'password') {
                    passwordField.type = 'text';
                    icon.className = 'bi bi-eye';
                    toggleBtn.setAttribute('aria-label', 'Hide password');
                } else {
                    passwordField.type = 'password';
                    icon.className = 'bi bi-eye-slash';
                    toggleBtn.setAttribute('aria-label', 'Show password');
                }
                // Maintain focus on the password field
                passwordField.focus();
            });
            
            wrapper.appendChild(toggleBtn);
            
            // Adjust the password field's padding to prevent overlap
            passwordField.style.paddingRight = '2.5rem';
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