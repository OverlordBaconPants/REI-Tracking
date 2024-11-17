// /static/js/modules/welcome.js

const welcomeModule = {
    init: async function() {
        console.log('Initializing welcome module');
        try {
            this.setupAnimations();
            this.initializeEventListeners();
            console.log('Welcome module initialized successfully');
        } catch (error) {
            console.error('Error initializing welcome module:', error);
        }
    },

    setupAnimations: function() {
        // Add animation for welcome content
        const welcomeContent = document.querySelector('.welcome-content');
        if (welcomeContent) {
            welcomeContent.style.opacity = '0';
            welcomeContent.style.transform = 'translateY(20px)';
            
            // Fade in content
            setTimeout(() => {
                welcomeContent.style.transition = 'all 0.5s ease-out';
                welcomeContent.style.opacity = '1';
                welcomeContent.style.transform = 'translateY(0)';
            }, 100);
        }

        // Add animation for any cards or sections
        const elements = document.querySelectorAll('.animate-in');
        elements.forEach((element, index) => {
            element.style.opacity = '0';
            element.style.transform = 'translateY(20px)';
            
            // Stagger the animations
            setTimeout(() => {
                element.style.transition = 'all 0.5s ease-out';
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }, 100 + (index * 100));
        });
    },

    initializeEventListeners: function() {
        // Add hover effects for interactive elements
        const interactiveElements = document.querySelectorAll('.interactive');
        interactiveElements.forEach(element => {
            element.addEventListener('mouseenter', () => {
                element.classList.add('hover-effect');
                element.style.transform = 'translateY(-5px)';
                element.style.transition = 'all 0.3s ease';
            });

            element.addEventListener('mouseleave', () => {
                element.classList.remove('hover-effect');
                element.style.transform = 'translateY(0)';
            });
        });

        // Add smooth scroll for any anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Setup any call-to-action buttons
        const ctaButtons = document.querySelectorAll('.cta-button');
        ctaButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                // Add any click handling logic here
                console.log('CTA button clicked:', e.target.dataset.action);
            });
        });
    }
};

export default welcomeModule;