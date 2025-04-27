/**
 * Password validation and UI enhancement module for the REI-Tracker application.
 * 
 * This module provides functionality for password strength validation,
 * visual feedback, and password visibility toggle.
 */

const passwordValidator = {
    /**
     * Initialize the password validator.
     * 
     * @param {string} passwordInputId - The ID of the password input element
     * @param {string} confirmPasswordInputId - The ID of the confirm password input element
     * @param {string} requirementsId - The ID of the element to display password requirements
     * @param {string} strengthId - The ID of the element to display password strength
     */
    init: function(passwordInputId, confirmPasswordInputId, requirementsId, strengthId) {
        this.passwordInput = document.getElementById(passwordInputId);
        this.confirmPasswordInput = document.getElementById(confirmPasswordInputId);
        this.requirementsElement = document.getElementById(requirementsId);
        this.strengthElement = document.getElementById(strengthId);
        
        if (this.passwordInput) {
            // Add input event listener for real-time validation
            this.passwordInput.addEventListener('input', () => {
                this.updatePasswordStrength();
                this.validatePasswordRequirements();
                this.checkPasswordMatch();
            });
            
            // Add password visibility toggle
            this.addPasswordToggle(this.passwordInput);
        }
        
        if (this.confirmPasswordInput) {
            this.confirmPasswordInput.addEventListener('input', () => {
                this.checkPasswordMatch();
            });
            
            // Add password visibility toggle
            this.addPasswordToggle(this.confirmPasswordInput);
        }
        
        // Initialize requirements display
        this.displayRequirements();
        // Initial strength check
        this.updatePasswordStrength();
    },
    
    /**
     * Password requirements definition.
     */
    requirements: {
        length: { test: (pwd) => pwd.length >= 8, message: 'At least 8 characters' },
        uppercase: { test: (pwd) => /[A-Z]/.test(pwd), message: 'At least one uppercase letter' },
        lowercase: { test: (pwd) => /[a-z]/.test(pwd), message: 'At least one lowercase letter' },
        number: { test: (pwd) => /\d/.test(pwd), message: 'At least one number' },
        special: { 
            test: (pwd) => /[!@#$%^&*(),.?":{}|<>]/.test(pwd), 
            message: 'At least one special character (!@#$%^&*(),.?":{}|<>)'
        }
    },
    
    /**
     * Display password requirements in the UI.
     */
    displayRequirements: function() {
        if (!this.requirementsElement) {
            console.error('Requirements element not found');
            return;
        }
        
        const reqList = document.createElement('ul');
        reqList.className = 'list-group password-requirements';
        
        Object.entries(this.requirements).forEach(([key, req]) => {
            const li = document.createElement('li');
            li.className = 'list-group-item d-flex align-items-center requirement-item';
            li.id = `req-${key}`;
            
            const icon = document.createElement('i');
            icon.className = 'bi bi-x-circle text-danger me-2';
            
            const text = document.createElement('span');
            text.textContent = req.message;
            
            li.appendChild(icon);
            li.appendChild(text);
            reqList.appendChild(li);
        });
        
        this.requirementsElement.innerHTML = ''; // Clear existing content
        this.requirementsElement.appendChild(reqList);
    },
    
    /**
     * Validate password requirements and update UI.
     * 
     * @returns {number} The number of requirements met
     */
    validatePasswordRequirements: function() {
        if (!this.passwordInput) {
            console.error('Password input not found');
            return 0;
        }
        
        const password = this.passwordInput.value;
        let metRequirements = 0;
        
        Object.entries(this.requirements).forEach(([key, req]) => {
            const reqElement = document.getElementById(`req-${key}`);
            if (!reqElement) return;
            
            const icon = reqElement.querySelector('i');
            if (!icon) return;
            
            if (req.test(password)) {
                icon.className = 'bi bi-check-circle text-success me-2';
                reqElement.classList.add('requirement-met');
                metRequirements++;
            } else {
                icon.className = 'bi bi-x-circle text-danger me-2';
                reqElement.classList.remove('requirement-met');
            }
        });
        
        return metRequirements;
    },
    
    /**
     * Calculate password strength score.
     * 
     * @param {string} password - The password to evaluate
     * @returns {number} The strength score (0-10)
     */
    calculatePasswordStrength: function(password) {
        if (!password) return 0;
        
        let score = 0;
        
        // Base length points
        if (password.length >= 12) score += 2;
        else if (password.length >= 8) score += 1;
        
        // Character type points
        if (/[A-Z]/.test(password)) score += 1;
        if (/[a-z]/.test(password)) score += 1;
        if (/\d/.test(password)) score += 1;
        if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) score += 1;
        
        // Additional complexity points
        if (password.length >= 16) score += 1;
        if (/[^A-Za-z0-9]/.test(password)) score += 1;
        if (new Set(password).size >= 8) score += 1; // Unique characters
        
        return score;
    },
    
    /**
     * Update password strength meter in the UI.
     */
    updatePasswordStrength: function() {
        if (!this.passwordInput || !this.strengthElement) {
            console.error('Required elements not found');
            return;
        }
        
        const password = this.passwordInput.value;
        const score = this.calculatePasswordStrength(password);
        
        // Update strength meter
        const strengthBar = this.strengthElement.querySelector('.progress-bar');
        const strengthText = this.strengthElement.querySelector('.strength-text');
        
        if (strengthBar && strengthText) {
            let percentage, strengthClass, strengthLabel;
            
            if (score >= 7) {
                percentage = 100;
                strengthClass = 'bg-success';
                strengthLabel = 'Strong';
            } else if (score >= 5) {
                percentage = 70;
                strengthClass = 'bg-info';
                strengthLabel = 'Good';
            } else if (score >= 3) {
                percentage = 40;
                strengthClass = 'bg-warning';
                strengthLabel = 'Moderate';
            } else {
                percentage = 20;
                strengthClass = 'bg-danger';
                strengthLabel = 'Weak';
            }
            
            strengthBar.style.width = `${percentage}%`;
            strengthBar.className = `progress-bar ${strengthClass}`;
            strengthText.textContent = strengthLabel;
        }
    },
    
    /**
     * Check if passwords match and update UI.
     */
    checkPasswordMatch: function() {
        if (!this.passwordInput || !this.confirmPasswordInput) {
            console.error('Password inputs not found');
            return;
        }
        
        const password = this.passwordInput.value;
        const confirmPassword = this.confirmPasswordInput.value;
        
        const matchMessage = document.getElementById('password-match-message');
        if (matchMessage) {
            if (confirmPassword) {
                if (password === confirmPassword) {
                    matchMessage.textContent = 'Passwords match';
                    matchMessage.className = 'text-success';
                } else {
                    matchMessage.textContent = 'Passwords do not match';
                    matchMessage.className = 'text-danger';
                }
            } else {
                matchMessage.textContent = '';
            }
        }
    },
    
    /**
     * Add password visibility toggle to a password input.
     * 
     * @param {HTMLElement} inputElement - The password input element
     */
    addPasswordToggle: function(inputElement) {
        if (!inputElement) return;
        
        // Create wrapper if not already in one
        let wrapper = inputElement.parentElement;
        if (!wrapper.classList.contains('password-wrapper')) {
            wrapper = document.createElement('div');
            wrapper.className = 'password-wrapper position-relative';
            inputElement.parentNode.insertBefore(wrapper, inputElement);
            wrapper.appendChild(inputElement);
        }
        
        // Create toggle button
        const toggleBtn = document.createElement('button');
        toggleBtn.type = 'button';
        toggleBtn.className = 'btn btn-link position-absolute end-0 top-50 translate-middle-y text-decoration-none';
        toggleBtn.style.zIndex = '10';
        toggleBtn.innerHTML = '<i class="bi bi-eye"></i>';
        toggleBtn.setAttribute('aria-label', 'Toggle password visibility');
        
        // Add click event
        toggleBtn.addEventListener('click', function() {
            const type = inputElement.getAttribute('type') === 'password' ? 'text' : 'password';
            inputElement.setAttribute('type', type);
            
            // Update icon
            const icon = toggleBtn.querySelector('i');
            if (type === 'text') {
                icon.className = 'bi bi-eye-slash';
            } else {
                icon.className = 'bi bi-eye';
            }
        });
        
        wrapper.appendChild(toggleBtn);
    }
};

export default passwordValidator;
