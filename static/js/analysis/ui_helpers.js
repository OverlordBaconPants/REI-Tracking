/**
 * ui_helpers.js
 * UI utilities for the analysis module
 */

const UIHelpers = {
    // Stored styles
    styles: {
      tooltipStyles: `
        @media (max-width: 767.98px) {
          .tooltip {
            font-size: 0.75rem;
          }
          .popover {
            max-width: 90%;
            font-size: 0.875rem;
          }
          .popover-header {
            padding: 0.5rem 0.75rem;
            font-size: 0.875rem;
          }
          .popover-body {
            padding: 0.5rem 0.75rem;
            font-size: 0.875rem;
          }
          .tooltip-inner {
            max-width: 200px;
            padding: 0.25rem 0.5rem;
          }
        }
      `,
      mobileStyles: `
        .keyboard-visible {
          padding-bottom: 40vh;
        }
  
        @media (max-width: 767.98px) {
          .form-group {
            margin-bottom: 1.5rem;
          }
  
          .btn-group {
            flex-direction: column;
          }
  
          .btn-group .btn {
            margin-bottom: 0.5rem;
          }
  
          .dropdown-menu {
            position: fixed !important;
            top: auto !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            margin: 0;
            border-radius: 1rem 1rem 0 0;
            max-height: 50vh;
            overflow-y: auto;
          }
  
          .modal {
            padding: 0 !important;
          }
  
          .modal-dialog {
            margin: 0;
            max-width: none;
            min-height: 100vh;
          }
  
          .modal-content {
            border-radius: 0;
            min-height: 100vh;
          }
        }
      `,
      notesStyles: `
        @media (max-width: 767.98px) {
          .notes-content {
            font-size: 0.875rem;
            line-height: 1.5;
            word-break: break-word;
          }
          
          .notes-content br {
            display: block;
            margin: 0.5rem 0;
            content: "";
          }
        }
      `
    },
    
    /**
     * Inject required styles into the document
     */
    injectStyles() {
      const styles = [
        { content: this.styles.tooltipStyles, id: 'analysis-tooltip-styles' },
        { content: this.styles.mobileStyles, id: 'analysis-mobile-styles' },
        { content: this.styles.notesStyles, id: 'analysis-notes-styles' }
      ];
  
      styles.forEach(style => {
        let styleElement = document.getElementById(style.id);
        if (!styleElement) {
          styleElement = document.createElement('style');
          styleElement.id = style.id;
          styleElement.textContent = style.content;
          document.head.appendChild(styleElement);
        }
      });
    },
    
    /**
     * Initialize toastr notifications
     */
    initToastr() {
      if (typeof toastr !== 'undefined') {
        toastr.options = {
          closeButton: true,
          progressBar: true,
          positionClass: 'toast-top-right',
          preventDuplicates: true,
          timeOut: 3000,
          extendedTimeOut: 1000,
          showEasing: 'swing',
          hideEasing: 'linear',
          showMethod: 'fadeIn',
          hideMethod: 'fadeOut'
        };
      }
    },
    
    /**
     * Show a toast notification
     * @param {string} type - The type of toast (success, error, warning, info)
     * @param {string} message - The message to display
     */
    showToast(type, message) {
      if (typeof toastr === 'undefined') {
        console.log(`Toast (${type}): ${message}`);
        return;
      }
      
      switch (type) {
        case 'success':
          toastr.success(message);
          break;
        case 'error':
          toastr.error(message);
          break;
        case 'warning':
          toastr.warning(message);
          break;
        case 'info':
          toastr.info(message);
          break;
        default:
          toastr.info(message);
      }
    },
    
    /**
     * Initialize viewport change handler
     */
    initViewportHandler() {
      window.addEventListener('resize', _.debounce(() => {
        this.initMobileInteractions();
        this.initTooltips();
      }, 250));
    },
    
    /**
     * Initialize mobile interactions
     */
    initMobileInteractions() {
      this.initAccordionScrolling();
      this.initTouchFeedback();
      this.initResponsiveTables();
      this.initMobileKeyboardHandling();
    },
    
    /**
     * Initialize accordion scrolling for better mobile UX
     */
    initAccordionScrolling() {
      const accordions = document.querySelectorAll('.accordion');
      accordions.forEach(accordion => {
        accordion.addEventListener('shown.bs.collapse', (e) => {
          const targetElement = e.target;
          const offset = targetElement.getBoundingClientRect().top + window.pageYOffset - 80;
          window.scrollTo({
            top: offset,
            behavior: 'smooth'
          });
        });
      });
    },
    
    /**
     * Initialize touch feedback for interactive elements
     */
    initTouchFeedback() {
      const interactiveElements = document.querySelectorAll(
        '.list-group-item, .accordion-button, .btn'
      );
      
      interactiveElements.forEach(element => {
        element.addEventListener('touchstart', function() {
          this.style.backgroundColor = 'rgba(0,0,0,0.05)';
        });
        
        element.addEventListener('touchend', function() {
          this.style.backgroundColor = '';
        });
      });
    },
    
    /**
     * Initialize responsive tables
     */
    initResponsiveTables() {
      const tables = document.querySelectorAll('.table:not(.responsive-handled)');
      tables.forEach(table => {
        if (!table.parentElement.classList.contains('table-responsive')) {
          const wrapper = document.createElement('div');
          wrapper.className = 'table-responsive';
          table.parentNode.insertBefore(wrapper, table);
          wrapper.appendChild(table);
          table.classList.add('responsive-handled');
        }
      });
    },
    
    /**
     * Initialize mobile keyboard handling
     */
    initMobileKeyboardHandling() {
      // Detect virtual keyboard
      let originalHeight = window.innerHeight;
      
      window.addEventListener('resize', () => {
        if (window.innerWidth < 768) {
          const heightDiff = originalHeight - window.innerHeight;
          if (heightDiff > 150) {
            // Keyboard is likely visible
            document.body.classList.add('keyboard-visible');
          } else {
            document.body.classList.remove('keyboard-visible');
          }
        }
      });

      // Improve input behavior on mobile
      const numericInputs = document.querySelectorAll('input[type="number"]');
      numericInputs.forEach(input => {
        input.addEventListener('focus', function() {
          if (window.innerWidth < 768) {
            this.type = 'tel';  // Better numeric keyboard on mobile
          }
        });
        
        input.addEventListener('blur', function() {
          this.type = 'number';
        });
      });
    },
    
    /**
     * Initialize tooltips
     */
    initTooltips() {
      const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
      tooltips.forEach(tooltip => {
        // Dispose existing tooltip instance
        const tooltipInstance = bootstrap.Tooltip.getInstance(tooltip);
        if (tooltipInstance) {
          tooltipInstance.dispose();
        }
        
        // Create new tooltip with mobile-friendly options
        new bootstrap.Tooltip(tooltip, {
          trigger: window.innerWidth < 768 ? 'click' : 'hover',
          placement: window.innerWidth < 768 ? 'bottom' : 'auto'
        });
      });
    },
    
    /**
     * Initialize notes character counter
     */
    initNotesCounter() {
      const notesTextarea = document.getElementById('notes');
      const notesCounter = document.getElementById('notes-counter');
      if (notesTextarea && notesCounter) {
        // Update counter with initial value if exists
        notesCounter.textContent = notesTextarea.value.length;
        
        // Add event listener for changes
        notesTextarea.addEventListener('input', function() {
          notesCounter.textContent = this.value.length;
        });
      }
    },
    
    /**
     * Initialize address autocomplete
     * @param {HTMLElement} addressInput - The address input field
     */
    initAddressAutocomplete(addressInput) {
      if (!addressInput) return;

      // Create results list element
      const resultsList = document.createElement('ul');
      resultsList.className = 'autocomplete-results list-group position-absolute w-100 shadow-sm';
      resultsList.style.zIndex = '1000';
      
      // Insert the results list after the input
      addressInput.parentNode.appendChild(resultsList);
      
      let timeoutId;
      
      // Add input event listener
      addressInput.addEventListener('input', function() {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
          const query = this.value;
          if (query.length > 2) {
            fetch(`/api/autocomplete?query=${encodeURIComponent(query)}`)
              .then(response => {
                if (!response.ok) {
                  throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
              })
              .then(data => {
                resultsList.innerHTML = '';
                
                if (data.status === 'success' && data.data && Array.isArray(data.data)) {
                  data.data.forEach(result => {
                    const li = document.createElement('li');
                    li.className = 'list-group-item list-group-item-action';
                    li.textContent = result.formatted;
                    li.style.cursor = 'pointer';
                    
                    li.addEventListener('click', function() {
                      addressInput.value = this.textContent;
                      resultsList.innerHTML = '';
                    });
                    
                    resultsList.appendChild(li);
                  });
                  
                  if (data.data.length === 0) {
                    const li = document.createElement('li');
                    li.className = 'list-group-item disabled';
                    li.textContent = 'No matches found';
                    resultsList.appendChild(li);
                  }
                }
              })
              .catch(error => {
                resultsList.innerHTML = `
                  <li class="list-group-item text-danger">
                    Error fetching results: ${error.message}
                  </li>
                `;
              });
          } else {
            resultsList.innerHTML = '';
          }
        }, 300);
      });

      // Close suggestions when clicking outside
      document.addEventListener('click', function(e) {
        if (e.target !== addressInput && e.target !== resultsList) {
          resultsList.innerHTML = '';
        }
      });

      // Prevent form submission when selecting from dropdown
      resultsList.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
      });
    },
    
    /**
     * Switch to financial tab
     */
    switchToFinancialTab() {
      const financialTab = document.getElementById('financial-tab');
      if (financialTab) {
        financialTab.click();
      }
    },
    
    /**
     * Switch to reports tab
     */
    switchToReportsTab() {
      const reportsTab = document.getElementById('reports-tab');
      if (reportsTab) {
        reportsTab.click();
      }
    },
    
    /**
     * Format display value for currency or percentage
     * @param {number|string} value - The value to format
     * @param {string} type - The type of formatting (money or percentage)
     * @returns {string} The formatted value
     */
    formatDisplayValue(value, type = 'money') {
      if (value === null || value === undefined || value === '') {
        return type === 'money' ? '$0.00' : '0.00%';
      }

      const numValue = parseFloat(value);
      if (isNaN(numValue)) {
        return type === 'money' ? '$0.00' : '0.00%';
      }

      if (type === 'money') {
        return new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD',
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        }).format(numValue);
      } else if (type === 'percentage') {
        return `${numValue.toFixed(2)}%`;
      }
      
      return value;
    },

    /**
     * Convert string to raw number
     * @param {string|number} value - The value to convert
     * @returns {number} The raw number
     */
    toRawNumber(value) {
      if (value === null || value === undefined || value === '') {
        return 0;
      }
      
      // Convert to string if not already
      const strValue = String(value);
      
      // Remove currency symbols, commas, spaces, and %
      const cleaned = strValue.replace(/[$,%\s]/g, '');
      
      // Convert to number
      const num = parseFloat(cleaned);
      return isNaN(num) ? 0 : num;
    },
    
    /**
     * Extract numeric value from string
     * @param {string|number} value - The value to extract
     * @returns {number} The numeric value
     */
    extractNumericValue(value) {
      if (value === null || value === undefined) return 0;
      if (typeof value === 'number') return value;
      
      // Handle string values
      if (typeof value === 'string') {
        // Remove currency symbols, commas, etc.
        const cleanValue = value.replace(/[$,\s]+/g, '');
        const parsedValue = parseFloat(cleanValue);
        return isNaN(parsedValue) ? 0 : parsedValue;
      }
      
      return 0;
    },
    
    /**
     * Extract percentage value from string
     * @param {string|number} value - The value to extract
     * @returns {number} The percentage value
     */
    extractPercentageValue(value) {
      if (value === null || value === undefined) return 0;
      if (typeof value === 'number') return value;
      
      // Handle string values
      if (typeof value === 'string') {
        // Remove percentage symbols, commas, etc.
        const cleanValue = value.replace(/[%,\s]+/g, '');
        const parsedValue = parseFloat(cleanValue);
        return isNaN(parsedValue) ? 0 : parsedValue;
      }
      
      return 0;
    },
    
    /**
     * Show a confirmation dialog for analysis type change
     * @param {string} newType - The new analysis type
     * @param {string} oldType - The old analysis type
     * @returns {Promise<boolean>} Whether the change was confirmed
     */
    async confirmTypeChange(newType, oldType) {
      return new Promise(resolve => {
        if (confirm(
          `Changing from ${oldType} to ${newType} will create a new analysis with the current data. Proceed?`
        )) {
          resolve(true);
        } else {
          resolve(false);
        }
      });
    }
};

// Export the helpers
export default UIHelpers;