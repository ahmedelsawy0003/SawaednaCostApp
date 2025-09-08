document.addEventListener("DOMContentLoaded", function() {

    // --- START: FINAL Custom Sidebar Toggler (v1.4) ---
    function setupSidebar() {
        // 1. Find all links that are meant to toggle a menu.
        const togglers = document.querySelectorAll('.sidebar-toggler');

        // 2. Loop through each of these toggler links.
        togglers.forEach(toggler => {
            
            // 3. Add a click event listener to each one.
            toggler.addEventListener('click', function(event) {
                // Prevent the link from trying to navigate anywhere.
                event.preventDefault();

                // Find the submenu, which is the VERY NEXT element in the HTML.
                const submenu = this.nextElementSibling;

                // Check if the submenu actually exists.
                if (submenu) {
                    // Toggle the class on the link itself (for the arrow icon).
                    this.classList.toggle('is-active');

                    // Check if the submenu is currently visible.
                    if (submenu.style.display === 'block') {
                        // If it is visible, hide it.
                        submenu.style.display = 'none';
                    } else {
                        // If it is hidden, show it.
                        submenu.style.display = 'block';
                    }
                }
            });
        });
    }

    // Run the function to make the sidebar work.
    setupSidebar();
    // --- END: FINAL Custom Sidebar Toggler (v1.4) ---


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

    // Bulk actions section
    const selectAllCheckbox = document.getElementById('select-all');
    const itemCheckboxes = document.querySelectorAll('.item-checkbox');
    const bulkEditForm = document.getElementById('bulk-edit-form');
    
    const selectedCountDisplay = document.getElementById('selected-count-display'); 
    const bulkUpdateBtn = document.getElementById('bulk-update-btn');
    const bulkDeleteBtn = document.getElementById('bulk-delete-btn');
    const bulkDuplicateBtn = document.getElementById('bulk-duplicate-btn'); // Add this

    const bulkDeleteCount = document.getElementById('bulk-delete-count');
    const confirmBulkDeleteBtn = document.getElementById('confirm-bulk-delete-btn');
    const confirmBulkDuplicateBtn = document.getElementById('confirm-bulk-duplicate-btn'); // Add this


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
            if (bulkDeleteBtn) bulkDeleteBtn.disabled = !hasSelection;
            if (bulkDuplicateBtn) bulkDuplicateBtn.disabled = !hasSelection; // Add this
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
                bulkEditForm.action = "{{ url_for('item.bulk_delete_items', project_id=project.id) }}";
                bulkEditForm.submit();
            });
        }

        if (confirmBulkDuplicateBtn) { // Add this whole block
            confirmBulkDuplicateBtn.addEventListener('click', function() {
                bulkEditForm.action = "{{ url_for('item.bulk_duplicate_items', project_id=project.id) }}";
                bulkEditForm.submit();
            });
        }
		
        updateSelectedState();
    }
});