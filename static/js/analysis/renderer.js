/**
 * renderer.js
 * Handles rendering analysis reports in the UI
 */

import AnalysisRegistry from './registry.js';
import Utils from './ui_helpers.js';
import AnalysisCore from './core.js';

const AnalysisRenderer = {
  /**
   * Populate the reports tab with analysis data
   * @param {Object} analysisData - The analysis data
   * @returns {Promise<boolean>} Success indicator
   */
  async populateReportsTab(analysisData) {
    console.log('Renderer: Populating reports tab with data:', analysisData);
    
    try {
      const reportsTab = document.getElementById('reports');
      if (!reportsTab) {
        console.error('Reports tab container not found');
        return false;
      }
      
      // Get handler for this analysis type
      const handler = AnalysisCore.registry.getHandler(analysisData.analysis_type);
      if (!handler) {
        console.error(`No handler registered for analysis type: ${analysisData.analysis_type}`);
        return false;
      }
      
      // Get report content
      const reportContent = handler.generateReport(analysisData);
      
      // Create the reports page structure without the comps card
      reportsTab.innerHTML = `
        <div class="container-fluid my-4">
          <div class="row">
            <div class="col-12">
              <div class="d-flex justify-content-between align-items-center mb-4">
                <h2 class="mb-0">${analysisData.analysis_name || 'Analysis Results'}</h2>
                <div>
                  <button id="editAnalysisBtn" class="btn btn-primary">
                    <i class="bi bi-pencil-square me-2"></i>Edit Analysis
                  </button>
                  <button id="exportPdfBtn" class="btn btn-outline-secondary ms-2">
                    <i class="bi bi-file-earmark-pdf me-2"></i>Export PDF
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <div class="row">
            <!-- Financial Results Column - Full width now -->
            <div class="col-12 mb-4">
              <div class="card">
                <div class="card-header">
                  <h4 class="mb-0">Financial Results</h4>
                </div>
                <div class="card-body px-0 py-0">
                  <div class="financial-results">
                    ${reportContent}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>`;
      
      // Add event handlers for reports tab buttons
      this.addReportEventHandlers(analysisData);
      
      console.log('Reports tab populated successfully');
      
      // Emit event when reports tab is populated
      if (window.analysisModule && window.analysisModule.core && 
          window.analysisModule.core.events) {
        window.analysisModule.core.events.emit('reports:populated', analysisData);
      } else {
        // Fallback - dispatch a custom DOM event
        const event = new CustomEvent('reports:populated', { 
          detail: { analysisData } 
        });
        document.dispatchEvent(event);
      }
      
      return true;
    } catch (error) {
      console.error('Error populating reports tab:', error);
      return false;
    }
  },
  
  /**
   * Add event handlers for the reports tab buttons
   * @param {Object} analysisData - The analysis data
   */
  addReportEventHandlers(analysisData) {
    const analysisId = analysisData.id;
    console.log(`Adding report event handlers for analysis: ${analysisId}`);
    
    // Handle Edit Analysis button
    const editAnalysisBtn = document.getElementById('editAnalysisBtn');
    if (editAnalysisBtn) {
      editAnalysisBtn.addEventListener('click', () => {
        console.log(`Edit Analysis button clicked for: ${analysisId}`);
        
        // Set ID attribute on button for reference
        editAnalysisBtn.setAttribute('data-analysis-id', analysisId);
        
        // Set core state if available
        if (window.AnalysisCore) {
          window.AnalysisCore.state.analysisId = analysisId;
        }
        
        // Create a data object if needed
        const editData = typeof analysisData === 'object' ? analysisData : { id: analysisId };
        
        // Emit edit request event with the data
        if (window.AnalysisCore && window.AnalysisCore.events) {
          window.AnalysisCore.events.emit('edit:requested', editData);
        } else {
          // Use custom event as fallback
          const event = new CustomEvent('edit:requested', { 
            detail: { analysisData: editData } 
          });
          document.dispatchEvent(event);
        }
        
        // Switch to financial tab
        const financialTab = document.getElementById('financial-tab');
        if (financialTab) {
          financialTab.click();
        }
      });
    }
    
    // Export PDF button handler remains the same
    const exportPdfBtn = document.getElementById('exportPdfBtn');
    if (exportPdfBtn) {
      exportPdfBtn.addEventListener('click', () => {
        console.log(`Export PDF button clicked for: ${analysisId}`);
        this.exportPdf(analysisId);
      });
    }
  },

  /**
   * Export a PDF for the analysis
   * @param {string} analysisId - The analysis ID
   */
  exportPdf(analysisId) {
    if (!analysisId) {
      console.error('No analysis ID available for PDF export');
      if (typeof Utils.showToast === 'function') {
        Utils.showToast('error', 'Unable to generate PDF: No analysis ID found');
      } else {
        alert('Unable to generate PDF: No analysis ID found');
      }
      return;
    }
    
    // Get button reference
    const exportBtn = document.getElementById('exportPdfBtn');
    if (exportBtn) {
      // Show loading state
      exportBtn.disabled = true;
      exportBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generating PDF...';
    }
    
    // Create hidden form for download
    const form = document.createElement('form');
    form.method = 'GET';
    form.action = `/analyses/generate_pdf/${analysisId}`; // Correct path to match your backend route
    document.body.appendChild(form);
    
    // Submit form to trigger download
    form.submit();
    document.body.removeChild(form);
    
    // Reset button after delay
    setTimeout(() => {
      if (exportBtn) {
        exportBtn.disabled = false;
        exportBtn.innerHTML = '<i class="bi bi-file-earmark-pdf me-2"></i>Export PDF';
      }
    }, 2000);
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
              </div>
          </div>
          <div class="card-body comps-container">
              <!-- Initial State Message -->
              <div id="initialCompsMessage" class="text-center py-4" ${hasExistingComps ? 'style="display: none;"' : ''}>
                  <p class="text-muted mb-0">Click "Run Comps" to fetch comparable properties and estimate values</p>
                  <div class="mt-3">
                      <button id="runCompsBtn" class="btn btn-primary">
                          <i class="bi bi-graph-up me-2"></i>Run Comps
                      </button>
                  </div>
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

              <!-- The key metrics section will be dynamically inserted here by comps_handler.js -->
              
              <!-- Comparable Sales section will be dynamically inserted here by comps_handler.js -->
              
              <!-- Comparable Rentals section will be dynamically inserted here by comps_handler.js -->
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
        'info': '5-10% indicates good value for Multi-Family.'
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
