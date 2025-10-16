// ==========================================================================
// == SAWAEDNA COST APP - MODERN JAVASCRIPT ENHANCEMENTS ==
// == Version: 8.0 - Enhanced & Optimized ==
// ==========================================================================

document.addEventListener("DOMContentLoaded", function() {
    console.log("🚀 Sawaedna Cost App - Modern JavaScript Loaded");
    
    // Initialize all modern features
    initializeModernFeatures();
    setupEnhancedSidebar();
    setupPasswordToggle();
    setupBulkActions();
    setupPaymentModal();
    setupAdvancedSearch();
    setupRealTimeCalculations();
    setupMobileOptimizations();
    setupPerformanceOptimizations();
});

// ==========================================================================
// == MODERN FEATURE INITIALIZATION ==
// ==========================================================================

function initializeModernFeatures() {
    // Add loading animation to all buttons
    document.querySelectorAll('button[type="submit"], .btn-primary, .btn-success').forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (!this.classList.contains('no-loading')) {
                this.classList.add('loading');
                this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>' + this.textContent;
                
                // Auto remove loading state after 3 seconds (fallback)
                setTimeout(() => {
                    this.classList.remove('loading');
                    this.innerHTML = this.innerHTML.replace('<i class="fas fa-spinner fa-spin me-2"></i>', '');
                }, 3000);
            }
        });
    });

    // Add smooth scrolling to all internal links
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

    // Initialize tooltips
    initializeTooltips();
    
    // Add fade-in animation to cards and tables
    addScrollAnimations();
}

// ==========================================================================
// == ENHANCED SIDEBAR FUNCTIONALITY ==
// ==========================================================================

function setupEnhancedSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const openSidebarBtn = document.getElementById('open-sidebar-btn');
    const closeSidebarBtn = document.getElementById('close-sidebar-btn');
    const sidebarOverlay = document.getElementById('sidebar-overlay');

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
        
        if (closeSidebarBtn) {
            closeSidebarBtn.addEventListener('click', closeSidebar);
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
            document.body.style.overflow = 'hidden';
            if (sidebarOverlay) {
                sidebarOverlay.classList.add('show');
            }
        }
    }

    function closeSidebar() {
        if (sidebar) {
            sidebar.classList.remove('show');
            document.body.style.overflow = '';
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
    const togglePassword = document.querySelector("#togglePassword");
    const passwordInput = document.querySelector("#password");
    const confirmPasswordInput = document.querySelector("#confirm_password");
    
    if (togglePassword && passwordInput) {
        togglePassword.addEventListener("click", function () {
            const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
            passwordInput.setAttribute("type", type);
            
            if (confirmPasswordInput) {
                confirmPasswordInput.setAttribute("type", type);
            }
            
            // Enhanced icon animation
            this.classList.toggle("fa-eye");
            this.classList.toggle("fa-eye-slash");
            this.style.transform = "scale(1.2)";
            
            setTimeout(() => {
                this.style.transform = "scale(1)";
            }, 200);
        });
        
        // Add focus effects
        [passwordInput, confirmPasswordInput].forEach(input => {
            if (input) {
                input.addEventListener('focus', function() {
                    this.parentElement.classList.add('input-focused');
                });
                
                input.addEventListener('blur', function() {
                    this.parentElement.classList.remove('input-focused');
                });
            }
        });
    }
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
                    btn.style.transform = hasSelection ? 'scale(1.05)' : 'scale(1)';
                    btn.style.transition = 'transform 0.2s ease';
                }
            });

            // Show/hide bulk actions section based on selection
            const bulkSection = document.querySelector('.bulk-actions-section');
            if (bulkSection) {
                if (hasSelection) {
                    bulkSection.style.display = 'block';
                    bulkSection.style.animation = 'fadeInUp 0.3s ease';
                } else {
                    bulkSection.style.display = 'none';
                }
            }
        }

        // Select All functionality with enhanced UI
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', function() {
                const isChecked = this.checked;
                
                itemCheckboxes.forEach(checkbox => {
                    checkbox.checked = isChecked;
                    // Add visual feedback
                    checkbox.parentElement.style.backgroundColor = isChecked ? 'rgba(37, 99, 235, 0.1)' : '';
                });
                
                updateSelectedState();
                
                // Visual feedback for select all
                this.parentElement.style.backgroundColor = isChecked ? 'rgba(37, 99, 235, 0.2)' : '';
                setTimeout(() => {
                    this.parentElement.style.backgroundColor = '';
                }, 500);
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
                    this.parentElement.style.backgroundColor = this.checked ? 'rgba(37, 99, 235, 0.1)' : '';
                    
                    updateSelectedState();
                });
                
                // Hover effects
                checkbox.addEventListener('mouseenter', function() {
                    this.parentElement.style.backgroundColor = 'rgba(37, 99, 235, 0.05)';
                });
                
                checkbox.addEventListener('mouseleave', function() {
                    if (!this.checked) {
                        this.parentElement.style.backgroundColor = '';
                    }
                });
            });
        }

        // Enhanced bulk action buttons
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
            const paymentId = button.getAttribute('data-payment-id');
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
                        <div class="loading-spinner">
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
                        row.style.animationDelay = (index * 0.1) + 's';
                        row.classList.add('fade-in-row');
                        
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
                    totalRow.classList.add('table-primary', 'fade-in-row');
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
            this.querySelector('.modal-content').classList.add('animate__animated', 'animate__fadeInUp');
        });
    }
}

// ==========================================================================
// == ADVANCED SEARCH FUNCTIONALITY ==
// ==========================================================================

function setupAdvancedSearch() {
    // Quick search for projects table
    const projectSearch = document.getElementById('project-quick-search');
    if (projectSearch) {
        projectSearch.addEventListener('input', debounce(function() {
            const filter = this.value.toLowerCase();
            const rows = document.querySelectorAll('#projects-table tbody tr');
            
            rows.forEach(row => {
                const name = row.querySelector('td:nth-child(1)').textContent.toLowerCase();
                const statusElement = row.querySelector('[data-project-status]');
                const status = statusElement ? statusElement.getAttribute('data-project-status').toLowerCase() : '';
                
                if (name.includes(filter) || status.includes(filter)) {
                    row.style.display = '';
                    row.classList.add('search-highlight');
                    setTimeout(() => row.classList.remove('search-highlight'), 1000);
                } else {
                    row.style.display = 'none';
                }
            });
            
            // Show search results count
            const visibleRows = document.querySelectorAll('#projects-table tbody tr:not([style*="display: none"])');
            updateSearchResultsCount(visibleRows.length, rows.length);
        }, 300));
    }
    
    // Quick search for contractors table
    const contractorSearch = document.getElementById('contractor-quick-search');
    if (contractorSearch) {
        contractorSearch.addEventListener('input', debounce(function() {
            const filter = this.value.toLowerCase();
            const table = document.getElementById('contractors-table');
            if (!table) return;
            
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(row => {
                const name = row.querySelector('td:nth-child(1)').textContent.toLowerCase();
                const contact = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
                const phone = row.querySelector('td:nth-child(3)').textContent.toLowerCase();
                
                if (name.includes(filter) || contact.includes(filter) || phone.includes(filter)) {
                    row.style.display = '';
                    row.classList.add('search-highlight');
                    setTimeout(() => row.classList.remove('search-highlight'), 1000);
                } else {
                    row.style.display = 'none';
                }
            });
        }, 300));
    }
}

// ==========================================================================
// == REAL-TIME CALCULATIONS ==
// ==========================================================================

function setupRealTimeCalculations() {
    // Real-time calculation for contract total
    const contractQtyInput = document.getElementById('contract_quantity');
    const contractUnitCostInput = document.getElementById('contract_unit_cost');
    const contractTotalInput = document.getElementById('contract_total_cost');
    
    if (contractQtyInput && contractUnitCostInput && contractTotalInput) {
        [contractQtyInput, contractUnitCostInput].forEach(input => {
            input.addEventListener('input', debounce(() => {
                calculateContractTotal();
            }, 200));
        });
    }
    
    // Real-time calculation for cost details
    document.querySelectorAll('.cost-input').forEach(input => {
        input.addEventListener('input', debounce(() => {
            calculateCostDetailTotal();
        }, 200));
    });
}

function calculateContractTotal() {
    const qty = parseFloat(contractQtyInput.value) || 0;
    const cost = parseFloat(contractUnitCostInput.value) || 0;
    const total = qty * cost;
    
    contractTotalInput.value = total.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// ==========================================================================
// == MOBILE OPTIMIZATIONS ==
// ==========================================================================

function setupMobileOptimizations() {
    // Improve touch experience
    document.querySelectorAll('.btn, .sidebar-link, .table-row').forEach(element => {
        element.style.minHeight = '44px';
        element.style.minWidth = '44px';
        element.classList.add('touch-optimized');
    });
    
    // Handle orientation changes
    window.addEventListener('orientationchange', function() {
        setTimeout(() => {
            window.dispatchEvent(new Event('resize'));
        }, 300);
    });
    
    // Prevent zoom on double-tap
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
// == PERFORMANCE OPTIMIZATIONS ==
// ==========================================================================

function setupPerformanceOptimizations() {
    // Lazy load images
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img.lazy').forEach(img => {
            imageObserver.observe(img);
        });
    }
    
    // Debounced resize handler
    window.addEventListener('resize', debounce(() => {
        // Handle responsive adjustments
        adjustLayoutForScreenSize();
    }, 250));
}

// ==========================================================================
// == UTILITY FUNCTIONS ==
// ==========================================================================

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

function formatDate(dateString) {
    if (!dateString) return '-';
    
    try {
        const date = new Date(dateString);
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
    button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> جاري المعالجة...';
    
    // Auto reset after 5 seconds (fallback)
    setTimeout(() => {
        button.disabled = false;
        button.innerHTML = originalText;
    }, 5000);
}

function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function addScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in-up');
            }
        });
    }, observerOptions);
    
    // Observe cards and tables for animation
    document.querySelectorAll('.card, .table-responsive').forEach(el => {
        observer.observe(el);
    });
}

function updateSearchResultsCount(visible, total) {
    let countElement = document.getElementById('search-results-count');
    
    if (!countElement) {
        countElement = document.createElement('div');
        countElement.id = 'search-results-count';
        countElement.className = 'search-results-count';
        document.querySelector('.card-header').appendChild(countElement);
    }
    
    countElement.textContent = `عرض ${visible} من أصل ${total} نتيجة`;
    countElement.style.display = visible === total ? 'none' : 'block';
}

function adjustLayoutForScreenSize() {
    const width = window.innerWidth;
    
    if (width < 768) {
        document.body.classList.add('mobile-view');
        // Mobile-specific adjustments
    } else {
        document.body.classList.remove('mobile-view');
    }
}

// ==========================================================================
// == ENHANCED CSS DYNAMICALLY ==
// ==========================================================================

// Inject additional CSS for enhanced features
const enhancedStyles = `
    .loading {
        position: relative;
        pointer-events: none;
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
    
    .search-highlight {
        animation: highlight 1s ease;
    }
    
    @keyframes highlight {
        0% { background-color: rgba(37, 99, 235, 0.3); }
        100% { background-color: transparent; }
    }
    
    .fade-in-row {
        animation: fadeInRow 0.5s ease forwards;
        opacity: 0;
    }
    
    @keyframes fadeInRow {
        to { opacity: 1; }
    }
    
    .sidebar-overlay {
        position: fixed;
        top: 0;
        left: 0;
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
    
    .input-focused {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 0.2rem rgba(37, 99, 235, 0.25) !important;
    }
    
    .touch-optimized {
        -webkit-tap-highlight-color: transparent;
        user-select: none;
    }
    
    .search-results-count {
        font-size: 0.875rem;
        color: #6b7280;
        margin-top: 0.5rem;
    }
    
    @media (max-width: 768px) {
        .mobile-view .table-responsive {
            font-size: 0.875rem;
        }
    }
`;

// Inject styles into the document
const styleSheet = document.createElement('style');
styleSheet.textContent = enhancedStyles;
document.head.appendChild(styleSheet);

// ==========================================================================
// == ERROR HANDLING & FALLBACKS ==
// ==========================================================================

// Global error handler for better user experience
window.addEventListener('error', function(e) {
    console.error('Application Error:', e.error);
    
    // Show user-friendly error message
    if (e.error && e.error.message) {
        showToast('حدث خطأ غير متوقع. يرجى تحديث الصفحة والمحاولة مرة أخرى.', 'error');
    }
});

// Unhandled promise rejection handler
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled Promise Rejection:', e.reason);
    showToast('حدث خطأ في النظام. يرجى المحاولة مرة أخرى.', 'error');
});

// Simple toast notification function
function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
            ${message}
        </div>
        <button class="toast-close">&times;</button>
    `;
    
    // Add to page
    document.body.appendChild(toast);
    
    // Show toast
    setTimeout(() => toast.classList.add('show'), 100);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 5000);
    
    // Close on button click
    toast.querySelector('.toast-close').addEventListener('click', () => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    });
}

console.log("✅ Enhanced JavaScript successfully loaded and initialized");
