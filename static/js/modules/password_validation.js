// static/js/password-validation.js

const passwordValidator = {
    init: function(passwordInputId, confirmPasswordInputId, requirementsId, strengthId) {
        this.passwordInput = document.getElementById(passwordInputId);
        this.confirmPasswordInput = document.getElementById(confirmPasswordInputId);
        this.requirementsElement = document.getElementById(requirementsId);
        this.strengthElement = document.getElementById(strengthId);
        
        if (this.passwordInput) {
            // Add input event listener for real-time validation
            this.passwordInput.addEventListener('input', () => {
                console.log('Password input changed'); // Debug log
                this.updatePasswordStrength();
                this.validatePasswordRequirements();
                this.checkPasswordMatch();
            });
        }
        
        if (this.confirmPasswordInput) {
            this.confirmPasswordInput.addEventListener('input', () => {
                this.checkPasswordMatch();
            });
        }
        
        // Initialize requirements display
        this.displayRequirements();
        // Initial strength check
        this.updatePasswordStrength();
    },
    
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
    
    validatePasswordRequirements: function() {
        if (!this.passwordInput) {
            console.error('Password input not found');
            return;
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
        
        console.log('Password strength score:', score); // Debug log
        return score;
    },
    
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
            console.log('Updating strength bar'); // Debug log
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
    }
};

export default passwordValidator;