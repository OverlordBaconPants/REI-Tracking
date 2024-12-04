const viewEditAnalysisModule = {
    init: function() {
        console.log('Initializing view/edit analysis module');
    },

    downloadPdf: function(analysisId) {
        console.log('Downloading PDF for analysis:', analysisId);
        if (!analysisId) {
            console.error('No analysis ID available');
            toastr.error('Unable to generate PDF: No analysis ID found');
            return;
        }
        
        const btn = document.querySelector(`button[data-analysis-id="${analysisId}"]`);
        if (btn) {
            const originalText = btn.innerHTML;
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
        }
        
        const form = document.createElement('form');
        form.method = 'GET';
        form.action = `/analyses/generate_pdf/${analysisId}`;
        document.body.appendChild(form);
        
        form.submit();
        document.body.removeChild(form);
        
        setTimeout(() => {
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = 'PDF';
            }
        }, 2000);
        
        toastr.success('Generating PDF report...');
    },

    deleteAnalysis: async function(analysisId) {
        if (!confirm('Are you sure you want to delete this analysis? This action cannot be undone.')) {
            return;
        }

        try {
            const response = await fetch(`/analyses/delete_analysis/${analysisId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (data.success) {
                toastr.success('Analysis deleted successfully');
                // Reload the page to show updated list
                window.location.reload();
            } else {
                toastr.error(data.message || 'Error deleting analysis');
            }
        } catch (error) {
            console.error('Error deleting analysis:', error);
            toastr.error('Error deleting analysis');
        }
    }
};

// Make module globally available
window.viewEditAnalysisModule = viewEditAnalysisModule;

// Initialize when the DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    viewEditAnalysisModule.init();
});

export default viewEditAnalysisModule;