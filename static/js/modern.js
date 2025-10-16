// Modern Enhancements for Sawaedna Cost App
class ModernApp {
    constructor() {
        this.init();
    }

    init() {
        this.setupSmoothAnimations();
        this.setupModernInteractions();
        this.setupRealTimeUpdates();
        this.setupAdvancedFilters();
    }

    setupSmoothAnimations() {
        // Add intersection observer for scroll animations
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fade-in-up');
                }
            });
        });

        document.querySelectorAll('.card, .table-responsive').forEach(el => {
            observer.observe(el);
        });
    }

    setupModernInteractions() {
        // Enhanced hover effects
        document.querySelectorAll('.btn, .card').forEach(element => {
            element.addEventListener('mouseenter', this.addHoverEffect);
            element.addEventListener('mouseleave', this.removeHoverEffect);
        });

        // Advanced tooltips
        this.setupAdvancedTooltips();
    }

    addHoverEffect(e) {
        this.style.transform = 'translateY(-2px)';
        this.style.boxShadow = '0 10px 25px -5px rgba(0, 0, 0, 0.15)';
    }

    removeHoverEffect(e) {
        this.style.transform = 'translateY(0)';
        this.style.boxShadow = '';
    }

    setupAdvancedTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl, {
                trigger: 'hover focus',
                placement: 'auto'
            });
        });
    }

    setupRealTimeUpdates() {
        // Real-time financial calculations
        this.setupRealTimeCalculations();
        
        // Auto-save functionality
        this.setupAutoSave();
    }

    setupRealTimeCalculations() {
        const calculationInputs = document.querySelectorAll('[data-calculate]');
        calculationInputs.forEach(input => {
            input.addEventListener('input', this.debounce(() => {
                this.updateCalculations();
            }, 300));
        });
    }

    setupAdvancedFilters() {
        // Advanced table filtering
        this.setupTableFilters();
        
        // Search with debounce
        this.setupSmartSearch();
    }

    setupTableFilters() {
        const filterInputs = document.querySelectorAll('.table-filter');
        filterInputs.forEach(input => {
            input.addEventListener('input', this.debounce(() => {
                this.filterTable(input);
            }, 250));
        });
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Initialize modern features when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new ModernApp();
    
    // Enhanced mobile menu
    const sidebarToggler = document.getElementById('sidebarToggler');
    const sidebar = document.getElementById('sidebar');
    
    if (sidebarToggler && sidebar) {
        sidebarToggler.addEventListener('click', function() {
            sidebar.classList.toggle('show');
            document.body.classList.toggle('sidebar-open');
        });
    }
});
