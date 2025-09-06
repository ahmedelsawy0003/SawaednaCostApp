document.addEventListener("DOMContentLoaded", function() {
    
    // --- START: NEW - Force Sidebar Collapse Initialization ---
    // This code finds all sidebar links that should act as a collapse trigger.
    const sidebarCollapses = document.querySelectorAll('.sidebar-link[data-bs-toggle="collapse"]');
    
    // It then manually initializes the Bootstrap Collapse functionality for each one.
    // This ensures that the click-to-open/close feature works even if the default
    // Bootstrap initialization fails for some reason.
    sidebarCollapses.forEach(function (element) {
        // We find the target of the collapse (the <ul> menu) using the href attribute.
        let target = document.querySelector(element.getAttribute('href'));
        if (target) {
            // We create a new Collapse instance but prevent it from toggling on its own
            // during initialization. This respects the 'show' class we added in base.html.
            new bootstrap.Collapse(target, {
                toggle: false
            });
        }
    });
    // --- END: NEW - Force Sidebar Collapse Initialization ---

    // --- Sidebar Toggle Functionality for mobile ---
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
    
    // Toast Functionality for Flash Messages
    const toastElList = document.querySelectorAll('.toast');
    [...toastElList].map(toastEl => {
        const toast = new bootstrap.Toast(toastEl, {
            autohide: true,
            delay: 5000
        });
        toast.show();
        return toast;
    });

    // Password Toggle Functionality
    const togglePassword = document.querySelector("#togglePassword");
    const passwordInput = document.querySelector("#password");

    if (togglePassword && passwordInput) {
        togglePassword.addEventListener("click", function () {
            const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
            passwordInput.setAttribute("type", type);
            
            this.classList.toggle("fa-eye");
            this.classList.toggle("fa-eye-slash");
        });
    }

    // --- Bulk actions section ---
    const selectAllCheckbox = document.getElementById('select-all');
    const itemCheckboxes = document.querySelectorAll('.item-checkbox');
    const bulkEditForm = document.getElementById('bulk-edit-form');
    
    const selectedCountDisplay = document.getElementById('selected-count-display'); 
    const bulkUpdateBtn = document.getElementById('bulk-update-btn');
    const bulkDeleteBtn = document.getElementById('bulk-delete-btn');

    const bulkDeleteCount = document.getElementById('bulk-delete-count');
    const confirmBulkDeleteBtn = document.getElementById('confirm-bulk-delete-btn');

    if (selectAllCheckbox && itemCheckboxes.length > 0 && bulkEditForm) {
        
        function updateSelectedState() {
            const count = document.querySelectorAll('.item-checkbox:checked').length;
            
            if (selectedCountDisplay) {
                selectedCountDisplay.textContent = count;
            }
            if (bulkDeleteCount) {
                bulkDeleteCount.textContent = count;
            }

            const hasSelection = count > 0;
            if (bulkUpdateBtn) {
                bulkUpdateBtn.disabled = !hasSelection;
            }
            if (bulkDeleteBtn) {
                bulkDeleteBtn.disabled = !hasSelection;
            }
        }

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
        
        if (confirmBulkDeleteBtn) {
            confirmBulkDeleteBtn.addEventListener('click', function() {
                bulkEditForm.action = bulkEditForm.action.replace('bulk_update', 'bulk_delete');
                bulkEditForm.submit();
            });
        }
        updateSelectedState();
    }
});