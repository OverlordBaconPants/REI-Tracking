// Comps Handler Module
const compsHandler = {
    // State
    analysisId: null,
    
    // Initialize the comps functionality
    init(analysisId) {
        console.log('Comps Handler: Starting initialization with ID:', analysisId);
        
        // Enhanced validation
        if (!analysisId || typeof analysisId !== 'string') {
            console.error('Comps Handler: Invalid analysis ID type:', typeof analysisId);
            return false;
        }

        const trimmedId = analysisId.trim();
        if (trimmedId === '') {
            console.error('Comps Handler: Empty analysis ID');
            return false;
        }

        this.analysisId = trimmedId;
        console.log('Comps Handler: Analysis ID set to:', this.analysisId);
        
        this.attachEventHandlers();
        this.loadExistingComps();
        
        return true;
    },
    
    // Attach event handlers
    attachEventHandlers() {
        console.log('Comps Handler: Starting to attach event handlers');
        const runCompsBtn = document.getElementById('runCompsBtn');
        console.log('Comps Handler: Run comps button found:', !!runCompsBtn);
        
        if (runCompsBtn) {
            // Remove any existing click handlers
            const newBtn = runCompsBtn.cloneNode(true);
            runCompsBtn.parentNode.replaceChild(newBtn, runCompsBtn);
            
            // Add click handler with debugging
            newBtn.addEventListener('click', (e) => {
                e.preventDefault();
                if (!this.analysisId) {
                    console.error('Comps Handler: No analysis ID available');
                    toastr.error('Analysis ID not found');
                    return;
                }
                console.log('Comps Handler: Run comps button clicked');
                console.log('Comps Handler: Current analysis ID:', this.analysisId);
                this.handleRunComps();
            });
            
            console.log('Comps Handler: Click handler attached successfully');
        } else {
            console.error('Comps Handler: Run comps button not found in DOM');
        }
    },
    
    // Load existing comps data if available
    loadExistingComps() {
        console.log('Comps Handler: Loading existing comps');
        const analysis = document.getElementById('analysis-data')?.textContent;
        if (analysis) {
            try {
                const data = JSON.parse(analysis);
                if (data.comps_data) {
                    this.displayExistingComps(data.comps_data);
                    console.log('Comps Handler: Loaded existing comps data');
                }
            } catch (error) {
                console.error('Comps Handler: Error parsing analysis data:', error);
            }
        }
    },
    
    // Handle running comps
    async handleRunComps() {
        console.log('Comps Handler: handleRunComps called');
        console.log('Comps Handler: Analysis ID at execution:', this.analysisId);
        
        if (!this.analysisId) {
            console.error('Comps Handler: Analysis ID not found');
            toastr.error('Analysis ID not found');
            return;
        }
        
        // Show loading state
        this.setLoadingState(true);
        console.log('Comps Handler: Set loading state');
        
        try {
            console.log('Comps Handler: Making API request to /analyses/run_comps/' + this.analysisId);
            const response = await fetch(`/analyses/run_comps/${this.analysisId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            console.log('Comps Handler: Received response:', response.status);
            const data = await response.json();
            console.log('Comps Handler: Parsed response data:', data);
            
            if (!response.ok) {
                throw new Error(data.message || 'Error fetching comps');
            }
            
            if (data.success) {
                // Update display with new comps data
                this.updateCompsDisplay(data.analysis.comps_data);
                toastr.success('Comps updated successfully');
                console.log('Comps Handler: Display updated successfully');
            } else {
                throw new Error(data.message);
            }
            
        } catch (error) {
            console.error('Comps Handler: Error in handleRunComps:', error);
            this.showError(error.message);
        } finally {
            this.setLoadingState(false);
            console.log('Comps Handler: Reset loading state');
        }
    },
    
    // Update the comps display
    updateCompsDisplay(compsData) {
        if (!compsData) return;
        
        // Show estimated value section
        const valueSection = document.getElementById('estimatedValueSection');
        if (valueSection) {
            valueSection.style.display = 'block';
            
            // Update estimated value and range
            document.getElementById('estimatedValue').textContent = 
                this.formatCurrency(compsData.estimated_value);
            document.getElementById('valueLow').textContent = 
                this.formatCurrency(compsData.value_range_low);
            document.getElementById('valueHigh').textContent = 
                this.formatCurrency(compsData.value_range_high);
        }
        
        // Update run count
        const runCountSection = document.getElementById('compsRunCount');
        if (runCountSection && compsData.run_count) {
            runCountSection.style.display = 'inline-block';
            document.getElementById('runCountValue').textContent = compsData.run_count;
        }
        
        // Update comps table
        const tableSection = document.getElementById('compsTableSection');
        const tableBody = document.getElementById('compsTableBody');
        if (tableSection && tableBody) {
            if (compsData.comparables && compsData.comparables.length > 0) {
                tableSection.style.display = 'block';
                tableBody.innerHTML = this.generateCompsTableRows(compsData.comparables);
                document.getElementById('noCompsFound').style.display = 'none';
            } else {
                tableSection.style.display = 'none';
                document.getElementById('noCompsFound').style.display = 'block';
            }
        }
        
        // Hide initial message
        document.getElementById('initialCompsMessage').style.display = 'none';
    },
    
    // Generate table rows for comps
    generateCompsTableRows(comparables) {
        return comparables.map(comp => {
            // Use removedDate as the sale date for sold properties
            const saleDate = comp.saleDate || comp.removedDate;
            
            return `
                <tr>
                    <td>${comp.formattedAddress || ''}</td>
                    <td>${this.formatCurrency(comp.price)}</td>
                    <td>${comp.bedrooms || 0}/${comp.bathrooms || 0}</td>
                    <td>${(comp.squareFootage || 0).toLocaleString()}</td>
                    <td>${comp.yearBuilt || 'N/A'}</td>
                    <td>${this.formatDate(saleDate)}</td>
                    <td>${(comp.distance || 0).toFixed(2)} mi</td>
                </tr>
            `;
        }).join('');
    },

    displayExistingComps(compsData) {
        console.log('Displaying existing comps:', compsData);
        
        const estimatedValueSection = document.getElementById('estimatedValueSection');
        const compsTableSection = document.getElementById('compsTableSection');
        const runCountElement = document.getElementById('compsRunCount');
        const initialMessage = document.getElementById('initialCompsMessage');
        const runCompsBtn = document.getElementById('runCompsBtn');
        
        console.log('Found elements:', {
            estimatedValueSection: !!estimatedValueSection,
            compsTableSection: !!compsTableSection,
            runCountElement: !!runCountElement,
            initialMessage: !!initialMessage,
            runCompsBtn: !!runCompsBtn
        });
        
        if (estimatedValueSection && compsData.estimated_value) {
            console.log('Showing estimated value:', compsData.estimated_value);
            estimatedValueSection.style.display = 'block';
            document.getElementById('estimatedValue').textContent = this.formatCurrency(compsData.estimated_value);
            document.getElementById('valueLow').textContent = this.formatCurrency(compsData.value_range_low);
            document.getElementById('valueHigh').textContent = this.formatCurrency(compsData.value_range_high);
        }
        
        if (compsTableSection && compsData.comparables?.length > 0) {
            console.log('Showing comps table with', compsData.comparables.length, 'entries');
            compsTableSection.style.display = 'block';
            const tableBody = document.getElementById('compsTableBody');
            if (tableBody) {
                tableBody.innerHTML = this.generateCompsTableRows(compsData.comparables);
            }
        }
        
        if (runCountElement && compsData.run_count) {
            console.log('Showing run count:', compsData.run_count);
            runCountElement.style.display = 'inline-block';
            document.getElementById('runCountValue').textContent = compsData.run_count;
        }
        
        if (initialMessage) {
            initialMessage.style.display = 'none';
        }
        
        if (runCompsBtn) {
            runCompsBtn.innerHTML = '<i class="bi bi-arrow-repeat me-2"></i>Re-Run Comps';
        }
    },
    
    // Set loading state
    setLoadingState(isLoading) {
        document.getElementById('compsLoading').style.display = isLoading ? 'block' : 'none';
        document.getElementById('runCompsBtn').disabled = isLoading;
        
        if (isLoading) {
            document.getElementById('compsError').style.display = 'none';
            document.getElementById('initialCompsMessage').style.display = 'none';
        }
    },
    
    // Show error message
    showError(message) {
        const errorDiv = document.getElementById('compsError');
        const errorMessage = document.getElementById('compsErrorMessage');
        if (errorDiv && errorMessage) {
            errorMessage.textContent = message;
            errorDiv.style.display = 'block';
        }
        toastr.error(message);
    },
    
    // Helper: Format currency
    formatCurrency(value) {
        if (value === undefined || value === null) {
            return '$0';
        }
        
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(value);
    },
    
    // Helper: Format date
    formatDate(dateString) {
        if (!dateString) return 'N/A';
        
        try {
            const date = new Date(dateString);
            if (isNaN(date.getTime())) return 'N/A';
            
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        } catch (error) {
            console.error('Error formatting date:', error);
            return 'N/A';
        }
    }
};

export default compsHandler;