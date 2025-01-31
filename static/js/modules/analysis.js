// PadSplit-specific expenses template
const padSplitExpensesHTML = `
    <div class="card mb-4">
        <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">PadSplit-Specific Expenses</h5>
        </div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-12 col-md-6">
                    <label for="padsplit_platform_percentage" class="form-label">PadSplit Platform (%)</label>
                    <div class="input-group">
                        <input type="number" class="form-control form-control-lg" id="padsplit_platform_percentage" 
                               name="padsplit_platform_percentage" value="12" min="0" max="100" 
                               step="0.5" required>
                        <span class="input-group-text">%</span>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="utilities" class="form-label">Utilities</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="utilities" name="utilities" 
                               placeholder="Monthly utility costs" required>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="internet" class="form-label">Internet</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="internet" name="internet" 
                               placeholder="Monthly Internet costs" required>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="cleaning" class="form-label">Cleaning Costs</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="cleaning" name="cleaning" 
                               placeholder="Monthly cleaning costs" required>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="pest_control" class="form-label">Pest Control</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="pest_control" name="pest_control" 
                               placeholder="Monthly pest control" required>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="landscaping" class="form-label">Landscaping</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="landscaping" name="landscaping" 
                               placeholder="Monthly landscaping" required>
                    </div>
                </div>
            </div>
        </div>
    </div>
`;

// Update the balloonPaymentHTML template
const balloonPaymentHTML = `
    <div class="card mb-4" id="balloon-payment-section">
        <div class="card-header bg-primary">
            <div class="d-flex justify-content-between align-items-center">
                <h5 class="mb-0 text-white">Balloon Payment</h5>
                <div class="form-check form-switch">
                    <input class="form-check-input" type="checkbox" id="has_balloon_payment" 
                           name="has_balloon_payment" role="switch">
                    <label class="form-check-label text-white fw-bold" for="has_balloon_payment">
                        Enable
                    </label>
                </div>
            </div>
        </div>
        <div class="card-body" id="balloon-payment-details" style="display: none;">
            <div class="row g-3">
                <div class="col-12 col-md-6">
                    <label for="balloon_due_date" class="form-label">Balloon Payment Due Date</label>
                    <input type="date" class="form-control form-control-lg" id="balloon_due_date" 
                           name="balloon_due_date">
                </div>
                <div class="col-12 col-md-6">
                    <label for="balloon_refinance_ltv_percentage" class="form-label">Refinance LTV (%)</label>
                    <div class="input-group">
                        <input type="number" class="form-control form-control-lg" id="balloon_refinance_ltv_percentage" 
                               name="balloon_refinance_ltv_percentage" step="0.01" min="0" max="100">
                        <span class="input-group-text">%</span>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="balloon_refinance_loan_amount" class="form-label">Refinance Loan Amount</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="balloon_refinance_loan_amount" 
                               name="balloon_refinance_loan_amount">
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="balloon_refinance_loan_interest_rate" class="form-label">Refinance Interest Rate (%)</label>
                    <div class="input-group">
                        <input type="number" class="form-control form-control-lg" id="balloon_refinance_loan_interest_rate" 
                               name="balloon_refinance_loan_interest_rate" step="0.025">
                        <span class="input-group-text">%</span>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="balloon_refinance_loan_term" class="form-label">Refinance Loan Term (months)</label>
                    <input type="number" class="form-control form-control-lg" id="balloon_refinance_loan_term" 
                           name="balloon_refinance_loan_term">
                </div>
                <div class="col-12 col-md-6">
                    <label for="balloon_refinance_loan_down_payment" class="form-label">Refinance Down Payment</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="balloon_refinance_loan_down_payment" 
                               name="balloon_refinance_loan_down_payment">
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="balloon_refinance_loan_closing_costs" class="form-label">Refinance Closing Costs</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="balloon_refinance_loan_closing_costs" 
                               name="balloon_refinance_loan_closing_costs">
                    </div>
                </div>
            </div>
        </div>
    </div>
`;

// Lease Option HTML
const getLeaseOptionHTML = () => `
    <!-- Property Details Card -->
    <div class="card mb-4">
        <div class="card-header">
            <h5 class="mb-0">Property Details</h5>
        </div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-12 col-md-4">
                    <label for="square_footage" class="form-label">Square Footage</label>
                    <div class="input-group">
                        <input type="number" class="form-control form-control-lg" id="square_footage" 
                            name="square_footage" placeholder="Property square footage">
                        <span class="input-group-text">sq ft</span>
                    </div>
                </div>
                <div class="col-12 col-md-4">
                    <label for="lot_size" class="form-label">Lot Size</label>
                    <div class="input-group">
                        <input type="number" class="form-control form-control-lg" id="lot_size" 
                            name="lot_size" placeholder="Lot size">
                        <span class="input-group-text">sq ft</span>
                    </div>
                </div>
                <div class="col-12 col-md-4">
                    <label for="year_built" class="form-label">Year Built</label>
                    <input type="number" class="form-control form-control-lg" id="year_built" 
                        name="year_built" placeholder="Construction year">
                </div>
                <div class="col-12 col-md-6">
                    <label for="bedrooms" class="form-label">Bedrooms</label>
                    <input type="number" class="form-control form-control-lg" id="bedrooms" 
                        name="bedrooms" min="0" step="1" placeholder="Number of bedrooms">
                </div>
                <div class="col-12 col-md-6">
                    <label for="bathrooms" class="form-label">Bathrooms</label>
                    <input type="number" class="form-control form-control-lg" id="bathrooms" 
                        name="bathrooms" min="0" step="0.5" placeholder="Number of bathrooms">
                </div>
            </div>
        </div>
    </div>

    <!-- Purchase Details Card -->
    <div class="card mb-4">
        <div class="card-header">
            <h5 class="mb-0">Purchase Details</h5>
        </div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-12 col-md-6">
                    <label for="purchase_price" class="form-label">Purchase Price</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" 
                               class="form-control form-control-lg" 
                               id="purchase_price" 
                               name="purchase_price" 
                               placeholder="Current market value/owner's purchase price" 
                               required
                               data-bs-toggle="tooltip"
                               data-bs-placement="top"
                               title="The current market value or price the owner paid for the property">
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="strike_price" class="form-label">Strike Price</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="strike_price" 
                               name="strike_price" placeholder="Agreed future purchase price" required>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="option_consideration_fee" class="form-label">Option Fee</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="option_consideration_fee" 
                               name="option_consideration_fee" placeholder="Non-refundable option fee" required>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="option_term_months" class="form-label">Option Term</label>
                    <div class="input-group">
                        <input type="number" class="form-control form-control-lg" id="option_term_months" 
                               name="option_term_months" placeholder="Option period duration" required>
                        <span class="input-group-text">months</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Add Financing Section -->
    <div class="card mb-4">
        <div class="card-header">
            <h5 class="mb-0">Financing</h5>
        </div>
        <div class="card-body" id="financing-section">
            <div id="loans-container">
                <!-- Existing loans will be inserted here -->
            </div>
            <div class="mt-3">
                <button type="button" class="btn btn-primary" id="add-loan-btn">
                    <i class="bi bi-plus-circle me-2"></i>Add Loan
                </button>
            </div>
        </div>
    </div>

    <!-- Rental Income Card -->
    <div class="card mb-4">
        <div class="card-header">
            <h5 class="mb-0">Rental Income</h5>
        </div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-12 col-md-6">
                    <label for="monthly_rent" class="form-label">Monthly Rent</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="monthly_rent" 
                               name="monthly_rent" placeholder="Monthly rent amount" required>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="monthly_rent_credit_percentage" class="form-label">Rent Credit</label>
                    <div class="input-group">
                        <input type="number" class="form-control form-control-lg" id="monthly_rent_credit_percentage" 
                               name="monthly_rent_credit_percentage" placeholder="Percentage of rent credited" required>
                        <span class="input-group-text">%</span>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="rent_credit_cap" class="form-label">Rent Credit Cap</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="rent_credit_cap" 
                               name="rent_credit_cap" placeholder="Maximum total rent credit" required>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Operating Expenses Card -->
    <div class="card mb-4">
        <div class="card-header">
            <h5 class="mb-0">Operating Expenses</h5>
        </div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-12 col-md-6">
                    <label for="property_taxes" class="form-label">Monthly Property Taxes</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="property_taxes" 
                               name="property_taxes" placeholder="Monthly taxes" required>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="insurance" class="form-label">Monthly Insurance</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="insurance" 
                               name="insurance" placeholder="Monthly insurance" required>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="management_fee_percentage" class="form-label">Management Fee</label>
                    <div class="input-group">
                        <input type="number" class="form-control form-control-lg" id="management_fee_percentage" 
                               name="management_fee_percentage" value="8" min="0" max="100" step="0.5" required>
                        <span class="input-group-text">%</span>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="capex_percentage" class="form-label">CapEx</label>
                    <div class="input-group">
                        <input type="number" class="form-control form-control-lg" id="capex_percentage" 
                               name="capex_percentage" value="2" min="0" max="100" step="1" required>
                        <span class="input-group-text">%</span>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="repairs_percentage" class="form-label">Repairs</label>
                    <div class="input-group">
                        <input type="number" class="form-control form-control-lg" id="repairs_percentage" 
                               name="repairs_percentage" value="2" min="0" max="100" step="1" required>
                        <span class="input-group-text">%</span>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="vacancy_percentage" class="form-label">Vacancy Rate</label>
                    <div class="input-group">
                        <input type="number" class="form-control form-control-lg" id="vacancy_percentage" 
                               name="vacancy_percentage" value="4" min="0" max="100" step="1" required>
                        <span class="input-group-text">%</span>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="hoa_coa_coop" class="form-label">HOA/COA/COOP</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="hoa_coa_coop" 
                               name="hoa_coa_coop" placeholder="Monthly association fees" required>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Notes Card -->
    <div class="card mb-4">
        <div class="card-header">
            <h5 class="mb-0">Notes</h5>
        </div>
        <div class="card-body">
            <div class="row">
                <div class="col-12">
                    <textarea class="form-control" id="notes" name="notes" rows="4" 
                              maxlength="1000" placeholder="Enter any notes about this analysis (max 1,000 characters)"></textarea>
                    <div class="form-text text-end mt-2">
                        <span id="notes-counter">0</span>/1000 characters
                    </div>
                </div>
            </div>
        </div>
    </div>
`;

// Long-term rental template
const getLongTermRentalHTML = () => `
    <div class="card mb-4">
        <div class="card mb-4">
            <div class="card-header">
                <h5 class="mb-0">Property Details</h5>
            </div>
            <div class="card-body">
                <div class="row g-3">
                    <div class="col-12 col-md-4">
                        <label for="square_footage" class="form-label">Square Footage</label>
                        <div class="input-group">
                            <input type="number" class="form-control form-control-lg" id="square_footage" 
                                name="square_footage" placeholder="Property square footage">
                            <span class="input-group-text">sq ft</span>
                        </div>
                    </div>
                    <div class="col-12 col-md-4">
                        <label for="lot_size" class="form-label">Lot Size</label>
                        <div class="input-group">
                            <input type="number" class="form-control form-control-lg" id="lot_size" 
                                name="lot_size" placeholder="Lot size">
                            <span class="input-group-text">sq ft</span>
                        </div>
                    </div>
                    <div class="col-12 col-md-4">
                        <label for="year_built" class="form-label">Year Built</label>
                        <input type="number" class="form-control form-control-lg" id="year_built" 
                            name="year_built" placeholder="Construction year">
                    </div>
                    <div class="col-12 col-md-6">
                        <label for="bedrooms" class="form-label">Bedrooms</label>
                        <input type="number" class="form-control form-control-lg" id="bedrooms" 
                            name="bedrooms" min="0" step="1" placeholder="Number of bedrooms">
                    </div>
                    <div class="col-12 col-md-6">
                        <label for="bathrooms" class="form-label">Bathrooms</label>
                        <input type="number" class="form-control form-control-lg" id="bathrooms" 
                            name="bathrooms" min="0" step="0.5" placeholder="Number of bathrooms">
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="card mb-4">
        <div class="card-header">
            <h5 class="mb-0">Purchase Details</h5>
        </div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-12 col-md-6">
                    <label for="purchase_price" class="form-label">Purchase Price</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="purchase_price" 
                               name="purchase_price" placeholder="Sales price" required>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="after_repair_value" class="form-label">After Repair Value</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="after_repair_value" 
                               name="after_repair_value" placeholder="Post-renovation value" required>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="renovation_costs" class="form-label">Renovation Costs</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="renovation_costs" 
                               name="renovation_costs" placeholder="Expected renovation costs" required>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="renovation_duration" class="form-label">Renovation Duration</label>
                    <div class="input-group">
                        <input type="number" class="form-control form-control-lg" id="renovation_duration" 
                               name="renovation_duration" placeholder="Duration" required>
                        <span class="input-group-text">months</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="card mb-4">
        <div class="card-header">
            <h5 class="mb-0">Rental Income</h5>
        </div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-12 col-md-6">
                    <label for="monthly_rent" class="form-label">Monthly Rent</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="monthly_rent" 
                               name="monthly_rent" placeholder="Expected monthly rent" required>
                    </div>
                </div>
            </div>
        </div>
    </div>

        <!-- Add Financing Section -->
    <div class="card mb-4">
        <div class="card-header">
            <h5 class="mb-0">Financing</h5>
        </div>
        <div class="card-body" id="financing-section">
            <div id="loans-container">
                <!-- Existing loans will be inserted here -->
            </div>
            <div class="mt-3">
                <button type="button" class="btn btn-primary" id="add-loan-btn">
                    <i class="bi bi-plus-circle me-2"></i>Add Loan
                </button>
            </div>
        </div>
    </div>

    <!-- Add Balloon Payment Section -->
    ${balloonPaymentHTML}

    <div class="card mb-4">
        <div class="card-header">
            <h5 class="mb-0">Operating Expenses</h5>
        </div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-12 col-md-6">
                    <label for="property_taxes" class="form-label">Monthly Property Taxes</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="property_taxes" 
                               name="property_taxes" placeholder="Monthly taxes" required>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="insurance" class="form-label">Monthly Insurance</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="insurance" 
                               name="insurance" placeholder="Monthly insurance" required>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="management_fee_percentage" class="form-label">Management Fee</label>
                    <div class="input-group">
                        <input type="number" class="form-control form-control-lg" id="management_fee_percentage" 
                               name="management_fee_percentage" value="8" min="0" max="100" step="0.5" required>
                        <span class="input-group-text">%</span>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="capex_percentage" class="form-label">CapEx</label>
                    <div class="input-group">
                        <input type="number" class="form-control form-control-lg" id="capex_percentage" 
                               name="capex_percentage" value="2" min="0" max="100" step="1" required>
                        <span class="input-group-text">%</span>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="repairs_percentage" class="form-label">Repairs</label>
                    <div class="input-group">
                        <input type="number" class="form-control form-control-lg" id="repairs_percentage" 
                               name="repairs_percentage" value="2" min="0" max="100" step="1" required>
                        <span class="input-group-text">%</span>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="vacancy_percentage" class="form-label">Vacancy Rate</label>
                    <div class="input-group">
                        <input type="number" class="form-control form-control-lg" id="vacancy_percentage" 
                               name="vacancy_percentage" value="4" min="0" max="100" step="1" required>
                        <span class="input-group-text">%</span>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="hoa_coa_coop" class="form-label">HOA/COA/COOP</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="hoa_coa_coop" 
                               name="hoa_coa_coop" placeholder="Monthly association fees" required>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="card mb-4">
        <div class="card-header">
            <h5 class="mb-0">Notes</h5>
        </div>
        <div class="card-body">
            <div class="row">
                <div class="col-12">
                    <textarea class="form-control" id="notes" name="notes" rows="4" 
                              maxlength="1000" placeholder="Enter any notes about this analysis (max 1,000 characters)"></textarea>
                    <div class="form-text text-end mt-2">
                        <span id="notes-counter">0</span>/1000 characters
                    </div>
                </div>
            </div>
        </div>
    </div>
`;

// Loan template function - used by loan handlers
const getLoanFieldsHTML = (loanNumber) => `
    <div class="loan-section mb-4">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">Loan ${loanNumber}</h5>
                <button type="button" class="btn btn-danger btn-sm remove-loan-btn">
                    <i class="bi bi-trash me-2"></i>Remove
                </button>
            </div>
            <div class="card-body">
                <div class="row g-3">
                    <div class="col-12 col-md-6">
                        <label for="loan${loanNumber}_loan_name" class="form-label">Loan Name</label>
                        <input type="text" class="form-control form-control-lg" id="loan${loanNumber}_loan_name" 
                               name="loan${loanNumber}_loan_name" placeholder="Enter loan name" required>
                    </div>
                    <div class="col-12 col-md-6">
                        <label for="loan${loanNumber}_loan_amount" class="form-label">Loan Amount</label>
                        <div class="input-group">
                            <span class="input-group-text">$</span>
                            <input type="number" class="form-control form-control-lg" id="loan${loanNumber}_loan_amount" 
                                   name="loan${loanNumber}_loan_amount" placeholder="Enter loan amount" required>
                        </div>
                    </div>
                    <div class="col-12 col-md-6">
                        <label for="loan${loanNumber}_loan_down_payment" class="form-label">Down Payment</label>
                        <div class="input-group">
                            <span class="input-group-text">$</span>
                            <input type="number" class="form-control form-control-lg" id="loan${loanNumber}_loan_down_payment" 
                                   name="loan${loanNumber}_loan_down_payment" placeholder="Enter down payment" required>
                        </div>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label for="loan${loanNumber}_loan_interest_rate" class="form-label">Interest Rate (%)</label>
                        <input type="number" class="form-control" id="loan${loanNumber}_loan_interest_rate" 
                            name="loan${loanNumber}_loan_interest_rate" step="0.025" min="0" max="100" 
                            placeholder="Enter interest rate" required>
                        <div class="form-check mt-2">
                            <input class="form-check-input" type="checkbox" id="loan${loanNumber}_interest_only" 
                                name="loan${loanNumber}_interest_only">
                            <label class="form-check-label" for="loan${loanNumber}_interest_only">
                                Interest Only
                            </label>
                        </div>
                    </div>
                    <div class="col-12 col-md-6">
                        <label for="loan${loanNumber}_loan_term" class="form-label">Loan Term (months)</label>
                        <input type="number" class="form-control form-control-lg" id="loan${loanNumber}_loan_term" 
                               name="loan${loanNumber}_loan_term" min="1" placeholder="Enter loan term" required>
                    </div>
                    <div class="col-12 col-md-6">
                        <label for="loan${loanNumber}_loan_closing_costs" class="form-label">Closing Costs</label>
                        <div class="input-group">
                            <span class="input-group-text">$</span>
                            <input type="number" class="form-control form-control-lg" id="loan${loanNumber}_loan_closing_costs" 
                                   name="loan${loanNumber}_loan_closing_costs" placeholder="Enter closing costs" required>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
`;

// BRRRR template
const getBRRRRHTML = () => `
    <div class="card mb-4">
        <div class="card-header">
            <h5 class="mb-0">Property Details</h5>
        </div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-12 col-md-4">
                    <label for="square_footage" class="form-label">Square Footage</label>
                    <div class="input-group">
                        <input type="number" class="form-control form-control-lg" id="square_footage" 
                            name="square_footage" placeholder="Property square footage">
                        <span class="input-group-text">sq ft</span>
                    </div>
                </div>
                <div class="col-12 col-md-4">
                    <label for="lot_size" class="form-label">Lot Size</label>
                    <div class="input-group">
                        <input type="number" class="form-control form-control-lg" id="lot_size" 
                            name="lot_size" placeholder="Lot size">
                        <span class="input-group-text">sq ft</span>
                    </div>
                </div>
                <div class="col-12 col-md-4">
                    <label for="year_built" class="form-label">Year Built</label>
                    <input type="number" class="form-control form-control-lg" id="year_built" 
                        name="year_built" placeholder="Construction year">
                </div>
                <div class="col-12 col-md-6">
                    <label for="bedrooms" class="form-label">Bedrooms</label>
                    <input type="number" class="form-control form-control-lg" id="bedrooms" 
                        name="bedrooms" min="0" step="1" placeholder="Number of bedrooms">
                </div>
                <div class="col-12 col-md-6">
                    <label for="bathrooms" class="form-label">Bathrooms</label>
                    <input type="number" class="form-control form-control-lg" id="bathrooms" 
                        name="bathrooms" min="0" step="0.5" placeholder="Number of bathrooms">
                </div>
            </div>
        </div>
    </div>

    <div class="card mb-4">
        <div class="card-header">
            <h5 class="mb-0">Initial Financing</h5>
        </div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-12 col-md-6">
                    <label for="initial_loan_amount" class="form-label">Initial Loan Amount</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="initial_loan_amount" 
                               name="initial_loan_amount" placeholder="Purchase loan amount" required>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="initial_loan_down_payment" class="form-label">Initial Down Payment</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="initial_loan_down_payment" 
                               name="initial_loan_down_payment" placeholder="Down payment amount" required>
                    </div>
                </div>
                <div class="col-md-6 mb-3">
                    <label for="initial_loan_interest_rate" class="form-label">Initial Interest Rate (%)</label>
                    <input type="number" class="form-control" id="initial_loan_interest_rate" 
                           name="initial_loan_interest_rate" placeholder="Interest rate" step="0.025" required>
                    <div class="form-check mt-2">
                        <input class="form-check-input" type="checkbox" id="initial_interest_only" 
                               name="initial_interest_only">
                        <label class="form-check-label" for="initial_interest_only">
                            Interest Only
                        </label>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="initial_loan_term" class="form-label">Initial Loan Term</label>
                    <div class="input-group">
                        <input type="number" class="form-control form-control-lg" id="initial_loan_term" 
                               name="initial_loan_term" placeholder="Loan duration" required>
                        <span class="input-group-text">months</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="card mb-4">
        <div class="card-header">
            <h5 class="mb-0">Refinance Details</h5>
        </div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-12 col-md-6">
                    <label for="refinance_loan_amount" class="form-label">Refinance Amount</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="refinance_loan_amount" 
                               name="refinance_loan_amount" placeholder="Expected refinance amount" required>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="refinance_loan_interest_rate" class="form-label">Refinance Rate</label>
                    <div class="input-group">
                        <input type="number" class="form-control form-control-lg" id="refinance_loan_interest_rate" 
                               name="refinance_loan_interest_rate" step="0.025" placeholder="Interest rate" required>
                        <span class="input-group-text">%</span>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="refinance_loan_term" class="form-label">Refinance Term</label>
                    <div class="input-group">
                        <input type="number" class="form-control form-control-lg" id="refinance_loan_term" 
                               name="refinance_loan_term" placeholder="Loan duration" required>
                        <span class="input-group-text">months</span>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="refinance_loan_closing_costs" class="form-label">Refinance Closing Costs</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="refinance_loan_closing_costs" 
                               name="refinance_loan_closing_costs" placeholder="Expected closing costs" required>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="card mb-4">
        <div class="card-header">
            <h5 class="mb-0">Operating Expenses</h5>
        </div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-12 col-md-6">
                    <label for="property_taxes" class="form-label">Monthly Property Taxes</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="property_taxes" 
                               name="property_taxes" placeholder="Monthly taxes" required>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="insurance" class="form-label">Monthly Insurance</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="insurance" 
                               name="insurance" placeholder="Monthly insurance" required>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="management_fee_percentage" class="form-label">Management Fee</label>
                    <div class="input-group">
                        <input type="number" class="form-control form-control-lg" id="management_fee_percentage" 
                               name="management_fee_percentage" value="8" min="0" max="100" step="0.5" required>
                        <span class="input-group-text">%</span>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="capex_percentage" class="form-label">CapEx</label>
                    <div class="input-group">
                        <input type="number" class="form-control form-control-lg" id="capex_percentage" 
                               name="capex_percentage" value="2" min="0" max="100" step="1" required>
                        <span class="input-group-text">%</span>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="repairs_percentage" class="form-label">Repairs</label>
                    <div class="input-group">
                        <input type="number" class="form-control form-control-lg" id="repairs_percentage" 
                               name="repairs_percentage" value="2" min="0" max="100" step="1" required>
                        <span class="input-group-text">%</span>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="vacancy_percentage" class="form-label">Vacancy Rate</label>
                    <div class="input-group">
                        <input type="number" class="form-control form-control-lg" id="vacancy_percentage" 
                               name="vacancy_percentage" value="4" min="0" max="100" step="1" required>
                        <span class="input-group-text">%</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="card mb-4">
        <div class="card-header">
            <h5 class="mb-0">Notes</h5>
        </div>
        <div class="card-body">
            <div class="row">
                <div class="col-12">
                    <textarea class="form-control" id="notes" name="notes" rows="4" 
                              maxlength="1000" placeholder="Enter any notes about this analysis (max 1,000 characters)"></textarea>
                    <div class="form-text text-end mt-2">
                        <span id="notes-counter">0</span>/1000 characters
                    </div>
                </div>
            </div>
        </div>
    </div>
`;

'use strict';

window.analysisModule = {
    initialAnalysisType: null,
    currentAnalysisId: null,
    isSubmitting: false,
    typeChangeInProgress: false,

    // Add style definitions as module properties
    tooltipStyles: `
        @media (max-width: 767.98px) {
            .tooltip {
                font-size: 0.75rem;
            }
            .popover {
                max-width: 90%;
                font-size: 0.875rem;
            }
            .popover-header {
                padding: 0.5rem 0.75rem;
                font-size: 0.875rem;
            }
            .popover-body {
                padding: 0.5rem 0.75rem;
                font-size: 0.875rem;
            }
            .tooltip-inner {
                max-width: 200px;
                padding: 0.25rem 0.5rem;
            }
        }
    `,

    mobileStyles: `
        .keyboard-visible {
            padding-bottom: 40vh;
        }

        @media (max-width: 767.98px) {
            .form-group {
                margin-bottom: 1.5rem;
            }

            .btn-group {
                flex-direction: column;
            }

            .btn-group .btn {
                margin-bottom: 0.5rem;
            }

            .dropdown-menu {
                position: fixed !important;
                top: auto !important;
                left: 0 !important;
                right: 0 !important;
                bottom: 0 !important;
                margin: 0;
                border-radius: 1rem 1rem 0 0;
                max-height: 50vh;
                overflow-y: auto;
            }

            .modal {
                padding: 0 !important;
            }

            .modal-dialog {
                margin: 0;
                max-width: none;
                min-height: 100vh;
            }

            .modal-content {
                border-radius: 0;
                min-height: 100vh;
            }
        }
    `,

    notesStyles: `
        @media (max-width: 767.98px) {
            .notes-content {
                font-size: 0.875rem;
                line-height: 1.5;
                word-break: break-word;
            }
            
            .notes-content br {
                display: block;
                margin: 0.5rem 0;
                content: "";
            }
        }
    `,

    // Make sure init is directly on the module object
    async init() {
        console.log('Analysis module initializing');
        try {
            // Inject styles first
            this.injectStyles();
            
            // Initialize mobile interactions
            this.initializeMobileInteractions();
            
            // Initialize viewport change handler
            this.initViewportHandler();
            
            // Initialize core functionality
            this.initToastr();
            this.initButtonHandlers();
            
            const analysisForm = document.querySelector('#analysisForm');
            console.log('Found analysis form:', !!analysisForm);
            
            if (analysisForm) {
                console.log('Initializing form functionality');
                this.initFormResponsiveness();
                
                const urlParams = new URLSearchParams(window.location.search);
                const analysisId = urlParams.get('analysis_id');
                console.log('Analysis ID from URL:', analysisId);
                
                if (analysisId) {
                    console.log('Loading existing analysis:', analysisId);
                    this.currentAnalysisId = analysisId;
                    analysisForm.setAttribute('data-analysis-id', analysisId);
                    analysisForm.addEventListener('submit', (event) => {
                        this.handleEditSubmit(event, analysisId);
                    });
                    await this.loadAnalysisData(analysisId);
                } else {
                    console.log('Creating new analysis');
                    const analysisDataElement = document.getElementById('analysis-data');
                    if (analysisDataElement) {
                        try {
                            const analysisData = JSON.parse(analysisDataElement.textContent);
                            this.populateFormFields(analysisData);
                        } catch (error) {
                            console.error('Error parsing analysis data:', error);
                        }
                    } else {
                        console.log('Initializing balloon payment handlers');
                        this.initBalloonPaymentHandlers();
                    }
                    
                    analysisForm.addEventListener('submit', (event) => {
                        this.handleSubmit(event);
                    });
                }
    
                console.log('Initializing analysis type handler');
                this.initAnalysisTypeHandler();
                console.log('Initializing address autocomplete');
                this.initAddressAutocomplete();
                console.log('Initializing tab handling');
                this.initTabHandling();
                console.log('Form initialization complete');
            }
    
            console.log('Analysis module initialized successfully');
            return true;
        } catch (error) {
            console.error('Error initializing analysis module:', error);
            throw error;
        }
    },

    initAnalysisTypeHandler() {
        console.log('Starting initAnalysisTypeHandler');
        const analysisType = document.getElementById('analysis_type');
        const financialTab = document.getElementById('financial');
        console.log('Found elements:', { 
            analysisType: !!analysisType, 
            analysisTypeValue: analysisType?.value,
            financialTab: !!financialTab 
        });
        
        if (analysisType && financialTab) {
            // Remove any existing event listeners by cloning
            const newAnalysisType = analysisType.cloneNode(true);
            analysisType.parentNode.replaceChild(newAnalysisType, analysisType);
            
            // Get the analysis ID from URL if it exists
            const urlParams = new URLSearchParams(window.location.search);
            const analysisId = urlParams.get('analysis_id');
            console.log('AnalysisId in type handler:', analysisId);
            
            // Store initial value
            this.initialAnalysisType = analysisId ? null : newAnalysisType.value;
            console.log('Initial analysis type:', this.initialAnalysisType);
            
            // Load initial template if not editing existing analysis
            if (!analysisId) {
                console.log('Should load initial template for:', this.initialAnalysisType);
                console.log('loadTemplateForType exists:', typeof this.loadTemplateForType === 'function');
                this.loadTemplateForType(this.initialAnalysisType, financialTab);
            }
                
            // Set up event listener for changes
            newAnalysisType.addEventListener('change', async (e) => {
                console.log('Analysis type changed to:', e.target.value);
                // Prevent multiple concurrent changes
                if (this.typeChangeInProgress) {
                    console.log('Type change already in progress');
                    return;
                }
        
                const newType = e.target.value;
                console.log('Processing change to type:', newType);
                
                // Skip if initial type hasn't been set yet or if type hasn't actually changed
                if (!this.initialAnalysisType || newType === this.initialAnalysisType) {
                    console.log('Skipping - no initial type or no change');
                    return;
                }
                
                // If we're in create mode, just update the fields
                if (!this.currentAnalysisId) {
                    console.log('Create mode - updating template for type:', newType);
                    this.loadTemplateForType(newType, financialTab);
                    this.initialAnalysisType = newType;
                    return;
                }
                
                try {
                    this.typeChangeInProgress = true;
                    const confirmed = await this.confirmTypeChange(newType);
                    
                    if (!confirmed) {
                        e.target.value = this.initialAnalysisType;
                        return;
                    }
                    
                    await this.handleTypeChange(newType);
                    
                } catch (error) {
                    console.error('Error:', error);
                    toastr.error(error.message);
                    e.target.value = this.initialAnalysisType;
                } finally {
                    this.typeChangeInProgress = false;
                }
            });
        }
    },

    loadTemplateForType(type, container) {
        console.log('loadTemplateForType called with:', {
            type,
            containerExists: !!container,
            typeIsLeaseOption: type === 'Lease Option',
            getLeaseOptionExists: typeof getLeaseOptionHTML === 'function',
            getLongTermRentalExists: typeof getLongTermRentalHTML === 'function',
            getBRRRRExists: typeof getBRRRRHTML === 'function'
        });
        
        if (!container) {
            console.error('No container provided to loadTemplateForType');
            return;
        }
        
        try {
            container.innerHTML = '';
            
            if (type === 'Lease Option') {
                console.log('Loading Lease Option template');
                if (typeof getLeaseOptionHTML !== 'function') {
                    console.error('getLeaseOptionHTML is not a function!');
                    console.log('Value:', getLeaseOptionHTML);
                    return;
                }
                container.innerHTML = getLeaseOptionHTML();
            } else if (type === 'BRRRR' || type === 'PadSplit BRRRR') {
                console.log('Loading BRRRR template');
                container.innerHTML = getBRRRRHTML();
            } else {
                console.log('Loading LTR template');
                container.innerHTML = getLongTermRentalHTML();
            }
    
            if (type.includes('PadSplit')) {
                console.log('Adding PadSplit expenses');
                container.insertAdjacentHTML('beforeend', padSplitExpensesHTML);
            }
    
            // Initialize handlers
            this.initLoanHandlers();
            if (type.includes('BRRRR')) {
                this.initRefinanceCalculations();
            }
            this.initNotesCounter();
            
            console.log('Template loaded successfully. Container HTML length:', container.innerHTML.length);
        } catch (error) {
            console.error('Error in loadTemplateForType:', error);
            throw error;  // Re-throw to see where it's called from
        }
    },

    // Add style injection method
    injectStyles() {
        const styles = [
            { content: this.tooltipStyles, id: 'analysis-tooltip-styles' },
            { content: this.mobileStyles, id: 'analysis-mobile-styles' },
            { content: this.notesStyles, id: 'analysis-notes-styles' }
        ];

        styles.forEach(style => {
            let styleElement = document.getElementById(style.id);
            if (!styleElement) {
                styleElement = document.createElement('style');
                styleElement.id = style.id;
                styleElement.textContent = style.content;
                document.head.appendChild(styleElement);
            }
        });
    },

    hasBalloonData(analysis) {
        return analysis.has_balloon_payment || (
            analysis.balloon_refinance_loan_amount > 0 && 
            analysis.balloon_due_date && 
            analysis.balloon_refinance_ltv_percentage > 0
        );
    },

    // Helper function to create notes section
    createNotesSection(notes) {
        if (!notes) return '';
    
        return `
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">Notes</h5>
                </div>
                <div class="card-body">
                    <div class="notes-content">
                        ${notes.replace(/\n/g, '<br>')}
                    </div>
                </div>
            </div>
        `;
    },
    
    // Move helper functions into the module
    formatDisplayValue(value, type = 'money') {
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

    toRawNumber(value) {
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

    // Add mobile interaction methods
    initializeMobileInteractions() {
        this.initAccordionScrolling();
        this.initTouchFeedback();
        this.initResponsiveTables();
        this.initMobileTooltips();
    },

    initAccordionScrolling() {
        const accordions = document.querySelectorAll('.accordion');
        accordions.forEach(accordion => {
            accordion.addEventListener('shown.bs.collapse', (e) => {
                const targetElement = e.target;
                const offset = targetElement.getBoundingClientRect().top + window.pageYOffset - 80;
                window.scrollTo({
                    top: offset,
                    behavior: 'smooth'
                });
            });
        });
    },

    initTouchFeedback() {
        const interactiveElements = document.querySelectorAll(
            '.list-group-item, .accordion-button, .btn'
        );
        
        interactiveElements.forEach(element => {
            element.addEventListener('touchstart', function() {
                this.style.backgroundColor = 'rgba(0,0,0,0.05)';
            });
            
            element.addEventListener('touchend', function() {
                this.style.backgroundColor = '';
            });
        });
    },

    initResponsiveTables() {
        const tables = document.querySelectorAll('.table:not(.responsive-handled)');
        tables.forEach(table => {
            if (!table.parentElement.classList.contains('table-responsive')) {
                const wrapper = document.createElement('div');
                wrapper.className = 'table-responsive';
                table.parentNode.insertBefore(wrapper, table);
                wrapper.appendChild(table);
                table.classList.add('responsive-handled');
            }
        });
    },

    // New method for mobile-specific event handlers
    initMobileSpecificHandlers() {
        // Handle form submission on mobile
        this.initMobileFormSubmission();
        
        // Handle mobile scroll behavior
        this.initMobileScrolling();
        
        // Initialize mobile-friendly tooltips
        this.initMobileTooltips();
        
        // Handle mobile keyboard adjustments
        this.initMobileKeyboardHandling();
    },

    // Optimize form submission for mobile
    initMobileFormSubmission() {
        const form = document.getElementById('analysisForm');
        if (form) {
            // Prevent double submission on mobile
            let isSubmitting = false;
            
            form.addEventListener('submit', (e) => {
                if (isSubmitting) {
                    e.preventDefault();
                    return;
                }
                
                isSubmitting = true;
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.disabled = true;
                }
                
                // Reset submission state after delay
                setTimeout(() => {
                    isSubmitting = false;
                    if (submitBtn) {
                        submitBtn.disabled = false;
                    }
                }, 2000);
            });
        }
    },

    // Handle mobile scrolling behavior
    initMobileScrolling() {
        // Smooth scrolling for mobile
        const contentArea = document.querySelector('.content-area');
        if (contentArea) {
            contentArea.style.overscrollBehavior = 'contain';
            contentArea.classList.add('touch-scroll');
        }

        // Handle fixed position elements when virtual keyboard is visible
        const inputs = document.querySelectorAll('input, textarea');
        inputs.forEach(input => {
            input.addEventListener('focus', () => {
                if (window.innerWidth < 768) {
                    document.body.classList.add('keyboard-visible');
                }
            });
            
            input.addEventListener('blur', () => {
                document.body.classList.remove('keyboard-visible');
            });
        });
    },

    initMobileTooltips() {
        const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltips.forEach(tooltip => {
            const instance = bootstrap.Tooltip.getInstance(tooltip);
            if (instance) {
                instance.dispose();
            }
            new bootstrap.Tooltip(tooltip, {
                trigger: window.innerWidth < 768 ? 'click' : 'hover',
                placement: window.innerWidth < 768 ? 'bottom' : 'auto'
            });
        });
    },

    // Handle mobile keyboard behavior
    initMobileKeyboardHandling() {
        // Detect virtual keyboard
        let originalHeight = window.innerHeight;
        
        window.addEventListener('resize', () => {
            if (window.innerWidth < 768) {
                const heightDiff = originalHeight - window.innerHeight;
                if (heightDiff > 150) {
                    // Keyboard is likely visible
                    document.body.classList.add('keyboard-visible');
                } else {
                    document.body.classList.remove('keyboard-visible');
                }
            }
        });

        // Improve input behavior on mobile
        const numericInputs = document.querySelectorAll('input[type="number"]');
        numericInputs.forEach(input => {
            input.addEventListener('focus', function() {
                if (window.innerWidth < 768) {
                    this.type = 'tel';  // Better numeric keyboard on mobile
                }
            });
            
            input.addEventListener('blur', function() {
                this.type = 'number';
            });
        });
    },

    // Enhanced form responsiveness
    initFormResponsiveness() {
        // Handle form layout on mobile
        this.adjustFormLayout();
        
        // Handle form validation display
        this.initMobileValidation();
        
        // Initialize mobile-friendly dropdowns
        this.initMobileDropdowns();
    },

    // Add viewport change handler
    initViewportHandler() {
        window.addEventListener('resize', _.debounce(() => {
            this.initializeMobileInteractions();
        }, 250));
    },

    // Adjust form layout for mobile
    adjustFormLayout() {
        if (window.innerWidth < 768) {
            // Stack form elements vertically on mobile
            const formGroups = document.querySelectorAll('.form-group');
            formGroups.forEach(group => {
                group.classList.add('mb-3');
            });

            // Adjust button groups for mobile
            const buttonGroups = document.querySelectorAll('.btn-group');
            buttonGroups.forEach(group => {
                group.classList.add('d-flex', 'flex-column');
            });
        }
    },

    // Mobile-friendly form validation
    initMobileValidation() {
        const form = document.getElementById('analysisForm');
        if (form) {
            // Show validation messages immediately on mobile
            form.addEventListener('input', (e) => {
                if (window.innerWidth < 768) {
                    const input = e.target;
                    if (input.checkValidity()) {
                        input.classList.remove('is-invalid');
                        input.classList.add('is-valid');
                    } else {
                        input.classList.remove('is-valid');
                        input.classList.add('is-invalid');
                    }
                }
            });
        }
    },

    // Initialize mobile-friendly dropdowns
    initMobileDropdowns() {
        const dropdowns = document.querySelectorAll('.dropdown-toggle');
        dropdowns.forEach(dropdown => {
            new bootstrap.Dropdown(dropdown, {
                display: 'static'  // Prevent dropdown from being cut off on mobile
            });
        });
    },

    clearBalloonPaymentFields() {
        const fields = [
            'balloon_due_date',
            'balloon_refinance_ltv_percentage',
            'balloon_refinance_loan_amount',
            'balloon_refinance_loan_interest_rate',
            'balloon_refinance_loan_term',
            'balloon_refinance_loan_down_payment',
            'balloon_refinance_loan_closing_costs'
        ];
        
        fields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.value = '';
                field.required = false;
            }
        });
    },

    initBalloonPaymentHandlers(skipToggleInit = false) {
        console.log('Initializing balloon payment handlers...');
        
        const balloonToggle = document.getElementById('has_balloon_payment');
        const balloonDetails = document.getElementById('balloon-payment-details');
        const analysisType = document.getElementById('analysis_type')?.value;
        
        // Only proceed for LTR analyses
        if (!analysisType?.includes('LTR')) {
            console.log('Balloon payments not applicable for', analysisType);
            return;
        }
    
        // If elements don't exist and this is an LTR analysis, elements might still be loading
        if (!balloonToggle || !balloonDetails) {
            if (!skipToggleInit) {
                console.log('Balloon payment elements not found - will retry in 100ms');
                setTimeout(() => this.initBalloonPaymentHandlers(true), 100);
            }
            return;
        }
    
        // Clear any existing balloon-related fields if balloon payment is not enabled
        if (!balloonToggle.checked) {
            this.clearBalloonPaymentFields();
        }
    
        console.log('Setting up balloon toggle event listener');
    
        console.log('Setting up balloon toggle event listener');
        // Add event listener to toggle
        balloonToggle.addEventListener('change', (e) => {
            console.log('Balloon toggle changed:', e.target.checked);
            
            // Toggle visibility with animation
            if (e.target.checked) {
                balloonDetails.style.display = 'block';
                // Optional: add fade-in effect
                balloonDetails.style.opacity = '0';
                setTimeout(() => {
                    balloonDetails.style.opacity = '1';
                    balloonDetails.style.transition = 'opacity 0.3s ease-in-out';
                }, 0);
            } else {
                balloonDetails.style.opacity = '0';
                setTimeout(() => {
                    balloonDetails.style.display = 'none';
                }, 300);
            }
            
            // Get all inputs in the balloon details section
            const balloonInputs = balloonDetails.querySelectorAll('input:not([type="checkbox"])');
            
            // Toggle required attribute and clear fields if unchecked
            balloonInputs.forEach(input => {
                if (e.target.checked) {
                    input.setAttribute('required', '');
                } else {
                    input.removeAttribute('required');
                    input.value = '';
                }
            });
        });
    
        // Set initial state
        const isChecked = balloonToggle.checked;
        balloonDetails.style.display = isChecked ? 'block' : 'none';
        balloonDetails.style.opacity = isChecked ? '1' : '0';
        
        const balloonInputs = balloonDetails.querySelectorAll('input:not([type="checkbox"])');
        balloonInputs.forEach(input => {
            input.required = isChecked;
        });
        
        console.log('Balloon payment handlers initialized successfully');
    },

    downloadPdf(analysisId) {
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

    initButtonHandlers() {
        const reEditButton = document.getElementById('reEditButton');
        if (reEditButton) {
            reEditButton.addEventListener('click', () => this.switchToFinancialTab());
        }
    },

    // Updated initRefinanceCalculations for flat 
    initRefinanceCalculations() {
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

    getAnalysisIdFromUrl() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('analysis_id');
    },

    // Configure toastr options
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

    initTabHandling() {
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

    // Update initAddressAutocomplete in the analysisModule
    initAddressAutocomplete() {
        console.log('Initializing address autocomplete');
        const addressInput = document.getElementById('address');
        
        if (!addressInput) {
            console.error('Address input not found');
            return;
        }

        // Create results list element
        const resultsList = document.createElement('ul');
        resultsList.className = 'autocomplete-results list-group position-absolute w-100 shadow-sm';
        resultsList.style.zIndex = '1000';
        
        // Insert the results list after the input
        addressInput.parentNode.appendChild(resultsList);
        
        let timeoutId;
        
        // Add input event listener
        addressInput.addEventListener('input', function() {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                const query = this.value;
                if (query.length > 2) {
                    console.log('Making API call for:', query);
                    fetch(`/api/autocomplete?query=${encodeURIComponent(query)}`)
                        .then(response => {
                            if (!response.ok) {
                                throw new Error(`HTTP error! status: ${response.status}`);
                            }
                            return response.json();
                        })
                        .then(data => {
                            console.log('API response:', data);
                            resultsList.innerHTML = '';
                            
                            if (data.status === 'success' && data.data && Array.isArray(data.data)) {
                                data.data.forEach(result => {
                                    const li = document.createElement('li');
                                    li.className = 'list-group-item list-group-item-action';
                                    li.textContent = result.formatted;
                                    li.style.cursor = 'pointer';
                                    
                                    li.addEventListener('click', function() {
                                        addressInput.value = this.textContent;
                                        resultsList.innerHTML = '';
                                    });
                                    
                                    resultsList.appendChild(li);
                                });
                                
                                if (data.data.length === 0) {
                                    const li = document.createElement('li');
                                    li.className = 'list-group-item disabled';
                                    li.textContent = 'No matches found';
                                    resultsList.appendChild(li);
                                }
                            }
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            resultsList.innerHTML = `
                                <li class="list-group-item text-danger">
                                    Error fetching results: ${error.message}
                                </li>
                            `;
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

        // Add some basic styling for the autocomplete
        const style = document.createElement('style');
        style.textContent = `
            .autocomplete-results {
                max-height: 200px;
                overflow-y: auto;
                background: white;
            }
            .autocomplete-results .list-group-item:hover {
                background-color: #f8f9fa;
            }
        `;
        document.head.appendChild(style);
    },

    async handleTypeChange(newType) {
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

    initAnalysisTypeHandler() {
        console.log('Starting initAnalysisTypeHandler');
        const analysisType = document.getElementById('analysis_type');
        const financialTab = document.getElementById('financial');
        console.log('Found elements:', { 
            analysisTypeExists: !!analysisType, 
            analysisTypeValue: analysisType?.value,
            financialTabExists: !!financialTab 
        });
        
        if (analysisType && financialTab) {
            // Remove any existing event listeners by cloning
            const newAnalysisType = analysisType.cloneNode(true);
            analysisType.parentNode.replaceChild(newAnalysisType, analysisType);
            
            // Get the analysis ID from URL if it exists
            const urlParams = new URLSearchParams(window.location.search);
            const analysisId = urlParams.get('analysis_id');
            console.log('AnalysisId in type handler:', analysisId);
            
            // Store initial value
            this.initialAnalysisType = analysisId ? null : newAnalysisType.value;
            console.log('Initial analysis type:', this.initialAnalysisType);
            
            // Load initial template if not editing existing analysis
            if (!analysisId) {
                console.log('Not editing - loading initial template for type:', this.initialAnalysisType);
                console.log('loadTemplateForType exists:', typeof this.loadTemplateForType === 'function');
                this.loadTemplateForType(this.initialAnalysisType, financialTab);
            }
                
            // Set up event listener for changes
            newAnalysisType.addEventListener('change', async (e) => {
                console.log('Analysis type changed to:', e.target.value);
                // Prevent multiple concurrent changes
                if (this.typeChangeInProgress) {
                    console.log('Type change already in progress');
                    return;
                }
    
                const newType = e.target.value;
                console.log('Processing change to type:', newType);
                console.log('Initial type:', this.initialAnalysisType);
                
                // Skip if initial type hasn't been set yet or if type hasn't actually changed
                if (!this.initialAnalysisType || newType === this.initialAnalysisType) {
                    console.log('Skipping - no initial type or no change. Initial:', 
                        this.initialAnalysisType, 'New:', newType);
                    return;
                }
                
                // If we're in create mode, just update the fields
                if (!this.currentAnalysisId) {
                    console.log('Create mode - will update template for type:', newType);
                    console.log('Financial tab exists:', !!financialTab);
                    console.log('loadTemplateForType exists:', typeof this.loadTemplateForType === 'function');
                    
                    // Call loadTemplateForType and check its result
                    try {
                        this.loadTemplateForType(newType, financialTab);
                        console.log('Template loaded successfully');
                    } catch (error) {
                        console.error('Error loading template:', error);
                    }
                    
                    this.initialAnalysisType = newType;
                    return;
                }
                
                try {
                    this.typeChangeInProgress = true;
                    const confirmed = await this.confirmTypeChange(newType);
                    
                    if (!confirmed) {
                        e.target.value = this.initialAnalysisType;
                        return;
                    }
                    
                    await this.handleTypeChange(newType);
                    
                } catch (error) {
                    console.error('Error:', error);
                    toastr.error(error.message);
                    e.target.value = this.initialAnalysisType;
                } finally {
                    this.typeChangeInProgress = false;
                }
            });
        } else {
            console.error('Missing required elements:', { 
                analysisType: !!analysisType, 
                financialTab: !!financialTab 
            });
        }
    },

    // Add a separate function for notes counter initialization
    initNotesCounter() {
        const notesTextarea = document.getElementById('notes');
        const notesCounter = document.getElementById('notes-counter');
        if (notesTextarea && notesCounter) {
            // Update counter with initial value if exists
            notesCounter.textContent = notesTextarea.value.length;
            
            // Add event listener for changes
            notesTextarea.addEventListener('input', function() {
                notesCounter.textContent = this.value.length;
            });
        }
    },

    loadAnalysisData(analysisId) {
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
                        if (this.initialAnalysisType === 'Lease Option') {
                            financialTab.innerHTML = getLeaseOptionHTML();
                        } else if (this.initialAnalysisType.includes('BRRRR')) {
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
    initLoanHandlers() {
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
    
        // Get form data
        const formData = new FormData(form);
        const analysisData = {};
        
        // First, set the balloon payment flag correctly
        const hasBalloon = form.querySelector('#has_balloon_payment')?.checked || false;
        analysisData.has_balloon_payment = hasBalloon;
        
        // Process each form field
        formData.forEach((value, key) => {
            if (key === 'has_balloon_payment') {
                return; // Skip as we've already handled this
            }
            
            // Handle balloon payment fields
            if (key.startsWith('balloon_')) {
                if (!hasBalloon) {
                    // If balloon payments are disabled, set all balloon fields to null
                    analysisData[key] = null;
                    return;
                }
            }
            
            // Normal field processing
            if (key.endsWith('_interest_only')) {
                const checkbox = form.querySelector(`#${key}`);
                analysisData[key] = checkbox ? checkbox.checked : false;
            } else if (key === 'balloon_due_date' && value && hasBalloon) {
                analysisData[key] = new Date(value).toISOString().split('T')[0];
            } else if (key.endsWith('_percentage') || this.isNumericField(key)) {
                analysisData[key] = value === '' ? 0 : this.toRawNumber(value);
            } else if (key === 'bathrooms') {
                analysisData[key] = this.toRawNumber(value);
            } else {
                analysisData[key] = value || null;
            }
        });
    
        // Make API call
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
    isNumericField(fieldName) {
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
            'year_built',
            'bedrooms',
            'option_consideration_fee',
            'strike_price',
            'rent_credit_cap'
        ];
    
        const decimalFields = [
            'bathrooms'
        ];
    
        const percentageFields = [
            'management_fee_percentage',
            'capex_percentage',
            'vacancy_percentage',
            'repairs_percentage',
            'padsplit_platform_percentage',
            'monthly_rent_credit_percentage'
        ];
    
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
    
        // Get current and original analysis types
        const formData = new FormData(form);
        const currentAnalysisType = formData.get('analysis_type');
        const originalAnalysisType = this.initialAnalysisType;
    
        // Create the analysis data object with ID
        const analysisData = {
            id: analysisId
        };
    
        // First, set the balloon payment flag correctly - convert checkbox value to boolean
        const hasBalloon = form.querySelector('#has_balloon_payment')?.checked || false;
        analysisData.has_balloon_payment = hasBalloon;  // This will be a true boolean, not 'on'
    
        // Process each field according to its type
        formData.forEach((value, key) => {
            if (key === 'has_balloon_payment') {
                // Skip as we've already handled this
                return;
            } else if (key.endsWith('_interest_only')) {
                // Handle checkbox fields - convert to boolean
                const checkbox = form.querySelector(`#${key}`);
                analysisData[key] = checkbox ? checkbox.checked : false;
            } else if (key === 'balloon_due_date' && value) {
                // Handle date field - only if balloon payments are enabled
                analysisData[key] = hasBalloon ? new Date(value).toISOString().split('T')[0] : null;
            } else if (key.endsWith('_percentage') || this.isNumericField(key)) {
                // Handle all numeric fields (including percentages)
                // Convert empty strings to 0
                analysisData[key] = value === '' ? 0 : this.toRawNumber(value);
            } else if (key === 'bathrooms') {
                // Handle bathrooms specifically as it can be decimal
                analysisData[key] = this.toRawNumber(value);
            } else {
                // Handle all other fields
                analysisData[key] = value || null;  // Convert empty strings to null
            }
        });
    
        // If balloon payment is false, ensure all balloon-related fields are 0 or null
        if (!hasBalloon) {
            const balloonFields = [
                'balloon_refinance_loan_amount',
                'balloon_refinance_loan_closing_costs',
                'balloon_refinance_loan_down_payment',
                'balloon_refinance_loan_interest_rate',
                'balloon_refinance_loan_term',
                'balloon_refinance_ltv_percentage'
            ];
            balloonFields.forEach(field => {
                analysisData[field] = 0;
            });
            analysisData.balloon_due_date = null;
        }
    
        // Set create_new flag if analysis type has changed
        if (currentAnalysisType !== originalAnalysisType) {
            analysisData.create_new = true;
        }
    
        // Log the prepared data
        console.log('Prepared analysis data:', analysisData);
    
        // Make the API call
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
                const analysisData = data.analysis.analysis || data.analysis;
                console.log('Analysis data for reports:', analysisData);
                
                if (!analysisData.analysis_type) {
                    console.error('Missing analysis type in data:', analysisData);
                    throw new Error('Invalid analysis data structure');
                }
    
                // Update IDs and URLs if needed
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
                submitBtn.innerHTML = '<i class="bi bi-save me-2"></i>Update Analysis';
                submitBtn.style.display = 'inline-block';
            }
        });
    },

    calculateMAO(analysis) {
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
    populateReportsTab(data) {
        console.log('Starting populateReportsTab with data:', data);
        
        const reportsContent = document.querySelector('#reports');
        if (!reportsContent) {
            console.error('Reports content element not found');
            return;
        }
        
        // Ensure we have the correct data structure
        const analysisData = data.analysis || data;
        this.currentAnalysisId = analysisData.id || null;
    
        try {
            let reportContent = '';
            const analysisType = analysisData.analysis_type || '';
            
            switch(analysisType) {
                case 'BRRRR':
                    reportContent = this.getBRRRRReportContent.call(this, analysisData);
                    break;
                case 'Lease Option':
                    reportContent = this.getLeaseOptionReportContent.call(this, analysisData);
                    break;
                default:
                    reportContent = this.getLTRReportContent.call(this, analysisData);
            }
    
            const finalContent = `
                <div class="row align-items-center mb-4">
                    <div class="col">
                        <h4 class="mb-0">${analysisType || 'Analysis'}: ${analysisData.analysis_name || 'Untitled'}</h4>
                    </div>
                    <div class="col-auto">
                        <div class="d-flex gap-2">
                            <button type="button" class="btn btn-secondary" onclick="analysisModule.downloadPdf('${analysisData.id}')">
                                <i class="bi bi-file-earmark-pdf me-1"></i>Download PDF
                            </button>
                            <button type="button" class="btn btn-primary" id="reEditButton">
                                <i class="bi bi-pencil me-1"></i>Re-Edit Analysis
                            </button>
                        </div>
                    </div>
                </div>
                ${reportContent}`;
    
            reportsContent.innerHTML = finalContent;
    
            const reEditButton = document.getElementById('reEditButton');
            if (reEditButton) {
                reEditButton.addEventListener('click', () => {
                    this.switchToFinancialTab();
                });
            }
        } catch (error) {
            console.error('Error in populateReportsTab:', error);
            reportsContent.innerHTML = `
                <div class="alert alert-danger">
                    Error generating report content: ${error.message}
                </div>`;
        }
    },

    // New function for lease option report content
    getLeaseOptionReportContent(analysis) {
        return `
            <!-- Option Details Card -->
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">Option Details</h5>
                </div>
                <div class="card-body">
                    <div class="list-group list-group-flush">
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Option Fee</span>
                            <strong>${this.formatDisplayValue(analysis.option_consideration_fee)}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Option Term</span>
                            <strong>${analysis.option_term_months} months</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Strike Price</span>
                            <strong>${this.formatDisplayValue(analysis.strike_price)}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Monthly Rent Credit</span>
                            <div class="text-end">
                                <div class="small text-muted">
                                    ${this.formatDisplayValue(analysis.monthly_rent_credit_percentage, 'percentage')}
                                </div>
                                <strong>${this.formatDisplayValue(analysis.monthly_rent * (analysis.monthly_rent_credit_percentage / 100))}/mo</strong>
                            </div>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Total Potential Credits</span>
                            <strong>${this.formatDisplayValue(Math.min(
                                analysis.monthly_rent * (analysis.monthly_rent_credit_percentage / 100) * analysis.option_term_months,
                                analysis.rent_credit_cap
                            ))}</strong>
                        </div>
                    </div>
                </div>
            </div>
    
            <!-- Financial Overview Card -->
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">Financial Overview</h5>
                </div>
                <div class="card-body">
                    <div class="list-group list-group-flush">
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Monthly Rent</span>
                            <strong>${this.formatDisplayValue(analysis.monthly_rent)}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Monthly Cash Flow</span>
                            <strong>${analysis.calculated_metrics?.monthly_cash_flow}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Annual Cash Flow</span>
                            <strong>${analysis.calculated_metrics?.annual_cash_flow}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Option Fee ROI (Annual)</span>
                            <strong>${this.formatDisplayValue(
                                (analysis.calculated_metrics?.annual_cash_flow / analysis.option_consideration_fee) * 100, 
                                'percentage'
                            )}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Cash-on-Cash Return</span>
                            <strong>${analysis.calculated_metrics?.cash_on_cash_return}</strong>
                        </div>
                    </div>
                </div>
            </div>
    
            <!-- Operating Expenses Card -->
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">Operating Expenses</h5>
                </div>
                <div class="card-body">
                    <div class="list-group list-group-flush">
                        <div class="row g-0">
                            <div class="col-12 col-md-6">
                                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                    <span>Property Taxes</span>
                                    <strong>${this.formatDisplayValue(analysis.property_taxes)}</strong>
                                </div>
                                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                    <span>Insurance</span>
                                    <strong>${this.formatDisplayValue(analysis.insurance)}</strong>
                                </div>
                                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                    <span>HOA/COA/COOP</span>
                                    <strong>${this.formatDisplayValue(analysis.hoa_coa_coop)}</strong>
                                </div>
                                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                    <span>Management</span>
                                    <div class="text-end">
                                        <div class="small text-muted">
                                            ${this.formatDisplayValue(analysis.management_fee_percentage, 'percentage')}
                                        </div>
                                        <strong>${this.formatDisplayValue(analysis.monthly_rent * (analysis.management_fee_percentage / 100))}</strong>
                                    </div>
                                </div>
                            </div>
                            <div class="col-12 col-md-6">
                                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                    <span>CapEx</span>
                                    <div class="text-end">
                                        <div class="small text-muted">
                                            ${this.formatDisplayValue(analysis.capex_percentage, 'percentage')}
                                        </div>
                                        <strong>${this.formatDisplayValue(analysis.monthly_rent * (analysis.capex_percentage / 100))}</strong>
                                    </div>
                                </div>
                                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                    <span>Vacancy</span>
                                    <div class="text-end">
                                        <div class="small text-muted">
                                            ${this.formatDisplayValue(analysis.vacancy_percentage, 'percentage')}
                                        </div>
                                        <strong>${this.formatDisplayValue(analysis.monthly_rent * (analysis.vacancy_percentage / 100))}</strong>
                                    </div>
                                </div>
                                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                    <span>Repairs</span>
                                    <div class="text-end">
                                        <div class="small text-muted">
                                            ${this.formatDisplayValue(analysis.repairs_percentage, 'percentage')}
                                        </div>
                                        <strong>${this.formatDisplayValue(analysis.monthly_rent * (analysis.repairs_percentage / 100))}</strong>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            ${this.createNotesSection(analysis.notes)}`;
    },

    getLTRReportContent(analysis) {
        console.log('LTR Report Data:', {
            monthlyRent: analysis.monthly_rent,
            monthlyCashFlow: analysis.calculated_metrics?.monthly_cash_flow,
            annualCashFlow: analysis.calculated_metrics?.annual_cash_flow,
            hasBalloon: this.hasBalloonData(analysis),
            fullMetrics: analysis.calculated_metrics
        });
    
        return `
            <!-- Income & Returns Card -->
            <div class="card mb-4">
                <div class="card-body p-3 p-md-4">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5 class="mb-0 fs-6 fs-md-5">
                            ${this.hasBalloonData(analysis) ? 'Pre-Balloon Financial Overview' : 'Income & Returns'}
                        </h5>
                        ${this.hasBalloonData(analysis) ? `
                            <span class="badge bg-primary">Balloon Due: ${new Date(analysis.balloon_due_date).toLocaleDateString()}</span>
                        ` : ''}
                    </div>
                    <div class="list-group list-group-flush">
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Monthly Rent</span>
                            <strong>${this.formatDisplayValue(analysis.monthly_rent)}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span class="d-flex align-items-center">
                                Monthly Cash Flow
                                <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" data-bs-html="true" 
                                   title="Monthly income after all operating expenses and ${this.hasBalloonData(analysis) ? 'initial ' : ''}loan payments">
                                </i>
                            </span>
                            <strong>${this.hasBalloonData(analysis) ? 
                                analysis.calculated_metrics?.pre_balloon_monthly_cash_flow :
                                analysis.calculated_metrics?.monthly_cash_flow}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span class="d-flex align-items-center">
                                Annual Cash Flow
                                <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" data-bs-html="true" 
                                   title="Monthly cash flow × 12 months">
                                </i>
                            </span>
                            <strong>${this.hasBalloonData(analysis) ? 
                                analysis.calculated_metrics?.pre_balloon_annual_cash_flow :
                                analysis.calculated_metrics?.annual_cash_flow}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span class="d-flex align-items-center">
                                Cash-on-Cash Return
                                <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" data-bs-html="true" 
                                   title="${this.hasBalloonData(analysis) ? 
                                       'Based on initial investment before balloon refinance' : 
                                       '(Annual Cash Flow ÷ Total Cash Invested) × 100'}">
                                </i>
                            </span>
                            <strong>${analysis.calculated_metrics?.cash_on_cash_return}</strong>
                        </div>
                    </div>
                </div>
            </div>
    
            <!-- Financing Details Card -->
            <div class="card mb-4">
                <div class="card-body p-3 p-md-4">
                    <h5 class="mb-3 fs-6 fs-md-5">Financing Details</h5>
                    ${this.getLoanDetailsContent(analysis)}
                </div>
            </div>
    
            <!-- Operating Expenses Card -->
            <div class="card mb-4">
                <div class="card-body p-3 p-md-4">
                    <h5 class="mb-3 fs-6 fs-md-5">
                        ${this.hasBalloonData(analysis) ? 'Pre-Balloon Operating Expenses' : 'Operating Expenses'}
                    </h5>
                    <div class="list-group list-group-flush">
                        <div class="row g-0">
                            <div class="col-12 col-md-6">
                                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                    <span>Property Taxes</span>
                                    <strong>${this.formatDisplayValue(analysis.property_taxes)}</strong>
                                </div>
                                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                    <span>Insurance</span>
                                    <strong>${this.formatDisplayValue(analysis.insurance)}</strong>
                                </div>
                                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                    <span>HOA/COA/COOP</span>
                                    <strong>${this.formatDisplayValue(analysis.hoa_coa_coop)}</strong>
                                </div>
                                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                    <span>Management</span>
                                    <div class="text-end">
                                        <div class="small text-muted">
                                            ${this.formatDisplayValue(analysis.management_fee_percentage, 'percentage')}
                                        </div>
                                        <strong>
                                            ${this.formatDisplayValue(analysis.monthly_rent * (analysis.management_fee_percentage / 100))}
                                        </strong>
                                    </div>
                                </div>
                            </div>
                            <div class="col-12 col-md-6">
                                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                    <span>CapEx</span>
                                    <div class="text-end">
                                        <div class="small text-muted">
                                            ${this.formatDisplayValue(analysis.capex_percentage, 'percentage')}
                                        </div>
                                        <strong>
                                            ${this.formatDisplayValue(analysis.monthly_rent * (analysis.capex_percentage / 100))}
                                        </strong>
                                    </div>
                                </div>
                                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                    <span>Vacancy</span>
                                    <div class="text-end">
                                        <div class="small text-muted">
                                            ${this.formatDisplayValue(analysis.vacancy_percentage, 'percentage')}
                                        </div>
                                        <strong>
                                            ${this.formatDisplayValue(analysis.monthly_rent * (analysis.vacancy_percentage / 100))}
                                        </strong>
                                    </div>
                                </div>
                                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                    <span>Repairs</span>
                                    <div class="text-end">
                                        <div class="small text-muted">
                                            ${this.formatDisplayValue(analysis.repairs_percentage, 'percentage')}
                                        </div>
                                        <strong>
                                            ${this.formatDisplayValue(analysis.monthly_rent * (analysis.repairs_percentage / 100))}
                                        </strong>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
    
            ${this.createNotesSection(analysis.notes)}`;
    },
    
    // Shared loan details component
    getLoanDetailsContent(analysis) {
        // Add debugging
        console.log('Loan payment metrics:', {
            loan1_payment: analysis.calculated_metrics?.loan1_loan_payment,
            loan2_payment: analysis.calculated_metrics?.loan2_loan_payment,
            loan3_payment: analysis.calculated_metrics?.loan3_loan_payment,
            hasBalloon: this.hasBalloonData(analysis),
            balloon_data: {
                amount: analysis.balloon_refinance_loan_amount,
                rate: analysis.balloon_refinance_loan_interest_rate,
                term: analysis.balloon_refinance_loan_term,
                due_date: analysis.balloon_due_date
            },
            all_metrics: analysis.calculated_metrics
        });
    
        if (this.hasBalloonData(analysis)) {
            // Get metrics
            const preMonthlyPayment = analysis.calculated_metrics?.pre_balloon_monthly_payment || 
                                     analysis.calculated_metrics?.loan1_loan_payment;
            const postMonthlyPayment = analysis.calculated_metrics?.post_balloon_monthly_payment || 
                                      analysis.calculated_metrics?.refinance_loan_payment;
            
            return `
                <div class="accordion" id="balloonLoanAccordion">
                    <!-- Pre-Balloon Section -->
                    <div class="accordion-item">
                        <h6 class="accordion-header">
                            <button class="accordion-button" type="button" data-bs-toggle="collapse" 
                                    data-bs-target="#preBalloonCollapse">
                                Original Loan (Pre-Balloon)
                            </button>
                        </h6>
                        <div id="preBalloonCollapse" class="accordion-collapse collapse show" 
                             data-bs-parent="#balloonLoanAccordion">
                            <div class="accordion-body p-0">
                                <div class="list-group list-group-flush">
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span>Amount</span>
                                        <strong>${this.formatDisplayValue(analysis.loan1_loan_amount)}</strong>
                                    </div>
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span>Interest Rate</span>
                                        <strong>${this.formatDisplayValue(analysis.loan1_loan_interest_rate, 'percentage')}</strong>
                                    </div>
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span>Term</span>
                                        <strong>${analysis.loan1_loan_term} months</strong>
                                    </div>
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span class="d-flex align-items-center">
                                            Monthly Payment
                                            <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" 
                                               title="Monthly payment before balloon refinance"></i>
                                        </span>
                                        <strong>${preMonthlyPayment || this.formatDisplayValue(0)}</strong>
                                    </div>
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span>Down Payment</span>
                                        <strong>${this.formatDisplayValue(analysis.loan1_loan_down_payment)}</strong>
                                    </div>
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span>Closing Costs</span>
                                        <strong>${this.formatDisplayValue(analysis.loan1_loan_closing_costs)}</strong>
                                    </div>
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span>Balloon Due Date</span>
                                        <strong>${new Date(analysis.balloon_due_date).toLocaleDateString()}</strong>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
    
                    <!-- Post-Balloon Section -->
                    <div class="accordion-item">
                        <h6 class="accordion-header">
                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" 
                                    data-bs-target="#postBalloonCollapse">
                                Balloon Refinance Terms
                            </button>
                        </h6>
                        <div id="postBalloonCollapse" class="accordion-collapse collapse" 
                             data-bs-parent="#balloonLoanAccordion">
                            <div class="accordion-body p-0">
                                <div class="list-group list-group-flush">
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span>Refinance Amount</span>
                                        <strong>${this.formatDisplayValue(analysis.balloon_refinance_loan_amount)}</strong>
                                    </div>
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span>Interest Rate</span>
                                        <strong>${this.formatDisplayValue(analysis.balloon_refinance_loan_interest_rate, 'percentage')}</strong>
                                    </div>
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span>Term</span>
                                        <strong>${analysis.balloon_refinance_loan_term} months</strong>
                                    </div>
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span class="d-flex align-items-center">
                                            Monthly Payment
                                            <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" 
                                               title="Monthly payment after balloon refinance"></i>
                                        </span>
                                        <strong>${postMonthlyPayment || this.formatDisplayValue(0)}</strong>
                                    </div>
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span>LTV</span>
                                        <strong>${this.formatDisplayValue(analysis.balloon_refinance_ltv_percentage, 'percentage')}</strong>
                                    </div>
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span>Down Payment</span>
                                        <strong>${this.formatDisplayValue(analysis.balloon_refinance_loan_down_payment)}</strong>
                                    </div>
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span>Closing Costs</span>
                                        <strong>${this.formatDisplayValue(analysis.balloon_refinance_loan_closing_costs)}</strong>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>`;
        } else {
            // Regular loans
            const loanPrefixes = ['loan1', 'loan2', 'loan3'];
            let hasLoans = false;
            
            let html = '<div class="accordion" id="regularLoansAccordion">';
            
            for (const prefix of loanPrefixes) {
                if (analysis[`${prefix}_loan_amount`] > 0) {
                    hasLoans = true;
                    html += `
                        <div class="accordion-item">
                            <h6 class="accordion-header">
                                <button class="accordion-button ${prefix !== 'loan1' ? 'collapsed' : ''}" type="button" 
                                        data-bs-toggle="collapse" data-bs-target="#${prefix}Collapse">
                                    ${analysis[`${prefix}_loan_name`] || `Loan ${prefix.slice(-1)}`}
                                </button>
                            </h6>
                            <div id="${prefix}Collapse" class="accordion-collapse collapse ${prefix === 'loan1' ? 'show' : ''}" 
                                 data-bs-parent="#regularLoansAccordion">
                                <div class="accordion-body p-0">
                                    <div class="list-group list-group-flush">
                                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                            <span>Amount</span>
                                            <strong>${this.formatDisplayValue(analysis[`${prefix}_loan_amount`])}</strong>
                                        </div>
                                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                            <span>Interest Rate</span>
                                            <div>
                                                <strong>${this.formatDisplayValue(analysis[`${prefix}_loan_interest_rate`], 'percentage')}</strong>
                                                <span class="badge ${analysis[`${prefix}_interest_only`] ? 'bg-success' : 'bg-info'} ms-2">
                                                    ${analysis[`${prefix}_interest_only`] ? 'Interest Only' : 'Amortized'}
                                                </span>
                                            </div>
                                        </div>
                                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                            <span>Term</span>
                                            <strong>${analysis[`${prefix}_loan_term`] || '0'} months</strong>
                                        </div>
                                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                            <span class="d-flex align-items-center">
                                                Monthly Payment
                                                <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" 
                                                   title="${analysis[`${prefix}_interest_only`] ? 
                                                       'Interest-only payment on loan' : 
                                                       'Fully amortized payment including principal and interest'}"></i>
                                            </span>
                                            <strong>${analysis.calculated_metrics?.[`${prefix}_loan_payment`] || 
                                                     this.formatDisplayValue(0)}</strong>
                                        </div>
                                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                            <span>Down Payment</span>
                                            <strong>${this.formatDisplayValue(analysis[`${prefix}_loan_down_payment`])}</strong>
                                        </div>
                                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                            <span>Closing Costs</span>
                                            <strong>${this.formatDisplayValue(analysis[`${prefix}_loan_closing_costs`])}</strong>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>`;
                }
            }
            html += '</div>';
            
            return hasLoans ? html : `
                <div class="text-center py-4">
                    <p class="mb-0 text-muted">No loan details available</p>
                </div>`;
        }
    },

    // Updated getBRRRRReportContent function to handle flat schema and formatting
    getBRRRRReportContent(analysis) {
        // Add debugging
        console.log('BRRRR Report Data:', {
            initialLoanPayment: analysis.calculated_metrics?.initial_loan_payment,
            refinanceLoanPayment: analysis.calculated_metrics?.refinance_loan_payment,
            monthlyRent: analysis.monthly_rent,
            monthlyCashFlow: analysis.calculated_metrics?.monthly_cash_flow,
            annualCashFlow: analysis.calculated_metrics?.annual_cash_flow,
            fullMetrics: analysis.calculated_metrics
        });
    
        // Check for required data
        if (!analysis || !analysis.calculated_metrics) {
            console.error('Missing required data for BRRRR report');
            return '';
        }
    
        return `
            <div class="card mb-4">
                <div class="card-body p-3 p-md-4">
                    <div class="row g-4">
                        <!-- Income & Returns Section -->
                        <div class="col-12 col-lg-6">
                            <h5 class="mb-3 fs-6 fs-md-5">Income & Returns</h5>
                            <div class="card bg-light h-100">
                                <div class="list-group list-group-flush">
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span>Monthly Rent</span>
                                        <strong>${this.formatDisplayValue(analysis.monthly_rent)}</strong>
                                    </div>
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span>Monthly Cash Flow</span>
                                        <strong>${analysis.calculated_metrics.monthly_cash_flow}</strong>
                                    </div>
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span>Annual Cash Flow</span>
                                        <strong>${analysis.calculated_metrics.annual_cash_flow}</strong>
                                    </div>
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span>Cash-on-Cash Return</span>
                                        <strong>${analysis.calculated_metrics.cash_on_cash_return}</strong>
                                    </div>
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span>ROI</span>
                                        <strong>${analysis.calculated_metrics.roi}</strong>
                                    </div>
                                </div>
                            </div>
                        </div>
    
                        <!-- Financing Section -->
                        <div class="col-12 col-lg-6">
                            <h5 class="mb-3 fs-6 fs-md-5">BRRRR Strategy Details</h5>
                            <div class="card bg-light h-100">
                                <div class="accordion" id="brrrFinancingAccordion">
                                    <!-- Initial Loan Section -->
                                    <div class="accordion-item">
                                        <h6 class="accordion-header">
                                            <button class="accordion-button" type="button" data-bs-toggle="collapse" 
                                                    data-bs-target="#initialLoanCollapse">
                                                Initial Loan Details
                                            </button>
                                        </h6>
                                        <div id="initialLoanCollapse" class="accordion-collapse collapse show" 
                                             data-bs-parent="#brrrFinancingAccordion">
                                            <div class="accordion-body p-0">
                                                <div class="list-group list-group-flush">
                                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                                        <span>Monthly Payment</span>
                                                        <strong>${analysis.calculated_metrics.initial_loan_payment}</strong>
                                                    </div>
                                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                                        <span>Interest Rate</span>
                                                        <strong>${this.formatDisplayValue(analysis.initial_loan_interest_rate, 'percentage')}</strong>
                                                    </div>
                                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                                        <span>Term</span>
                                                        <strong>${analysis.initial_loan_term} months</strong>
                                                    </div>
                                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                                        <span>Down Payment</span>
                                                        <strong>${this.formatDisplayValue(analysis.initial_loan_down_payment)}</strong>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
    
                                    <!-- Refinance Loan Section -->
                                    <div class="accordion-item">
                                        <h6 class="accordion-header">
                                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" 
                                                    data-bs-target="#refinanceCollapse">
                                                Refinance Details
                                            </button>
                                        </h6>
                                        <div id="refinanceCollapse" class="accordion-collapse collapse" 
                                             data-bs-parent="#brrrFinancingAccordion">
                                            <div class="accordion-body p-0">
                                                <div class="list-group list-group-flush">
                                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                                        <span>Monthly Payment</span>
                                                        <strong>${analysis.calculated_metrics.refinance_loan_payment}</strong>
                                                    </div>
                                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                                        <span>Interest Rate</span>
                                                        <strong>${this.formatDisplayValue(analysis.refinance_loan_interest_rate, 'percentage')}</strong>
                                                    </div>
                                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                                        <span>Term</span>
                                                        <strong>${analysis.refinance_loan_term} months</strong>
                                                    </div>
                                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                                        <span>Down Payment</span>
                                                        <strong>${this.formatDisplayValue(analysis.refinance_loan_down_payment)}</strong>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
    
                        <!-- Operating Expenses Section -->
                        <div class="col-12">
                            <h5 class="mb-3 fs-6 fs-md-5">Operating Expenses</h5>
                            <div class="card bg-light">
                                <div class="list-group list-group-flush">
                                    <div class="row g-0">
                                        <div class="col-12 col-md-6">
                                            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                                <span>Property Taxes</span>
                                                <strong>${this.formatDisplayValue(analysis.property_taxes)}</strong>
                                            </div>
                                            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                                <span>Insurance</span>
                                                <strong>${this.formatDisplayValue(analysis.insurance)}</strong>
                                            </div>
                                            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                                <span>HOA/COA/COOP</span>
                                                <strong>${this.formatDisplayValue(analysis.hoa_coa_coop)}</strong>
                                            </div>
                                            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                                <span>Management</span>
                                                <div class="text-end">
                                                    <div class="small text-muted">
                                                        ${this.formatDisplayValue(analysis.management_fee_percentage, 'percentage')}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-12 col-md-6">
                                            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                                <span>CapEx</span>
                                                <div class="text-end">
                                                    <div class="small text-muted">
                                                        ${this.formatDisplayValue(analysis.capex_percentage, 'percentage')}
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                                <span>Vacancy</span>
                                                <div class="text-end">
                                                    <div class="small text-muted">
                                                        ${this.formatDisplayValue(analysis.vacancy_percentage, 'percentage')}
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                                <span>Repairs</span>
                                                <div class="text-end">
                                                    <div class="small text-muted">
                                                        ${this.formatDisplayValue(analysis.repairs_percentage, 'percentage')}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            ${this.createNotesSection(analysis.notes)}`;
    },

    // Helper method to initialize report event handlers
    initReportEventHandlers() {
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

    switchToFinancialTab() {
        const financialTab = document.getElementById('financial-tab');
        const submitBtn = document.getElementById('submitAnalysisBtn');
        const reEditButton = document.getElementById('reEditButton');
        
        if (financialTab) {
            financialTab.click();
        }
    
        console.log('Switching to financial tab, currentAnalysisId:', this.currentAnalysisId);
        console.log('Submit button exists:', !!submitBtn);
    
        // Always create or show submit button when editing
        if (!submitBtn) {
            console.log('Creating new submit button');
            const form = document.getElementById('analysisForm');
            const actionButtons = form.querySelector('.d-flex.gap-2');
            if (actionButtons) {
                const newSubmitBtn = document.createElement('button');
                newSubmitBtn.id = 'submitAnalysisBtn';
                newSubmitBtn.type = 'submit';
                newSubmitBtn.className = 'btn btn-success';
                newSubmitBtn.innerHTML = '<i class="bi bi-save me-2"></i>Update Analysis';
                actionButtons.insertBefore(newSubmitBtn, actionButtons.firstChild);
                
                // Set up form for editing
                if (this.currentAnalysisId) {
                    form.setAttribute('data-analysis-id', this.currentAnalysisId);
                    form.onsubmit = (event) => this.handleEditSubmit(event, this.currentAnalysisId);
                }
                console.log('New submit button created');
            }
        } else {
            console.log('Showing existing submit button');
            submitBtn.style.display = 'inline-block';
            submitBtn.innerHTML = '<i class="bi bi-save me-2"></i>Update Analysis';
        }
    
        // Hide re-edit button if it exists
        if (reEditButton) {
            reEditButton.style.display = 'none';
        }
    },

    switchToReportsTab() {
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

    showReportActions() {
        const submitBtn = document.getElementById('submitAnalysisBtn');
        const reEditButton = document.getElementById('reEditButton');
        
        if (submitBtn && reEditButton) {
            submitBtn.style.display = 'none';
            reEditButton.style.display = 'inline-block';
        }
    },

    editAnalysis() {
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
    cleanNumericValue(value, fieldName) {
        if (value === null || value === undefined || value === '') {
            return '0';
        }
        
        // Convert to string if not already
        value = String(value);
        
        // Handle special lease option fields
        if (fieldName === 'option_term_months') {
            return value.replace(/\D/g, ''); // Strip non-digits
        }
        
        // Remove currency symbols, commas, spaces
        let cleaned = value.replace(/[$,\s]/g, '');
        
        // Remove % symbol
        cleaned = cleaned.replace(/%/g, '');
        
        return cleaned || '0';
    },

    // Updated populateFormFields function - uses raw values
    populateFormFields(analysis) {
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
            setFieldValue('bedrooms', analysis.bedrooms);
            setFieldValue('bathrooms', analysis.bathrooms);
            
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

            // Handle Lease Option fields
            if (analysis.analysis_type === 'Lease Option') {
                // Clear any irrelevant fields that might be present
                ['after_repair_value', 'renovation_costs', 'renovation_duration'].forEach(field => {
                    const element = document.getElementById(field);
                    if (element) element.value = '';
                });
                
                // Set Lease Option specific fields
                setFieldValue('option_consideration_fee', analysis.option_consideration_fee);
                setFieldValue('option_term_months', analysis.option_term_months);
                setFieldValue('strike_price', analysis.strike_price);
                setFieldValue('monthly_rent_credit_percentage', analysis.monthly_rent_credit_percentage);
                setFieldValue('rent_credit_cap', analysis.rent_credit_cap);
                
                // Handle loan fields
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
                            
                            // Handle interest-only checkbox
                            const interestOnlyCheckbox = document.getElementById(`${prefix}_interest_only`);
                            if (interestOnlyCheckbox) {
                                interestOnlyCheckbox.checked = Boolean(analysis[`${prefix}_interest_only`]);
                                interestOnlyCheckbox.dispatchEvent(new Event('change', { bubbles: true }));
                                console.log(`Setting ${prefix}_interest_only to:`, Boolean(analysis[`${prefix}_interest_only`]));
                            }
                        }
                    }
                }
                
                // Initialize loan handlers after populating fields
                this.initLoanHandlers();
            }

            // Initialize balloon payment handlers AFTER setting values
            this.initBalloonPaymentHandlers(true);  // Pass true to skip toggle init

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

            // Set Notes
            setFieldValue('notes', analysis.notes || '');
            
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

    createNewAnalysis() {
        window.location.href = '/analyses/create_analysis';
    },

    downloadPdf(analysisId) {
        if (!analysisId) {
            console.error('No analysis ID available');
            toastr.error('Unable to generate PDF: No analysis ID found');
            return;
        }
        
        // Get button reference
        const downloadBtn = document.getElementById('downloadPdfBtn');
        if (downloadBtn) {
            // Show loading state
            downloadBtn.disabled = true;
            downloadBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generating PDF...';
        }
        
        // Make AJAX request instead of form submission
        fetch(`/analyses/generate_pdf/${analysisId}`)
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw err; });
                }
                return response.blob();
            })
            .then(blob => {
                // Create download link
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `analysis_${analysisId}.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                toastr.success('PDF generated successfully');
            })
            .catch(error => {
                console.error('Error:', error);
                toastr.error(error.message || 'Error generating PDF');
            })
            .finally(() => {
                if (downloadBtn) {
                    downloadBtn.disabled = false;
                    downloadBtn.innerHTML = 'Download PDF';
                }
            });
    },

    validateNumericRange(value, min, max = Infinity) {
        const num = this.toRawNumber(value);
        return !isNaN(num) && num >= min && num <= (max || Infinity);
    },

    // Updated validation function for flat schema
    validateForm(form) {
        let isValid = true;
        const hasBalloon = form.querySelector('#has_balloon_payment')?.checked || false;
        const analysisType = form.querySelector('#analysis_type')?.value;
    
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
    
        // Lease Option specific validation
        if (analysisType === 'Lease Option') {
            console.log('Validating Lease Option fields');
            const leaseFields = {
                'option_consideration_fee': {
                    validate: value => validateNumericRange(value, 0),
                    message: "Option fee must be greater than 0"
                },
                'option_term_months': {
                    validate: value => validateNumericRange(value, 1, 120),
                    message: "Option term must be between 1 and 120 months"
                },
                'strike_price': {
                    validate: value => {
                        const strikePrice = this.toRawNumber(value);
                        const purchasePrice = this.toRawNumber(form.querySelector('#purchase_price').value);
                        return strikePrice > purchasePrice;
                    },
                    message: "Strike price must be greater than purchase price"
                },
                'monthly_rent_credit_percentage': {
                    validate: value => validateNumericRange(value, 0, 100),
                    message: "Rent credit percentage must be between 0 and 100"
                },
                'rent_credit_cap': {
                    validate: value => validateNumericRange(value, 0),
                    message: "Rent credit cap must be greater than 0"
                }
            };
    
            Object.entries(leaseFields).forEach(([fieldName, config]) => {
                const field = form.querySelector(`#${fieldName}`);
                if (field) {
                    const value = field.value;
                    if (!config.validate(value)) {
                        isValid = false;
                        field.classList.add('is-invalid');
                        
                        let errorDiv = field.nextElementSibling;
                        if (!errorDiv || !errorDiv.classList.contains('invalid-feedback')) {
                            errorDiv = document.createElement('div');
                            errorDiv.className = 'invalid-feedback';
                            field.parentNode.insertBefore(errorDiv, field.nextSibling);
                        }
                        errorDiv.textContent = config.message;
                    } else {
                        field.classList.remove('is-invalid');
                        const errorDiv = field.nextElementSibling;
                        if (errorDiv?.classList.contains('invalid-feedback')) {
                            errorDiv.remove();
                        }
                    }
                }
            });
        }
    
        // Validate balloon payment fields only if enabled
        if (hasBalloon) {
            const balloonFields = {
                'balloon_due_date': {
                    validate: (value) => {
                        if (!value) return false;
                        const dueDate = new Date(value);
                        const today = new Date();
                        today.setHours(0, 0, 0, 0);
                        return dueDate >= today;
                    },
                    message: "Balloon due date must be in the future"
                },
                'balloon_refinance_ltv_percentage': {
                    validate: (value) => validateNumericRange(value, 0, 100),
                    message: "LTV percentage must be between 0 and 100"
                },
                'balloon_refinance_loan_amount': {
                    validate: (value) => validateNumericRange(value, 0),
                    message: "Refinance loan amount must be greater than 0"
                },
                'balloon_refinance_loan_interest_rate': {
                    validate: (value) => validateNumericRange(value, 0, 30),
                    message: "Interest rate must be between 0 and 30"
                },
                'balloon_refinance_loan_term': {
                    validate: (value) => validateNumericRange(value, 1, 360),
                    message: "Loan term must be between 1 and 360 months"
                }
            };
    
            Object.entries(balloonFields).forEach(([fieldName, config]) => {
                const field = form.querySelector(`#${fieldName}`);
                if (field) {
                    const value = field.value;
                    if (!config.validate(value)) {
                        isValid = false;
                        field.classList.add('is-invalid');
                        
                        let errorDiv = field.nextElementSibling;
                        if (!errorDiv || !errorDiv.classList.contains('invalid-feedback')) {
                            errorDiv = document.createElement('div');
                            errorDiv.className = 'invalid-feedback';
                            field.parentNode.insertBefore(errorDiv, field.nextSibling);
                        }
                        errorDiv.textContent = config.message;
                    } else {
                        field.classList.remove('is-invalid');
                        const errorDiv = field.nextElementSibling;
                        if (errorDiv?.classList.contains('invalid-feedback')) {
                            errorDiv.remove();
                        }
                    }
                }
            });
        }
    
        // Validate loan fields if present
        if (analysisType?.includes('BRRRR')) {
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

console.log('Analysis module loaded:', window.analysisModule);
console.log('Init function present:', typeof window.analysisModule.init === 'function');

// Optional: Initialize if not being loaded by moduleManager
if (!window.moduleManager) {
    document.addEventListener('DOMContentLoaded', function() {
        if (typeof window.analysisModule.init === 'function') {
            window.analysisModule.init();
        }
    });
}