const padSplitExpensesHTML = `
    <div class="mt-4">
        <h6 class="mb-3">PadSplit-Specific Expenses</h6>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label for="padsplit_platform_percentage" class="form-label">PadSplit Platform (%)</label>
                <input type="number" class="form-control" id="padsplit_platform_percentage" 
                       name="padsplit_platform_percentage" value="12" min="0" max="100" 
                       step="0.5" required>
            </div>
            <div class="col-md-6 mb-3">
                <label for="utilities" class="form-label">Utilities</label>
                <input type="number" class="form-control" id="utilities" name="utilities" 
                       placeholder="Monthly utility costs" required>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label for="internet" class="form-label">Internet</label>
                <input type="number" class="form-control" id="internet" name="internet" 
                       placeholder="Monthly Internet costs" required>
            </div>
            <div class="col-md-6 mb-3">
                <label for="cleaning_costs" class="form-label">Cleaning Costs</label>
                <input type="number" class="form-control" id="cleaning_costs" name="cleaning_costs" 
                       placeholder="Monthly costs to clean common areas" required>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label for="pest_control" class="form-label">Pest Control</label>
                <input type="number" class="form-control" id="pest_control" name="pest_control" 
                       placeholder="Monthly pest control costs" required>
            </div>
            <div class="col-md-6 mb-3">
                <label for="landscaping" class="form-label">Landscaping</label>
                <input type="number" class="form-control" id="landscaping" name="landscaping" 
                       placeholder="Monthly landscaping budget" required>
            </div>
        </div>
    </div>
`;

window.analysisModule = {
    initialAnalysisType: null,
    currentAnalysisId: null,
    isSubmitting: false,
    typeChangeInProgress: false,

    init: function() {
        console.log('Analysis module initializing');
        this.initToastr();
        
        const analysisForm = document.querySelector('#analysisForm');
        if (analysisForm) {
            console.log('Analysis form found');
            
            // Remove any existing event listeners
            analysisForm.replaceWith(analysisForm.cloneNode(true));
            
            // Get the fresh form reference after replacement
            const freshForm = document.querySelector('#analysisForm');
            
            // Get analysis ID from URL
            const urlParams = new URLSearchParams(window.location.search);
            const analysisId = urlParams.get('analysis_id');
            console.log('URL Analysis ID:', analysisId);
            
            if (analysisId) {
                console.log('Edit mode detected - loading analysis:', analysisId);
                this.currentAnalysisId = analysisId;
                freshForm.setAttribute('data-analysis-id', analysisId);
                
                // Set up form for edit mode
                freshForm.addEventListener('submit', (event) => {
                    this.handleEditSubmit(event, analysisId);
                });
                
                // Load existing analysis data
                this.loadAnalysisData(analysisId);
            } else {
                // Create mode
                freshForm.addEventListener('submit', (event) => {
                    this.handleSubmit(event);
                });
            }
            
            // Initialize handlers
            this.initAddressAutocomplete();
            this.initLoanHandlers();
            this.initAnalysisTypeHandler();
            this.initTabHandling();
            this.initReportEventHandlers();
        } else {
            console.error('Analysis form not found');
        }
    },

    downloadPdf: function(analysisId) {
        console.log('Downloading PDF for analysis:', analysisId);
        if (!analysisId) {
            console.error('No analysis ID available');
            toastr.error('Unable to generate PDF: No analysis ID found');
            return;
        }
        
        // Get button reference
        const downloadBtn = document.querySelector('.card-header button');
        if (downloadBtn) {
            // Show loading state
            downloadBtn.disabled = true;
            downloadBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generating PDF...';
        }
        
        // Create hidden form for download
        const form = document.createElement('form');
        form.method = 'GET';
        form.action = `/analyses/generate_pdf/${analysisId}`;
        document.body.appendChild(form);
        
        // Submit form to trigger download
        form.submit();
        document.body.removeChild(form);
        
        // Reset button after delay
        setTimeout(() => {
            if (downloadBtn) {
                downloadBtn.disabled = false;
                downloadBtn.innerHTML = 'Download PDF';
            }
        }, 2000);
    },

    initRefinanceCalculations: function() {
        // Get relevant elements
        const arvInput = document.getElementById('after_repair_value');
        const ltvInput = document.getElementById('refinance_ltv_percentage');
        const loanAmountInput = document.getElementById('refinance_loan_amount');
        const downPaymentInput = document.getElementById('refinance_down_payment');
        const closingCostsInput = document.getElementById('refinance_closing_costs');
    
        // Function to update refinance calculations
        const updateRefinanceCalcs = () => {
            const arv = parseFloat(arvInput.value) || 0;
            const ltv = parseFloat(ltvInput.value) || 0;
    
            // Calculate loan amount
            const loanAmount = (arv * ltv) / 100;
            loanAmountInput.value = loanAmount.toFixed(2);
    
            // Calculate down payment
            const downPayment = (arv * (100 - ltv)) / 100;
            downPaymentInput.value = downPayment.toFixed(2);
    
            // Calculate closing costs (5%)
            const closingCosts = loanAmount * 0.05;
            closingCostsInput.value = closingCosts.toFixed(2);
        };
    
        // Add event listeners
        if (arvInput && ltvInput) {
            arvInput.addEventListener('input', updateRefinanceCalcs);
            ltvInput.addEventListener('input', updateRefinanceCalcs);
        }
    },

    getAnalysisIdFromUrl: function() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('analysis_id');
    },

    // Configure toastr options
    initToastr: function() {
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
    },

    initTabHandling: function() {
        // Use this.getAnalysisIdFromUrl() instead
        const analysisId = this.getAnalysisIdFromUrl();
        if (!analysisId) return;
    
        const reportTab = document.getElementById('reports-tab');
        const financialTab = document.getElementById('financial-tab');
    
        if (reportTab) {
            reportTab.addEventListener('click', () => {
                this.currentAnalysisId = analysisId;
                console.log('Report tab clicked, analysis ID:', this.currentAnalysisId);
            });
        }
    
        if (financialTab) {
            financialTab.addEventListener('click', () => {
                this.currentAnalysisId = analysisId;
                console.log('Financial tab clicked, analysis ID:', this.currentAnalysisId);
            });
        }
    },

    initAddressAutocomplete: function() {
        console.log('Initializing address autocomplete');
        const addressInput = document.getElementById('property_address');
        const resultsList = document.getElementById('addressSuggestions');
        let timeoutId;

        if (addressInput && resultsList) {
            console.log('Address input and results list found');
            addressInput.addEventListener('input', function() {
                clearTimeout(timeoutId);
                timeoutId = setTimeout(() => {
                    const query = this.value;
                    if (query.length > 2) {
                        console.log('Making API call for:', query);
                        fetch(`/api/autocomplete?query=${encodeURIComponent(query)}`)
                            .then(response => {
                                console.log('Response status:', response.status);
                                if (!response.ok) {
                                    return response.text().then(text => {
                                        throw new Error(`HTTP error! status: ${response.status}, message: ${text}`);
                                    });
                                }
                                return response.json();
                            })
                            .then(response => {
                                console.log('API response:', response);
                                resultsList.innerHTML = '';
                                
                                if (response.status === 'success' && response.data && Array.isArray(response.data)) {
                                    response.data.forEach(result => {
                                        const li = document.createElement('li');
                                        li.textContent = result.formatted;
                                        li.addEventListener('click', function() {
                                            addressInput.value = this.textContent;
                                            resultsList.innerHTML = '';
                                        });
                                        resultsList.appendChild(li);
                                    });
                                    
                                    if (response.data.length === 0) {
                                        resultsList.innerHTML = '<li class="no-results">No matches found</li>';
                                    }
                                } else {
                                    throw new Error('Invalid response format');
                                }
                            })
                            .catch(error => {
                                console.error('Error:', error);
                                resultsList.innerHTML = `<li class="error">Error fetching results: ${error.message}</li>`;
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
        } else {
            console.error('Address input or results list not found', {
                addressInput: !!addressInput,
                resultsList: !!resultsList
            });
        }
    },

    handleTypeChange: async function(newType) {
        const financialTab = document.getElementById('financial');
        if (!financialTab) return;
        
        try {
            // Get current analysis data
            const currentForm = document.getElementById('analysisForm');
            const analysisId = currentForm.getAttribute('data-analysis-id');
            
            if (!analysisId) return;
    
            // Create new analysis with the new type
            const formData = new FormData(currentForm);
            const analysisData = {
                ...Object.fromEntries(formData.entries()),
                id: analysisId,
                analysis_type: newType
            };
            
            // Make API call to create new analysis
            const response = await fetch('/analyses/update_analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(analysisData)
            });
            
            const data = await response.json();
            if (data.success) {
                // Load form fields for new type
                this.loadTypeFields(newType);

                // Initialize calculations if BRRRR type
                if (newType.includes('BRRRR')) {
                    this.initRefinanceCalculations();
                }
                
                // Update form with new analysis data
                currentForm.setAttribute('data-analysis-id', data.analysis.id);
                this.currentAnalysisId = data.analysis.id;
                
                // Wait for DOM to be ready before populating fields
                setTimeout(() => {
                    this.populateFormFields(data.analysis);
                }, 100);
                
                toastr.success(`Created new ${newType} analysis`);
            } else {
                throw new Error(data.message || 'Error creating new analysis');
            }
        } catch (error) {
            console.error('Error:', error);
            toastr.error(error.message);
            // Reset to original type
            const analysisType = document.getElementById('analysis_type');
            if (analysisType) {
                analysisType.value = this.initialAnalysisType;
            }
        }
    },

    initAnalysisTypeHandler: function() {
        const analysisType = document.getElementById('analysis_type');
        const financialTab = document.getElementById('financial');
        
        if (analysisType && financialTab) {
            // Remove any existing event listeners by cloning
            const newAnalysisType = analysisType.cloneNode(true);
            analysisType.parentNode.replaceChild(newAnalysisType, analysisType);
            
            // Store initial value
            this.initialAnalysisType = newAnalysisType.value;
            console.log('Initial analysis type:', this.initialAnalysisType);
            
            // Load initial fields
            this.loadTypeFields(this.initialAnalysisType);
            
            // Check if we're in edit mode by looking for an existing analysis ID
            const isEditMode = () => {
                return !!(this.currentAnalysisId || 
                         this.getAnalysisIdFromUrl() || 
                         document.getElementById('analysisForm')?.getAttribute('data-analysis-id'));
            };
            
            // Set up event listener for changes
            newAnalysisType.addEventListener('change', async (e) => {
                // Prevent multiple concurrent changes
                if (this.typeChangeInProgress) {
                    console.log('Type change already in progress');
                    return;
                }
                
                const newType = e.target.value;
                
                // If we're in create mode, just update the fields
                if (!isEditMode()) {
                    console.log('Create mode - updating fields without confirmation');
                    this.loadTypeFields(newType);
                    this.initialAnalysisType = newType;
                    return;
                }
                
                // Only prompt if actually changing types in edit mode
                if (newType === this.initialAnalysisType) {
                    return;
                }
                
                try {
                    this.typeChangeInProgress = true;
                    
                    const confirmed = await new Promise(resolve => {
                        const modal = document.createElement('div');
                        modal.className = 'modal fade';
                        modal.innerHTML = `
                            <div class="modal-dialog">
                                <div class="modal-content">
                                    <div class="modal-header">
                                        <h5 class="modal-title">Change Analysis Type</h5>
                                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                                    </div>
                                    <div class="modal-body">
                                        Changing analysis type will create a fresh ${newType} analysis for this property. Do you want to proceed?
                                    </div>
                                    <div class="modal-footer gap-2">
                                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                        <button type="button" class="btn btn-primary" id="confirmTypeChange">Yes, Proceed</button>
                                    </div>
                                </div>
                            </div>
                        `;
                        document.body.appendChild(modal);
                        
                        const modalInstance = new bootstrap.Modal(modal);
                        modalInstance.show();
                        
                        modal.querySelector('#confirmTypeChange').addEventListener('click', () => {
                            modalInstance.hide();
                            resolve(true);
                        });
                        
                        modal.addEventListener('hidden.bs.modal', () => {
                            resolve(false);
                            modal.remove();
                        });
                    });
    
                    if (!confirmed) {
                        // Reset to original type without triggering change event
                        e.target.value = this.initialAnalysisType;
                        return;
                    }
    
                    // Create new analysis
                    const currentForm = document.getElementById('analysisForm');
                    const analysisId = currentForm.getAttribute('data-analysis-id');
                    
                    if (!analysisId) return;
    
                    const formData = new FormData(currentForm);
                    const analysisData = {
                        ...Object.fromEntries(formData.entries()),
                        id: analysisId,
                        analysis_type: newType
                    };
                    
                    const response = await fetch('/analyses/update_analysis', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(analysisData)
                    });
                    
                    const data = await response.json();
                    if (data.success) {
                        // Update UI first
                        this.loadTypeFields(newType);
                        currentForm.setAttribute('data-analysis-id', data.analysis.id);
                        this.currentAnalysisId = data.analysis.id;
                        
                        // Then update the type selector to match
                        this.initialAnalysisType = newType;
                        e.target.value = newType;
                        
                        // Finally populate fields
                        setTimeout(() => {
                            this.populateFormFields(data.analysis);
                        }, 100);
                        
                        toastr.success(`Created new ${newType} analysis`);
                    } else {
                        throw new Error(data.message || 'Error creating new analysis');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    toastr.error(error.message);
                    // Reset to original type
                    e.target.value = this.initialAnalysisType;
                } finally {
                    this.typeChangeInProgress = false;
                }
            });
        } else {
            console.error('Required elements not found:', {
                analysisType: !!analysisType,
                financialTab: !!financialTab
            });
        }
    },

    loadTypeFields: function(type) {
        const financialTab = document.getElementById('financial');
        if (!financialTab) return;
        
        let htmlContent;
        switch(type) {
            case 'Maximum Allowable Offer':
                htmlContent = this.getMAOHTML();
                financialTab.innerHTML = htmlContent;
                
                const reportsTab = document.getElementById('reports-tab');
                const reportsContent = document.getElementById('reports');
                const submitBtn = document.getElementById('submitAnalysisBtn');
                
                if (reportsTab) reportsTab.style.display = 'none';
                if (reportsContent) reportsContent.style.display = 'none';
                if (submitBtn) submitBtn.style.display = 'none';
                
                setTimeout(() => this.initMAOCalculation(), 100);
                break;
    
            case 'Long-Term Rental':
                htmlContent = this.getLongTermRentalHTML();
                break;
                
            case 'PadSplit LTR':
                htmlContent = this.getPadSplitLTRHTML();
                break;
                
            case 'BRRRR':
                htmlContent = this.getBRRRRHTML();
                break;
                
            case 'PadSplit BRRRR':
                htmlContent = this.getPadSplitBRRRRHTML();
                break;
                
            default:
                htmlContent = '<p>Financial details for this analysis type are not yet implemented.</p>';
        }
    
        if (type !== 'Maximum Allowable Offer') {
            financialTab.innerHTML = htmlContent;
            
            const reportsTab = document.getElementById('reports-tab');
            const reportsContent = document.getElementById('reports');
            const submitBtn = document.getElementById('submitAnalysisBtn');
            
            if (reportsTab) reportsTab.style.display = '';
            if (reportsContent) reportsContent.style.display = '';
            if (submitBtn) submitBtn.style.display = '';
            
            this.initLoanHandlers();
            
            if (type.includes('BRRRR')) {
                this.initRefinanceCalculations();
            }
        }
    },

    loadAnalysisData: function(analysisId) {
        if (!analysisId) {
            console.error('No analysis ID provided to loadAnalysisData');
            return;
        }
    
        console.log('Loading analysis data for ID:', analysisId);
        
        fetch(`/analyses/get_analysis/${analysisId}`)
            .then(response => response.json())
            .then(data => {
                if (data?.success) {
                    const form = document.getElementById('analysisForm');
                    if (form) {
                        form.setAttribute('data-analysis-id', analysisId);
                    }
                    
                    // Set analysis type and trigger change event
                    const analysisType = document.getElementById('analysis_type');
                    if (analysisType) {
                        analysisType.value = data.analysis.analysis_type;
                        analysisType.dispatchEvent(new Event('change'));
                        
                        // Wait for fields to be created before populating
                        setTimeout(() => {
                            this.populateFormFields(data.analysis);
                        }, 300);
                    } else {
                        console.error('Analysis type field not found');
                    }
                } else {
                    console.error('Failed to fetch analysis data');
                    toastr.error('Error loading analysis data');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                toastr.error('Error loading analysis data');
            });
    },
    
    loadLongTermRentalFields: function(container) {
        container.innerHTML = `
            <div class="card mb-4">
                <div class="card-header">Direct Expenses</div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="purchase_price" class="form-label">Purchase Price</label>
                            <input type="number" class="form-control" id="purchase_price" name="purchase_price" 
                                   placeholder="The sales price as recorded on the ALTA or HUD" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="after_repair_value" class="form-label">After Repair Value</label>
                            <input type="number" class="form-control" id="after_repair_value" name="after_repair_value" 
                                   placeholder="How much the property is worth after renovation" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="cash_to_seller" class="form-label">Cash to Seller</label>
                            <input type="number" class="form-control" id="cash_to_seller" name="cash_to_seller" 
                                   placeholder="How much cash you gave the seller at closing" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="closing_costs" class="form-label">Closing Costs</label>
                            <input type="number" class="form-control" id="closing_costs" name="closing_costs" 
                                   placeholder="How much it cost to close at settlement" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="assignment_fee" class="form-label">Assignment Fee / Agent Commission</label>
                            <input type="number" class="form-control" id="assignment_fee" name="assignment_fee" 
                                   placeholder="How much it cost to work with someone to get you this property" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="marketing_costs" class="form-label">Marketing Costs</label>
                            <input type="number" class="form-control" id="marketing_costs" name="marketing_costs" 
                                   placeholder="How much you intend to pay to market the property once ready" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="renovation_costs" class="form-label">Renovation Costs</label>
                            <input type="number" class="form-control" id="renovation_costs" name="renovation_costs" 
                                   placeholder="How much you anticipate spending to renovate the property" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="renovation_duration" class="form-label">Renovation Duration (months)</label>
                            <input type="number" class="form-control" id="renovation_duration" name="renovation_duration" 
                                   placeholder="How long before the property is ready for market" required>
                        </div>
                    </div>
                </div>
            </div>
    
            <div class="card mb-4">
                <div class="card-header">Financing</div>
                <div class="card-body" id="financing-section">
                    <div id="loans-container">
                        <!-- Existing loans will be inserted here -->
                    </div>
                    <button type="button" class="btn btn-primary mb-3" id="add-loan-btn">Add Loan</button>
                </div>
            </div>
    
            <div class="card mb-4">
                <div class="card-header">Operating Income</div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="monthly_rent" class="form-label">Monthly Income</label>
                            <input type="number" class="form-control" id="monthly_rent" name="monthly_rent" 
                                   placeholder="Include rents, subsidies, leases, storage, and any other incomes" required>
                        </div>
                    </div>
                </div>
            </div>
    
            <div class="card mb-4">
                <div class="card-header">Operating Expenses</div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="management_percentage" class="form-label">Management (%)</label>
                            <input type="number" class="form-control" id="management_percentage" name="management_percentage" 
                                   value="8" min="0" max="100" step="0.5" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="capex_percentage" class="form-label">CapEx (%)</label>
                            <input type="number" class="form-control" id="capex_percentage" name="capex_percentage" 
                                   value="2" min="0" max="100" step="0.5" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="repairs_percentage" class="form-label">Repairs (%)</label>
                            <input type="number" class="form-control" id="repairs_percentage" name="repairs_percentage" 
                                   value="2" min="0" max="100" step="0.5" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="vacancy_percentage" class="form-label">Vacancy (%)</label>
                            <input type="number" class="form-control" id="vacancy_percentage" name="vacancy_percentage" 
                                   value="4" min="0" max="100" step="0.5" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-4 mb-3">
                            <label for="property_taxes" class="form-label">Property Taxes</label>
                            <input type="number" class="form-control" id="property_taxes" name="property_taxes" 
                                   placeholder="Monthly taxes" required>
                        </div>
                        <div class="col-md-4 mb-3">
                            <label for="insurance" class="form-label">Insurance</label>
                            <input type="number" class="form-control" id="insurance" name="insurance" 
                                   placeholder="Monthly insurance costs" required>
                        </div>
                        <div class="col-md-4 mb-3">
                            <label for="hoa_coa_coop" class="form-label">HOA/COA/COOP</label>
                            <input type="number" class="form-control" id="hoa_coa_coop" name="hoa_coa_coop" 
                                   placeholder="Monthly association costs, if any" required>
                        </div>
                    </div>
                </div>
            </div>
        `;
    
        // Initialize loan handlers
        this.initLoanHandlers();
    },

    loadBRRRRFields: function(container) {
        container.innerHTML = `
            <div class="card mb-4">
                <div class="card-header">Purchase Details</div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="purchase_price" class="form-label">Purchase Price</label>
                            <input type="number" class="form-control" id="purchase_price" name="purchase_price" 
                                placeholder="The sales price as recorded on the ALTA or HUD" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="after_repair_value" class="form-label">After Repair Value (ARV)</label>
                            <input type="number" class="form-control" id="after_repair_value" name="after_repair_value" 
                                placeholder="How much the property will be worth after renovation" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="renovation_costs" class="form-label">Renovation Costs</label>
                            <input type="number" class="form-control" id="renovation_costs" name="renovation_costs" 
                                placeholder="How much you anticipate spending to renovate the property" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="renovation_duration" class="form-label">Renovation Duration (months)</label>
                            <input type="number" class="form-control" id="renovation_duration" name="renovation_duration" 
                                placeholder="How long before the property is ready for refinance" required>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card mb-4">
                <div class="card-header">Initial Financing</div>
                <div class="card-body" id="initial-financing-section">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="initial_loan_amount" class="form-label">Initial Loan Amount</label>
                            <input type="number" class="form-control" id="initial_loan_amount" name="initial_loan_amount" 
                                placeholder="Amount of your initial purchase loan" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="initial_down_payment" class="form-label">Initial Down Payment</label>
                            <input type="number" class="form-control" id="initial_down_payment" name="initial_down_payment" 
                                placeholder="Down payment required for initial purchase" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="initial_interest_rate" class="form-label">Initial Interest Rate (%)</label>
                            <input type="number" class="form-control" id="initial_interest_rate" name="initial_interest_rate" 
                                placeholder="Interest rate for initial loan" step="0.125" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="initial_loan_term" class="form-label">Initial Loan Term (months)</label>
                            <input type="number" class="form-control" id="initial_loan_term" name="initial_loan_term" 
                                placeholder="Duration of initial loan in months" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="initial_closing_costs" class="form-label">Initial Closing Costs</label>
                            <input type="number" class="form-control" id="initial_closing_costs" name="initial_closing_costs" 
                                placeholder="All costs associated with initial purchase closing" required>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card mb-4">
                <div class="card-header">Refinance Details</div>
                <div class="card-body">
                    <!-- Moved to top, in its own row -->
                    <div class="row mb-3">
                        <div class="col-md-6">
                            <label for="refinance_ltv_percentage" class="form-label">Expected Refinance LTV (%)</label>
                            <input type="number" class="form-control" id="refinance_ltv_percentage" 
                                name="refinance_ltv_percentage" value="75" min="0" max="100" 
                                step="5" required>
                            <div class="form-text">Expected Loan-to-Value ratio for refinance</div>
                        </div>
                        <div class="col-md-6">
                            <label for="max_cash_left" class="form-label">Maximum Cash Left in Deal</label>
                            <input type="number" class="form-control" id="max_cash_left" 
                                name="max_cash_left" value="10000" min="0" 
                                step="500" required>
                            <div class="form-text">Maximum cash to leave in deal after refinance</div>
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="refinance_loan_amount" class="form-label">Refinance Loan Amount</label>
                            <input type="number" class="form-control" id="refinance_loan_amount" 
                                name="refinance_loan_amount" readonly>
                            <div class="form-text">Calculated based on ARV × LTV%</div>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="refinance_down_payment" class="form-label">Refinance Down Payment</label>
                            <input type="number" class="form-control" id="refinance_down_payment" 
                                name="refinance_down_payment" readonly>
                            <div class="form-text">Calculated based on ARV × (100% - LTV%)</div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="refinance_interest_rate" class="form-label">Refinance Interest Rate (%)</label>
                            <input type="number" class="form-control" id="refinance_interest_rate" 
                                name="refinance_interest_rate" step="0.125" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="refinance_loan_term" class="form-label">Refinance Loan Term (months)</label>
                            <input type="number" class="form-control" id="refinance_loan_term" 
                                name="refinance_loan_term" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="refinance_closing_costs" class="form-label">Refinance Closing Costs</label>
                            <input type="number" class="form-control" id="refinance_closing_costs" 
                                name="refinance_closing_costs" readonly>
                            <div class="form-text">Automatically calculated as 5% of refinance loan amount</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card mb-4">
                <div class="card-header">Rental Income</div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="monthly_rent" class="form-label">Monthly Rent</label>
                            <input type="number" class="form-control" id="monthly_rent" name="monthly_rent" 
                                placeholder="Expected monthly rental income" required>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card mb-4">
                <div class="card-header">Operating Expenses</div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="property_taxes" class="form-label">Monthly Property Taxes</label>
                            <input type="number" class="form-control" id="property_taxes" name="property_taxes" 
                                placeholder="Monthly property tax amount" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="insurance" class="form-label">Monthly Insurance</label>
                            <input type="number" class="form-control" id="insurance" name="insurance" 
                                placeholder="Monthly insurance costs" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="repairs_percentage" class="form-label">Maintenance (% of rent)</label>
                            <input type="number" class="form-control" id="repairs_percentage" name="repairs_percentage" 
                                value="2" min="0" max="100" step="0.5" 
                                placeholder="Percentage of rent for maintenance" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="vacancy_percentage" class="form-label">Vacancy (% of rent)</label>
                            <input type="number" class="form-control" id="vacancy_percentage" name="vacancy_percentage" 
                                value="4" min="0" max="100" step="0.5" 
                                placeholder="Percentage of rent for vacancy" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="capex_percentage" class="form-label">CapEx (% of rent)</label>
                            <input type="number" class="form-control" id="capex_percentage" name="capex_percentage" 
                                value="2" min="0" max="100" step="0.5" 
                                placeholder="Percentage of rent for capital expenditures" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="management_percentage" class="form-label">Management (% of rent)</label>
                            <input type="number" class="form-control" id="management_percentage" name="management_percentage" 
                                value="8" min="0" max="100" step="0.5" 
                                placeholder="Percentage of rent for property management" required>
                        </div>
                    </div>
                </div>
            </div>
        `;
        container.innerHTML = this.getBRRRRHTML();
    },

    loadPadSplitLTRFields: function(container) {
        // First load standard LTR fields
        const ltrHtml = this.getLongTermRentalHTML();
        const updatedLtrHtml = ltrHtml.replace(
            /after_repair_value/g,
            'after_repair_value'
        );
        container.innerHTML = updatedLtrHtml;

        // Find the Operating Expenses card and add PadSplit expenses
        const cards = container.querySelectorAll('.card');
        let operatingExpensesBody;
        
        for (const card of cards) {
            const header = card.querySelector('.card-header');
            if (header && header.textContent.trim() === 'Operating Expenses') {
                operatingExpensesBody = card.querySelector('.card-body');
                break;
            }
        }
        
        if (operatingExpensesBody) {
            operatingExpensesBody.insertAdjacentHTML('beforeend', padSplitExpensesHTML);
        } else {
            console.error('Operating Expenses section not found');
        }

        // Initialize loan handlers
        this.initLoanHandlers();
    },

    loadPadSplitBRRRRFields: function(container) {
        // First load standard BRRRR fields
        const brrrHtml = this.getBRRRRHTML();
        container.innerHTML = brrrHtml;

        // Find the Operating Expenses card
        const cards = container.querySelectorAll('.card');
        let operatingExpensesBody;
        
        for (const card of cards) {
            const header = card.querySelector('.card-header');
            if (header && header.textContent.trim() === 'Operating Expenses') {
                operatingExpensesBody = card.querySelector('.card-body');
                break;
            }
        }
        
        if (operatingExpensesBody) {
            // Add PadSplit-specific expenses
            operatingExpensesBody.insertAdjacentHTML('beforeend', padSplitExpensesHTML);
        } else {
            console.error('Operating Expenses section not found');
        }
    },

    // Helper function to get Long-Term Rental HTML
    getLongTermRentalHTML: function() {
        return `
            <div class="card mb-4">
                <div class="card-header">Purchase Details</div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="purchase_price" class="form-label">Purchase Price</label>
                            <input type="number" class="form-control" id="purchase_price" name="purchase_price" 
                                   placeholder="The sales price as recorded on the ALTA or HUD" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="after_repair_value" class="form-label">After Repair Value</label>
                            <input type="number" class="form-control" id="after_repair_value" name="after_repair_value" 
                                   placeholder="How much the property will be worth after renovation" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="renovation_costs" class="form-label">Renovation Costs</label>
                            <input type="number" class="form-control" id="renovation_costs" name="renovation_costs" 
                                   placeholder="How much you anticipate spending to renovate the property" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="renovation_duration" class="form-label">Renovation Duration (months)</label>
                            <input type="number" class="form-control" id="renovation_duration" name="renovation_duration" 
                                   placeholder="How long before the property is ready for market" required>
                        </div>
                    </div>
                </div>
            </div>
    
            <div class="card mb-4">
                <div class="card-header">Purchase Closing Details</div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="cash_to_seller" class="form-label">Cash to Seller</label>
                            <input type="number" class="form-control" id="cash_to_seller" name="cash_to_seller" 
                                   placeholder="How much cash you gave the seller at closing" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="closing_costs" class="form-label">Closing Costs</label>
                            <input type="number" class="form-control" id="closing_costs" name="closing_costs" 
                                   placeholder="All costs associated with purchase closing" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="assignment_fee" class="form-label">Assignment Fee / Agent Commission</label>
                            <input type="number" class="form-control" id="assignment_fee" name="assignment_fee" 
                                   placeholder="Cost to work with someone to get this property" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="marketing_costs" class="form-label">Marketing Costs</label>
                            <input type="number" class="form-control" id="marketing_costs" name="marketing_costs" 
                                   placeholder="How much you intend to spend on marketing" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="entry_fee_cap_percentage" class="form-label">Entry Fee Cap (% of ARV)</label>
                            <input type="number" class="form-control" id="entry_fee_cap_percentage" 
                                name="entry_fee_cap_percentage" value="15" min="0" max="100" 
                                step="0.5" required>
                            <div class="form-text">Maximum entry fee as percentage of ARV</div>
                        </div>
                    </div>
                </div>
            </div>
    
            <div class="card mb-4">
                <div class="card-header">Financing</div>
                <div class="card-body" id="financing-section">
                    <div id="loans-container">
                        <!-- Existing loans will be inserted here -->
                    </div>
                    <button type="button" class="btn btn-primary mb-3" id="add-loan-btn">Add Loan</button>
                </div>
            </div>
    
            <div class="card mb-4">
                <div class="card-header">Rental Income</div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="monthly_rent" class="form-label">Monthly Rent</label>
                            <input type="number" class="form-control" id="monthly_rent" name="monthly_rent" 
                                   placeholder="Expected monthly rental income" required>
                        </div>
                    </div>
                </div>
            </div>
    
            <div class="card mb-4">
                <div class="card-header">Operating Expenses</div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="property_taxes" class="form-label">Monthly Property Taxes</label>
                            <input type="number" class="form-control" id="property_taxes" name="property_taxes" 
                                   placeholder="Monthly property tax amount" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="insurance" class="form-label">Monthly Insurance</label>
                            <input type="number" class="form-control" id="insurance" name="insurance" 
                                   placeholder="Monthly insurance costs" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="management_percentage" class="form-label">Management (% of rent)</label>
                            <input type="number" class="form-control" id="management_percentage" name="management_percentage" 
                                   value="8" min="0" max="100" step="0.5" 
                                   placeholder="Percentage of rent for property management" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="capex_percentage" class="form-label">CapEx (% of rent)</label>
                            <input type="number" class="form-control" id="capex_percentage" name="capex_percentage" 
                                   value="2" min="0" max="100" step="0.5" 
                                   placeholder="Percentage of rent for capital expenditures" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="repairs_percentage" class="form-label">Repairs (% of rent)</label>
                            <input type="number" class="form-control" id="repairs_percentage" name="repairs_percentage" 
                                   value="2" min="0" max="100" step="0.5" 
                                   placeholder="Percentage of rent for repairs" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="vacancy_percentage" class="form-label">Vacancy (% of rent)</label>
                            <input type="number" class="form-control" id="vacancy_percentage" name="vacancy_percentage" 
                                   value="4" min="0" max="100" step="0.5" 
                                   placeholder="Percentage of rent for vacancy" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="hoa_coa_coop" class="form-label">HOA/COA/COOP</label>
                            <input type="number" class="form-control" id="hoa_coa_coop" name="hoa_coa_coop" 
                                   placeholder="Monthly association costs, if any" required>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    // Helper function to get BRRRR HTML
    getBRRRRHTML: function() {
        return `
            <div class="card mb-4">
                <div class="card-header">Purchase Details</div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="purchase_price" class="form-label">Purchase Price</label>
                                <input type="number" class="form-control" id="purchase_price" name="purchase_price" 
                                    placeholder="The sales price as recorded on the ALTA or HUD" required>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="after_repair_value" class="form-label">After Repair Value (ARV)</label>
                                <input type="number" class="form-control" id="after_repair_value" name="after_repair_value" 
                                    placeholder="How much the property will be worth after renovation" required>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="renovation_costs" class="form-label">Renovation Costs</label>
                                <input type="number" class="form-control" id="renovation_costs" name="renovation_costs" 
                                    placeholder="How much you anticipate spending to renovate the property" required>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="renovation_duration" class="form-label">Renovation Duration (months)</label>
                                <input type="number" class="form-control" id="renovation_duration" name="renovation_duration" 
                                    placeholder="How long before the property is ready for refinance" required>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-header">Initial Financing</div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="initial_loan_amount" class="form-label">Initial Loan Amount</label>
                                <input type="number" class="form-control" id="initial_loan_amount" name="initial_loan_amount" 
                                    placeholder="Amount of your initial purchase loan" required>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="initial_down_payment" class="form-label">Initial Down Payment</label>
                                <input type="number" class="form-control" id="initial_down_payment" name="initial_down_payment" 
                                    placeholder="Down payment required for initial purchase" required>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <div class="d-flex align-items-end gap-2">
                                    <div style="flex: 1;">
                                        <label for="initial_interest_rate" class="form-label">Initial Interest Rate (%)</label>
                                        <input type="number" class="form-control" id="initial_interest_rate" name="initial_interest_rate" 
                                            placeholder="Interest rate" step="0.125" required>
                                    </div>
                                    <div class="mb-2">
                                        <div class="form-check">
                                            <input class="form-check-input" type="checkbox" id="initial_interest_only" name="initial_interest_only">
                                            <label class="form-check-label" for="initial_interest_only">
                                                Interest Only
                                            </label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="initial_loan_term" class="form-label">Initial Loan Term (months)</label>
                                <input type="number" class="form-control" id="initial_loan_term" name="initial_loan_term" 
                                    placeholder="Duration of initial loan in months" required>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="initial_closing_costs" class="form-label">Initial Closing Costs</label>
                                <input type="number" class="form-control" id="initial_closing_costs" name="initial_closing_costs" 
                                    placeholder="All costs associated with initial purchase closing" required>
                            </div>
                        </div>
                    </div>
                </div>
    
            <div class="card mb-4">
                <div class="card-header">Refinance Details</div>
                <div class="card-body">
                    <!-- Moved to top, in its own row -->
                    <div class="row mb-3">
                        <div class="col-md-6">
                            <label for="refinance_ltv_percentage" class="form-label">Expected Refinance LTV (%)</label>
                            <input type="number" class="form-control" id="refinance_ltv_percentage" 
                                name="refinance_ltv_percentage" value="75" min="0" max="100" 
                                step="5" required>
                            <div class="form-text">Expected Loan-to-Value ratio for refinance</div>
                        </div>
                        <div class="col-md-6">
                            <label for="max_cash_left" class="form-label">Maximum Cash Left in Deal</label>
                            <input type="number" class="form-control" id="max_cash_left" 
                                name="max_cash_left" value="10000" min="0" 
                                step="500" required>
                            <div class="form-text">Maximum cash to leave in deal after refinance</div>
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="refinance_loan_amount" class="form-label">Refinance Loan Amount</label>
                            <input type="number" class="form-control" id="refinance_loan_amount" 
                                name="refinance_loan_amount" readonly>
                            <div class="form-text">Calculated based on ARV × LTV%</div>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="refinance_down_payment" class="form-label">Refinance Down Payment</label>
                            <input type="number" class="form-control" id="refinance_down_payment" 
                                name="refinance_down_payment" readonly>
                            <div class="form-text">Calculated based on ARV × (100% - LTV%)</div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="refinance_interest_rate" class="form-label">Refinance Interest Rate (%)</label>
                            <input type="number" class="form-control" id="refinance_interest_rate" 
                                name="refinance_interest_rate" step="0.125" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="refinance_loan_term" class="form-label">Refinance Loan Term (months)</label>
                            <input type="number" class="form-control" id="refinance_loan_term" 
                                name="refinance_loan_term" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="refinance_closing_costs" class="form-label">Refinance Closing Costs</label>
                            <input type="number" class="form-control" id="refinance_closing_costs" 
                                name="refinance_closing_costs" readonly>
                            <div class="form-text">Automatically calculated as 5% of refinance loan amount</div>
                        </div>
                    </div>
                </div>
            </div>
    
            <div class="card mb-4">
                <div class="card-header">Rental Income</div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="monthly_rent" class="form-label">Monthly Rent</label>
                            <input type="number" class="form-control" id="monthly_rent" name="monthly_rent" 
                                   placeholder="Expected monthly rental income" required>
                        </div>
                    </div>
                </div>
            </div>
    
            <div class="card mb-4">
                <div class="card-header">Operating Expenses</div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="property_taxes" class="form-label">Monthly Property Taxes</label>
                            <input type="number" class="form-control" id="property_taxes" name="property_taxes" 
                                   placeholder="Monthly property tax amount" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="insurance" class="form-label">Monthly Insurance</label>
                            <input type="number" class="form-control" id="insurance" name="insurance" 
                                   placeholder="Monthly insurance costs" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="management_percentage" class="form-label">Management (% of rent)</label>
                            <input type="number" class="form-control" id="management_percentage" name="management_percentage" 
                                   value="8" min="0" max="100" step="0.5" 
                                   placeholder="Percentage of rent for property management" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="capex_percentage" class="form-label">CapEx (% of rent)</label>
                            <input type="number" class="form-control" id="capex_percentage" name="capex_percentage" 
                                   value="2" min="0" max="100" step="0.5" 
                                   placeholder="Percentage of rent for capital expenditures" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="repairs_percentage" class="form-label">Maintenance (% of rent)</label>
                            <input type="number" class="form-control" id="repairs_percentage" name="repairs_percentage" 
                                   value="2" min="0" max="100" step="0.5" 
                                   placeholder="Percentage of rent for maintenance" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="vacancy_percentage" class="form-label">Vacancy (% of rent)</label>
                            <input type="number" class="form-control" id="vacancy_percentage" name="vacancy_percentage" 
                                   value="4" min="0" max="100" step="0.5" 
                                   placeholder="Percentage of rent for vacancy" required>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },
    
    initLoanHandlers: function(container = null) {  // Add default value
        // Only initialize if we haven't already done so for this container
        const addLoanBtn = container ? container.querySelector('#add-loan-btn') : document.getElementById('add-loan-btn');
        const loansContainer = container ? container.querySelector('#loans-container') : document.getElementById('loans-container');
        
        // If we've already initialized this container, return early
        if (addLoanBtn && addLoanBtn.hasAttribute('data-initialized')) {
            return;
        }

        if (addLoanBtn && loansContainer) {
            // Mark as initialized
            addLoanBtn.setAttribute('data-initialized', 'true');
                    
            // Handle adding new loans
            addLoanBtn.addEventListener('click', () => {
                const loanCount = loansContainer.querySelectorAll('.loan-section').length + 1;
                
                if (loanCount <= 3) {
                    const loanHtml = `
                        <div class="loan-section mb-3">
                            <div class="card">
                                <div class="card-header">
                                    <h5 class="mb-0">Loan ${loanCount}</h5>
                                </div>
                                <div class="card-body">
                                    <div class="row">
                                        <div class="col-md-6 mb-3">
                                            <label for="loan_name_${loanCount}" class="form-label">Loan Name</label>
                                            <input type="text" class="form-control" id="loan_name_${loanCount}" 
                                                   name="loans[${loanCount}][name]" placeholder="Enter loan name" required>
                                        </div>
                                        <div class="col-md-6 mb-3">
                                            <label for="loan_amount_${loanCount}" class="form-label">Loan Amount</label>
                                            <input type="number" class="form-control" id="loan_amount_${loanCount}" 
                                                   name="loans[${loanCount}][amount]" placeholder="Enter loan amount" required>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-md-6 mb-3">
                                            <label for="loan_down_payment_${loanCount}" class="form-label">Down Payment</label>
                                            <input type="number" class="form-control" id="loan_down_payment_${loanCount}" 
                                                   name="loans[${loanCount}][down_payment]" placeholder="Enter down payment amount" required>
                                        </div>
                                        <div class="col-md-6 mb-3">
                                            <label for="loan_interest_rate_${loanCount}" class="form-label">Interest Rate (%)</label>
                                            <input type="number" class="form-control" id="loan_interest_rate_${loanCount}" 
                                                   name="loans[${loanCount}][interest_rate]" step="0.125" min="0" max="100" 
                                                   placeholder="Enter interest rate" required>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-md-6 mb-3">
                                            <label for="loan_term_${loanCount}" class="form-label">Loan Term (months)</label>
                                            <input type="number" class="form-control" id="loan_term_${loanCount}" 
                                                   name="loans[${loanCount}][term]" min="1" 
                                                   placeholder="Enter loan term in months" required>
                                        </div>
                                        <div class="col-md-6 mb-3">
                                            <label for="loan_closing_costs_${loanCount}" class="form-label">Closing Costs</label>
                                            <input type="number" class="form-control" id="loan_closing_costs_${loanCount}" 
                                                   name="loans[${loanCount}][closing_costs]" 
                                                   placeholder="Enter closing costs" required>
                                        </div>
                                    </div>
                                    <div class="text-end">
                                        <button type="button" class="btn btn-danger remove-loan-btn">Remove Loan</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
    
                    loansContainer.insertAdjacentHTML('beforeend', loanHtml);
    
                    // Hide the Add Loan button if we've reached the maximum
                    if (loanCount >= 3) {
                        addLoanBtn.style.display = 'none';
                    }
                }
            });
    
            // Event delegation for remove loan buttons
            loansContainer.addEventListener('click', (e) => {
                if (e.target.classList.contains('remove-loan-btn')) {
                    const loanSection = e.target.closest('.loan-section');
                    if (loanSection) {
                        loanSection.remove();
                        
                        // Renumber remaining loans
                        const remainingLoans = loansContainer.querySelectorAll('.loan-section');
                        remainingLoans.forEach((loan, index) => {
                            const newIndex = index + 1;
                            // Update the heading
                            const heading = loan.querySelector('h5');
                            if (heading) {
                                heading.textContent = `Loan ${newIndex}`;
                            }
                            
                            // Update all input IDs and names
                            const inputs = loan.querySelectorAll('input');
                            inputs.forEach(input => {
                                const fieldName = input.id.split('_').slice(0, -1).join('_');
                                input.id = `${fieldName}_${newIndex}`;
                                input.name = `loans[${newIndex}][${fieldName.split('_').pop()}]`;
                            });
                        });
    
                        // Show the Add Loan button if we're below the maximum
                        if (remainingLoans.length < 3) {
                            addLoanBtn.style.display = 'block';
                        }
                    }
                }
            });
        }
    },

    handleSubmit: function(event) {
        event.preventDefault();
        
        // Check if already submitting
        if (this.isSubmitting) {
            console.log('Form submission already in progress');
            return;
        }
        
        console.log('Starting form submission');
        this.isSubmitting = true;
    
        const form = event.target;
        // Get submit button reference FIRST
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Creating...';
        }
    
        if (!this.validateForm(form)) {
            console.log('Form validation failed');
            this.isSubmitting = false;
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Create Analysis';
            }
            return;
        }
    
        const formData = new FormData(form);
        const analysisData = {};
    
        // Process form data with proper numeric conversion
        formData.forEach((value, key) => {
            if (this.isNumericField(key)) {
                // Convert to number and back to string to ensure proper format
                const numValue = parseFloat(this.cleanNumericValue(value));
                analysisData[key] = isNaN(numValue) ? '0' : numValue.toString();
            } else {
                analysisData[key] = value;
            }
        });
    
        // Process loan data if present
        analysisData.loans = [];
        const loanSections = form.querySelectorAll('.loan-section');
        loanSections.forEach((section, index) => {
            const loanNumber = index + 1;
            if (formData.get(`loans[${loanNumber}][name]`)) {
                analysisData.loans.push({
                    name: formData.get(`loans[${loanNumber}][name]`),
                    amount: parseFloat(this.cleanNumericValue(formData.get(`loans[${loanNumber}][amount]`))).toString(),
                    down_payment: parseFloat(this.cleanNumericValue(formData.get(`loans[${loanNumber}][down_payment]`))).toString(),
                    interest_rate: parseFloat(this.cleanNumericValue(formData.get(`loans[${loanNumber}][interest_rate]`))).toString(),
                    term: parseInt(this.cleanNumericValue(formData.get(`loans[${loanNumber}][term]`))).toString(),
                    closing_costs: parseFloat(this.cleanNumericValue(formData.get(`loans[${loanNumber}][closing_costs]`))).toString()
                });
            }
        });
    
        // Handle boolean fields
        analysisData.initial_interest_only = form.querySelector('#initial_interest_only')?.checked || false;
    
        console.log('Sending analysis data:', analysisData);
    
        fetch('/analyses/create_analysis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(analysisData)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw err; });
            }
            return response.json();
        })
        .then(data => {
            console.log('Server response:', data);
            if (data.success) {
                this.currentAnalysisId = data.analysis.id;
                this.populateReportsTab(data.analysis);
                this.switchToReportsTab();
                this.showReportActions();
                toastr.success('Analysis created successfully');
            } else {
                throw new Error(data.message || 'Unknown error occurred');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            toastr.error(error.message || 'Error creating analysis');
        })
        .finally(() => {
            // Reset submission lock
            this.isSubmitting = false;
            
            // Re-enable submit button
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Create Analysis';
            }
        });
    },

    // Helper method to identify numeric fields
    isNumericField: function(fieldName) {
        // Base numeric fields
        const baseNumericFields = [
            'purchase_price',
            'after_repair_value',
            'renovation_costs',
            'renovation_duration',
            'monthly_rent',
            'home_square_footage',
            'lot_square_footage',
            'year_built',
            'cash_to_seller',
            'closing_costs',
            'assignment_fee',
            'marketing_costs'
        ];
    
        // Percentage fields
        const percentageFields = [
            'management_percentage',
            'capex_percentage',
            'vacancy_percentage',
            'repairs_percentage',
            'refinance_ltv_percentage',
            'padsplit_platform_percentage'
        ];
    
        // BRRRR-specific fields
        const brrrFields = [
            'initial_loan_amount',
            'initial_down_payment',
            'initial_interest_rate',
            'initial_loan_term',
            'initial_closing_costs',
            'refinance_loan_amount',
            'refinance_down_payment',
            'refinance_interest_rate',
            'refinance_loan_term',
            'refinance_closing_costs',
            'max_cash_left'
        ];
    
        // Operating expense fields
        const expenseFields = [
            'property_taxes',
            'insurance',
            'hoa_coa_coop',
            'utilities',
            'internet',
            'cleaning_costs',
            'pest_control',
            'landscaping'
        ];
    
        // Loan fields
        if (fieldName.startsWith('loans[') && 
            (fieldName.includes('[amount]') || 
             fieldName.includes('[down_payment]') ||
             fieldName.includes('[interest_rate]') ||
             fieldName.includes('[term]') ||
             fieldName.includes('[closing_costs]'))) {
            return true;
        }
    
        // Check if field is in any of our numeric field arrays
        return baseNumericFields.includes(fieldName) ||
               percentageFields.includes(fieldName) ||
               brrrFields.includes(fieldName) ||
               expenseFields.includes(fieldName);
    },

    handleEditSubmit: function(event, analysisId) {
        event.preventDefault();
        
        if (this.isSubmitting) {
            console.log('Form submission already in progress');
            return;
        }
        
        console.log('Starting edit form submission');
        this.isSubmitting = true;
    
        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Updating...';
        }
    
        if (!this.validateForm(form)) {
            console.log('Form validation failed');
            this.isSubmitting = false;
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Update Analysis';
            }
            return;
        }
    
        const formData = new FormData(form);
        console.log("Form data entries:", Object.fromEntries(formData.entries()));
        const analysisData = {
            id: analysisId  // Always include the original ID
        };
    
        // Get current and original analysis types
        const currentAnalysisType = formData.get('analysis_type');
        const originalAnalysisType = this.initialAnalysisType;
    
        // Process form data with proper numeric conversion
        formData.forEach((value, key) => {
            if (this.isNumericField(key)) {
                const numValue = parseFloat(this.cleanNumericValue(value));
                analysisData[key] = isNaN(numValue) ? '0' : numValue.toString();
            } else {
                analysisData[key] = value;
            }
        });
    
        // Handle loan data if needed
        if (currentAnalysisType.includes('LTR')) {
            analysisData.loans = [];
            const loanSections = form.querySelectorAll('.loan-section');
            loanSections.forEach((section, index) => {
                const loanNumber = index + 1;
                if (formData.get(`loans[${loanNumber}][name]`)) {
                    analysisData.loans.push({
                        name: formData.get(`loans[${loanNumber}][name]`),
                        amount: this.cleanNumericValue(formData.get(`loans[${loanNumber}][amount]`)),
                        interest_rate: this.cleanNumericValue(formData.get(`loans[${loanNumber}][interest_rate]`)),
                        term_months: this.cleanNumericValue(formData.get(`loans[${loanNumber}][term]`)), // Changed from term to term_months
                        down_payment: this.cleanNumericValue(formData.get(`loans[${loanNumber}][down_payment]`)),
                        closing_costs: this.cleanNumericValue(formData.get(`loans[${loanNumber}][closing_costs]`))
                    });
                }
            });
        }
    
        // Handle BRRRR-specific fields
        if (currentAnalysisType.includes('BRRRR')) {
            analysisData.initial_interest_only = form.querySelector('#initial_interest_only')?.checked || false;
            
            // Ensure required BRRRR fields are present
            const brrrFields = [
                'initial_loan_amount',
                'initial_down_payment',
                'initial_interest_rate',
                'initial_loan_term',
                'initial_closing_costs',
                'refinance_loan_amount',
                'refinance_down_payment',
                'refinance_interest_rate',
                'refinance_loan_term',
                'refinance_closing_costs',
                'max_cash_left'
            ];
            brrrFields.forEach(field => {
                if (!analysisData[field]) {
                    analysisData[field] = '0';
                }
            });
        }
    
        // Only set create_new flag if analysis type has changed
        if (currentAnalysisType !== originalAnalysisType) {
            analysisData.create_new = true;
        }
    
        console.log('Sending update data:', analysisData);
    
        fetch('/analyses/update_analysis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(analysisData)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw err; });
            }
            return response.json();
        })
        .then(data => {
            console.log('Server response:', data);
            if (data.success) {
                // Update the current analysis ID if a new one was created
                if (data.analysis.id !== analysisId) {
                    this.currentAnalysisId = data.analysis.id;
                    form.setAttribute('data-analysis-id', data.analysis.id);
                    // Update URL without reloading the page
                    const newUrl = new URL(window.location.href);
                    newUrl.searchParams.set('analysis_id', data.analysis.id);
                    window.history.pushState({}, '', newUrl);
                    
                    toastr.success(`New ${data.analysis.analysis_type} analysis created`);
                } else {
                    toastr.success('Analysis updated successfully');
                }
                
                this.populateReportsTab(data.analysis);
                this.switchToReportsTab();
                this.showReportActions();
                
                // Update initial analysis type if we didn't create a new analysis
                if (data.analysis.id === analysisId) {
                    this.initialAnalysisType = currentAnalysisType;
                }
            } else {
                throw new Error(data.message || 'Unknown error occurred');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            toastr.error(error.message || 'Error updating analysis');
        })
        .finally(() => {
            this.isSubmitting = false;
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Update Analysis';
            }
        });
    },

    calculateMAO: function(analysis) {
        try {
            // Extract numeric values from currency strings
            const purchasePrice = parseFloat(analysis.purchase_price?.replace(/[$,]/g, '')) || 0;
            const maxCashLeft = 10000; // Default $10k if not specified
            const totalProjectCosts = parseFloat(analysis.total_project_costs?.replace(/[$,]/g, '')) || 0;
            
            // Calculate MAO
            const mao = purchasePrice + (maxCashLeft - totalProjectCosts);
            
            // Format as currency
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD',
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }).format(mao);
        } catch (error) {
            console.error('Error calculating MAO:', error);
            return '$0.00';
        }
    },

    getMAOHTML: function() {
        return `
            <div class="card mb-4">
                <div class="card-header">Required Fields</div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="after_repair_value" class="form-label">After Repair Value (ARV)</label>
                            <input type="number" class="form-control" id="after_repair_value" name="after_repair_value" 
                                   placeholder="Expected value after renovation" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="max_cash_left" class="form-label">Maximum Cash Left in Deal</label>
                            <input type="number" class="form-control" id="max_cash_left" name="max_cash_left" 
                                   value="10000" placeholder="Maximum cash to leave in deal" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="renovation_costs" class="form-label">Renovation Costs</label>
                            <input type="number" class="form-control" id="renovation_costs" name="renovation_costs" 
                                   placeholder="Expected renovation costs" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="closing_costs" class="form-label">Closing Costs</label>
                            <input type="number" class="form-control" id="closing_costs" name="closing_costs" 
                                   placeholder="Expected closing costs" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="renovation_duration" class="form-label">Renovation Duration (months)</label>
                            <input type="number" class="form-control" id="renovation_duration" name="renovation_duration" 
                                   placeholder="Expected renovation duration" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="time_to_refinance" class="form-label">Time to Refinance Post-Renovation (months)</label>
                            <input type="number" class="form-control" id="time_to_refinance" name="time_to_refinance" 
                                   placeholder="Expected time to secure refinancing" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="property_taxes" class="form-label">Monthly Property Taxes</label>
                            <input type="number" class="form-control" id="property_taxes" name="property_taxes" 
                                   placeholder="Monthly property taxes" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="insurance" class="form-label">Monthly Insurance</label>
                            <input type="number" class="form-control" id="insurance" name="insurance" 
                                   placeholder="Monthly insurance cost" required>
                        </div>
                    </div>
                </div>
            </div>
    
            <div class="card mb-4">
                <div class="card-header">Maximum Allowable Offer</div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-12">
                            <h3 class="text-center" id="mao_result">$0.00</h3>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },
    
    initMAOCalculation: function() {
        const inputs = [
            'after_repair_value',
            'max_cash_left', 
            'renovation_costs', 
            'closing_costs',
            'renovation_duration',
            'time_to_refinance',
            'property_taxes',
            'insurance'
        ];
        
        // Set up event listeners first
        inputs.forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                input.addEventListener('input', () => {
                    this.updateMAO();
                });
            }
        });
    },
    
    updateMAO: function() {
        try {
            // Get all input values with error checking
            const values = {
                arv: parseFloat(document.getElementById('after_repair_value')?.value) || 0,
                maxCashLeft: parseFloat(document.getElementById('max_cash_left')?.value) || 0,
                renovationCosts: parseFloat(document.getElementById('renovation_costs')?.value) || 0,
                closingCosts: parseFloat(document.getElementById('closing_costs')?.value) || 0,
                renovationDuration: parseFloat(document.getElementById('renovation_duration')?.value) || 0,
                timeToRefinance: parseFloat(document.getElementById('time_to_refinance')?.value) || 0,
                monthlyTaxes: parseFloat(document.getElementById('property_taxes')?.value) || 0,
                monthlyInsurance: parseFloat(document.getElementById('insurance')?.value) || 0
            };
            
            // Calculate MAO
            const totalMonths = values.renovationDuration + values.timeToRefinance;
            const monthlyHoldingCosts = values.monthlyTaxes + values.monthlyInsurance;
            const totalHoldingCosts = monthlyHoldingCosts * totalMonths;
            const totalProjectCosts = values.renovationCosts + values.closingCosts + totalHoldingCosts;
            const mao = values.arv - totalProjectCosts - values.maxCashLeft;
            
            // Update display
            const maoResult = document.getElementById('mao_result');
            if (maoResult) {
                maoResult.textContent = new Intl.NumberFormat('en-US', {
                    style: 'currency',
                    currency: 'USD',
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                }).format(mao);
            }
        } catch (error) {
            console.error('Error calculating MAO:', error);
        }
    },
    
    // Add this helper function in analysis.js
    getPadSplitLTRHTML: function() {
        return `
            <div class="card mb-4">
                <div class="card-header">Purchase Details</div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="purchase_price" class="form-label">Purchase Price</label>
                            <input type="number" class="form-control" id="purchase_price" name="purchase_price" 
                                    placeholder="The sales price as recorded on the ALTA or HUD" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="after_repair_value" class="form-label">After Repair Value</label>
                            <input type="number" class="form-control" id="after_repair_value" name="after_repair_value" 
                                    placeholder="How much the property will be worth after renovation" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="renovation_costs" class="form-label">Renovation Costs (including Furnishing)</label>
                            <input type="number" class="form-control" id="renovation_costs" name="renovation_costs" 
                                    placeholder="How much you anticipate spending to renovate and furnish" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="renovation_duration" class="form-label">Renovation Duration (months)</label>
                            <input type="number" class="form-control" id="renovation_duration" name="renovation_duration" 
                                    placeholder="How long before the property is ready for market" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="cash_to_seller" class="form-label">Cash to Seller</label>
                            <input type="number" class="form-control" id="cash_to_seller" name="cash_to_seller"
                                    placeholder="How much cash you gave the seller at closing" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="assignment_fee" class="form-label">Assignment/Agent Fee</label>
                            <input type="number" class="form-control" id="assignment_fee" name="assignment_fee" 
                                    placeholder="Cost to work with someone to get this property" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="marketing_costs" class="form-label">Marketing Fee</label>
                            <input type="number" class="form-control" id="marketing_costs" name="marketing_costs" 
                                    placeholder="How much you intend to spend on marketing" required>
                        </div>
                    </div>
                </div>
                </div>

            <div class="card mb-4">
                <div class="card-header">Financing</div>
                <div class="card-body" id="financing-section">
                    <div id="loans-container">
                        <!-- Loans will be dynamically added here -->
                    </div>
                    <button type="button" class="btn btn-primary mb-3" id="add-loan-btn">Add Loan</button>
                </div>
            </div>

            <div class="card mb-4">
                <div class="card-header">Rental Income</div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="monthly_rent" class="form-label">Monthly Income</label>
                            <input type="number" class="form-control" id="monthly_rent" name="monthly_rent" 
                                placeholder="Expected monthly rental income" required>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card mb-4">
                <div class="card-header">Operating Expenses</div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="property_taxes" class="form-label">Property Taxes</label>
                            <input type="number" class="form-control" id="property_taxes" name="property_taxes" 
                                placeholder="Monthly property tax amount" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="insurance" class="form-label">Insurance</label>
                            <input type="number" class="form-control" id="insurance" name="insurance" 
                                placeholder="Monthly insurance costs" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="management_percentage" class="form-label">Management (%)</label>
                            <input type="number" class="form-control" id="management_percentage" name="management_percentage" 
                                value="8" min="0" max="100" step="0.5" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="capex_percentage" class="form-label">CapEx (%)</label>
                            <input type="number" class="form-control" id="capex_percentage" name="capex_percentage" 
                                value="2" min="0" max="100" step="0.5" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="repairs_percentage" class="form-label">Repairs (%)</label>
                            <input type="number" class="form-control" id="repairs_percentage" name="repairs_percentage" 
                                value="2" min="0" max="100" step="0.5" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="vacancy_percentage" class="form-label">Vacancy (%)</label>
                            <input type="number" class="form-control" id="vacancy_percentage" name="vacancy_percentage" 
                                value="4" min="0" max="100" step="0.5" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="hoa_coa_coop" class="form-label">HOA/COA/COOP</label>
                            <input type="number" class="form-control" id="hoa_coa_coop" name="hoa_coa_coop" 
                                placeholder="Monthly association costs, if any" required>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card mb-4">
                <div class="card-header">PadSplit-Specific Expenses</div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="padsplit_platform_percentage" class="form-label">PadSplit Platform (%)</label>
                            <input type="number" class="form-control" id="padsplit_platform_percentage" 
                                name="padsplit_platform_percentage" value="12" min="0" max="100" 
                                step="0.5" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="utilities" class="form-label">Utilities</label>
                            <input type="number" class="form-control" id="utilities" name="utilities" 
                                placeholder="Monthly utility costs" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="internet" class="form-label">Internet</label>
                            <input type="number" class="form-control" id="internet" name="internet" 
                                placeholder="Monthly Internet costs" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="cleaning_costs" class="form-label">Cleaning Costs</label>
                            <input type="number" class="form-control" id="cleaning_costs" name="cleaning_costs" 
                                placeholder="Monthly costs to clean common areas" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="pest_control" class="form-label">Pest Control</label>
                            <input type="number" class="form-control" id="pest_control" name="pest_control" 
                                placeholder="Monthly pest control costs" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="landscaping" class="form-label">Landscaping</label>
                            <input type="number" class="form-control" id="landscaping" name="landscaping" 
                                placeholder="Monthly landscaping budget" required>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },
    
    populateReportsTab: function(analysis) {
        const reportsContent = document.querySelector('#reports');
        if (!reportsContent) return;
    
        this.currentAnalysisId = analysis.id || null;
        const maoValue = this.calculateMAO(analysis);
    
        let html = `
            <div class="row align-items-start mb-4">
                <div class="col">
                    <h4 class="mb-0">${analysis.analysis_type || 'Analysis'}: ${analysis.analysis_name || 'Untitled'}</h4>
                </div>
                <div class="col-auto">
                    <button onclick="analysisModule.downloadPdf('${this.currentAnalysisId}')" class="btn btn-primary ms-3">
                        Download PDF
                    </button>
                </div>
            </div>
            <div class="row">
                <div class="col-md-6">
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="mb-0">Purchase Details</h5>
                        </div>
                        <div class="card-body">
                            <p><strong>Purchase Price:</strong> ${analysis.purchase_price || '$0.00'}</p>
                            <p><strong>Renovation Costs:</strong> ${analysis.renovation_costs || '$0.00'}</p>
                            <p><strong>After Repair Value:</strong> ${analysis.after_repair_value || '$0.00'}</p>
                            <p>
                                <strong>Maximum Allowable Offer:</strong> ${maoValue}
                                <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" data-bs-html="true" 
                                   title="Maximum price based on your financing terms and cash requirements"></i>
                            </p>
                        </div>
                    </div>
                </div>
    
                <div class="col-md-6">
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="mb-0">Income & Returns</h5>
                        </div>
                        <div class="card-body">
                            <p><strong>Monthly Rent:</strong> ${analysis.monthly_rent || '$0.00'}</p>
                            <p><strong>Monthly Cash Flow:</strong> ${analysis.monthly_cash_flow || '$0.00'}</p>
                            <p><strong>Annual Cash Flow:</strong> ${analysis.annual_cash_flow || '$0.00'}</p>
                            <p><strong>Cash-on-Cash Return:</strong> ${analysis.cash_on_cash_return || '0%'}</p>
                        </div>
                    </div>
                </div>
            </div>`;
    
        // BRRRR-specific sections
        if (analysis.analysis_type.includes('BRRRR')) {
            html += `
            <div class="row">
                <div class="col-md-6">
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="mb-0">Investment Summary</h5>
                        </div>
                        <div class="card-body">
                            <p><strong>Total Project Costs:</strong> ${analysis.total_project_costs || '$0.00'}</p>
                            <p><strong>Total Cash Invested:</strong> ${analysis.total_cash_invested || '$0.00'}</p>
                            <p><strong>Cash Recouped:</strong> ${analysis.cash_recouped || '$0.00'}</p>
                            <p><strong>Equity Captured:</strong> ${analysis.equity_captured || '$0.00'}</p>
                        </div>
                    </div>
                </div>
    
                <div class="col-md-6">
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="mb-0">Financing Details</h5>
                        </div>
                        <div class="card-body">
                            <h6 class="mb-2">Initial Purchase Loan</h6>
                            <ul class="list-unstyled mb-4">
                                <li>Amount: ${analysis.initial_loan_amount || '$0.00'}</li>
                                <li>Interest Rate: ${analysis.initial_interest_rate || '0.00%'}
                                    <span class="badge ${analysis.initial_interest_only ? 'bg-success' : 'bg-info'} ms-2">
                                        ${analysis.initial_interest_only ? 'Interest Only' : 'Amortized'}
                                    </span>
                                </li>
                                <li>Term: ${analysis.initial_loan_term || '0'} months</li>
                                <li>Monthly Payment: ${analysis.initial_monthly_payment || '$0.00'}</li>
                                <li>Down Payment: ${analysis.initial_down_payment || '$0.00'}</li>
                                <li>Closing Costs: ${analysis.initial_closing_costs || '$0.00'}</li>
                            </ul>
                            <h6 class="mb-2">Refinance Loan</h6>
                            <ul class="list-unstyled">
                                <li>Amount: ${analysis.refinance_loan_amount || '$0.00'}</li>
                                <li>Interest Rate: ${analysis.refinance_interest_rate || '0.00%'}</li>
                                <li>Term: ${analysis.refinance_loan_term || '0'} months</li>
                                <li>Monthly Payment: ${analysis.refinance_monthly_payment || '$0.00'}</li>
                                <li>Down Payment: ${analysis.refinance_down_payment || '$0.00'}</li>
                                <li>Closing Costs: ${analysis.refinance_closing_costs || '$0.00'}</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>`;
        }
        
        // LTR and PadSplit LTR loan details
        if (analysis.analysis_type.includes('LTR') && analysis.loans?.length > 0) {
            html += `
            <div class="row">
                <div class="col-md-12">
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="mb-0">Financing Details</h5>
                        </div>
                        <div class="card-body">
                            ${analysis.loans.map(loan => `
                                <div class="mb-4">
                                    <h6 class="fw-bold">${loan.name}</h6>
                                    <ul class="list-unstyled ms-3">
                                        <li>Amount: ${this.cleanDisplayValue(loan.amount)}</li>
                                        <li>Interest Rate: ${this.cleanDisplayValue(loan.interest_rate, 'percentage')}</li>
                                        <li>Term: ${loan.term_months} months</li>
                                        <li>Down Payment: ${this.cleanDisplayValue(loan.down_payment)}</li>
                                        <li>Closing Costs: ${this.cleanDisplayValue(loan.closing_costs)}</li>
                                    </ul>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>`;
        }
    
        reportsContent.innerHTML = html;
    
        // Initialize tooltips
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    },

    // Helper method to initialize report event handlers
    initReportEventHandlers: function() {
        console.log('Initializing report event handlers');
    
        // Handle Edit Analysis button
        const editBtn = document.getElementById('editAnalysisBtn');
        if (editBtn) {
            console.log('Adding event listener to Edit Analysis button');
            editBtn.addEventListener('click', () => {
                console.log('Edit button clicked');
                this.editAnalysis();
            });
        } else {
            console.error('Edit Analysis button not found');
        }
    
        // Handle Create New Analysis button
        const createNewBtn = document.getElementById('createNewAnalysisBtn');
        if (createNewBtn) {
            createNewBtn.addEventListener('click', () => {
                this.createNewAnalysis();
            });
        }
    
        // Handle PDF download button
        const downloadPdfBtn = document.querySelector('.card-header button');
        if (downloadPdfBtn) {
            console.log('Adding click handler to download PDF button');
            downloadPdfBtn.addEventListener('click', () => {
                console.log('Download PDF button clicked');
                if (!this.currentAnalysisId) {
                    console.error('No analysis ID available');
                    toastr.error('Unable to generate PDF: No analysis ID found');
                    return;
                }
                
                // Show loading state
                downloadPdfBtn.disabled = true;
                downloadPdfBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generating PDF...';
                
                // Create hidden form to handle download
                const form = document.createElement('form');
                form.method = 'GET';
                form.action = `/analyses/generate_pdf/${this.currentAnalysisId}`;
                document.body.appendChild(form);
                
                // Submit form to trigger download
                form.submit();
                document.body.removeChild(form);
                
                // Reset button state after a delay
                setTimeout(() => {
                    downloadPdfBtn.disabled = false;
                    downloadPdfBtn.innerHTML = 'Download PDF';
                }, 2000);
            });
        } else {
            console.log('Download PDF button not found in DOM');
        }
    },

    switchToReportsTab: function() {
        const reportsTab = document.querySelector('#reports-tab');
        const reportsContent = document.querySelector('#reports');
        const financialTab = document.querySelector('#financial-tab');
        const financialContent = document.querySelector('#financial');
        
        console.log('Tab elements:', {
            reportsTab,
            reportsContent,
            financialTab,
            financialContent
        });
        
        if (reportsTab && reportsContent && financialTab && financialContent) {
            console.log('Switching tabs - Before:', {
                reportsTabClasses: reportsTab.className,
                reportsContentClasses: reportsContent.className,
                financialTabClasses: financialTab.className,
                financialContentClasses: financialContent.className
            });
    
            financialTab.classList.remove('active');
            financialContent.classList.remove('show', 'active');
            reportsTab.classList.add('active');
            reportsContent.classList.add('show', 'active');
    
            console.log('Switching tabs - After:', {
                reportsTabClasses: reportsTab.className,
                reportsContentClasses: reportsContent.className,
                financialTabClasses: financialTab.className,
                financialContentClasses: financialContent.className
            });
        } else {
            console.error('Missing required tab elements');
        }
    },

    showReportActions: function() {
        const submitBtn = document.getElementById('submitAnalysisBtn');
        const reportActions = document.getElementById('reportActions');
        
        if (submitBtn && reportActions) {
            submitBtn.style.display = 'none';
            reportActions.style.display = 'block';
        }
    },

    editAnalysis: function() {
        console.log('editAnalysis called');
        
        // Get analysis ID (try multiple sources)
        let analysisId = this.currentAnalysisId;
        if (!analysisId) {
            analysisId = this.getAnalysisIdFromUrl();
        }
        if (!analysisId) {
            const form = document.getElementById('analysisForm');
            analysisId = form ? form.getAttribute('data-analysis-id') : null;
        }
        
        console.log('Editing analysis with ID:', analysisId);
    
        if (!analysisId) {
            console.error('No analysis ID found');
            toastr.error('No analysis ID found. Cannot edit analysis.');
            return;
        }
    
        // Switch to the Financial tab
        const financialTab = document.getElementById('financial-tab');
        if (financialTab) {
            financialTab.click();
        }
    
        // Show the submit button and hide report actions
        const submitBtn = document.getElementById('submitAnalysisBtn');
        const reportActions = document.getElementById('reportActions');
        
        if (submitBtn && reportActions) {
            submitBtn.style.display = 'inline-block';
            submitBtn.textContent = 'Update Analysis';
            reportActions.style.display = 'none';
        }
    
        // Update the form submission handler
        const form = document.getElementById('analysisForm');
        if (form) {
            form.setAttribute('data-analysis-id', analysisId);
            form.onsubmit = (event) => this.handleEditSubmit(event, analysisId);
        }
    
        // Load and populate the form
        this.loadAnalysisData(analysisId);
    },

    // Modified cleanNumericValue to only clean numeric fields
    cleanNumericValue: function(value) {
        if (value === null || value === undefined || value === '') {
            return '0';
        }
        
        // Convert to string if not already
        value = String(value);
        
        // Remove currency symbols, commas, spaces
        let cleaned = value.replace(/[$,\s]/g, '');
        
        // Remove % symbol
        cleaned = cleaned.replace(/%/g, '');
        
        // If result is empty or not a valid number, return '0'
        if (!cleaned || isNaN(parseFloat(cleaned))) {
            return '0';
        }
        
        return cleaned;
    },

    // Add this helper function to handle empty/null values
    cleanDisplayValue: function(value, type = 'money') {
        if (value === null || value === undefined || value === '') {
            return type === 'money' ? '$0.00' : '0.00%';
        }
        
        if (type === 'money') {
            // If it's already formatted with $ and commas, return as is
            if (typeof value === 'string' && value.startsWith('$')) {
                return value;
            }
            // Otherwise format it
            return `$${parseFloat(value).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
        } else if (type === 'percentage') {
            // If it's already formatted with %, return as is
            if (typeof value === 'string' && value.endsWith('%')) {
                return value;
            }
            // Otherwise format it
            return `${parseFloat(value).toFixed(2)}%`;
        }
        return value;
    },

    populateFormFields: function(analysis) {
        console.log('Starting populateFormFields with:', analysis);
        
        const self = this;
        
        // Helper function to set field value and trigger change event
        const setFieldValue = (fieldId, value, type = 'text') => {
            const field = document.getElementById(fieldId);
            if (field) {
                // Clean the value based on field type
                let cleanedValue = value;
                if (type === 'money') {
                    cleanedValue = value ? value.replace(/[$,]/g, '') : '0';
                } else if (type === 'percentage') {
                    cleanedValue = value ? value.replace(/%/g, '') : '0';
                } else if (type === 'number') {
                    cleanedValue = value || '0';
                }
                
                field.value = cleanedValue;
                console.log(`Set ${fieldId} to "${cleanedValue}" (original: "${value}")`);
                
                // Trigger change event
                const event = new Event('change', { bubbles: true });
                field.dispatchEvent(event);
                return true;
            }
            console.warn(`Field not found: ${fieldId} for value:`, value);
            return false;
        };
    
        try {
            // Set basic fields first
            console.log('Setting basic fields');
            setFieldValue('analysis_name', analysis.analysis_name);
            setFieldValue('property_address', analysis.property_address);
            setFieldValue('home_square_footage', analysis.home_square_footage, 'number');
            setFieldValue('lot_square_footage', analysis.lot_square_footage, 'number');
            setFieldValue('year_built', analysis.year_built, 'number');
    
            // Set analysis type and trigger change event
            const analysisType = document.getElementById('analysis_type');
            if (analysisType) {
                analysisType.value = analysis.analysis_type;
                analysisType.dispatchEvent(new Event('change'));
                console.log('Set analysis type to:', analysis.analysis_type);
            }
    
            // Wait for dynamic fields to be created
            setTimeout(() => {
                console.log('Populating dynamic fields for type:', analysis.analysis_type);
                
                // Common fields for all analysis types
                console.log('Setting common fields');
                setFieldValue('purchase_price', analysis.purchase_price, 'money');
                setFieldValue('after_repair_value', analysis.after_repair_value, 'money');
                setFieldValue('renovation_costs', analysis.renovation_costs, 'money');
                setFieldValue('renovation_duration', analysis.renovation_duration, 'number');
                setFieldValue('monthly_rent', analysis.monthly_rent, 'money');
    
                // Common purchase closing details
                console.log('Setting purchase closing details');
                setFieldValue('cash_to_seller', analysis.cash_to_seller, 'money');
                setFieldValue('closing_costs', analysis.closing_costs, 'money');
                setFieldValue('assignment_fee', analysis.assignment_fee, 'money');
                setFieldValue('marketing_costs', analysis.marketing_costs, 'money');
    
                // Common operating expenses
                console.log('Setting operating expenses');
                setFieldValue('property_taxes', analysis.property_taxes, 'money');
                setFieldValue('insurance', analysis.insurance, 'money');
                setFieldValue('hoa_coa_coop', analysis.hoa_coa_coop, 'money');
                setFieldValue('management_percentage', analysis.management_percentage, 'percentage');
                setFieldValue('capex_percentage', analysis.capex_percentage, 'percentage');
                setFieldValue('vacancy_percentage', analysis.vacancy_percentage, 'percentage');
                setFieldValue('repairs_percentage', analysis.repairs_percentage, 'percentage');
    
                // Handle loan data for both LTR and PadSplit LTR
                if (analysis.analysis_type.includes('LTR') && analysis.loans) {
                    console.log('Setting up loans for', analysis.analysis_type);
                    const loansContainer = document.getElementById('loans-container');
                    
                    if (loansContainer) {
                        // Clear existing loans first
                        loansContainer.innerHTML = '';
                        
                        // Add each loan
                        analysis.loans.forEach((loan, index) => {
                            const addLoanBtn = document.getElementById('add-loan-btn');
                            if (addLoanBtn) {
                                addLoanBtn.click();
                                
                                // Set timeout to ensure DOM is updated
                                setTimeout(() => {
                                    const loanNumber = index + 1;
                                    setFieldValue(`loan_name_${loanNumber}`, loan.name);
                                    setFieldValue(`loan_amount_${loanNumber}`, loan.amount, 'money');
                                    setFieldValue(`loan_down_payment_${loanNumber}`, loan.down_payment, 'money');
                                    setFieldValue(`loan_interest_rate_${loanNumber}`, loan.interest_rate, 'percentage');
                                    setFieldValue(`loan_term_${loanNumber}`, loan.term, 'number');
                                    setFieldValue(`loan_closing_costs_${loanNumber}`, loan.closing_costs, 'money');
                                }, 100);
                            }
                        });
                    }
                }
    
                // BRRRR-specific fields
                if (analysis.analysis_type.includes('BRRRR')) {
                    console.log('Setting BRRRR-specific fields');
                    
                    // Initial loan details
                    setFieldValue('initial_loan_amount', analysis.initial_loan_amount, 'money');
                    setFieldValue('initial_down_payment', analysis.initial_down_payment, 'money');
                    setFieldValue('initial_interest_rate', analysis.initial_interest_rate, 'percentage');
                    setFieldValue('initial_loan_term', analysis.initial_loan_term, 'number');
                    setFieldValue('initial_closing_costs', analysis.initial_closing_costs, 'money');
                    
                    // Set initial interest only checkbox
                    const initialInterestOnly = document.getElementById('initial_interest_only');
                    if (initialInterestOnly) {
                        initialInterestOnly.checked = analysis.initial_interest_only;
                    }
                    
                    // Refinance details
                    setFieldValue('refinance_loan_amount', analysis.refinance_loan_amount, 'money');
                    setFieldValue('refinance_down_payment', analysis.refinance_down_payment, 'money');
                    setFieldValue('refinance_interest_rate', analysis.refinance_interest_rate, 'percentage');
                    setFieldValue('refinance_loan_term', analysis.refinance_loan_term, 'number');
                    setFieldValue('refinance_closing_costs', analysis.refinance_closing_costs, 'money');
                    setFieldValue('refinance_ltv_percentage', analysis.refinance_ltv_percentage, 'percentage');
                    setFieldValue('max_cash_left', analysis.max_cash_left, 'money');
                }
    
                // PadSplit-specific fields
                if (analysis.analysis_type.includes('PadSplit')) {
                    console.log('Setting PadSplit-specific fields');
                    setFieldValue('padsplit_platform_percentage', analysis.padsplit_platform_percentage, 'percentage');
                    setFieldValue('utilities', analysis.utilities, 'money');
                    setFieldValue('internet', analysis.internet, 'money');
                    setFieldValue('cleaning_costs', analysis.cleaning_costs, 'money');
                    setFieldValue('pest_control', analysis.pest_control, 'money');
                    setFieldValue('landscaping', analysis.landscaping, 'money');
                }
                
            }, 500); // Added delay to ensure fields are loaded
    
        } catch (error) {
            console.error('Error in populateFormFields:', error);
            toastr.error('Error populating form fields');
        }
    },

    // Define setLoanFields as a method of the module
    setLoanFields: function(loanNumber, loan) {
        console.log(`Setting fields for loan ${loanNumber}:`, loan);
        
        const fields = {
            name: `loan_name_${loanNumber}`,
            amount: `loan_amount_${loanNumber}`,
            down_payment: `loan_down_payment_${loanNumber}`,
            interest_rate: `loan_interest_rate_${loanNumber}`,
            term: `loan_term_${loanNumber}`,
            closing_costs: `loan_closing_costs_${loanNumber}`
        };

        Object.entries(fields).forEach(([key, fieldId]) => {
            const field = document.getElementById(fieldId);
            if (field) {
                let value = loan[key];
                if (typeof value === 'string' && (value.includes('$') || value.includes('%'))) {
                    value = value.replace(/[$,%]/g, '');
                }
                field.value = value;
                console.log(`Set ${fieldId} to ${value}`);

                // Trigger change event
                const event = new Event('change', { bubbles: true });
                field.dispatchEvent(event);
            } else {
                console.warn(`Field not found: ${fieldId}`);
            }
        });
    },

    // Add this helper function to clean numeric values
    cleanFormattedValue: function(value) {
        if (typeof value !== 'string') {
            return value;
        }
        return value.replace(/[$,\s%]/g, '');
    },

    createNewAnalysis: function() {
        window.location.href = '/analyses/create_analysis';
    },

    generateExpensesList: function(expenses) {
        return Object.entries(expenses)
            .sort(([, a], [, b]) => parseFloat(b.replace(/,/g, '')) - parseFloat(a.replace(/,/g, '')))
            .map(([name, value]) => `<p>${name}: $${value}</p>`)
            .join('');
    },

    generateLoansList: function(loans) {
        return loans.map(loan => `
            <div class="mb-3">
                <h5>${loan.name}</h5>
                <p>Loan Amount: $${loan.amount}</p>
                <p>Down Payment: $${loan.down_payment}</p>
                <p>Monthly Payment: $${loan.monthly_payment}</p>
                <p>Interest Rate: ${loan.interest_rate}%</p>
                <p>Loan Term: ${loan.term} months</p>
                <p>Closing Costs: $${loan.closing_costs}</p>
            </div>
        `).join('');
    },

    downloadPdf: function(analysisId) {
        const downloadButton = document.getElementById('downloadPdfBtn');
        if (downloadButton) {
            downloadButton.disabled = true;
            downloadButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generating PDF...';
        }
    
        fetch(`/analyses/generate_pdf/${encodeURIComponent(analysisId)}`)
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(data.error || 'Error generating PDF');
                    });
                }
                return response.blob();
            })
            .then(blob => {
                // Create download link
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                
                // Set filename from Content-Disposition header if available
                const filename = 'analysis_report.pdf';
                a.download = filename;
                
                // Trigger download
                document.body.appendChild(a);
                a.click();
                
                // Cleanup
                window.URL.revokeObjectURL(url);
                toastr.success('Report downloaded successfully');
            })
            .catch(error => {
                console.error('Error:', error);
                toastr.error(error.message || 'Error downloading PDF. Please try again.');
            })
            .finally(() => {
                // Re-enable download button
                if (downloadButton) {
                    downloadButton.disabled = false;
                    downloadButton.innerHTML = 'Download PDF';
                }
            });
    },

    validateForm: function(form) {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                field.classList.add('is-invalid');
            } else {
                field.classList.remove('is-invalid');
            }
        });

        // Validate numeric fields
        const numericFields = form.querySelectorAll('input[type="number"]');
        numericFields.forEach(field => {
            const value = parseFloat(field.value);
            if (isNaN(value) || value < 0) {
                isValid = false;
                field.classList.add('is-invalid');
            } else {
                field.classList.remove('is-invalid');
            }
        });

        // Validate Year Built field
        const yearBuiltField = form.querySelector('#year_built');
        if (yearBuiltField) {
            const yearBuilt = parseInt(yearBuiltField.value);
            const currentYear = new Date().getFullYear();
            if (isNaN(yearBuilt) || yearBuilt < 1850 || yearBuilt > currentYear || yearBuiltField.value.length !== 4) {
                isValid = false;
                yearBuiltField.classList.add('is-invalid');
            } else {
                yearBuiltField.classList.remove('is-invalid');
            }
        }

        // Validate percentage fields
        const percentageFields = ['management_percentage', 'capex_percentage', 'repairs_percentage', 'vacancy_percentage'];
        percentageFields.forEach(fieldName => {
            const field = form.querySelector(`#${fieldName}`);
            if (field) {
                const value = parseFloat(field.value);
                if (isNaN(value) || value < 0 || value > 100) {
                    isValid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            }
        });

        // Validate loan fields
        const loanSections = form.querySelectorAll('.loan-section');
        loanSections.forEach(section => {
            const loanFields = section.querySelectorAll('input');
            let loanFieldsFilled = 0;
            loanFields.forEach(field => {
                if (field.value.trim()) {
                    loanFieldsFilled++;
                }
            });
            if (loanFieldsFilled > 0 && loanFieldsFilled < loanFields.length) {
                isValid = false;
                loanFields.forEach(field => {
                    if (!field.value.trim()) {
                        field.classList.add('is-invalid');
                    }
                });
            }
        });

        if (!isValid) {
            toastr.error('Please fill out all required fields correctly.');
        }

        return isValid;
    },
};

// Initialize when the DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    analysisModule.init();
});

// Export for module usage
export default window.analysisModule;