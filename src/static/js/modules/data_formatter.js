/**
 * data_formatter.js - Data formatting and visualization module
 * Provides utilities for formatting data and creating visualizations
 */

/**
 * Data Formatter Module
 * Handles data formatting and visualization
 */
const dataFormatterModule = {
    /**
     * Initialize the data formatter
     * @param {Object} config - Configuration options
     */
    init: function(config = {}) {
        console.log('Initializing data formatter module');
        this.config = {
            currency: 'USD',
            locale: 'en-US',
            dateFormat: 'MM/DD/YYYY',
            ...config
        };
        
        this.initializeCharts();
        this.initializeDataTables();
    },
    
    /**
     * Initialize charts on the page
     */
    initializeCharts: function() {
        const chartContainers = document.querySelectorAll('[data-chart]');
        chartContainers.forEach(container => {
            const chartType = container.dataset.chart;
            const chartDataStr = container.dataset.chartData;
            const chartOptionsStr = container.dataset.chartOptions || '{}';
            
            if (chartType && chartDataStr) {
                try {
                    const chartData = JSON.parse(chartDataStr);
                    const chartOptions = JSON.parse(chartOptionsStr);
                    this.renderChart(container, chartType, chartData, chartOptions);
                } catch (error) {
                    console.error('Error parsing chart data:', error);
                    container.innerHTML = `<div class="alert alert-danger">Error parsing chart data: ${error.message}</div>`;
                }
            }
        });
    },
    
    /**
     * Initialize data tables on the page
     */
    initializeDataTables: function() {
        const dataTables = document.querySelectorAll('[data-table]');
        dataTables.forEach(table => {
            const tableDataStr = table.dataset.tableData;
            const tableOptionsStr = table.dataset.tableOptions || '{}';
            
            if (tableDataStr) {
                try {
                    const tableData = JSON.parse(tableDataStr);
                    const tableOptions = JSON.parse(tableOptionsStr);
                    this.renderDataTable(table, tableData, tableOptions);
                } catch (error) {
                    console.error('Error parsing table data:', error);
                    table.innerHTML = `<div class="alert alert-danger">Error parsing table data: ${error.message}</div>`;
                }
            }
        });
    },
    
    /**
     * Render a chart
     * @param {HTMLElement} container - The container element
     * @param {string} type - The chart type
     * @param {Object} data - The chart data
     * @param {Object} options - The chart options
     */
    renderChart: function(container, type, data, options = {}) {
        // Check if Chart.js is available
        if (typeof Chart === 'undefined') {
            console.error('Chart.js is not loaded');
            container.innerHTML = '<div class="alert alert-warning">Chart.js library is required for charts</div>';
            return;
        }
        
        // Set default options based on chart type
        const defaultOptions = this.getDefaultChartOptions(type);
        
        // Create chart
        const ctx = document.createElement('canvas');
        ctx.width = container.clientWidth;
        ctx.height = container.dataset.height || 300;
        container.appendChild(ctx);
        
        // Create chart instance
        new Chart(ctx, {
            type,
            data,
            options: {
                ...defaultOptions,
                ...options,
                responsive: true,
                maintainAspectRatio: false
            }
        });
        
        // Add accessibility description
        this.addChartAccessibility(container, type, data);
    },
    
    /**
     * Get default chart options based on chart type
     * @param {string} type - The chart type
     * @returns {Object} Default options for the chart type
     */
    getDefaultChartOptions: function(type) {
        const baseOptions = {
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        boxWidth: 12,
                        padding: 15
                    }
                },
                tooltip: {
                    enabled: true,
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: 'rgba(0, 0, 0, 0.1)',
                    borderWidth: 1,
                    padding: 10,
                    displayColors: true
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            }
        };
        
        // Add type-specific options
        switch (type) {
            case 'bar':
                return {
                    ...baseOptions,
                    scales: {
                        x: {
                            grid: {
                                display: false
                            }
                        },
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(0, 0, 0, 0.05)'
                            }
                        }
                    }
                };
                
            case 'line':
                return {
                    ...baseOptions,
                    elements: {
                        line: {
                            tension: 0.4
                        },
                        point: {
                            radius: 4,
                            hitRadius: 10,
                            hoverRadius: 6
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                display: false
                            }
                        },
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(0, 0, 0, 0.05)'
                            }
                        }
                    }
                };
                
            case 'pie':
            case 'doughnut':
                return {
                    ...baseOptions,
                    cutout: type === 'doughnut' ? '70%' : 0,
                    plugins: {
                        ...baseOptions.plugins,
                        legend: {
                            ...baseOptions.plugins.legend,
                            position: 'bottom'
                        }
                    }
                };
                
            case 'radar':
                return {
                    ...baseOptions,
                    elements: {
                        line: {
                            tension: 0.4
                        }
                    },
                    scales: {
                        r: {
                            beginAtZero: true,
                            angleLines: {
                                color: 'rgba(0, 0, 0, 0.1)'
                            },
                            grid: {
                                color: 'rgba(0, 0, 0, 0.05)'
                            }
                        }
                    }
                };
                
            default:
                return baseOptions;
        }
    },
    
    /**
     * Add accessibility description to chart
     * @param {HTMLElement} container - The chart container
     * @param {string} type - The chart type
     * @param {Object} data - The chart data
     */
    addChartAccessibility: function(container, type, data) {
        // Create accessible description
        const description = document.createElement('div');
        description.className = 'sr-only';
        description.id = `chart-desc-${Math.random().toString(36).substr(2, 9)}`;
        
        // Generate description based on chart type and data
        let descText = `${type.charAt(0).toUpperCase() + type.slice(1)} chart `;
        
        if (data.labels && data.labels.length) {
            descText += `with categories: ${data.labels.join(', ')}. `;
        }
        
        if (data.datasets && data.datasets.length) {
            data.datasets.forEach((dataset, i) => {
                descText += `${dataset.label || `Dataset ${i+1}`}: `;
                if (dataset.data && dataset.data.length) {
                    if (typeof dataset.data[0] === 'object') {
                        // Handle complex data structures
                        descText += 'complex data structure. ';
                    } else {
                        descText += `values ${dataset.data.join(', ')}. `;
                    }
                }
            });
        }
        
        description.textContent = descText;
        container.appendChild(description);
        
        // Set aria attributes
        container.setAttribute('role', 'img');
        container.setAttribute('aria-labelledby', description.id);
    },
    
    /**
     * Render a data table
     * @param {HTMLElement} container - The container element
     * @param {Object} data - The table data
     * @param {Object} options - The table options
     */
    renderDataTable: function(container, data, options = {}) {
        // Check if data has headers and rows
        if (!data.headers || !data.rows) {
            console.error('Table data must have headers and rows');
            container.innerHTML = '<div class="alert alert-danger">Invalid table data format</div>';
            return;
        }
        
        // Create table element
        const table = document.createElement('table');
        table.className = 'table table-striped table-hover';
        
        // Add responsive wrapper if needed
        if (options.responsive !== false) {
            const wrapper = document.createElement('div');
            wrapper.className = 'table-responsive';
            wrapper.appendChild(table);
            container.appendChild(wrapper);
        } else {
            container.appendChild(table);
        }
        
        // Create table header
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        
        data.headers.forEach(header => {
            const th = document.createElement('th');
            th.textContent = header.label || '';
            
            // Add sorting attributes if enabled
            if (options.sortable !== false) {
                th.setAttribute('data-sort', header.key || '');
                th.style.cursor = 'pointer';
                th.addEventListener('click', () => this.sortTable(table, header.key));
            }
            
            // Add column width if specified
            if (header.width) {
                th.style.width = header.width;
            }
            
            headerRow.appendChild(th);
        });
        
        thead.appendChild(headerRow);
        table.appendChild(thead);
        
        // Create table body
        const tbody = document.createElement('tbody');
        
        data.rows.forEach(row => {
            const tr = document.createElement('tr');
            
            // Add row ID if available
            if (row.id) {
                tr.setAttribute('data-id', row.id);
            }
            
            // Add row click handler if specified
            if (options.onRowClick) {
                tr.style.cursor = 'pointer';
                tr.addEventListener('click', () => options.onRowClick(row));
            }
            
            // Add cells
            data.headers.forEach(header => {
                const td = document.createElement('td');
                const key = header.key || '';
                const value = row[key];
                
                // Format cell value based on type
                if (header.type) {
                    td.innerHTML = this.formatCellValue(value, header.type, header.format);
                } else {
                    td.textContent = value || '';
                }
                
                tr.appendChild(td);
            });
            
            tbody.appendChild(tr);
        });
        
        table.appendChild(tbody);
        
        // Add pagination if enabled
        if (options.pagination && data.totalRows > data.rows.length) {
            this.addTablePagination(container, data, options);
        }
        
        // Add search if enabled
        if (options.search) {
            this.addTableSearch(container, table);
        }
    },
    
    /**
     * Format cell value based on type
     * @param {*} value - The cell value
     * @param {string} type - The value type
     * @param {string|Object} format - The format options
     * @returns {string} Formatted cell value
     */
    formatCellValue: function(value, type, format) {
        if (value === null || value === undefined) {
            return '';
        }
        
        switch (type) {
            case 'currency':
                return this.formatCurrency(value, format);
                
            case 'percentage':
                return this.formatPercentage(value, format);
                
            case 'date':
                return this.formatDate(value, format);
                
            case 'number':
                return this.formatNumber(value, format);
                
            case 'boolean':
                return this.formatBoolean(value, format);
                
            case 'link':
                return this.formatLink(value, format);
                
            case 'image':
                return this.formatImage(value, format);
                
            case 'badge':
                return this.formatBadge(value, format);
                
            case 'button':
                return this.formatButton(value, format);
                
            case 'html':
                return value;
                
            default:
                return value.toString();
        }
    },
    
    /**
     * Format currency value
     * @param {number} value - The value to format
     * @param {Object} format - Format options
     * @returns {string} Formatted currency string
     */
    formatCurrency: function(value, format = {}) {
        const currency = format.currency || this.config.currency;
        const locale = format.locale || this.config.locale;
        const decimals = format.decimals !== undefined ? format.decimals : 2;
        
        return new Intl.NumberFormat(locale, {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(value);
    },
    
    /**
     * Format percentage value
     * @param {number} value - The value to format
     * @param {Object} format - Format options
     * @returns {string} Formatted percentage string
     */
    formatPercentage: function(value, format = {}) {
        const locale = format.locale || this.config.locale;
        const decimals = format.decimals !== undefined ? format.decimals : 2;
        
        return new Intl.NumberFormat(locale, {
            style: 'percent',
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(value / 100);
    },
    
    /**
     * Format date value
     * @param {string|Date} value - The date to format
     * @param {string} format - Date format
     * @returns {string} Formatted date string
     */
    formatDate: function(value, format) {
        const date = value instanceof Date ? value : new Date(value);
        
        if (isNaN(date.getTime())) {
            return '';
        }
        
        const dateFormat = format || this.config.dateFormat;
        
        // Simple date formatting
        const day = date.getDate().toString().padStart(2, '0');
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const year = date.getFullYear();
        
        let formatted = dateFormat
            .replace('MM', month)
            .replace('DD', day)
            .replace('YYYY', year);
            
        // Add time if format includes it
        if (dateFormat.includes('HH')) {
            const hours = date.getHours().toString().padStart(2, '0');
            const minutes = date.getMinutes().toString().padStart(2, '0');
            
            formatted = formatted
                .replace('HH', hours)
                .replace('mm', minutes);
        }
        
        return formatted;
    },
    
    /**
     * Format number value
     * @param {number} value - The value to format
     * @param {Object} format - Format options
     * @returns {string} Formatted number string
     */
    formatNumber: function(value, format = {}) {
        const locale = format.locale || this.config.locale;
        const decimals = format.decimals !== undefined ? format.decimals : 0;
        
        return new Intl.NumberFormat(locale, {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(value);
    },
    
    /**
     * Format boolean value
     * @param {boolean} value - The value to format
     * @param {Object} format - Format options
     * @returns {string} Formatted boolean HTML
     */
    formatBoolean: function(value, format = {}) {
        const trueText = format.trueText || '<i class="bi bi-check-circle-fill text-success"></i>';
        const falseText = format.falseText || '<i class="bi bi-x-circle-fill text-danger"></i>';
        
        return value ? trueText : falseText;
    },
    
    /**
     * Format link value
     * @param {string} value - The link text
     * @param {Object} format - Format options
     * @returns {string} Formatted link HTML
     */
    formatLink: function(value, format = {}) {
        const url = format.url || value;
        const text = format.text || value;
        const target = format.target || '_self';
        const classes = format.classes || '';
        
        return `<a href="${url}" target="${target}" class="${classes}">${text}</a>`;
    },
    
    /**
     * Format image value
     * @param {string} value - The image URL
     * @param {Object} format - Format options
     * @returns {string} Formatted image HTML
     */
    formatImage: function(value, format = {}) {
        const url = format.url || value;
        const alt = format.alt || '';
        const width = format.width || 'auto';
        const height = format.height || 'auto';
        const classes = format.classes || 'img-thumbnail';
        
        return `<img src="${url}" alt="${alt}" width="${width}" height="${height}" class="${classes}">`;
    },
    
    /**
     * Format badge value
     * @param {string} value - The badge text
     * @param {Object} format - Format options
     * @returns {string} Formatted badge HTML
     */
    formatBadge: function(value, format = {}) {
        const text = format.text || value;
        let type = format.type || 'primary';
        
        // Map value to type if mapping is provided
        if (format.mapping && format.mapping[value]) {
            type = format.mapping[value];
        }
        
        return `<span class="badge bg-${type}">${text}</span>`;
    },
    
    /**
     * Format button value
     * @param {string} value - The button text
     * @param {Object} format - Format options
     * @returns {string} Formatted button HTML
     */
    formatButton: function(value, format = {}) {
        const text = format.text || value;
        const type = format.type || 'primary';
        const size = format.size || 'sm';
        const action = format.action || '';
        const id = format.id || `btn-${Math.random().toString(36).substr(2, 9)}`;
        
        return `<button id="${id}" class="btn btn-${type} btn-${size}" data-action="${action}">${text}</button>`;
    },
    
    /**
     * Sort table by column
     * @param {HTMLTableElement} table - The table to sort
     * @param {string} column - The column key to sort by
     */
    sortTable: function(table, column) {
        const thead = table.querySelector('thead');
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        // Get current sort direction
        const th = thead.querySelector(`th[data-sort="${column}"]`);
        const currentDir = th.getAttribute('data-sort-dir') || 'asc';
        const newDir = currentDir === 'asc' ? 'desc' : 'asc';
        
        // Update sort direction
        thead.querySelectorAll('th').forEach(header => {
            header.removeAttribute('data-sort-dir');
            header.classList.remove('sort-asc', 'sort-desc');
        });
        
        th.setAttribute('data-sort-dir', newDir);
        th.classList.add(`sort-${newDir}`);
        
        // Get column index
        const headers = Array.from(thead.querySelectorAll('th'));
        const columnIndex = headers.findIndex(header => header.getAttribute('data-sort') === column);
        
        if (columnIndex === -1) return;
        
        // Sort rows
        rows.sort((a, b) => {
            const aValue = a.cells[columnIndex].textContent.trim();
            const bValue = b.cells[columnIndex].textContent.trim();
            
            // Try to sort as numbers if possible
            const aNum = parseFloat(aValue.replace(/[^0-9.-]+/g, ''));
            const bNum = parseFloat(bValue.replace(/[^0-9.-]+/g, ''));
            
            if (!isNaN(aNum) && !isNaN(bNum)) {
                return newDir === 'asc' ? aNum - bNum : bNum - aNum;
            }
            
            // Otherwise sort as strings
            return newDir === 'asc' 
                ? aValue.localeCompare(bValue) 
                : bValue.localeCompare(aValue);
        });
        
        // Reorder rows
        rows.forEach(row => tbody.appendChild(row));
    },
    
    /**
     * Add pagination to table
     * @param {HTMLElement} container - The container element
     * @param {Object} data - The table data
     * @param {Object} options - The pagination options
     */
    addTablePagination: function(container, data, options) {
        const totalRows = data.totalRows || 0;
        const pageSize = options.pageSize || 10;
        const totalPages = Math.ceil(totalRows / pageSize);
        const currentPage = options.currentPage || 1;
        
        // Create pagination element
        const pagination = document.createElement('nav');
        pagination.setAttribute('aria-label', 'Table pagination');
        
        const ul = document.createElement('ul');
        ul.className = 'pagination justify-content-center';
        
        // Previous button
        const prevLi = document.createElement('li');
        prevLi.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`;
        
        const prevLink = document.createElement('a');
        prevLink.className = 'page-link';
        prevLink.href = '#';
        prevLink.setAttribute('aria-label', 'Previous');
        prevLink.innerHTML = '<span aria-hidden="true">&laquo;</span>';
        
        if (currentPage > 1) {
            prevLink.addEventListener('click', e => {
                e.preventDefault();
                if (options.onPageChange) {
                    options.onPageChange(currentPage - 1);
                }
            });
        }
        
        prevLi.appendChild(prevLink);
        ul.appendChild(prevLi);
        
        // Page numbers
        const maxPages = 5; // Maximum number of page links to show
        let startPage = Math.max(1, currentPage - Math.floor(maxPages / 2));
        let endPage = Math.min(totalPages, startPage + maxPages - 1);
        
        if (endPage - startPage + 1 < maxPages) {
            startPage = Math.max(1, endPage - maxPages + 1);
        }
        
        for (let i = startPage; i <= endPage; i++) {
            const li = document.createElement('li');
            li.className = `page-item ${i === currentPage ? 'active' : ''}`;
            
            const link = document.createElement('a');
            link.className = 'page-link';
            link.href = '#';
            link.textContent = i;
            
            if (i !== currentPage) {
                link.addEventListener('click', e => {
                    e.preventDefault();
                    if (options.onPageChange) {
                        options.onPageChange(i);
                    }
                });
            }
            
            li.appendChild(link);
            ul.appendChild(li);
        }
        
        // Next button
        const nextLi = document.createElement('li');
        nextLi.className = `page-item ${currentPage === totalPages ? 'disabled' : ''}`;
        
        const nextLink = document.createElement('a');
        nextLink.className = 'page-link';
        nextLink.href = '#';
        nextLink.setAttribute('aria-label', 'Next');
        nextLink.innerHTML = '<span aria-hidden="true">&raquo;</span>';
        
        if (currentPage < totalPages) {
            nextLink.addEventListener('click', e => {
                e.preventDefault();
                if (options.onPageChange) {
                    options.onPageChange(currentPage + 1);
                }
            });
        }
        
        nextLi.appendChild(nextLink);
        ul.appendChild(nextLi);
        
        pagination.appendChild(ul);
        container.appendChild(pagination);
    },
    
    /**
     * Add search functionality to table
     * @param {HTMLElement} container - The container element
     * @param {HTMLTableElement} table - The table element
     */
    addTableSearch: function(container, table) {
        // Create search input
        const searchContainer = document.createElement('div');
        searchContainer.className = 'mb-3';
        
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.className = 'form-control';
        searchInput.placeholder = 'Search...';
        searchInput.setAttribute('aria-label', 'Search table');
        
        searchContainer.appendChild(searchInput);
        container.insertBefore(searchContainer, container.firstChild);
        
        // Add search functionality
        searchInput.addEventListener('input', _.debounce(function() {
            const searchTerm = this.value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        }, 300));
    }
};

// Register the module with REITracker namespace
if (typeof window.REITracker !== 'undefined') {
    window.REITracker.modules = window.REITracker.modules || {};
    window.REITracker.modules.dataFormatter = dataFormatterModule;
}

// For ES6 module support
if (typeof module !== 'undefined' && module.exports) {
    module.exports = dataFormatterModule;
}
