/**
 * Landing page module for REI Tracker
 * 
 * This module provides functionality specific to the landing page,
 * including animations, interactive elements, and form handling.
 */

// Module object
const landing = {
    /**
     * Initialize the landing page module
     */
    init: function() {
        console.log('Initializing landing page module');
        
        // Initialize Bootstrap components
        this.initBootstrapComponents();
        
        // Initialize card animations
        this.initCardAnimations();
        
        // Initialize scroll animations
        this.initScrollAnimations();
        
        // Initialize form handlers
        this.initFormHandlers();
        
        console.log('Landing page module initialized');
    },
    
    /**
     * Initialize Bootstrap components
     */
    initBootstrapComponents: function() {
        // Initialize tooltips
        if (window.baseModule) {
            window.baseModule.updateTooltips();
        } else {
            // Fallback if baseModule is not available
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
            
            // Initialize popovers
            const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
            popoverTriggerList.map(function (popoverTriggerEl) {
                return new bootstrap.Popover(popoverTriggerEl);
            });
        }
    },
    
    /**
     * Initialize card animations
     */
    initCardAnimations: function() {
        // Add hover animations to cards
        const cards = document.querySelectorAll('.card');
        
        cards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-5px)';
                this.style.boxShadow = '0 10px 20px rgba(0,0,0,0.1)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
            });
        });
    },
    
    /**
     * Initialize scroll animations
     */
    initScrollAnimations: function() {
        // Add fade-in animation to sections when scrolled into view
        const sections = document.querySelectorAll('section');
        
        // Check if IntersectionObserver is supported
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('visible');
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.1 });
            
            sections.forEach(section => {
                section.classList.add('fade-in');
                observer.observe(section);
            });
        } else {
            // Fallback for browsers that don't support IntersectionObserver
            sections.forEach(section => {
                section.classList.add('visible');
            });
        }
    },
    
    /**
     * Initialize form handlers
     */
    initFormHandlers: function() {
        // Add smooth scrolling to CTA buttons
        const ctaButtons = document.querySelectorAll('.btn-lg');
        
        ctaButtons.forEach(button => {
            if (button.getAttribute('href') && button.getAttribute('href').startsWith('#')) {
                button.addEventListener('click', function(e) {
                    e.preventDefault();
                    
                    const targetId = this.getAttribute('href');
                    const targetElement = document.querySelector(targetId);
                    
                    if (targetElement) {
                        window.scrollTo({
                            top: targetElement.offsetTop - 100,
                            behavior: 'smooth'
                        });
                    }
                });
            }
        });
    }
};

// Export the module
export default landing;
