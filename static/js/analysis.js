const padSplitExpensesHTML = `
    <div class="mt-4">
        <h6 class="mb-3">PadSplit-Specific Expenses</h6>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label for="padsplit_platform_percentage" class="form-label">PadSplit Platform (%)</label>
                <input type="number" class="form-control" id="padsplit_platform_percentage" 
                       name="padsplit_platform_percentage" value="12" min="0" max="100" 
                       step="0.01" required>
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

const analysisModule = {
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

    init: function() {
        this.initToastr();
        console.log('AnalysisModule initialized');
        
        const analysisForm = document.querySelector('#analysisForm');
        if (analysisForm) {
            console.log('Analysis form found');
            
            // Check if we're in edit mode by looking for an analysis_id in the URL
            const urlParams = new URLSearchParams(window.location.search);
            const analysisId = urlParams.get('analysis_id');
            
            // Remove any existing event listeners
            analysisForm.removeEventListener('submit', this.handleSubmit);
            analysisForm.removeEventListener('submit', this.handleEditSubmit);
            
            if (analysisId) {
                // Edit mode
                console.log('Edit mode detected for analysis ID:', analysisId);
                analysisForm.addEventListener('submit', (event) => {
                    event.preventDefault();
                    this.handleEditSubmit(event, analysisId);
                });
                this.loadAnalysisData(analysisId);
                
                // Update button text
                const submitBtn = document.getElementById('submitAnalysisBtn');
                if (submitBtn) {
                    submitBtn.textContent = 'Update Analysis';
                }
            } else {
                // Create mode
                console.log('Create mode detected');
                analysisForm.addEventListener('submit', (event) => {
                    event.preventDefault();
                    this.handleSubmit(event);
                });
            }
            
            this.initAddressAutocomplete();
            this.initLoanHandlers();
            this.initAnalysisTypeHandler();
        } else {
            console.error('Analysis form not found');
        }
    
        // Set up event listeners for the buttons
        const editBtn = document.getElementById('editAnalysisBtn');
        const createNewBtn = document.getElementById('createNewAnalysisBtn');
        
        if (editBtn) {
            editBtn.addEventListener('click', () => this.editAnalysis());
        }
        
        if (createNewBtn) {
            createNewBtn.addEventListener('click', () => this.createNewAnalysis());
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

    initAnalysisTypeHandler: function() {
        const analysisType = document.getElementById('analysis_type');
        const financialTab = document.getElementById('financial');
        
        if (analysisType && financialTab) {
            // Store 'this' context
            const self = this;
            
            // Handle both change events and initial load
            const handleTypeChange = (value) => {
                console.log('Loading fields for analysis type:', value);
                switch(value) {
                    case 'Long-Term Rental':
                        financialTab.innerHTML = self.getLongTermRentalHTML();
                        break;
                    case 'PadSplit LTR':
                        self.loadPadSplitLTRFields(financialTab);
                        break;
                    case 'BRRRR':
                        financialTab.innerHTML = self.getBRRRRHTML();
                        break;
                    case 'PadSplit BRRRR':
                        self.loadPadSplitBRRRRFields(financialTab);
                        break;
                    default:
                        financialTab.innerHTML = '<p>Financial details for this analysis type are not yet implemented.</p>';
                }
                // Initialize loan handlers after loading new content
                self.initLoanHandlers();
            };
    
            // Set up event listener for changes
            analysisType.addEventListener('change', (e) => {
                handleTypeChange(e.target.value);
            });
    
            // If there's an initial value, load the appropriate fields
            if (analysisType.value) {
                handleTypeChange(analysisType.value);
            }
        }
    },

    // Function to update the form display when switching between analysis types
    loadAnalysisTypeFields: function(container, analysisType) {
        switch(analysisType) {
            case 'Long-Term Rental':
                container.innerHTML = this.getLongTermRentalHTML();
                this.initLoanHandlers();
                break;
            case 'PadSplit LTR':
                this.loadPadSplitLTRFields(container);
                break;
            case 'BRRRR':
                container.innerHTML = this.getBRRRRHTML();
                break;
            case 'PadSplit BRRRR':
                this.loadPadSplitBRRRRFields(container);
                break;
            default:
                container.innerHTML = '<p>Financial details for this analysis type are not yet implemented.</p>';
        }
    },

    loadAnalysisData: function(analysisId) {
        const self = this;
        console.log('Loading analysis data for ID:', analysisId);
        
        fetch(`/analyses/get_analysis/${analysisId}`)
            .then(response => {
                if (!response.ok) {
                    toastr.error('Error loading analysis data');
                    return null;
                }
                return response.json();
            })
            .then(data => {
                if (data?.success) {
                    console.log('Received analysis data:', data.analysis);
                    
                    // Store the current analysis ID
                    self.currentAnalysisId = analysisId;
                    
                    // Set the analysis type first
                    const analysisType = document.getElementById('analysis_type');
                    if (analysisType) {
                        analysisType.value = data.analysis.analysis_type;
                        // This will trigger loading the correct fields
                        analysisType.dispatchEvent(new Event('change'));
                        
                        // Wait for fields to be loaded before populating
                        setTimeout(() => {
                            self.populateFormFields(data.analysis);
                        }, 100);
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
                                   value="8" min="0" max="100" step="0.01" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="capex_percentage" class="form-label">CapEx (%)</label>
                            <input type="number" class="form-control" id="capex_percentage" name="capex_percentage" 
                                   value="2" min="0" max="100" step="0.01" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="repairs_percentage" class="form-label">Repairs (%)</label>
                            <input type="number" class="form-control" id="repairs_percentage" name="repairs_percentage" 
                                   value="2" min="0" max="100" step="0.01" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="vacancy_percentage" class="form-label">Vacancy (%)</label>
                            <input type="number" class="form-control" id="vacancy_percentage" name="vacancy_percentage" 
                                   value="4" min="0" max="100" step="0.01" required>
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
                                placeholder="Interest rate for initial loan" step="0.01" required>
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
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="refinance_loan_amount" class="form-label">Refinance Loan Amount</label>
                            <input type="number" class="form-control" id="refinance_loan_amount" name="refinance_loan_amount" 
                                placeholder="Amount of your refinance loan" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="refinance_down_payment" class="form-label">Refinance Down Payment</label>
                            <input type="number" class="form-control" id="refinance_down_payment" name="refinance_down_payment" 
                                placeholder="Down payment required for refinance" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="refinance_interest_rate" class="form-label">Refinance Interest Rate (%)</label>
                            <input type="number" class="form-control" id="refinance_interest_rate" name="refinance_interest_rate" 
                                placeholder="Interest rate for refinance loan" step="0.01" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="refinance_loan_term" class="form-label">Refinance Loan Term (months)</label>
                            <input type="number" class="form-control" id="refinance_loan_term" name="refinance_loan_term" 
                                placeholder="Duration of refinance loan in months" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="refinance_closing_costs" class="form-label">Refinance Closing Costs</label>
                            <input type="number" class="form-control" id="refinance_closing_costs" name="refinance_closing_costs" 
                                placeholder="All costs associated with refinance closing" required>
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
                            <label for="maintenance_percentage" class="form-label">Maintenance (% of rent)</label>
                            <input type="number" class="form-control" id="maintenance_percentage" name="maintenance_percentage" 
                                value="2" min="0" max="100" step="0.1" 
                                placeholder="Percentage of rent for maintenance" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="vacancy_percentage" class="form-label">Vacancy (% of rent)</label>
                            <input type="number" class="form-control" id="vacancy_percentage" name="vacancy_percentage" 
                                value="4" min="0" max="100" step="0.1" 
                                placeholder="Percentage of rent for vacancy" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="capex_percentage" class="form-label">CapEx (% of rent)</label>
                            <input type="number" class="form-control" id="capex_percentage" name="capex_percentage" 
                                value="2" min="0" max="100" step="0.1" 
                                placeholder="Percentage of rent for capital expenditures" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="management_percentage" class="form-label">Management (% of rent)</label>
                            <input type="number" class="form-control" id="management_percentage" name="management_percentage" 
                                value="8" min="0" max="100" step="0.1" 
                                placeholder="Percentage of rent for property management" required>
                        </div>
                    </div>
                </div>
            </div>
        `;
        container.innerHTML = this.getBRRRRHTML();
    },

    loadPadSplitLTRFields: function(container) {
        // First load standard LTR fields but update the after_repair_value field name
        const ltrHtml = this.getLongTermRentalHTML();
        const updatedLtrHtml = ltrHtml.replace(
            /after_repair_value/g,
            'after_repair_value'
        );
        container.innerHTML = updatedLtrHtml;

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
                                step="1" required>
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
                                   value="8" min="0" max="100" step="0.1" 
                                   placeholder="Percentage of rent for property management" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="capex_percentage" class="form-label">CapEx (% of rent)</label>
                            <input type="number" class="form-control" id="capex_percentage" name="capex_percentage" 
                                   value="2" min="0" max="100" step="0.1" 
                                   placeholder="Percentage of rent for capital expenditures" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="repairs_percentage" class="form-label">Repairs (% of rent)</label>
                            <input type="number" class="form-control" id="repairs_percentage" name="repairs_percentage" 
                                   value="2" min="0" max="100" step="0.1" 
                                   placeholder="Percentage of rent for repairs" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="vacancy_percentage" class="form-label">Vacancy (% of rent)</label>
                            <input type="number" class="form-control" id="vacancy_percentage" name="vacancy_percentage" 
                                   value="4" min="0" max="100" step="0.1" 
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
                                            placeholder="Interest rate" step="0.01" required>
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
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="refinance_loan_amount" class="form-label">Refinance Loan Amount</label>
                            <input type="number" class="form-control" id="refinance_loan_amount" name="refinance_loan_amount" 
                                   placeholder="Amount of your refinance loan" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="refinance_down_payment" class="form-label">Refinance Down Payment</label>
                            <input type="number" class="form-control" id="refinance_down_payment" name="refinance_down_payment" 
                                   placeholder="Down payment required for refinance" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="refinance_interest_rate" class="form-label">Refinance Interest Rate (%)</label>
                            <input type="number" class="form-control" id="refinance_interest_rate" name="refinance_interest_rate" 
                                   placeholder="Interest rate for refinance loan" step="0.01" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="refinance_loan_term" class="form-label">Refinance Loan Term (months)</label>
                            <input type="number" class="form-control" id="refinance_loan_term" name="refinance_loan_term" 
                                   placeholder="Duration of refinance loan in months" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="refinance_closing_costs" class="form-label">Refinance Closing Costs</label>
                            <input type="number" class="form-control" id="refinance_closing_costs" name="refinance_closing_costs" 
                                   placeholder="All costs associated with refinance closing" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="refinance_ltv_percentage" class="form-label">Expected Refinance LTV (%)</label>
                            <input type="number" class="form-control" id="refinance_ltv_percentage" 
                                name="refinance_ltv_percentage" value="75" min="0" max="100" 
                                step="1" required>
                            <div class="form-text">Expected Loan-to-Value ratio for refinance</div>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="max_cash_left" class="form-label">Maximum Cash Left in Deal</label>
                            <input type="number" class="form-control" id="max_cash_left" 
                                name="max_cash_left" value="10000" min="0" 
                                step="100" required>
                            <div class="form-text">Maximum cash to leave in deal after refinance</div>
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
                                   value="8" min="0" max="100" step="0.1" 
                                   placeholder="Percentage of rent for property management" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="capex_percentage" class="form-label">CapEx (% of rent)</label>
                            <input type="number" class="form-control" id="capex_percentage" name="capex_percentage" 
                                   value="2" min="0" max="100" step="0.1" 
                                   placeholder="Percentage of rent for capital expenditures" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="maintenance_percentage" class="form-label">Maintenance (% of rent)</label>
                            <input type="number" class="form-control" id="maintenance_percentage" name="maintenance_percentage" 
                                   value="2" min="0" max="100" step="0.1" 
                                   placeholder="Percentage of rent for maintenance" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="vacancy_percentage" class="form-label">Vacancy (% of rent)</label>
                            <input type="number" class="form-control" id="vacancy_percentage" name="vacancy_percentage" 
                                   value="4" min="0" max="100" step="0.1" 
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
                                                   name="loans[${loanCount}][interest_rate]" step="0.01" min="0" max="100" 
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
        console.log('Create form submission started');
    
        const form = event.target;
        if (!this.validateForm(form)) {
            console.log('Form validation failed');
            return;
        }
    
        const formData = new FormData(form);
        const analysisData = {
            ...Object.fromEntries(formData.entries())
        };
    
        // Get analysis type
        analysisData.analysis_type = document.getElementById('analysis_type').value;
    
        // Process loan data
        analysisData.loans = [];
        for (let i = 1; i <= 3; i++) {
            if (formData.get(`loans[${i}][name]`)) {
                analysisData.loans.push({
                    name: formData.get(`loans[${i}][name]`),
                    amount: parseFloat(this.cleanNumericValue(formData.get(`loans[${i}][amount]`))),
                    down_payment: parseFloat(this.cleanNumericValue(formData.get(`loans[${i}][down_payment]`))),
                    interest_rate: parseFloat(this.cleanNumericValue(formData.get(`loans[${i}][interest_rate]`))),
                    term: parseInt(this.cleanNumericValue(formData.get(`loans[${i}][term]`))),
                    closing_costs: parseFloat(this.cleanNumericValue(formData.get(`loans[${i}][closing_costs]`)))
                });
            }
        }
    
        // Complete list of all numeric fields
        const numericFields = [
            // Property Details
            'purchase_price', 
            'after_repair_value', 
            'home_square_footage',
            'lot_square_footage',
            'year_built',
            
            // Purchase Details
            'cash_to_seller', 
            'closing_costs',
            'assignment_fee', 
            'marketing_costs', 
            'renovation_costs', 
            'renovation_duration',
            
            // Initial Loan Details
            'initial_loan_amount',
            'initial_down_payment',
            'initial_interest_rate',
            'initial_loan_term',
            'initial_closing_costs',
            
            // Refinance Details
            'refinance_loan_amount',
            'refinance_down_payment',
            'refinance_interest_rate',
            'refinance_loan_term',
            'refinance_closing_costs',
            'refinance_ltv_percentage',
            'max_cash_left',
            
            // Income and Operating Expenses
            'monthly_rent',
            'management_percentage',
            'capex_percentage',
            'repairs_percentage',
            'vacancy_percentage',
            'property_taxes',
            'insurance',
            'hoa_coa_coop',
            
            // PadSplit specific fields
            'padsplit_platform_percentage',
            'utilities',
            'internet',
            'cleaning_costs',
            'pest_control',
            'landscaping'
        ];
    
        // Convert numeric fields
        numericFields.forEach(field => {
            if (analysisData[field] !== undefined && analysisData[field] !== '') {
                analysisData[field] = parseFloat(this.cleanNumericValue(analysisData[field]));
                console.log(`Converted ${field} to number: ${analysisData[field]}`);
            }
        });
    
        // Handle boolean fields
        if (analysisData.initial_interest_only) {
            analysisData.initial_interest_only = analysisData.initial_interest_only === 'on';
        }
    
        console.log('Sending analysis data:', JSON.stringify(analysisData, null, 2));
    
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
            console.log('Create handler - Server response:', data);
            console.log('Create handler - Analysis data:', data.analysis);
            if (data.success) {
                this.currentAnalysisId = data.analysis.id;
                this.populateReportsTab(data.analysis);
                this.switchToReportsTab();
                this.showReportActions();
                toastr.success('Analysis created successfully');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            toastr.error('An error occurred while creating the analysis. Please try again.');
        });
    },

    handleEditSubmit: function(event, analysisId) {
        event.preventDefault();
        console.log('Edit form submission started');
        console.log('Analysis ID:', analysisId);
        
        if (!analysisId) {
            console.error('No analysis ID provided for update');
            toastr.error('No analysis ID found. Cannot update.');
            return;
        }
    
        const form = event.target;
        if (!this.validateForm(form)) {
            console.log('Form validation failed');
            return;
        }
    
        // Create analysis data object with explicit ID
        const formData = new FormData(form);
        const analysisData = {
            id: analysisId,
            ...Object.fromEntries(formData.entries())
        };
    
        // Get analysis type
        analysisData.analysis_type = document.getElementById('analysis_type').value;
    
        // Process loan data
        analysisData.loans = [];
        for (let i = 1; i <= 3; i++) {
            if (formData.get(`loans[${i}][name]`)) {
                analysisData.loans.push({
                    name: formData.get(`loans[${i}][name]`),
                    amount: parseFloat(this.cleanNumericValue(formData.get(`loans[${i}][amount]`))),
                    down_payment: parseFloat(this.cleanNumericValue(formData.get(`loans[${i}][down_payment]`))),
                    interest_rate: parseFloat(this.cleanNumericValue(formData.get(`loans[${i}][interest_rate]`))),
                    term: parseInt(this.cleanNumericValue(formData.get(`loans[${i}][term]`))),
                    closing_costs: parseFloat(this.cleanNumericValue(formData.get(`loans[${i}][closing_costs]`)))
                });
            }
        }
    
        // Complete list of numeric fields
        const numericFields = [
            // Property Details
            'purchase_price', 
            'after_repair_value', 
            'home_square_footage',
            'lot_square_footage',
            'year_built',
            
            // Purchase Details
            'cash_to_seller', 
            'closing_costs',
            'assignment_fee', 
            'marketing_costs', 
            'renovation_costs', 
            'renovation_duration',
            
            // Initial Loan Details
            'initial_loan_amount',
            'initial_down_payment',
            'initial_interest_rate',
            'initial_loan_term',
            'initial_closing_costs',
            
            // Refinance Details
            'refinance_loan_amount',
            'refinance_down_payment',
            'refinance_interest_rate',
            'refinance_loan_term',
            'refinance_closing_costs',
            'refinance_ltv_percentage',
            'max_cash_left',
            
            // Income and Operating Expenses
            'monthly_rent',
            'management_percentage',
            'capex_percentage',
            'repairs_percentage',
            'vacancy_percentage',
            'property_taxes',
            'insurance',
            'hoa_coa_coop'
        ];
    
        // Convert numeric fields and add validation
        numericFields.forEach(field => {
            if (analysisData[field] !== undefined && analysisData[field] !== '') {
                const cleanValue = this.cleanNumericValue(analysisData[field]);
                if (!isNaN(cleanValue)) {
                    analysisData[field] = parseFloat(cleanValue);
                    console.log(`Converted ${field} to number: ${analysisData[field]}`);
                } else {
                    console.warn(`Invalid numeric value for ${field}: ${analysisData[field]}`);
                    analysisData[field] = 0; // Default to 0 for invalid numbers
                }
            } else {
                console.debug(`Field ${field} is undefined or empty`);
            }
        });
    
        // Handle boolean fields
        analysisData.initial_interest_only = 
            document.getElementById('initial_interest_only')?.checked || false;
    
        // Add retry mechanism
        const maxRetries = 3;
        let currentTry = 0;
    
        const attemptUpdate = () => {
            currentTry++;
            console.log(`Attempt ${currentTry} to update analysis`);
            console.log('Sending analysis data:', JSON.stringify(analysisData, null, 2));
    
            return fetch('/analyses/update_analysis', {
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
                console.log('Edit handler - Server response:', data);
                console.log('Edit handler - Analysis data:', data.analysis);
                if (data.success) {
                    const analysisWithId = {
                        ...data.analysis,
                        id: analysisId
                    };
                    console.log('Edit handler - Reconstructed analysis:', analysisWithId);
                    this.populateReportsTab(analysisWithId);
                    this.switchToReportsTab();
                    this.showReportActions();
                    toastr.success('Analysis updated successfully');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                if (currentTry < maxRetries) {
                    console.log(`Retrying update (attempt ${currentTry + 1} of ${maxRetries})...`);
                    return new Promise(resolve => setTimeout(resolve, 1000)) // Wait 1 second
                        .then(() => attemptUpdate());
                } else {
                    toastr.error('An error occurred while updating the analysis. Please try again.');
                    throw error;
                }
            });
        };
    
        // Start the update process
        attemptUpdate().catch(error => {
            console.error('All retry attempts failed:', error);
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
    
    populateReportsTab: function(analysis) {
        console.log('Starting populateReportsTab with analysis:', analysis);
        
        // Store ID and get reports container
        this.currentAnalysisId = analysis.id || null;
        const reportsContent = document.querySelector('#reports');
        
        if (!reportsContent) {
            console.error('Reports content element not found');
            return;
        }
    
        const maoValue = this.calculateMAO(analysis);
        console.log('Calculated MAO:', maoValue);
    
        // Verify content exists and structure
        console.log('Found reports container:', reportsContent);
    
        let html = `
            <div class="card mb-4">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <span>${analysis.analysis_type || 'Analysis'}: ${analysis.analysis_name || 'Untitled'}</span>
                    <button id="downloadPdfBtn" class="btn btn-primary">Download PDF</button>
                </div>
                
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6 mb-4">
                            <h5 class="mb-3">Purchase Details</h5>
                            <div class="card bg-light">
                                <div class="card-body">
                                    <p class="mb-2"><strong>Purchase Price:</strong> ${analysis.purchase_price || '$0.00'}</p>
                                    <p class="mb-2"><strong>Renovation Costs:</strong> ${analysis.renovation_costs || '$0.00'}</p>
                                    <p class="mb-2"><strong>After Repair Value:</strong> ${analysis.after_repair_value || '$0.00'}</p>
                                    <p class="mb-2">
                                        <strong>Maximum Allowable Offer:</strong> ${maoValue}
                                        <i class="ms-2 bi bi-info-circle" 
                                           data-bs-toggle="tooltip" 
                                           data-bs-html="true" 
                                           title="This value represents the highest possible value of Purchase Price given your LTV Cash-Out Refi and the maximum amount you're willing to be stuck in a deal"></i>
                                    </p>
                                </div>
                            </div>
                        </div>
    
                        <div class="col-md-6 mb-4">
                            <h5 class="mb-3">Income & Returns</h5>
                            <div class="card bg-light">
                                <div class="card-body">
                                    <p class="mb-2"><strong>Monthly Rent:</strong> ${analysis.monthly_rent || '$0.00'}</p>
                                    <p class="mb-2"><strong>Monthly Cash Flow:</strong> ${analysis.monthly_cash_flow || '$0.00'}</p>
                                    <p class="mb-2"><strong>Annual Cash Flow:</strong> ${analysis.annual_cash_flow || '$0.00'}</p>
                                    <p class="mb-2"><strong>Cash-on-Cash Return:</strong> ${analysis.cash_on_cash_return || '0%'}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>;

                ${(analysis.analysis_type === 'BRRRR' || analysis.analysis_type === 'PadSplit BRRRR') ? `
                <!-- Second row with Investment Summary and Financing Details -->
                <div class="row">
                    <div class="col-md-6">
                        <h5>Investment Summary</h5>
                        <div class="card bg-light mb-3">
                            <div class="card-body">
                                <p class="mb-2">
                                    <strong>Total Project Costs:</strong> ${analysis.total_project_costs || '$0.00'}
                                    <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" data-bs-html="true" 
                                    title="Purchase Price + Renovation Costs + All Closing Costs"></i>
                                </p>
                                <p class="mb-2">
                                    <strong>After Repair Value:</strong> ${analysis.after_repair_value || '$0.00'}
                                </p>
                                <p class="mb-2">
                                    <strong>Refinance Loan Amount:</strong> ${analysis.refinance_loan_amount || '$0.00'}
                                    <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" data-bs-html="true" 
                                    title="New loan based on ARV × LTV%"></i>
                                </p>
                                <p class="mb-2">
                                    <strong>Total Cash Invested:</strong> ${analysis.total_cash_invested || '$0.00'}
                                    <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" data-bs-html="true" 
                                    title="Total Project Costs - Refinance Loan Amount"></i>
                                </p>
                                <p class="mb-2">
                                    <strong>Equity Captured:</strong> ${analysis.equity_captured || '$0.00'}
                                    <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" data-bs-html="true" 
                                    title="After Repair Value - Total Project Costs"></i>
                                </p>
                            </div>
                        </div>
                    </div>

                    <div class="col-md-6">
                        <h5>Financing Details</h5>
                        <div class="card bg-light mb-3">
                            <div class="card-body">
                                <p class="fw-bold mb-2">Initial Purchase Loan:</p>
                                <ul class="list-unstyled ms-3 mb-3">
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
                                <p class="fw-bold mb-2">Refinance Loan:</p>
                                <ul class="list-unstyled ms-3">
                                    <li>Amount: ${analysis.refinance_loan_amount || '$0.00'}</li>
                                    <li>Interest Rate: ${analysis.refinance_interest_rate || '0.00%'}
                                        <span class="badge bg-info ms-2">Amortized</span>
                                    </li>
                                    <li>Term: ${analysis.refinance_loan_term || '0'} months</li>
                                    <li>Monthly Payment: ${analysis.refinance_monthly_payment || '$0.00'}</li>
                                    <li>Down Payment: ${analysis.refinance_down_payment || '$0.00'}</li>
                                    <li>Closing Costs: ${analysis.refinance_closing_costs || '$0.00'}</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
                ` : ''}
            </div>
        </div>`;

        console.log('Generated HTML:', html);

        // Set the HTML content
        reportsContent.innerHTML = html;
        console.log('HTML content set. Current reports content:', reportsContent.innerHTML);

        // Initialize tooltips
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });

        // Add event handlers
        this.initReportEventHandlers();
    },

    // Helper method to initialize report event handlers
    initReportEventHandlers: function() {
        // Add event listener for PDF download
        const downloadPdfBtn = document.getElementById('downloadPdfBtn');
        if (downloadPdfBtn) {
            downloadPdfBtn.addEventListener('click', () => {
                this.downloadPdf(this.currentAnalysisId);
            });
        }

        // Show the Edit and Create New buttons
        const editBtn = document.getElementById('editAnalysisBtn');
        const createNewBtn = document.getElementById('createNewAnalysisBtn');
        
        if (editBtn) {
            editBtn.setAttribute('data-analysis-id', this.currentAnalysisId);
            editBtn.style.display = 'inline-block';
        }
        
        if (editBtn && createNewBtn) {
            editBtn.style.display = 'inline-block';
            createNewBtn.style.display = 'inline-block';
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
        // Get ID from the button's data attribute
        const editBtn = document.getElementById('editAnalysisBtn');
        const analysisId = editBtn ? editBtn.getAttribute('data-analysis-id') : null;
        
        console.log('Editing analysis with ID:', analysisId);

        if (!analysisId) {
            console.error('No analysis ID found');
            return;
        }
    
        this.currentAnalysisId = analysisId;  // Store it in the instance

        // Switch to the Financial tab
        const financialTab = document.querySelector('#financial-tab');
        const financialContent = document.querySelector('#financial');
        const reportsTab = document.querySelector('#reports-tab');
        const reportsContent = document.querySelector('#reports');
        
        if (financialTab && financialContent && reportsTab && reportsContent) {
            reportsTab.classList.remove('active');
            reportsContent.classList.remove('show', 'active');
            financialTab.classList.add('active');
            financialContent.classList.add('show', 'active');
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
        const form = document.querySelector('#analysisForm');
        if (form) {
            form.onsubmit = (event) => this.handleEditSubmit(event, this.currentAnalysisId);
        }
    
        // Fetch and populate the form with existing data
        if (this.currentAnalysisId) {
            fetch(`/analyses/get_analysis/${this.currentAnalysisId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        this.populateFormFields(data.analysis);
                    } else {
                        console.error('Failed to fetch analysis data');
                    }
                })
                .catch(error => console.error('Error:', error));
        } else {
            console.error('No current analysis ID found');
        }
    },

    cleanNumericValue: function(value) {
        if (typeof value !== 'string') {
            value = String(value);
        }
        
        // Remove currency symbols, commas, and trim whitespace
        let cleaned = value.replace(/[$,\s]/g, '');
        
        // Remove % symbol for percentage values
        cleaned = cleaned.replace(/%/g, '');
        
        // Return cleaned value or 0 if empty/invalid
        return cleaned || '0';
    },

    populateFormFields: function(analysis) {
        console.log('Populating form with analysis:', analysis);

        // Handle basic fields as before
        Object.keys(analysis).forEach(key => {
            const field = document.getElementById(key);
            if (field) {
                if (field.type === 'number') {
                    field.value = this.cleanNumericValue(analysis[key]);
                } else {
                    field.value = analysis[key];
                }
                console.log(`Set ${key} to ${field.value}`);
            }
        });
        
        // First populate the basic fields
        Object.keys(analysis).forEach(key => {
            const field = document.getElementById(key);
            if (field) {
                if (field.type === 'number') {
                    field.value = this.cleanNumericValue(analysis[key]);
                } else {
                    field.value = analysis[key];
                }
                console.log(`Set ${key} to ${field.value}`);
            }
        });

        // Handle BRRRR-specific fields
        if (analysis.analysis_type === 'BRRRR') {
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
                'refinance_ltv_percentage',
                'max_cash_left'
            ];

            brrrFields.forEach(fieldName => {
                const field = document.getElementById(fieldName);
                if (field && analysis[fieldName] !== undefined) {
                    if (field.type === 'number') {
                        field.value = this.cleanNumericValue(analysis[fieldName]);
                    } else {
                        field.value = analysis[fieldName];
                    }
                    console.log(`Set BRRRR field ${fieldName} to ${field.value}`);
                }
            });
        }

        // Special handling for operating expenses
        if (analysis.operating_expenses) {
            // Map the stored keys to form field IDs
            const expenseMapping = {
                'Property Taxes': 'property_taxes',
                'Insurance': 'insurance',
                'Management': 'management_percentage'
            };

            Object.entries(analysis.operating_expenses).forEach(([key, value]) => {
                const fieldId = expenseMapping[key];
                if (fieldId) {
                    const field = document.getElementById(fieldId);
                    if (field) {
                        field.value = this.cleanNumericValue(value);
                        console.log(`Set operating expense ${fieldId} to ${field.value} (from ${key}: ${value})`);
                    }
                }
            });
        }

        // Handle interest-only checkbox
        const interestOnlyCheckbox = document.getElementById('initial_interest_only');
        if (interestOnlyCheckbox && analysis.initial_interest_only !== undefined) {
            interestOnlyCheckbox.checked = analysis.initial_interest_only;
        }

        // Handle loan data population for Long-Term Rental
        if (analysis.analysis_type === 'Long-Term Rental' && analysis.loans && Array.isArray(analysis.loans)) {
            const loansContainer = document.getElementById('loans-container');
            if (loansContainer) {
                loansContainer.innerHTML = ''; // Clear existing loans
                
                // Add each loan section
                analysis.loans.forEach((loan, index) => {
                    const loanNumber = index + 1;
                    const loanHtml = `
                        <div class="loan-section mb-3">
                            <div class="card">
                                <div class="card-header">
                                    <h5 class="mb-0">Loan ${loanNumber}</h5>
                                </div>
                                <div class="card-body">
                                    <div class="row">
                                        <div class="col-md-6 mb-3">
                                            <label for="loan_name_${loanNumber}" class="form-label">Loan Name</label>
                                            <input type="text" class="form-control" id="loan_name_${loanNumber}" 
                                                   name="loans[${loanNumber}][name]" value="${loan.name || ''}" required>
                                        </div>
                                        <div class="col-md-6 mb-3">
                                            <label for="loan_amount_${loanNumber}" class="form-label">Loan Amount</label>
                                            <input type="number" class="form-control" id="loan_amount_${loanNumber}" 
                                                   name="loans[${loanNumber}][amount]" value="${this.cleanNumericValue(loan.amount)}" required>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-md-6 mb-3">
                                            <label for="loan_down_payment_${loanNumber}" class="form-label">Down Payment</label>
                                            <input type="number" class="form-control" id="loan_down_payment_${loanNumber}" 
                                                   name="loans[${loanNumber}][down_payment]" value="${this.cleanNumericValue(loan.down_payment)}" required>
                                        </div>
                                        <div class="col-md-6 mb-3">
                                            <label for="loan_interest_rate_${loanNumber}" class="form-label">Interest Rate (%)</label>
                                            <input type="number" class="form-control" id="loan_interest_rate_${loanNumber}" 
                                                   name="loans[${loanNumber}][interest_rate]" value="${this.cleanNumericValue(loan.interest_rate)}" 
                                                   step="0.01" required>
                                        </div>
                                    </div>
                                    <div class="row">
                                        <div class="col-md-6 mb-3">
                                            <label for="loan_term_${loanNumber}" class="form-label">Loan Term (months)</label>
                                            <input type="number" class="form-control" id="loan_term_${loanNumber}" 
                                                   name="loans[${loanNumber}][term]" value="${this.cleanNumericValue(loan.term)}" required>
                                        </div>
                                        <div class="col-md-6 mb-3">
                                            <label for="loan_closing_costs_${loanNumber}" class="form-label">Closing Costs</label>
                                            <input type="number" class="form-control" id="loan_closing_costs_${loanNumber}" 
                                                   name="loans[${loanNumber}][closing_costs]" value="${this.cleanNumericValue(loan.closing_costs)}" required>
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
                });

                // Update the Add Loan button visibility
                const addLoanBtn = document.getElementById('add-loan-btn');
                if (addLoanBtn) {
                    addLoanBtn.style.display = analysis.loans.length >= 3 ? 'none' : 'block';
                }
            }
        }

        // Log fields that weren't found
        Object.keys(analysis).forEach(key => {
            if (!document.getElementById(key)) {
                console.debug(`Field not found for ${key}: ${analysis[key]}`);
            }
        });
    },
    
    populateReportsTab: function(analysis) {
        console.log('Starting populateReportsTab with analysis:', analysis);
        
        // Get reports container
        const reportsContent = document.querySelector('#reports');
        console.log('Reports container found:', reportsContent);
        
        if (!reportsContent) {
            console.error('Reports content element not found');
            return;
        }
    
        // Clear existing content
        reportsContent.innerHTML = '';
    
        // Build main card structure
        const mainCard = document.createElement('div');
        mainCard.className = 'card mb-4';
        
        // Add header
        const header = document.createElement('div');
        header.className = 'card-header d-flex justify-content-between align-items-center';
        header.innerHTML = `
            <span>${analysis.analysis_type || 'Analysis'}: ${analysis.analysis_name || 'Untitled'}</span>
            <button id="downloadPdfBtn" class="btn btn-primary">Download PDF</button>
        `;
        mainCard.appendChild(header);
        
        // Build body content
        const cardBody = document.createElement('div');
        cardBody.className = 'card-body';
        
        // First row with Purchase Details and Income & Returns
        const firstRow = document.createElement('div');
        firstRow.className = 'row mb-4';
        firstRow.innerHTML = `
            <div class="col-md-6">
                <h5 class="mb-3">Purchase Details</h5>
                <div class="card bg-light">
                    <div class="card-body">
                        <p class="mb-2"><strong>Purchase Price:</strong> ${analysis.purchase_price || '$0.00'}</p>
                        <p class="mb-2"><strong>Renovation Costs:</strong> ${analysis.renovation_costs || '$0.00'}</p>
                        <p class="mb-2"><strong>After Repair Value:</strong> ${analysis.after_repair_value || '$0.00'}</p>
                        <p class="mb-2">
                            <strong>Maximum Allowable Offer:</strong> ${this.calculateMAO(analysis)}
                            <i class="ms-2 bi bi-info-circle" 
                               data-bs-toggle="tooltip" 
                               data-bs-html="true" 
                               title="This value represents the highest possible value of Purchase Price given your LTV Cash-Out Refi and the maximum amount you're willing to be stuck in a deal"></i>
                        </p>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <h5 class="mb-3">Income & Returns</h5>
                <div class="card bg-light">
                    <div class="card-body">
                        <p class="mb-2"><strong>Monthly Rent:</strong> ${analysis.monthly_rent || '$0.00'}</p>
                        <p class="mb-2"><strong>Monthly Cash Flow:</strong> ${analysis.monthly_cash_flow || '$0.00'}</p>
                        <p class="mb-2"><strong>Annual Cash Flow:</strong> ${analysis.annual_cash_flow || '$0.00'}</p>
                        <p class="mb-2"><strong>Cash-on-Cash Return:</strong> ${analysis.cash_on_cash_return || '0%'}</p>
                    </div>
                </div>
            </div>
        `;
        cardBody.appendChild(firstRow);
    
        // BRRRR-specific content
        if (analysis.analysis_type === 'BRRRR' || analysis.analysis_type === 'PadSplit BRRRR') {
            const brrrRow = document.createElement('div');
            brrrRow.className = 'row mt-4';
            brrrRow.innerHTML = `
                <!-- Investment Summary -->
                <div class="col-md-6">
                    <h5>Investment Summary</h5>
                    <div class="card bg-light mb-3">
                        <div class="card-body">
                            <p class="mb-2">
                                <strong>Total Project Costs:</strong> ${analysis.total_project_costs || '$0.00'}
                                <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" data-bs-html="true" 
                                title="Purchase Price + Renovation Costs + All Closing Costs"></i>
                            </p>
                            <p class="mb-2">
                                <strong>After Repair Value:</strong> ${analysis.after_repair_value || '$0.00'}
                            </p>
                            <p class="mb-2">
                                <strong>Refinance Loan Amount:</strong> ${analysis.refinance_loan_amount || '$0.00'}
                                <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" data-bs-html="true" 
                                title="New loan based on ARV × LTV%"></i>
                            </p>
                            <p class="mb-2">
                                <strong>Total Cash Invested:</strong> ${analysis.total_cash_invested || '$0.00'}
                                <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" data-bs-html="true" 
                                title="Total Project Costs - Refinance Loan Amount"></i>
                            </p>
                            <p class="mb-2">
                                <strong>Equity Captured:</strong> ${analysis.equity_captured || '$0.00'}
                                <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" data-bs-html="true" 
                                title="After Repair Value - Total Project Costs"></i>
                            </p>
                        </div>
                    </div>
                </div>

                <!-- Financing Details -->
                <div class="col-md-6">
                    <h5>Financing Details</h5>
                    <div class="card bg-light mb-3">
                        <div class="card-body">
                            <p class="fw-bold mb-2">Initial Purchase Loan:</p>
                            <ul class="list-unstyled ms-3 mb-3">
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
                            <p class="fw-bold mb-2">Refinance Loan:</p>
                            <ul class="list-unstyled ms-3">
                                <li>Amount: ${analysis.refinance_loan_amount || '$0.00'}</li>
                                <li>Interest Rate: ${analysis.refinance_interest_rate || '0.00%'}
                                    <span class="badge bg-info ms-2">Amortized</span>
                                </li>
                                <li>Term: ${analysis.refinance_loan_term || '0'} months</li>
                                <li>Monthly Payment: ${analysis.refinance_monthly_payment || '$0.00'}</li>
                                <li>Down Payment: ${analysis.refinance_down_payment || '$0.00'}</li>
                                <li>Closing Costs: ${analysis.refinance_closing_costs || '$0.00'}</li>
                            </ul>
                        </div>
                    </div>
                </div>
            `;
            cardBody.appendChild(brrrRow);
        }
    
        // Add body to main card
        mainCard.appendChild(cardBody);
        
        // Log the constructed HTML
        console.log('Constructed HTML:', mainCard.outerHTML);
        
        // Clear and append new content
        reportsContent.innerHTML = '';
        reportsContent.appendChild(mainCard);
        
        // Initialize tooltips
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });

        console.log('Final reports content:', reportsContent.innerHTML);
    },

    handleEditSubmit: function(event, analysisId) {
        event.preventDefault();
        console.log('Edit form submission started');
        console.log('Analysis ID:', analysisId);
        
        if (!analysisId) {
            console.error('No analysis ID provided for update');
            toastr.error('No analysis ID found. Cannot update.');
            return;
        }

        const form = event.target;
        const formData = new FormData(form);
        
        if (!this.validateForm(form)) {
            console.log('Form validation failed');
            return;
        }
    
        // Create analysis data object and explicitly set the ID
        const analysisData = {
            id: analysisId,  // Explicitly set the ID
            ...Object.fromEntries(formData.entries())
        };
    
        console.log('Analysis data before processing:', analysisData);
    
        // Process loan data
        analysisData.loans = [];
        for (let i = 1; i <= 3; i++) {
            if (formData.get(`loans[${i}][name]`)) {
                analysisData.loans.push({
                    name: formData.get(`loans[${i}][name]`),
                    amount: parseFloat(this.cleanNumericValue(formData.get(`loans[${i}][amount]`))),
                    down_payment: parseFloat(this.cleanNumericValue(formData.get(`loans[${i}][down_payment]`))),
                    interest_rate: parseFloat(this.cleanNumericValue(formData.get(`loans[${i}][interest_rate]`))),
                    term: parseInt(this.cleanNumericValue(formData.get(`loans[${i}][term]`))),
                    closing_costs: parseFloat(this.cleanNumericValue(formData.get(`loans[${i}][closing_costs]`)))
                });
            }
        }
        
        // Ensure all numeric fields are parsed as numbers
        ['monthly_rent', 'management_percentage', 'capex_percentage', 'repairs_percentage', 'vacancy_percentage',
            'property_taxes', 'insurance', 'hoa_coa_coop', 'renovation_costs', 'renovation_duration'].forEach(field => {
            analysisData[field] = parseFloat(this.cleanNumericValue(analysisData[field]));
        });
    
        console.log('Sending updated analysis data:', JSON.stringify(analysisData, null, 2));

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
                const analysisWithId = {
                    ...data.analysis,
                    id: analysisId  // Ensure ID is preserved
                };
                this.populateReportsTab(analysisWithId);
                this.switchToReportsTab();
                this.showReportActions();
            } else {
                throw new Error(data.message || 'Unknown error occurred');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            toastr.error('An error occurred while updating the analysis. Please try again.');
        });
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
