// main.js

// Covers common functionality and initialization logic

(function(window) {
    const baseModule = {
        init: function() {
            console.log('Initializing base module');
            // Initialize accordion functionality
            const accordionButtons = document.querySelectorAll('.accordion-button');
            accordionButtons.forEach(button => {
                button.addEventListener('click', function() {
                    this.classList.toggle('collapsed');
                    const target = document.querySelector(this.getAttribute('data-bs-target'));
                    if (target) {
                        target.classList.toggle('show');
                    }
                });
            });
        },

        checkFlashMessages: function() {
            const flashMessages = document.querySelectorAll('.flash-message');
            flashMessages.forEach(message => {
                alert(message.textContent);
                message.remove();
            });
        }
    };

    async function loadModule(moduleName) {
        try {
            console.log(`Attempting to load module: ${moduleName}`);
            const module = await import(`./${moduleName}.js`);
            console.log(`Successfully loaded module: ${moduleName}`);
            return module.default;
        } catch (error) {
            console.error(`Error loading module ${moduleName}:`, error);
            return null;
        }
    }

    async function initPage() {
        const body = document.body;
        let moduleToLoad = null;

        if (body.classList.contains('add-transactions-page')) {
            console.log('Add transactions page detected');
            moduleToLoad = 'add_transactions';
        } else if (body.classList.contains('add-properties-page')) {
            console.log('Add properties page detected');
            moduleToLoad = 'add_properties';
        } else if (body.classList.contains('edit-properties-page')) {
            console.log('Edit properties page detected');
            moduleToLoad = 'edit_properties';
        } else if (body.classList.contains('remove-properties-page')) {
            console.log('Remove properties page detected');
            moduleToLoad = 'remove_properties';
        }

        if (moduleToLoad) {
            const module = await loadModule(moduleToLoad);
            if (module && typeof module.init === 'function') {
                console.log(`Initializing module: ${moduleToLoad}`);
                module.init();
            } else {
                console.error(`Failed to initialize module: ${moduleToLoad}`);
            }
        } else {
            console.log('No specific module detected for this page');
        }
    }

    async function init() {
        console.log('Main init function called');
        console.log('Body classes:', document.body.className);
        
        baseModule.init();
        await initPage();
    }

    // Expose the init function and baseModule to the global scope
    window.mainInit = init;
    window.baseModule = baseModule;

})(window);

// Initialize when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    if (window.mainInit) {
        window.mainInit();
    }
});