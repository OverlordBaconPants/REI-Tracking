/**
 * renderer.js
 * Handles rendering analysis reports in the UI
 */

import AnalysisRegistry from './registry.js';
import Utils from './ui-helpers.js';

const AnalysisRenderer = {
  /**
   * Populate the reports tab with analysis data
   * @param {Object} analysisData - The analysis data to render
   * @returns {Promise<boolean>} Success indicator
   */
  async populateReportsTab(analysisData) {
    console.log('Renderer: Populating reports tab with data:', analysisData);
    
    try {
      if (!analysisData) {
        throw new Error('No analysis data provided');
      }
      
      const analysisType = analysisData.analysis_type;
      
      // Get the handler for this analysis type
      const handler = AnalysisRegistry.getHandler(analysisType);
      if (!handler) {
        throw new Error(`No handler registered for type: ${analysisType}`);
      }
      
      // Generate report content
      const reportContent = await handler.generateReport(analysisData);
      
      // Generate comps HTML
      const compsHtml = this.getCompsHTML(analysisData);
      
      // Combine everything into the final content
      const finalContent = `
        <div class="row align-items-center mb-4">
            <div class="col">
                <h4 class="mb-0">${analysisType || 'Analysis'}: ${analysisData.analysis_name || 'Untitled'}</h4>
            </div>
            <div class="col-auto">
                <div class="d-flex gap-2">
                    <button type="button" class="btn btn-secondary" id="downloadPdfBtn" data-analysis-id="${analysisData.id}">
                        <i class="bi bi-file-earmark-pdf me-1"></i>Download PDF
                    </button>
                    <button type="button" class="btn btn-primary" id="reEditButton" data-analysis-id="${analysisData.id}">
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
        
        // Initialize comps if available
        if (analysisData.comps_data && window.compsHandler) {
          window.compsHandler.displayExistingComps(analysisData.comps_data);
        }
        
        // Attach event handlers
        this.initReportEventHandlers(analysisData.id);
      }
      
      return true;
    } catch (error) {
      console.error('Error populating reports tab:', error);
      
      // Display error message in the reports tab
      const reportsContent = document.querySelector('#reports');
      if (reportsContent) {
        reportsContent.innerHTML = `
          <div class="alert alert-danger">
            <i class="bi bi-exclamation-circle-fill me-2"></i>
            Error generating report: ${error.message}
          </div>`;
      }
      
      return false;
    }
  },
  
  /**
   * Generate HTML for the comps section
   * @param {Object} analysisData - Analysis data object
   * @returns {string} The HTML for the comps section
   */
  getCompsHTML(analysisData) {
    // Check for existing comps
    const hasExistingComps = analysisData.comps_data && 
                             Array.isArray(analysisData.comps_data.comparables) && 
                             analysisData.comps_data.comparables.length > 0;
    
    return `
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

              <!-- MAO Section -->
              <div id="maoSection" style="display: none;" class="alert alert-primary mb-4">
                  <div class="row align-items-center">
                      <div class="col-12 col-md-6 mb-3 mb-md-0">
                          <h6 class="mb-1">Maximum Allowable Offer (MAO):</h6>
                          <h4 class="mb-0" id="maoValue">$0</h4>
                          <p class="small mb-0 mt-2">
                              <button type="button" class="btn btn-sm btn-outline-primary" id="useMaoButton">
                                  <i class="bi bi-pencil-square me-1"></i>Use MAO as Purchase Price
                              </button>
                          </p>
                      </div>
                      <div class="col-12 col-md-6">
                          <div class="accordion" id="maoDetailsAccordion">
                              <div class="accordion-item">
                                  <h2 class="accordion-header" id="maoDetailsHeading">
                                      <button class="accordion-button collapsed py-2" type="button" 
                                              data-bs-toggle="collapse" data-bs-target="#maoDetailsCollapse">
                                          <small>Show Calculation Details</small>
                                      </button>
                                  </h2>
                                  <div id="maoDetailsCollapse" class="accordion-collapse collapse" 
                                      data-bs-parent="#maoDetailsAccordion">
                                      <div class="accordion-body p-0" id="maoDetailsBody">
                                          <!-- MAO details will be inserted here -->
                                      </div>
                                  </div>
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
      </div>`;
  },
  
  /**
   * Initialize event handlers for the report
   * @param {string} analysisId - The analysis ID
   */
  initReportEventHandlers(analysisId) {
    // Handle Re-Edit Analysis button
    const reEditButton = document.getElementById('reEditButton');
    if (reEditButton) {
      reEditButton.addEventListener('click', () => {
        // Set the button's data attribute to ensure we have the ID
        reEditButton.setAttribute('data-analysis-id', analysisId);
        
        // Check if we're already in edit mode with the correct ID
        const currentForm = document.getElementById('analysisForm');
        if (currentForm) {
          const currentId = currentForm.getAttribute('data-analysis-id');
          
          // If we don't have an ID or it's different, set it explicitly
          if (!currentId || currentId !== analysisId) {
            currentForm.setAttribute('data-analysis-id', analysisId);
            console.log(`Updated form with analysis ID: ${analysisId}`);
          }
        }
        
        // Switch to the financial tab to edit
        Utils.switchToFinancialTab();
        
        // Emit an event that can be caught by the core system
        if (window.AnalysisCore && window.AnalysisCore.events) {
          window.AnalysisCore.events.emit('edit:requested', analysisId);
        }
      });
    }
    
    // Handle PDF download button
    const downloadPdfBtn = document.getElementById('downloadPdfBtn');
    if (downloadPdfBtn) {
      downloadPdfBtn.addEventListener('click', () => {
        this.downloadPdf(analysisId);
      });
    }
    
    // Initialize tooltips
    Utils.initTooltips();
  },
  
  /**
   * Download a PDF for the analysis
   * @param {string} analysisId - The analysis ID
   */
  downloadPdf(analysisId) {
    if (!analysisId) {
      console.error('No analysis ID available');
      Utils.showToast('error', 'Unable to generate PDF: No analysis ID found');
      return;
    }
    
    // Get button reference
    const downloadBtn = document.getElementById('downloadPdfBtn');
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
        downloadBtn.innerHTML = '<i class="bi bi-file-earmark-pdf me-1"></i>Download PDF';
      }
    }, 2000);
  },
  
  /**
   * Generate KPI card for an analysis
   * @param {Object} analysis - The analysis data
   * @returns {string} HTML for the KPI card
   */
  generateKPICard(analysis) {
    // Early return if no metrics available
    if (!analysis || !analysis.calculated_metrics) {
      return `
        <div class="card mb-4">
          <div class="card-header">
            <h5 class="mb-0">Key Performance Indicators</h5>
          </div>
          <div class="card-body text-center">
            <p>KPIs unavailable - analysis has not been saved or metrics are missing.</p>
          </div>
        </div>`;
    }
    
    // Prepare KPI data
    const kpiData = this.prepareKPIData(analysis);
    
    // Render the KPI card
    return this.renderKPICard(kpiData);
  },
  
  /**
   * Prepare KPI data for display
   * @param {Object} analysis - The analysis data
   * @returns {Object} Formatted KPI data
   */
  prepareKPIData(analysis) {
    const metrics = analysis.calculated_metrics || {};
    const analysisType = analysis.analysis_type || '';
    
    // Get KPI configuration based on analysis type
    const kpiConfig = this.getKPIConfig(analysisType);
    
    // Process metrics into KPI data
    const kpiData = {};
    
    // Process NOI
    if (kpiConfig.noi) {
      const noiValue = Utils.extractNumericValue(metrics.monthly_noi || metrics.noi);
      kpiData.noi = {
        label: kpiConfig.noi.label,
        value: noiValue,
        formatted_value: `${noiValue.toFixed(2)}`,
        threshold: `${kpiConfig.noi.threshold.toFixed(2)}`,
        info: kpiConfig.noi.info,
        is_favorable: noiValue >= kpiConfig.noi.threshold
      };
    }
    
    // Process Cap Rate
    if (kpiConfig.capRate && (metrics.cap_rate || metrics.capRate)) {
      const capRateValue = Utils.extractPercentageValue(metrics.cap_rate || metrics.capRate);
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
      const cocValue = Utils.extractPercentageValue(metrics.cash_on_cash_return || metrics.cashOnCash);
      kpiData.cash_on_cash = {
        label: kpiConfig.cashOnCash.label,
        value: cocValue,
        formatted_value: `${cocValue.toFixed(2)}%`,
        threshold: `≥ ${kpiConfig.cashOnCash.threshold.toFixed(2)}%`,
        info: kpiConfig.cashOnCash.info,
        is_favorable: cocValue >= kpiConfig.cashOnCash.threshold
      };
    }
    
    // Process DSCR
    if (kpiConfig.dscr && (metrics.dscr || metrics.DSCR)) {
      const dscrValue = Utils.extractNumericValue(metrics.dscr || metrics.DSCR);
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
      const expenseRatioValue = Utils.extractPercentageValue(metrics.operating_expense_ratio || metrics.expenseRatio);
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
  
  /**
   * Get KPI configuration for an analysis type
   * @param {string} analysisType - The analysis type
   * @returns {Object} KPI configuration
   */
  getKPIConfig(analysisType) {
    // Default to LTR configuration
    let config = this.KPI_CONFIGS.LTR;
    
    if (analysisType.includes('BRRRR')) {
      config = this.KPI_CONFIGS.BRRRR;
    } else if (analysisType === 'Multi-Family') {
      config = this.KPI_CONFIGS['Multi-Family'];
    } else if (analysisType === 'Lease Option') {
      config = this.KPI_CONFIGS['Lease Option'];
    }
    
    return config;
  },
  
  /**
   * Render a KPI card from prepared data
   * @param {Object} kpiData - The prepared KPI data
   * @returns {string} HTML for the KPI card
   */
  renderKPICard(kpiData) {
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
  
  // KPI Configurations for different analysis types
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
  
  /**
   * Create HTML for notes section
   * @param {string} notes - The notes content
   * @returns {string} HTML for notes section
   */
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
      </div>`;
  }
};

// Export the renderer
export default AnalysisRenderer;
