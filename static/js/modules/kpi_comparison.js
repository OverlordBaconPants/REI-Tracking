document.addEventListener('DOMContentLoaded', function() {
    const propertySelect = document.getElementById('property_select');
    const loadKpisBtn = document.getElementById('loadKpisBtn');
    const kpiContainer = document.getElementById('kpiContainer');
    const noAnalysisAlert = document.getElementById('noAnalysisAlert');
    const plannedMetrics = document.getElementById('plannedMetrics');
    const createAnalysisBtn = document.getElementById('createAnalysisBtn');
    const downloadReportBtn = document.getElementById('downloadReportBtn');

    // Fetch properties from server
    async function fetchProperties() {
        try {
            const response = await fetch('/analyses/api/properties');
            if (!response.ok) {
                throw new Error('Failed to fetch properties');
            }
            const data = await response.json();
            populatePropertySelect(data.properties || []);
        } catch (error) {
            console.error('Error:', error);
            toastr.error('Failed to load properties');
        }
    }

    function populatePropertySelect(properties) {
        propertySelect.innerHTML = '<option value="">Select a property...</option>';
        properties.forEach(property => {
            const fullAddress = property.address;
            const truncatedAddress = fullAddress.split(',').slice(0, 2).join(',');
            const option = document.createElement('option');
            option.value = fullAddress; // Keep full address as value
            option.textContent = truncatedAddress; // Show truncated address to user
            propertySelect.appendChild(option);
        });
    }

    function formatCurrency(value) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(parseFloat(value) || 0);
    }

    function formatPercentage(value) {
        return `${parseFloat(value || 0).toFixed(2)}%`;
    }

    function updateKPIDisplays(data) {
        console.log('Updating KPI displays with data:', data); // Debug data
    
        // Show container first
        if (kpiContainer) {
            kpiContainer.style.display = 'block';
        }
    
        if (!data.planned) {
            console.log('No planned data found');
            if (noAnalysisAlert) noAnalysisAlert.style.display = 'block';
            if (plannedMetrics) plannedMetrics.style.display = 'none';
        } else {
            console.log('Found planned data, updating displays');
            if (noAnalysisAlert) noAnalysisAlert.style.display = 'none';
            if (plannedMetrics) plannedMetrics.style.display = 'block';
            
            // Update planned metrics
            document.getElementById('planned_income').textContent = formatCurrency(data.planned.monthly_income);
            document.getElementById('planned_expenses').textContent = formatCurrency(data.planned.monthly_expenses);
            document.getElementById('planned_cashflow').textContent = formatCurrency(data.planned.monthly_cash_flow);
            document.getElementById('planned_annual_cashflow').textContent = formatCurrency(data.planned.annual_cash_flow);
            document.getElementById('planned_coc').textContent = formatPercentage(data.planned.cash_on_cash_return);
        }
    
        // Update actual metrics if they exist
        if (data.actual) {
            console.log('Found actual data, updating displays');
            document.getElementById('actual_income').textContent = formatCurrency(data.actual.actual_monthly_income);
            document.getElementById('actual_expenses').textContent = formatCurrency(data.actual.actual_monthly_expenses);
            document.getElementById('actual_cashflow').textContent = formatCurrency(data.actual.actual_monthly_cash_flow);
            document.getElementById('actual_annual_cashflow').textContent = formatCurrency(data.actual.actual_annual_cash_flow);
        }
    }

    function isSimilarAddress(addr1, addr2) {
        // Split addresses into components
        const components1 = addr1.split(',').map(s => s.trim().toLowerCase());
        const components2 = addr2.split(',').map(s => s.trim().toLowerCase());
        
        // Check if street number and name match
        if (components1[0] !== components2[0]) return false;
        
        // Check if city matches
        if (!components1[1].includes(components2[1].toLowerCase())) return false;
        
        // Check if state matches
        const state1 = components1[2].replace(/[^a-z]/g, '');
        const state2 = components2[2].replace(/[^a-z]/g, '');
        if (state1 !== state2) return false;
        
        return true;
    }
    
    async function loadKPIs(propertyId) {
        try {
            console.log('Loading KPIs for:', propertyId);
            const response = await fetch(`/analyses/api/kpi-data/${encodeURIComponent(propertyId)}`);
            console.log('Response:', response); // Debug response
    
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to load KPI data');
            }
            
            const data = await response.json();
            console.log('Received data:', data); // Debug received data
            updateKPIDisplays(data);
    
        } catch (error) {
            console.error('Error:', error);
            toastr.error(error.message);
        }
    }

    loadKpisBtn.addEventListener('click', () => {
        const selectedProperty = propertySelect.value;
        if (selectedProperty) {
            loadKPIs(selectedProperty);
        } else {
            toastr.warning('Please select a property');
        }
    });

    createAnalysisBtn.addEventListener('click', (e) => {
        e.preventDefault();
        const selectedProperty = propertySelect.value;
        if (selectedProperty) {
            window.location.href = `/analyses/create_analysis?property=${encodeURIComponent(selectedProperty)}`;
        }
    });

    downloadReportBtn.addEventListener('click', () => {
        const selectedProperty = propertySelect.value;
        if (selectedProperty) {
            window.location.href = `/analyses/generate_pdf/${encodeURIComponent(selectedProperty)}`;
        }
    });

    // Initialize by fetching properties
    fetchProperties();
});