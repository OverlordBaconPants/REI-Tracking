import compsHandler from './comps_handler.js';

// Add new template for Multi-Family analysis
const getMultiFamilyHTML = () => `
    <!-- Property Details Card -->
    <div class="card mb-4">
        <div class="card-header">
            <h5 class="mb-0">Property Details</h5>
        </div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-12 col-md-6">
                    <label for="property_type" class="form-label">Property Type</label>
                    <select class="form-select form-select-lg" id="property_type" name="property_type" required>
                        <option value="">Select Property Type</option>
                        <option value="Single Family">Single Family</option>
                        <option value="Condo">Condo</option>
                        <option value="Townhouse">Townhouse</option>
                        <option value="Manufactured">Manufactured</option>
                    </select>
                </div>
                <div class="col-12 col-md-4">
                    <label for="square_footage" class="form-label">Total Square Footage</label>
                    <div class="input-group">
                        <input type="number" class="form-control form-control-lg" id="square_footage" 
                            name="square_footage" placeholder="Total building square footage">
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
                <div class="col-12 col-md-4">
                    <label for="total_units" class="form-label">Total Units</label>
                    <input type="number" class="form-control form-control-lg" id="total_units" 
                        name="total_units" min="2" placeholder="Number of units" required>
                </div>
                <div class="col-12 col-md-4">
                    <label for="occupied_units" class="form-label">Occupied Units</label>
                    <input type="number" class="form-control form-control-lg" id="occupied_units" 
                        name="occupied_units" min="0" placeholder="Currently occupied units" required>
                </div>
                <div class="col-12 col-md-4">
                    <label for="floors" class="form-label">Number of Floors</label>
                    <input type="number" class="form-control form-control-lg" id="floors" 
                        name="floors" min="1" placeholder="Number of floors" required>
                </div>
            </div>
        </div>
    </div>

    <!-- Unit Mix Card -->
    <div class="card mb-4">
        <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Unit Mix</h5>
            <button type="button" class="btn btn-primary btn-sm" id="add-unit-type-btn">
                <i class="bi bi-plus-circle me-2"></i>Add Unit Type
            </button>
        </div>
        <div class="card-body">
            <div id="unit-types-container">
                <!-- Unit types will be added here dynamically -->
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

    <!-- Building Income Card -->
    <div class="card mb-4">
        <div class="card-header">
            <h5 class="mb-0">Building Income</h5>
        </div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-12 col-md-6">
                    <label for="other_income" class="form-label">Other Monthly Income</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="other_income" 
                               name="other_income" placeholder="Parking, laundry, etc." required>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="total_potential_income" class="form-label">Total Potential Income</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="total_potential_income" 
                               name="total_potential_income" readonly>
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

    <!-- Operating Expenses Card -->
    <div class="card mb-4">
        <div class="card-header">
            <h5 class="mb-0">Operating Expenses</h5>
        </div>
        <div class="card-body">
            <div class="row g-3">
                <!-- Standard Expenses -->
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
                
                <!-- Multi-Family Specific Expenses -->
                <div class="col-12 col-md-6">
                    <label for="common_area_maintenance" class="form-label">Common Area Maintenance</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="common_area_maintenance" 
                               name="common_area_maintenance" placeholder="Monthly CAM costs" required>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="elevator_maintenance" class="form-label">Elevator Maintenance</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="elevator_maintenance" 
                               name="elevator_maintenance" placeholder="Monthly maintenance">
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="staff_payroll" class="form-label">Staff Payroll</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="staff_payroll" 
                               name="staff_payroll" placeholder="Monthly payroll costs" required>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="trash_removal" class="form-label">Trash Removal</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="trash_removal" 
                               name="trash_removal" placeholder="Monthly cost" required>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="common_utilities" class="form-label">Common Utilities</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="common_utilities" 
                               name="common_utilities" placeholder="Monthly utilities" required>
                    </div>
                </div>

                <!-- Percentage-based expenses -->
                <div class="col-12 col-md-6">
                    <label for="management_fee_percentage" class="form-label">Management Fee</label>
                    <div class="input-group">
                        <input type="number" class="form-control form-control-lg" id="management_fee_percentage" 
                               name="management_fee_percentage" value="4" min="0" max="100" step="0.5" required>
                        <span class="input-group-text">%</span>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="capex_percentage" class="form-label">CapEx</label>
                    <div class="input-group">
                        <input type="number" class="form-control form-control-lg" id="capex_percentage" 
                               name="capex_percentage" value="5" min="0" max="100" step="1" required>
                        <span class="input-group-text">%</span>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="repairs_percentage" class="form-label">Repairs</label>
                    <div class="input-group">
                        <input type="number" class="form-control form-control-lg" id="repairs_percentage" 
                               name="repairs_percentage" value="3" min="0" max="100" step="1" required>
                        <span class="input-group-text">%</span>
                    </div>
                </div>
                <div class="col-12 col-md-6">
                    <label for="vacancy_percentage" class="form-label">Vacancy Rate</label>
                    <div class="input-group">
                        <input type="number" class="form-control form-control-lg" id="vacancy_percentage" 
                               name="vacancy_percentage" value="7" min="0" max="100" step="1" required>
                        <span class="input-group-text">%</span>
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

// Template for adding unit types dynamically
const getUnitTypeHTML = (index) => `
    <div class="unit-type-section mb-4" data-unit-index="${index}">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h6 class="mb-0">Unit Type ${index + 1}</h6>
                <button type="button" class="btn btn-danger btn-sm remove-unit-type-btn">
                    <i class="bi bi-trash me-2"></i>Remove
                </button>
            </div>
            <div class="card-body">
                <div class="row g-3">
                    <div class="col-12 col-md-6">
                        <label class="form-label">Unit Type</label>
                        <select class="form-select form-select-lg" name="unit_types[${index}][type]" required>
                            <option value="studio">Studio</option>
                            <option value="1br">1 Bedroom</option>
                            <option value="2br">2 Bedrooms</option>
                            <option value="3br">3 Bedrooms</option>
                            <option value="4br">4 Bedrooms</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                    <div class="col-12 col-md-6">
                        <label class="form-label">Number of Units</label>
                        <input type="number" class="form-control form-control-lg unit-count" 
                               name="unit_types[${index}][count]" min="1" required>
                    </div>
                    <div class="col-12 col-md-6">
                        <label class="form-label">Square Footage per Unit</label>
                        <div class="input-group">
                            <input type="number" class="form-control form-control-lg" 
                                   name="unit_types[${index}][square_footage]" required>
                            <span class="input-group-text">sq ft</span>
                        </div>
                    </div>
                    <div class="col-12 col-md-6">
                        <label class="form-label">Monthly Rent per Unit</label>
                        <div class="input-group">
                            <span class="input-group-text">$</span>
                            <input type="number" class="form-control form-control-lg unit-rent" 
                                   name="unit_types[${index}][rent]" required>
                        </div>
                    </div>
                    <div class="col-12 col-md-6">
                        <label class="form-label">Number of Occupied Units</label>
                        <input type="number" class="form-control form-control-lg unit-occupied" 
                               name="unit_types[${index}][occupied]" min="0" required>
                    </div>
                </div>
            </div>
        </div>
    </div>
`;

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
                <div class="col-12 col-md-6">
                    <label for="property_type" class="form-label">Property Type</label>
                    <select class="form-select form-select-lg" id="property_type" name="property_type" required>
                        <option value="">Select Property Type</option>
                        <option value="Single Family">Single Family</option>
                        <option value="Condo">Condo</option>
                        <option value="Townhouse">Townhouse</option>
                        <option value="Manufactured">Manufactured</option>
                    </select>
                </div>
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
                    <div class="col-12 col-md-6">
                        <label for="property_type" class="form-label">Property Type</label>
                        <select class="form-select form-select-lg" id="property_type" name="property_type" required>
                            <option value="">Select Property Type</option>
                            <option value="Single Family">Single Family</option>
                            <option value="Condo">Condo</option>
                            <option value="Townhouse">Townhouse</option>
                            <option value="Manufactured">Manufactured</option>
                        </select>
                    </div>
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
                <!-- Add Cash to Seller field -->
                <div class="col-12 col-md-6">
                    <label for="cash_to_seller" class="form-label">Cash to Seller</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="cash_to_seller" 
                               name="cash_to_seller" placeholder="Cash paid directly to seller">
                    </div>
                </div>
                <!-- Add Assignment Fee field -->
                <div class="col-12 col-md-6">
                    <label for="assignment_fee" class="form-label">Assignment Fee</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="assignment_fee" 
                               name="assignment_fee" placeholder="Assignment fee if any">
                    </div>
                </div>
                <!-- Add Closing Costs field -->
                <div class="col-12 col-md-6">
                    <label for="closing_costs" class="form-label">Closing Costs</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="closing_costs" 
                               name="closing_costs" placeholder="Base closing costs">
                    </div>
                </div>
                <!-- Add Marketing Costs field -->
                <div class="col-12 col-md-6">
                    <label for="marketing_costs" class="form-label">Marketing Costs</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="marketing_costs" 
                               name="marketing_costs" placeholder="Marketing costs if any">
                    </div>
                </div>
                <!-- Add Furnishing Costs field for PadSplit -->
                <div class="col-12 col-md-6 padsplit-field" style="display: none;">
                    <label for="furnishing_costs" class="form-label">Furnishing Costs</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="furnishing_costs" 
                            name="furnishing_costs" placeholder="PadSplit furnishing costs" required>
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
    <!-- Property Details Card -->
    <div class="card mb-4">
        <div class="card-header">
            <h5 class="mb-0">Property Details</h5>
        </div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-12 col-md-6">
                    <label for="property_type" class="form-label">Property Type</label>
                    <select class="form-select form-select-lg" id="property_type" name="property_type" required>
                        <option value="">Select Property Type</option>
                        <option value="Single Family">Single Family</option>
                        <option value="Condo">Condo</option>
                        <option value="Townhouse">Townhouse</option>
                        <option value="Manufactured">Manufactured</option>
                    </select>
                </div>
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
                <!-- Add Furnishing Costs field for PadSplit -->
                <div class="col-12 col-md-6 padsplit-field" style="display: none;">
                    <label for="furnishing_costs" class="form-label">Furnishing Costs</label>
                    <div class="input-group">
                        <span class="input-group-text">$</span>
                        <input type="number" class="form-control form-control-lg" id="furnishing_costs" 
                            name="furnishing_costs" placeholder="PadSplit furnishing costs" required>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Initial Financing -->
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

    <!-- Refinance Details -->
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
                               name="monthly_rent" placeholder="Expected monthly rent" required>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Operating Expenses -->
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

const getCompsHTML = (hasExistingComps = false) => `
    <!-- Comps Card -->
    <div class="card mb-4" id="compsCard">
        <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Property Comparables</h5>
            <div>
                <span id="compsRunCount" class="badge bg-info me-2" style="display: none;">
                    Runs: <span id="runCountValue">0</span>/3
                </span>
                <button type="button" class="btn btn-primary" id="runCompsBtn">
                    <i class="bi bi-arrow-repeat me-2"></i>${hasExistingComps ? 'Re-Run Comps' : 'Run Comps'}
                </button>
            </div>
        </div>
        <div class="card-body">
            <!-- Estimated Value Section -->
            <div id="estimatedValueSection" style="display: none;">
                <div class="alert alert-info mb-4">
                    <div class="row align-items-center">
                        <div class="col-12 col-md-4 mb-3 mb-md-0">
                            <h6 class="mb-0">Estimated Value:</h6>
                            <h4 class="mb-0" id="estimatedValue">$0</h4>
                        </div>
                        <div class="col-12 col-md-8">
                            <h6 class="mb-0">Value Range:</h6>
                            <div class="d-flex align-items-center">
                                <span id="valueLow" class="h5 mb-0">$0</span>
                                <div class="mx-3 flex-grow-1">
                                    <div class="progress">
                                        <div class="progress-bar bg-success" role="progressbar" style="width: 100%"></div>
                                    </div>
                                </div>
                                <span id="valueHigh" class="h5 mb-0">$0</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Comps Table Section -->
            <div id="compsTableSection" style="display: none;">
                <div class="table-responsive">
                    <table class="table table-bordered table-hover">
                        <thead class="table-light">
                            <tr>
                                <th>Address</th>
                                <th>Price</th>
                                <th>Bed/Bath</th>
                                <th>Sq Ft</th>
                                <th>Year Built</th>
                                <th>Date Sold</th>
                                <th>Distance</th>
                            </tr>
                        </thead>
                        <tbody id="compsTableBody">
                            <!-- Comps will be inserted here -->
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Initial State Message -->
            <div id="initialCompsMessage" class="text-center py-4" ${hasExistingComps ? 'style="display: none;"' : ''}>
                <p class="text-muted mb-0">Click "${hasExistingComps ? 'Re-Run Comps' : 'Run Comps'}" to fetch comparable properties</p>
            </div>

            <!-- Loading State -->
            <div id="compsLoading" class="text-center py-4" style="display: none;">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2 mb-0">Fetching comparable properties...</p>
            </div>

            <!-- Error State -->
            <div id="compsError" class="alert alert-danger mb-0" style="display: none;">
                <i class="bi bi-exclamation-triangle me-2"></i>
                <span id="compsErrorMessage">Error fetching comps</span>
            </div>

            <!-- No Comps Found State -->
            <div id="noCompsFound" class="alert alert-warning mb-0" style="display: none;">
                <i class="bi bi-info-circle me-2"></i>
                No comparable properties found within the search criteria
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

    // KPI Metrics Configuration
    KPI_CONFIGS: {
        'Multi-Family': {
            'noi': {
                'label': 'Net Operating Income (per unit)',
                'min': 0,
                'max': 2000,
                'threshold': 800,
                'direction': 'min',
                'format': 'money',
                'info': 'Monthly NOI should be at least $800 per unit. Higher is better.'
            },
            'operatingExpenseRatio': {
                'label': 'Operating Expense Ratio',
                'min': 0,
                'max': 100,
                'threshold': 40,
                'direction': 'max',
                'format': 'percentage',
                'info': 'Operating expenses should be at most 40% of income. Lower is better.'
            },
            'capRate': {
                'label': 'Cap Rate',
                'min': 3,
                'max': 12,
                'goodMin': 5,
                'goodMax': 10,
                'format': 'percentage',
                'info': '5-10% indicates good value for multi-family.'
            },
            'dscr': {
                'label': 'Debt Service Coverage Ratio',
                'min': 0,
                'max': 3,
                'threshold': 1.25,
                'direction': 'min',
                'format': 'ratio',
                'info': 'DSCR should be at least 1.25. Higher is better.'
            },
            'cashOnCash': {
                'label': 'Cash-on-Cash Return',
                'min': 0,
                'max': 30,
                'threshold': 10,
                'direction': 'min',
                'format': 'percentage',
                'info': 'Cash-on-Cash return should be at least 10%. Higher is better.'
            }
        },
        'LTR': {
            'noi': {
                'label': 'Net Operating Income (monthly)',
                'min': 0,
                'max': 2000,
                'threshold': 800,
                'direction': 'min',
                'format': 'money',
                'info': 'Monthly NOI should be at least $800. Higher is better.'
            },
            'operatingExpenseRatio': {
                'label': 'Operating Expense Ratio',
                'min': 0,
                'max': 100,
                'threshold': 40,
                'direction': 'max',
                'format': 'percentage',
                'info': 'Operating expenses should be at most 40% of income. Lower is better.'
            },
            'capRate': {
                'label': 'Cap Rate',
                'min': 4,
                'max': 14,
                'goodMin': 6,
                'goodMax': 12,
                'format': 'percentage',
                'info': '6-12% indicates good value for long-term rentals.'
            },
            'dscr': {
                'label': 'Debt Service Coverage Ratio',
                'min': 0,
                'max': 3,
                'threshold': 1.25,
                'direction': 'min',
                'format': 'ratio',
                'info': 'DSCR should be at least 1.25. Higher is better.'
            },
            'cashOnCash': {
                'label': 'Cash-on-Cash Return',
                'min': 0,
                'max': 30,
                'threshold': 10,
                'direction': 'min',
                'format': 'percentage',
                'info': 'Cash-on-Cash return should be at least 10%. Higher is better.'
            }
        },
        'BRRRR': {
            'noi': {
                'label': 'Net Operating Income (monthly)',
                'min': 0,
                'max': 2000,
                'threshold': 800,
                'direction': 'min',
                'format': 'money',
                'info': 'Monthly NOI should be at least $800. Higher is better.'
            },
            'operatingExpenseRatio': {
                'label': 'Operating Expense Ratio',
                'min': 0,
                'max': 100,
                'threshold': 40,
                'direction': 'max',
                'format': 'percentage',
                'info': 'Operating expenses should be at most 40% of income. Lower is better.'
            },
            'capRate': {
                'label': 'Cap Rate',
                'min': 5,
                'max': 15,
                'goodMin': 7,
                'goodMax': 12,
                'format': 'percentage',
                'info': '7-12% indicates good value for BRRRR strategy.'
            },
            'dscr': {
                'label': 'Debt Service Coverage Ratio',
                'min': 0,
                'max': 3,
                'threshold': 1.25,
                'direction': 'min',
                'format': 'ratio',
                'info': 'DSCR should be at least 1.25. Higher is better.'
            },
            'cashOnCash': {
                'label': 'Cash-on-Cash Return',
                'min': 0,
                'max': 30,
                'threshold': 10,
                'direction': 'min',
                'format': 'percentage',
                'info': 'Cash-on-Cash return should be at least 10%. Higher is better.'
            }
        },
        'Lease Option': {
            'noi': {
                'label': 'Net Operating Income (monthly)',
                'min': 0,
                'max': 2000,
                'threshold': 800,
                'direction': 'min',
                'format': 'money',
                'info': 'Monthly NOI should be at least $800. Higher is better.'
            },
            'operatingExpenseRatio': {
                'label': 'Operating Expense Ratio',
                'min': 0,
                'max': 100,
                'threshold': 40,
                'direction': 'max',
                'format': 'percentage',
                'info': 'Operating expenses should be at most 40% of income. Lower is better.'
            },
            'cashOnCash': {
                'label': 'Cash-on-Cash Return',
                'min': 0,
                'max': 30,
                'threshold': 10,
                'direction': 'min',
                'format': 'percentage',
                'info': 'Cash-on-Cash return should be at least 10%. Higher is better.'
            }
        }
    },

    // Make sure init is directly on the module object
    async init() {
        console.log('Analysis module initializing');
        try {
            // Inject styles first
            this.injectStyles();
            
            // Make compsHandler available globally
            window.compsHandler = compsHandler;
            
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
                    // Initialize comps handler with the analysis ID
                    compsHandler.init(analysisId);
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
                            
                            // Initialize comps handler if analysis data exists
                            if (analysisData.id) {
                                console.log('Initializing comps handler for analysis:', analysisData.id);
                                window.compsHandler.init(analysisData.id);
                            }
                        } catch (error) {
                            console.error('Error parsing analysis data:', error);
                        }
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
            } else {
                // Check if we're on a view-only page that might need comps
                const analysisDataElement = document.getElementById('analysis-data');
                if (analysisDataElement) {
                    try {
                        const analysisData = JSON.parse(analysisDataElement.textContent);
                        if (analysisData.id) {
                            console.log('Initializing comps handler for view-only analysis:', analysisData.id);
                            window.compsHandler.init(analysisData.id);
                        }
                    } catch (error) {
                        console.error('Error parsing analysis data for comps:', error);
                    }
                }
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
        
        if (!analysisType || !financialTab) {
            console.error('Missing required elements');
            return;
        }
    
        // Remove existing event listeners by cloning
        const newAnalysisType = analysisType.cloneNode(true);
        analysisType.parentNode.replaceChild(newAnalysisType, analysisType);
        
        // Get analysis ID from URL if it exists
        const urlParams = new URLSearchParams(window.location.search);
        const analysisId = urlParams.get('analysis_id');
        console.log('AnalysisId in type handler:', analysisId);
        
        // Store initial value
        this.initialAnalysisType = analysisId ? null : newAnalysisType.value;
        console.log('Initial analysis type:', this.initialAnalysisType);
        
        // Load initial template if not editing existing analysis
        if (!analysisId) {
            console.log('Loading initial template for type:', this.initialAnalysisType);
            if (this.initialAnalysisType === 'Multi-Family') {
                console.log('Loading Multi-Family template');
                financialTab.innerHTML = getMultiFamilyHTML();
                setTimeout(() => {
                    console.log('Initializing Multi-Family handlers');
                    this.initMultiFamilyHandlers();
                }, 0);
            } else {
                this.loadTemplateForType(this.initialAnalysisType, financialTab);
            }
        }
            
        // Set up event listener for changes
        newAnalysisType.addEventListener('change', async (e) => {
            console.log('Analysis type change detected:', {
                newType: e.target.value,
                isPadSplit: e.target.value.includes('PadSplit'),
                padSplitFields: document.querySelectorAll('.padsplit-field')
            });
            if (this.typeChangeInProgress) {
                console.log('Type change already in progress');
                return;
            }
        
            const newType = e.target.value;
            console.log('Processing change to type:', newType);
            
            // Add PadSplit field handling
            const isPadSplit = newType.includes('PadSplit');
            const padSplitFields = document.querySelectorAll('.padsplit-field');
            
            padSplitFields.forEach(field => {
                field.style.display = isPadSplit ? 'block' : 'none';
                const inputs = field.querySelectorAll('input');
                inputs.forEach(input => {
                    input.required = isPadSplit;
                    if (!isPadSplit) {
                        input.value = '';
                    }
                });
            });
            
            // Skip if initial type hasn't been set yet or if type hasn't actually changed
            if (!this.initialAnalysisType || newType === this.initialAnalysisType) {
                console.log('Skipping - no initial type or no change');
                return;
            }
            
            // Handle Multi-Family type change immediately
            if (newType === 'Multi-Family') {
                console.log('Loading Multi-Family template');
                financialTab.innerHTML = getMultiFamilyHTML();
                setTimeout(() => {
                    console.log('Initializing Multi-Family handlers');
                    this.initMultiFamilyHandlers();
                }, 0);
                this.initialAnalysisType = newType;
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
    },

    debugPropertyType(message, data = {}) {
        console.log(`[Property Type Debug] ${message}`, data);
    },
    
    // Modified property type initialization
    initPropertyTypeHandler(analysis = null) {
        this.debugPropertyType('Initializing property type handler', { analysis });
        
        const analysisType = document.getElementById('analysis_type');
        const propertyType = document.getElementById('property_type');
        
        if (!analysisType || !propertyType) {
            this.debugPropertyType('Required elements not found', { 
                analysisType: !!analysisType, 
                propertyType: !!propertyType 
            });
            return;
        }
    
        // Function to manage property type options
        const updatePropertyTypeOptions = (type, savedPropertyType = null) => {
            this.debugPropertyType('Updating property type options', { 
                type, 
                savedPropertyType 
            });
            
            // First, reset to default options
            propertyType.innerHTML = `
                <option value="">Select Property Type</option>
                <option value="Single Family">Single Family</option>
                <option value="Condo">Condo</option>
                <option value="Townhouse">Townhouse</option>
                <option value="Manufactured">Manufactured</option>
            `;
            
            // Handle Multi-Family case
            if (type === 'Multi-Family') {
                propertyType.innerHTML = '<option value="Multi-Family">Multi-Family</option>';
                propertyType.value = 'Multi-Family';
                propertyType.disabled = true;
            } else {
                propertyType.disabled = false;
                
                // Set saved value if exists
                if (savedPropertyType) {
                    this.debugPropertyType('Setting saved property type', { savedPropertyType });
                    propertyType.value = savedPropertyType;
                }
            }
            
            this.debugPropertyType('Final property type value', { value: propertyType.value });
        };
    
        // Initial setup
        if (analysis && analysis.property_type) {
            updatePropertyTypeOptions(analysisType.value, analysis.property_type);
        } else {
            updatePropertyTypeOptions(analysisType.value);
        }
    
        // Handle analysis type changes
        analysisType.addEventListener('change', (e) => {
            updatePropertyTypeOptions(e.target.value);
        });
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

    initButtonHandlers() {
        const reEditButton = document.getElementById('reEditButton');
        if (reEditButton) {
            reEditButton.addEventListener('click', () => {
                this.switchToFinancialTab();
            });
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
    
    // In the loadTemplateForType function:
    loadTemplateForType(type, container) {
        console.log('loadTemplateForType called with type:', type);
        
        if (!container) {
            console.error('No container provided to loadTemplateForType');
            return;
        }
        
        try {
            // Clear existing content
            container.innerHTML = '';
            
            // Get appropriate template based on type
            let template;
            const isPadSplit = type.includes('PadSplit');

            switch(type) {
                case 'Multi-Family':
                    console.log('Using Multi-Family template');
                    template = getMultiFamilyHTML();
                    break;
                case 'Lease Option':
                    console.log('Using Lease Option template');
                    template = getLeaseOptionHTML();
                    break;
                case 'BRRRR':
                case 'PadSplit BRRRR':
                    console.log('Using BRRRR template');
                    template = getBRRRRHTML();
                    break;
                default:
                    console.log('Using LTR template');
                    template = getLongTermRentalHTML();
            }
            
            // Apply template
            container.innerHTML = template;
            console.log('Template applied successfully');

            setTimeout(() => {
                this.initPropertyTypeHandler();
            }, 0);

            // Handle PadSplit fields visibility
            console.log('Checking PadSplit fields for type:', type);
            const padSplitFields = container.querySelectorAll('.padsplit-field');
            console.log('Found PadSplit fields:', padSplitFields.length);
            
            padSplitFields.forEach(field => {
                field.style.display = isPadSplit ? 'block' : 'none';
                const inputs = field.querySelectorAll('input');
                inputs.forEach(input => {
                    input.required = isPadSplit;
                    if (!isPadSplit) {
                        input.value = '';
                    }
                });
            });
            
            // Initialize appropriate handlers
            if (type === 'Multi-Family') {
                console.log('Initializing Multi-Family handlers');
                setTimeout(() => {
                    this.initMultiFamilyHandlers();
                }, 0);
            } else {
                if (!type.includes('BRRRR')) {
                    setTimeout(() => {
                        this.initBalloonPaymentHandlers();
                    }, 0);
                }
                this.initLoanHandlers();
                if (type.includes('BRRRR')) {
                    this.initRefinanceCalculations();
                }
            }
            
            // Add PadSplit expenses if needed
            if (type.includes('PadSplit')) {
                console.log('Adding PadSplit expenses');
                container.insertAdjacentHTML('beforeend', padSplitExpensesHTML);
            }
            
            this.initNotesCounter();
            
        } catch (error) {
            console.error('Error in loadTemplateForType:', error);
            console.error(error.stack);
            throw error;
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
    
        // Get elements
        const balloonToggle = document.getElementById('has_balloon_payment');
        const balloonDetails = document.getElementById('balloon-payment-details');
        const analysisType = document.getElementById('analysis_type')?.value;
        
        // Debug log the elements we found
        console.log('Found elements:', {
            balloonToggle: !!balloonToggle,
            balloonDetails: !!balloonDetails,
            analysisType
        });
        
        // Only proceed for LTR analyses
        if (!analysisType?.includes('LTR')) {
            console.log('Balloon payments not applicable for', analysisType);
            return;
        }

        // If elements don't exist and this is an LTR analysis, retry
        if (!balloonToggle || !balloonDetails) {
            if (!skipToggleInit) {
                console.log('Balloon payment elements not found - will retry in 100ms');
                setTimeout(() => initBalloonPaymentHandlers(true), 100);
            } else {
                console.error('Failed to find balloon payment elements after retry');
            }
            return;
        }

        // Remove any existing event listeners
        const newToggle = balloonToggle.cloneNode(true);
        balloonToggle.parentNode.replaceChild(newToggle, balloonToggle);
        
        // Set initial state
        console.log('Setting initial state...');
        if (newToggle.checked) {
            balloonDetails.style.display = 'block';
            const balloonInputs = balloonDetails.querySelectorAll('input:not([type="checkbox"])');
            balloonInputs.forEach(input => {
                input.required = true;
            });
        } else {
            this.clearBalloonPaymentFields();
            balloonDetails.style.display = 'none';
        }

        // Add event listener to toggle
        newToggle.addEventListener('change', (e) => {
            console.log('Balloon toggle changed:', e.target.checked);
            
            // Toggle display with animation
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
                    // Clear fields when hiding
                    this.clearBalloonPaymentFields();
                }, 300);
            }
            
            // Toggle required fields
            const balloonInputs = balloonDetails.querySelectorAll('input:not([type="checkbox"])');
            balloonInputs.forEach(input => {
                input.required = e.target.checked;
            });
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

    getAnalysisIdFromUrl() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('analysis_id');
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
                        
                        // Load appropriate template
                        console.log('Loading template for type:', this.initialAnalysisType);
                        if (this.initialAnalysisType === 'Multi-Family') {
                            console.log('Setting Multi-Family template');
                            financialTab.innerHTML = getMultiFamilyHTML();
                            setTimeout(() => {
                                this.initMultiFamilyHandlers();
                                this.populateFormFields(data.analysis);
                            }, 100);
                        } else {
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
                            if (!this.initialAnalysisType.includes('BRRRR')) {
                                this.initBalloonPaymentHandlers();
                            }
                            this.initLoanHandlers();
                            if (this.initialAnalysisType.includes('BRRRR')) {
                                this.initRefinanceCalculations();
                            }
                            
                            // Wait for DOM to be ready before populating fields
                            setTimeout(() => {
                                this.populateFormFields(data.analysis);
                            }, 100);
                        }
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

    handleTypeChange(newType) {
        const financialTab = document.getElementById('financial');
        if (!financialTab) return;
        
        try {
            // Get current form data
            const currentForm = document.getElementById('analysisForm');
            const analysisId = currentForm.getAttribute('data-analysis-id');
            if (!analysisId) return;
    
            // Create new analysis data
            const formData = new FormData(currentForm);
            const analysisData = {
                ...Object.fromEntries(formData.entries()),
                id: analysisId,
                analysis_type: newType
            };
            
            // Make API call
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
                if (data.success) {
                    // Update form with new template
                    if (newType === 'Multi-Family') {
                        financialTab.innerHTML = getMultiFamilyHTML();
                        this.initMultiFamilyHandlers();
                    } else if (newType.includes('BRRRR')) {
                        financialTab.innerHTML = getBRRRRHTML();
                    } else {
                        financialTab.innerHTML = getLongTermRentalHTML();
                    }
    
                    // Add PadSplit expenses if needed
                    if (newType.includes('PadSplit')) {
                        financialTab.insertAdjacentHTML('beforeend', padSplitExpensesHTML);
                    }
    
                    // Initialize appropriate handlers
                    if (!newType.includes('BRRRR') && newType !== 'Multi-Family') {
                        this.initBalloonPaymentHandlers();
                    }
                    if (newType !== 'Multi-Family') {
                        this.initLoanHandlers();
                    }
                    if (newType.includes('BRRRR')) {
                        this.initRefinanceCalculations();
                    }
    
                    // Update form and populate fields
                    currentForm.setAttribute('data-analysis-id', data.analysis.id);
                    this.currentAnalysisId = data.analysis.id;
                    setTimeout(() => {
                        this.populateFormFields(data.analysis);
                    }, 100);
                    
                    toastr.success(`Created new ${newType} analysis`);
                } else {
                    throw new Error(data.message || 'Error creating new analysis');
                }
            });
        } catch (error) {
            console.error('Error:', error);
            toastr.error(error.message);
            throw error;
        }
    },

    // Updated handleSubmit function for flat data structure
    handleSubmit(event) {
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
    
        // First, set the analysis type
        const analysisType = formData.get('analysis_type');
        analysisData.analysis_type = analysisType;

        // Add property type handling
        const propertyType = formData.get('property_type');
        analysisData.property_type = propertyType || null;  // Allow null for backward compatibility
        
        if (analysisType === 'Multi-Family') {
            // Get unit types data
            const unitTypes = this.getUnitTypesData();
            analysisData.unit_types = JSON.stringify(unitTypes);
            
            // Don't include monthly_rent field for Multi-Family
            formData.delete('monthly_rent');
        }
        
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
    
        // Handle PadSplit furnishing costs
        if (analysisType.includes('PadSplit')) {
            const furnishingCosts = formData.get('furnishing_costs');
            analysisData.furnishing_costs = furnishingCosts ? this.toRawNumber(furnishingCosts) : 0;
        } else {
            analysisData.furnishing_costs = 0;
        }
    
        // Log data before sending
        if (analysisType === 'Multi-Family') {
            console.log('Sending Multi-Family data:', {
                analysisData,
                unitTypes: JSON.parse(analysisData.unit_types)
            });
        }
    
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
                console.log('Analysis updated, initializing UI components...');
                
                // Store the analysis ID first
                this.currentAnalysisId = data.analysis.id;
                console.log('Analysis ID set to:', this.currentAnalysisId);
                
                // Make sure we have the required data
                if (!data.analysis.calculated_metrics) {
                    console.warn('No calculated metrics in response:', data.analysis);
                }
                
                // Populate reports and switch tabs
                this.populateReportsTab(data.analysis);
                this.switchToReportsTab();
                this.showReportActions();
                
                // Initialize comps handler only after we have the ID
                if (this.currentAnalysisId && typeof compsHandler.init === 'function') {
                    const initResult = compsHandler.init(this.currentAnalysisId);
                    console.log('Comps handler initialization result:', initResult);
                }
                
                toastr.success('Analysis updated successfully');
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

    // Updated handleEditSubmit function for flat schema
    handleEditSubmit: async function(event, analysisId) {
        event.preventDefault();
        
        if (this.isSubmitting) {
            console.log('Form submission already in progress');
            return;
        }
        
        const form = event.target;
        let submitBtn = null;
        let existingComps = null;  // Store comps data at this scope
        
        try {
            this.isSubmitting = true;
            
            if (!analysisId) {
                console.error('No analysis ID provided for update');
                toastr.error('Missing analysis ID');
                return;
            }
    
            this.currentAnalysisId = analysisId;
            console.log('Set currentAnalysisId to:', this.currentAnalysisId);
            
            submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Updating...';
            }
    
            if (!this.validateForm(form)) {
                throw new Error('Form validation failed');
            }
    
            // Get form data
            const formData = new FormData(form);
            const currentAnalysisType = formData.get('analysis_type');
            const originalAnalysisType = this.initialAnalysisType;
    
            // Get current analysis data
            console.log('Fetching current analysis to preserve comps data');
            const currentResponse = await fetch(`/analyses/get_analysis/${analysisId}`);
            if (!currentResponse.ok) {
                throw new Error('Failed to fetch current analysis data');
            }
            const currentData = await currentResponse.json();
            existingComps = currentData.analysis?.comps_data;
            console.log('Retrieved existing comps:', existingComps);
    
            // Create base request data
            const requestData = {
                id: analysisId,
                comps_data: existingComps  // Include existing comps
            };
    
            // Add property type handling
            const propertyType = formData.get('property_type');
            requestData.property_type = propertyType || null;
    
            // Handle Multi-Family unit types
            if (currentAnalysisType === 'Multi-Family') {
                const unitTypes = [];
                let totalPotentialRent = 0;
                
                document.querySelectorAll('.unit-type-section').forEach(section => {
                    const count = parseInt(section.querySelector('.unit-count').value) || 0;
                    const rent = parseFloat(section.querySelector('.unit-rent').value) || 0;
                    totalPotentialRent += count * rent;
                    
                    unitTypes.push({
                        type: section.querySelector('select').value || '',
                        count: count,
                        occupied: parseInt(section.querySelector('.unit-occupied').value) || 0,
                        square_footage: parseInt(section.querySelector('input[name$="[square_footage]"]').value) || 0,
                        rent: rent
                    });
                });
                
                requestData.unit_types = JSON.stringify(unitTypes);
                requestData.monthly_rent = totalPotentialRent;
            }
    
            // Set balloon payment flag
            const hasBalloon = form.querySelector('#has_balloon_payment')?.checked || false;
            requestData.has_balloon_payment = hasBalloon;
    
            // Process each form field
            formData.forEach((value, key) => {
                if (key === 'has_balloon_payment') {
                    return; // Skip as we've already handled this
                }
                
                // Handle balloon payment fields
                if (key.startsWith('balloon_')) {
                    if (!hasBalloon) {
                        // If balloon payments are disabled, set all balloon fields to null or 0
                        if (key === 'balloon_due_date') {
                            requestData[key] = null;
                        } else {
                            requestData[key] = 0;
                        }
                        return;
                    }
                }
                
                // Normal field processing
                if (key.endsWith('_interest_only')) {
                    const checkbox = form.querySelector(`#${key}`);
                    requestData[key] = checkbox ? checkbox.checked : false;
                } else if (key === 'balloon_due_date' && value && hasBalloon) {
                    requestData[key] = new Date(value).toISOString().split('T')[0];
                } else if (key.endsWith('_percentage') || this.isNumericField(key)) {
                    requestData[key] = value === '' ? 0 : this.toRawNumber(value);
                } else if (key === 'bathrooms') {
                    requestData[key] = this.toRawNumber(value);
                } else {
                    requestData[key] = value || null;
                }
            });
    
            // Handle PadSplit furnishing costs
            if (currentAnalysisType.includes('PadSplit')) {
                const furnishingCosts = formData.get('furnishing_costs');
                requestData.furnishing_costs = furnishingCosts ? this.toRawNumber(furnishingCosts) : 0;
            } else {
                requestData.furnishing_costs = 0;
            }
    
            // Set create_new flag if analysis type has changed
            if (currentAnalysisType !== originalAnalysisType) {
                requestData.create_new = true;
            }
    
            console.log('Sending request data:', requestData);
    
            // Make API call
            const response = await fetch('/analyses/update_analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Error updating analysis');
            }

            const responseData = await response.json();
            
            if (!responseData.success) {
                throw new Error(responseData.message || 'Unknown error occurred');
            }

            console.log('Update successful:', responseData);
            
            // Get the analysis data and ensure comps are preserved
            let updatedAnalysis = responseData.analysis || responseData;
            if (!updatedAnalysis.comps_data && existingComps) {
                console.log('Restoring comps data from original analysis');
                updatedAnalysis = {
                    ...updatedAnalysis,
                    comps_data: existingComps
                };
            }
            
            // Keep using the original analysis ID if not in response
            this.currentAnalysisId = updatedAnalysis.id || analysisId;
            console.log('Using analysis ID:', this.currentAnalysisId);

            // After updating display
            await this.populateReportsTab(updatedAnalysis);
            this.switchToReportsTab();
            this.showReportActions();

            // Initialize comps handler
            await new Promise(resolve => setTimeout(resolve, 250));

            if (this.currentAnalysisId) {
                console.log('Initializing comps handler for analysis:', this.currentAnalysisId);
                if (!window.compsHandler?.init) {
                    console.error('Comps handler not available');
                    throw new Error('Comps handler not available');
                }

                const success = window.compsHandler.init(this.currentAnalysisId);
                if (!success) {
                    console.error('Failed to initialize comps handler');
                    throw new Error('Comps handler initialization failed');
                }

                console.log('Comps handler initialized successfully');
            } else {
                throw new Error('No analysis ID available for comps handler');
            }

            toastr.success('Analysis updated successfully');

        } catch (error) {
            console.error('Error in handleEditSubmit:', error);
            if (error.response) {
                console.error('Response error:', await error.response.text());
            }
            toastr.error(error.message || 'Error updating analysis');
        } finally {
            this.isSubmitting = false;
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="bi bi-save me-2"></i>Update Analysis';
            }
        }
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

    // Updated populateFormFields function - uses raw values
    populateFormFields(analysis) {
        // Store reference to 'this' for use in nested functions
        const self = this;
        
        self.debugPropertyType('Starting form population', { analysis });
        
        try {
            // Define setFieldValue with proper 'this' context first
            const setFieldValue = (fieldId, value) => {
                const field = document.getElementById(fieldId);
                if (field) {
                    self.debugPropertyType(`Setting field ${fieldId}`, { value });
                    
                    // Skip property type as it's handled separately
                    if (fieldId === 'property_type') {
                        return true;
                    }
                    
                    if (field.type === 'checkbox') {
                        field.checked = Boolean(value);
                    } else {
                        field.value = (value !== null && value !== undefined) ? value : '';
                    }
                    
                    const event = new Event('change', { bubbles: true });
                    field.dispatchEvent(event);
                    return true;
                }
                return false;
            };
    
            // Set analysis type first
            setFieldValue('analysis_type', analysis.analysis_type);
            
            // Initialize property type handler with a delay
            setTimeout(() => {
                self.initPropertyTypeHandler(analysis);
            }, 100);
    
            // Basic fields
            setFieldValue('analysis_name', analysis.analysis_name);
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
    
            // Handle Multi-Family specific fields
            if (analysis.analysis_type === 'Multi-Family') {
                try {
                    // Set basic Multi-Family fields
                    setFieldValue('total_units', analysis.total_units);
                    setFieldValue('occupied_units', analysis.occupied_units);
                    setFieldValue('floors', analysis.floors);
                    setFieldValue('other_income', analysis.other_income);
                    setFieldValue('total_potential_income', analysis.total_potential_income);
                    
                    // Set Multi-Family specific expenses
                    setFieldValue('common_area_maintenance', analysis.common_area_maintenance);
                    setFieldValue('elevator_maintenance', analysis.elevator_maintenance);
                    setFieldValue('staff_payroll', analysis.staff_payroll);
                    setFieldValue('trash_removal', analysis.trash_removal);
                    setFieldValue('common_utilities', analysis.common_utilities);
                    
                    // Handle unit types
                    const unitTypesContainer = document.getElementById('unit-types-container');
                    if (unitTypesContainer) {
                        // Clear existing unit types
                        unitTypesContainer.innerHTML = '';
                        
                        // Parse unit types from stored JSON string
                        const unitTypes = JSON.parse(analysis.unit_types || '[]');
                        
                        // Add each unit type
                        unitTypes.forEach((unitType, index) => {
                            unitTypesContainer.insertAdjacentHTML('beforeend', getUnitTypeHTML(index));
                            
                            // Set values for this unit type
                            const section = unitTypesContainer.children[index];
                            if (section) {
                                section.querySelector('select').value = unitType.type;
                                section.querySelector('.unit-count').value = unitType.count;
                                section.querySelector('.unit-occupied').value = unitType.occupied;
                                section.querySelector('input[name$="[square_footage]"]').value = unitType.square_footage;
                                section.querySelector('.unit-rent').value = unitType.rent;
                            }
                        });
                        
                        // Initialize calculations
                        self.initUnitTypeCalculations();
                    }
                    
                } catch (error) {
                    console.error('Error populating Multi-Family fields:', error);
                    toastr.error('Error loading Multi-Family data');
                }
            }
    
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
            }
    
            // Handle balloon payment configuration
            const hasBalloon = analysis.has_balloon_payment || (
                analysis.balloon_refinance_loan_amount > 0 && 
                analysis.balloon_due_date && 
                analysis.balloon_refinance_ltv_percentage > 0
            );
    
            // Set balloon toggle state
            const balloonToggle = document.getElementById('has_balloon_payment');
            const balloonDetails = document.getElementById('balloon-payment-details');
            
            if (balloonToggle && balloonDetails) {
                balloonToggle.checked = hasBalloon;
                if (hasBalloon) {
                    balloonDetails.style.display = 'block';
                    const balloonInputs = balloonDetails.querySelectorAll('input:not([type="checkbox"])');
                    balloonInputs.forEach(input => {
                        input.required = true;
                    });
                } else {
                    balloonDetails.style.display = 'none';
                    self.clearBalloonPaymentFields();
                }
            }
    
            // Set balloon payment fields if enabled
            if (hasBalloon) {
                setFieldValue('balloon_due_date', analysis.balloon_due_date);
                setFieldValue('balloon_refinance_ltv_percentage', analysis.balloon_refinance_ltv_percentage);
                setFieldValue('balloon_refinance_loan_amount', analysis.balloon_refinance_loan_amount);
                setFieldValue('balloon_refinance_loan_interest_rate', analysis.balloon_refinance_loan_interest_rate);
                setFieldValue('balloon_refinance_loan_term', analysis.balloon_refinance_loan_term);
                setFieldValue('balloon_refinance_loan_down_payment', analysis.balloon_refinance_loan_down_payment);
                setFieldValue('balloon_refinance_loan_closing_costs', analysis.balloon_refinance_loan_closing_costs);
            }
    
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
                        const interestOnlyCheckbox = document.getElementById(`${prefix}_interest_only`);
                        if (interestOnlyCheckbox) {
                            // Convert the value to boolean and set it
                            interestOnlyCheckbox.checked = Boolean(analysis[`${prefix}_interest_only`]);
                            // Dispatch change event to trigger any listeners
                            interestOnlyCheckbox.dispatchEvent(new Event('change', { bubbles: true }));
                            console.log(`Setting ${prefix}_interest_only to:`, Boolean(analysis[`${prefix}_interest_only`]));
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
    
            // Handle PadSplit-specific fields visibility
            if (analysis.analysis_type?.includes('PadSplit')) {
                setFieldValue('furnishing_costs', analysis.furnishing_costs || 0);
                document.querySelectorAll('.padsplit-field').forEach(field => {
                    field.style.display = 'block';
                    field.querySelectorAll('input').forEach(input => {
                        input.required = true;
                    });
                });
            } else {
                document.querySelectorAll('.padsplit-field').forEach(field => {
                    field.style.display = 'none';
                    field.querySelectorAll('input').forEach(input => {
                        input.required = false;
                        input.value = '';
                    });
                });
            }
    
            // Initialize balloon payment handlers after setting all values
            self.initBalloonPaymentHandlers(true);  // Pass true to skip toggle init
            
        } catch (error) {
            console.error('Error populating form fields:', error);
            toastr.error('Error populating form fields');
        }
    },

    // Updated populateReportsTab function - applies formatting for display
    populateReportsTab(data) {
        console.log('Starting populateReportsTab with data:', data);
        
        // Ensure we have analysis data
        const analysisData = data.analysis || data;
        if (!analysisData) {
            console.error('No analysis data provided to populateReportsTab');
            return;
        }
    
        // Initialize empty comps data if not present
        if (!analysisData.comps_data) {
            analysisData.comps_data = {
                comparables: [],
                run_count: 0
            };
        }
        
        console.log('Checking for comps data:', analysisData.comps_data);
    
        // Check for existing comps
        const hasExistingComps = analysisData.comps_data && 
                                Array.isArray(analysisData.comps_data.comparables) && 
                                analysisData.comps_data.comparables.length > 0;
                                
        console.log('Has existing comps:', hasExistingComps);
        if (hasExistingComps) {
            console.log('Existing comps:', analysisData.comps_data.comparables);
        }
    
        // Get your report content
        let reportContent = '';
        const analysisType = analysisData.analysis_type || '';
        
        // Generate appropriate report content based on type
        switch(analysisType) {
            case 'Multi-Family':
                reportContent = this.getMultiFamilyReportContent(analysisData);
                break;
            case 'BRRRR':
                reportContent = this.getBRRRRReportContent(analysisData);
                break;
            case 'Lease Option':
                reportContent = this.getLeaseOptionReportContent(analysisData);
                break;
            default:
                reportContent = this.getLTRReportContent(analysisData);
        }
    
        // Add comps section
        const compsHtml = getCompsHTML(hasExistingComps);
        
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
            ${reportContent}
            ${compsHtml}`;
    
        // Update the DOM
        const reportsContent = document.querySelector('#reports');
        if (reportsContent) {
            reportsContent.innerHTML = finalContent;
            
            // If we have comps data and compsHandler is available, reinitialize it
            if (hasExistingComps && window.compsHandler) {
                window.compsHandler.displayExistingComps(analysisData.comps_data);
            }
            
            // Attach event handler after content is added
            const reEditButton = reportsContent.querySelector('#reEditButton');
            if (reEditButton) {
                reEditButton.addEventListener('click', () => this.switchToFinancialTab());
            }
        }
    },

    // Add this helper method to display existing comps
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
    },
    
    // Calculate KPIs
    calculateOperatingExpenseRatio(analysis) {
        const grossIncome = parseFloat(analysis.total_potential_income) || 0;
        if (!grossIncome) return 0;
        
        const expenses = [
            'property_taxes',
            'insurance',
            'common_area_maintenance',
            'elevator_maintenance',
            'staff_payroll',
            'trash_removal',
            'common_utilities'
        ].reduce((total, field) => total + (parseFloat(analysis[field]) || 0), 0);
    
        // Add percentage-based expenses
        const managementFee = grossIncome * (analysis.management_fee_percentage || 0) / 100;
        const repairs = grossIncome * (analysis.repairs_percentage || 0) / 100;
        const capex = grossIncome * (analysis.capex_percentage || 0) / 100;
        
        const totalExpenses = expenses + managementFee + repairs + capex;
        return (totalExpenses * 12 / (grossIncome * 12)) * 100;
    },
    
    calculateDSCR(analysis) {
        // Calculate NOI
        const annualNOI = parseFloat(analysis.calculated_metrics?.annual_noi) || 0;
        if (!annualNOI) return 0;
        
        // Calculate annual debt service
        let annualDebtService = 0;
        ['loan1', 'loan2', 'loan3'].forEach(prefix => {
            const payment = analysis.calculated_metrics?.[`${prefix}_loan_payment`];
            if (payment) {
                annualDebtService += parseFloat(payment.replace(/[^0-9.-]+/g, '')) * 12;
            }
        });
    
        return annualDebtService ? annualNOI / annualDebtService : 0;
    },

    // Add Multi-Family report content generator
    getMultiFamilyReportContent(analysis) {
        console.log('Generating Multi-Family report with data:', analysis);
    
        try {
            // Parse unit types
            const unitTypes = JSON.parse(analysis.unit_types || '[]');
            const metrics = analysis.calculated_metrics || {};
    
            // Calculate gross potential rent
            const grossPotentialRent = unitTypes.reduce((total, ut) => {
                return total + (ut.count * ut.rent);
            }, 0);
    
            // Calculate gross potential income including other income
            const grossPotentialIncome = grossPotentialRent + (analysis.other_income || 0);
    
            // Calculate management fee
            const managementFeePercentage = analysis.management_fee_percentage || 0;
            const monthlyManagementFee = grossPotentialRent * (managementFeePercentage / 100);
    
            console.log('Management fee calculation:', {
                grossPotentialRent,
                managementFeePercentage,
                monthlyManagementFee
            });

            // Add debugging for KPI configuration access
            console.log('Analysis module:', this);
            console.log('KPI_CONFIGS access:', this.KPI_CONFIGS);

            // Add KPI card at the start of the content
            const kpiCard = this.generateKPICard(analysis);
            console.log('Generated KPI card:', kpiCard ? 'Success' : 'Empty');
    
            return `
                <!-- Purchase Details Card -->
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">Purchase Details</h5>
                    </div>
                    <div class="card-body">
                        <div class="list-group list-group-flush">
                            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                <span>Purchase Price</span>
                                <strong>${this.formatDisplayValue(analysis.purchase_price)}</strong>
                            </div>
                            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                <span>After Repair Value</span>
                                <strong>${this.formatDisplayValue(analysis.after_repair_value)}</strong>
                            </div>
                            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                <span>Renovation Costs</span>
                                <strong>${this.formatDisplayValue(analysis.renovation_costs)}</strong>
                            </div>
                            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                <span>Renovation Duration</span>
                                <strong>${analysis.renovation_duration} months</strong>
                            </div>
                            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                <span>Cash to Seller</span>
                                <strong>${this.formatDisplayValue(analysis.cash_to_seller)}</strong>
                            </div>
                            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                <span>Closing Costs</span>
                                <strong>${this.formatDisplayValue(analysis.closing_costs)}</strong>
                            </div>
                            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                <span>Assignment Fee</span>
                                <strong>${this.formatDisplayValue(analysis.assignment_fee)}</strong>
                            </div>
                            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                <span>Marketing Costs</span>
                                <strong>${this.formatDisplayValue(analysis.marketing_costs)}</strong>
                            </div>
                            ${analysis.analysis_type.includes('PadSplit') ? `
                                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                    <span>Furnishing Costs</span>
                                    <strong>${this.formatDisplayValue(analysis.furnishing_costs)}</strong>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
            
                <!-- Property Overview Card -->
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">Property Overview</h5>
                    </div>
                    <div class="card-body">
                        <div class="list-group list-group-flush">
                            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                <span>Property Type</span>
                                <strong>${analysis.property_type || 'Not Specified'}</strong>
                            </div>
                            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                <span>Total Units</span>
                                <strong>${analysis.total_units}</strong>
                            </div>
                            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                <span>Occupied Units</span>
                                <div class="text-end">
                                    <strong>${analysis.occupied_units}</strong>
                                    <div class="small text-muted">
                                        ${metrics.occupancy_rate || '0%'} Occupancy
                                    </div>
                                </div>
                            </div>
                            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                <span>Purchase Price</span>
                                <div class="text-end">
                                    <strong>${this.formatDisplayValue(analysis.purchase_price)}</strong>
                                    <div class="small text-muted">
                                        ${this.formatDisplayValue(metrics.price_per_unit)} per unit
                                    </div>
                                </div>
                            </div>
                            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                <span>Square Footage</span>
                                <strong>${analysis.square_footage.toLocaleString()} sq ft</strong>
                            </div>
                            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                <span>Year Built</span>
                                <strong>${analysis.year_built}</strong>
                            </div>
                        </div>
                    </div>
                </div>
    
                <!-- Financial Performance Card -->
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">Financial Performance</h5>
                    </div>
                    <div class="card-body">
                        <div class="list-group list-group-flush">
                            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                <span>Gross Potential Rent</span>
                                <strong>${metrics.gross_potential_rent}</strong>
                            </div>
                            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                <span>Other Income</span>
                                <strong>${this.formatDisplayValue(analysis.other_income)}</strong>
                            </div>
                            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                <span>Actual Gross Income</span>
                                <strong>${metrics.actual_gross_income}</strong>
                            </div>
                            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                <span class="d-flex align-items-center">
                                    Net Operating Income
                                    <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" 
                                       title="Annual NOI before debt service">
                                    </i>
                                </span>
                                <strong>${metrics.annual_noi}</strong>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- KPIs Card -->
                ${kpiCard}
    
                <!-- Unit Mix Card -->
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">Unit Mix</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-bordered table-hover">
                                <thead>
                                    <tr>
                                        <th>Type</th>
                                        <th>Units</th>
                                        <th>Occupied</th>
                                        <th>Sq Ft</th>
                                        <th>Rent</th>
                                        <th>Total Potential</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${unitTypes.map(ut => `
                                        <tr>
                                            <td>${ut.type}</td>
                                            <td>${ut.count}</td>
                                            <td>${ut.occupied}</td>
                                            <td>${ut.square_footage}</td>
                                            <td>${this.formatDisplayValue(ut.rent)}</td>
                                            <td>${this.formatDisplayValue(ut.rent * ut.count)}</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
    
                <!-- Operating Expenses Card -->
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">Operating Expenses</h5>
                    </div>
                    <div class="card-body">
                        <div class="row g-0">
                            <div class="col-12 col-md-6">
                                <div class="list-group list-group-flush">
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span>Property Taxes</span>
                                        <strong>${this.formatDisplayValue(analysis.property_taxes)}</strong>
                                    </div>
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span>Insurance</span>
                                        <strong>${this.formatDisplayValue(analysis.insurance)}</strong>
                                    </div>
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span>Common Area Maintenance</span>
                                        <strong>${this.formatDisplayValue(analysis.common_area_maintenance)}</strong>
                                    </div>
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span>Elevator Maintenance</span>
                                        <strong>${this.formatDisplayValue(analysis.elevator_maintenance)}</strong>
                                    </div>
                                </div>
                            </div>
                            <div class="col-12 col-md-6">
                                <div class="list-group list-group-flush">
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span>Staff Payroll</span>
                                        <strong>${this.formatDisplayValue(analysis.staff_payroll)}</strong>
                                    </div>
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span>Trash Removal</span>
                                        <strong>${this.formatDisplayValue(analysis.trash_removal)}</strong>
                                    </div>
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span>Common Utilities</span>
                                        <strong>${this.formatDisplayValue(analysis.common_utilities)}</strong>
                                    </div>
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span>Management Fee</span>
                                        <div class="text-end">
                                            <div class="small text-muted">
                                                ${this.formatDisplayValue(managementFeePercentage, 'percentage')}
                                            </div>
                                            <strong>${this.formatDisplayValue(monthlyManagementFee)}</strong>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
    
                <!-- Financing Details Card -->
                ${this.getLoanDetailsContent(analysis)}
    
                ${this.createNotesSection(analysis.notes)}`;
    
        } catch (error) {
            console.error('Error generating Multi-Family report:', error);
            return `
                <div class="alert alert-danger">
                    Error generating report content: ${error.message}
                </div>`;
        }

        // Initialize tooltips - add this after the content is added to DOM
        setTimeout(() => {
            const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
            tooltips.forEach(tooltip => new bootstrap.Tooltip(tooltip));
        }, 0);
    },
        
    // New function for lease option report content
    getLeaseOptionReportContent(analysis) {
        // Add debugging for KPI configuration access
        console.log('Analysis module:', this);
        console.log('KPI_CONFIGS access:', this.KPI_CONFIGS);

        // Add KPI card at the start of the content
        const kpiCard = this.generateKPICard(analysis);
        console.log('Generated KPI card:', kpiCard ? 'Success' : 'Empty');
        
        return `       
            <!-- Purchase Details Card -->
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">Lease Option Details</h5>
                </div>
                <div class="card-body">
                    <div class="list-group list-group-flush">
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Purchase Price</span>
                            <strong>${this.formatDisplayValue(analysis.purchase_price)}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Strike Price</span>
                            <strong>${this.formatDisplayValue(analysis.strike_price)}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Option Fee</span>
                            <strong>${this.formatDisplayValue(analysis.option_consideration_fee)}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Option Term</span>
                            <strong>${analysis.option_term_months} months</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Monthly Rent Credit %</span>
                            <strong>${this.formatDisplayValue(analysis.monthly_rent_credit_percentage, 'percentage')}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Rent Credit Cap</span>
                            <strong>${this.formatDisplayValue(analysis.rent_credit_cap)}</strong>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Property Details Card -->
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">Property Details</h5>
                </div>
                <div class="card-body">
                    <div class="list-group list-group-flush">
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Property Type</span>
                            <strong>${analysis.property_type || 'Not Specified'}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Square Footage</span>
                            <strong>${analysis.square_footage ? analysis.square_footage.toLocaleString() + ' sq ft' : 'Not Specified'}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Lot Size</span>
                            <strong>${analysis.lot_size ? analysis.lot_size.toLocaleString() + ' sq ft' : 'Not Specified'}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Year Built</span>
                            <strong>${analysis.year_built || 'Not Specified'}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Bedrooms</span>
                            <strong>${analysis.bedrooms || 'Not Specified'}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Bathrooms</span>
                            <strong>${analysis.bathrooms || 'Not Specified'}</strong>
                        </div>
                    </div>
                </div>
            </div>
                
            <!-- KPIs Card -->
            ${kpiCard}

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
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Total Rent Credits</span>
                            <strong>${analysis.calculated_metrics?.total_rent_credits || this.formatDisplayValue(Math.min(
                                analysis.monthly_rent * (analysis.monthly_rent_credit_percentage / 100) * analysis.option_term_months,
                                analysis.rent_credit_cap
                            ))}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Effective Purchase Price</span>
                            <strong>${analysis.calculated_metrics?.effective_purchase_price || this.formatDisplayValue(
                                analysis.strike_price - Math.min(
                                    analysis.monthly_rent * (analysis.monthly_rent_credit_percentage / 100) * analysis.option_term_months,
                                    analysis.rent_credit_cap
                                )
                            )}</strong>
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

            <!-- Financing Details Card -->
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">Financing Details</h5>
                </div>
                <div class="card-body">
                    <div class="accordion" id="loanDetailsAccordion">
                        ${this.getLoanDetailsContent(analysis)}
                    </div>
                </div>
            </div>
            ${this.createNotesSection(analysis.notes)}`;
    },

    getLTRReportContent(analysis) {
        // Add debugging for KPI configuration access
        console.log('Analysis module:', this);
        console.log('KPI_CONFIGS access:', this.KPI_CONFIGS);

        // Add KPI card at the start of the content
        const kpiCard = this.generateKPICard(analysis);
        console.log('Generated KPI card:', kpiCard ? 'Success' : 'Empty');
        
        // Your existing code...
        console.log('LTR Report Data:', {
            monthlyRent: analysis.monthly_rent,
            monthlyCashFlow: analysis.calculated_metrics?.monthly_cash_flow,
            annualCashFlow: analysis.calculated_metrics?.annual_cash_flow,
            hasBalloon: this.hasBalloonData(analysis),
            fullMetrics: analysis.calculated_metrics
        });
    
        return `
            <!-- Purchase Details Card -->
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">Purchase Details</h5>
                </div>
                <div class="card-body">
                    <div class="list-group list-group-flush">
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Purchase Price</span>
                            <strong>${this.formatDisplayValue(analysis.purchase_price)}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>After Repair Value</span>
                            <strong>${this.formatDisplayValue(analysis.after_repair_value)}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Renovation Costs</span>
                            <strong>${this.formatDisplayValue(analysis.renovation_costs)}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Renovation Duration</span>
                            <strong>${analysis.renovation_duration} months</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Cash to Seller</span>
                            <strong>${this.formatDisplayValue(analysis.cash_to_seller)}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Closing Costs</span>
                            <strong>${this.formatDisplayValue(analysis.closing_costs)}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Assignment Fee</span>
                            <strong>${this.formatDisplayValue(analysis.assignment_fee)}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Marketing Costs</span>
                            <strong>${this.formatDisplayValue(analysis.marketing_costs)}</strong>
                        </div>
                        ${analysis.analysis_type.includes('PadSplit') ? `
                            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                <span>Furnishing Costs</span>
                                <strong>${this.formatDisplayValue(analysis.furnishing_costs)}</strong>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        
            <!-- Income & Returns Card -->
            <div class="card mb-4">
                <div class="card-header">
                    <div class="d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">
                            ${this.hasBalloonData(analysis) ? 'Pre-Balloon Financial Overview' : 'Income & Returns'}
                        </h5>
                        ${this.hasBalloonData(analysis) ? 
                            `<span class="badge bg-primary">Balloon Due: ${new Date(analysis.balloon_due_date).toLocaleDateString()}</span>` 
                            : ''}
                    </div>
                </div>
                <div class="card-body">
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

            <!-- KPIs Card -->
            ${kpiCard}
    
            <!-- Operating Expenses Card -->
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">
                        ${this.hasBalloonData(analysis) ? 'Pre-Balloon Operating Expenses' : 'Operating Expenses'}
                    </h5>
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
                                ${analysis.analysis_type.includes('PadSplit') ? `
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span>Utilities</span>
                                        <strong>${this.formatDisplayValue(analysis.utilities)}</strong>
                                    </div>
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span>Internet</span>
                                        <strong>${this.formatDisplayValue(analysis.internet)}</strong>
                                    </div>
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span>Cleaning</span>
                                        <strong>${this.formatDisplayValue(analysis.cleaning)}</strong>
                                    </div>
                                ` : ''}
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
                                ${analysis.analysis_type.includes('PadSplit') ? `
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span>Pest Control</span>
                                        <strong>${this.formatDisplayValue(analysis.pest_control)}</strong>
                                    </div>
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span>Landscaping</span>
                                        <strong>${this.formatDisplayValue(analysis.landscaping)}</strong>
                                    </div>
                                    <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                        <span class="d-flex align-items-center">
                                            Platform Fee
                                            <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" data-bs-html="true" 
                                            title="PadSplit platform fee based on monthly rent">
                                            </i>
                                        </span>
                                        <div class="text-end">
                                            <div class="small text-muted">
                                                ${this.formatDisplayValue(analysis.padsplit_platform_percentage, 'percentage')}
                                            </div>
                                            <strong>${this.formatDisplayValue(analysis.monthly_rent * (analysis.padsplit_platform_percentage / 100))}</strong>
                                        </div>
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Financing Details Card -->
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">Financing Details</h5>
                </div>
                <div class="card-body">
                    <div class="accordion" id="loanDetailsAccordion">
                        ${this.getLoanDetailsContent(analysis)}
                    </div>
                </div>
            </div>

            ${this.createNotesSection(analysis.notes)}`;
    },
    
    getBRRRRLoanDetails(analysis) {
        // Log BRRRR call
        console.log('Generating BRRRR loan details for analysis type:', analysis.analysis_type);
        
        // Check if we have the required loan data
        const hasInitialLoan = this.toRawNumber(analysis.initial_loan_amount) > 0;
        const hasRefinanceLoan = this.toRawNumber(analysis.refinance_loan_amount) > 0;
        
        // Get loan payment metrics - use fallback values if not in calculated_metrics
        let initialLoanPayment = '$0.00';
        let refinanceLoanPayment = '$0.00';
        
        if (analysis.calculated_metrics) {
            // Try to get values from calculated_metrics first
            initialLoanPayment = analysis.calculated_metrics.initial_loan_payment || '$0.00';
            refinanceLoanPayment = analysis.calculated_metrics.refinance_loan_payment || '$0.00';
        }
        
        // If not available in calculated_metrics, calculate them directly
        if (initialLoanPayment === '$0.00' && hasInitialLoan) {
            // Basic calculation for initial loan payment
            const loanAmount = this.toRawNumber(analysis.initial_loan_amount);
            const interestRate = this.toRawNumber(analysis.initial_loan_interest_rate) / 100 / 12; // Monthly rate
            const term = this.toRawNumber(analysis.initial_loan_term);
            
            if (analysis.initial_interest_only) {
                // Interest-only payment
                initialLoanPayment = this.formatDisplayValue(loanAmount * interestRate);
            } else if (term > 0 && interestRate > 0) {
                // Amortized payment formula: P * r * (1+r)^n / ((1+r)^n - 1)
                const payment = loanAmount * interestRate * Math.pow(1 + interestRate, term) / 
                              (Math.pow(1 + interestRate, term) - 1);
                initialLoanPayment = this.formatDisplayValue(payment);
            }
        }
        
        if (refinanceLoanPayment === '$0.00' && hasRefinanceLoan) {
            // Basic calculation for refinance loan payment
            const loanAmount = this.toRawNumber(analysis.refinance_loan_amount);
            const interestRate = this.toRawNumber(analysis.refinance_loan_interest_rate) / 100 / 12; // Monthly rate
            const term = this.toRawNumber(analysis.refinance_loan_term);
            
            if (term > 0 && interestRate > 0) {
                // Amortized payment formula: P * r * (1+r)^n / ((1+r)^n - 1)
                const payment = loanAmount * interestRate * Math.pow(1 + interestRate, term) / 
                              (Math.pow(1 + interestRate, term) - 1);
                refinanceLoanPayment = this.formatDisplayValue(payment);
            }
        }
        
        // Determine if initial loan is interest-only
        const isInitialLoanInterestOnly = analysis.initial_interest_only || false;
        
        // Check if we have any loan data
        if (!hasInitialLoan && !hasRefinanceLoan) {
            console.log('No BRRRR loan data found, showing empty message');
            return `
                <div class="text-center py-4">
                    <p class="mb-0 text-muted">No loan details available</p>
                </div>`;
        }
        
        // Build the loan details HTML
        return `
            <div class="accordion" id="brrrrLoansAccordion">
                ${hasInitialLoan ? `
                <!-- Initial Loan Section -->
                <div class="accordion-item">
                    <h6 class="accordion-header">
                        <button class="accordion-button" type="button" data-bs-toggle="collapse" 
                                data-bs-target="#initialLoanCollapse">
                            Initial Hard Money Loan
                        </button>
                    </h6>
                    <div id="initialLoanCollapse" class="accordion-collapse collapse show" 
                         data-bs-parent="#brrrrLoansAccordion">
                        <div class="accordion-body p-0">
                            <div class="list-group list-group-flush">
                                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                    <span>Amount</span>
                                    <strong>${this.formatDisplayValue(analysis.initial_loan_amount)}</strong>
                                </div>
                                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                    <span>Interest Rate</span>
                                    <div>
                                        <strong>${this.formatDisplayValue(analysis.initial_loan_interest_rate, 'percentage')}</strong>
                                        <span class="badge ${isInitialLoanInterestOnly ? 'bg-success' : 'bg-info'} ms-2">
                                            ${isInitialLoanInterestOnly ? 'Interest Only' : 'Amortized'}
                                        </span>
                                    </div>
                                </div>
                                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                    <span>Term</span>
                                    <strong>${analysis.initial_loan_term || '0'} months</strong>
                                </div>
                                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                    <span class="d-flex align-items-center">
                                        Monthly Payment
                                        <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" 
                                           title="${isInitialLoanInterestOnly ? 
                                               'Interest-only payment during renovation period' : 
                                               'Fully amortized payment including principal and interest'}"></i>
                                    </span>
                                    <strong>${initialLoanPayment}</strong>
                                </div>
                                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                    <span>Down Payment</span>
                                    <strong>${this.formatDisplayValue(analysis.initial_loan_down_payment)}</strong>
                                </div>
                                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                    <span>Closing Costs</span>
                                    <strong>${this.formatDisplayValue(analysis.initial_loan_closing_costs)}</strong>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                ` : ''}
    
                ${hasRefinanceLoan ? `
                <!-- Refinance Loan Section -->
                <div class="accordion-item">
                    <h6 class="accordion-header">
                        <button class="accordion-button ${!hasInitialLoan ? '' : 'collapsed'}" type="button" data-bs-toggle="collapse" 
                                data-bs-target="#refinanceLoanCollapse">
                            Long-term Refinance Loan
                        </button>
                    </h6>
                    <div id="refinanceLoanCollapse" class="accordion-collapse collapse ${!hasInitialLoan ? 'show' : ''}" 
                         data-bs-parent="#brrrrLoansAccordion">
                        <div class="accordion-body p-0">
                            <div class="list-group list-group-flush">
                                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                    <span>Amount</span>
                                    <strong>${this.formatDisplayValue(analysis.refinance_loan_amount)}</strong>
                                </div>
                                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                    <span>Interest Rate</span>
                                    <div>
                                        <strong>${this.formatDisplayValue(analysis.refinance_loan_interest_rate, 'percentage')}</strong>
                                        <span class="badge bg-info ms-2">Amortized</span>
                                    </div>
                                </div>
                                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                    <span>Term</span>
                                    <strong>${analysis.refinance_loan_term || '360'} months</strong>
                                </div>
                                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                    <span class="d-flex align-items-center">
                                        Monthly Payment
                                        <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" 
                                           title="Long-term refinance payment after renovation"></i>
                                    </span>
                                    <strong>${refinanceLoanPayment}</strong>
                                </div>
                                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                    <span>Down Payment</span>
                                    <strong>${this.formatDisplayValue(analysis.refinance_loan_down_payment)}</strong>
                                </div>
                                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                    <span>Closing Costs</span>
                                    <strong>${this.formatDisplayValue(analysis.refinance_loan_closing_costs)}</strong>
                                </div>
                                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                    <span>Cash Recouped</span>
                                    <strong>${analysis.calculated_metrics?.cash_recouped || 
                                              this.formatDisplayValue(analysis.refinance_loan_amount)}</strong>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                ` : ''}
            </div>`;
    },

    // Shared loan details component
    getLoanDetailsContent(analysis) {
        // Add debugging
        console.log('Generating loan details with analysis:', {
            hasBalloon: this.hasBalloonData(analysis),
            loans: {
                loan1: {
                    amount: analysis.loan1_loan_amount,
                    interest: analysis.loan1_loan_interest_rate,
                    term: analysis.loan1_loan_term
                },
                loan2: {
                    amount: analysis.loan2_loan_amount,
                    interest: analysis.loan2_loan_interest_rate,
                    term: analysis.loan2_loan_term
                }
            },
            calculated_metrics: analysis.calculated_metrics
        });
    
        // Check for BRRRR analysis type first and validate loan data exists
        if (analysis.analysis_type?.includes('BRRRR') && 
            (this.toRawNumber(analysis.initial_loan_amount) > 0 || 
             this.toRawNumber(analysis.refinance_loan_amount) > 0)) {
            // Log BRRRR loan data for debugging
            console.log('BRRRR loan data detected:', {
                initial_loan_amount: analysis.initial_loan_amount,
                initial_loan_interest_rate: analysis.initial_loan_interest_rate,
                initial_loan_term: analysis.initial_loan_term,
                refinance_loan_amount: analysis.refinance_loan_amount,
                refinance_loan_interest_rate: analysis.refinance_loan_interest_rate,
                refinance_loan_term: analysis.refinance_loan_term,
                calculated_metrics: {
                    initial_loan_payment: analysis.calculated_metrics?.initial_loan_payment,
                    refinance_loan_payment: analysis.calculated_metrics?.refinance_loan_payment
                }
            });
            
            // Handle BRRRR-specific loan details
            return this.getBRRRRLoanDetails(analysis);
        } else if (this.hasBalloonData(analysis)) {
            // Get metrics
            const preMonthlyPayment = analysis.calculated_metrics?.pre_balloon_monthly_payment || 
                                     analysis.calculated_metrics?.loan1_loan_payment;
            const postMonthlyPayment = analysis.calculated_metrics?.post_balloon_monthly_payment || 
                                      analysis.calculated_metrics?.refinance_loan_payment;
            
            // Get all loan prefixes with existing loans
            const existingLoans = [];
            ['loan1', 'loan2', 'loan3'].forEach(prefix => {
                const loanAmount = this.toRawNumber(analysis[`${prefix}_loan_amount`]);
                if (loanAmount > 0) {
                    existingLoans.push(prefix);
                }
            });
            
            // Generate HTML for all existing pre-balloon loans
            let preBallooonLoansHTML = '';
            existingLoans.forEach(prefix => {
                const loanPayment = analysis.calculated_metrics?.[`${prefix}_loan_payment`];
                preBallooonLoansHTML += `
                    <div class="list-group list-group-flush">
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Loan Name</span>
                            <strong>${analysis[`${prefix}_loan_name`] || `Loan ${prefix.slice(-1)}`}</strong>
                        </div>
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
                            <strong>${loanPayment || this.formatDisplayValue(0)}</strong>
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
                    ${prefix !== existingLoans[existingLoans.length - 1] ? '<hr class="my-3">' : ''}
                `;
            });
            
            return `
                <div class="accordion" id="balloonLoanAccordion">
                    <!-- Pre-Balloon Section -->
                    <div class="accordion-item">
                        <h6 class="accordion-header">
                            <button class="accordion-button" type="button" data-bs-toggle="collapse" 
                                    data-bs-target="#preBalloonCollapse">
                                Original Loans (Pre-Balloon)
                            </button>
                        </h6>
                        <div id="preBalloonCollapse" class="accordion-collapse collapse show" 
                             data-bs-parent="#balloonLoanAccordion">
                            <div class="accordion-body p-0">
                                ${preBallooonLoansHTML}
                                <div class="list-group-item d-flex justify-content-between align-items-center py-3 bg-light">
                                    <span class="fw-bold">Combined Monthly Payment</span>
                                    <strong>${preMonthlyPayment || this.formatDisplayValue(0)}</strong>
                                </div>
                                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                    <span>Balloon Due Date</span>
                                    <strong>${new Date(analysis.balloon_due_date).toLocaleDateString()}</strong>
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
            // Regular loans - keep your existing code here
            const loanPrefixes = ['loan1', 'loan2', 'loan3'];
            let hasLoans = false;
            
            let html = '<div class="accordion" id="regularLoansAccordion">';
            
            for (const prefix of loanPrefixes) {
                // Check if loan exists by verifying amount is greater than 0
                const loanAmount = this.toRawNumber(analysis[`${prefix}_loan_amount`]);
                if (loanAmount > 0) {
                    hasLoans = true;
                    
                    // Get loan payment from calculated metrics
                    const loanPayment = analysis.calculated_metrics?.[`${prefix}_loan_payment`];
                    console.log(`${prefix} payment:`, loanPayment);
                    
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
                                            <strong>${this.formatDisplayValue(loanAmount)}</strong>
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
                                            <strong>${loanPayment || this.formatDisplayValue(0)}</strong>
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
        console.log('BRRRR Report Data:', {
            initialLoanPayment: analysis?.calculated_metrics?.initial_loan_payment,
            refinanceLoanPayment: analysis?.calculated_metrics?.refinance_loan_payment,
            monthlyRent: analysis.monthly_rent,
            monthlyCashFlow: analysis.calculated_metrics?.monthly_cash_flow,
            annualCashFlow: analysis.calculated_metrics?.annual_cash_flow,
            fullMetrics: analysis.calculated_metrics
        });
    
        // Add debugging for KPI configuration access
        console.log('Analysis module:', this);
        console.log('KPI_CONFIGS access:', this.KPI_CONFIGS);
    
        // Generate KPI card
        const kpiCard = this.generateKPICard(analysis);
        console.log('Generated KPI card:', kpiCard ? 'Success' : 'Empty');
        
        // Calculate additional BRRRR specific values to display
        const initialInvestment = this.toRawNumber(analysis.purchase_price) + 
                                this.toRawNumber(analysis.renovation_costs) +
                                (analysis.analysis_type.includes('PadSplit') ? this.toRawNumber(analysis.furnishing_costs) : 0);
                                
        const initialLoanAmount = this.toRawNumber(analysis.initial_loan_amount);
        const refinanceLoanAmount = this.toRawNumber(analysis.refinance_loan_amount);
        const refinanceClosingCosts = this.toRawNumber(analysis.refinance_loan_closing_costs);
        
        // Calculate initial out-of-pocket before refinance
        const initialOutOfPocket = Math.max(0, initialInvestment - initialLoanAmount);
        
        // Calculate cash recouped after refinance
        const cashRecouped = Math.max(0, refinanceLoanAmount - initialLoanAmount - refinanceClosingCosts);
        
        // Calculate final investment after refinance
        const finalInvestment = Math.max(0, initialOutOfPocket - cashRecouped);
        
        // Calculate the actual cash-on-cash return based on final investment
        const annualCashFlow = this.toRawNumber(analysis.calculated_metrics?.annual_cash_flow);
        const cashOnCashReturn = finalInvestment > 0 ? 
                                (annualCashFlow / finalInvestment) * 100 : 
                                999.99; // Cap at 999.99% for near-zero investments
        
        console.log('BRRRR Investment Calculation:', {
            initialInvestment,
            initialLoanAmount,
            initialOutOfPocket,
            refinanceLoanAmount,
            refinanceClosingCosts,
            cashRecouped,
            finalInvestment,
            annualCashFlow,
            cashOnCashReturn: cashOnCashReturn.toFixed(2) + '%'
        });
    
        return `
            <!-- Purchase Details Card -->
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">Purchase Details</h5>
                </div>
                <div class="card-body">
                    <div class="list-group list-group-flush">
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Purchase Price</span>
                            <strong>${this.formatDisplayValue(analysis.purchase_price)}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>After Repair Value</span>
                            <strong>${this.formatDisplayValue(analysis.after_repair_value)}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Renovation Costs</span>
                            <strong>${this.formatDisplayValue(analysis.renovation_costs)}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Renovation Duration</span>
                            <strong>${analysis.renovation_duration} months</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Cash to Seller</span>
                            <strong>${this.formatDisplayValue(analysis.cash_to_seller)}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Closing Costs</span>
                            <strong>${this.formatDisplayValue(analysis.closing_costs)}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Assignment Fee</span>
                            <strong>${this.formatDisplayValue(analysis.assignment_fee)}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Marketing Costs</span>
                            <strong>${this.formatDisplayValue(analysis.marketing_costs)}</strong>
                        </div>
                        ${analysis.analysis_type.includes('PadSplit') ? `
                            <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                <span>Furnishing Costs</span>
                                <strong>${this.formatDisplayValue(analysis.furnishing_costs)}</strong>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        
            <!-- Income & Returns Card -->
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">Income & Returns</h5>
                </div>
                <div class="card-body">
                    <div class="list-group list-group-flush">
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Property Type</span>
                            <strong>${analysis.property_type || 'Not Specified'}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Monthly Rent</span>
                            <strong>${this.formatDisplayValue(analysis.monthly_rent)}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Monthly Cash Flow</span>
                            <strong>${analysis.calculated_metrics?.monthly_cash_flow || '$0.00'}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Annual Cash Flow</span>
                            <strong>${analysis.calculated_metrics?.annual_cash_flow || '$0.00'}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span class="d-flex align-items-center">
                                Cash-on-Cash Return
                                <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" 
                                   title="Based on remaining invested capital after refinancing">
                                </i>
                            </span>
                            <strong>${finalInvestment > 0 ? 
                                    this.formatDisplayValue(cashOnCashReturn, 'percentage') : 
                                    '999.99%'}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>ROI</span>
                            <strong>${analysis.calculated_metrics?.roi || '0%'}</strong>
                        </div>
                    </div>
                </div>
            </div>
    
            <!-- BRRRR Strategy Details Card -->
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">BRRRR Strategy Analysis</h5>
                </div>
                <div class="card-body">
                    <div class="list-group list-group-flush">
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Initial Investment (Before Financing)</span>
                            <strong>${this.formatDisplayValue(initialInvestment)}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Initial Loan Amount</span>
                            <strong>${this.formatDisplayValue(analysis.initial_loan_amount)}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span class="d-flex align-items-center">
                                Initial Out-of-Pocket
                                <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" 
                                   title="Initial investment minus initial loan amount">
                                </i>
                            </span>
                            <strong>${this.formatDisplayValue(initialOutOfPocket)}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Refinance Loan Amount</span>
                            <strong>${this.formatDisplayValue(analysis.refinance_loan_amount)}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Refinance Closing Costs</span>
                            <strong>${this.formatDisplayValue(analysis.refinance_loan_closing_costs)}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span class="d-flex align-items-center">
                                Cash Recouped From Refinance
                                <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" 
                                   title="Refinance amount minus initial loan payoff minus closing costs">
                                </i>
                            </span>
                            <strong>${this.formatDisplayValue(cashRecouped)}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3 bg-light">
                            <span class="d-flex align-items-center fw-bold">
                                Final Cash Invested 
                                <i class="ms-2 bi bi-info-circle" data-bs-toggle="tooltip" 
                                   title="Initial out-of-pocket minus cash recouped from refinance">
                                </i>
                            </span>
                            <strong>${this.formatDisplayValue(finalInvestment)}</strong>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                            <span>Equity Captured</span>
                            <strong>${analysis.calculated_metrics?.equity_captured || '$0.00'}</strong>
                        </div>
                    </div>
                </div>
            </div>
    
            <!-- KPIs Card -->
            ${kpiCard}
    
            <!-- The rest of the report content remains the same -->
            <!-- Financing Card -->
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">Financing Details</h5>
                </div>
                <div class="card-body">
                    <div class="accordion" id="brrrFinancingAccordion">
                        <!-- Initial Loan Section -->
                        <div class="accordion-item">
                            <h6 class="accordion-header">
                                <button class="accordion-button" type="button" data-bs-toggle="collapse" 
                                        data-bs-target="#initialLoanCollapse">
                                    Initial Hard Money Loan
                                </button>
                            </h6>
                            <div id="initialLoanCollapse" class="accordion-collapse collapse show" 
                                 data-bs-parent="#brrrFinancingAccordion">
                                <div class="accordion-body p-0">
                                    <div class="list-group list-group-flush">
                                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                            <span>Amount</span>
                                            <strong>${this.formatDisplayValue(analysis.initial_loan_amount)}</strong>
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
                                            <span>Monthly Payment</span>
                                            <strong>${analysis.calculated_metrics?.initial_loan_payment || '$0.00'}</strong>
                                        </div>
                                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                            <span>Interest Only</span>
                                            <strong>${analysis.initial_interest_only ? 'Yes' : 'No'}</strong>
                                        </div>
                                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                            <span>Down Payment</span>
                                            <strong>${this.formatDisplayValue(analysis.initial_loan_down_payment)}</strong>
                                        </div>
                                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                            <span>Closing Costs</span>
                                            <strong>${this.formatDisplayValue(analysis.initial_loan_closing_costs)}</strong>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
    
                        <!-- Refinance Section -->
                        <div class="accordion-item">
                            <h6 class="accordion-header">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" 
                                        data-bs-target="#refinanceCollapse">
                                    Refinance Loan
                                </button>
                            </h6>
                            <div id="refinanceCollapse" class="accordion-collapse collapse" 
                                 data-bs-parent="#brrrFinancingAccordion">
                                <div class="accordion-body p-0">
                                    <div class="list-group list-group-flush">
                                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                            <span>Amount</span>
                                            <strong>${this.formatDisplayValue(analysis.refinance_loan_amount)}</strong>
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
                                            <span>Monthly Payment</span>
                                            <strong>${analysis.calculated_metrics?.refinance_loan_payment || '$0.00'}</strong>
                                        </div>
                                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                            <span>Down Payment</span>
                                            <strong>${this.formatDisplayValue(analysis.refinance_loan_down_payment)}</strong>
                                        </div>
                                        <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                                            <span>Closing Costs</span>
                                            <strong>${this.formatDisplayValue(analysis.refinance_loan_closing_costs)}</strong>
                                        </div>
                                    </div>
                                </div>
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
        
        console.log('Switching to financial tab, currentAnalysisId:', this.currentAnalysisId);
        
        if (financialTab) {
            // Trigger click on financial tab
            financialTab.click();
        }
    
        // Create or show submit button
        if (!submitBtn) {
            console.log('Creating new submit button');
            const form = document.getElementById('analysisForm');
            if (form) {
                const actionButtons = form.querySelector('.d-flex.gap-2');
                if (actionButtons) {
                    const newSubmitBtn = document.createElement('button');
                    newSubmitBtn.id = 'submitAnalysisBtn';
                    newSubmitBtn.type = 'submit';
                    newSubmitBtn.className = 'btn btn-primary';
                    newSubmitBtn.innerHTML = '<i class="bi bi-save me-2"></i>Update Analysis';
                    actionButtons.insertBefore(newSubmitBtn, actionButtons.firstChild);
                    
                    // Set up form for editing
                    if (this.currentAnalysisId) {
                        form.setAttribute('data-analysis-id', this.currentAnalysisId);
                        form.onsubmit = (event) => this.handleEditSubmit(event, this.currentAnalysisId);
                    }
                }
            }
        } else {
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

    initMultiFamilyHandlers() {
        console.log('Initializing Multi-Family handlers');
        
        const unitTypesContainer = document.getElementById('unit-types-container');
        const addUnitTypeBtn = document.getElementById('add-unit-type-btn');
        
        if (!unitTypesContainer || !addUnitTypeBtn) {
            console.log('Unit type elements not found');
            return;
        }
        
        // Initialize with one unit type if none exist
        if (!unitTypesContainer.children.length) {
            unitTypesContainer.insertAdjacentHTML('beforeend', getUnitTypeHTML(0));
        }
        
        // Handle adding new unit types
        addUnitTypeBtn.addEventListener('click', () => {
            const nextIndex = unitTypesContainer.children.length;
            if (nextIndex < 10) { // Limit to 10 unit types
                unitTypesContainer.insertAdjacentHTML('beforeend', getUnitTypeHTML(nextIndex));
                this.initUnitTypeCalculations();
            } else {
                toastr.warning('Maximum of 10 unit types allowed');
            }
        });
        
        // Handle removing unit types
        unitTypesContainer.addEventListener('click', (e) => {
            if (e.target.closest('.remove-unit-type-btn')) {
                const unitSection = e.target.closest('.unit-type-section');
                if (unitTypesContainer.children.length > 1) {
                    unitSection.remove();
                    this.reindexUnitTypes();
                    this.updateTotalUnits();
                    this.updateTotalIncome();
                } else {
                    toastr.warning('At least one unit type is required');
                }
            }
        });
        
        this.initUnitTypeCalculations();
        this.initMultiFamilyValidation();
    },
    
    initUnitTypeCalculations() {
        // Initialize listeners for unit count and rent changes
        const unitInputs = document.querySelectorAll('.unit-count, .unit-rent, .unit-occupied');
        unitInputs.forEach(input => {
            input.removeEventListener('input', this.updateTotalUnits);
            input.removeEventListener('input', this.updateTotalIncome);
            input.addEventListener('input', () => {
                this.updateTotalUnits();
                this.updateTotalIncome();
            });
        });
    },

    updateTotalIncome() {
        const totalPotentialIncomeInput = document.getElementById('total_potential_income');
        const otherIncomeInput = document.getElementById('other_income');
        
        if (!totalPotentialIncomeInput) return;
        
        let totalRent = 0;
        document.querySelectorAll('.unit-type-section').forEach(section => {
            const count = parseInt(section.querySelector('.unit-count').value) || 0;
            const rent = parseFloat(section.querySelector('.unit-rent').value) || 0;
            totalRent += count * rent;
        });
        
        const otherIncome = parseFloat(otherIncomeInput?.value) || 0;
        totalPotentialIncomeInput.value = (totalRent + otherIncome).toFixed(2);
    },

    initMultiFamilyValidation() {
        const form = document.getElementById('analysisForm');
        if (!form) return;
        
        // Remove any existing submit event listeners
        const newForm = form.cloneNode(true);
        form.parentNode.replaceChild(newForm, form);
        
        // Add validation for unit mix only when it's Multi-Family
        newForm.addEventListener('submit', (e) => {
            const analysisType = document.getElementById('analysis_type')?.value;
            if (analysisType === 'Multi-Family') {
                if (!this.validateMultiFamilyData()) {
                    e.preventDefault();
                    return false;
                }
            }
        });
    },
    
    validateMultiFamilyData() {
        try {
            // Only validate unit types for Multi-Family
            if (this.initialAnalysisType === 'Multi-Family') {
                const unitTypes = this.getUnitTypesData();
                let isValid = true;
                let errors = [];
    
                // 1. Validate unit types exist
                if (!unitTypes || unitTypes.length === 0) {
                    errors.push('At least one unit type is required');
                    isValid = false;
                } else {
                    // 2. Validate each unit type
                    unitTypes.forEach((ut, index) => {
                        const section = document.querySelector(`.unit-type-section[data-unit-index="${index}"]`);
                        
                        // Clear previous validation states
                        if (section) {
                            section.querySelectorAll('.is-invalid').forEach(field => {
                                field.classList.remove('is-invalid');
                            });
                        }
    
                        // Basic unit type validation
                        if (ut.count <= 0) {
                            errors.push(`Unit Type ${index + 1}: Number of units must be greater than 0`);
                            isValid = false;
                            section?.querySelector('.unit-count')?.classList.add('is-invalid');
                        }
    
                        if (ut.occupied > ut.count) {
                            errors.push(`Unit Type ${index + 1}: Occupied units cannot exceed total units`);
                            isValid = false;
                            section?.querySelector('.unit-occupied')?.classList.add('is-invalid');
                        }
    
                        if (ut.square_footage <= 0) {
                            errors.push(`Unit Type ${index + 1}: Square footage must be greater than 0`);
                            isValid = false;
                            section?.querySelector('input[name$="[square_footage]"]')?.classList.add('is-invalid');
                        }
    
                        if (ut.rent <= 0) {
                            errors.push(`Unit Type ${index + 1}: Rent must be greater than 0`);
                            isValid = false;
                            section?.querySelector('.unit-rent')?.classList.add('is-invalid');
                        }
                    });
                }
    
                // Validate building details if Multi-Family
                const buildingFields = {
                    'floors': {
                        min: 1,
                        max: 30,
                        label: 'Number of floors',
                        message: 'Number of floors must be between 1 and 30'
                    },
                    'year_built': {
                        min: 1800,
                        max: new Date().getFullYear(),
                        label: 'Year built',
                        message: `Year built must be between 1800 and ${new Date().getFullYear()}`
                    }
                };
    
                Object.entries(buildingFields).forEach(([fieldId, config]) => {
                    const field = document.getElementById(fieldId);
                    if (field) {
                        const value = parseInt(field.value) || 0;
                        if (value < config.min || value > config.max) {
                            errors.push(config.message);
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
                        }
                    }
                });
    
                // Validate required operating expenses only for Multi-Family
                const requiredExpenses = {
                    'property_taxes': 'Property taxes',
                    'insurance': 'Insurance',
                    'common_area_maintenance': 'Common area maintenance'
                };
    
                Object.entries(requiredExpenses).forEach(([fieldId, label]) => {
                    const field = document.getElementById(fieldId);
                    if (field) {
                        const value = parseFloat(field.value) || 0;
                        if (value <= 0) {
                            errors.push(`${label} must be greater than 0`);
                            isValid = false;
                            field.classList.add('is-invalid');
                        }
                    }
                });
    
                if (!isValid) {
                    toastr.error(errors.join('<br>'), 'Validation Errors', {
                        timeOut: 5000,
                        extendedTimeOut: 2000,
                        progressBar: true,
                        closeButton: true,
                        enableHtml: true,
                        newestOnTop: false
                    });
                    return false;
                }
            }
    
            // If we get here, either validation passed or it's not a Multi-Family analysis
            return true;
    
        } catch (error) {
            console.error('Error validating Multi-Family data:', error);
            toastr.error('Error validating form data');
            return false;
        }
    },
    
    getUnitTypesData() {
        const unitTypes = [];
        document.querySelectorAll('.unit-type-section').forEach(section => {
            unitTypes.push({
                type: section.querySelector('select').value,
                count: parseInt(section.querySelector('.unit-count').value) || 0,
                occupied: parseInt(section.querySelector('.unit-occupied').value) || 0,
                square_footage: parseInt(section.querySelector('input[name$="[square_footage]"]').value) || 0,
                rent: parseFloat(section.querySelector('.unit-rent').value) || 0
            });
        });
        return unitTypes;
    },
    
    reindexUnitTypes() {
        const unitSections = document.querySelectorAll('.unit-type-section');
        unitSections.forEach((section, index) => {
            section.dataset.unitIndex = index;
            section.querySelector('.card-header h6').textContent = `Unit Type ${index + 1}`;
            
            // Update input names
            section.querySelectorAll('input, select').forEach(input => {
                const fieldName = input.name.split('[')[0];
                input.name = `${fieldName}[${index}]${input.name.split(']')[1] || ''}`;
            });
        });
    },
    
    updateTotalUnits() {
        const totalUnitsInput = document.getElementById('total_units');
        const occupiedUnitsInput = document.getElementById('occupied_units');
        
        if (!totalUnitsInput || !occupiedUnitsInput) return;
        
        let totalUnits = 0;
        let occupiedUnits = 0;
        
        document.querySelectorAll('.unit-type-section').forEach(section => {
            const count = parseInt(section.querySelector('.unit-count').value) || 0;
            const occupied = parseInt(section.querySelector('.unit-occupied').value) || 0;
            totalUnits += count;
            occupiedUnits += Math.min(occupied, count); // Occupied cannot exceed total
        });
        
        totalUnitsInput.value = totalUnits;
        occupiedUnitsInput.value = occupiedUnits;
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

    parseNumericValue(value) {
        if (value === null || value === undefined) return 0;
        // Handle string values that might include currency symbols, commas, or percentage signs
        if (typeof value === 'string') {
            // Remove currency symbols, commas, and % signs
            value = value.replace(/[$,\s%]+/g, '');
        }
        const parsed = parseFloat(value);
        return isNaN(parsed) ? 0 : parsed;
    },
    
    // Function to calculate KPIs for the analysis
    calculateKPIs: function(analysis) {
        const metrics = {};
        
        try {
            // Get gross income
            let grossIncome = 0;
            let totalUnits = 1;  // Default for single-unit properties
            
            if (analysis.analysis_type === 'Multi-Family') {
                // For Multi-Family, calculate from unit types
                let unitTypes = [];
                if (analysis.unit_types) {
                    try {
                        if (typeof analysis.unit_types === 'string') {
                            unitTypes = JSON.parse(analysis.unit_types);
                        } else {
                            unitTypes = analysis.unit_types;
                        }
                    } catch (error) {
                        console.error('Error parsing unit types:', error);
                        unitTypes = [];
                    }
                }
                
                grossIncome = unitTypes.reduce((total, ut) => 
                    total + (ut.count || 0) * (ut.rent || 0), 0);
                totalUnits = unitTypes.reduce((total, ut) => 
                    total + (ut.count || 0), 0) || 1;  // Avoid division by zero
            } else {
                // For single-unit properties
                grossIncome = this.toRawNumber(analysis.monthly_rent);
            }
            
            console.log(`Monthly Gross Income: ${grossIncome}, Total Units: ${totalUnits}`);
            const annualGrossIncome = grossIncome * 12;
            
            // Calculate expenses
            const expenseFields = [
                'property_taxes',
                'insurance',
                'hoa_coa_coop',
                'common_area_maintenance',
                'elevator_maintenance',
                'staff_payroll',
                'trash_removal',
                'common_utilities'
            ];
            
            const annualFixedExpenses = expenseFields.reduce((total, field) => {
                const monthlyExpense = this.toRawNumber(analysis[field]);
                return total + (monthlyExpense * 12);
            }, 0);
            
            // Calculate percentage-based expenses
            const percentageFields = {
                management: this.toRawNumber(analysis.management_fee_percentage),
                capex: this.toRawNumber(analysis.capex_percentage),
                vacancy: this.toRawNumber(analysis.vacancy_percentage),
                repairs: this.toRawNumber(analysis.repairs_percentage)
            };
            
            const annualPercentageExpenses = Object.entries(percentageFields).reduce((total, [name, percentage]) => {
                const expense = annualGrossIncome * (percentage / 100);
                return total + expense;
            }, 0);
            
            // Add PadSplit-specific expenses if applicable
            let additionalExpenses = 0;
            if (analysis.analysis_type.includes('PadSplit')) {
                const padsplitFields = [
                    'utilities',
                    'internet',
                    'cleaning',
                    'pest_control',
                    'landscaping'
                ];
                
                const padsplitExpenses = padsplitFields.reduce((total, field) => {
                    return total + (this.toRawNumber(analysis[field]) * 12);
                }, 0);
                
                // Add platform fee
                const platformPercentage = this.toRawNumber(analysis.padsplit_platform_percentage);
                const platformFee = annualGrossIncome * (platformPercentage / 100);
                
                additionalExpenses = padsplitExpenses + platformFee;
            }
            
            // Calculate NOI
            const totalExpenses = annualFixedExpenses + annualPercentageExpenses + additionalExpenses;
            const annualNOI = annualGrossIncome - totalExpenses;
            
            // Set NOI metric (monthly)
            const monthlyNOI = annualNOI / 12;
            if (analysis.analysis_type === 'Multi-Family') {
                metrics.noi = monthlyNOI / totalUnits;  // Per unit for Multi-Family
            } else {
                metrics.noi = monthlyNOI;
            }
            
            // Calculate Operating Expense Ratio
            if (annualGrossIncome > 0) {
                metrics.operating_expense_ratio = (totalExpenses / annualGrossIncome) * 100;
            } else {
                metrics.operating_expense_ratio = 0;
            }
            
            // Calculate Cap Rate (except for Lease Option)
            if (analysis.analysis_type !== 'Lease Option') {
                const purchasePrice = this.toRawNumber(analysis.purchase_price);
                if (purchasePrice > 0) {
                    metrics.cap_rate = (annualNOI / purchasePrice) * 100;
                }
            }
            
            // Calculate DSCR (except for Lease Option)
            if (analysis.analysis_type !== 'Lease Option') {
                let annualDebtService = 0;
                
                // For BRRRR, use refinance loan payment
                if (analysis.analysis_type.includes('BRRRR')) {
                    // Get payment from calculated metrics if available
                    const refinancePayment = analysis.calculated_metrics?.refinance_loan_payment;
                    if (refinancePayment) {
                        const monthlyPayment = this.toRawNumber(refinancePayment);
                        annualDebtService = monthlyPayment * 12;
                    } else {
                        // Calculate if not available
                        const loanAmount = this.toRawNumber(analysis.refinance_loan_amount);
                        const interestRate = this.toRawNumber(analysis.refinance_loan_interest_rate) / 100 / 12;
                        const term = this.toRawNumber(analysis.refinance_loan_term);
                        
                        if (loanAmount > 0 && interestRate > 0 && term > 0) {
                            const monthlyPayment = loanAmount * interestRate * Math.pow(1 + interestRate, term) / (Math.pow(1 + interestRate, term) - 1);
                            annualDebtService = monthlyPayment * 12;
                        }
                    }
                } else {
                    // For other types, sum all loan payments
                    for (let i = 1; i <= 3; i++) {
                        const prefix = `loan${i}`;
                        const payment = analysis.calculated_metrics?.[`${prefix}_loan_payment`];
                        if (payment) {
                            const monthlyPayment = this.toRawNumber(payment);
                            annualDebtService += monthlyPayment * 12;
                        }
                    }
                }
                
                if (annualDebtService > 0) {
                    metrics.dscr = annualNOI / annualDebtService;
                }
            }
            
            // Calculate Cash on Cash Return
            if (analysis.analysis_type.includes('BRRRR')) {
                // Use the BRRRR-specific calculation
                const totalInvestment = this.calculateBRRRRInvestment(analysis);
                
                // Get annual cash flow
                let annualCashFlow = 0;
                if (analysis.calculated_metrics?.annual_cash_flow) {
                    annualCashFlow = this.toRawNumber(analysis.calculated_metrics.annual_cash_flow);
                } else {
                    // Calculate from monthly cash flow if available
                    const monthlyCashFlow = analysis.calculated_metrics?.monthly_cash_flow;
                    if (monthlyCashFlow) {
                        annualCashFlow = this.toRawNumber(monthlyCashFlow) * 12;
                    } else {
                        // Calculate directly if no calculated value available
                        let loanPayment = 0;
                        const refinancePayment = analysis.calculated_metrics?.refinance_loan_payment;
                        if (refinancePayment) {
                            loanPayment = this.toRawNumber(refinancePayment);
                        }
                        annualCashFlow = annualNOI - (loanPayment * 12);
                    }
                }
                
                // Calculate Cash on Cash Return
                if (totalInvestment > 0.01) {  // Avoid division by zero
                    metrics.cash_on_cash_return = (annualCashFlow / totalInvestment) * 100;
                } else {
                    metrics.cash_on_cash_return = 999.99;  // Cap at 999.99% for near-zero investments
                }
            } else {
                // Standard calculation
                let totalCashInvested = 0;
                
                // Try to get from calculated metrics first
                if (analysis.calculated_metrics?.total_cash_invested) {
                    totalCashInvested = this.toRawNumber(analysis.calculated_metrics.total_cash_invested);
                } else {
                    // For Lease Option, use option fee
                    if (analysis.analysis_type === 'Lease Option') {
                        totalCashInvested = this.toRawNumber(analysis.option_consideration_fee);
                    } else {
                        // Calculate sum of down payments and costs
                        let downPaymentTotal = 0;
                        for (let i = 1; i <= 3; i++) {
                            downPaymentTotal += this.toRawNumber(analysis[`loan${i}_loan_down_payment`]);
                        }
                        
                        let closingCosts = 0;
                        for (let i = 1; i <= 3; i++) {
                            closingCosts += this.toRawNumber(analysis[`loan${i}_loan_closing_costs`]);
                        }
                        
                        const renovationCosts = this.toRawNumber(analysis.renovation_costs);
                        
                        totalCashInvested = downPaymentTotal + closingCosts + renovationCosts;
                    }
                }
                
                // Get annual cash flow
                let annualCashFlow = 0;
                if (analysis.calculated_metrics?.annual_cash_flow) {
                    annualCashFlow = this.toRawNumber(analysis.calculated_metrics.annual_cash_flow);
                } else {
                    const monthlyCashFlow = analysis.calculated_metrics?.monthly_cash_flow;
                    if (monthlyCashFlow) {
                        annualCashFlow = this.toRawNumber(monthlyCashFlow) * 12;
                    } else {
                        // For Lease Option, simple rent - expenses calculation
                        if (analysis.analysis_type === 'Lease Option') {
                            annualCashFlow = annualNOI;
                        } else {
                            // Get total loan payment
                            let totalLoanPayment = 0;
                            for (let i = 1; i <= 3; i++) {
                                const prefix = `loan${i}`;
                                const payment = analysis.calculated_metrics?.[`${prefix}_loan_payment`];
                                if (payment) {
                                    totalLoanPayment += this.toRawNumber(payment);
                                }
                            }
                            
                            annualCashFlow = annualNOI - (totalLoanPayment * 12);
                        }
                    }
                }
                
                // Calculate Cash on Cash Return
                if (totalCashInvested > 0) {
                    metrics.cash_on_cash_return = (annualCashFlow / totalCashInvested) * 100;
                }
            }
            
            return metrics;
            
        } catch (error) {
            console.error('Error calculating KPIs:', error);
            return {};
        }
    },
    
    calculateBRRRRInvestment: function(analysis) {
        try {
            // Step 1: Calculate initial investment (before financing)
            const initialInvestment = 
                this.toRawNumber(analysis.purchase_price) + 
                this.toRawNumber(analysis.renovation_costs) + 
                this.toRawNumber(analysis.initial_loan_closing_costs);
            
            // Add holding costs if available in calculated metrics
            const holdingCosts = this.toRawNumber(analysis.calculated_metrics?.holding_costs);
            
            // Add furnishing costs for PadSplit
            let furnishingCosts = 0;
            if (analysis.analysis_type.includes('PadSplit')) {
                furnishingCosts = this.toRawNumber(analysis.furnishing_costs);
            }
            
            const totalInitialInvestment = initialInvestment + holdingCosts + furnishingCosts;
            
            // Step 2: Subtract initial financing to get out-of-pocket
            const initialLoanAmount = this.toRawNumber(analysis.initial_loan_amount);
            const initialOutOfPocket = Math.max(0, totalInitialInvestment - initialLoanAmount);
            
            // Step 3: Calculate cash recouped from refinance
            const refinanceLoanAmount = this.toRawNumber(analysis.refinance_loan_amount);
            const refinanceClosingCosts = this.toRawNumber(analysis.refinance_loan_closing_costs);
            
            const cashRecouped = Math.max(0, refinanceLoanAmount - initialLoanAmount - refinanceClosingCosts);
            
            // Step 4: Calculate final out-of-pocket investment
            const finalInvestment = Math.max(0, initialOutOfPocket - cashRecouped);
            
            console.log("BRRRR Investment Calculation:", {
                initialInvestment: totalInitialInvestment,
                initialLoanAmount,
                initialOutOfPocket,
                refinanceLoanAmount,
                refinanceClosingCosts,
                cashRecouped,
                finalInvestment
            });
            
            return finalInvestment;
            
        } catch (error) {
            console.error('Error calculating BRRRR investment:', error);
            return 0;
        }
    },

    // Function to generate the KPI card HTML
    generateKPICard: function(analysis) {
        console.log('Generating KPI card for analysis:', {
            type: analysis.analysis_type,
            id: analysis.id
        });
        
        // If we don't have an analysis ID, we can't generate KPIs
        if (!analysis.id) {
            return `
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">Key Performance Indicators</h5>
                    </div>
                    <div class="card-body text-center">
                        <p>KPIs unavailable - analysis has not been saved.</p>
                    </div>
                </div>`;
        }
        
        // Get KPI data directly from the analysis calculated metrics
        const metrics = analysis.calculated_metrics || {};
        console.log('Using calculated metrics for KPIs:', metrics);
        
        // Create KPI data structure
        const kpiData = this.prepareKPIData(analysis);
        
        // Return the rendered KPI card
        return this.renderKPICard(kpiData);
    },
    
    // New helper function to transform calculated metrics into KPI format
    prepareKPIData: function(analysis) {
        const metrics = analysis.calculated_metrics || {};
        const analysisType = analysis.analysis_type || '';
        
        // Get KPI configuration based on analysis type
        let kpiConfig = this.KPI_CONFIGS.LTR; // Default to LTR config
        if (analysisType.includes('BRRRR')) {
            kpiConfig = this.KPI_CONFIGS.BRRRR;
        } else if (analysisType === 'Multi-Family') {
            kpiConfig = this.KPI_CONFIGS['Multi-Family']; // Use bracket notation for property with spaces
        } else if (analysisType === 'Lease Option') {
            kpiConfig = this.KPI_CONFIGS['Lease Option']; // Use bracket notation for property with spaces
        }
        
        // Process metrics into KPI data
        const kpiData = {};
        
        // Process NOI
        if (kpiConfig.noi) {
            const noiValue = this.extractNumericValue(metrics.monthly_noi || metrics.noi);
            kpiData.noi = {
                label: kpiConfig.noi.label,
                value: noiValue,
                formatted_value: `$${noiValue.toFixed(2)}`,
                threshold: `$${kpiConfig.noi.threshold.toFixed(2)}`,
                info: kpiConfig.noi.info,
                is_favorable: noiValue >= kpiConfig.noi.threshold
            };
        }
        
        // Process Cap Rate
        if (kpiConfig.capRate && (metrics.cap_rate || metrics.capRate)) {
            const capRateValue = this.extractPercentageValue(metrics.cap_rate || metrics.capRate);
            const isFavorable = kpiConfig.capRate.goodMin <= capRateValue && capRateValue <= kpiConfig.capRate.goodMax;
            kpiData.cap_rate = {
                label: kpiConfig.capRate.label,
                value: capRateValue,
                formatted_value: `${capRateValue.toFixed(2)}%`,
                threshold: `${kpiConfig.capRate.goodMin.toFixed(2)}%-${kpiConfig.capRate.goodMax.toFixed(2)}%`,
                info: kpiConfig.capRate.info,
                is_favorable: isFavorable
            };
        }
        
        // Process Cash on Cash Return
        if (kpiConfig.cashOnCash && (metrics.cash_on_cash_return || metrics.cashOnCash)) {
            const cocValue = this.extractPercentageValue(metrics.cash_on_cash_return || metrics.cashOnCash);
            kpiData.cash_on_cash = {
                label: kpiConfig.cashOnCash.label,
                value: cocValue,
                formatted_value: `${cocValue.toFixed(2)}%`,
                threshold: `≥ ${kpiConfig.cashOnCash.threshold.toFixed(2)}%`,
                info: kpiConfig.cashOnCash.info,
                is_favorable: cocValue >= kpiConfig.cashOnCash.threshold
            };
        }
        
        // Process DSCR (if available)
        if (kpiConfig.dscr && (metrics.dscr || metrics.DSCR)) {
            const dscrValue = this.extractNumericValue(metrics.dscr || metrics.DSCR);
            kpiData.dscr = {
                label: kpiConfig.dscr.label,
                value: dscrValue,
                formatted_value: dscrValue.toFixed(2),
                threshold: `≥ ${kpiConfig.dscr.threshold.toFixed(2)}`,
                info: kpiConfig.dscr.info,
                is_favorable: dscrValue >= kpiConfig.dscr.threshold
            };
        }
        
        // Process Operating Expense Ratio
        if (kpiConfig.operatingExpenseRatio && (metrics.operating_expense_ratio || metrics.expenseRatio)) {
            const expenseRatioValue = this.extractPercentageValue(metrics.operating_expense_ratio || metrics.expenseRatio);
            kpiData.expense_ratio = {
                label: kpiConfig.operatingExpenseRatio.label,
                value: expenseRatioValue,
                formatted_value: `${expenseRatioValue.toFixed(2)}%`,
                threshold: `≤ ${kpiConfig.operatingExpenseRatio.threshold.toFixed(2)}%`,
                info: kpiConfig.operatingExpenseRatio.info,
                is_favorable: expenseRatioValue <= kpiConfig.operatingExpenseRatio.threshold
            };
        }
        
        return kpiData;
    },
    
    // Helper function to extract numeric value from a string or formatted value
    extractNumericValue: function(value) {
        if (value === null || value === undefined) return 0;
        if (typeof value === 'number') return value;
        
        // Handle string values
        if (typeof value === 'string') {
            // Remove currency symbols, commas, etc.
            const cleanValue = value.replace(/[$,\s]+/g, '');
            const parsedValue = parseFloat(cleanValue);
            return isNaN(parsedValue) ? 0 : parsedValue;
        }
        
        return 0;
    },
    
    // Helper function to extract percentage value from a string or formatted value
    extractPercentageValue: function(value) {
        if (value === null || value === undefined) return 0;
        if (typeof value === 'number') return value;
        
        // Handle string values
        if (typeof value === 'string') {
            // Remove percentage symbols, commas, etc.
            const cleanValue = value.replace(/[%,\s]+/g, '');
            const parsedValue = parseFloat(cleanValue);
            return isNaN(parsedValue) ? 0 : parsedValue;
        }
        
        return 0;
    },
    
    // Add a method to refresh KPIs
    refreshKPIs: function(analysisId, kpiCardId) {
        const kpiCard = document.getElementById(kpiCardId);
        if (kpiCard) {
            kpiCard.querySelector('.card-body').innerHTML = `
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading KPI data...</p>`;
                
            // Fetch the analysis data to get fresh KPIs
            this.getAnalysis(analysisId)
                .then(analysis => {
                    // Update the KPI card
                    kpiCard.outerHTML = this.generateKPICard(analysis);
                })
                .catch(error => {
                    console.error('Error refreshing KPIs:', error);
                    kpiCard.querySelector('.card-body').innerHTML = `
                        <div class="alert alert-danger mb-0">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            Failed to refresh KPI data.
                        </div>`;
                });
        }
    },

    renderKPICard: function(kpiData) {
        if (!kpiData || Object.keys(kpiData).length === 0) {
            return `
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="mb-0">Key Performance Indicators</h5>
                    </div>
                    <div class="card-body">
                        <p class="text-muted mb-0">No KPI data available</p>
                    </div>
                </div>`;
        }
        
        // Format KPI data for display
        let html = `
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">Key Performance Indicators</h5>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-bordered">
                            <thead class="bg-primary text-white">
                                <tr>
                                    <th>KPI</th>
                                    <th class="text-center">Target</th>
                                    <th class="text-center">Current</th>
                                    <th class="text-center">Assessment</th>
                                </tr>
                            </thead>
                            <tbody>`;
        
        // Add each KPI to the table
        for (const [key, data] of Object.entries(kpiData)) {
            html += `
                <tr>
                    <td>
                        <div class="d-flex align-items-center">
                            ${data.label}
                            <i class="bi bi-info-circle ms-2" 
                               data-bs-toggle="tooltip" 
                               data-bs-placement="right" 
                               title="${data.info}"></i>
                        </div>
                    </td>
                    <td class="text-center">${data.threshold}</td>
                    <td class="text-center">${data.formatted_value}</td>
                    <td class="text-center">
                        <span class="badge ${data.is_favorable ? 'bg-success' : 'bg-danger'}">
                            ${data.is_favorable ? 'Favorable' : 'Unfavorable'}
                        </span>
                    </td>
                </tr>`;
        }
        
        html += `
                            </tbody>
                        </table>
                    </div>
                    <div class="small text-muted mt-3">
                        Key Performance Indicators (KPIs) evaluate different aspects of the investment. 
                        Each metric has a target threshold that indicates good performance. 
                        'Favorable' means the metric meets or exceeds its performance target.
                    </div>
                </div>
            </div>`;
        
        return html;
    },
    
    // Initialize tooltips after adding KPI card
    initKPITooltips() {
        const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltips.forEach(tooltip => {
            new bootstrap.Tooltip(tooltip);
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
    
        console.log('Starting form validation:', { analysisType, hasBalloon });
    
        // Helper to validate numeric range
        const validateNumericRange = (value, min, max = Infinity) => {
            const num = this.toRawNumber(value);
            return !isNaN(num) && num >= min && num <= max;
        };
    
        // Helper to add error message
        const addErrorMessage = (field, message) => {
            let errorDiv = field.nextElementSibling;
            if (!errorDiv || !errorDiv.classList.contains('invalid-feedback')) {
                errorDiv = document.createElement('div');
                errorDiv.className = 'invalid-feedback';
                field.parentNode.insertBefore(errorDiv, field.nextSibling);
            }
            errorDiv.textContent = message;
        };
    
        // Validate required fields first
        const requiredFields = form.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                field.classList.add('is-invalid');
                addErrorMessage(field, 'This field is required');
                console.log('Required field empty:', field.id);
            } else {
                field.classList.remove('is-invalid');
            }
        });
    
        // Validate all numeric fields
        const numericFields = {
            'purchase_price': { min: 0, message: 'Purchase price must be greater than 0' },
            'monthly_rent': { min: 0, message: 'Monthly rent must be greater than 0' },
            'property_taxes': { min: 0, message: 'Property taxes must be greater than 0' },
            'insurance': { min: 0, message: 'Insurance must be greater than 0' },
            'hoa_coa_coop': { min: 0, message: 'HOA/COA/COOP must be greater than 0' },
            'square_footage': { min: 0, message: 'Square footage must be greater than 0' },
            'lot_size': { min: 0, message: 'Lot size must be greater than 0' },
            'year_built': { min: 1800, max: new Date().getFullYear(), message: 'Please enter a valid year' },
            'bedrooms': { min: 0, message: 'Number of bedrooms must be 0 or greater' },
            'bathrooms': { min: 0, message: 'Number of bathrooms must be 0 or greater' }
        };
    
        // Only validate Multi-Family specific fields if it's a Multi-Family analysis
        if (analysisType === 'Multi-Family') {
            if (!this.validateMultiFamilyData()) {
                isValid = false;
            }
        }

        // Add renovation fields if not Lease Option
        if (analysisType !== 'Lease Option') {
            Object.assign(numericFields, {
                'renovation_costs': { min: 0, message: 'Renovation costs must be 0 or greater' },
                'renovation_duration': { min: 0, message: 'Renovation duration must be 0 or greater' },
                'after_repair_value': { min: 0, message: 'After repair value must be greater than 0' }
            });
        }
    
        // Validate percentage fields
        const percentageFields = {
            'management_fee_percentage': { min: 0, max: 100, message: 'Management fee must be between 0 and 100%' },
            'capex_percentage': { min: 0, max: 100, message: 'CapEx must be between 0 and 100%' },
            'vacancy_percentage': { min: 0, max: 100, message: 'Vacancy rate must be between 0 and 100%' },
            'repairs_percentage': { min: 0, max: 100, message: 'Repairs percentage must be between 0 and 100%' }
        };
    
        // Validate PadSplit-specific fields if applicable
        if (analysisType?.includes('PadSplit')) {
            Object.assign(numericFields, {
                'furnishing_costs': { min: 0, message: 'Furnishing costs must be 0 or greater' },
                'utilities': { min: 0, message: 'Utilities must be 0 or greater' },
                'internet': { min: 0, message: 'Internet must be 0 or greater' },
                'cleaning': { min: 0, message: 'Cleaning costs must be 0 or greater' },
                'pest_control': { min: 0, message: 'Pest control must be 0 or greater' },
                'landscaping': { min: 0, message: 'Landscaping must be 0 or greater' }
            });
            Object.assign(percentageFields, {
                'padsplit_platform_percentage': { min: 0, max: 100, message: 'Platform fee must be between 0 and 100%' }
            });
        }
    
        // Validate numeric fields
        Object.entries(numericFields).forEach(([fieldName, rules]) => {
            const field = form.querySelector(`#${fieldName}`);
            if (field && field.value.trim()) {
                if (!validateNumericRange(field.value, rules.min, rules.max)) {
                    isValid = false;
                    field.classList.add('is-invalid');
                    addErrorMessage(field, rules.message);
                    console.log(`Invalid numeric field: ${fieldName}`, {
                        value: field.value,
                        rules: rules
                    });
                } else {
                    field.classList.remove('is-invalid');
                }
            }
        });
    
        // Validate percentage fields
        Object.entries(percentageFields).forEach(([fieldName, rules]) => {
            const field = form.querySelector(`#${fieldName}`);
            if (field && field.value.trim()) {
                if (!validateNumericRange(field.value, rules.min, rules.max)) {
                    isValid = false;
                    field.classList.add('is-invalid');
                    addErrorMessage(field, rules.message);
                    console.log(`Invalid percentage field: ${fieldName}`, {
                        value: field.value,
                        rules: rules
                    });
                } else {
                    field.classList.remove('is-invalid');
                }
            }
        });
    
        // Validate Lease Option specific fields
        if (analysisType === 'Lease Option') {
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
                        addErrorMessage(field, config.message);
                        console.log(`Invalid lease option field: ${fieldName}`, {
                            value: value,
                            valid: config.validate(value)
                        });
                    } else {
                        field.classList.remove('is-invalid');
                    }
                }
            });
        }
    
        // Validate balloon payment fields if enabled
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
                    if (!config.validate(field.value)) {
                        isValid = false;
                        field.classList.add('is-invalid');
                        addErrorMessage(field, config.message);
                        console.log(`Invalid balloon field: ${fieldName}`, {
                            value: field.value,
                            valid: config.validate(field.value)
                        });
                    } else {
                        field.classList.remove('is-invalid');
                    }
                }
            });
        }
    
        // Validate loan fields for BRRRR analysis
        if (analysisType?.includes('BRRRR')) {
            const brrrFields = {
                'initial_loan_amount': { min: 0, message: 'Initial loan amount must be greater than 0' },
                'initial_loan_down_payment': { min: 0, message: 'Initial down payment must be 0 or greater' },
                'initial_loan_interest_rate': { min: 0, max: 30, message: 'Interest rate must be between 0 and 30%' },
                'initial_loan_term': { min: 1, max: 360, message: 'Loan term must be between 1 and 360 months' },
                'initial_loan_closing_costs': { min: 0, message: 'Closing costs must be 0 or greater' },
                'refinance_loan_amount': { min: 0, message: 'Refinance amount must be greater than 0' },
                'refinance_loan_down_payment': { min: 0, message: 'Refinance down payment must be 0 or greater' },
                'refinance_loan_interest_rate': { min: 0, max: 30, message: 'Interest rate must be between 0 and 30%' },
                'refinance_loan_term': { min: 1, max: 360, message: 'Loan term must be between 1 and 360 months' },
                'refinance_loan_closing_costs': { min: 0, message: 'Closing costs must be 0 or greater' }
            };
    
            Object.entries(brrrFields).forEach(([fieldName, rules]) => {
                const field = form.querySelector(`#${fieldName}`);
                if (field && field.value.trim()) {
                    if (!validateNumericRange(field.value, rules.min, rules.max)) {
                        isValid = false;
                        field.classList.add('is-invalid');
                        addErrorMessage(field, rules.message);
                        console.log(`Invalid BRRRR field: ${fieldName}`, {
                            value: field.value,
                            rules: rules
                        });
                    } else {
                        field.classList.remove('is-invalid');
                    }
                }
            });
        }
    
        // Check for any invalid fields and show appropriate error message
        if (!isValid) {
            const invalidFields = form.querySelectorAll('.is-invalid');
            if (invalidFields.length > 0) {
                const fieldNames = Array.from(invalidFields)
                    .map(f => f.labels?.[0]?.textContent || f.id)
                    .filter(Boolean);
                toastr.error(`Please check these fields: ${fieldNames.join(', ')}`);
            } else {
                toastr.error('Please check all required fields');
            }
        }
    
        console.log('Form validation result:', isValid);
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