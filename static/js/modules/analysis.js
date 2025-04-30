/**
 * analysis.js
 * Entry point for the analysis module - imports all components from the analysis directory
 */

// Import property type handlers
import BRRRRHandler from '../analysis/brrrr.js';
import LeaseOptionHandler from '../analysis/lease_option.js';
import LTRHandler from '../analysis/ltr.js';
import MultiFamilyHandler from '../analysis/multi_family.js';

// Import core functionality
import AnalysisCore from '../analysis/core.js';
import FormHandler from '../analysis/form_handler.js';
import PropertyDetailsHandler from '../analysis/property_details.js';
import AnalysisRegistry from '../analysis/registry.js';

// Import utility modules
import FinancialCalculator from '../analysis/calculator.js';
import AnalysisRenderer from '../analysis/renderer.js';
import UIHelpers from '../analysis/ui_helpers.js';
import AnalysisValidator from '../analysis/validators.js';
import compsHandler from '../analysis/comps_handler.js';

// Initialize the Analysis Module
const analysisModule = {
    brrrr: BRRRRHandler,
    calculator: FinancialCalculator,
    core: AnalysisCore,
    comps: compsHandler,
    form_handler: FormHandler,
    lease_option: LeaseOptionHandler,
    ltr: LTRHandler,
    multi_family: MultiFamilyHandler,
    property_details: PropertyDetailsHandler,
    registry: AnalysisRegistry,
    ui_helper: UIHelpers,
    validators: AnalysisValidator,
    
    // Initialize the module
    init: async function() {
        console.log('Analysis module initializing...');
        
        try {
            // Initialize the core module first
            await AnalysisCore.init();
            
            // Check if registry is initialized through the core
            if (AnalysisCore.registry && AnalysisCore.registry._initialized) {
                // Register handlers only after we confirm registry is initialized
                this.registerAllHandlers();
            } else {
                // If registry not initialized through core, initialize it directly
                if (!AnalysisCore.registry) {
                    AnalysisCore.registry = AnalysisRegistry;
                }
                
                // Make sure registry is initialized
                const registryReady = await AnalysisCore.registry.init();
                
                if (registryReady) {
                    // Now it's safe to register handlers
                    this.registerAllHandlers();
                } else {
                    console.warn('Registry initialization failed, handlers will not be registered');
                }
            }
            
            console.log('Analysis module initialized successfully');
            return true;
        } catch (error) {
            console.error('Failed to initialize analysis module:', error);
            return false;
        }
    },
    
    // Register all analysis type handlers
    registerAllHandlers: function() {
        // BRRRR variants
        this.registerHandler('BRRRR', BRRRRHandler);
        this.registerHandler('PadSplit BRRRR', BRRRRHandler);
        
        // LTR variants
        this.registerHandler('Long-Term Rental', LTRHandler);
        this.registerHandler('PadSplit LTR', LTRHandler);
        
        // Other property types
        this.registerHandler('Multi-Family', MultiFamilyHandler);
        this.registerHandler('Lease Option', LeaseOptionHandler);
    },
    
    // Helper method to register handlers
    registerHandler: function(type, handler) {
        // Check if registry exists and has the right method
        if (!AnalysisCore.registry) {
            console.error('Unable to register handler - registry not available');
            return;
        }
        
        // Determine the correct method name
        const registerMethod = 
            typeof AnalysisCore.registry.registerHandler === 'function' ? 'registerHandler' : 
            typeof AnalysisCore.registry.register === 'function' ? 'register' : 
            null;
        
        if (!registerMethod) {
            console.error('Unable to register handler - no valid registration method found');
            return;
        }
        
        // Register the handler using the correct method
        console.log(`Registering handler for ${type}`);
        AnalysisCore.registry[registerMethod](type, handler);
    }
};

// Expose the module to the window for the module loader
window.analysisModule = analysisModule;

// Export as default for ES modules
export default analysisModule;