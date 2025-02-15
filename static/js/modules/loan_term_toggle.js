// loan_term_toggle.js

const LoanTermToggleModule = {
    init: function(primaryTermId, secondaryTermId) {
        // Add a small delay to ensure DOM elements are ready
        setTimeout(() => {
            this.initToggle(primaryTermId);
            if (secondaryTermId) {
                this.initToggle(secondaryTermId);
            }
        }, 0);
    },

    initToggle: function(termId) {
        const container = document.getElementById(`${termId}-container`);
        if (!container) {
            console.warn(`Container for ${termId} not found, will try again later`);
            // Add retry logic
            setTimeout(() => this.initToggle(termId), 100);
            return;
        }

        const yearInput = document.getElementById(`${termId}-years`);
        const monthInput = document.getElementById(`${termId}-months`);
        const toggleBtn = document.getElementById(`${termId}-toggle`);

        if (!yearInput || !monthInput || !toggleBtn) {
            console.warn(`Required elements for ${termId} not found, will try again later`);
            setTimeout(() => this.initToggle(termId), 100);
            return;
        }

        // Initialize with years view
        yearInput.style.display = 'block';
        monthInput.style.display = 'none';
        toggleBtn.textContent = 'Switch to Months';

        // Set up event listeners
        toggleBtn.addEventListener('click', () => {
            const isYearsView = yearInput.style.display === 'block';
            
            // Toggle visibility
            yearInput.style.display = isYearsView ? 'none' : 'block';
            monthInput.style.display = isYearsView ? 'block' : 'none';
            toggleBtn.textContent = isYearsView ? 'Switch to Years' : 'Switch to Months';

            // Convert and update value
            if (isYearsView) {
                // Converting from years to months
                const years = parseFloat(yearInput.value) || 0;
                monthInput.value = (years * 12).toString();
            } else {
                // Converting from months to years
                const months = parseFloat(monthInput.value) || 0;
                yearInput.value = (months / 12).toString();
            }
        });

        // Handle input changes
        yearInput.addEventListener('input', () => {
            const years = parseFloat(yearInput.value) || 0;
            monthInput.value = (years * 12).toString();
        });

        monthInput.addEventListener('input', () => {
            const months = parseFloat(monthInput.value) || 0;
            yearInput.value = (months / 12).toString();
        });
    },

    getValueInMonths: function(termId) {
        const yearInput = document.getElementById(`${termId}-years`);
        const monthInput = document.getElementById(`${termId}-months`);
        
        if (!yearInput || !monthInput) {
            console.warn(`Inputs for ${termId} not found`);
            return 0;
        }

        // Return value from whichever input is currently visible
        if (yearInput.style.display === 'block') {
            const years = parseFloat(yearInput.value) || 0;
            return years * 12;
        } else {
            return parseFloat(monthInput.value) || 0;
        }
    },

    setValue: function(termId, months) {
        console.log(`Setting value for ${termId} to ${months} months`);
        const yearInput = document.getElementById(`${termId}-years`);
        const monthInput = document.getElementById(`${termId}-months`);
        const hiddenInput = document.getElementById(termId);
        
        if (!yearInput || !monthInput) {
            console.warn(`Inputs for ${termId} not found when setting value`);
            return false;
        }

        const monthValue = parseFloat(months) || 0;
        const yearValue = monthValue / 12;

        yearInput.value = yearValue.toString();
        monthInput.value = monthValue.toString();
        if (hiddenInput) {
            hiddenInput.value = monthValue.toString();
        }

        return true;
    }
};

export default LoanTermToggleModule;