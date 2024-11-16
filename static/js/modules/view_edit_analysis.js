const viewEditAnalysisModule = {
    init: function() {
        console.log('Initializing view/edit analysis module');
        // We don't need initializePdfButtons anymore since we're using onclick
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
            // Show loading state
            const originalText = btn.innerHTML;
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
                btn.innerHTML = 'PDF';
            }
        }, 2000);
        
        // Show success message
        toastr.success('Generating PDF report...');
    }
};

// Make module globally available
window.viewEditAnalysisModule = viewEditAnalysisModule;

// Initialize when the DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    viewEditAnalysisModule.init();
});

export default viewEditAnalysisModule;