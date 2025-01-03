const viewTransactionsModule = {
    init: async function() {
        try {
            console.log('Initializing view transactions module');
            
            // Get URL parameters
            const urlParams = new URLSearchParams(window.location.search);
            
            // Handle filters if present
            const filters = urlParams.get('filters');
            if (filters) {
                try {
                    const filterState = JSON.parse(decodeURIComponent(filters));
                    this.restoreFilters(filterState);
                    
                    // Check for refresh parameter
                    const refresh = urlParams.get('refresh');
                    if (refresh) {
                        // Small delay to ensure filters are applied first
                        setTimeout(() => {
                            this.forceDataRefresh();
                        }, 100);
                    }
                } catch (e) {
                    console.error('Error restoring filters:', e);
                }
            }
            
            this.initializeDashboard();
            this.initializeMessageHandler();
            this.initializeDeleteHandlers();
        } catch (error) {
            console.error('Error initializing View Transactions module:', error);
            toastr.error('Error loading View Transactions module: ' + error.message);
        }
    },

    handleDeleteTransaction: function(transactionId, description) {
        // Create and show modal
        const modalHtml = `
            <div class="modal fade" id="deleteConfirmModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Delete Transaction</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            Are you sure you want to delete the transaction "${description}"? This action cannot be undone.
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-danger" onclick="viewTransactionsModule.deleteTransaction(${transactionId})">Delete</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal if any
        const existingModal = document.getElementById('deleteConfirmModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Add new modal to document
        document.body.insertAdjacentHTML('beforeend', modalHtml);

        // Show the modal
        const modal = new bootstrap.Modal(document.getElementById('deleteConfirmModal'));
        modal.show();
    },

    deleteTransaction: async function(transactionId) {
        try {
            const response = await fetch(`/transactions/delete/${transactionId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Trigger refresh of the Dash table
                this.forceDataRefresh();
                toastr.success('Transaction deleted successfully');
            } else {
                toastr.error(data.message || 'Error deleting transaction');
            }
        } catch (error) {
            console.error('Error:', error);
            toastr.error('Error deleting transaction');
        }
    },
    
    // Add event listener for delete buttons
    initializeDeleteHandlers: function() {
        document.addEventListener('click', (e) => {
            if (e.target.matches('.delete-transaction')) {
                const transactionId = e.target.dataset.transactionId;
                if (confirm('Are you sure you want to delete this transaction? This action cannot be undone.')) {
                    this.deleteTransaction(transactionId);
                }
            }
        });
    },

    initializeDashboard: function() {
        console.log('Initializing transactions dashboard');
        
        // Check for success message in URL
        const urlParams = new URLSearchParams(window.location.search);
        const successMessage = urlParams.get('success');
        if (successMessage) {
            toastr.success(decodeURIComponent(successMessage));
        }
        
        // Check for any flash messages that need to be displayed
        const flashMessages = document.querySelectorAll('.flash-message');
        flashMessages.forEach(message => {
            const category = message.dataset.category || 'info';
            const text = message.textContent;
            
            switch(category.toLowerCase()) {
                case 'success':
                    toastr.success(text);
                    break;
                case 'error':
                    toastr.error(text);
                    break;
                case 'warning':
                    toastr.warning(text);
                    break;
                default:
                    toastr.info(text);
            }
            
            // Remove the message from DOM after displaying
            message.remove();
        });
    },

    initializeMessageHandler: function() {
        window.addEventListener('message', (event) => {
            console.log('Received message in view transactions:', event.data);
            
            if (event.data.type === 'transactionUpdated') {
                if (event.data.shouldRefresh) {
                    // Trigger Dash callback to refresh data
                    if (window.dash_clientside) {
                        window.dash_clientside.no_update = Symbol('no_update');
                        const store = document.querySelector('#refresh-trigger');
                        if (store) {
                            store.value = Date.now();
                            const event = new Event('change');
                            store.dispatchEvent(event);
                        }
                    }
                    
                    // Show success notification
                    toastr.success('Transaction updated successfully');
                } else {
                    // Show info notification for cancelled edit
                    toastr.info(event.data.message || 'Edit cancelled');
                }
            } else if (event.data.type === 'bulkImportCompleted') {
                // Handle bulk import completion
                const stats = event.data.stats;
                toastr.success(
                    `Successfully processed ${stats.total_processed} rows, saved ${stats.total_saved} transactions`
                );
                
                if (stats.total_modified > 0) {
                    toastr.warning(
                        `${stats.total_modified} rows had modifications. Check the notifications for details.`
                    );
                }
                
                // Process any modifications
                if (event.data.modifications) {
                    this.showModificationNotifications(event.data.modifications);
                }
            }
        });
    },

    restoreFilters: function(filterState) {
        console.log('Restoring filters:', filterState);
        
        // Update filter store to trigger Dash callback
        const filterStore = document.getElementById('filter-options');
        if (filterStore) {
            filterStore.value = JSON.stringify(filterState);
            const event = new Event('change');
            filterStore.dispatchEvent(event);
        }
    },

    forceDataRefresh: function() {
        console.log('Forcing data refresh');
        const refreshTrigger = document.getElementById('refresh-trigger');
        if (refreshTrigger) {
            refreshTrigger.value = Date.now();
            const event = new Event('change');
            refreshTrigger.dispatchEvent(event);
        }
    },

    showModificationNotifications: function(modifications) {
        // Group modifications by row
        const groupedMods = modifications.reduce((acc, mod) => {
            if (!acc[mod.row]) {
                acc[mod.row] = [];
            }
            acc[mod.row].push(mod);
            return acc;
        }, {});
        
        // Show notifications for each row's modifications
        Object.entries(groupedMods).forEach(([row, mods]) => {
            const messages = mods.map(mod => mod.message);
            toastr.warning(
                `Row ${row}:<br>${messages.join('<br>')}`,
                'Data Modifications',
                { 
                    timeOut: 10000, 
                    extendedTimeOut: 5000,
                    closeButton: true,
                    progressBar: true,
                    newestOnTop: false,
                    preventDuplicates: true
                }
            );
        });
    }
};

// Configure toastr options
toastr.options = {
    closeButton: true,
    progressBar: true,
    newestOnTop: false,
    positionClass: "toast-top-right",
    preventDuplicates: true,
    onclick: null,
    showDuration: "300",
    hideDuration: "1000",
    timeOut: "1000",  // Updated to match our delay
    extendedTimeOut: "1000",
    showEasing: "swing",
    hideEasing: "linear",
    showMethod: "fadeIn",
    hideMethod: "fadeOut"
};

export default viewTransactionsModule;