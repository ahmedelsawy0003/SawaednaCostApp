// ==========================================================================
// Modern UX Enhancements for Sawaedna Cost App - Enhanced UI Logic
// ==========================================================================

class ModernUX {
    constructor() {
        // Initialize core interactions after DOM load
        this.initSidebarToggle();
        this.initAnimations(); 
        this.handleFlashMessages();
        this.setupAdvancedTooltips();
        this.setupDropdowns();
        this.initSmoothScrolling();
        this.enhanceTableInteractions();
    }
    
    // Setup Intersection Observer for scroll animations
    initAnimations() {
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('is-visible');
                        observer.unobserve(entry.target);
                    }
                });
            }, {
                root: null,
                rootMargin: '0px',
                threshold: 0.1
            });

            document.querySelectorAll('.animate-fade-in-up').forEach(element => {
                observer.observe(element);
            });
        }
    }

    // Enhanced sidebar toggle with smooth animations
    initSidebarToggle() {
        const sidebarToggler = document.getElementById('sidebarToggler');
        const sidebar = document.getElementById('sidebar');
        const sidebarClose = document.getElementById('sidebarClose');
        const mainContent = document.querySelector('.modern-main'); 

        const closeSidebar = () => {
            if (sidebar) {
                sidebar.classList.remove('show');
                document.body.classList.remove('sidebar-open');
                
                // Add smooth transition
                sidebar.style.transition = 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
            }
        };

        const openSidebar = () => {
            if (sidebar) {
                sidebar.classList.add('show');
                document.body.classList.add('sidebar-open');
                
                // Add smooth transition
                sidebar.style.transition = 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
            }
        };

        if (sidebarToggler) {
            sidebarToggler.addEventListener('click', (e) => {
                e.stopPropagation();
                openSidebar();
            });
        }
        
        if (sidebarClose) {
            sidebarClose.addEventListener('click', (e) => {
                e.stopPropagation();
                closeSidebar();
            });
        }

        // Close sidebar when clicking on backdrop (main content area)
        if (mainContent) {
            mainContent.addEventListener('click', (e) => {
                if (document.body.classList.contains('sidebar-open') && window.innerWidth < 992) {
                    if (e.target.closest('#sidebar') === null && e.target.closest('#sidebarToggler') === null) {
                        closeSidebar();
                    }
                }
            });
        }

        // Close sidebar on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && document.body.classList.contains('sidebar-open')) {
                closeSidebar();
            }
        });

        // Handle window resize
        let resizeTimer;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                if (window.innerWidth >= 992) {
                    closeSidebar();
                }
            }, 250);
        });
    }

    // Enhanced dropdown menus with smooth animations
    setupDropdowns() {
        const navDropdowns = document.querySelectorAll('.nav-list .has-submenu');
        
        navDropdowns.forEach(dropdown => {
            const toggler = dropdown.querySelector('.sidebar-toggler');
            const submenu = dropdown.querySelector('.sidebar-submenu');
            
            if (!toggler || !submenu) return;

            // Set initial state for open menus
            if (submenu.style.maxHeight && submenu.style.maxHeight !== '0px') {
                submenu.style.maxHeight = submenu.scrollHeight + "px";
                dropdown.classList.add('open');
            }

            toggler.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                // Close other open dropdowns (accordion behavior)
                navDropdowns.forEach(otherDropdown => {
                    if (otherDropdown !== dropdown && otherDropdown.classList.contains('open')) {
                        otherDropdown.classList.remove('open');
                        const otherSubmenu = otherDropdown.querySelector('.sidebar-submenu');
                        if (otherSubmenu) {
                            otherSubmenu.style.maxHeight = 0;
                        }
                    }
                });
                
                // Toggle current dropdown
                dropdown.classList.toggle('open');

                if (dropdown.classList.contains('open')) {
                    // Open with smooth animation
                    submenu.style.maxHeight = submenu.scrollHeight + "px";
                    
                    // Add a slight delay for smooth appearance
                    setTimeout(() => {
                        submenu.style.opacity = '1';
                    }, 50);
                } else {
                    // Close with smooth animation
                    submenu.style.maxHeight = 0;
                    submenu.style.opacity = '0';
                }
            });

            // Add hover effect for parent items
            toggler.addEventListener('mouseenter', function() {
                if (!dropdown.classList.contains('open')) {
                    toggler.style.transform = 'translateX(-2px)';
                }
            });

            toggler.addEventListener('mouseleave', function() {
                toggler.style.transform = 'translateX(0)';
            });
        });
    }

    // Enhanced tooltips
    setupAdvancedTooltips() {
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl, {
                    trigger: 'hover focus',
                    placement: 'auto',
                    delay: { show: 300, hide: 100 }
                });
            });
        }
    }

    // Handle flash messages with modern toast notifications
    handleFlashMessages() {
        const notificationsContainer = document.getElementById('flash-messages-container');
        if (!notificationsContainer) return;
        
        const flashMessages = notificationsContainer.querySelectorAll('.modern-alert');
        
        flashMessages.forEach((alertEl, index) => {
            // Auto-dismiss after 5 seconds with fade out
            setTimeout(() => {
                alertEl.style.animation = 'slideOutUp 0.4s ease-out forwards';
                setTimeout(() => {
                    alertEl.remove();
                }, 400);
            }, 5000 + (index * 200)); // Stagger dismissal for multiple messages
            
            // Add close button functionality if exists
            const closeBtn = alertEl.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => {
                    alertEl.style.animation = 'slideOutUp 0.4s ease-out forwards';
                    setTimeout(() => {
                        alertEl.remove();
                    }, 400);
                });
            }
        });
    }

    // Smooth scrolling for anchor links
    initSmoothScrolling() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                const href = this.getAttribute('href');
                if (href === '#' || href === '') return;
                
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    // Enhance table interactions
    enhanceTableInteractions() {
        const tables = document.querySelectorAll('.table');
        
        tables.forEach(table => {
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                // Add subtle scale effect on hover
                row.addEventListener('mouseenter', function() {
                    this.style.transition = 'all 0.2s ease';
                });
                
                row.addEventListener('mouseleave', function() {
                    this.style.transition = 'all 0.2s ease';
                });
            });
        });
    }

    // Utility: Show toast notification (can be called from other scripts)
    static showToast(message, type = 'info', duration = 5000) {
        const container = document.getElementById('flash-messages-container') || document.body;
        
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} alert-dismissible fade show modern-alert`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <i class="alert-icon"></i>
            <span>${message}</span>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        container.appendChild(toast);
        
        // Auto-dismiss
        setTimeout(() => {
            toast.style.animation = 'slideOutUp 0.4s ease-out forwards';
            setTimeout(() => {
                toast.remove();
            }, 400);
        }, duration);
        
        // Manual close
        const closeBtn = toast.querySelector('.btn-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                toast.style.animation = 'slideOutUp 0.4s ease-out forwards';
                setTimeout(() => {
                    toast.remove();
                }, 400);
            });
        }
    }
}

// Add slideOutUp animation to CSS dynamically if not exists
if (!document.querySelector('#modern-animations')) {
    const style = document.createElement('style');
    style.id = 'modern-animations';
    style.textContent = `
        @keyframes slideOutUp {
            from {
                opacity: 1;
                transform: translateY(0);
            }
            to {
                opacity: 0;
                transform: translateY(-20px);
            }
        }
    `;
    document.head.appendChild(style);
}

// Initialize Modern UX when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.modernUX = new ModernUX();
    
    // Expose showToast globally for backward compatibility
    window.showToast = ModernUX.showToast;
});

// Export for use in other modules if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ModernUX;
}

