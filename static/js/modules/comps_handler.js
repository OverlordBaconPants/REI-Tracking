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
    
        console.log("Comps data received:", compsData);
        console.log("MAO data present:", compsData.mao ? "Yes" : "No");
        console.log("Rental comps present:", compsData.rental_comps ? "Yes" : "No");
        
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

        // Add MAO display if available
        const maoSection = document.getElementById('maoSection');
        if (maoSection && compsData.mao) {
            maoSection.style.display = 'block';
            document.getElementById('maoValue').textContent = this.formatCurrency(compsData.mao.value);
            
            // Add event handler for "Use as Purchase Price" button
            const useMaoButton = document.getElementById('useMaoButton');
            if (useMaoButton) {
                useMaoButton.onclick = () => this.useMAOasPurchasePrice(compsData.mao.value);
            }
            
            // Display calculation details
            const maoDetails = document.getElementById('maoDetailsBody');
            if (maoDetails) {
                maoDetails.innerHTML = `
                    <div class="table-responsive">
                        <table class="table table-sm">
                            <tbody>
                                <tr>
                                    <td>ARV (from comps):</td>
                                    <td class="text-end">${this.formatCurrency(compsData.mao.arv)}</td>
                                </tr>
                                <tr>
                                    <td>LTV Percentage:</td>
                                    <td class="text-end">${compsData.mao.ltv_percentage.toFixed(1)}%</td>
                                </tr>
                                <tr>
                                    <td>Renovation Costs:</td>
                                    <td class="text-end">${this.formatCurrency(compsData.mao.renovation_costs)}</td>
                                </tr>
                                <tr>
                                    <td>Monthly Holding Costs:</td>
                                    <td class="text-end">${this.formatCurrency(compsData.mao.monthly_holding_costs)}</td>
                                </tr>
                                <tr>
                                    <td>Holding Period:</td>
                                    <td class="text-end">${compsData.mao.holding_months} months</td>
                                </tr>
                                <tr>
                                    <td>Total Holding Costs:</td>
                                    <td class="text-end">${this.formatCurrency(compsData.mao.total_holding_costs)}</td>
                                </tr>
                                <tr>
                                    <td>Closing Costs:</td>
                                    <td class="text-end">${this.formatCurrency(compsData.mao.closing_costs)}</td>
                                </tr>
                                <tr>
                                    <td>Max Cash Left in Deal:</td>
                                    <td class="text-end">${this.formatCurrency(compsData.mao.max_cash_left)}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                `;
            }
        }
        
        // Display rental comps if available
        if (compsData.rental_comps) {
            this.displayRentalComps(compsData.rental_comps);
        }
        
        // Hide initial message
        document.getElementById('initialCompsMessage').style.display = 'none';
    },
    
    // Display rental comps data
    displayRentalComps(rentalComps) {
        if (!rentalComps) {
            console.log('No rental comps data to display');
            return;
        }
        
        console.log('Displaying rental comps:', rentalComps);
        
        // Create or find rental section
        let rentalSection = document.getElementById('rentalCompsSection');
        
        // If section doesn't exist, create it
        if (!rentalSection) {
            // Find the parent element where we'll add the rental comps section
            const compsContainer = document.querySelector('.comps-container') || 
                                   document.getElementById('compsTableSection')?.parentElement;
            
            if (!compsContainer) {
                console.error('Comps Handler: Could not find comps container');
                return;
            }
            
            // Create rental comps section
            rentalSection = document.createElement('div');
            rentalSection.id = 'rentalCompsSection';
            rentalSection.className = 'card mt-4';
            rentalSection.innerHTML = `
                <div class="card-header bg-primary text-white">
                    <h5 class="mb-0">Rental Comps Analysis</h5>
                </div>
                <div class="card-body">
                    <div class="row mb-4">
                        <div class="col-md-4">
                            <div class="card h-100">
                                <div class="card-body text-center">
                                    <h5 class="card-title">Estimated Monthly Rent</h5>
                                    <h2 id="estimatedRent" class="text-primary mt-3"></h2>
                                    <p class="text-muted small">
                                        Range: <span id="rentLow"></span> - <span id="rentHigh"></span>
                                    </p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card h-100">
                                <div class="card-body text-center">
                                    <h5 class="card-title">Cap Rate</h5>
                                    <h2 id="capRate" class="text-success mt-3"></h2>
                                    <p class="text-muted small">
                                        Based on purchase price and estimated rent
                                    </p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card h-100">
                                <div class="card-body text-center">
                                    <h5 class="card-title">Annual Rental Income</h5>
                                    <h2 id="annualRent" class="text-info mt-3"></h2>
                                    <p class="text-muted small">
                                        Projected annual gross rental income
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div id="rentalTableSection">
                        <h5>Comparable Rentals</h5>
                        <div class="table-responsive">
                            <table class="table table-sm table-striped">
                                <thead>
                                    <tr>
                                        <th>Address</th>
                                        <th>Monthly Rent</th>
                                        <th>Beds/Baths</th>
                                        <th>Sq Ft</th>
                                        <th>Year Built</th>
                                        <th>Distance</th>
                                    </tr>
                                </thead>
                                <tbody id="rentalTableBody">
                                </tbody>
                            </table>
                        </div>
                    </div>
                    
                    <div id="noRentalsFound" style="display:none;" class="alert alert-warning">
                        No comparable rentals found in the area.
                    </div>
                    
                    <div class="mt-3">
                        <button id="useRentButton" class="btn btn-sm btn-success">
                            <i class="bi bi-check-circle me-2"></i>Use as Monthly Rent
                        </button>
                    </div>
                </div>
            `;
            
            // Add the rental section after the property comps section
            compsContainer.appendChild(rentalSection);
            
            // Add event listener for the "Use as Monthly Rent" button
            const useRentButton = document.getElementById('useRentButton');
            if (useRentButton) {
                useRentButton.addEventListener('click', () => {
                    this.useEstimatedRent(rentalComps.estimated_rent);
                });
            }
        }
        
        // Update rental data
        document.getElementById('estimatedRent').textContent = this.formatCurrency(rentalComps.estimated_rent);
        document.getElementById('rentLow').textContent = this.formatCurrency(rentalComps.rent_range_low);
        document.getElementById('rentHigh').textContent = this.formatCurrency(rentalComps.rent_range_high);
        
        // Calculate and display annual rent
        const annualRent = rentalComps.estimated_rent * 12;
        document.getElementById('annualRent').textContent = this.formatCurrency(annualRent);
        
        // Display cap rate if available
        if (rentalComps.cap_rate) {
            document.getElementById('capRate').textContent = rentalComps.cap_rate.toFixed(2) + '%';
        } else {
            document.getElementById('capRate').textContent = 'N/A';
        }
        
        // Display rental comparables
        const rentalTableBody = document.getElementById('rentalTableBody');
        const noRentalsFound = document.getElementById('noRentalsFound');
        const rentalTableSection = document.getElementById('rentalTableSection');
        
        if (rentalComps.comparable_rentals && rentalComps.comparable_rentals.length > 0) {
            rentalTableBody.innerHTML = this.generateRentalTableRows(rentalComps.comparable_rentals);
            rentalTableSection.style.display = 'block';
            noRentalsFound.style.display = 'none';
        } else {
            rentalTableSection.style.display = 'none';
            noRentalsFound.style.display = 'block';
        }
    },
    
    // Generate table rows for rental comps
    generateRentalTableRows(comparables) {
        return comparables.map(comp => {
            return `
                <tr>
                    <td>${comp.formattedAddress || 'N/A'}</td>
                    <td>${this.formatCurrency(comp.price || 0)}</td>
                    <td>${comp.bedrooms || 0}/${comp.bathrooms || 0}</td>
                    <td>${(comp.squareFootage || 0).toLocaleString()}</td>
                    <td>${comp.yearBuilt || 'N/A'}</td>
                    <td>${(comp.distance || 0).toFixed(2)} mi</td>
                </tr>
            `;
        }).join('');
    },
    
    // Use estimated rent as monthly rent
    useEstimatedRent(estimatedRent) {
        const monthlyRentField = document.getElementById('monthly_rent');
        if (monthlyRentField) {
            // Update monthly rent with estimated rent
            monthlyRentField.value = estimatedRent.toFixed(0); // Round to nearest dollar
            
            // Trigger change event to ensure calculations update
            const event = new Event('change', { bubbles: true });
            monthlyRentField.dispatchEvent(event);
            
            // Show success message
            toastr.success('Monthly rent updated to estimated rental value');
            
            // If we're on the financial tab, offer to update analysis
            const updateBtn = document.getElementById('submitAnalysisBtn');
            if (updateBtn) {
                const confirmUpdate = confirm('Would you like to update the analysis with the new rental value?');
                if (confirmUpdate) {
                    updateBtn.click();
                }
            }
        } else {
            toastr.error('Monthly rent field not found');
        }
    },

    useMAOasPurchasePrice(maoValue) {
        const purchasePriceField = document.getElementById('purchase_price');
        if (purchasePriceField) {
            // Store original value
            const originalValue = purchasePriceField.value;
            
            // Update purchase price with MAO
            purchasePriceField.value = maoValue.toFixed(0); // Round to nearest dollar
            
            // Trigger change event to ensure calculations update
            const event = new Event('change', { bubbles: true });
            purchasePriceField.dispatchEvent(event);
            
            // Show success message
            toastr.success('Purchase price updated to Maximum Allowable Offer');
            
            // If we're on the financial tab, offer to update analysis
            const updateBtn = document.getElementById('submitAnalysisBtn');
            if (updateBtn) {
                const confirmUpdate = confirm('Would you like to update the analysis with the new purchase price?');
                if (confirmUpdate) {
                    updateBtn.click();
                }
            }
        } else {
            toastr.error('Purchase price field not found');
        }
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
        
        // Display MAO if available
        if (compsData.mao) {
            console.log('Showing MAO:', compsData.mao);
            const maoSection = document.getElementById('maoSection');
            if (maoSection) {
                maoSection.style.display = 'block';
                document.getElementById('maoValue').textContent = this.formatCurrency(compsData.mao.value);
                
                // Display calculation details
                const maoDetails = document.getElementById('maoDetailsBody');
                if (maoDetails) {
                    maoDetails.innerHTML = `
                        <div class="table-responsive">
                            <table class="table table-sm">
                                <tbody>
                                    <tr>
                                        <td>ARV (from comps):</td>
                                        <td class="text-end">${this.formatCurrency(compsData.mao.arv)}</td>
                                    </tr>
                                    <tr>
                                        <td>LTV Percentage:</td>
                                        <td class="text-end">${compsData.mao.ltv_percentage.toFixed(1)}%</td>
                                    </tr>
                                    <tr>
                                        <td>Renovation Costs:</td>
                                        <td class="text-end">${this.formatCurrency(compsData.mao.renovation_costs)}</td>
                                    </tr>
                                    <tr>
                                        <td>Monthly Holding Costs:</td>
                                        <td class="text-end">${this.formatCurrency(compsData.mao.monthly_holding_costs)}</td>
                                    </tr>
                                    <tr>
                                        <td>Holding Period:</td>
                                        <td class="text-end">${compsData.mao.holding_months} months</td>
                                    </tr>
                                    <tr>
                                        <td>Total Holding Costs:</td>
                                        <td class="text-end">${this.formatCurrency(compsData.mao.total_holding_costs)}</td>
                                    </tr>
                                    <tr>
                                        <td>Closing Costs:</td>
                                        <td class="text-end">${this.formatCurrency(compsData.mao.closing_costs)}</td>
                                    </tr>
                                    <tr>
                                        <td>Max Cash Left in Deal:</td>
                                        <td class="text-end">${this.formatCurrency(compsData.mao.max_cash_left)}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    `;
                }
            }
        }
        
        // Display rental comps if available
        if (compsData.rental_comps) {
            console.log('Showing rental comps');
            this.displayRentalComps(compsData.rental_comps);
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