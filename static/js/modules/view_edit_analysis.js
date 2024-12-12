// Create the module
const viewEditAnalysisModule = {
    init: function() {
        console.log('Initializing view/edit analysis module');
        this.initToastr();
    },

    initToastr: function() {
        // Configure toastr options
        toastr.options = {
            closeButton: true,
            progressBar: true,
            positionClass: 'toast-top-right',
            preventDuplicates: true,
            timeOut: 3000
        };
    },

    editAnalysis: function(analysisId) {
        console.log('editAnalysis called with ID:', analysisId);
        if (!analysisId) {
            console.error('No analysis ID provided');
            toastr.error('No analysis ID provided');
            return;
        }
        const url = `/analyses/create_analysis?analysis_id=${analysisId}`;
        console.log('Navigating to:', url);
        window.location.href = url;
    },

    downloadPdf: function(analysisId) {
        console.log('Downloading PDF for analysis:', analysisId);
        if (!analysisId) {
            console.error('No analysis ID available');
            toastr.error('Unable to generate PDF: No analysis ID found');
            return;
        }
        
        // Get button reference
        const btn = document.querySelector(`button[data-analysis-id="${analysisId}"]`);
        if (btn) {
            // Store original content and show loading state
            const originalHtml = btn.innerHTML;
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
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
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = '<i class="bi bi-file-pdf"></i> PDF';
            }
        }, 2000);
    },

    deleteAnalysis: function(analysisId, analysisName) {
        console.log('Deleting analysis:', analysisId, analysisName);
        
        // Show confirmation dialog
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Delete Analysis</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        Are you sure you want to delete the analysis "${analysisName}"? This action cannot be undone.
                    </div>
                    <div class="modal-footer gap-2">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-danger" id="confirmDelete">Delete</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        
        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
        
        // Handle delete confirmation
        modal.querySelector('#confirmDelete').addEventListener('click', async () => {
            try {
                modalInstance.hide();
                
                const response = await fetch(`/analyses/delete_analysis/${analysisId}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Remove the row from the table
                    const row = document.querySelector(`button[data-analysis-id="${analysisId}"]`).closest('tr');
                    row.remove();
                    
                    // Show success message
                    toastr.success('Analysis deleted successfully');
                    
                    // If table is empty, refresh the page to show the "no analyses" message
                    const tableBody = document.querySelector('tbody');
                    if (tableBody && !tableBody.hasChildNodes()) {
                        window.location.reload();
                    }
                } else {
                    throw new Error(data.message || 'Failed to delete analysis');
                }
            } catch (error) {
                console.error('Error:', error);
                toastr.error(error.message || 'Error deleting analysis');
            } finally {
                modal.remove();
            }
        });
        
        // Clean up modal when hidden
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }
};

// Make sure the module is available globally
window.viewEditAnalysisModule = viewEditAnalysisModule;

// Initialize when the DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    viewEditAnalysisModule.init();
});

// Export the module
export default viewEditAnalysisModule;