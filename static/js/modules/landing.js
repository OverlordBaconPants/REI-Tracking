// /static/js/modules/landing.js

const landingModule = {
    init: async function() {
        console.log('Initializing landing page module');
        try {
            this.setupAnimations();
            this.initializeEventListeners();
            console.log('Landing page module initialized successfully');
        } catch (error) {
            console.error('Error initializing landing page module:', error);
        }
    },

    setupAnimations: function() {
        // Add any animations for the landing page cards or content
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            
            // Fade in cards sequentially
            setTimeout(() => {
                card.style.transition = 'all 0.5s ease-out';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 100);
        });
    },

    initializeEventListeners: function() {
        // Add hover effects for cards
        const cards = document.querySelectorAll('.card.shadow-sm');
        cards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.classList.add('shadow-lg');
                card.style.transform = 'translateY(-5px)';
                card.style.transition = 'all 0.3s ease';
            });

            card.addEventListener('mouseleave', () => {
                card.classList.remove('shadow-lg');
                card.style.transform = 'translateY(0)';
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

        // Handle authentication buttons
        const loginBtn = document.querySelector('a[href*="login"]');
        const signupBtn = document.querySelector('a[href*="signup"]');

        if (loginBtn) {
            loginBtn.addEventListener('click', (e) => {
                // Add any pre-navigation logic here if needed
                console.log('Navigating to login page');
            });
        }

        if (signupBtn) {
            signupBtn.addEventListener('click', (e) => {
                // Add any pre-navigation logic here if needed
                console.log('Navigating to signup page');
            });
        }
    }
};

export default landingModule;