document.addEventListener("DOMContentLoaded", function() {
    
    // --- START: NEW Custom Sidebar Toggler ---
    function setupSidebarToggler() {
        const togglers = document.querySelectorAll('.sidebar-toggler');

        togglers.forEach(toggler => {
            const submenu = toggler.nextElementSibling;

            if (submenu && submenu.classList.contains('sidebar-submenu')) {
                // Check if any link inside the submenu matches the current page URL
                let isSectionActive = false;
                submenu.querySelectorAll('a.sidebar-submenu-link').forEach(link => {
                    // Using 'pathname' to ignore query strings or hashes
                    if (link.pathname === window.location.pathname) {
                        isSectionActive = true;
                    }
                });

                // If a link is active, open this submenu by default on page load
                if (isSectionActive) {
                    toggler.classList.add('is-active');
                    submenu.classList.add('is-open');
                }

                // Add the click event listener to the toggler
                toggler.addEventListener('click', function(event) {
                    event.preventDefault(); // Prevent default link behavior

                    // Toggle the active classes for the icon and the menu visibility
                    this.classList.toggle('is-active');
                    submenu.classList.toggle('is-open');
                });
            }
        });

        // Also, set the 'active' class on the main "الرئيسية" link if it's the current page
        document.querySelectorAll('.sidebar-link').forEach(link => {
            if (link.href === window.location.href) {
                link.classList.add('active');
            }
        });
    }

    // Run the function to activate the sidebar
    setupSidebarToggler();
    // --- END: NEW Custom Sidebar Toggler ---


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