/**
 * Theme Switcher JavaScript
 * Handles switching between Light and Dark modes
 */

(function() {
    'use strict';
    
    // Get theme from localStorage or default to 'light'
    const getTheme = () => {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            return savedTheme;
        }
        
        // Check system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        
        return 'light';
    };
    
    // Set theme
    const setTheme = (theme) => {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        // Update toggle button state
        updateToggleButton(theme);
        
        // Dispatch custom event for other components
        window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));
    };
    
    // Update toggle button
    const updateToggleButton = (theme) => {
        const toggleButton = document.getElementById('themeToggle');
        if (toggleButton) {
            toggleButton.setAttribute('aria-label', 
                theme === 'dark' ? 'التبديل إلى الوضع الفاتح' : 'التبديل إلى الوضع الداكن'
            );
        }
    };
    
    // Toggle theme
    const toggleTheme = () => {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        setTheme(newTheme);
    };
    
    // Initialize theme on page load
    const initTheme = () => {
        const theme = getTheme();
        setTheme(theme);
    };
    
    // Listen for system theme changes
    const watchSystemTheme = () => {
        if (window.matchMedia) {
            const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
            
            darkModeQuery.addEventListener('change', (e) => {
                // Only update if user hasn't manually set a preference
                if (!localStorage.getItem('theme')) {
                    setTheme(e.matches ? 'dark' : 'light');
                }
            });
        }
    };
    
    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            initTheme();
            watchSystemTheme();
            
            // Attach event listener to toggle button
            const toggleButton = document.getElementById('themeToggle');
            if (toggleButton) {
                toggleButton.addEventListener('click', toggleTheme);
            }
        });
    } else {
        initTheme();
        watchSystemTheme();
        
        // Attach event listener to toggle button
        const toggleButton = document.getElementById('themeToggle');
        if (toggleButton) {
            toggleButton.addEventListener('click', toggleTheme);
        }
    }
    
    // Expose functions globally
    window.themeManager = {
        getTheme,
        setTheme,
        toggleTheme
    };
})();

// Keyboard shortcut for theme toggle (Ctrl/Cmd + Shift + T)
document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'T') {
        e.preventDefault();
        window.themeManager.toggleTheme();
    }
});

// Log theme changes (for debugging)
window.addEventListener('themeChanged', (e) => {
    console.log('Theme changed to:', e.detail.theme);
});

