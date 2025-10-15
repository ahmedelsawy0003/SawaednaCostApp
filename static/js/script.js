document.addEventListener("DOMContentLoaded", function() {


    // --- START: ROBUST Sidebar Toggler ---
    function setupSidebar() {
        const togglers = document.querySelectorAll('.sidebar-toggler');

        togglers.forEach(toggler => {
            toggler.addEventListener('click', function(event) {
                event.preventDefault();
                
                // This robustly finds the submenu, even for nested items
                const submenu = this.nextElementSibling;

                if (submenu && submenu.classList.contains('sidebar-submenu')) {
                    this.classList.toggle('is-active');
                    if (submenu.style.display === 'block') {
                        submenu.style.display = 'none';
                    } else {
                        submenu.style.display = 'block';
                    }
                }
            });
        });
    }
    setupSidebar();
    // --- END: ROBUST Sidebar Toggler ---


    // --- Other functionalities ---

    // Sidebar Toggle Functionality for mobile
    const sidebar = document.querySelector('.sidebar');
    const openSidebarBtn = document.getElementById('open-sidebar-btn');
    const closeSidebarBtn = document.getElementById('close-sidebar-btn');

    if (sidebar && openSidebarBtn && closeSidebarBtn) {
        openSidebarBtn.addEventListener('click', () => {
            sidebar.classList.add('show');
        });

        closeSidebarBtn.addEventListener('click', () => {
            sidebar.classList.remove('show');
        });
    }
    
    // Toast Functionality for Flash Messages (Handled in base.html script block now for better control)
    // Removed old toast initialization here.


    // Password Toggle Functionality
    // This is the single source of truth for password toggling across all pages
    const togglePassword = document.querySelector("#togglePassword");
    const passwordInput = document.querySelector("#password");
    // Handle the password field in the register/edit_user template which might have a different ID (confirm_password)
    const confirmPasswordInput = document.querySelector("#confirm_password");
    
    if (togglePassword && passwordInput) {
        togglePassword.addEventListener("click", function () {
            const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
            passwordInput.setAttribute("type", type);
            // Also update the confirm password if it exists on the page
            if (confirmPasswordInput) {
                confirmPasswordInput.setAttribute("type", type);
            }
            
            this.classList.toggle("fa-eye");
            this.classList.toggle("fa-eye-slash");
        });
    }

    // Bulk actions section for item index page
    const bulkEditForm = document.getElementById('bulk-edit-form');
    if(bulkEditForm) {
        const selectAllCheckbox = document.getElementById('select-all');
        const itemCheckboxes = document.querySelectorAll('.item-checkbox');
        
        const selectedCountDisplay = document.getElementById('selected-count-display'); 
        const bulkUpdateBtn = document.getElementById('bulk-update-btn');
        const bulkDeleteBtn = document.getElementById('bulk-delete-btn');
        const bulkDuplicateBtn = document.getElementById('bulk-duplicate-btn');
        
        // New spans for dynamic counts on buttons
        const bulkDeleteCountDisplay = document.getElementById('bulk-delete-count-display');
        const bulkDuplicateCountDisplay = document.getElementById('bulk-duplicate-count');

        const bulkDeleteCount = document.getElementById('bulk-delete-count');
        const confirmBulkDeleteBtn = document.getElementById('confirm-bulk-delete-btn');
        const confirmBulkDuplicateBtn = document.getElementById('confirm-bulk-duplicate-btn');

        function updateSelectedState() {
            const count = document.querySelectorAll('.item-checkbox:checked').length;
            
            if (selectedCountDisplay) selectedCountDisplay.textContent = count;
            if (bulkDeleteCount) bulkDeleteCount.textContent = count;
            if (bulkDeleteCountDisplay) bulkDeleteCountDisplay.textContent = count;
            if (bulkDuplicateCountDisplay) bulkDuplicateCountDisplay.textContent = count;

            const hasSelection = count > 0;
            if (bulkUpdateBtn) bulkUpdateBtn.disabled = !hasSelection;
            if (bulkDeleteBtn) bulkDeleteBtn.disabled = !hasSelection;
            if (bulkDuplicateBtn) bulkDuplicateBtn.disabled = !hasSelection;
        }

        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', function() {
                itemCheckboxes.forEach(checkbox => {
                    checkbox.checked = this.checked;
                });
                updateSelectedState();
            });

            itemCheckboxes.forEach(checkbox => {
                checkbox.addEventListener('change', function() {
                    if (!this.checked) {
                        selectAllCheckbox.checked = false;
                    } else if (document.querySelectorAll('.item-checkbox:checked').length === itemCheckboxes.length) {
                        selectAllCheckbox.checked = true;
                    }
                    updateSelectedState();
                });
            });
        }
        
        if (bulkUpdateBtn) {
            bulkUpdateBtn.addEventListener('click', function(e) {
                e.preventDefault();
                bulkEditForm.action = bulkEditForm.dataset.updateUrl;
                bulkEditForm.submit();
            });
        }
        
        if (confirmBulkDeleteBtn) {
            confirmBulkDeleteBtn.addEventListener('click', function() {
                bulkEditForm.action = bulkEditForm.dataset.deleteUrl;
                bulkEditForm.submit();
            });
        }

        if (confirmBulkDuplicateBtn) {
            confirmBulkDuplicateBtn.addEventListener('click', function() {
                bulkEditForm.action = bulkEditForm.dataset.duplicateUrl;
                bulkEditForm.submit();
            });
        }
        
        // Initial setup for bulk actions
        if(selectAllCheckbox) {
            updateSelectedState();
        }
    }

    // START: Show Payment Items Modal
    const paymentItemsModal = document.getElementById('paymentItemsModal');
    if (paymentItemsModal) {
        paymentItemsModal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            // Get data from button attributes
            const paymentId = button.getAttribute('data-payment-id');
            const paymentAmount = button.getAttribute('data-payment-amount');
            const paymentDate = button.getAttribute('data-payment-date');
            const paymentDescription = button.getAttribute('data-payment-description');

            // Get modal elements
            const modalAmount = paymentItemsModal.querySelector('#modal-payment-amount');
            const modalDate = paymentItemsModal.querySelector('#modal-payment-date');
            const modalDescription = paymentItemsModal.querySelector('#modal-payment-description');
            const modalItemsList = paymentItemsModal.querySelector('#modal-items-list');
            
            // Set basic info
            modalAmount.textContent = parseFloat(paymentAmount).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
            modalDate.textContent = paymentDate;
            modalDescription.textContent = paymentDescription === 'null' ? '-' : paymentDescription;
            modalItemsList.innerHTML = '<tr><td colspan="2" class="text-center text-muted">جاري تحميل تفاصيل التوزيع...</td></tr>';
            
            const distributionsJsonAttr = button.getAttribute('data-distributions');
            const distApiUrl = button.getAttribute('data-dist-url');

            const renderRows = (list) => {
                modalItemsList.innerHTML = '';
                if (list && list.length > 0) {
                    list.forEach(dist => {
                        const row = document.createElement('tr');
                        const description = dist.description || (dist.invoice_item ? dist.invoice_item.description : 'غير محدد');
                        const amount = parseFloat(dist.amount);

                        row.innerHTML = `
                            <td>${description}</td>
                            <td class="text-end fw-bold text-success number-cell">${amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ر.س</td>
                        `;
                        modalItemsList.appendChild(row);
                    });
                } else {
                    modalItemsList.innerHTML = '<tr><td colspan="2" class="text-center text-muted">لم يتم العثور على توزيعات لهذه الدفعة.</td></tr>';
                }
            };

            // Attempt to use embedded data first
            if (distributionsJsonAttr && distributionsJsonAttr.trim() !== '') {
                let parsed = [];
                try { 
                    // Using JSON.parse to correctly handle the Python tojson output
                    parsed = JSON.parse(distributionsJsonAttr); 
                } catch (e) { 
                    console.error("Error parsing embedded JSON data:", e);
                    parsed = []; 
                }
                renderRows(parsed);
            } 
            // Fallback to API call if no embedded data is available
            else if (distApiUrl) {
                fetch(distApiUrl, { credentials: 'same-origin' })
                    .then(r => r.ok ? r.json() : Promise.reject())
                    .then(data => {
                        renderRows(data.distributions || []);
                    })
                    .catch(() => {
                        modalItemsList.innerHTML = '<tr><td colspan="2" class="text-center text-danger"><i class="fas fa-times-circle me-1"></i> فشل تحميل البيانات من الخادم.</td></tr>';
                    });
            } else {
                 renderRows([]);
            }
        });
    }
    // END: Show Payment Items Modal	
	
});