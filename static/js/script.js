document.addEventListener("DOMContentLoaded", function() {
    
    // --- START: NEW Sidebar Auto-Open Logic ---
    function activateSidebarMenu() {
        const currentPath = window.location.pathname;
        let activeSection = null;

        if (currentPath.includes('/projects/') || currentPath.includes('/items/') || currentPath.includes('/sheets/')) {
            activeSection = 'project';
        } else if (currentPath.startsWith('/projects')) {
            activeSection = 'project';
        } else if (currentPath.includes('/invoices/')) {
            activeSection = 'invoice';
        } else if (currentPath.includes('/contractors/')) {
            activeSection = 'contractor';
        } else if (currentPath.includes('/admin/')) {
            activeSection = 'admin';
        }

        // Deactivate all active links first
        document.querySelectorAll('.sidebar-link.active').forEach(link => link.classList.remove('active'));
        document.querySelectorAll('.sidebar-submenu.show').forEach(menu => menu.classList.remove('show'));
        document.querySelectorAll('.sidebar-link:not(.collapsed)').forEach(link => link.classList.add('collapsed'));

        if (activeSection) {
            const activeLink = document.querySelector(`.sidebar-link[data-section="${activeSection}"]`);
            if (activeLink) {
                // If it's a main link, make it active
                if (!activeLink.hasAttribute('data-bs-toggle')) {
                     activeLink.classList.add('active');
                }
                
                // If it's a dropdown, open it
                const submenuId = activeLink.getAttribute('href');
                if (submenuId) {
                    const submenu = document.querySelector(submenuId);
                    if (submenu) {
                        activeLink.classList.remove('collapsed');
                        submenu.classList.add('show');
                    }
                }
            }
        } else if (currentPath === '/' || currentPath.startsWith('/projects')) {
             const homeLink = document.querySelector('.sidebar-link[data-section="home"]');
             if(homeLink) homeLink.classList.add('active');
        }
    }
    
    // Run the function to set the correct menu state on page load
    activateSidebarMenu();
    // --- END: NEW Sidebar Auto-Open Logic ---

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