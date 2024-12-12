// PadSplit-specific expenses template
const padSplitExpensesHTML = `
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
                    <label for="cleaning" class="form-label">Cleaning Costs</label>
                    <input type="number" class="form-control" id="cleaning" name="cleaning" 
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

// Loan template function - used by loan handlers
const getLoanFieldsHTML = (loanNumber) => `
    <div class="loan-section mb-3">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Loan ${loanNumber}</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label for="loan${loanNumber}_loan_name" class="form-label">Loan Name</label>
                        <input type="text" class="form-control" id="loan${loanNumber}_loan_name" 
                               name="loan${loanNumber}_loan_name" placeholder="Enter loan name" required>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label for="loan${loanNumber}_loan_amount" class="form-label">Loan Amount</label>
                        <input type="number" class="form-control" id="loan${loanNumber}_loan_amount" 
                               name="loan${loanNumber}_loan_amount" placeholder="Enter loan amount" required>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label for="loan${loanNumber}_loan_down_payment" class="form-label">Down Payment</label>
                        <input type="number" class="form-control" id="loan${loanNumber}_loan_down_payment" 
                               name="loan${loanNumber}_loan_down_payment" placeholder="Enter down payment amount" required>
                    </div>
                    <div class="col-md-6 mb-3">
                        <div class="d-flex align-items-end gap-2">
                            <div style="flex: 1;">
                                <label for="loan${loanNumber}_loan_interest_rate" class="form-label">Interest Rate (%)</label>
                                <input type="number" class="form-control" id="loan${loanNumber}_loan_interest_rate" 
                                       name="loan${loanNumber}_loan_interest_rate" step="0.125" min="0" max="100" 
                                       placeholder="Enter interest rate" required>
                            </div>
                            <div class="mb-2">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="loan${loanNumber}_interest_only" 
                                           name="loan${loanNumber}_interest_only">
                                    <label class="form-check-label" for="loan${loanNumber}_interest_only">
                                        Interest Only
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label for="loan${loanNumber}_loan_term" class="form-label">Loan Term (months)</label>
                        <input type="number" class="form-control" id="loan${loanNumber}_loan_term" 
                               name="loan${loanNumber}_loan_term" min="1" 
                               placeholder="Enter loan term in months" required>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label for="loan${loanNumber}_loan_closing_costs" class="form-label">Closing Costs</label>
                        <input type="number" class="form-control" id="loan${loanNumber}_loan_closing_costs" 
                               name="loan${loanNumber}_loan_closing_costs" 
                               placeholder="Enter closing costs" required>
                    </div>
                </div>
                <div class="text-end">
                    <button type="button" class="btn btn-danger remove-loan-btn"><i class="bi bi-trash me-2"></i>Remove Loan</button>
                </div>
            </div>
        </div>
    </div>
`;

// Long-term rental template
const getLongTermRentalHTML = () => `
    <div class="card mb-4">
        <div class="card-header">Property Details</div>
        <div class="card-body">
            <div class="row">
                <div class="col-md-4 mb-3">
                    <label for="square_footage" class="form-label">Square Footage</label>
                    <input type="number" class="form-control" id="square_footage" name="square_footage" 
                            placeholder="Property square footage" required>
                </div>
                <div class="col-md-4 mb-3">
                    <label for="lot_size" class="form-label">Lot Size</label>
                    <input type="number" class="form-control" id="lot_size" name="lot_size" 
                            placeholder="Lot size in square feet" required>
                </div>
                <div class="col-md-4 mb-3">
                    <label for="year_built" class="form-label">Year Built</label>
                    <input type="number" class="form-control" id="year_built" name="year_built" 
                            placeholder="Year property was built" required>
                </div>
            </div>
        </div>
    </div>

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
                            placeholder="How much you anticipate spending to renovate" required>
                </div>
                <div class="col-md-6 mb-3">
                    <label for="renovation_duration" class="form-label">Renovation Duration (months)</label>
                    <input type="number" class="form-control" id="renovation_duration" name="renovation_duration" 
                            placeholder="How long before the property is ready to rent" required>
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
        <div class="card-header">Financing</div>
        <div class="card-body" id="financing-section">
            <div id="loans-container">
                <!-- Existing loans will be inserted here -->
            </div>
            <button type="button" class="btn btn-primary mb-3" id="add-loan-btn"><i class="bi bi-plus-circle me-2"></i>Add Loan</button>
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
                    <label for="management_fee_percentage" class="form-label">Management (%)</label>
                    <input type="number" class="form-control" id="management_fee_percentage" name="management_fee_percentage" 
                           value="8" min="0" max="100" step="0.5" required>
                </div>
                <div class="col-md-6 mb-3">
                    <label for="capex_percentage" class="form-label">CapEx (%)</label>
                    <input type="number" class="form-control" id="capex_percentage" name="capex_percentage" 
                           value="2" min="0" max="100" step="1" required>
                </div>
            </div>
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="repairs_percentage" class="form-label">Repairs (%)</label>
                    <input type="number" class="form-control" id="repairs_percentage" name="repairs_percentage" 
                           value="2" min="0" max="100" step="1" required>
                </div>
                <div class="col-md-6 mb-3">
                    <label for="vacancy_percentage" class="form-label">Vacancy (%)</label>
                    <input type="number" class="form-control" id="vacancy_percentage" name="vacancy_percentage" 
                           value="4" min="0" max="100" step="1" required>
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

// BRRRR template
const getBRRRRHTML = () => `
    <div class="card mb-4">
        <div class="card-header">Property Details</div>
        <div class="card-body">
            <div class="row">
                <div class="col-md-4 mb-3">
                    <label for="square_footage" class="form-label">Square Footage</label>
                    <input type="number" class="form-control" id="square_footage" name="square_footage" 
                           placeholder="Property square footage" required>
                </div>
                <div class="col-md-4 mb-3">
                    <label for="lot_size" class="form-label">Lot Size</label>
                    <input type="number" class="form-control" id="lot_size" name="lot_size" 
                           placeholder="Lot size in square feet" required>
                </div>
                <div class="col-md-4 mb-3">
                    <label for="year_built" class="form-label">Year Built</label>
                    <input type="number" class="form-control" id="year_built" name="year_built" 
                           placeholder="Year property was built" required>
                </div>
            </div>
        </div>
    </div>

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
                        placeholder="How much you anticipate spending to renovate" required>
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
                    <label for="initial_loan_down_payment" class="form-label">Initial Down Payment</label>
                    <input type="number" class="form-control" id="initial_loan_down_payment" name="initial_loan_down_payment" 
                        placeholder="Down payment required for initial purchase" required>
                </div>
            </div>
            <div class="row">
                <div class="col-md-6 mb-3">
                    <div class="d-flex align-items-end gap-2">
                        <div style="flex: 1;">
                            <label for="initial_loan_interest_rate" class="form-label">Initial Interest Rate (%)</label>
                            <input type="number" class="form-control" id="initial_loan_interest_rate" 
                                   name="initial_loan_interest_rate" placeholder="Interest rate" step="0.125" required>
                        </div>
                        <div class="mb-2">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="initial_interest_only" 
                                       name="initial_interest_only">
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
                    <label for="initial_loan_closing_costs" class="form-label">Initial Closing Costs</label>
                    <input type="number" class="form-control" id="initial_loan_closing_costs" name="initial_loan_closing_costs" 
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
                    <input type="number" class="form-control" id="refinance_loan_amount" 
                        name="refinance_loan_amount" placeholder="Expected refinance amount" required>
                </div>
                <div class="col-md-6 mb-3">
                    <label for="refinance_loan_down_payment" class="form-label">Refinance Down Payment</label>
                    <input type="number" class="form-control" id="refinance_loan_down_payment" 
                        name="refinance_loan_down_payment" placeholder="Expected down payment" required>
                </div>
            </div>
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="refinance_loan_interest_rate" class="form-label">Refinance Interest Rate (%)</label>
                    <input type="number" class="form-control" id="refinance_loan_interest_rate" 
                        name="refinance_loan_interest_rate" step="0.125" required>
                </div>
                <div class="col-md-6 mb-3">
                    <label for="refinance_loan_term" class="form-label">Refinance Loan Term (months)</label>
                    <input type="number" class="form-control" id="refinance_loan_term" 
                        name="refinance_loan_term" required>
                </div>
            </div>
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="refinance_loan_closing_costs" class="form-label">Refinance Closing Costs</label>
                    <input type="number" class="form-control" id="refinance_loan_closing_costs" 
                        name="refinance_loan_closing_costs" placeholder="Expected closing costs" required>
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
                    <label for="management_fee_percentage" class="form-label">Management (%)</label>
                    <input type="number" class="form-control" id="management_fee_percentage" name="management_fee_percentage" 
                           value="8" min="0" max="100" step="0.5" required>
                </div>
                <div class="col-md-6 mb-3">
                    <label for="capex_percentage" class="form-label">CapEx (%)</label>
                    <input type="number" class="form-control" id="capex_percentage" name="capex_percentage" 
                           value="2" min="0" max="100" step="1" required>
                </div>
            </div>
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="repairs_percentage" class="form-label">Repairs (%)</label>
                    <input type="number" class="form-control" id="repairs_percentage" name="repairs_percentage" 
                           value="2" min="0" max="100" step="1" required>
                </div>
                <div class="col-md-6 mb-3">
                    <label for="vacancy_percentage" class="form-label">Vacancy (%)</label>
                    <input type="number" class="form-control" id="vacancy_percentage" name="vacancy_percentage" 
                           value="4" min="0" max="100" step="1" required>
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

window.analysisModule = {
    initialAnalysisType: null,
    currentAnalysisId: null,
    isSubmitting: false,
    typeChangeInProgress: false,

    // Move helper functions into the module
    formatDisplayValue: function(value, type = 'money') {
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

    toRawNumber: function(value) {
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

    init: function() {
        console.log('Analysis module initializing');
        this.initToastr();
        this.initButtonHandlers();
        
        const analysisForm = document.querySelector('#analysisForm');
        if (analysisForm) {
            // Get analysis ID from URL
            const urlParams = new URLSearchParams(window.location.search);
            const analysisId = urlParams.get('analysis_id');
            
            if (analysisId) {
                this.currentAnalysisId = analysisId;
                analysisForm.setAttribute('data-analysis-id', analysisId);
                analysisForm.addEventListener('submit', (event) => {
                    this.handleEditSubmit(event, analysisId);
                });
                this.loadAnalysisData(analysisId);
            } else {
                // Check if we have pre-populated analysis data
                const analysisDataElement = document.getElementById('analysis-data');
                if (analysisDataElement) {
                    try {
                        const analysisData = JSON.parse(analysisDataElement.textContent);
                        this.populateFormFields(analysisData);
                    } catch (error) {
                        console.error('Error parsing analysis data:', error);
                    }
                }
                
                analysisForm.addEventListener('submit', (event) => {
                    this.handleSubmit(event);
                });
            }
            
            this.initAddressAutocomplete();
            this.initAnalysisTypeHandler();
            this.initTabHandling();
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

    initButtonHandlers: function() {
        const reEditButton = document.getElementById('reEditButton');
        if (reEditButton) {
            reEditButton.addEventListener('click', () => this.switchToFinancialTab());
        }
    },

    // Updated initRefinanceCalculations for flat schema
    initRefinanceCalculations: function() {
        const arvInput = document.getElementById('after_repair_value');
        const ltvInput = document.getElementById('refinance_ltv_percentage');
        const loanAmountInput = document.getElementById('refinance_loan_amount');
        const downPaymentInput = document.getElementById('refinance_loan_down_payment');
        const closingCostsInput = document.getElementById('refinance_loan_closing_costs');

        const updateRefinanceCalcs = () => {
            const arv = toRawNumber(arvInput.value);
            const ltv = toRawNumber(ltvInput.value);

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
        const addressInput = document.getElementById('address');
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
                // Update form with new template based on type
                if (newType.includes('BRRRR')) {
                    financialTab.innerHTML = getBRRRRHTML();
                } else {
                    financialTab.innerHTML = getLongTermRentalHTML();
                }
    
                // Add PadSplit expenses if needed
                if (newType.includes('PadSplit')) {
                    financialTab.insertAdjacentHTML('beforeend', padSplitExpensesHTML);
                }
    
                // Initialize handlers
                this.initLoanHandlers();
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
            
            // Get the analysis ID from URL if it exists
            const urlParams = new URLSearchParams(window.location.search);
            const analysisId = urlParams.get('analysis_id');
            
            // Store initial value - if editing existing analysis, this will be updated in loadAnalysisData
            this.initialAnalysisType = analysisId ? null : newAnalysisType.value;
            console.log('Initial analysis type:', this.initialAnalysisType);
            
            // Load initial template if not editing existing analysis
            if (!analysisId) {
                if (this.initialAnalysisType.includes('BRRRR')) {
                    financialTab.innerHTML = getBRRRRHTML();
                } else {
                    financialTab.innerHTML = getLongTermRentalHTML();
                }
                
                if (this.initialAnalysisType.includes('PadSplit')) {
                    financialTab.insertAdjacentHTML('beforeend', padSplitExpensesHTML);
                }
                
                // Initialize handlers
                this.initLoanHandlers();
                if (this.initialAnalysisType.includes('BRRRR')) {
                    this.initRefinanceCalculations();
                }
            }
            
            // Set up event listener for changes
            newAnalysisType.addEventListener('change', async (e) => {
                // Prevent multiple concurrent changes
                if (this.typeChangeInProgress) {
                    console.log('Type change already in progress');
                    return;
                }
        
                const newType = e.target.value;
                
                // Skip if initial type hasn't been set yet or if type hasn't actually changed
                if (!this.initialAnalysisType || newType === this.initialAnalysisType) {
                    return;
                }
                
                // If we're in create mode, just update the fields
                if (!this.currentAnalysisId) {
                    console.log('Create mode - updating fields without confirmation');
                    if (newType.includes('BRRRR')) {
                        financialTab.innerHTML = getBRRRRHTML();
                    } else {
                        financialTab.innerHTML = getLongTermRentalHTML();
                    }
                    
                    if (newType.includes('PadSplit')) {
                        financialTab.insertAdjacentHTML('beforeend', padSplitExpensesHTML);
                    }
                    
                    this.initLoanHandlers();
                    if (newType.includes('BRRRR')) {
                        this.initRefinanceCalculations();
                    }
                    this.initialAnalysisType = newType;
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
    
                    await this.handleTypeChange(newType);
                    
                } catch (error) {
                    console.error('Error:', error);
                    toastr.error(error.message);
                    // Reset to original type
                    e.target.value = this.initialAnalysisType;
                } finally {
                    this.typeChangeInProgress = false;
                }
            });
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
                    const financialTab = document.getElementById('financial');
                    
                    if (form) {
                        form.setAttribute('data-analysis-id', analysisId);
                    }
                    
                    // Set analysis type and store as initial type
                    const analysisType = document.getElementById('analysis_type');
                    if (analysisType && financialTab) {
                        analysisType.value = data.analysis.analysis_type;
                        this.initialAnalysisType = data.analysis.analysis_type;
                        
                        // Load appropriate template based on analysis type
                        console.log('Loading template for type:', this.initialAnalysisType);
                        if (this.initialAnalysisType.includes('BRRRR')) {
                            financialTab.innerHTML = getBRRRRHTML();
                        } else {
                            financialTab.innerHTML = getLongTermRentalHTML();
                        }
                        
                        // Add PadSplit expenses if needed
                        if (this.initialAnalysisType.includes('PadSplit')) {
                            financialTab.insertAdjacentHTML('beforeend', padSplitExpensesHTML);
                        }
                        
                        // Initialize handlers
                        this.initLoanHandlers();
                        if (this.initialAnalysisType.includes('BRRRR')) {
                            this.initRefinanceCalculations();
                        }
                        
                        // Wait for DOM to be ready before populating fields
                        setTimeout(() => {
                            this.populateFormFields(data.analysis);
                        }, 100);
                    } else {
                        console.error('Analysis type field or financial tab not found');
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
    
    // Updated initLoanHandlers for flat schema
    initLoanHandlers: function() {
        const addLoanBtn = document.getElementById('add-loan-btn');
        const loansContainer = document.getElementById('loans-container');
        
        if (!addLoanBtn || !loansContainer || addLoanBtn.hasAttribute('data-initialized')) {
            return;
        }

        // Mark as initialized
        addLoanBtn.setAttribute('data-initialized', 'true');
        
        addLoanBtn.addEventListener('click', () => {
            const loanCount = loansContainer.querySelectorAll('.loan-section').length + 1;
            
            if (loanCount <= 3) {  // Maximum 3 loans allowed
                loansContainer.insertAdjacentHTML('beforeend', getLoanFieldsHTML(loanCount));
                
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
                        const heading = loan.querySelector('h5');
                        if (heading) {
                            heading.textContent = `Loan ${newIndex}`;
                        }
                        
                        // Update field IDs and names to match flat schema
                        const inputs = loan.querySelectorAll('input');
                        inputs.forEach(input => {
                            const fieldType = input.id.split('_').pop(); // amount, interest_rate, etc.
                            input.id = `loan${newIndex}_loan_${fieldType}`;
                            input.name = `loan${newIndex}_loan_${fieldType}`;
                        });
                    });

                    if (remainingLoans.length < 3) {
                        addLoanBtn.style.display = 'block';
                    }
                }
            }
        });
    },

    // Updated handleSubmit function for flat data structure
    handleSubmit: function(event) {
        event.preventDefault();
        
        if (this.isSubmitting) {
            console.log('Form submission already in progress');
            return;
        }
        
        this.isSubmitting = true;
        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Creating...';
        }

        if (!this.validateForm(form)) {
            this.isSubmitting = false;
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Create Analysis';
            }
            return;
        }

        // Get all form fields
        const formData = new FormData(form);
        const analysisData = {};

        // Process each field according to schema type
        formData.forEach((value, key) => {
            if (key.endsWith('_interest_only')) {
                // Get checkbox state directly from the element
                const checkbox = form.querySelector(`#${key}`);
                analysisData[key] = checkbox ? checkbox.checked : false;
                console.log(`Processing ${key}:`, analysisData[key]);
            } else if (key.endsWith('_percentage')) {
                analysisData[key] = this.toRawNumber(value);
            } else if (this.isNumericField(key)) {
                analysisData[key] = this.toRawNumber(value);
            } else {
                analysisData[key] = value;
            }
        });

        console.log('Sending analysis data:', {
            ...analysisData,
            loan1_interest_only: analysisData.loan1_interest_only,
            loan2_interest_only: analysisData.loan2_interest_only,
            loan3_interest_only: analysisData.loan3_interest_only
        });

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
            this.isSubmitting = false;
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Create Analysis';
            }
        });
    },

    // Updated isNumericField function for flat schema
    isNumericField: function(fieldName) {
        // Money fields (integers in schema)
        const moneyFields = [
            'purchase_price',
            'after_repair_value',
            'renovation_costs',
            'renovation_duration',
            'cash_to_seller',
            'closing_costs',
            'assignment_fee',
            'marketing_costs',
            'monthly_rent',
            'property_taxes',
            'insurance',
            'hoa_coa_coop',
            'utilities',
            'internet',
            'cleaning',
            'pest_control',
            'landscaping',
            'square_footage',
            'lot_size',
            'year_built'
        ];

        // Percentage fields (floats in schema)
        const percentageFields = [
            'management_fee_percentage',
            'capex_percentage',
            'vacancy_percentage',
            'repairs_percentage',
            'padsplit_platform_percentage'
        ];

        // Loan-related fields
        const loanFields = [
            'initial_loan_amount',
            'initial_loan_down_payment',
            'initial_loan_interest_rate',
            'initial_loan_term',
            'initial_loan_closing_costs',
            'refinance_loan_amount',
            'refinance_loan_down_payment',
            'refinance_loan_interest_rate',
            'refinance_loan_term',
            'refinance_loan_closing_costs',
            'loan1_loan_amount',
            'loan1_loan_down_payment',
            'loan1_loan_interest_rate',
            'loan1_loan_term',
            'loan1_loan_closing_costs',
            'loan2_loan_amount',
            'loan2_loan_down_payment',
            'loan2_loan_interest_rate',
            'loan2_loan_term',
            'loan2_loan_closing_costs',
            'loan3_loan_amount',
            'loan3_loan_down_payment',
            'loan3_loan_interest_rate',
            'loan3_loan_term',
            'loan3_loan_closing_costs'
        ];

        return moneyFields.includes(fieldName) || 
            percentageFields.includes(fieldName) || 
            loanFields.includes(fieldName);
    },

    // Updated handleEditSubmit function for flat schema
    handleEditSubmit: function(event, analysisId) {
        event.preventDefault();
        
        if (this.isSubmitting) {
            console.log('Form submission already in progress');
            return;
        }
        
        this.isSubmitting = true;
        
        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Updating...';
        }
    
        if (!this.validateForm(form)) {
            this.isSubmitting = false;
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Update Analysis';
            }
            return;
        }
    
        const formData = new FormData(form);
        const analysisData = {
            id: analysisId
        };
    
        // Get current and original analysis types
        const currentAnalysisType = formData.get('analysis_type');
        const originalAnalysisType = this.initialAnalysisType;
    
        // Process each field according to schema type
        formData.forEach((value, key) => {
            if (key.endsWith('_interest_only')) {
                // Get checkbox state directly from the element
                const checkbox = form.querySelector(`#${key}`);
                analysisData[key] = checkbox ? checkbox.checked : false;
                console.log(`Processing ${key}:`, analysisData[key]);
            } else if (key.endsWith('_percentage')) {
                analysisData[key] = this.toRawNumber(value);
            } else if (this.isNumericField(key)) {
                analysisData[key] = this.toRawNumber(value);
            } else {
                analysisData[key] = value;
            }
        });
    
        // Set create_new flag if analysis type has changed
        if (currentAnalysisType !== originalAnalysisType) {
            analysisData.create_new = true;
        }
    
        console.log('Sending analysis data:', {
            ...analysisData,
            loan1_interest_only: analysisData.loan1_interest_only,
            loan2_interest_only: analysisData.loan2_interest_only,
            loan3_interest_only: analysisData.loan3_interest_only
        });
    
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
                // Extract analysis data from nested structure
                const analysisData = data.analysis.analysis || data.analysis;
                
                console.log('Extracted analysis data:', analysisData);
                
                // Verify data structure
                if (!analysisData || typeof analysisData !== 'object') {
                    console.error('Invalid analysis data received:', analysisData);
                    throw new Error('Invalid response data structure');
                }
        
                if (!analysisData.analysis_type) {
                    console.error('Missing analysis type:', analysisData);
                    throw new Error('Missing analysis type in response');
                }
        
                if (analysisData.id !== analysisId) {
                    this.currentAnalysisId = analysisData.id;
                    form.setAttribute('data-analysis-id', analysisData.id);
                    const newUrl = new URL(window.location.href);
                    newUrl.searchParams.set('analysis_id', analysisData.id);
                    window.history.pushState({}, '', newUrl);
                    toastr.success(`New ${analysisData.analysis_type} analysis created`);
                } else {
                    toastr.success('Analysis updated successfully');
                }
                
                this.populateReportsTab(analysisData);
                this.switchToReportsTab();
                this.showReportActions();
                
                if (analysisData.id === analysisId) {
                    this.initialAnalysisType = analysisData.analysis_type;
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
            const purchasePrice = toRawNumber(analysis.purchase_price);
            const maxCashLeft = 10000; // Default $10k if not specified
            const totalProjectCosts = toRawNumber(analysis.total_project_costs);
            
            const mao = purchasePrice + (maxCashLeft - totalProjectCosts);
            return formatDisplayValue(mao);
        } catch (error) {
            console.error('Error calculating MAO:', error);
            return '$0.00';
        }
    },
    
    // Updated populateReportsTab function - applies formatting for display
    populateReportsTab: function(data) {
        console.log('Populating reports tab with:', data);
        
        const reportsContent = document.querySelector('#reports');
        if (!reportsContent) {
            console.error('Reports content element not found');
            return;
        }
    
        // Store ID
        this.currentAnalysisId = data.id || null;
    
        // Get the appropriate report content based on analysis type
        let reportContent = '';
        if (data.analysis_type.includes('BRRRR')) {
            reportContent = this.getBRRRRReportContent(data);
        } else if (data.analysis_type.includes('LTR')) {
            reportContent = this.getLTRReportContent(data);
        }
    
        // Create the header with action buttons
        reportsContent.innerHTML = `
            <div class="row align-items-center mb-4">
                <div class="col">
                    <h4 class="mb-0">${data.analysis_type || 'Analysis'}: ${data.analysis_name || 'Untitled'}</h4>
                </div>
                <div class="col-auto">
                    <div class="btn-group" role="group">
                        <button type="button" class="btn btn-primary" id="downloadPdfBtn" onclick="analysisModule.downloadPdf('${data.id}')">
                            <i class="bi bi-file-pdf me-1"></i>Download PDF
                        </button>
                        <button type="button" class="btn btn-primary" id="reEditButton">
                            <i class="bi bi-pencil me-1"></i>Re-Edit Analysis
                        </button>
                    </div>
                </div>
            </div>
            ${reportContent}`;
    
        // Add click handler for re-edit button
        const reEditButton = document.getElementById('reEditButton');
        if (reEditButton) {
            reEditButton.addEventListener('click', () => {
                const financialTab = document.getElementById('financial-tab');
                if (financialTab) {
                    financialTab.click();
                }
            });
        }
    },

    getLTRReportContent: function(analysis) {
        // Add debugging
        console.log('LTR Report Data:', {
            monthlyRent: analysis.monthly_rent,
            monthlyCashFlow: analysis.calculated_metrics?.monthly_cash_flow,
            annualCashFlow: analysis.calculated_metrics?.annual_cash_flow,
            fullMetrics: analysis.calculated_metrics
        });
    
        return `
            <div class="card mb-4">
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h5 class="mb-3">Income & Returns</h5>
                            <div class="card bg-light">
                                <div class="card-body">
                                    <p class="mb-2"><strong>Monthly Rent:</strong> ${this.formatDisplayValue(analysis.monthly_rent)}</p>
                                    <p class="mb-2"><strong>Monthly Cash Flow:</strong> ${analysis.calculated_metrics?.monthly_cash_flow}</p>
                                    <p class="mb-2"><strong>Annual Cash Flow:</strong> ${analysis.calculated_metrics?.annual_cash_flow}</p>
                                    <p class="mb-2"><strong>Cash-on-Cash Return:</strong> ${analysis.calculated_metrics?.cash_on_cash_return}</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <h5 class="mb-3">Financing Details</h5>
                            <div class="card bg-light">
                                <div class="card-body">
                                    ${this.getLoanDetailsContent(analysis)}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>`;
    },
    
    // Shared loan details component
    getLoanDetailsContent: function(analysis) {
        // Add debugging
        console.log('Loan payment metrics:', {
            loan1_payment: analysis.calculated_metrics?.loan1_loan_payment,
            loan2_payment: analysis.calculated_metrics?.loan2_loan_payment,
            loan3_payment: analysis.calculated_metrics?.loan3_loan_payment,
            all_metrics: analysis.calculated_metrics
        });
    
        let html = '';
        const loanPrefixes = ['loan1', 'loan2', 'loan3'];
        
        for (const prefix of loanPrefixes) {
            if (analysis[`${prefix}_loan_amount`] > 0) {
                html += `
                    <div class="mb-3">
                        <p class="fw-bold mb-2">${analysis[`${prefix}_loan_name`] || `Loan ${prefix.slice(-1)}`}:</p>
                        <ul class="list-unstyled ms-3">
                            <li>Amount: ${this.formatDisplayValue(analysis[`${prefix}_loan_amount`])}</li>
                            <li>Interest Rate: ${this.formatDisplayValue(analysis[`${prefix}_loan_interest_rate`], 'percentage')}
                                <span class="badge ${analysis[`${prefix}_interest_only`] ? 'bg-success' : 'bg-info'} ms-2">
                                    ${analysis[`${prefix}_interest_only`] ? 'Interest Only' : 'Amortized'}
                                </span>
                            </li>
                            <li>Term: ${analysis[`${prefix}_loan_term`] || '0'} months</li>
                            <li>Down Payment: ${this.formatDisplayValue(analysis[`${prefix}_loan_down_payment`])}</li>
                            <li>Closing Costs: ${this.formatDisplayValue(analysis[`${prefix}_loan_closing_costs`])}</li>
                            <li class="mt-2">
                                <strong>Monthly Payment: ${analysis.calculated_metrics?.[`${prefix}_loan_payment`]}</strong>
                                <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" data-bs-html="true" 
                                title="${analysis[`${prefix}_interest_only`] ? 
                                    'Interest-only payment on loan' : 
                                    'Fully amortized payment including principal and interest'}"></i>
                            </li>
                        </ul>
                    </div>`;
            }
        }
        
        return html || '<p>No loan details available</p>';
    },

    // Updated getBRRRRReportContent function to handle flat schema and formatting
    getBRRRRReportContent: function(analysis) {
        // Add debugging
        console.log('BRRRR Report Data:', {
            initialLoanPayment: analysis.calculated_metrics?.initial_loan_payment,
            refinanceLoanPayment: analysis.calculated_metrics?.refinance_loan_payment,
            monthlyRent: analysis.monthly_rent,
            monthlyCashFlow: analysis.calculated_metrics?.monthly_cash_flow,
            annualCashFlow: analysis.calculated_metrics?.annual_cash_flow,
            fullMetrics: analysis.calculated_metrics
        });
    
        return `
            <div class="card mb-4">
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6 mb-4">
                            <h5 class="mb-3">Purchase Details</h5>
                            <div class="card bg-light">
                                <div class="card-body">
                                    <p class="mb-2"><strong>Purchase Price:</strong> ${this.formatDisplayValue(analysis.purchase_price)}</p>
                                    <p class="mb-2"><strong>Renovation Costs:</strong> ${this.formatDisplayValue(analysis.renovation_costs)}</p>
                                    <p class="mb-2"><strong>After Repair Value:</strong> ${this.formatDisplayValue(analysis.after_repair_value)}</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6 mb-4">
                            <h5 class="mb-3">Investment Summary</h5>
                            <div class="card bg-light">
                                <div class="card-body">
                                    <p class="mb-2">
                                        <strong>Total Project Costs:</strong> ${this.formatDisplayValue(analysis.calculated_metrics?.total_project_costs)}
                                        <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" data-bs-html="true" 
                                        title="Purchase Price + Renovation Costs + All Closing Costs - Cash Out from Refi"></i>
                                    </p>
                                    <p class="mb-2">
                                        <strong>Refinance Loan Amount:</strong> ${this.formatDisplayValue(analysis.refinance_loan_amount)}
                                        <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" data-bs-html="true" 
                                        title="New loan based on ARV × LTV%"></i>
                                    </p>
                                    <p class="mb-2">
                                        <strong>Total Cash Invested:</strong> ${this.formatDisplayValue(analysis.calculated_metrics?.total_cash_invested)}
                                        <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" data-bs-html="true" 
                                        title="Total Project Costs - Refinance Loan Amount"></i>
                                    </p>
                                    <p class="mb-2">
                                        <strong>Equity Captured:</strong> ${this.formatDisplayValue(analysis.calculated_metrics?.equity_captured)}
                                        <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" data-bs-html="true" 
                                        title="After Repair Value - Total Project Costs"></i>
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
    
            <div class="card mb-4">
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6 mb-4">
                            <h5 class="mb-3">Income & Returns</h5>
                            <div class="card bg-light">
                                <div class="card-body">
                                    <p class="mb-2"><strong>Monthly Rent:</strong> ${this.formatDisplayValue(analysis.monthly_rent)}</p>
                                    <p class="mb-2"><strong>Monthly Cash Flow:</strong> ${analysis.calculated_metrics?.monthly_cash_flow}</p>
                                    <p class="mb-2"><strong>Annual Cash Flow:</strong> ${analysis.calculated_metrics?.annual_cash_flow}</p>
                                    <p class="mb-2"><strong>Cash-on-Cash Return:</strong> ${analysis.calculated_metrics?.cash_on_cash_return}</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6 mb-4">
                            <h5 class="mb-3">Financing Details</h5>
                            <div class="card bg-light">
                                <div class="card-body">
                                    <p class="fw-bold mb-2">Initial Purchase Loan:</p>
                                    <ul class="list-unstyled ms-3 mb-3">
                                        <li>Amount: ${this.formatDisplayValue(analysis.initial_loan_amount)}</li>
                                        <li>Interest Rate: ${this.formatDisplayValue(analysis.initial_loan_interest_rate, 'percentage')}
                                            <span class="badge ${analysis.initial_interest_only ? 'bg-success' : 'bg-info'} ms-2">
                                                ${analysis.initial_interest_only ? 'Interest Only' : 'Amortized'}
                                            </span>
                                        </li>
                                        <li>Term: ${analysis.initial_loan_term || '0'} months</li>
                                        <li>Down Payment: ${this.formatDisplayValue(analysis.initial_loan_down_payment)}</li>
                                        <li>Closing Costs: ${this.formatDisplayValue(analysis.initial_loan_closing_costs)}</li>
                                        <li class="mt-2">
                                            <strong>Monthly Payment: ${analysis.calculated_metrics?.initial_loan_payment}</strong>
                                            <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" data-bs-html="true" 
                                            title="${analysis.initial_interest_only ? 'Interest-only payment on initial loan' : 
                                            'Amortized payment on initial loan'}"></i>
                                        </li>
                                    </ul>
                                    <p class="fw-bold mb-2">Refinance Loan:</p>
                                    <ul class="list-unstyled ms-3">
                                        <li>Amount: ${this.formatDisplayValue(analysis.refinance_loan_amount)}</li>
                                        <li>Interest Rate: ${this.formatDisplayValue(analysis.refinance_loan_interest_rate, 'percentage')}
                                            <span class="badge bg-info ms-2">Amortized</span>
                                        </li>
                                        <li>Term: ${analysis.refinance_loan_term || '0'} months</li>
                                        <li>Down Payment: ${this.formatDisplayValue(analysis.refinance_loan_down_payment)}</li>
                                        <li>Closing Costs: ${this.formatDisplayValue(analysis.refinance_loan_closing_costs)}</li>
                                        <li class="mt-2">
                                            <strong>Monthly Payment: ${analysis.calculated_metrics?.refinance_loan_payment}</strong>
                                            <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" data-bs-html="true" 
                                            title="Fully amortized payment including principal and interest"></i>
                                        </li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>`;
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

    switchToFinancialTab: function() {
        const financialTab = document.getElementById('financial-tab');
        const submitBtn = document.getElementById('submitAnalysisBtn');
        const reEditButton = document.getElementById('reEditButton');
        
        if (financialTab) {
            financialTab.click();
        }
    
        if (submitBtn && reEditButton) {
            submitBtn.style.display = 'inline-block';
            reEditButton.style.display = 'none';
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
        const reEditButton = document.getElementById('reEditButton');
        
        if (submitBtn && reEditButton) {
            submitBtn.style.display = 'none';
            reEditButton.style.display = 'inline-block';
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

    // Updated populateFormFields function - uses raw values
    populateFormFields: function(analysis) {
        console.log('Populating form fields with:', analysis);
        
        const setFieldValue = (fieldId, value) => {
            const field = document.getElementById(fieldId);
            if (field) {
                // Handle checkbox fields differently
                if (field.type === 'checkbox') {
                    field.checked = Boolean(value);
                } else {
                    // Handle zero values explicitly
                    field.value = (value !== null && value !== undefined) ? value : '';
                }
                const event = new Event('change', { bubbles: true });
                field.dispatchEvent(event);
                return true;
            }
            return false;
        };
    
        try {
            // Basic fields
            setFieldValue('analysis_name', analysis.analysis_name);
            setFieldValue('analysis_type', analysis.analysis_type);
            setFieldValue('address', analysis.address);
            
            // Property details
            setFieldValue('square_footage', analysis.square_footage);
            setFieldValue('lot_size', analysis.lot_size);
            setFieldValue('year_built', analysis.year_built);
            
            // Purchase details
            setFieldValue('purchase_price', analysis.purchase_price);
            setFieldValue('after_repair_value', analysis.after_repair_value);
            setFieldValue('renovation_costs', analysis.renovation_costs);
            setFieldValue('renovation_duration', analysis.renovation_duration);
            
            // Purchase closing details
            setFieldValue('cash_to_seller', analysis.cash_to_seller);
            setFieldValue('closing_costs', analysis.closing_costs);
            setFieldValue('assignment_fee', analysis.assignment_fee);
            setFieldValue('marketing_costs', analysis.marketing_costs);
            
            // Handle existing loans
            const loansContainer = document.getElementById('loans-container');
            if (loansContainer) {
                // Clear existing loans
                loansContainer.innerHTML = '';
                
                // Add each existing loan
                for (let i = 1; i <= 3; i++) {
                    const prefix = `loan${i}`;
                    if (analysis[`${prefix}_loan_amount`] > 0) {
                        // Insert loan HTML
                        loansContainer.insertAdjacentHTML('beforeend', getLoanFieldsHTML(i));
                        
                        // Populate loan fields
                        setFieldValue(`${prefix}_loan_name`, analysis[`${prefix}_loan_name`]);
                        setFieldValue(`${prefix}_loan_amount`, analysis[`${prefix}_loan_amount`]);
                        setFieldValue(`${prefix}_loan_interest_rate`, analysis[`${prefix}_loan_interest_rate`]);
                        setFieldValue(`${prefix}_loan_term`, analysis[`${prefix}_loan_term`]);
                        setFieldValue(`${prefix}_loan_down_payment`, analysis[`${prefix}_loan_down_payment`]);
                        setFieldValue(`${prefix}_loan_closing_costs`, analysis[`${prefix}_loan_closing_costs`]);
                        
                        // Handle interest-only checkbox specifically
                        const interestOnlyCheckbox = document.getElementById(`loan${i}_interest_only`);
                        if (interestOnlyCheckbox) {
                            // Convert the value to boolean and set it
                            interestOnlyCheckbox.checked = Boolean(analysis[`loan${i}_interest_only`]);
                            // Dispatch change event to trigger any listeners
                            interestOnlyCheckbox.dispatchEvent(new Event('change', { bubbles: true }));
                            console.log(`Setting loan${i}_interest_only to:`, Boolean(analysis[`loan${i}_interest_only`]));
                        }
                    }
                }
            }

            setFieldValue('monthly_rent', analysis.monthly_rent);
            
            // Set operating expenses - now handles zero values
            setFieldValue('property_taxes', analysis.property_taxes);
            setFieldValue('insurance', analysis.insurance);
            setFieldValue('hoa_coa_coop', analysis.hoa_coa_coop);
            setFieldValue('management_fee_percentage', analysis.management_fee_percentage);
            setFieldValue('capex_percentage', analysis.capex_percentage);
            setFieldValue('vacancy_percentage', analysis.vacancy_percentage);
            setFieldValue('repairs_percentage', analysis.repairs_percentage);
            
            // Set BRRRR-specific fields if applicable
            if (analysis.analysis_type.includes('BRRRR')) {
                // Initial loan details
                setFieldValue('initial_loan_amount', analysis.initial_loan_amount);
                setFieldValue('initial_loan_down_payment', analysis.initial_loan_down_payment);
                setFieldValue('initial_loan_interest_rate', analysis.initial_loan_interest_rate);
                setFieldValue('initial_loan_term', analysis.initial_loan_term);
                setFieldValue('initial_loan_closing_costs', analysis.initial_loan_closing_costs);
                
                // Set interest-only checkbox - explicit boolean conversion
                const initialInterestOnly = document.getElementById('initial_interest_only');
                if (initialInterestOnly) {
                    initialInterestOnly.checked = Boolean(analysis.initial_interest_only);
                    initialInterestOnly.dispatchEvent(new Event('change', { bubbles: true }));
                }
                
                // Refinance details
                setFieldValue('refinance_loan_amount', analysis.refinance_loan_amount);
                setFieldValue('refinance_loan_down_payment', analysis.refinance_loan_down_payment);
                setFieldValue('refinance_loan_interest_rate', analysis.refinance_loan_interest_rate);
                setFieldValue('refinance_loan_term', analysis.refinance_loan_term);
                setFieldValue('refinance_loan_closing_costs', analysis.refinance_loan_closing_costs);
            }
            
            // Set PadSplit-specific fields if applicable
            if (analysis.analysis_type.includes('PadSplit')) {
                setFieldValue('padsplit_platform_percentage', analysis.padsplit_platform_percentage);
                setFieldValue('utilities', analysis.utilities);
                setFieldValue('internet', analysis.internet);
                setFieldValue('cleaning', analysis.cleaning);
                setFieldValue('pest_control', analysis.pest_control);
                setFieldValue('landscaping', analysis.landscaping);
            }
            
        } catch (error) {
            console.error('Error populating form fields:', error);
            toastr.error('Error populating form fields');
        }
    },

    createNewAnalysis: function() {
        window.location.href = '/analyses/create_analysis';
    },

    downloadPdf: function(analysisId) {
        if (!analysisId) {
            console.error('No analysis ID available');
            toastr.error('Unable to generate PDF: No analysis ID found');
            return;
        }
        
        // Get button reference and show loading state
        const downloadBtn = document.querySelector('#downloadPdfBtn') || 
                           document.querySelector(`button[data-analysis-id="${analysisId}"]`);
        
        if (downloadBtn) {
            downloadBtn.disabled = true;
            const originalHtml = downloadBtn.innerHTML;
            downloadBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generating...';
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
                downloadBtn.innerHTML = originalHtml;
            }
        }, 2000);
    },

    // Updated validation function for flat schema
    validateForm: function(form) {
        let isValid = true;

        // Helper to validate numeric range
        const validateNumericRange = (value, min, max = Infinity) => {
            const num = parseFloat(value);
            return !isNaN(num) && num >= min && num <= max;
        };

        // Validate required fields
        const requiredFields = form.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                field.classList.add('is-invalid');
            } else {
                field.classList.remove('is-invalid');
            }
        });

        // Validate percentage fields
        const percentageFields = [
            'management_fee_percentage',
            'capex_percentage',
            'vacancy_percentage',
            'repairs_percentage',
            'padsplit_platform_percentage'
        ];
        
        percentageFields.forEach(fieldName => {
            const field = form.querySelector(`#${fieldName}`);
            if (field && !validateNumericRange(field.value, 0, 100)) {
                isValid = false;
                field.classList.add('is-invalid');
            }
        });

        // Validate money fields (must be non-negative)
        const moneyFields = [
            'purchase_price',
            'after_repair_value',
            'renovation_costs',
            'cash_to_seller',
            'closing_costs',
            'assignment_fee',
            'marketing_costs',
            'monthly_rent',
            'property_taxes',
            'insurance',
            'hoa_coa_coop',
            'utilities',
            'internet',
            'cleaning',
            'pest_control',
            'landscaping'
        ];

        moneyFields.forEach(fieldName => {
            const field = form.querySelector(`#${fieldName}`);
            if (field && !validateNumericRange(field.value, 0)) {
                isValid = false;
                field.classList.add('is-invalid');
            }
        });

        // Validate loan fields if present
        const analysisType = form.querySelector('#analysis_type').value;
        if (analysisType.includes('BRRRR')) {
            const brrrFields = [
                'initial_loan_amount',
                'initial_loan_down_payment',
                'initial_loan_interest_rate',
                'initial_loan_term',
                'initial_loan_closing_costs',
                'refinance_loan_amount',
                'refinance_loan_down_payment',
                'refinance_loan_interest_rate',
                'refinance_loan_term',
                'refinance_loan_closing_costs'
            ];

            brrrFields.forEach(fieldName => {
                const field = form.querySelector(`#${fieldName}`);
                if (field && !validateNumericRange(field.value, 0)) {
                    isValid = false;
                    field.classList.add('is-invalid');
                }
            });
        }

        if (!isValid) {
            toastr.error('Please correct the highlighted fields');
        }

        return isValid;
    }
};

// Initialize when the DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    analysisModule.init();
});

// Export for module usage
export default window.analysisModule;