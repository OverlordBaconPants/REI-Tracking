/**
 * registry.js
 * Registry for analysis types
 */

// Import handlers
import LTRHandler from './ltr.js';
import BRRRRHandler from './brrrr.js';
import LeaseOptionHandler from './lease-option.js';
import MultiFamilyHandler from './multi-family.js';

const AnalysisRegistry = {
  _handlers: {},
  _initialized: false,
  
  /**
   * Initialize the registry
   * @returns {Promise<boolean>} Success indicator
   */
  async init() {
    if (this._initialized) {
      return true;
    }
    
    try {
      console.log('Registry: Initializing analysis type registry');
      
      // Register all analysis types
      this.register('LTR', LTRHandler);
      this.register('BRRRR', BRRRRHandler);
      this.register('Lease Option', LeaseOptionHandler);
      this.register('Multi-Family', MultiFamilyHandler);
      
      // Register PadSplit variants
      this.register('PadSplit LTR', LTRHandler);
      this.register('PadSplit BRRRR', BRRRRHandler);
      
      this._initialized = true;
      console.log('Registry: Initialization complete');
      
      return true;
    } catch (error) {
      console.error('Registry: Initialization failed', error);
      return false;
    }
  },
  
  /**
   * Register a handler for an analysis type
   * @param {string} type - The analysis type
   * @param {Object} handler - The handler object
   * @returns {boolean} Success indicator
   */
  register(type, handler) {
    if (!type || typeof type !== 'string') {
      console.error('Registry: Invalid analysis type');
      return false;
    }
    
    if (!handler || typeof handler !== 'object') {
      console.error('Registry: Invalid handler object');
      return false;
    }
    
    this._handlers[type] = handler;
    console.log(`Registry: Registered handler for ${type}`);
    return true;
  },
  
  /**
   * Get the handler for an analysis type
   * @param {string} type - The analysis type
   * @returns {Object|null} The handler or null if not found
   */
  getHandler(type) {
    const handler = this._handlers[type];
    
    if (!handler) {
      console.warn(`Registry: No handler found for ${type}`);
      return null;
    }
    
    return handler;
  },
  
  /**
   * Check if a handler exists for an analysis type
   * @param {string} type - The analysis type
   * @returns {boolean} Whether a handler exists
   */
  hasHandler(type) {
    return !!this._handlers[type];
  },
  
  /**
   * Get all registered analysis types
   * @returns {string[]} Array of analysis types
   */
  getTypes() {
    return Object.keys(this._handlers);
  }
};

// Export the registry
export default AnalysisRegistry;