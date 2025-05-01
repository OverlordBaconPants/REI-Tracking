/**
 * core.js
 * Core functionality for the analysis module system
 */

// Main namespace for the analysis system
const AnalysisCore = {
  // Current state
  state: {
    analysisId: null,
    analysisType: null,
    isSubmitting: false,
    typeChangeInProgress: false,
    initialized: false,
  },

  // Event system
  events: {
    listeners: {},
    
    // Subscribe to an event
    on(eventName, callback) {
      if (!this.listeners[eventName]) {
        this.listeners[eventName] = [];
      }
      this.listeners[eventName].push(callback);
      return this;
    },
    
    // Unsubscribe from an event
    off(eventName, callback) {
      if (!this.listeners[eventName]) return this;
      
      if (callback) {
        this.listeners[eventName] = this.listeners[eventName].filter(cb => cb !== callback);
      } else {
        delete this.listeners[eventName];
      }
      return this;
    },
    
    // Trigger an event
    emit(eventName, ...args) {
      if (!this.listeners[eventName]) return;
      
      this.listeners[eventName].forEach(callback => {
        try {
          callback(...args);
        } catch (error) {
          console.error(`Error in event listener for ${eventName}:`, error);
        }
      });
      return this;
    }
  },

  // Initialize the core system
  async init() {
    console.log('Analysis Core: Initializing');
    
    try {
      // Avoid double initialization
      if (this.state.initialized) {
        console.log('Analysis Core already initialized');
        return true;
      }
      
      // Load other modules
      await this.loadModules();
      
      // Initialize UI elements
      this.initUI();
      
      // Extract current analysis ID if present
      this.state.analysisId = this.getAnalysisIdFromUrl();
      
      // Handle edit requests from the renderer
      this.events.on('edit:requested', (analysisData) => {
        console.log(`Edit requested for analysis: ${typeof analysisData === 'object' ? analysisData.id : analysisData}`);
        
        // Get the ID whether we received an object or just the ID string
        let analysisId = typeof analysisData === 'object' ? analysisData.id : analysisData;
        
        if (!analysisId) {
          console.error('No analysis ID provided for edit request');
          return;
        }
        
        // Set the analysis ID in our state
        this.state.analysisId = analysisId;
        
        // Find the form and set the ID
        const form = document.getElementById('analysisForm');
        if (form) {
          form.setAttribute('data-analysis-id', analysisId);
          
          // Also add or update hidden input
          let idInput = form.querySelector('input[name="id"]');
          if (!idInput) {
            idInput = document.createElement('input');
            idInput.type = 'hidden';
            idInput.name = 'id';
            form.appendChild(idInput);
          }
          idInput.value = analysisId;
          
          // If we need to load the analysis data
          if (!this.state.analysisData || this.state.analysisData.id !== analysisId) {
            this.loadAnalysis(analysisId).catch(error => {
              console.error('Failed to load analysis for editing:', error);
              this.ui.showToast('error', 'Failed to load analysis data for editing');
            });
          }
        }
      });
  
      // Add event listener for reports tab population - NEW CODE ADDED HERE
      this.events.on('reports:populated', (analysis) => {
        if (this.comps && analysis.id) {
          console.log('Initializing comps handler from event:', analysis.id);
          this.comps.init(analysis.id);
        }
      });
  
      // Initialize based on mode (create or edit)
      if (this.state.analysisId) {
        console.log(`Analysis Core: Edit mode for analysis ${this.state.analysisId}`);
        await this.loadAnalysis(this.state.analysisId);
      } else {
        console.log('Analysis Core: Create mode');
        this.initCreateMode();
      }
      
      // Mark as initialized
      this.state.initialized = true;
      this.events.emit('core:initialized');
      
      return true;
    } catch (error) {
      console.error('Analysis Core: Initialization failed', error);
      this.displayError('Failed to initialize analysis system');
      return false;
    }
  },
  
  // Load required modules
  async loadModules() {
    try {
      // Import registry
      this.registry = await import('./registry.js').then(m => m.default);
      
      // Import utility modules
      this.renderer = await import('./renderer.js').then(m => m.default);
      this.calculator = await import('./calculator.js').then(m => m.default);
      this.validator = await import('./validators.js').then(m => m.default);
      this.ui = await import('./ui_helpers.js').then(m => m.default);
      this.comps = await import('./comps_handler.js').then(m => m.default);
      
      // Initialize registry
      await this.registry.init();
      
      this.events.emit('modules:loaded');
      return true;
    } catch (error) {
      console.error('Failed to load modules:', error);
      throw new Error('Module loading failed');
    }
  },
  
  // Initialize UI elements
  initUI() {
    // Initialize any global UI elements
    this.ui.initToastr();
    this.ui.injectStyles();
    this.ui.initViewportHandler();
    this.ui.initMobileInteractions();
    
    // Set up form event handlers
    this.initFormHandlers();
    
    // Set up analysis type change handler
    this.initAnalysisTypeHandler();
    
    // Initialize address autocomplete
    this.initAddressAutocomplete();
    
    // Initialize tab handling
    this.initTabHandling();
    
    this.events.emit('ui:initialized');
  },
  
  // Initialize form handlers
  initFormHandlers() {
    const analysisForm = document.getElementById('analysisForm');
    if (!analysisForm) return;
    
    // Handle form submission
    if (this.state.analysisId) {
      // Edit mode
      analysisForm.addEventListener('submit', (event) => this.handleEditSubmit(event));
    } else {
      // Create mode
      analysisForm.addEventListener('submit', (event) => this.handleCreateSubmit(event));
    }
    
    // Handle notes character counter
    this.ui.initNotesCounter();
  },
  
  // Initialize analysis type handler
  initAnalysisTypeHandler() {
    const analysisType = document.getElementById('analysis_type');
    const financialTab = document.getElementById('financial');
    
    if (!analysisType || !financialTab) {
      console.error('Missing required elements for analysis type handler');
      return;
    }

    // Remove existing event listeners by cloning
    const newAnalysisType = analysisType.cloneNode(true);
    analysisType.parentNode.replaceChild(newAnalysisType, analysisType);
    
    // Store initial value
    this.state.initialAnalysisType = newAnalysisType.value;
    console.log('Initial analysis type:', this.state.initialAnalysisType);
    
    // Set up event listener for changes
    newAnalysisType.addEventListener('change', async (e) => {
      // Prevent multiple concurrent changes
      if (this.state.typeChangeInProgress) {
        console.log('Type change already in progress');
        return;
      }
      
      const newType = e.target.value;
      console.log('Processing change to type:', newType);
      
      // Skip if initial type hasn't been set yet or if type hasn't actually changed
      if (!this.state.initialAnalysisType || newType === this.state.initialAnalysisType) {
        console.log('Skipping - no initial type or no change');
        return;
      }
      
      try {
        this.state.typeChangeInProgress = true;
        
        if (this.state.analysisId) {
          // In edit mode, confirm before changing
          const confirmed = await this.ui.confirmTypeChange(newType, this.state.initialAnalysisType);
          if (!confirmed) {
            e.target.value = this.state.initialAnalysisType;
            return;
          }
          await this.handleTypeChange(newType);
        } else {
          // In create mode, just update the template
          await this.loadTemplateForType(newType);
          this.state.initialAnalysisType = newType;
        }
      } catch (error) {
        console.error('Error changing analysis type:', error);
        this.ui.showToast('error', error.message || 'Error changing analysis type');
        e.target.value = this.state.initialAnalysisType;
      } finally {
        this.state.typeChangeInProgress = false;
      }
    });
  },
  
  // Initialize address autocomplete
  initAddressAutocomplete() {
    const addressInput = document.getElementById('address');
    if (!addressInput) return;
    
    this.ui.initAddressAutocomplete(addressInput);
  },
  
  // Initialize tab handling
  initTabHandling() {
    const reportTab = document.getElementById('reports-tab');
    const financialTab = document.getElementById('financial-tab');
    
    if (reportTab) {
      reportTab.addEventListener('click', () => {
        this.events.emit('tab:reports');
      });
    }
    
    if (financialTab) {
      financialTab.addEventListener('click', () => {
        this.events.emit('tab:financial');
      });
    }
  },
  
  // Get analysis ID from URL
  getAnalysisIdFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('analysis_id');
  },
  
  // Load analysis data for editing
  async loadAnalysis(analysisId) {
    try {
      console.log('Loading analysis data for ID:', analysisId);
      
      const response = await fetch(`/analyses/get_analysis/${analysisId}`);
      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.message || 'Failed to load analysis data');
      }
      
      // Store the analysis data
      this.state.analysisData = data.analysis;
      this.state.analysisType = data.analysis.analysis_type;
      this.state.initialAnalysisType = data.analysis.analysis_type;
      
      // Emit event with analysis data
      this.events.emit('analysis:loaded', data.analysis);
      
      // Load the appropriate template
      await this.loadTemplateForType(data.analysis.analysis_type);
      
      // Set form state
      const form = document.getElementById('analysisForm');
      if (form) {
        form.setAttribute('data-analysis-id', analysisId);
      }
      
      // Populate form fields after a brief delay to ensure DOM is ready
      setTimeout(() => {
        this.populateFormFields(data.analysis);
      }, 100);
      
      // Initialize comps handler with the analysis ID - Add these lines
      if (this.comps) {
        console.log('Initializing comps handler with ID:', analysisId);
        this.comps.init(analysisId);
      }
      
      return data.analysis;
    } catch (error) {
      console.error('Error loading analysis:', error);
      this.ui.showToast('error', 'Error loading analysis data');
      throw error;
    }
  },
  
  // Load template for the specified analysis type
  async loadTemplateForType(type) {
    try {
      console.log('Loading template for type:', type);
      
      const financialTab = document.getElementById('financial');
      if (!financialTab) {
        throw new Error('Financial tab container not found');
      }
      
      // Get handler for this analysis type
      const handler = this.registry.getHandler(type);
      if (!handler) {
        throw new Error(`No handler registered for analysis type: ${type}`);
      }
      
      // Get template HTML
      const template = await handler.getTemplate();
      
      // Apply template
      financialTab.innerHTML = template;
      
      // Initialize type-specific handlers
      await handler.initHandlers();
      
      // Initialize shared handlers
      this.ui.initNotesCounter();
      
      // Emit event
      this.events.emit('template:loaded', type);
      
      return true;
    } catch (error) {
      console.error('Error loading template:', error);
      throw error;
    }
  },
  
  // Initialize create mode
  initCreateMode() {
    // Set initial analysis type
    const analysisType = document.getElementById('analysis_type');
    if (analysisType) {
      this.state.initialAnalysisType = analysisType.value;
      this.loadTemplateForType(this.state.initialAnalysisType).then(() => {
        // Initialize comps handler for new analysis mode
        if (this.comps) {
          console.log('Initializing comps handler for new analysis mode');
          this.comps.init('new');
        }
      });
    }
  },

  getCompsCardHTML() {
    return `
      <!-- Comparable Properties Card -->
      <div class="card mb-4">
        <div class="card-header">
          <div class="d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Comparable Properties and MAO</h5>
            <span id="compsRunCount" class="badge bg-info" style="display: none;">
              Run <span id="runCountValue">0</span>
            </span>
          </div>
        </div>
        <div class="card-body comps-container">
          <div id="initialCompsMessage">
            <p class="mb-3">Run the comparables tool to see similar properties in the area and get an estimated After Repair Value (ARV).</p>
          </div>
          
          <div id="compsLoading" style="display: none;">
            <div class="d-flex justify-content-center my-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <p class="text-center">Fetching comparable properties...</p>
          </div>
          
          <div id="compsError" class="alert alert-danger" style="display: none;">
            <i class="bi bi-exclamation-triangle-fill me-2"></i>
            <span id="compsErrorMessage">Error fetching comps</span>
          </div>
          
          <!-- The key metrics section will be dynamically inserted here by comps_handler.js -->
          
          <!-- Comparable Sales section will be dynamically inserted here by comps_handler.js -->
          
          <!-- Comparable Rentals section will be dynamically inserted here by comps_handler.js -->
          
          <!-- Run Comps button will be inside key metrics section in the new design -->
        </div>
      </div>
    `;
  },
  
  // Populate form fields with analysis data
  populateFormFields(analysis) {
    try {
      console.log('Populating form fields with analysis data');
      
      // Get handler for this analysis type
      const handler = this.registry.getHandler(analysis.analysis_type);
      if (!handler) {
        throw new Error(`No handler registered for analysis type: ${analysis.analysis_type}`);
      }
      
      // Set analysis type first
      this.setFieldValue('analysis_type', analysis.analysis_type);
      
      // Set basic fields
      this.setFieldValue('analysis_name', analysis.analysis_name);
      this.setFieldValue('address', analysis.address);
      
      // Set property details
      this.setFieldValue('property_type', analysis.property_type);
      this.setFieldValue('square_footage', analysis.square_footage);
      this.setFieldValue('lot_size', analysis.lot_size);
      this.setFieldValue('year_built', analysis.year_built);
      this.setFieldValue('bedrooms', analysis.bedrooms);
      this.setFieldValue('bathrooms', analysis.bathrooms);
      
      // Set notes
      this.setFieldValue('notes', analysis.notes || '');
      
      // Let the type-specific handler set its fields
      handler.populateFields(analysis);
      
      // Emit event
      this.events.emit('form:populated', analysis);
    } catch (error) {
      console.error('Error populating form fields:', error);
      this.ui.showToast('error', 'Error populating form fields');
    }
  },
  
  // Set the value of a form field
  setFieldValue(fieldId, value) {
    const field = document.getElementById(fieldId);
    if (!field) return false;
    
    if (field.type === 'checkbox') {
      field.checked = Boolean(value);
    } else {
      field.value = (value !== null && value !== undefined) ? value : '';
    }
    
    const event = new Event('change', { bubbles: true });
    field.dispatchEvent(event);
    return true;
  },
  
  // Handle analysis type change in edit mode
  async handleTypeChange(newType) {
    try {
      const currentForm = document.getElementById('analysisForm');
      const analysisId = currentForm.getAttribute('data-analysis-id');
      if (!analysisId) throw new Error('No analysis ID found');
      
      // Create new analysis data
      const formData = new FormData(currentForm);
      const analysisData = {
        ...Object.fromEntries(formData.entries()),
        id: analysisId,  // Preserve the original ID
        analysis_type: newType
      };
      
      // Make API call to update the existing analysis
      const response = await fetch('/analyses/update_analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(analysisData)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Update failed');
      }
      
      const data = await response.json();
      if (!data.success) {
        throw new Error(data.message || 'Error updating analysis');
      }
      
      // Update state
      this.state.analysisType = newType;
      this.state.initialAnalysisType = newType;
      
      // Load the new template
      await this.loadTemplateForType(newType);
      
      // Keep the same analysis ID in the form
      currentForm.setAttribute('data-analysis-id', analysisId);
      
      // Populate form fields
      setTimeout(() => {
        this.populateFormFields(data.analysis);
      }, 100);
      
      this.ui.showToast('success', `Updated to ${newType} analysis type`);
      
      return data.analysis;
    } catch (error) {
      console.error('Error during type change:', error);
      this.ui.showToast('error', error.message || 'Error changing analysis type');
      throw error;
    }
  },
  
  // Handle form submission in create mode
  async handleCreateSubmit(event) {
    event.preventDefault();
    
    if (this.state.isSubmitting) {
      console.log('Form submission already in progress');
      return;
    }
    
    try {
      this.state.isSubmitting = true;
      const form = event.target;
      
      // Get submit button
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Creating...';
      }
      
      // Validate form
      if (!this.validator.validateForm(form)) {
        throw new Error('Form validation failed');
      }
      
      // Get current analysis type
      const analysisType = form.querySelector('#analysis_type').value;
      
      // Get handler for this analysis type
      const handler = this.registry.getHandler(analysisType);
      if (!handler) {
        throw new Error(`No handler registered for analysis type: ${analysisType}`);
      }
      
      // Get form data
      const formData = new FormData(form);
      let analysisData = Object.fromEntries(formData.entries());
      
      // Let the handler process its type-specific data
      analysisData = await handler.processFormData(formData, analysisData);
      
      // Make API call
      const response = await fetch('/analyses/create_analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(analysisData)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Create failed');
      }
      
      const data = await response.json();
      if (!data.success) {
        throw new Error(data.message || 'Error creating analysis');
      }
      
      // Update state
      this.state.analysisId = data.analysis.id;
      
      // Populate reports tab and switch to it
      await this.renderer.populateReportsTab(data.analysis);

      // Initialize comps handler for the new analysis
      if (this.comps) {
        console.log('Initializing comps handler for new analysis:', data.analysis.id);
        this.comps.init(data.analysis.id);
      }
      this.ui.switchToReportsTab();
      
      this.ui.showToast('success', 'Analysis created successfully');
      
      return data.analysis;
    } catch (error) {
      console.error('Error creating analysis:', error);
      this.ui.showToast('error', error.message || 'Error creating analysis');
    } finally {
      this.state.isSubmitting = false;
      const submitBtn = event.target.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Create Analysis';
      }
    }
  },
  
  // Handle form submission in edit mode
  async handleEditSubmit(event) {
    event.preventDefault();
    
    if (this.state.isSubmitting) {
      console.log('Form submission already in progress');
      return;
    }
    
    const form = event.target;
    
    // Get analysis ID with better fallbacks
    let analysisId = form.getAttribute('data-analysis-id');
    
    // If not found in attribute, check for hidden input
    if (!analysisId) {
      const hiddenIdField = form.querySelector('input[name="id"]');
      if (hiddenIdField) {
        analysisId = hiddenIdField.value;
      }
    }
    
    // If still not found, check state
    if (!analysisId) {
      analysisId = this.state.analysisId;
    }
    
    if (!analysisId) {
      console.error('No analysis ID found for edit operation');
      this.ui.showToast('error', 'No analysis ID found');
      return;
    }
    
    // Log found ID
    console.log(`Editing analysis with ID: ${analysisId}`);
    
    try {
      this.state.isSubmitting = true;
      
      // Get submit button
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Updating...';
      }
      
      // Validate form
      if (!this.validator.validateForm(form)) {
        throw new Error('Form validation failed');
      }
      
      // Get form data
      const formData = new FormData(form);
      
      // CRITICAL: Force the ID to be included in the formData
      if (!formData.has('id')) {
        formData.append('id', analysisId);
      }
      
      let analysisData = Object.fromEntries(formData.entries());
      
      // DOUBLE CHECK: Make sure the ID is explicitly set
      if (analysisData.id !== analysisId) {
        console.log(`Correcting analysis ID mismatch: ${analysisData.id} -> ${analysisId}`);
        analysisData.id = analysisId;
      }
      
      // Get current analysis to preserve comps data
      const currentResponse = await fetch(`/analyses/get_analysis/${analysisId}`);
      if (!currentResponse.ok) {
        throw new Error('Failed to fetch current analysis data');
      }
      const currentData = await currentResponse.json();
      const existingComps = currentData.analysis?.comps_data;
      
      // Add comps data back
      if (existingComps) {
        analysisData.comps_data = existingComps;
      }
      
      // Log the final data to be sent
      console.log(`Updating analysis ${analysisId} with data:`, {
        id: analysisData.id,
        analysis_name: analysisData.analysis_name,
        analysis_type: analysisData.analysis_type
      });
      
      // Make API call - EXPLICITLY to update_analysis endpoint
      const response = await fetch('/analyses/update_analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(analysisData)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Update failed');
      }
      
      const data = await response.json();
      if (!data.success) {
        throw new Error(data.message || 'Error updating analysis');
      }
      
      // Verify returned analysis has same ID
      if (data.analysis.id !== analysisId) {
        console.error(`Server returned different analysis ID: ${data.analysis.id} vs original ${analysisId}`);
      }
      
      // Populate reports tab and switch to it
      await this.renderer.populateReportsTab(data.analysis);
      
      // Initialize comps handler
      if (this.comps) {
        console.log(`Initializing comps handler for updated analysis: ${data.analysis.id}`);
        this.comps.init(data.analysis.id);
      }

      this.ui.switchToReportsTab();
      
      this.ui.showToast('success', 'Analysis updated successfully');
      
      return data.analysis;
    } catch (error) {
      console.error('Error updating analysis:', error);
      this.ui.showToast('error', error.message || 'Error updating analysis');
    } finally {
      this.state.isSubmitting = false;
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="bi bi-save me-2"></i>Update Analysis';
      }
    }
  },
  
  // Display an error message
  displayError(message) {
    console.error(message);
    this.ui.showToast('error', message);
  }
};

// Export the core
export default AnalysisCore;
