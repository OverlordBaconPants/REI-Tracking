// property-details.js
// This new file will handle the workflow for the property details tab

const PropertyDetailsHandler = {
    // State to track property details completion
    state: {
        detailsComplete: false,
        compsRun: false,
        compsData: null,
        stepActive: 'details' // 'details', 'comps', 'financial'
    },

    
    // Initialize the property details handler
    init() {
        console.log('PropertyDetails: Initializing property details workflow - THIS SHOULD BE VISIBLE');

        // Create workflow UI
        this.createWorkflowUI();
        
        // Set up event listeners
        this.attachEventListeners();
        
        // If this is an edit with existing comps, update state
        this.checkExistingComps();
        
        return true;
    },
    
    // Create the workflow UI
    createWorkflowUI() {
        console.log('PropertyDetails: Creating workflow UI');
        
        // Find the property details tab
        const propertyTab = document.getElementById('property');
        if (!propertyTab) {
            console.error('PropertyDetails: Property tab not found');
            return;
        }
        
        // Create workflow steps container
        const workflowSteps = document.createElement('div');
        workflowSteps.className = 'workflow-steps mb-4';
        workflowSteps.innerHTML = `
            <div class="d-flex justify-content-between position-relative mb-2">
                <div class="workflow-step active" id="details-step">
                    <div class="step-number">1</div>
                    <div class="step-label">Property Details</div>
                </div>
                <div class="workflow-step" id="comps-step">
                    <div class="step-number">2</div>
                    <div class="step-label">Run Comps</div>
                </div>
                <div class="workflow-step" id="financial-step">
                    <div class="step-number">3</div>
                    <div class="step-label">Financial Analysis</div>
                </div>
                <div class="workflow-line"></div>
            </div>
        `;
        
        // Add CSS for the workflow
        const styleElement = document.createElement('style');
        styleElement.textContent = `
            .workflow-steps {
                position: relative;
            }
            .workflow-line {
                position: absolute;
                top: 25px;
                left: 50px;
                right: 50px;
                height: 3px;
                background-color: #e9ecef;
                z-index: 1;
            }
            .workflow-step {
                text-align: center;
                position: relative;
                z-index: 2;
                background-color: #fff;
                padding: 0 15px;
            }
            .step-number {
                width: 50px;
                height: 50px;
                border-radius: 50%;
                background-color: #e9ecef;
                color: #6c757d;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto;
                font-weight: bold;
                font-size: 1.2rem;
            }
            .step-label {
                margin-top: 8px;
                font-weight: 500;
                color: #6c757d;
            }
            .workflow-step.active .step-number {
                background-color: #007bff;
                color: #fff;
            }
            .workflow-step.active .step-label {
                color: #007bff;
            }
            .workflow-step.completed .step-number {
                background-color: #28a745;
                color: #fff;
            }
            .workflow-step.completed .step-label {
                color: #28a745;
            }
            .action-buttons {
                margin-top: 1.5rem;
                display: flex;
                justify-content: space-between;
            }
            #comps-container {
                display: none;
                margin-top: 1.5rem;
            }
            .comp-selection-box {
                border: 1px solid #dee2e6;
                border-radius: 0.25rem;
                padding: 1rem;
                margin-bottom: 1rem;
                background-color: #f8f9fa;
            }
            .comp-selection-box h5 {
                margin-bottom: 1rem;
                color: #495057;
            }
            .comp-btn {
                margin-top: 0.5rem;
            }
        `;
        
        // Add action buttons at the bottom of the property details section
        const actionButtons = document.createElement('div');
        actionButtons.className = 'action-buttons mt-4';
        actionButtons.innerHTML = `
            <button type="button" class="btn btn-secondary" id="back-to-details-btn" style="display: none;">
                <i class="bi bi-arrow-left me-2"></i>Back to Details
            </button>
            <button type="button" class="btn btn-primary" id="continue-to-comps-btn">
                Continue to Comps<i class="bi bi-arrow-right ms-2"></i>
            </button>
        `;
        
        // Create comps container that will be shown after property details
        const compsContainer = document.createElement('div');
        compsContainer.id = 'comps-container';
        compsContainer.innerHTML = `
            <div class="comp-selection-box" id="mao-selection" style="display: none;">
                <h5>Maximum Allowable Offer</h5>
                <p>Based on the comps, the calculated Maximum Allowable Offer is: <strong id="mao-value">$0</strong></p>
                <button type="button" class="btn btn-success btn-sm comp-btn" id="use-mao-btn">
                    <i class="bi bi-check-circle me-2"></i>Use as Purchase Price
                </button>
            </div>
            
            <div class="comp-selection-box" id="arv-selection" style="display: none;">
                <h5>After Repair Value</h5>
                <p>Based on the comps, the estimated After Repair Value is: <strong id="arv-value">$0</strong></p>
                <button type="button" class="btn btn-success btn-sm comp-btn" id="use-arv-btn">
                    <i class="bi bi-check-circle me-2"></i>Use as ARV
                </button>
            </div>
            
            <div class="comp-selection-box" id="rent-selection" style="display: none;">
                <h5>Estimated Monthly Rent</h5>
                <p>Based on the comps, the estimated Monthly Rent is: <strong id="rent-value">$0</strong></p>
                <button type="button" class="btn btn-success btn-sm comp-btn" id="use-rent-btn">
                    <i class="bi bi-check-circle me-2"></i>Use as Monthly Rent
                </button>
            </div>
            
            <div class="action-buttons mt-4">
                <button type="button" class="btn btn-primary" id="continue-to-financial-btn">
                    Continue to Financial Analysis<i class="bi bi-arrow-right ms-2"></i>
                </button>
            </div>
        `;
        
        // Insert elements into the DOM
        document.head.appendChild(styleElement);
        propertyTab.insertBefore(workflowSteps, propertyTab.firstChild);
        propertyTab.appendChild(actionButtons);
        propertyTab.appendChild(compsContainer);
    },
    
    // Attach event listeners
    attachEventListeners() {
        console.log('PropertyDetails: Attaching event listeners');
        
        // Continue to comps button
        const continueToCompsBtn = document.getElementById('continue-to-comps-btn');
        if (continueToCompsBtn) {
            continueToCompsBtn.addEventListener('click', () => this.continueToComps());
        }
        
        // Back to details button
        const backToDetailsBtn = document.getElementById('back-to-details-btn');
        if (backToDetailsBtn) {
            backToDetailsBtn.addEventListener('click', () => this.backToDetails());
        }
        
        // Continue to financial button
        const continueToFinancialBtn = document.getElementById('continue-to-financial-btn');
        if (continueToFinancialBtn) {
            continueToFinancialBtn.addEventListener('click', () => this.continueToFinancial());
        }
        
        // Use MAO as Purchase Price button
        const useMaoBtn = document.getElementById('use-mao-btn');
        if (useMaoBtn) {
            useMaoBtn.addEventListener('click', () => this.useMAOasPurchasePrice());
        }
        
        // Use ARV button
        const useArvBtn = document.getElementById('use-arv-btn');
        if (useArvBtn) {
            useArvBtn.addEventListener('click', () => this.useARVasARV());
        }
        
        // Use Rent button
        const useRentBtn = document.getElementById('use-rent-btn');
        if (useRentBtn) {
            useRentBtn.addEventListener('click', () => this.useRentAsMonthlyRent());
        }
        
        // Listen for successful comps update
        document.addEventListener('comps-updated', (event) => {
            console.log('PropertyDetails: Comps updated event received');
            if (event.detail && event.detail.compsData) {
                this.handleCompsUpdated(event.detail.compsData);
            }
        });
    },
    
    // Check for existing comps data
    checkExistingComps() {
        console.log('PropertyDetails: Checking for existing comps data');
        
        const analysis = document.getElementById('analysis-data')?.textContent;
        if (analysis) {
            try {
                const data = JSON.parse(analysis);
                if (data.comps_data) {
                    this.state.compsRun = true;
                    this.state.compsData = data.comps_data;
                    
                    // Update UI to reflect comps have been run
                    const compsStep = document.getElementById('comps-step');
                    if (compsStep) {
                        compsStep.classList.add('completed');
                    }
                    
                    console.log('PropertyDetails: Found existing comps data');
                }
            } catch (error) {
                console.error('PropertyDetails: Error parsing analysis data:', error);
            }
        }
    },
    
    // Continue to comps step
    continueToComps() {
        console.log('PropertyDetails: Continuing to comps step');
        
        // Validate required property details first
        if (!this.validatePropertyDetails()) {
            toastr.error('Please complete all required property details first');
            return;
        }
        
        // Update state
        this.state.detailsComplete = true;
        this.state.stepActive = 'comps';
        
        // Update UI
        this.updateStepUI('comps');
        
        // Show the comps container
        const compsContainer = document.getElementById('comps-container');
        if (compsContainer) {
            compsContainer.style.display = 'block';
        }
        
        // Hide property form fields but keep the section visible
        const formGroups = document.querySelectorAll('#property .form-group:not(.workflow-steps)');
        formGroups.forEach(group => {
            group.style.display = 'none';
        });
        
        // Update buttons
        document.getElementById('continue-to-comps-btn').style.display = 'none';
        document.getElementById('back-to-details-btn').style.display = 'block';
        
        // Scroll to comps
        window.scrollTo({
            top: document.getElementById('property').offsetTop - 20,
            behavior: 'smooth'
        });
        
        // If comps have already been run, show the values
        if (this.state.compsRun && this.state.compsData) {
            this.displayCompsSelections(this.state.compsData);
        }
    },
    
    // Go back to property details
    backToDetails() {
        console.log('PropertyDetails: Going back to property details');
        
        // Update state
        this.state.stepActive = 'details';
        
        // Update UI
        this.updateStepUI('details');
        
        // Show property form fields
        const formGroups = document.querySelectorAll('#property .form-group:not(.workflow-steps)');
        formGroups.forEach(group => {
            group.style.display = 'block';
        });
        
        // Hide the comps container
        const compsContainer = document.getElementById('comps-container');
        if (compsContainer) {
            compsContainer.style.display = 'none';
        }
        
        // Update buttons
        document.getElementById('continue-to-comps-btn').style.display = 'block';
        document.getElementById('back-to-details-btn').style.display = 'none';
    },
    
    // Continue to financial analysis
    continueToFinancial() {
        console.log('PropertyDetails: Continuing to financial analysis');
        
        // Update state
        this.state.stepActive = 'financial';
        
        // Update UI
        this.updateStepUI('financial');
        
        // Switch to financial tab
        const financialTab = document.getElementById('financial-tab');
        if (financialTab) {
            financialTab.click();
        }
    },
    
    // Handle comps updated event
    handleCompsUpdated(compsData) {
        console.log('PropertyDetails: Handling comps updated event');
        
        // Update state
        this.state.compsRun = true;
        this.state.compsData = compsData;
        
        // Mark comps step as completed
        const compsStep = document.getElementById('comps-step');
        if (compsStep) {
            compsStep.classList.add('completed');
        }
        
        // Display comps selections
        this.displayCompsSelections(compsData);
    },
    
    // Display comps selections
    displayCompsSelections(compsData) {
        console.log('PropertyDetails: Displaying comps selections', compsData);
        
        // Show MAO if available
        if (compsData.mao && compsData.mao.value) {
            const maoSelection = document.getElementById('mao-selection');
            const maoValue = document.getElementById('mao-value');
            
            if (maoSelection && maoValue) {
                maoSelection.style.display = 'block';
                maoValue.textContent = this.formatCurrency(compsData.mao.value);
            }
        }
        
        // Show ARV if available (estimated value from comps)
        if (compsData.estimated_value) {
            const arvSelection = document.getElementById('arv-selection');
            const arvValue = document.getElementById('arv-value');
            
            if (arvSelection && arvValue) {
                arvSelection.style.display = 'block';
                arvValue.textContent = this.formatCurrency(compsData.estimated_value);
            }
        }
        
        // Show estimated rent if available
        if (compsData.rental_comps && compsData.rental_comps.estimated_rent) {
            const rentSelection = document.getElementById('rent-selection');
            const rentValue = document.getElementById('rent-value');
            
            if (rentSelection && rentValue) {
                rentSelection.style.display = 'block';
                rentValue.textContent = this.formatCurrency(compsData.rental_comps.estimated_rent);
            }
        }
    },
    
    // Use MAO as Purchase Price
    useMAOasPurchasePrice() {
        console.log('PropertyDetails: Using MAO as Purchase Price');
        
        if (!this.state.compsData || !this.state.compsData.mao) {
            toastr.error('MAO data not available');
            return;
        }
        
        const maoValue = this.state.compsData.mao.value;
        const purchasePriceField = document.getElementById('purchase_price');
        
        if (purchasePriceField) {
            // Update purchase price with MAO
            purchasePriceField.value = Math.round(maoValue); // Round to nearest dollar
            
            // Trigger change event to ensure calculations update
            const event = new Event('change', { bubbles: true });
            purchasePriceField.dispatchEvent(event);
            
            // Show success message
            toastr.success('Purchase price updated to Maximum Allowable Offer');
            
            // Mark button as used
            document.getElementById('use-mao-btn').classList.add('btn-outline-success');
            document.getElementById('use-mao-btn').classList.remove('btn-success');
            document.getElementById('use-mao-btn').innerHTML = '<i class="bi bi-check-circle me-2"></i>Applied';
        } else {
            toastr.error('Purchase price field not found');
        }
    },
    
    // Use ARV value
    useARVasARV() {
        console.log('PropertyDetails: Using estimated value as ARV');
        
        if (!this.state.compsData || !this.state.compsData.estimated_value) {
            toastr.error('ARV data not available');
            return;
        }
        
        const arvValue = this.state.compsData.estimated_value;
        const arvField = document.getElementById('after_repair_value');
        
        if (arvField) {
            // Update ARV field
            arvField.value = Math.round(arvValue); // Round to nearest dollar
            
            // Trigger change event
            const event = new Event('change', { bubbles: true });
            arvField.dispatchEvent(event);
            
            // Show success message
            toastr.success('After Repair Value updated to estimated value from comps');
            
            // Mark button as used
            document.getElementById('use-arv-btn').classList.add('btn-outline-success');
            document.getElementById('use-arv-btn').classList.remove('btn-success');
            document.getElementById('use-arv-btn').innerHTML = '<i class="bi bi-check-circle me-2"></i>Applied';
        } else {
            toastr.error('After Repair Value field not found');
        }
    },
    
    // Use estimated rent as monthly rent
    useRentAsMonthlyRent() {
        console.log('PropertyDetails: Using estimated rent as monthly rent');
        
        if (!this.state.compsData || 
            !this.state.compsData.rental_comps || 
            !this.state.compsData.rental_comps.estimated_rent) {
            toastr.error('Rental data not available');
            return;
        }
        
        const rentValue = this.state.compsData.rental_comps.estimated_rent;
        const rentField = document.getElementById('monthly_rent');
        
        if (rentField) {
            // Update monthly rent field
            rentField.value = Math.round(rentValue); // Round to nearest dollar
            
            // Trigger change event
            const event = new Event('change', { bubbles: true });
            rentField.dispatchEvent(event);
            
            // Show success message
            toastr.success('Monthly rent updated to estimated rent from comps');
            
            // Mark button as used
            document.getElementById('use-rent-btn').classList.add('btn-outline-success');
            document.getElementById('use-rent-btn').classList.remove('btn-success');
            document.getElementById('use-rent-btn').innerHTML = '<i class="bi bi-check-circle me-2"></i>Applied';
        } else {
            toastr.error('Monthly rent field not found');
        }
    },
    
    // Update step UI
    updateStepUI(activeStep) {
        console.log('PropertyDetails: Updating step UI to', activeStep);
        
        // Get all step elements
        const detailsStep = document.getElementById('details-step');
        const compsStep = document.getElementById('comps-step');
        const financialStep = document.getElementById('financial-step');
        
        // Remove active class from all steps
        detailsStep.classList.remove('active');
        compsStep.classList.remove('active');
        financialStep.classList.remove('active');
        
        // Add appropriate classes based on current step
        switch(activeStep) {
            case 'details':
                detailsStep.classList.add('active');
                break;
            case 'comps':
                if (this.state.detailsComplete) {
                    detailsStep.classList.add('completed');
                }
                compsStep.classList.add('active');
                break;
            case 'financial':
                if (this.state.detailsComplete) {
                    detailsStep.classList.add('completed');
                }
                if (this.state.compsRun) {
                    compsStep.classList.add('completed');
                }
                financialStep.classList.add('active');
                break;
        }
    },
    
    // Validate property details
    validatePropertyDetails() {
        console.log('PropertyDetails: Validating property details');
        
        // Get required fields
        const requiredFields = [
            { id: 'analysis_name', label: 'Analysis Name' },
            { id: 'address', label: 'Property Address' },
            { id: 'property_type', label: 'Property Type' }
        ];
        
        // Check each required field
        let isValid = true;
        let missingFields = [];
        
        requiredFields.forEach(field => {
            const element = document.getElementById(field.id);
            if (!element || !element.value.trim()) {
                isValid = false;
                missingFields.push(field.label);
                
                // Highlight the field
                if (element) {
                    element.classList.add('is-invalid');
                }
            } else if (element) {
                element.classList.remove('is-invalid');
            }
        });
        
        // Show error message if validation fails
        if (!isValid) {
            toastr.error(`Please complete the following required fields: ${missingFields.join(', ')}`);
        }
        
        return isValid;
    },
    
    // Format currency
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
    }
};

export default PropertyDetailsHandler;