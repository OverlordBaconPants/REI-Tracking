const analysisModule = {
    init: function() {
        console.log('AnalysisModule initialized');
        const analysisForm = document.querySelector('#analysisForm');
        if (analysisForm) {
            console.log('Analysis form found');
            analysisForm.addEventListener('submit', this.handleSubmit.bind(this));
            this.initAddressAutocomplete();
            this.initAnalysisTypeHandler();
        } else {
            console.log('Analysis form not found');
        }

        // Set up event listeners for the new buttons
        const editBtn = document.getElementById('editAnalysisBtn');
        const createNewBtn = document.getElementById('createNewAnalysisBtn');
        
        if (editBtn) {
            editBtn.addEventListener('click', this.editAnalysis.bind(this));
        }
        
        if (createNewBtn) {
            createNewBtn.addEventListener('click', this.createNewAnalysis.bind(this));
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
                console.log('Input event triggered');
                clearTimeout(timeoutId);
                timeoutId = setTimeout(() => {
                    const query = this.value;
                    console.log('Query:', query);
                    if (query.length > 2) {
                        console.log('Making API call');
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
                            .then(data => {
                                console.log('API response:', data);
                                resultsList.innerHTML = '';
                                if (Array.isArray(data) && data.length > 0) {
                                    data.forEach(result => {
                                        const li = document.createElement('li');
                                        li.textContent = result.formatted;
                                        li.addEventListener('click', function() {
                                            addressInput.value = this.textContent;
                                            resultsList.innerHTML = '';
                                        });
                                        resultsList.appendChild(li);
                                    });
                                } else {
                                    resultsList.innerHTML = '<li>No results found</li>';
                                }
                            })
                            .catch(error => {
                                console.error('Error:', error);
                                resultsList.innerHTML = `<li>Error fetching results: ${error.message}</li>`;
                            });
                    } else {
                        resultsList.innerHTML = '';
                    }
                }, 300);
            });

            document.addEventListener('click', function(e) {
                if (e.target !== addressInput && e.target !== resultsList) {
                    resultsList.innerHTML = '';
                }
            });
        } else {
            console.error('Address input or results list not found');
        }
    },

    initAnalysisTypeHandler: function() {
        const analysisType = document.getElementById('analysis_type');
        const financialTab = document.getElementById('financial');
        
        if (analysisType && financialTab) {
            analysisType.addEventListener('change', () => {
                if (analysisType.value === 'Long-Term Rental') {
                    this.loadLongTermRentalFields(financialTab);
                } else if (analysisType.value === 'BRRRR') {
                    this.loadBRRRRFields(financialTab);
                } else {
                    // Clear the financial tab content for other analysis types
                    financialTab.innerHTML = '<p>Financial details for this analysis type are not yet implemented.</p>';
                }
            });
        }
    },

    loadLongTermRentalFields: function(container) {
        container.innerHTML = `
            <div class="card mb-4">
                <div class="card-header">Direct Expenses</div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="purchase_price" class="form-label">Purchase Price</label>
                            <input type="number" class="form-control" id="purchase_price" name="purchase_price" placeholder="The sales price as recorded on the ALTA or HUD" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="after_rehab_value" class="form-label">After Rehab Value</label>
                            <input type="number" class="form-control" id="after_rehab_value" name="after_rehab_value" placeholder="How much the property is worth after renovation" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="cash_to_seller" class="form-label">Cash to Seller</label>
                            <input type="number" class="form-control" id="cash_to_seller" name="cash_to_seller" placeholder="How much cash you gave the seller at closing" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="closing_costs" class="form-label">Closing Costs</label>
                            <input type="number" class="form-control" id="closing_costs" name="closing_costs" placeholder="How much it cost to close at settlement" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="assignment_fee" class="form-label">Assignment Fee / Agent Commission</label>
                            <input type="number" class="form-control" id="assignment_fee" name="assignment_fee" placeholder="How much it cost to work with someone to get you this property" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="marketing_costs" class="form-label">Marketing Costs</label>
                            <input type="number" class="form-control" id="marketing_costs" name="marketing_costs" placeholder="How much you intend to pay to market the property once ready" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="renovation_costs" class="form-label">Renovation Costs</label>
                            <input type="number" class="form-control" id="renovation_costs" name="renovation_costs" placeholder="How much you anticipate spending to renovate the property" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="renovation_duration" class="form-label">Renovation Duration (months)</label>
                            <input type="number" class="form-control" id="renovation_duration" name="renovation_duration" placeholder="How long before the property is ready for market" required>
                        </div>
                    </div>
                </div>
            </div>
            <div class="card mb-4">
                <div class="card-header">Financing</div>
                <div class="card-body" id="financing-section">
                    <button type="button" class="btn btn-primary mb-3" id="add-loan-btn">Add Loan</button>
                </div>
            </div>
            <div class="card mb-4">
                <div class="card-header">Operating Income</div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="monthly_income" class="form-label">Monthly Income</label>
                            <input type="number" class="form-control" id="monthly_income" name="monthly_income" placeholder="Include rents, subsidies, leases, storage, and any other incomes" required>
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
                            <input type="number" class="form-control" id="management_percentage" name="management_percentage" value="8" min="0" max="100" step="0.01" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="capex_percentage" class="form-label">CapEx (%)</label>
                            <input type="number" class="form-control" id="capex_percentage" name="capex_percentage" value="2" min="0" max="100" step="0.01" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="repairs_percentage" class="form-label">Repairs (%)</label>
                            <input type="number" class="form-control" id="repairs_percentage" name="repairs_percentage" value="2" min="0" max="100" step="0.01" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="vacancy_percentage" class="form-label">Vacancy (%)</label>
                            <input type="number" class="form-control" id="vacancy_percentage" name="vacancy_percentage" value="4" min="0" max="100" step="0.01" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-4 mb-3">
                            <label for="property_taxes" class="form-label">Property Taxes</label>
                            <input type="number" class="form-control" id="property_taxes" name="property_taxes" placeholder="Monthly taxes" required>
                        </div>
                        <div class="col-md-4 mb-3">
                            <label for="insurance" class="form-label">Insurance</label>
                            <input type="number" class="form-control" id="insurance" name="insurance" placeholder="Monthly insurance costs" required>
                        </div>
                        <div class="col-md-4 mb-3">
                            <label for="hoa_coa_coop" class="form-label">HOA/COA/COOP</label>
                            <input type="number" class="form-control" id="hoa_coa_coop" name="hoa_coa_coop" placeholder="Monthly association costs, if any" required>
                        </div>
                    </div>
                </div>
            </div>
        `;
        this.initLoanHandlers(container);
    },

    loadBRRRRFields: function(container) {
        container.innerHTML = `
            <div class="card mb-4">
                <div class="card-header">Purchase Details</div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="purchase_price" class="form-label">Purchase Price</label>
                            <input type="number" class="form-control" id="purchase_price" name="purchase_price" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="after_repair_value" class="form-label">After Repair Value (ARV)</label>
                            <input type="number" class="form-control" id="after_repair_value" name="after_repair_value" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="renovation_costs" class="form-label">Renovation Costs</label>
                            <input type="number" class="form-control" id="renovation_costs" name="renovation_costs" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="renovation_duration" class="form-label">Renovation Duration (months)</label>
                            <input type="number" class="form-control" id="renovation_duration" name="renovation_duration" required>
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
                            <input type="number" class="form-control" id="initial_loan_amount" name="initial_loan_amount" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="initial_down_payment" class="form-label">Initial Down Payment</label>
                            <input type="number" class="form-control" id="initial_down_payment" name="initial_down_payment" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="initial_interest_rate" class="form-label">Initial Interest Rate (%)</label>
                            <input type="number" class="form-control" id="initial_interest_rate" name="initial_interest_rate" step="0.01" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="initial_loan_term" class="form-label">Initial Loan Term (months)</label>
                            <input type="number" class="form-control" id="initial_loan_term" name="initial_loan_term" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="initial_closing_costs" class="form-label">Initial Closing Costs</label>
                            <input type="number" class="form-control" id="initial_closing_costs" name="initial_closing_costs" required>
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
                            <input type="number" class="form-control" id="refinance_loan_amount" name="refinance_loan_amount" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="refinance_down_payment" class="form-label">Refinance Down Payment</label>
                            <input type="number" class="form-control" id="refinance_down_payment" name="refinance_down_payment" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="refinance_interest_rate" class="form-label">Refinance Interest Rate (%)</label>
                            <input type="number" class="form-control" id="refinance_interest_rate" name="refinance_interest_rate" step="0.01" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="refinance_loan_term" class="form-label">Refinance Loan Term (months)</label>
                            <input type="number" class="form-control" id="refinance_loan_term" name="refinance_loan_term" required>
                        </div>
                        <div class="col-md-6 mb-3">

                        <label for="refinance_closing_costs" class="form-label">Refinance Closing Costs</label>
                            <input type="number" class="form-control" id="refinance_closing_costs" name="refinance_closing_costs" required>
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
                            <input type="number" class="form-control" id="monthly_rent" name="monthly_rent" required>
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
                            <input type="number" class="form-control" id="property_taxes" name="property_taxes" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="insurance" class="form-label">Monthly Insurance</label>
                            <input type="number" class="form-control" id="insurance" name="insurance" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="maintenance_percentage" class="form-label">Maintenance (% of rent)</label>
                            <input type="number" class="form-control" id="maintenance_percentage" name="maintenance_percentage" value="2" min="0" max="100" step="0.1" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="vacancy_percentage" class="form-label">Vacancy (% of rent)</label>
                            <input type="number" class="form-control" id="vacancy_percentage" name="vacancy_percentage" value="4" min="0" max="100" step="0.1" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="capex_percentage" class="form-label">CapEx (% of rent)</label>
                            <input type="number" class="form-control" id="capex_percentage" name="capex_percentage" value="2" min="0" max="100" step="0.1" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="management_percentage" class="form-label">Management (% of rent)</label>
                            <input type="number" class="form-control" id="management_percentage" name="management_percentage" value="0" min="0" max="100" step="0.1" required>
                        </div>
                    </div>
                </div>
            </div>
        `;
        this.initLoanHandlers(container);
    },

    initLoanHandlers: function(container) {
        const addLoanBtn = container.querySelector('#add-loan-btn');
        const financingSection = container.querySelector('#financing-section');
        let loanCount = 0;

        if (addLoanBtn && financingSection) {
            addLoanBtn.addEventListener('click', () => {
                loanCount++;
                const loanHtml = `
                    <div class="loan-section mb-3">
                        <h5>Loan ${loanCount}</h5>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="loan_name_${loanCount}" class="form-label">Loan Name</label>
                                <input type="text" class="form-control" id="loan_name_${loanCount}" name="loans[${loanCount}][name]" required>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="loan_amount_${loanCount}" class="form-label">Loan Amount</label>
                                <input type="number" class="form-control" id="loan_amount_${loanCount}" name="loans[${loanCount}][amount]" required>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="loan_down_payment_${loanCount}" class="form-label">Down Payment</label>
                                <input type="number" class="form-control" id="loan_down_payment_${loanCount}" name="loans[${loanCount}][down_payment]" required>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="loan_interest_rate_${loanCount}" class="form-label">Interest Rate (%)</label>
                                <input type="number" class="form-control" id="loan_interest_rate_${loanCount}" name="loans[${loanCount}][interest_rate]" step="0.01" required>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="loan_term_${loanCount}" class="form-label">Loan Term (months)</label>
                                <input type="number" class="form-control" id="loan_term_${loanCount}" name="loans[${loanCount}][term]" required>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="loan_closing_costs_${loanCount}" class="form-label">Closing Costs</label>
                                <input type="number" class="form-control" id="loan_closing_costs_${loanCount}" name="loans[${loanCount}][closing_costs]" required>
                            </div>
                        </div>
                        <div class="col-md-12 mb-3">
                            <button type="button" class="btn btn-danger remove-loan-btn">Remove Loan</button>
                        </div>
                    </div>
                `;

                financingSection.insertAdjacentHTML('beforeend', loanHtml);

                if (loanCount >= 3) {
                    addLoanBtn.style.display = 'none';
                }
            });

            // Event delegation for remove loan buttons
            financingSection.addEventListener('click', (e) => {
                if (e.target.classList.contains('remove-loan-btn')) {
                    e.target.closest('.loan-section').remove();
                    loanCount--;
                    if (loanCount < 3) {
                        addLoanBtn.style.display = 'block';
                    }
                }
            });
        }
    },
    

    handleSubmit: function(event, analysisId = null) {
        event.preventDefault();
        console.log('Form submission started');
        
        const form = event.target;
        const formData = new FormData(form);
        
        if (!this.validateForm(form)) {
            console.log('Form validation failed');
            return;
        }
    
        const analysisData = Object.fromEntries(formData.entries());
        
        // Process loan data
        analysisData.loans = [];
        for (let i = 1; i <= 3; i++) {
            if (formData.get(`loans[${i}][name]`)) {
                analysisData.loans.push({
                    name: formData.get(`loans[${i}][name]`),
                    amount: parseFloat(formData.get(`loans[${i}][amount]`)),
                    down_payment: parseFloat(formData.get(`loans[${i}][down_payment]`)),
                    interest_rate: parseFloat(formData.get(`loans[${i}][interest_rate]`)),
                    term: parseInt(formData.get(`loans[${i}][term]`)),
                    closing_costs: parseFloat(formData.get(`loans[${i}][closing_costs]`))
                });
            }
        }
        
        // Ensure all numeric fields are parsed as numbers
        ['monthly_income', 'management_percentage', 'capex_percentage', 'repairs_percentage', 'vacancy_percentage',
            'property_taxes', 'insurance', 'hoa_coa_coop', 'renovation_costs', 'renovation_duration'].forEach(field => {
            analysisData[field] = parseFloat(analysisData[field]);
        });
    
        // If we're editing an existing analysis, include the ID
        if (analysisId) {
            analysisData.id = analysisId;
        }
           
        console.log('Sending analysis data:', JSON.stringify(analysisData, null, 2));
    
        const url = analysisId ? '/analyses/update_analysis' : '/analyses/create_analysis';
        const method = analysisId ? 'PUT' : 'POST';
    
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
                this.populateReportsTab(data.analysis);
                this.switchToReportsTab();
                this.showReportActions();
            } else {
                throw new Error(data.message || 'Unknown error occurred');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert(`An error occurred while creating the analysis: ${error.message || 'Please try again.'}`);
        });
    },
    
    populateReportsTab: function(analysis) {
        console.log('Populating reports tab with analysis:', analysis);
        this.currentAnalysisId = analysis.id;
        console.log('Set currentAnalysisId to:', this.currentAnalysisId);
        const reportsContent = document.querySelector('#reports');
        if (!reportsContent) {
            console.error('Reports content element not found');
            return;
        }
    
        let html = `
            <div class="card mb-4">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <span>${analysis.analysis_type} Analysis: ${analysis.analysis_name}</span>
                    <button id="downloadPdfBtn" class="btn btn-primary">Download PDF</button>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h5>Purchase and Financing</h5>
                            <p>Purchase Price: $${analysis.purchase_price}</p>
                            <p>Renovation Costs: $${analysis.renovation_costs}</p>
                            <p>After Repair Value (ARV): $${analysis.after_repair_value}</p>
                            <p>Initial Loan Amount: $${analysis.initial_loan_amount}</p>
                            <p>Refinance Loan Amount: $${analysis.refinance_loan_amount}</p>
                        </div>
                        <div class="col-md-6">
                            <h5>Income and Returns</h5>
                            <p>Monthly Rent: $${analysis.monthly_rent}</p>
                            <p>Monthly Cash Flow: $${analysis.monthly_cash_flow}</p>
                            <p>Annual Cash Flow: $${analysis.annual_cash_flow}</p>
                            <p>Cash-on-Cash Return: ${analysis.cash_on_cash_return}</p>
                            <p>Return on Investment (ROI): ${analysis.roi}</p>
                        </div>
                    </div>
                    <div class="row mt-4">
                        <div class="col-md-6">
                            <h5>Investment Summary</h5>
                            <p>Total Cash Invested: $${analysis.total_cash_invested}</p>
                            <p>Equity Captured: $${analysis.equity_captured}</p>
                            <p>Cash Recouped: $${analysis.cash_recouped}</p>
                        </div>
                        <div class="col-md-6">
                            <h5>Expenses</h5>
                            <p>Total Monthly Expenses: $${analysis.total_expenses}</p>
                            <p>Initial Monthly Payment: $${analysis.initial_monthly_payment}</p>
                            <p>Refinance Monthly Payment: $${analysis.refinance_monthly_payment}</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    
        reportsContent.innerHTML = html;

        // Add event listener for PDF download
        const downloadPdfBtn = document.getElementById('downloadPdfBtn');
        if (downloadPdfBtn) {
            downloadPdfBtn.addEventListener('click', () => {
                this.downloadPdf(analysis.id);
            });
        } else {
            console.error('Download PDF button not found');
        }

        // Show the Edit and Create New buttons
        const editBtn = document.getElementById('editAnalysisBtn');
        const createNewBtn = document.getElementById('createNewAnalysisBtn');
        
        if (editBtn && createNewBtn) {
            editBtn.style.display = 'inline-block';
            createNewBtn.style.display = 'inline-block';

            editBtn.addEventListener('click', () => this.editAnalysis(analysis.id));
            createNewBtn.addEventListener('click', () => window.location.href = '/analyses/create_analysis');
        }

        this.currentAnalysisId = analysis.id; // Store the current analysis ID
    },

    switchToReportsTab: function() {
        const reportsTab = document.querySelector('#reports-tab');
        const reportsContent = document.querySelector('#reports');
        const financialTab = document.querySelector('#financial-tab');
        const financialContent = document.querySelector('#financial');
        
        if (reportsTab && reportsContent && financialTab && financialContent) {
            financialTab.classList.remove('active');
            financialContent.classList.remove('show', 'active');
            reportsTab.classList.add('active');
            reportsContent.classList.add('show', 'active');
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
        console.log('Editing analysis with ID:', this.currentAnalysisId);

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
                        this.populateForm(data.analysis);
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
        if (typeof value === 'string') {
            // Remove dollar signs and commas
            return value.replace(/[$,]/g, '');
        }
        return value;
    },

    populateForm: function(analysis) {
        console.log('Populating form with analysis:', analysis);
        // Populate form fields with analysis data
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

        // Handle special cases like loans, if any
        if (analysis.loans && Array.isArray(analysis.loans)) {
            analysis.loans.forEach((loan, index) => {
                Object.keys(loan).forEach(loanKey => {
                    const field = document.getElementById(`loan_${loanKey}_${index + 1}`);
                    if (field) {
                        if (field.type === 'number') {
                            field.value = this.cleanNumericValue(loan[loanKey]);
                        } else {
                            field.value = loan[loanKey];
                        }
                        console.log(`Set loan ${index + 1} ${loanKey} to ${field.value}`);
                    }
                });
            });
        }
    },

    handleEditSubmit: function(event, analysisId) {
        event.preventDefault();
        console.log('Edit form submission started');
        console.log('Analysis ID:', analysisId);
        
        if (!analysisId) {
            console.error('No analysis ID provided for update');
            alert('Error: No analysis ID found. Cannot update.');
            return;
        }
    
        const form = event.target;
        const formData = new FormData(form);
        
        if (!this.validateForm(form)) {
            console.log('Form validation failed');
            return;
        }
    
        const analysisData = Object.fromEntries(formData.entries());
        analysisData.id = analysisId;  // Ensure the ID is included
    
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
        ['monthly_income', 'management_percentage', 'capex_percentage', 'repairs_percentage', 'vacancy_percentage',
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
                this.populateReportsTab(data.analysis);
                this.switchToReportsTab();
                this.showReportActions();
            } else {
                throw new Error(data.message || 'Unknown error occurred');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert(`An error occurred while updating the analysis: ${error.message || 'Please try again.'}`);
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
        fetch(`/analyses/generate_pdf/${encodeURIComponent(analysisId)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.blob();
            })
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = `${analysisId}_report.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while downloading the PDF. Please try again.');
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
            alert('Please fill out all required fields correctly.');
        }

        return isValid;
    }
};

document.addEventListener('DOMContentLoaded', function() {
    analysisModule.init();
});