// Comps Handler Module
const compsHandler = {
    // State
    analysisId: null,
    hasRunComps: false, // Track if comps have been run
    
    watchForDOMChanges() {
        console.log('Starting DOM mutation observer');
        
        // Create an observer instance
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                // If nodes were added or removed
                if (mutation.addedNodes.length || mutation.removedNodes.length) {
                    // Check if our comps section still exists
                    const compsSection = document.getElementById('compsSection');
                    if (!compsSection) {
                        console.log('Comps section was removed, recreating it');
                        this.createCompsContainer();
                    }
                }
            });
        });
        
        // Start observing the financial tab
        const financialTab = document.getElementById('financial');
        if (financialTab) {
            observer.observe(financialTab, { 
                childList: true,
                subtree: true
            });
            console.log('Watching for DOM changes in financial tab');
        }
    },

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
        
        // Remove any existing comps sections first
        this.removeExistingCompsSections();
        
        // Create a single clean comps container
        this.createCompsContainer();
        
        // Load existing comps data if available
        this.loadExistingComps();

        // Watch for DOM changes
        this.watchForDOMChanges();

        // Add this debug check
        setTimeout(() => {
            const compsSection = document.getElementById('compsSection');
            console.log('Debug: Comps section exists in DOM:', !!compsSection);
            if (compsSection) {
                console.log('Debug: Comps section display style:', window.getComputedStyle(compsSection).display);
                console.log('Debug: Comps section visibility:', window.getComputedStyle(compsSection).visibility);
                console.log('Debug: Comps section height:', window.getComputedStyle(compsSection).height);
            }
        }, 1000); // Check after 1 second
        
        return true;
    },

    // Remove any existing comps sections to start fresh
    removeExistingCompsSections() {
        console.log('Comps Handler: Removing any existing comps sections');
        
        // Remove by ID
        ['compsSection', 'comparableSalesSection', 'rentalCompsSection', 'keyMetricsSection'].forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                console.log(`Removing existing element with ID: ${id}`);
                element.remove();
            }
        });
        
        // Remove by header text
        document.querySelectorAll('.card').forEach(card => {
            const header = card.querySelector('.card-header');
            if (header && (
                header.textContent.includes('Comparable Properties') ||
                header.textContent.includes('Comparable Sales') ||
                header.textContent.includes('Comparable Rentals') ||
                header.textContent.includes('Key Property Metrics')
            )) {
                console.log('Removing card with comps-related header:', header.textContent.trim());
                const container = card.closest('.row, .col, .col-12, div') || card;
                container.remove();
            }
        });
    },

    // Create a fresh comps container
    createCompsContainer() {
        console.log('Comps Handler: Creating fresh comps container');
        
        // Look for the financial tab
        const financialTab = document.getElementById('financial');
        if (!financialTab) {
            console.log('Financial tab not found, trying alternative approach');
            return;
        }
        
        // IMPROVED INSERTION LOGIC with simpler selectors:
        // First try to find Notes section by ID
        let insertAfter = document.getElementById('notesSection');
        console.log('Notes section found by ID:', !!insertAfter);
        
        // If not found, try looking for a card with Notes in the header
        if (!insertAfter) {
            const cardHeaders = financialTab.querySelectorAll('.card-header');
            for (const header of cardHeaders) {
                if (header.textContent.includes('Notes')) {
                    insertAfter = header.closest('.card');
                    console.log('Found Notes card by header text');
                    break;
                }
            }
        }
        
        // If still not found, try looking for the form's last direct child that's a card
        if (!insertAfter) {
            const allCards = Array.from(financialTab.querySelectorAll('.card'));
            // Get top-level cards (not nested inside other cards)
            const topLevelCards = allCards.filter(card => {
                // Check if this card is not inside another card
                const closestCardBody = card.closest('.card-body');
                return !closestCardBody || !closestCardBody.querySelector('.card');
            });
            
            if (topLevelCards.length > 0) {
                insertAfter = topLevelCards[topLevelCards.length - 1];
                console.log('Using last top-level card as insertion point');
            }
        }
        
        // Create comps section with standard styling
        const compsSection = document.createElement('div');
        compsSection.id = 'compsSection';
        compsSection.className = 'row mt-4 mb-4'; // Add margin for separation
        compsSection.innerHTML = `
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">Comparable Properties</h5>
                    </div>
                    <div class="card-body comps-container">
                        <div id="initialCompsMessage" class="text-center">
                            <p class="mb-3">Run the comparables tool to see similar properties in the area and get an estimated After Repair Value (ARV).</p>
                            <button id="runCompsBtn" class="btn btn-primary">
                                <i class="bi bi-graph-up me-2"></i>Run Comps
                            </button>
                        </div>
                        
                        <div id="compsLoading" style="display: none;">
                            <div class="d-flex justify-content-center my-5">
                                <div class="spinner-border text-primary" role="status">
                                    <span class="visually-hidden">Loading...</span>
                                </div>
                            </div>
                            <p class="text-center">Fetching comparable properties...</p>
                        </div>
                        
                        <div id="compsError" class="alert alert-danger" style="display: none;">
                            <i class="bi bi-exclamation-triangle-fill me-2"></i>
                            <span id="compsErrorMessage">Error fetching comps</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        console.log('Insert point found:', !!insertAfter);
        
        // PLACEMENT LOGIC:
        // We need to insert after the element, not inside it
        if (insertAfter) {
            const insertionTarget = insertAfter.parentNode;
            if (insertionTarget) {
                console.log('Inserting comps section after:', insertAfter.id || insertAfter.tagName);
                
                // Check if we're inside a card-body but not already a comps section
                if (insertAfter.closest('.card-body') && !insertAfter.closest('#compsSection')) {
                    // We're inside a card-body, need to go up levels
                    const parentCard = insertAfter.closest('.card');
                    if (parentCard && parentCard.parentNode) {
                        // Insert after the entire parent card, not inside it
                        console.log('Moving up to insert after parent card');
                        parentCard.parentNode.insertBefore(compsSection, parentCard.nextSibling);
                    } else {
                        // Fallback to appending to financial tab
                        console.log('Cannot find proper insertion point, appending to financial tab');
                        financialTab.appendChild(compsSection);
                    }
                } else {
                    // Normal insertion after the target element
                    insertionTarget.insertBefore(compsSection, insertAfter.nextSibling);
                }
            } else {
                console.log('Insertion target has no parent, appending to financial tab');
                financialTab.appendChild(compsSection);
            }
        } else {
            console.log('No insertion point found, appending directly to financial tab');
            financialTab.appendChild(compsSection);
        }
        
        // Add click handler to Run Comps button
        const runCompsBtn = document.getElementById('runCompsBtn');
        if (runCompsBtn) {
            runCompsBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleRunComps();
            });
            console.log('Added event handler to Run Comps button');
        }
    },

    createCompsSectionElement() {
        const compsSection = document.createElement('div');
        compsSection.id = 'compsSection';
        compsSection.className = 'row mt-4 mb-4'; // Add margin for separation
        compsSection.style.border = '3px solid red'; // Add temporary border to make it visible
        compsSection.innerHTML = `
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-danger text-white">
                        <h5 class="mb-0">Comparable Properties</h5>
                    </div>
                    <div class="card-body comps-container">
                        <div id="initialCompsMessage" class="text-center">
                            <p class="mb-3">Run the comparables tool to see similar properties in the area and get an estimated After Repair Value (ARV).</p>
                            <button id="runCompsBtn" class="btn btn-primary btn-lg">
                                <i class="bi bi-graph-up me-2"></i>Run Comps
                            </button>
                        </div>
                        
                        <div id="compsLoading" style="display: none;">
                            <div class="d-flex justify-content-center my-5">
                                <div class="spinner-border text-primary" role="status">
                                    <span class="visually-hidden">Loading...</span>
                                </div>
                            </div>
                            <p class="text-center">Fetching comparable properties...</p>
                        </div>
                        
                        <div id="compsError" class="alert alert-danger" style="display: none;">
                            <i class="bi bi-exclamation-triangle-fill me-2"></i>
                            <span id="compsErrorMessage">Error fetching comps</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        return compsSection;
    },
    
    // Ensure the comps container exists below Notes
    ensureCompsContainer() {
        console.log('Comps Handler: Ensuring comps container exists');
        
        // Look for the financial tab
        const financialTab = document.getElementById('financial');
        if (!financialTab) {
            console.log('Financial tab not found, trying alternative approach');
            return;
        }
        
        // IMPORTANT: First check for ALL existing comps sections and remove extras
        const existingCompsSections = financialTab.querySelectorAll('#compsSection');
        console.log('Found existing comps sections:', existingCompsSections.length);
        
        // If we have more than one, remove all but the first one
        if (existingCompsSections.length > 1) {
            for (let i = 1; i < existingCompsSections.length; i++) {
                console.log('Removing duplicate comps section:', i);
                existingCompsSections[i].remove();
            }
        }
        
        // Check if we still have a comps section after cleanup
        let compsSection = document.getElementById('compsSection');
        if (compsSection) {
            console.log('Comps section already exists after cleanup');
            return;
        }
        
        // Find the notes section or other suitable insertion point
        let insertAfter = financialTab.querySelector('#notesSection');
        if (!insertAfter) {
            // Look for other potential insert points
            insertAfter = financialTab.querySelector('.form-group:last-child');
            if (!insertAfter) {
                insertAfter = financialTab.querySelector('.card:last-child');
            }
        }
        
        console.log('Insert point found:', !!insertAfter);
        
        // Create comps section
        compsSection = document.createElement('div');
        compsSection.id = 'compsSection';
        compsSection.className = 'row mt-4 mb-4'; // Add margin for separation
        compsSection.innerHTML = `
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">Comparable Properties</h5>
                    </div>
                    <div class="card-body comps-container">
                        <div id="initialCompsMessage" class="text-center">
                            <p class="mb-3">Run the comparables tool to see similar properties in the area and get an estimated After Repair Value (ARV).</p>
                            <button id="runCompsBtn" class="btn btn-primary">
                                <i class="bi bi-graph-up me-2"></i>Run Comps
                            </button>
                        </div>
                        
                        <div id="compsLoading" style="display: none;">
                            <div class="d-flex justify-content-center my-5">
                                <div class="spinner-border text-primary" role="status">
                                    <span class="visually-hidden">Loading...</span>
                                </div>
                            </div>
                            <p class="text-center">Fetching comparable properties...</p>
                        </div>
                        
                        <div id="compsError" class="alert alert-danger" style="display: none;">
                            <i class="bi bi-exclamation-triangle-fill me-2"></i>
                            <span id="compsErrorMessage">Error fetching comps</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Insert the comps section
        if (insertAfter && insertAfter.parentNode) {
            console.log('Inserting comps section after element:', insertAfter.id || insertAfter.tagName);
            insertAfter.parentNode.insertBefore(compsSection, insertAfter.nextSibling);
        } else {
            console.log('Appending comps section directly to financial tab');
            financialTab.appendChild(compsSection);
        }
        
        // Add click handler to Run Comps button
        const runCompsBtn = document.getElementById('runCompsBtn');
        if (runCompsBtn) {
            runCompsBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleRunComps();
            });
            console.log('Added event handler to Run Comps button');
        }
    },
    
    // Add fallback button if main button isn't working
    addFallbackButton() {
        // Create a floating button at the bottom-right of the screen
        const fallbackContainer = document.createElement('div');
        fallbackContainer.id = 'fallbackCompsBtn';
        fallbackContainer.style.position = 'fixed';
        fallbackContainer.style.bottom = '20px';
        fallbackContainer.style.right = '20px';
        fallbackContainer.style.zIndex = '9999';
        fallbackContainer.innerHTML = `
            <button class="btn btn-primary">
                <i class="bi bi-graph-up me-2"></i>Run Comps
            </button>
        `;
        document.body.appendChild(fallbackContainer);
        
        // Add click handler
        fallbackContainer.querySelector('button').addEventListener('click', (e) => {
            e.preventDefault();
            this.handleRunComps();
        });
        
        console.log('Added fallback comps button');
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
                    this.hasRunComps = true; // Mark as run since we have existing data
                }
            } catch (error) {
                console.error('Comps Handler: Error parsing analysis data:', error);
            }
        }
    },
    
    // Apply estimated values to analysis inputs
    applyCompsValues() {
        console.log('Applying comps values to analysis form');
        
        // Get values from displayed elements
        const estimatedValue = document.getElementById('estimatedValue')?.textContent;
        const estimatedRent = document.getElementById('estimatedRent')?.textContent;
        const maoValue = document.getElementById('maoValue')?.textContent;
        
        console.log('Retrieved values:', {
            estimatedValue,
            estimatedRent,
            maoValue
        });
        
        // Try multiple possible field IDs for ARV
        const arvValue = this.extractNumericValue(estimatedValue);
        const arvFieldsToTry = ['arv', 'after_repair_value', 'afterRepairValue'];
        let arvFieldFound = false;
        
        for (const fieldId of arvFieldsToTry) {
            if (this.setAnalysisValue(fieldId, arvValue)) {
                console.log(`Updated ARV field with ID: ${fieldId} to value: ${arvValue}`);
                arvFieldFound = true;
                break;
            }
        }
        
        if (!arvFieldFound) {
            console.log('Could not find ARV field. Trying to find field by label');
            // Try to find field by label text
            const arvLabeledFields = Array.from(document.querySelectorAll('label'))
                .filter(label => label.textContent.includes('After Repair Value') || 
                                label.textContent.includes('ARV'))
                .map(label => {
                    const forAttr = label.getAttribute('for');
                    return forAttr ? document.getElementById(forAttr) : null;
                })
                .filter(field => field !== null);
                
            if (arvLabeledFields.length > 0) {
                const field = arvLabeledFields[0];
                field.value = arvValue;
                const event = new Event('change', { bubbles: true });
                field.dispatchEvent(event);
                console.log('Updated ARV field found by label to:', arvValue);
                arvFieldFound = true;
            }
        }
        
        // Try multiple possible field IDs for purchase price
        const purchasePriceValue = this.extractNumericValue(maoValue);
        const purchasePriceFieldsToTry = ['purchase_price', 'purchasePrice'];
        let purchasePriceFieldFound = false;
        
        for (const fieldId of purchasePriceFieldsToTry) {
            if (this.setAnalysisValue(fieldId, purchasePriceValue)) {
                console.log(`Updated purchase price field with ID: ${fieldId} to value: ${purchasePriceValue}`);
                purchasePriceFieldFound = true;
                break;
            }
        }
        
        if (!purchasePriceFieldFound) {
            console.log('Could not find purchase price field. Trying to find field by label');
            // Try to find field by label text
            const purchasePriceLabeledFields = Array.from(document.querySelectorAll('label'))
                .filter(label => label.textContent.includes('Purchase Price'))
                .map(label => {
                    const forAttr = label.getAttribute('for');
                    return forAttr ? document.getElementById(forAttr) : null;
                })
                .filter(field => field !== null);
                
            if (purchasePriceLabeledFields.length > 0) {
                const field = purchasePriceLabeledFields[0];
                field.value = purchasePriceValue;
                const event = new Event('change', { bubbles: true });
                field.dispatchEvent(event);
                console.log('Updated purchase price field found by label to:', purchasePriceValue);
                purchasePriceFieldFound = true;
            }
        }
        
        // Try multiple possible field IDs for monthly rent
        const monthlyRentValue = this.extractNumericValue(estimatedRent);
        const monthlyRentFieldsToTry = ['monthly_rent', 'monthlyRent'];
        let monthlyRentFieldFound = false;
        
        for (const fieldId of monthlyRentFieldsToTry) {
            if (this.setAnalysisValue(fieldId, monthlyRentValue)) {
                console.log(`Updated monthly rent field with ID: ${fieldId} to value: ${monthlyRentValue}`);
                monthlyRentFieldFound = true;
                break;
            }
        }
        
        if (!monthlyRentFieldFound) {
            console.log('Could not find monthly rent field. Trying to find field by label');
            // Try to find field by label text
            const monthlyRentLabeledFields = Array.from(document.querySelectorAll('label'))
                .filter(label => label.textContent.includes('Monthly Rent'))
                .map(label => {
                    const forAttr = label.getAttribute('for');
                    return forAttr ? document.getElementById(forAttr) : null;
                })
                .filter(field => field !== null);
                
            if (monthlyRentLabeledFields.length > 0) {
                const field = monthlyRentLabeledFields[0];
                field.value = monthlyRentValue;
                const event = new Event('change', { bubbles: true });
                field.dispatchEvent(event);
                console.log('Updated monthly rent field found by label to:', monthlyRentValue);
                monthlyRentFieldFound = true;
            }
        }
        
        // Report results
        let message = 'Applied ';
        if (arvFieldFound) message += 'ARV, ';
        if (purchasePriceFieldFound) message += 'purchase price, ';
        if (monthlyRentFieldFound) message += 'monthly rent, ';
        
        // Clean up message
        message = message.endsWith(', ') ? message.slice(0, -2) : message;
        message += ' to analysis';
        
        // Show notification
        toastr.success(message);
        
        // If all fields were found, offer to update analysis
        if (arvFieldFound && purchasePriceFieldFound && monthlyRentFieldFound) {
            // Find the update/submit button
            const updateBtn = document.querySelector('button[type="submit"], #submitAnalysisBtn, .btn-primary:contains("Update")');
            if (updateBtn) {
                setTimeout(() => {
                    const confirmUpdate = confirm('Would you like to update the analysis with these values?');
                    if (confirmUpdate) {
                        updateBtn.click();
                    }
                }, 500);
            }
        }
    },
    


    // Helper: Extract numeric value from formatted currency
    extractNumericValue(formattedValue) {
        if (!formattedValue) return 0;
        return parseFloat(formattedValue.replace(/[$,]/g, '')) || 0;
    },
    
    // Helper: Set value in analysis form
    setAnalysisValue(fieldId, value) {
        console.log(`Attempting to set ${fieldId} to ${value}`);
        const field = document.getElementById(fieldId);
        if (field) {
            console.log(`Found field with ID ${fieldId}`);
            field.value = value;
            // Trigger change event to update calculations
            const event = new Event('change', { bubbles: true });
            field.dispatchEvent(event);
            return true;
        }
        console.log(`Field with ID ${fieldId} not found`);
        return false;
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
                this.hasRunComps = true; // Mark as run
                
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
        
        // Hide initial message
        const initialMsg = document.getElementById('initialCompsMessage');
        if (initialMsg) {
            initialMsg.style.display = 'none';
        }
        
        // Create key metrics container if it doesn't exist
        this.createOrUpdateKeyMetricsSection(compsData);
        
        // Update comps table
        this.updateComparableSalesTable(compsData);
        
        // Display rental comps if available
        if (compsData.rental_comps) {
            this.displayRentalComps(compsData.rental_comps);
        }
    },
    
    // Create or update the key metrics section
    createOrUpdateKeyMetricsSection(compsData) {
        // Get parent container
        const compsContainer = document.querySelector('.comps-container');
        if (!compsContainer) return;
        
        // CLEANUP: Remove any duplicate sections first to prevent duplication
        const existingKeyMetrics = compsContainer.querySelectorAll('#keyMetricsSection');
        if (existingKeyMetrics.length > 1) {
            console.log('Found multiple key metrics sections, removing duplicates');
            for (let i = 1; i < existingKeyMetrics.length; i++) {
                existingKeyMetrics[i].remove();
            }
        }
        
        // Check if key metrics section exists, create if not
        let keyMetricsSection = document.getElementById('keyMetricsSection');
        if (!keyMetricsSection) {
            keyMetricsSection = document.createElement('div');
            keyMetricsSection.id = 'keyMetricsSection';
            keyMetricsSection.className = 'card bg-light mb-4';
            
            // Add it as the first element in comps container
            if (compsContainer.firstChild) {
                compsContainer.insertBefore(keyMetricsSection, compsContainer.firstChild);
            } else {
                compsContainer.appendChild(keyMetricsSection);
            }
        }
        
        // Get rental data if available
        const rentalComps = compsData.rental_comps || {};
        
        // Update the key metrics content
        keyMetricsSection.innerHTML = `
            <div class="card-header bg-dark">
                <h5 class="mb-3">Key Property Metrics</h5>
            </div>
            <div class="card-body">
                <div class="row mb-3">
                    <!-- ARV Section -->
                    <div class="col-md-4">
                        <div class="card h-100 border-primary">
                            <div class="card-header bg-primary text-white">
                                <h6 class="mb-0">Estimated Value (ARV)</h6>
                            </div>
                            <div class="card-body text-center">
                                <h4 id="estimatedValue" class="text-primary mb-2">${this.formatCurrency(compsData.estimated_value)}</h4>
                                <p class="small mb-0">
                                    Range: <span id="valueLow">${this.formatCurrency(compsData.value_range_low)}</span> - 
                                    <span id="valueHigh">${this.formatCurrency(compsData.value_range_high)}</span>
                                </p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- MAO Section -->
                    <div class="col-md-4">
                        <div class="card h-100 border-success">
                            <div class="card-header bg-success text-white">
                                <h6 class="mb-0">Maximum Allowable Offer</h6>
                            </div>
                            <div class="card-body text-center">
                                <h4 id="maoValue" class="text-success mb-2">
                                    ${compsData.mao ? this.formatCurrency(compsData.mao.value) : 'N/A'}
                                </h4>
                                <p class="small mb-0">
                                    <button class="btn btn-sm btn-link" type="button" data-bs-toggle="collapse" 
                                            data-bs-target="#maoDetails" aria-expanded="false">
                                        <i class="bi bi-info-circle me-1"></i>View Calculation Details
                                    </button>
                                </p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Rent Section -->
                    <div class="col-md-4">
                        <div class="card h-100 border-info">
                            <div class="card-header bg-info text-white">
                                <h6 class="mb-0">Estimated Monthly Rent</h6>
                            </div>
                            <div class="card-body text-center">
                                <h4 id="estimatedRent" class="text-info mb-2">
                                    ${rentalComps.estimated_rent ? this.formatCurrency(rentalComps.estimated_rent) : 'N/A'}
                                </h4>
                                <p class="small mb-0">
                                    ${rentalComps.rent_range_low && rentalComps.rent_range_high ? 
                                    `Range: <span id="rentLow">${this.formatCurrency(rentalComps.rent_range_low)}</span> - 
                                    <span id="rentHigh">${this.formatCurrency(rentalComps.rent_range_high)}</span>` : ''}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- MAO Calculation Details Collapse -->
                <div class="collapse mb-3" id="maoDetails">
                    <div class="card card-body">
                        <h6 class="mb-3">MAO Calculation Details</h6>
                        <div class="table-responsive" id="maoDetailsBody">
                            ${this.generateMAODetailsTable(compsData.mao)}
                        </div>
                    </div>
                </div>
                
                <!-- Apply Values Button -->
                <div class="d-grid">
                    <button id="applyValuesBtn" class="btn btn-success">
                        <i class="bi bi-check-circle me-2"></i>Apply Values to Analysis
                    </button>
                </div>
            </div>
        `;
        
        // Add event handler to Apply Values button
        const applyValuesBtn = document.getElementById('applyValuesBtn');
        if (applyValuesBtn) {
            applyValuesBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.applyCompsValues();
            });
        }
    },
    
    // Generate MAO details table
    generateMAODetailsTable(maoData) {
        if (!maoData) return '<p class="text-muted">No MAO calculation data available</p>';
        
        return `
            <table class="table table-sm">
                <tbody>
                    <tr>
                        <td>ARV (from comps):</td>
                        <td class="text-end">${this.formatCurrency(maoData.arv)}</td>
                    </tr>
                    <tr>
                        <td>LTV Percentage:</td>
                        <td class="text-end">${maoData.ltv_percentage.toFixed(1)}%</td>
                    </tr>
                    <tr>
                        <td>Renovation Costs:</td>
                        <td class="text-end">${this.formatCurrency(maoData.renovation_costs)}</td>
                    </tr>
                    <tr>
                        <td>Monthly Holding Costs:</td>
                        <td class="text-end">${this.formatCurrency(maoData.monthly_holding_costs)}</td>
                    </tr>
                    <tr>
                        <td>Holding Period:</td>
                        <td class="text-end">${maoData.holding_months} months</td>
                    </tr>
                    <tr>
                        <td>Total Holding Costs:</td>
                        <td class="text-end">${this.formatCurrency(maoData.total_holding_costs)}</td>
                    </tr>
                    <tr>
                        <td>Closing Costs:</td>
                        <td class="text-end">${this.formatCurrency(maoData.closing_costs)}</td>
                    </tr>
                    <tr>
                        <td>Max Cash Left in Deal:</td>
                        <td class="text-end">${this.formatCurrency(maoData.max_cash_left)}</td>
                    </tr>
                </tbody>
            </table>
        `;
    },
    
    // Update comparable sales table
    updateComparableSalesTable(compsData) {
        const comparablesSectionId = 'comparableSalesSection';
        
        // CLEANUP: Remove any duplicate sections first
        const existingSections = document.querySelectorAll(`#${comparablesSectionId}`);
        if (existingSections.length > 1) {
            console.log('Found multiple comparable sales sections, removing duplicates');
            for (let i = 1; i < existingSections.length; i++) {
                existingSections[i].remove();
            }
        }
        
        const comparablesSection = document.getElementById(comparablesSectionId) || this.createComparableSalesSection(comparablesSectionId);
        
        if (!comparablesSection) return;
        
        const tableBody = document.getElementById('compsTableBody');
        const noCompsFound = document.getElementById('noCompsFound');
        
        if (compsData.comparables && compsData.comparables.length > 0) {
            comparablesSection.style.display = 'block';
            if (tableBody) {
                tableBody.innerHTML = this.generateCompsTableRows(compsData.comparables);
            }
            if (noCompsFound) {
                noCompsFound.style.display = 'none';
            }
        } else {
            if (tableBody) {
                tableBody.innerHTML = '';
            }
            if (noCompsFound) {
                noCompsFound.style.display = 'block';
            }
        }
        
        // Update run count display
        const runCountElement = document.getElementById('compsRunCount');
        if (runCountElement && compsData.run_count) {
            runCountElement.style.display = 'inline-block';
            document.getElementById('runCountValue').textContent = compsData.run_count;
        }
    },
    
    // Create comparable sales section
    createComparableSalesSection(id) {
        const compsContainer = document.querySelector('.comps-container');
        if (!compsContainer) return null;
        
        // Find the point to insert the new section (after key metrics section)
        const keyMetricsSection = document.getElementById('keyMetricsSection');
        
        // Create the section
        const section = document.createElement('div');
        section.id = id;
        section.className = 'card mb-4 mt-4';
        section.innerHTML = `
            <div class="card-header d-flex justify-content-between">
                <h5 class="mb-0">Comparable Sales</h5>
                <span id="compsRunCount" class="badge bg-info" style="display: none;">
                    Run <span id="runCountValue">0</span>
                </span>
            </div>
            <div class="card-body">
                <div id="compsTableSection">
                    <div class="table-responsive">
                        <table class="table table-sm table-striped">
                            <thead>
                                <tr>
                                    <th>Address</th>
                                    <th>Price</th>
                                    <th>Beds/Baths</th>
                                    <th>Sq Ft</th>
                                    <th>Year Built</th>
                                    <th>Date Sold</th>
                                    <th>Distance</th>
                                </tr>
                            </thead>
                            <tbody id="compsTableBody">
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div id="noCompsFound" style="display: none;" class="alert alert-warning">
                    No comparable properties found in the area.
                </div>
            </div>
        `;
        
        // Insert after key metrics section
        if (keyMetricsSection && keyMetricsSection.nextSibling) {
            compsContainer.insertBefore(section, keyMetricsSection.nextSibling);
        } else {
            compsContainer.appendChild(section);
        }
        
        return section;
    },
    
    // Display rental comps data
    displayRentalComps(rentalComps) {
        if (!rentalComps) {
            console.log('No rental comps data to display');
            return;
        }
        
        console.log('Displaying rental comps:', rentalComps);
        
        // Create or find rental section
        const rentalSectionId = 'rentalCompsSection';
        
        // CLEANUP: Remove any duplicate sections first
        const existingSections = document.querySelectorAll(`#${rentalSectionId}`);
        if (existingSections.length > 1) {
            console.log('Found multiple rental comps sections, removing duplicates');
            for (let i = 1; i < existingSections.length; i++) {
                existingSections[i].remove();
            }
        }
        
        let rentalSection = document.getElementById(rentalSectionId);
        
        // If section doesn't exist, create it
        if (!rentalSection) {
            rentalSection = this.createRentalCompsSection(rentalSectionId, rentalComps);
        } else {
            // Update existing section
            this.updateRentalCompsSection(rentalSection, rentalComps);
        }
    },
    
    // Create rental comps section
    createRentalCompsSection(id, rentalComps) {
        const compsContainer = document.querySelector('.comps-container');
        if (!compsContainer) return null;
        
        // Create rental comps section
        const section = document.createElement('div');
        section.id = id;
        section.className = 'card mt-4';
        section.innerHTML = `
            <div class="card-header">
                <h5 class="mb-0">Comparable Rentals</h5>
            </div>
            <div class="card-body">
                <div id="rentalTableSection">
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
                
                <div id="noRentalsFound" style="display: none;" class="alert alert-warning">
                    No comparable rentals found in the area.
                </div>
            </div>
        `;
        
        // Add to container at the end
        compsContainer.appendChild(section);
        
        // Populate with data
        this.updateRentalCompsSection(section, rentalComps);
        
        return section;
    },
    
    // Update existing rental comps section
    updateRentalCompsSection(section, rentalComps) {
        const rentalTableBody = section.querySelector('#rentalTableBody');
        const noRentalsFound = section.querySelector('#noRentalsFound');
        const rentalTableSection = section.querySelector('#rentalTableSection');
        
        if (rentalComps.comparable_rentals && rentalComps.comparable_rentals.length > 0) {
            if (rentalTableBody) {
                rentalTableBody.innerHTML = this.generateRentalTableRows(rentalComps.comparable_rentals);
            }
            if (rentalTableSection) rentalTableSection.style.display = 'block';
            if (noRentalsFound) noRentalsFound.style.display = 'none';
        } else {
            if (rentalTableSection) rentalTableSection.style.display = 'none';
            if (noRentalsFound) noRentalsFound.style.display = 'block';
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
        
        // Since we're displaying existing comps, set the flag
        this.hasRunComps = true;
        
        // Update display with the data
        this.updateCompsDisplay(compsData);
    },
    
    // Set loading state
    setLoadingState(isLoading) {
        const loadingElement = document.getElementById('compsLoading');
        const runCompsBtn = document.getElementById('runCompsBtn');
        const fallbackBtn = document.getElementById('fallbackCompsBtn')?.querySelector('button');
        
        if (loadingElement) {
            loadingElement.style.display = isLoading ? 'block' : 'none';
        }
        
        if (runCompsBtn) {
            runCompsBtn.disabled = isLoading;
            if (isLoading) {
                runCompsBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
            } else {
                runCompsBtn.innerHTML = '<i class="bi bi-graph-up me-2"></i>Run Comps';
            }
        }
        
        if (fallbackBtn) {
            fallbackBtn.disabled = isLoading;
            if (isLoading) {
                fallbackBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
            } else {
                fallbackBtn.innerHTML = '<i class="bi bi-graph-up me-2"></i>Run Comps';
            }
        }
        
        if (isLoading) {
            const errorDiv = document.getElementById('compsError');
            const initialMessage = document.getElementById('initialCompsMessage');
            
            if (errorDiv) errorDiv.style.display = 'none';
            if (initialMessage) initialMessage.style.display = 'none';
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