// Constants
const DEFAULTS = {
    PERCENTAGES: {
        MANAGEMENT: 8,
        CAPEX: 2,
        VACANCY: 4,
        REPAIRS: 2,
        PADSPLIT_PLATFORM: 12,
        REFINANCE_LTV: 75
    },
    MAX_CASH_LEFT: 10000,
    MAX_LOANS: 3
};

const NUMERIC_FIELDS = {
    MONEY: [
        'purchase_price',
        'after_repair_value',
        'renovation_costs',
        'monthly_rent',
        'cash_to_seller',
        'closing_costs',
        'assignment_fee',
        'marketing_costs',
        'property_taxes',
        'insurance',
        'hoa_coa_coop',
        'utilities',
        'internet',
        'cleaning_costs',
        'pest_control',
        'landscaping',
        'initial_loan_amount',
        'initial_down_payment',
        'initial_closing_costs',
        'refinance_loan_amount',
        'refinance_down_payment',
        'refinance_closing_costs',
        'max_cash_left'
    ],
    PERCENTAGE: [
        'management_percentage',
        'capex_percentage',
        'vacancy_percentage',
        'repairs_percentage',
        'refinance_ltv_percentage',
        'padsplit_platform_percentage',
        'initial_interest_rate',
        'refinance_interest_rate'
    ],
    INTEGER: [
        'home_square_footage',
        'lot_square_footage',
        'year_built',
        'renovation_duration',
        'initial_loan_term',
        'refinance_loan_term'
    ]
};

// HTML Templates
const TEMPLATES = {
    PADSPLIT_EXPENSES: `
        <div class="mt-4">
            <h6 class="mb-3">PadSplit-Specific Expenses</h6>
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="padsplit_platform_percentage" class="form-label">PadSplit Platform (%)</label>
                    <input type="number" class="form-control" id="padsplit_platform_percentage" 
                           name="padsplit_platform_percentage" value="12" min="0" max="100" 
                           step="0.25" required>
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
    `,

    getLongTermRentalHTML() {
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
                                value="8.0" min="0" max="100" step="0.25" 
                                placeholder="Percentage of rent for property management" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="capex_percentage" class="form-label">CapEx (% of rent)</label>
                            <input type="number" class="form-control" id="capex_percentage" name="capex_percentage" 
                                value="2.0" min="0" max="100" step="0.25" 
                                placeholder="Percentage of rent for capital expenditures" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="repairs_percentage" class="form-label">Repairs (% of rent)</label>
                            <input type="number" class="form-control" id="repairs_percentage" name="repairs_percentage" 
                                value="2.0" min="0" max="100" step="0.25" 
                                placeholder="Percentage of rent for repairs" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="vacancy_percentage" class="form-label">Vacancy (% of rent)</label>
                            <input type="number" class="form-control" id="vacancy_percentage" name="vacancy_percentage" 
                                value="4.0" min="0" max="100" step="0.25" 
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

    getBRRRRHTML() {
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
                    <div class="row mb-3">
                        <div class="col-md-6">
                            <label for="refinance_ltv_percentage" class="form-label">Expected Refinance LTV (%)</label>
                            <input type="number" class="form-control" id="refinance_ltv_percentage" 
                                name="refinance_ltv_percentage" value="75" min="0" max="100" 
                                step="1" required>
                            <div class="form-text">Expected Loan-to-Value ratio for refinance</div>
                        </div>
                        <div class="col-md-6">
                            <label for="max_cash_left" class="form-label">Maximum Cash Left in Deal</label>
                            <input type="number" class="form-control" id="max_cash_left" 
                                name="max_cash_left" value="5000" min="0" 
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
                <div class="card-header">Operating Income</div>
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
                                value="2.0" min="0" max="100" step="0.5" 
                                placeholder="Percentage of rent for maintenance" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="vacancy_percentage" class="form-label">Vacancy (% of rent)</label>
                            <input type="number" class="form-control" id="vacancy_percentage" name="vacancy_percentage" 
                                value="4.0" min="0" max="100" step="0.5" 
                                placeholder="Percentage of rent for vacancy" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="capex_percentage" class="form-label">CapEx (% of rent)</label>
                            <input type="number" class="form-control" id="capex_percentage" name="capex_percentage" 
                                value="2.0" min="0" max="100" step="0.5" 
                                placeholder="Percentage of rent for capital expenditures" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="management_percentage" class="form-label">Management (% of rent)</label>
                            <input type="number" class="form-control" id="management_percentage" name="management_percentage" 
                                value="8.0" min="0" max="100" step="0.5" 
                                placeholder="Percentage of rent for property management" required>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    getPadSplitLTRHTML() {
        const ltrHtml = this.getLongTermRentalHTML();
        return ltrHtml.replace('</div></div>', `${this.PADSPLIT_EXPENSES}</div></div>`);
    },

    getPadSplitBRRRRHTML() {
        const brrrHtml = this.getBRRRRHTML();
        return brrrHtml.replace('</div></div>', `${this.PADSPLIT_EXPENSES}</div></div>`);
    }
};

// Main Module
const analysisModule = {
    state: {
        currentAnalysisId: null,
        initialAnalysisType: null,
        isSubmitting: false,
        typeChangeInProgress: false
    },

    init() {
        console.log('Initializing analysis module');
        this.initToastr();
        this.setupForm();
        this.initEventListeners();
    },

    initToastr() {
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

    setupForm() {
        const form = document.querySelector('#analysisForm');
        if (!form) {
            console.error('Analysis form not found');
            return;
        }

        const freshForm = form.cloneNode(true);
        form.replaceWith(freshForm);

        const analysisId = this.getAnalysisIdFromUrl();
        
        if (analysisId) {
            this.setupEditMode(freshForm, analysisId);
        } else {
            this.setupCreateMode(freshForm);
        }
    },

    setupEditMode(form, analysisId) {
        this.state.currentAnalysisId = analysisId;
        form.setAttribute('data-analysis-id', analysisId);
        form.addEventListener('submit', (e) => this.handleEditSubmit(e, analysisId));
        this.loadAnalysisData(analysisId);
    },

    setupCreateMode(form) {
        form.addEventListener('submit', (e) => this.handleSubmit(e));
    },

    initAnalysisTypeHandler() {
        const analysisType = document.getElementById('analysis_type');
        if (!analysisType) return;
        
        // Remove existing event listeners
        const newAnalysisType = analysisType.cloneNode(true);
        analysisType.parentNode.replaceChild(newAnalysisType, analysisType);
        
        this.state.initialAnalysisType = newAnalysisType.value;
        this.loadTypeFields(this.state.initialAnalysisType);
        
        // Only add change handler after initial load
        setTimeout(() => {
            newAnalysisType.addEventListener('change', (e) => this.handleTypeChange(e.target.value));
        }, 100);
    },

    loadTypeFields(type) {
        const container = document.getElementById('financial');
        if (!container) return;
        
        const templates = {
            'LTR': TEMPLATES.getLongTermRentalHTML(),
            'PadSplit LTR': TEMPLATES.getPadSplitLTRHTML(),
            'BRRRR': TEMPLATES.getBRRRRHTML(),
            'PadSplit BRRRR': TEMPLATES.getPadSplitBRRRRHTML()
        };
        
        container.innerHTML = templates[type] || 
            '<p>Financial details for this analysis type are not yet implemented.</p>';
        
        this.initFieldHandlers(type);
    },

    initTabHandling() {
        const reportTab = document.getElementById('reports-tab');
        const financialTab = document.getElementById('financial-tab');
        
        if (reportTab && financialTab) {
            reportTab.addEventListener('click', () => {
                this.state.currentAnalysisId = this.getAnalysisIdFromUrl();
            });
            
            financialTab.addEventListener('click', () => {
                this.state.currentAnalysisId = this.getAnalysisIdFromUrl();
            });
        }
    },

    initReportEventHandlers() {
        // Add event handlers for report buttons
        const editBtn = document.getElementById('editAnalysisBtn');
        if (editBtn) {
            editBtn.addEventListener('click', () => this.editAnalysis());
        }
        
        const createNewBtn = document.getElementById('createNewAnalysisBtn');
        if (createNewBtn) {
            createNewBtn.addEventListener('click', () => this.createNewAnalysis());
        }
        
        // Add PDF download handler
        const downloadPdfBtn = document.querySelector('.card-header button');
        if (downloadPdfBtn) {
            downloadPdfBtn.addEventListener('click', () => this.downloadPdf(this.state.currentAnalysisId));
        }
    },

    initEventListeners() {
        this.initAddressAutocomplete();
        this.initLoanHandlers();
        this.initAnalysisTypeHandler();
        this.initTabHandling();
        this.initReportEventHandlers();
    },

    getAnalysisIdFromUrl() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('analysis_id');
    },

    parseValue: {
        money: (value) => {
            if (!value) return 0;
            return typeof value === 'string' ? 
                parseFloat(value.replace(/[$,]/g, '')) || 0 :
                parseFloat(value) || 0;
        },
        
        percentage: (value) => {
            if (!value) return 0;
            return typeof value === 'string' ? 
                parseFloat(value.replace(/%/g, '')) || 0 :
                parseFloat(value) || 0;
        },
        
        integer: (value) => {
            if (!value) return 0;
            return parseInt(value) || 0;
        }
    },

    prepareFormData(form, analysisId = null) {
        const formData = new FormData(form);
        const data = {
            id: analysisId,
            analysis_type: formData.get('analysis_type'),
            analysis_name: formData.get('analysis_name'),
            property_address: formData.get('property_address')
        };
    
        // Add all numeric fields
        NUMERIC_FIELDS.MONEY.forEach(field => {
            data[field] = this.parseValue.money(formData.get(field));
        });
        
        NUMERIC_FIELDS.PERCENTAGE.forEach(field => {
            data[field] = this.parseValue.percentage(formData.get(field));
        });
        
        NUMERIC_FIELDS.INTEGER.forEach(field => {
            data[field] = this.parseValue.integer(formData.get(field));
        });
    
        // Handle loans for LTR analysis types
        if (data.analysis_type.includes('LTR')) {
            data.loans = this.collectLoanData(form);
        }
    
        // Handle BRRRR-specific fields
        if (data.analysis_type.includes('BRRRR')) {
            data.initial_interest_only = form.querySelector('#initial_interest_only')?.checked || false;
        }
    
        // If editing, include creation timestamp
        if (analysisId) {
            data.create_new = this.state.initialAnalysisType !== data.analysis_type;
        }
    
        return data;
    },
    
    collectLoanData(form) {
        const loans = [];
        const loanSections = form.querySelectorAll('.loan-section');
        
        loanSections.forEach((section, index) => {
            const loanNumber = index + 1;
            const loan = {
                name: form.querySelector(`#loan_name_${loanNumber}`)?.value || '',
                amount: this.parseValue.money(form.querySelector(`#loan_amount_${loanNumber}`)?.value),
                down_payment: this.parseValue.money(form.querySelector(`#loan_down_payment_${loanNumber}`)?.value),
                interest_rate: this.parseValue.percentage(form.querySelector(`#loan_interest_rate_${loanNumber}`)?.value),
                term: this.parseValue.integer(form.querySelector(`#loan_term_${loanNumber}`)?.value),
                closing_costs: this.parseValue.money(form.querySelector(`#loan_closing_costs_${loanNumber}`)?.value)
            };
            
            // Only add loan if all fields have values
            if (Object.values(loan).some(val => val)) {
                loans.push(loan);
            }
        });
        
        return loans;
    },
    
    resetSubmitButton(button, text) {
        if (!button) return;
        button.disabled = false;
        button.innerHTML = text;
    },

    populateFormFields(analysis) {
        // Basic Details
        this.setFieldValue('analysis_name', analysis.analysis_name, 'text');
        this.setFieldValue('property_address', analysis.property_address, 'text');
        this.setFieldValue('home_square_footage', analysis.home_square_footage, 'integer');
        this.setFieldValue('lot_square_footage', analysis.lot_square_footage, 'integer');
        this.setFieldValue('year_built', analysis.year_built, 'integer');
    
        const analysisType = document.getElementById('analysis_type');
        if (analysisType) {
            analysisType.value = analysis.analysis_type;
            analysisType.dispatchEvent(new Event('change'));
        }
    
        setTimeout(() => {
            // Purchase Details
            this.setFieldValue('purchase_price', analysis.purchase_price, 'money');
            this.setFieldValue('after_repair_value', analysis.after_repair_value, 'money');
            this.setFieldValue('renovation_costs', analysis.renovation_costs, 'money');
            this.setFieldValue('renovation_duration', analysis.renovation_duration, 'integer');
            this.setFieldValue('cash_to_seller', analysis.cash_to_seller, 'money');
            this.setFieldValue('closing_costs', analysis.closing_costs, 'money');
            this.setFieldValue('assignment_fee', analysis.assignment_fee, 'money');
            this.setFieldValue('marketing_costs', analysis.marketing_costs, 'money');
    
            // Financial Metrics
            this.setFieldValue('monthly_rent', analysis.monthly_rent, 'money');
            this.setFieldValue('max_cash_left', analysis.max_cash_left, 'money');
    
            // Operating Expenses
            this.setFieldValue('property_taxes', analysis.property_taxes, 'money');
            this.setFieldValue('insurance', analysis.insurance, 'money');
            this.setFieldValue('hoa_coa_coop', analysis.hoa_coa_coop, 'money');
            this.setFieldValue('management_percentage', analysis.management_percentage, 'percentage');
            this.setFieldValue('capex_percentage', analysis.capex_percentage, 'percentage');
            this.setFieldValue('vacancy_percentage', analysis.vacancy_percentage, 'percentage');
            this.setFieldValue('repairs_percentage', analysis.repairs_percentage, 'percentage');
    
            // BRRRR-specific fields
            if (analysis.analysis_type.includes('BRRRR')) {
                this.populateBRRRRFields(analysis);
            }
    
            // PadSplit fields 
            if (analysis.analysis_type.includes('PadSplit')) {
                this.populatePadSplitFields(analysis);
            }
    
            // Handle loans
            if (analysis.analysis_type.includes('LTR')) {
                this.populateLoanFields(analysis);
            }
        }, 500);
    },

    setFieldValue(id, value, type = 'text') {
        const field = document.getElementById(id);
        if (!field) return false;
        
        try {
            let parsedValue;
            
            // Handle different types of values
            switch (type) {
                case 'money':
                    parsedValue = this.parseValue.money(value);
                    break;
                    
                case 'percentage':
                    parsedValue = this.parseValue.percentage(value);
                    break;
                    
                case 'integer':
                    parsedValue = this.parseValue.integer(value);
                    break;
                    
                default:
                    parsedValue = value;
            }
            
            field.value = parsedValue;
            field.dispatchEvent(new Event('change', { bubbles: true }));
            return true;
        } catch (error) {
            console.error(`Error setting value for field ${id}:`, error);
            return false;
        }
    },

    populateBRRRRFields(analysis) { 
        // Initial loan details
        this.setFieldValue('initial_loan_amount', analysis.initial_loan_amount, 'money');
        this.setFieldValue('initial_down_payment', analysis.initial_down_payment, 'money');
        this.setFieldValue('initial_interest_rate', analysis.initial_interest_rate, 'percentage');
        this.setFieldValue('initial_loan_term', analysis.initial_loan_term, 'integer');
        this.setFieldValue('initial_closing_costs', analysis.initial_closing_costs, 'money');
        
        const initialInterestOnly = document.getElementById('initial_interest_only');
        if (initialInterestOnly) {
            initialInterestOnly.checked = Boolean(analysis.initial_interest_only);
        }
        
        // Refinance details
        this.setFieldValue('refinance_loan_amount', analysis.refinance_loan_amount, 'money');
        this.setFieldValue('refinance_down_payment', analysis.refinance_down_payment, 'money');
        this.setFieldValue('refinance_interest_rate', analysis.refinance_interest_rate, 'percentage');
        this.setFieldValue('refinance_loan_term', analysis.refinance_loan_term, 'integer');
        this.setFieldValue('refinance_closing_costs', analysis.refinance_closing_costs, 'money');
        this.setFieldValue('refinance_ltv_percentage', analysis.refinance_ltv_percentage, 'percentage');
        
        // Trigger any calculation updates
        const refinanceLtvField = document.getElementById('refinance_ltv_percentage');
        if (refinanceLtvField) {
            refinanceLtvField.dispatchEvent(new Event('input'));
        }
    },
     
    populatePadSplitFields(analysis) {    
        this.setFieldValue('padsplit_platform_percentage', analysis.padsplit_platform_percentage, 'percentage');
        this.setFieldValue('utilities', analysis.utilities, 'money');
        this.setFieldValue('internet', analysis.internet, 'money');
        this.setFieldValue('cleaning_costs', analysis.cleaning_costs, 'money');
        this.setFieldValue('pest_control', analysis.pest_control, 'money');
        this.setFieldValue('landscaping', analysis.landscaping, 'money');
    },

    setLoanFields(loanNumber, loan) {
        const fields = {
            name: `loan_name_${loanNumber}`,
            amount: `loan_amount_${loanNumber}`,
            down_payment: `loan_down_payment_${loanNumber}`,
            interest_rate: `loan_interest_rate_${loanNumber}`, 
            term: `loan_term_${loanNumber}`,  // Maps directly to 'term' from JSON
            closing_costs: `loan_closing_costs_${loanNumber}`
        };
     
        Object.entries(fields).forEach(([key, fieldId]) => {
            let value = loan[key];
            let type = key.includes('amount') || key.includes('payment') || key.includes('costs') ? 'money' : 
                      key.includes('rate') ? 'percentage' : 
                      key.includes('term') ? 'number' : 'text';
                      
            this.setFieldValue(fieldId, value, type);
        });
    },
     
    populateLoanFields(analysis) {
        const loansContainer = document.getElementById('loans-container');
        if (!loansContainer) return;
     
        loansContainer.innerHTML = '';
        
        if (analysis.loans?.length > 0) {
            analysis.loans.forEach((loan, index) => {
                const addLoanBtn = document.getElementById('add-loan-btn');
                if (addLoanBtn) {
                    addLoanBtn.click();
                    
                    setTimeout(() => {
                        const loanNumber = index + 1;
                        this.setLoanFields(loanNumber, {
                            name: loan.name,
                            amount: loan.amount,
                            down_payment: loan.down_payment,
                            interest_rate: loan.interest_rate,
                            term: loan.term,
                            closing_costs: loan.closing_costs
                        });
                    }, 100);
                }
            });
        }
    },

    async handleSubmit(event) {
        event.preventDefault();
        if (this.state.isSubmitting) return;
        
        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        try {
            this.state.isSubmitting = true;
            this.updateSubmitButton(submitBtn, 'Creating...');
            
            if (!this.validateForm(form)) {
                throw new Error('Form validation failed');
            }
            
            const analysisData = this.prepareFormData(form);
            const response = await this.api.submitAnalysis(analysisData);
            
            if (response.success) {
                this.handleSubmitSuccess(response);
            } else {
                throw new Error(response.message || 'Unknown error occurred');
            }
        } catch (error) {
            console.error('Submit error:', error);
            toastr.error(error.message || 'Error creating analysis');
        } finally {
            this.state.isSubmitting = false;
            this.resetSubmitButton(submitBtn, 'Create Analysis');
        }
    },

    handleUpdateSuccess(response) {
        toastr.success('Analysis updated successfully');
        const analysisId = response.analysis?.id;
        if (analysisId) {
            // Reload the current page with the updated analysis
            window.location.href = `/analyses/view_analysis/${analysisId}`;
        } else {
            // Fallback to analysis list if no ID
            window.location.href = '/analyses/view_edit_analysis';
        }
    },

    populateReportsTab(analysis) {
        console.log('Starting populateReportsTab with analysis:', analysis);
        const reportsContent = document.querySelector('#reports');
        
        if (!reportsContent) {
            console.error('Reports content element not found');
            return;
        }
    
        const html = this.getReportHTML(analysis);
        console.log('Generated report HTML:', html);
        reportsContent.innerHTML = html;
        
        // Initialize tooltips after content is added
        const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltips.forEach(tooltip => new bootstrap.Tooltip(tooltip));
    },

    async handleEditSubmit(event, analysisId) {
        event.preventDefault();
        if (this.state.isSubmitting) return;
        
        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        try {
            this.state.isSubmitting = true;
            this.updateSubmitButton(submitBtn, 'Updating...');
            
            if (!this.validateForm(form)) {
                throw new Error('Form validation failed');
            }
            
            const analysisData = this.prepareFormData(form, analysisId);
            console.log('Submitting analysis data:', analysisData);
            
            const response = await this.updateAnalysis(analysisData);
            console.log('Update response:', response);

            console.log("Full analysis data:", JSON.stringify(response.analysis, null, 2));
            console.log("Loans data:", JSON.stringify(response.analysis.loans, null, 2));
            
            if (response.success && response.analysis) {
                toastr.success('Analysis updated successfully');
                console.log('Populating reports tab with analysis:', response.analysis);
                this.populateReportsTab(response.analysis);
                
                const reportsTab = document.getElementById('reports-tab');
                if (reportsTab) {
                    console.log('Switching to reports tab');
                    reportsTab.click();
                } else {
                    console.error('Reports tab element not found');
                }
            } else {
                throw new Error(response.message || 'Unknown error occurred');
            }
        } catch (error) {
            console.error('Update error:', error);
            toastr.error(error.message || 'Error updating analysis');
        } finally {
            this.state.isSubmitting = false;
            this.resetSubmitButton(submitBtn, 'Update Analysis');
        }
    },

    validateForm(form) {
        let isValid = true;
        const validationRules = {
            required: () => this.validateRequired(form),
            numeric: () => this.validateNumeric(form),
            percentage: () => this.validatePercentage(form),
            year: () => this.validateYear(form),
            loans: () => this.validateLoans(form)
        };

        Object.entries(validationRules).forEach(([rule, validator]) => {
            if (!validator()) {
                isValid = false;
            }
        });

        return isValid;
    },

    validateRequired(form) {
        const requiredFields = form.querySelectorAll('[required]');
        return Array.from(requiredFields).every(field => {
            const isValid = field.value.trim() !== '';
            this.toggleFieldValidation(field, isValid);
            return isValid;
        });
    },

    validateNumeric(form) {
        const numericFields = form.querySelectorAll('input[type="number"]');
        return Array.from(numericFields).every(field => {
            const value = parseFloat(field.value);
            const isValid = !isNaN(value) && value >= 0;
            this.toggleFieldValidation(field, isValid);
            return isValid;
        });
    },

    validatePercentage(form) {
        return NUMERIC_FIELDS.PERCENTAGE.every(fieldName => {
            const field = form.querySelector(`#${fieldName}`);
            if (!field) return true;
            
            const value = parseFloat(field.value);
            const isValid = !isNaN(value) && value >= 0 && value <= 100;
            this.toggleFieldValidation(field, isValid);
            return isValid;
        });
    },

    validateYear(form) {
        const yearField = form.querySelector('#year_built');
        if (!yearField) return true;
        
        const year = this.parseValue.integer(yearField.value);
        const currentYear = new Date().getFullYear();
        const isValid = !isNaN(year) && year >= 1850 && year <= currentYear && 
                     yearField.value.length === 4;
        
        this.toggleFieldValidation(yearField, isValid);
        return isValid;
    },

    validateLoans(form) {
        const loanSections = form.querySelectorAll('.loan-section');
        return Array.from(loanSections).every(section => {
            const fields = section.querySelectorAll('input');
            const filledFields = Array.from(fields).filter(f => f.value.trim());
            
            const isValid = filledFields.length === 0 || filledFields.length === fields.length;
            fields.forEach(field => this.toggleFieldValidation(field, isValid));
            return isValid;
        });
    },

    toggleFieldValidation(field, isValid) {
        field.classList.toggle('is-invalid', !isValid);
        return isValid;
    },

    async loadAnalysisData(analysisId) {
        try {
            const response = await fetch(`/analyses/get_analysis/${analysisId}`);
            if (!response.ok) {
                throw new Error('Failed to load analysis');
            }
            const data = await response.json();
            if (data.success) {
                this.populateFormFields(data.analysis);
            }
        } catch (error) {
            console.error('Error loading analysis:', error);
            toastr.error('Error loading analysis data');
        }
    },

    async submitAnalysis(data) {
        const response = await fetch('/analyses/create_analysis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to create analysis');
        }
        return response.json();
    },

    async updateAnalysis(data) {
        const response = await fetch('/analyses/update_analysis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to update analysis');
        }
        return response.json();
    },

    async downloadPdf(analysisId) {
        const response = await fetch(`/analyses/generate_pdf/${analysisId}`);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to generate PDF');
        }
        return response.blob();
    },

    async searchAddress(query) {
        const response = await fetch(`/api/autocomplete?query=${encodeURIComponent(query)}`);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to search address');
        }
        return response.json();
    },

    updateSubmitButton(button, text, disabled = true) {
        if (!button) return;
        button.disabled = disabled;
        button.innerHTML = disabled ? 
            `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> ${text}` :
            text;
    },

    showTypeChangeConfirmation(newType) {
        return new Promise(resolve => {
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
    },

    resetTypeSelector() {
        const analysisType = document.getElementById('analysis_type');
        if (analysisType) {
            analysisType.value = this.state.initialAnalysisType;
        }
    },

    async handleTypeChange(newType) {
        if (this.state.typeChangeInProgress) return;
        
        try {
            this.state.typeChangeInProgress = true;
            
            if (!this.state.currentAnalysisId) {
                this.loadTypeFields(newType);
                this.state.initialAnalysisType = newType;
                return;
            }
            
            this.showTypeChangeConfirmation(newType)
                .then(confirmed => {
                    if (!confirmed) {
                        this.resetTypeSelector();
                        return;
                    }
                    return this.updateAnalysisType(newType);
                })
                .catch(error => {
                    console.error('Type change error:', error);
                    toastr.error(error.message || 'Error changing analysis type');
                    this.resetTypeSelector();
                });
        } finally {
            this.state.typeChangeInProgress = false;
        }
    },

    loadTypeFields(type) {
        const container = document.getElementById('financial');
        if (!container) return;
        
        const templates = {
            'LTR': TEMPLATES.getLongTermRentalHTML(),
            'PadSplit LTR': TEMPLATES.getPadSplitLTRHTML(),
            'BRRRR': TEMPLATES.getBRRRRHTML(),
            'PadSplit BRRRR': TEMPLATES.getPadSplitBRRRRHTML()
        };
        
        container.innerHTML = templates[type] || 
            '<p>Financial details for this analysis type are not yet implemented.</p>';
        
        this.initFieldHandlers(type);
    },

    initFieldHandlers(type) {
        this.initLoanHandlers();
        if (type.includes('BRRRR')) {
            this.initRefinanceCalculations();
        }
    },

    getReportHTML(analysis) {
        // Store current analysis ID for PDF downloads
        this.currentAnalysisId = analysis.id;
    
        // Ensure proper formatting of numeric values
        const formatValue = (value, type) => {
            if (value === undefined || value === null) return type === 'money' ? '$0.00' : '0.00%';
            // If value is already a formatted string, return it
            if (typeof value === 'string' && (value.includes('$') || value.includes('%'))) return value;
            // Otherwise format it
            return type === 'money' ? this.parseValue.money(value) : this.parseValue.percentage(value);
        };
    
        // Handle purchase price and project costs calculations
        const purchasePrice = typeof analysis.purchase_price === 'number' ? 
            analysis.purchase_price : 
            parseFloat(String(analysis.purchase_price).replace(/[$,]/g, ''));
        
        const mao = this.calculateMAO({
            purchase_price: purchasePrice,
            total_project_costs: analysis.total_project_costs,
            max_cash_left: analysis.max_cash_left
        });
    
        const baseSummaryHTML = `
            <div class="row align-items-start mb-4">
                <div class="col">
                    <h4 class="mb-0">${analysis.analysis_type || 'Analysis'}: ${analysis.analysis_name || 'Untitled'}</h4>
                </div>
                <div class="col-auto">
                    <button 
                        onclick="analysisModule.downloadPdf('${this.currentAnalysisId}')" 
                        class="btn btn-primary ms-3"
                    >Download PDF</button>
                </div>
            </div>
            <div class="card mb-4">
                <div class="card mb-4">
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6 mb-4">
                                <h5 class="mb-3">Purchase Details</h5>
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <p class="mb-2"><strong>Purchase Price:</strong> ${formatValue(analysis.purchase_price, 'money')}</p>
                                        <p class="mb-2"><strong>Renovation Costs:</strong> ${formatValue(analysis.renovation_costs, 'money')}</p>
                                        <p class="mb-2"><strong>After Repair Value:</strong> ${formatValue(analysis.after_repair_value, 'money')}</p>
                                        <p class="mb-2"><strong>Maximum Allowable Offer:</strong> ${formatValue(mao, 'money')}</p>
                                    </div>
                                </div>
                            </div>
    
                            <div class="col-md-6 mb-4">
                                <h5 class="mb-3">Income & Returns</h5>
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <p class="mb-2"><strong>Monthly Rent:</strong> ${formatValue(analysis.monthly_rent, 'money')}</p>
                                        <p class="mb-2"><strong>Monthly Cash Flow:</strong> ${formatValue(analysis.monthly_cash_flow, 'money')}</p>
                                        <p class="mb-2"><strong>Annual Cash Flow:</strong> ${formatValue(analysis.annual_cash_flow, 'money')}</p>
                                        <p class="mb-2"><strong>Cash-on-Cash Return:</strong> ${formatValue(analysis.cash_on_cash_return, 'percentage')}</p>
                                        <p class="mb-2"><strong>ROI:</strong> ${formatValue(analysis.roi, 'percentage')}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>`;
    
        if (analysis.analysis_type?.includes('BRRRR')) {
            return baseSummaryHTML + this.getBRRRRDetailsHTML(analysis);
        }
    
        return baseSummaryHTML;
    },
    
    getBRRRRDetailsHTML(analysis) {
        return `
            <div class="row">
                <div class="col-md-6">
                    <h5>Investment Summary</h5>
                    <div class="card bg-light mb-3">
                        <div class="card-body">
                            <p class="mb-2">
                                <strong>Total Project Costs:</strong> ${this.parseValue.money(analysis.total_project_costs)}
                                <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" data-bs-html="true" 
                                title="Purchase Price + Renovation Costs + All Closing Costs - Cash Out from Refi"></i>
                            </p>
                            <p class="mb-2">
                                <strong>After Repair Value:</strong> ${this.parseValue.money(analysis.after_repair_value)}
                            </p>
                            <p class="mb-2">
                                <strong>Refinance Loan Amount:</strong> ${this.parseValue.money(analysis.refinance_loan_amount)}
                                <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" data-bs-html="true" 
                                title="New loan based on ARV × LTV%"></i>
                            </p>
                            <p class="mb-2">
                                <strong>Total Cash Invested:</strong> ${this.parseValue.money(analysis.total_cash_invested)}
                                <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" data-bs-html="true" 
                                title="Total Project Costs - Refinance Loan Amount"></i>
                            </p>
                            <p class="mb-2">
                                <strong>Equity Captured:</strong> ${this.parseValue.money(analysis.equity_captured)}
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
                                <li>Amount: ${this.parseValue.money(analysis.initial_loan_amount)}</li>
                                <li>Interest Rate: ${this.parseValue.percentage(analysis.initial_interest_rate)}
                                    <span class="badge ${analysis.initial_interest_only ? 'bg-success' : 'bg-info'} ms-2">
                                        ${analysis.initial_interest_only ? 'Interest Only' : 'Amortized'}
                                    </span>
                                </li>
                                <li>Term: ${this.parseValue.integer(analysis.initial_loan_term)} months</li>
                                <li>Monthly Payment: ${this.parseValue.money(analysis.initial_monthly_payment)}</li>
                                <li>Down Payment: ${this.parseValue.money(analysis.initial_down_payment)}</li>
                                <li>Closing Costs: ${this.parseValue.money(analysis.initial_closing_costs)}</li>
                            </ul>
                            <p class="fw-bold mb-2">Refinance Loan:</p>
                            <ul class="list-unstyled ms-3">
                                <li>Amount: ${this.parseValue.money(analysis.refinance_loan_amount)}</li>
                                <li>Interest Rate: ${this.parseValue.percentage(analysis.refinance_interest_rate)}</li>
                                <li>Term: ${this.parseValue.integer(analysis.refinance_loan_term)} months</li>
                                <li>Monthly Payment: ${this.parseValue.money(analysis.refinance_monthly_payment)}</li>
                                <li>Down Payment: ${this.parseValue.money(analysis.refinance_down_payment)}</li>
                                <li>Closing Costs: ${this.parseValue.money(analysis.refinance_closing_costs)}</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>`;
    },

    async handleEditSubmit(event, analysisId) {
    event.preventDefault();
    if (this.state.isSubmitting) return;
    
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    
    try {
        this.state.isSubmitting = true;
        this.updateSubmitButton(submitBtn, 'Updating...');
        
        if (!this.validateForm(form)) {
            throw new Error('Form validation failed');
        }
        
        const analysisData = this.prepareFormData(form, analysisId);
        console.log('Submitting analysis data:', analysisData);
        
        const response = await this.updateAnalysis(analysisData);
        console.log('Update response:', response);
        
        if (response.success && response.analysis) {
            toastr.success('Analysis updated successfully');
            console.log('Populating reports tab with analysis:', response.analysis);
            this.populateReportsTab(response.analysis);
            
            const reportsTab = document.getElementById('reports-tab');
            if (reportsTab) {
                console.log('Switching to reports tab');
                reportsTab.click();
            } else {
                console.error('Reports tab element not found');
            }
        } else {
            throw new Error(response.message || 'Unknown error occurred');
        }
    } catch (error) {
        console.error('Update error:', error);
        toastr.error(error.message || 'Error updating analysis');
    } finally {
        this.state.isSubmitting = false;
        this.resetSubmitButton(submitBtn, 'Update Analysis');
    }
},

    switchToReportsTab() {
        const tabs = {
            reports: {
                tab: document.querySelector('#reports-tab'),
                content: document.querySelector('#reports')
            },
            financial: {
                tab: document.querySelector('#financial-tab'),
                content: document.querySelector('#financial')
            }
        };
        
        if (!Object.values(tabs).every(({tab, content}) => tab && content)) {
            console.error('Missing required tab elements');
            return;
        }
        
        tabs.financial.tab.classList.remove('active');
        tabs.financial.content.classList.remove('show', 'active');
        tabs.reports.tab.classList.add('active');
        tabs.reports.content.classList.add('show', 'active');
    },

    initAddressAutocomplete() {
        const addressInput = document.getElementById('property_address');
        const resultsList = document.getElementById('addressSuggestions');
        let timeoutId;

        if (!addressInput || !resultsList) return;

        const handleInput = async () => {
            clearTimeout(timeoutId);
            const query = addressInput.value;
            
            if (query.length <= 2) {
                resultsList.innerHTML = '';
                return;
            }

            try {
                const response = await this.api.searchAddress(query);
                this.updateAddressSuggestions(response, resultsList, addressInput);
            } catch (error) {
                resultsList.innerHTML = `<li class="error">Error: ${error.message}</li>`;
            }
        };

        addressInput.addEventListener('input', () => {
            timeoutId = setTimeout(handleInput, 300);
        });

        document.addEventListener('click', (e) => {
            if (e.target !== addressInput && e.target !== resultsList) {
                resultsList.innerHTML = '';
            }
        });
    },

    initLoanHandlers() {
        const addLoanBtn = document.getElementById('add-loan-btn');
        const loansContainer = document.getElementById('loans-container');
        
        if (!addLoanBtn || !loansContainer || addLoanBtn.hasAttribute('data-initialized')) return;
        
        addLoanBtn.setAttribute('data-initialized', 'true');
        
        addLoanBtn.addEventListener('click', () => {
            const loanCount = loansContainer.querySelectorAll('.loan-section').length + 1;
            
            if (loanCount <= DEFAULTS.MAX_LOANS) {
                loansContainer.insertAdjacentHTML('beforeend', this.getLoanSectionHTML(loanCount));
                addLoanBtn.style.display = loanCount >= DEFAULTS.MAX_LOANS ? 'none' : 'block';
            }
        });

        loansContainer.addEventListener('click', (e) => {
            if (e.target.classList.contains('remove-loan-btn')) {
                this.handleLoanRemoval(e.target);
            }
        });
    },

    getLoanSectionHTML(loanNumber) {
        return `
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
                                    name="loans[${loanNumber}][name]" placeholder="Enter loan name" required>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="loan_amount_${loanNumber}" class="form-label">Loan Amount</label>
                                <input type="number" class="form-control" id="loan_amount_${loanNumber}" 
                                    name="loans[${loanNumber}][amount]" placeholder="Enter loan amount" required>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="loan_down_payment_${loanNumber}" class="form-label">Down Payment</label>
                                <input type="number" class="form-control" id="loan_down_payment_${loanNumber}" 
                                    name="loans[${loanNumber}][down_payment]" placeholder="Enter down payment amount" required>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="loan_interest_rate_${loanNumber}" class="form-label">Interest Rate (%)</label>
                                <input type="number" class="form-control" id="loan_interest_rate_${loanNumber}" 
                                    name="loans[${loanNumber}][interest_rate]" step="0.01" min="0" max="100" 
                                    placeholder="Enter interest rate" required>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="loan_term_${loanNumber}" class="form-label">Loan Term (months)</label>
                                <input type="number" class="form-control" id="loan_term_${loanNumber}" 
                                    name="loans[${loanNumber}][term]" min="1" 
                                    placeholder="Enter loan term in months" required>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="loan_closing_costs_${loanNumber}" class="form-label">Closing Costs</label>
                                <input type="number" class="form-control" id="loan_closing_costs_${loanNumber}" 
                                    name="loans[${loanNumber}][closing_costs]" 
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
    },

    handleLoanRemoval(button) {
        const loanSection = button.closest('.loan-section');
        if (!loanSection) return;
        
        loanSection.remove();
        this.reorderLoans();
        
        const addLoanBtn = document.getElementById('add-loan-btn');
        const remainingLoans = document.querySelectorAll('.loan-section');
        if (addLoanBtn) {
            addLoanBtn.style.display = remainingLoans.length < DEFAULTS.MAX_LOANS ? 'block' : 'none';
        }
    },

    reorderLoans() {
        const loans = document.querySelectorAll('.loan-section');
        loans.forEach((loan, index) => {
            const newIndex = index + 1;
            const heading = loan.querySelector('h5');
            if (heading) heading.textContent = `Loan ${newIndex}`;
            
            loan.querySelectorAll('input').forEach(input => {
                const fieldName = input.id.split('_').slice(0, -1).join('_');
                input.id = `${fieldName}_${newIndex}`;
                input.name = `loans[${newIndex}][${fieldName.split('_').pop()}]`;
            });
        });
    },

    initRefinanceCalculations() {
        const elements = {
            arv: document.getElementById('after_repair_value'),
            ltv: document.getElementById('refinance_ltv_percentage'),
            loanAmount: document.getElementById('refinance_loan_amount'),
            downPayment: document.getElementById('refinance_down_payment'),
            closingCosts: document.getElementById('refinance_closing_costs')
        };

        if (!Object.values(elements).every(Boolean)) return;

        const updateCalcs = () => {
            const arv = parseFloat(elements.arv.value) || 0;
            const ltv = parseFloat(elements.ltv.value) || 0;
            
            const loanAmount = (arv * ltv) / 100;
            elements.loanAmount.value = loanAmount.toFixed(2);
            
            const downPayment = (arv * (100 - ltv)) / 100;
            elements.downPayment.value = downPayment.toFixed(2);
            
            const closingCosts = loanAmount * 0.05;
            elements.closingCosts.value = closingCosts.toFixed(2);
        };

        elements.arv.addEventListener('input', updateCalcs);
        elements.ltv.addEventListener('input', updateCalcs);
    },

    calculateMAO(analysis) {
        try {
            // Ensure we're working with numbers
            const purchasePrice = typeof analysis.purchase_price === 'number' ? 
                analysis.purchase_price : 
                parseFloat(String(analysis.purchase_price).replace(/[$,]/g, '')) || 0;
                
            const projectCosts = typeof analysis.total_project_costs === 'number' ?
                analysis.total_project_costs :
                parseFloat(String(analysis.total_project_costs).replace(/[$,]/g, '')) || 0;
                
            const maxCashLeft = typeof analysis.max_cash_left === 'number' ?
                analysis.max_cash_left :
                parseFloat(String(analysis.max_cash_left).replace(/[$,]/g, '')) || DEFAULTS.MAX_CASH_LEFT;
    
            const mao = purchasePrice + (maxCashLeft - projectCosts);
            return isNaN(mao) ? 0 : mao;
        } catch (error) {
            console.error('Error calculating MAO:', error);
            return 0;
        }
    },
    
    // Helper function to parse money values from formatted strings
    parseMoney(value) {
        if (!value) return 0;
        return parseFloat(value.replace(/[$,]/g, '')) || 0;
    },
    
    // Helper function to parse percentage values from formatted strings
    parsePercentage(value) {
        if (!value) return 0;
        return parseFloat(value.replace(/%/g, '')) || 0;
    },

    calculateRefinanceDetails(arv, ltv) {
        const loanAmount = (arv * ltv) / 100;
        const downPayment = (arv * (100 - ltv)) / 100;
        const closingCosts = loanAmount * 0.05;
        
        return {
            loanAmount: this.parseValue.money(loanAmount),
            downPayment: this.parseValue.money(downPayment),
            closingCosts: this.parseValue.money(closingCosts)
        };
    },
};

// Clean up the initialization
document.addEventListener('DOMContentLoaded', () => {
    analysisModule.init();
});

// Export and global assignment
window.analysisModule = analysisModule;
export default analysisModule;