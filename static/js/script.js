// ==========================================================================
// == SAWAEDNA COST APP - ATLANTIS DESIGN SYSTEM JS (Core Features) ==
// == Version: 9.0 - Optimized & Unified JS ==
// ==========================================================================

document.addEventListener("DOMContentLoaded", function() {
    console.log("🚀 Sawaedna Cost App - Atlantis JavaScript Loaded");
    
    // Initialize core features
    initializeCoreFeatures();
    setupEnhancedSidebar();
    setupPasswordToggle();
    setupBulkActions();
    setupPaymentModal();
    // setupAdvancedSearch is now handled in modern.js for unification
    setupRealTimeCalculations();
    setupMobileOptimizations();
});

// ==========================================================================
// == UTILITY FUNCTIONS (Centralized) ==
// ==========================================================================

// Global debounce function (moved here to centralize)
function debounce(func, wait) {
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

// Simple toast notification function (New Atlantis System)
window.showToast = function(message, type = 'info') {
    // 1. Create toast container if it doesn't exist (positioned in the top-left)
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'modern-notifications'; // Use the CSS class defined in style.css
        document.body.appendChild(container);
    }

    // 2. Create the toast element
    const toast = document.createElement('div');
    toast.className = `modern-alert alert-${type}`;
    
    // Determine the icon based on the type (using Font Awesome)
    let iconClass = 'fa-info-circle';
    if (type === 'success') iconClass = 'fa-check-circle';
    if (type === 'danger') iconClass = 'fa-exclamation-triangle';
    if (type === 'warning') iconClass = 'fa-exclamation-circle';

    toast.innerHTML = `
        <i class="alert-icon fas ${iconClass}"></i>
        <span>${message}</span>
        <button class="alert-close">&times;</button>
    `;
    
    // 3. Add to container and show
    container.prepend(toast); // Add to the beginning (LIFO)
    
    // 4. Auto remove after 5 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(-100%)';
        setTimeout(() => toast.remove(), 500); // Remove after animation
    }, 5000);
    
    // 5. Close on button click
    toast.querySelector('.alert-close').addEventListener('click', () => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(-100%)';
        setTimeout(() => toast.remove(), 500);
    });
}

// Global error handler for better user experience
window.addEventListener('error', function(e) {
    console.error('Application Error:', e.error);
    if (e.error && e.error.message) {
        // Use the new centralized showToast
        showToast('حدث خطأ غير متوقع. يرجى تحديث الصفحة والمحاولة مرة أخرى.', 'danger');
    }
});

// Unhandled promise rejection handler
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled Promise Rejection:', e.reason);
    showToast('حدث خطأ في النظام. يرجى المحاولة مرة أخرى.', 'danger');
});

function formatDate(dateString) {
    if (!dateString) return '-';
    
    try {
        const date = new Date(dateString);
        // نستخدم التنسيق العربي مع الحماية من الأخطاء
        return date.toLocaleDateString('ar-EG', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        });
    } catch (e) {
        return dateString;
    }
}

function showLoadingState(button) {
    const originalText = button.innerHTML;
    button.disabled = true;
    // استخدام أيقونة التحميل الجديدة
    button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> جاري المعالجة...';
    
    // Auto reset after 5 seconds (fallback)
    setTimeout(() => {
        button.disabled = false;
        button.innerHTML = originalText;
    }, 5000);
}

// ==========================================================================
// == CORE FEATURE INITIALIZATION ==
// ==========================================================================

function initializeCoreFeatures() {
    // 1. Add loading animation to all buttons (Optimized)
    document.querySelectorAll('button[type="submit"], .btn-primary, .btn-success, .btn-warning, .btn-danger, .btn-info').forEach(btn => {
        btn.addEventListener('click', function(e) {
            // Prevent adding loading state if button is already disabled or has 'no-loading' class
            if (!this.classList.contains('no-loading') && !this.disabled && !this.classList.contains('loading')) {
                // Remove existing content before setting loading text
                const originalContent = this.innerHTML;
                
                this.classList.add('loading');
                this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> جاري...';
                
                // Store original content for fallback removal
                this.dataset.originalContent = originalContent;

                // Auto remove loading state after 4 seconds (fallback)
                setTimeout((button) => {
                    if (button.classList.contains('loading')) {
                         button.classList.remove('loading');
                         button.innerHTML = button.dataset.originalContent;
                    }
                }, 4000, this);
            }
        });
    });

    // 2. Add smooth scrolling to all internal links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
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
}

// ==========================================================================
// == ENHANCED SIDEBAR FUNCTIONALITY ==
// ==========================================================================

// Function remains mostly the same, now relying on modern.js for tooltips
function setupEnhancedSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const openSidebarBtn = document.getElementById('sidebarToggler'); // Changed ID to match base.html
    const sidebarCloseBtn = document.getElementById('sidebarClose');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    
    // The rest of the sidebar logic is preserved as it is robust.
    // ... (Your original sidebar logic) ...
    // Create overlay if it doesn't exist
    if (!sidebarOverlay && sidebar) {
        const overlay = document.createElement('div');
        overlay.id = 'sidebar-overlay';
        overlay.className = 'sidebar-overlay';
        document.body.appendChild(overlay);
        
        overlay.addEventListener('click', closeSidebar);
    }
    
    // Enhanced sidebar togglers with animations
    const togglers = document.querySelectorAll('.sidebar-toggler');
    
    togglers.forEach(toggler => {
        toggler.addEventListener('click', function(event) {
            event.preventDefault();
            event.stopPropagation();
            
            const submenu = this.nextElementSibling;
            const icon = this.querySelector('.toggle-icon');
            
            if (submenu && submenu.classList.contains('sidebar-submenu')) {
                // Toggle with smooth animation
                this.classList.toggle('is-active');
                
                if (submenu.style.maxHeight) {
                    submenu.style.maxHeight = null;
                    submenu.style.opacity = '0';
                    if (icon) icon.classList.replace('fa-chevron-down', 'fa-chevron-left');
                } else {
                    submenu.style.maxHeight = submenu.scrollHeight + 'px';
                    submenu.style.opacity = '1';
                    if (icon) icon.classList.replace('fa-chevron-left', 'fa-chevron-down');
                }
                
                // Add transition for smooth animation
                submenu.style.transition = 'max-height 0.3s ease, opacity 0.3s ease';
            }
        });
    });

    // Mobile sidebar functionality
    if (sidebar && openSidebarBtn) {
        openSidebarBtn.addEventListener('click', openSidebar);
        
        if (sidebarCloseBtn) {
            sidebarCloseBtn.addEventListener('click', closeSidebar);
        }
        
        // Close sidebar when clicking on overlay
        if (sidebarOverlay) {
            sidebarOverlay.addEventListener('click', closeSidebar);
        }
        
        // Close sidebar when pressing Escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeSidebar();
            }
        });
    }

    function openSidebar() {
        if (sidebar) {
            sidebar.classList.add('show');
            document.body.classList.add('sidebar-open'); // New class to manage body overflow
            if (sidebarOverlay) {
                sidebarOverlay.classList.add('show');
            }
        }
    }

    function closeSidebar() {
        if (sidebar) {
            sidebar.classList.remove('show');
            document.body.classList.remove('sidebar-open');
            if (sidebarOverlay) {
                sidebarOverlay.classList.remove('show');
            }
        }
    }
}

// ==========================================================================
// == ENHANCED PASSWORD TOGGLE ==
// ==========================================================================

function setupPasswordToggle() {
    const togglePassword = document.querySelectorAll(".password-toggle-icon");
    
    togglePassword.forEach(toggleBtn => {
        toggleBtn.addEventListener("click", function () {
            // Find the nearest password input sibling
            const passwordInput = this.closest('.input-group').querySelector('input[type="password"], input[type="text"]');
            
            if (passwordInput) {
                const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
                passwordInput.setAttribute("type", type);
                
                // Enhanced icon animation
                this.classList.toggle("fa-eye");
                this.classList.toggle("fa-eye-slash");
                this.style.transform = "scale(1.2)";
                
                setTimeout(() => {
                    this.style.transform = "scale(1)";
                }, 200);
            }
        });
    });

    // Add focus effects to all relevant inputs
    document.querySelectorAll('input[type="password"], input[type="text"], input[type="email"], input[type="number"], input[type="date"]').forEach(input => {
        if (input) {
            input.addEventListener('focus', function() {
                // Find parent element that should get the focus class
                const parent = this.closest('.input-group') || this.parentElement;
                parent.classList.add('input-focused');
            });
            
            input.addEventListener('blur', function() {
                const parent = this.closest('.input-group') || this.parentElement;
                parent.classList.remove('input-focused');
            });
        }
    });
}

// ==========================================================================
// == ENHANCED BULK ACTIONS ==
// ==========================================================================

function setupBulkActions() {
    const bulkEditForm = document.getElementById('bulk-edit-form');
    
    if (bulkEditForm) {
        const selectAllCheckbox = document.getElementById('select-all');
        const itemCheckboxes = document.querySelectorAll('.item-checkbox');
        const selectedCountDisplay = document.getElementById('selected-count-display');
        const bulkUpdateBtn = document.getElementById('bulk-update-btn');
        const bulkDeleteBtn = document.getElementById('bulk-delete-btn');
        const bulkDuplicateBtn = document.getElementById('bulk-duplicate-btn');
        const bulkDeleteCountDisplay = document.getElementById('bulk-delete-count-display');
        const bulkDuplicateCountDisplay = document.getElementById('bulk-duplicate-count');
        const bulkDeleteCount = document.getElementById('bulk-delete-count');
        const confirmBulkDeleteBtn = document.getElementById('confirm-bulk-delete-btn');
        const confirmBulkDuplicateBtn = document.getElementById('confirm-bulk-duplicate-btn');

        // Enhanced selection functionality
        function updateSelectedState() {
            const count = document.querySelectorAll('.item-checkbox:checked').length;
            
            // Update all count displays
            if (selectedCountDisplay) selectedCountDisplay.textContent = count;
            if (bulkDeleteCount) bulkDeleteCount.textContent = count;
            if (bulkDeleteCountDisplay) bulkDeleteCountDisplay.textContent = count;
            if (bulkDuplicateCountDisplay) bulkDuplicateCountDisplay.textContent = count;

            const hasSelection = count > 0;
            
            // Update button states with animations
            [bulkUpdateBtn, bulkDeleteBtn, bulkDuplicateBtn].forEach(btn => {
                if (btn) {
                    btn.disabled = !hasSelection;
                    // Remove scale animation as it is distracting
                }
            });

            // Show/hide bulk actions section based on selection
            const bulkSection = document.getElementById('collapseBulkEdit');
            if (bulkSection) {
                 // Use Bootstrap's collapse function
                 const bsCollapse = bootstrap.Collapse.getOrCreateInstance(bulkSection, { toggle: false });
                if (hasSelection) {
                    bsCollapse.show();
                } else {
                    bsCollapse.hide();
                }
            }
        }

        // Select All functionality with enhanced UI
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', function() {
                const isChecked = this.checked;
                
                itemCheckboxes.forEach(checkbox => {
                    checkbox.checked = isChecked;
                    // Add visual feedback directly to the row for better clarity
                    const row = checkbox.closest('tr');
                    if (row) {
                        row.style.backgroundColor = isChecked ? 'var(--bg-hover)' : '';
                    }
                });
                
                updateSelectedState();
            });

            // Individual checkbox functionality
            itemCheckboxes.forEach(checkbox => {
                checkbox.addEventListener('change', function() {
                    if (!this.checked) {
                        selectAllCheckbox.checked = false;
                    } else if (document.querySelectorAll('.item-checkbox:checked').length === itemCheckboxes.length) {
                        selectAllCheckbox.checked = true;
                    }
                    
                    // Visual feedback
                    const row = this.closest('tr');
                    if (row) {
                        row.style.backgroundColor = this.checked ? 'var(--bg-hover)' : '';
                    }
                    
                    updateSelectedState();
                });
                
                // Hover effects (removed for table rows as it's already handled by CSS)
            });
        }

        // Enhanced bulk action buttons (now using showLoadingState)
        if (bulkUpdateBtn) {
            bulkUpdateBtn.addEventListener('click', function(e) {
                e.preventDefault();
                showLoadingState(this);
                bulkEditForm.action = bulkEditForm.dataset.updateUrl;
                setTimeout(() => {
                    bulkEditForm.submit();
                }, 500);
            });
        }
        
        if (confirmBulkDeleteBtn) {
            confirmBulkDeleteBtn.addEventListener('click', function() {
                showLoadingState(this);
                bulkEditForm.action = bulkEditForm.dataset.deleteUrl;
                setTimeout(() => {
                    bulkEditForm.submit();
                }, 500);
            });
        }

        if (confirmBulkDuplicateBtn) {
            confirmBulkDuplicateBtn.addEventListener('click', function() {
                showLoadingState(this);
                bulkEditForm.action = bulkEditForm.dataset.duplicateUrl;
                setTimeout(() => {
                    bulkEditForm.submit();
                }, 500);
            });
        }

        // Initialize selected state
        if (selectAllCheckbox) {
            updateSelectedState();
        }
    }
}

// ==========================================================================
// == ENHANCED PAYMENT MODAL ==
// ==========================================================================

function setupPaymentModal() {
    const paymentItemsModal = document.getElementById('paymentItemsModal');
    
    if (paymentItemsModal) {
        paymentItemsModal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            const paymentAmount = button.getAttribute('data-payment-amount');
            const paymentDate = button.getAttribute('data-payment-date');
            const paymentDescription = button.getAttribute('data-payment-description');

            const modalAmount = paymentItemsModal.querySelector('#modal-payment-amount');
            const modalDate = paymentItemsModal.querySelector('#modal-payment-date');
            const modalDescription = paymentItemsModal.querySelector('#modal-payment-description');
            const modalItemsList = paymentItemsModal.querySelector('#modal-items-list');
            
            // Format and display basic payment info
            modalAmount.textContent = (parseFloat(paymentAmount) || 0).toLocaleString('en-US', { 
                minimumFractionDigits: 2, 
                maximumFractionDigits: 2 
            });
            modalDate.textContent = formatDate(paymentDate);
            modalDescription.textContent = paymentDescription === 'null' ? '-' : paymentDescription;
            
            // Show loading state
            modalItemsList.innerHTML = `
                <tr>
                    <td colspan="2" class="text-center">
                        <div class="loading-spinner py-4 text-muted">
                            <i class="fas fa-spinner fa-spin me-2"></i> جاري تحميل تفاصيل التوزيع...
                        </div>
                    </td>
                </tr>
            `;
            
            const distributionsJsonAttr = button.getAttribute('data-distributions');
            const distApiUrl = button.getAttribute('data-dist-url');

            // Enhanced data rendering with animations
            const renderRows = (list) => {
                modalItemsList.innerHTML = '';
                
                if (list && list.length > 0) {
                    list.forEach((dist, index) => {
                        const row = document.createElement('tr');
                        // Add fade-in-up class defined in modern.js / style.css
                        row.classList.add('animate-fade-in-up'); 
                        row.style.animationDelay = (index * 0.1) + 's';
                        
                        const description = dist.description || (dist.invoice_item ? dist.invoice_item.description : 'غير محدد');
                        const amount = parseFloat(dist.amount);

                        row.innerHTML = `
                            <td>${description}</td>
                            <td class="text-end fw-bold text-success number-cell">
                                ${amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ر.س
                            </td>
                        `;
                        modalItemsList.appendChild(row);
                    });
                    
                    // Add total row
                    const totalRow = document.createElement('tr');
                    totalRow.classList.add('table-primary', 'animate-fade-in-up');
                    totalRow.style.animationDelay = (list.length * 0.1) + 's';
                    
                    const totalAmount = list.reduce((sum, dist) => sum + parseFloat(dist.amount), 0);
                    
                    totalRow.innerHTML = `
                        <td class="fw-bold">الإجمالي</td>
                        <td class="text-end fw-bold text-primary number-cell">
                            ${totalAmount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ر.س
                        </td>
                    `;
                    modalItemsList.appendChild(totalRow);
                } else {
                    modalItemsList.innerHTML = `
                        <tr>
                            <td colspan="2" class="text-center text-muted py-4">
                                <i class="fas fa-info-circle me-2"></i> لم يتم العثور على توزيعات لهذه الدفعة.
                            </td>
                        </tr>
                    `;
                }
            };

            // Try embedded data first for faster loading
            if (distributionsJsonAttr && distributionsJsonAttr.trim() !== '') {
                let parsed = [];
                try { 
                    // Note: distributionsJsonAttr is already JSON-encoded string from the template.
                    // The tojson filter in Jinja2 escapes the content. We only need JSON.parse
                    // if it was the string attribute, but since we are copying from the element
                    // attribute, it might be double escaped. We rely on the template output being correct.
                    // Let's assume the template provided a clean JSON string:
                    parsed = JSON.parse(distributionsJsonAttr);
                } catch (e) { 
                    console.error("Error parsing embedded JSON data:", e);
                    parsed = []; 
                }
                renderRows(parsed);
            } 
            // Fallback to API call
            else if (distApiUrl) {
                fetch(distApiUrl, { credentials: 'same-origin' })
                    .then(response => {
                        if (!response.ok) throw new Error('Network response was not ok');
                        return response.json();
                    })
                    .then(data => {
                        renderRows(data.distributions || []);
                    })
                    .catch(error => {
                        console.error('Error fetching distributions:', error);
                        modalItemsList.innerHTML = `
                            <tr>
                                <td colspan="2" class="text-center text-danger py-4">
                                    <i class="fas fa-times-circle me-2"></i> فشل تحميل البيانات من الخادم.
                                </td>
                            </tr>
                        `;
                    });
            } else {
                renderRows([]);
            }
        });

        // Add animation when modal is fully shown
        paymentItemsModal.addEventListener('shown.bs.modal', function() {
            // Animation class is now handled by CSS or by the items themselves
        });
    }
}

// ==========================================================================
// == ADVANCED SEARCH FUNCTIONALITY (Client-Side) ==
// ==========================================================================

function setupAdvancedSearch() {
    // Quick search for projects table (Logic is moved to modern.js)
    
    // Quick search for contractors table (Logic is moved to modern.js)
}

// ==========================================================================
// == REAL-TIME CALCULATIONS ==
// ==========================================================================

// Centralized calculation logic for contract total (remains here)
const contractQtyInput = document.getElementById('contract_quantity');
const contractUnitCostInput = document.getElementById('contract_unit_cost');
const contractTotalInput = document.getElementById('contract_total_cost');

function calculateContractTotal() {
    if (!contractQtyInput || !contractUnitCostInput || !contractTotalInput) return;

    const qty = parseFloat(contractQtyInput.value) || 0;
    const cost = parseFloat(contractUnitCostInput.value) || 0;
    const total = qty * cost;
    
    contractTotalInput.value = total.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Note: calculateCostDetailTotal() is removed as it's now handled by cost_details/edit.html specific script.
function setupRealTimeCalculations() {
    // Real-time calculation for contract total
    if (contractQtyInput && contractUnitCostInput && contractTotalInput) {
        [contractQtyInput, contractUnitCostInput].forEach(input => {
            input.addEventListener('input', debounce(() => {
                calculateContractTotal();
            }, 200));
        });
        calculateContractTotal(); // Initial run
    }
    
    // Real-time calculation for cost details (Inputs are handled in their own template script now)
}


// ==========================================================================
// == MOBILE OPTIMIZATIONS ==
// ==========================================================================

function setupMobileOptimizations() {
    // Ensure sufficient touch target size (UX improvement for smaller screens)
    document.querySelectorAll('.btn, .sidebar-link, .table-row, .form-select, .form-control').forEach(element => {
        // Enforce the 44px touch target rule
        element.style.minHeight = '44px';
        element.classList.add('touch-optimized');
    });
    
    // Handle orientation changes
    window.addEventListener('orientationchange', function() {
        setTimeout(() => {
            window.dispatchEvent(new Event('resize'));
        }, 300);
    });
    
    // Prevent zoom on double-tap (optional but good for mobile UX)
    let lastTouchEnd = 0;
    document.addEventListener('touchend', function(event) {
        const now = (new Date()).getTime();
        if (now - lastTouchEnd <= 300) {
            event.preventDefault();
        }
        lastTouchEnd = now;
    }, false);
}

// ==========================================================================
// == PERFORMANCE OPTIMIZATIONS (Only essential parts remain) ==
// ==========================================================================

function setupPerformanceOptimizations() {
    // Lazy load images (remains if img.lazy class is used)
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    const src = img.dataset.src || img.getAttribute('data-src');
                    if (src) {
                        img.src = src;
                        img.removeAttribute('data-src');
                        img.classList.remove('lazy');
                    }
                    imageObserver.unobserve(img);
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('img.lazy').forEach(img => {
            imageObserver.observe(img);
        });
    }
    
    // Debounced resize handler (handled in modern.js)
}

// ==========================================================================
// == ENHANCED CSS DYNAMICALLY (Removed most CSS as it's in style.css now) ==
// ==========================================================================

const enhancedStyles = `
    /* Loading state for buttons */
    .loading {
        position: relative;
        pointer-events: none;
        color: transparent !important;
    }
    
    .loading::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 20px;
        height: 20px;
        margin: -10px 0 0 -10px;
        border: 2px solid #ffffff;
        border-radius: 50%;
        border-top-color: transparent;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Input focus visual feedback */
    .input-focused {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 0.2rem var(--bg-hover) !important;
    }
    
    /* Sidebar overlay fix */
    .sidebar-overlay {
        position: fixed;
        top: 0;
        right: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 999;
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s ease;
    }
    
    .sidebar-overlay.show {
        opacity: 1;
        visibility: visible;
    }

    /* Mobile UX improvement */
    .touch-optimized {
        -webkit-tap-highlight-color: transparent;
        user-select: none;
    }
    .sidebar-open {
        overflow: hidden;
    }
`;

// Inject styles into the document
const styleSheet = document.createElement('style');
styleSheet.textContent = enhancedStyles;
document.head.appendChild(styleSheet);

console.log("✅ Core JavaScript successfully optimized and initialized");