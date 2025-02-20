// Comps Handler Module
const compsHandler = {
    // State
    analysisId: null,
    
    // Initialize the comps functionality
    init(analysisId) {
        this.analysisId = analysisId;
        this.attachEventHandlers();
        this.loadExistingComps();
    },
    
    // Attach event handlers
    attachEventHandlers() {
        console.log('Attaching comps event handlers...');
        const runCompsBtn = document.getElementById('runCompsBtn');
        console.log('Run comps button found:', !!runCompsBtn);
        
        if (runCompsBtn) {
            // Remove any existing click handlers
            const newBtn = runCompsBtn.cloneNode(true);
            runCompsBtn.parentNode.replaceChild(newBtn, runCompsBtn);
            
            newBtn.addEventListener('click', () => {
                console.log('Run comps button clicked');
                this.handleRunComps();
            });
            console.log('Click handler attached to run comps button');
        } else {
            console.error('Run comps button not found in DOM');
        }
    },
    
    // Load existing comps data if available
    loadExistingComps() {
        const analysis = document.getElementById('analysis-data')?.textContent;
        if (analysis) {
            try {
                const data = JSON.parse(analysis);
                if (data.comps_data) {
                    this.updateCompsDisplay(data.comps_data);
                }
            } catch (error) {
                console.error('Error parsing analysis data:', error);
            }
        }
    },
    
    // Handle running comps
    async handleRunComps() {
        if (!this.analysisId) {
            toastr.error('Analysis ID not found');
            return;
        }
        
        // Show loading state
        this.setLoadingState(true);
        
        try {
            const response = await fetch(`/analyses/run_comps/${this.analysisId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Error fetching comps');
            }
            
            if (data.success) {
                // Update display with new comps data
                this.updateCompsDisplay(data.analysis.comps_data);
                toastr.success('Comps updated successfully');
            } else {
                throw new Error(data.message);
            }
            
        } catch (error) {
            console.error('Error:', error);
            this.showError(error.message);
        } finally {
            this.setLoadingState(false);
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
        return comparables.map(comp => `
            <tr>
                <td>${comp.formattedAddress}</td>
                <td>${this.formatCurrency(comp.price)}</td>
                <td>${comp.bedrooms}/${comp.bathrooms}</td>
                <td>${comp.squareFootage.toLocaleString()}</td>
                <td>${comp.yearBuilt}</td>
                <td>${this.formatDate(comp.removedDate || comp.listedDate)}</td>
                <td>${comp.distance.toFixed(2)} mi</td>
            </tr>
        `).join('');
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
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }
};

export default compsHandler;