/**
 * base.js - Core functionality for the REI Tracker application
 * Provides base utilities, formatting, and common functions
 */
(function(window) {
    // Create base module
    const baseModule = {
        // Device detection module
        device: {
            viewportWidth: window.innerWidth,
            isMobile: false,
            isTablet: false,
            isDesktop: true,
            
            detectDeviceType: function() {
                // Detect viewport size
                this.viewportWidth = window.innerWidth;
                
                // Detect device type
                this.isMobile = this.viewportWidth < 768;
                this.isTablet = this.viewportWidth >= 768 && this.viewportWidth < 992;
                this.isDesktop = this.viewportWidth >= 992;
                
                // Add device-specific classes to the body
                const body = document.body;
                if (this.isMobile) body.classList.add('device-mobile');
                if (this.isTablet) body.classList.add('device-tablet');
                if (this.isDesktop) body.classList.add('device-desktop');
                
                return this;
            }
        },
        
        // Formatting module
        format: {
            currency: function(value, currency, locale) {
                if (currency === undefined) currency = 'USD';
                if (locale === undefined) locale = 'en-US';
                
                if (typeof value !== 'number') {
                    value = baseModule.utils.parseNumericValue(value);
                }
                
                try {
                    return new Intl.NumberFormat(locale, {
                        style: 'currency',
                        currency: currency
                    }).format(value);
                } catch (e) {
                    // Fallback formatting
                    return '$' + value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
                }
            },
            
            percentage: function(value, decimals, locale) {
                if (decimals === undefined) decimals = 2;
                if (locale === undefined) locale = 'en-US';
                
                if (typeof value !== 'number') {
                    value = baseModule.utils.parseNumericValue(value);
                }
                
                try {
                    return new Intl.NumberFormat(locale, {
                        style: 'percent',
                        minimumFractionDigits: decimals,
                        maximumFractionDigits: decimals
                    }).format(value);
                } catch (e) {
                    // Fallback formatting
                    return (value * 100).toFixed(decimals) + '%';
                }
            },
            
            number: function(value, decimals, locale) {
                if (decimals === undefined) decimals = 2;
                if (locale === undefined) locale = 'en-US';
                
                if (typeof value !== 'number') {
                    value = baseModule.utils.parseNumericValue(value);
                }
                
                try {
                    return new Intl.NumberFormat(locale, {
                        minimumFractionDigits: decimals,
                        maximumFractionDigits: decimals
                    }).format(value);
                } catch (e) {
                    // Fallback formatting
                    return value.toFixed(decimals).replace(/\d(?=(\d{3})+\.)/g, '$&,');
                }
            },
            
            date: function(date, format, locale) {
                if (format === undefined) format = 'MM/DD/YYYY';
                if (locale === undefined) locale = 'en-US';
                
                const d = date instanceof Date ? date : new Date(date);
                
                // Simple format implementation
                const year = d.getFullYear();
                const month = String(d.getMonth() + 1).padStart(2, '0');
                const day = String(d.getDate()).padStart(2, '0');
                
                let result = format;
                result = result.replace('YYYY', year);
                result = result.replace('MM', month);
                result = result.replace('DD', day);
                
                return result;
            },
            
            phone: function(phone) {
                // Clean the phone number
                const cleaned = ('' + phone).replace(/\D/g, '');
                
                // Check if it's a valid US phone number
                if (cleaned.length === 10) {
                    return '(' + cleaned.substring(0, 3) + ') ' + 
                           cleaned.substring(3, 6) + '-' + 
                           cleaned.substring(6, 10);
                }
                
                // Return original if not valid
                return phone;
            }
        },
        
        // Utility functions
        utils: {
            parseNumericValue: function(value) {
                if (typeof value === 'number') {
                    return value;
                }
                
                if (!value) {
                    return 0;
                }
                
                // Remove currency symbols, commas, and other non-numeric characters
                const cleanValue = String(value)
                    .replace(/[$,\s]/g, '')
                    .replace(/[^\d.-]/g, '');
                
                return parseFloat(cleanValue) || 0;
            },
            
            generateId: function(length) {
                if (length === undefined) length = 10;
                
                const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
                let result = '';
                for (let i = 0; i < length; i++) {
                    result += chars.charAt(Math.floor(Math.random() * chars.length));
                }
                return result;
            },
            
            validateEmail: function(email) {
                const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                return re.test(String(email).toLowerCase());
            },
            
            validatePhone: function(phone) {
                const re = /^\+?[0-9\s\-()]{10,20}$/;
                return re.test(String(phone));
            },
            
            validateUrl: function(url) {
                try {
                    new URL(url);
                    return true;
                } catch (e) {
                    return false;
                }
            },
            
            getCookie: function(name) {
                const match = document.cookie.match(new RegExp('(^|;\\s*)(' + name + ')=([^;]*)'));
                return match ? decodeURIComponent(match[3]) : null;
            },
            
            setCookie: function(name, value, days) {
                let expires = '';
                if (days) {
                    const date = new Date();
                    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
                    expires = '; expires=' + date.toUTCString();
                }
                document.cookie = name + '=' + encodeURIComponent(value) + expires + '; path=/';
            },
            
            deleteCookie: function(name) {
                this.setCookie(name, '', -1);
            }
        },
        
        // Add the methods required by the tests
        detectEnvironment: function() {
            // Detect touch capability
            this.touchEnabled = 'ontouchstart' in window;
            document.documentElement.classList.toggle('touch-device', this.touchEnabled);
            document.documentElement.classList.toggle('no-touch', !this.touchEnabled);
            
            // Detect reduced motion preference
            const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
            document.documentElement.classList.toggle('reduced-motion', prefersReducedMotion);
            
            // Detect high contrast mode
            const highContrast = window.matchMedia('(forced-colors: active)').matches;
            document.documentElement.classList.toggle('high-contrast', highContrast);
            
            // Update device detection
            this.device.detectDeviceType();
            
            return this;
        },
        
        initializeLibraries: function() {
            // Check for required libraries
            const requiredLibraries = {
                'jQuery': typeof jQuery !== 'undefined',
                'bootstrap': typeof bootstrap !== 'undefined',
                'toastr': typeof toastr !== 'undefined',
                'lodash': typeof _ !== 'undefined'
            };
            
            // Log library status
            console.log('Checking required libraries:', requiredLibraries);
            
            // Check if any required libraries are missing
            const missingLibraries = Object.entries(requiredLibraries)
                .filter(([, loaded]) => !loaded)
                .map(([name]) => name);
            
            if (missingLibraries.length > 0) {
                console.error('Required libraries not loaded:', missingLibraries.join(', '));
                if (typeof window.showNotification === 'function') {
                    window.showNotification(`Required libraries missing: ${missingLibraries.join(', ')}`, 'error', 'both');
                }
                return false;
            }
            
            return true;
        },
        
        formatCurrency: function(value, currency = 'USD') {
            return this.format.currency(value, currency);
        },
        
        formatPercentage: function(value, decimals = 2) {
            // Check if the value is already in percentage form (e.g., 12.34 instead of 0.1234)
            if (value > 1) {
                value = value / 100;
            }
            return this.format.percentage(value, decimals);
        },
        
        parseNumericValue: function(value) {
            return this.utils.parseNumericValue(value);
        },
        
        init: function() {
            console.log('Initializing base module');
            
            // Detect environment
            this.detectEnvironment();
            
            // Initialize libraries
            this.initializeLibraries();
            
            // Detect device type
            this.device.detectDeviceType();
            
            return this;
        }
    };
    
    // Expose the base module
    window.baseModule = baseModule;
    
    // Add to REITracker namespace if it exists
    if (window.REITracker) {
        window.REITracker.base = baseModule;
    }
    
    // Initialize when the DOM is fully loaded
    document.addEventListener('DOMContentLoaded', function() {
        baseModule.init();
    });
    
})(window);
