document.addEventListener("DOMContentLoaded", function() {
    
    // --- START: Sidebar Toggle Functionality ---
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
    // --- END: Sidebar Toggle Functionality ---
    
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

    // Auto-calculation functionality (remains the same)
    // ...

    // --- START: تعديل وتطوير قسم الإجراءات الجماعية ---
    const selectAllCheckbox = document.getElementById('select-all');
    const itemCheckboxes = document.querySelectorAll('.item-checkbox');
    const bulkEditForm = document.getElementById('bulk-edit-form');
    
    // الأزرار
    const selectedCountDisplay = document.getElementById('selected-count-display'); 
    const bulkUpdateBtn = document.getElementById('bulk-update-btn');
    const bulkDeleteBtn = document.getElementById('bulk-delete-btn');

    // عناصر نافذة تأكيد الحذف
    const bulkDeleteCount = document.getElementById('bulk-delete-count');
    const confirmBulkDeleteBtn = document.getElementById('confirm-bulk-delete-btn');

    if (selectAllCheckbox && itemCheckboxes.length > 0 && bulkEditForm) {
        
        function updateSelectedState() {
            const count = document.querySelectorAll('.item-checkbox:checked').length;
            
            // تحديث عدد العناصر المحددة
            if (selectedCountDisplay) {
                selectedCountDisplay.textContent = count;
            }
            if (bulkDeleteCount) {
                bulkDeleteCount.textContent = count;
            }

            // تفعيل أو تعطيل الأزرار
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
        
        // عند الضغط على زر تأكيد الحذف الجماعي
        if (confirmBulkDeleteBtn) {
            confirmBulkDeleteBtn.addEventListener('click', function() {
                // 1. تغيير مسار الإرسال للنموذج
                bulkEditForm.action = bulkEditForm.action.replace('bulk_update', 'bulk_delete');
                // 2. إرسال النموذج
                bulkEditForm.submit();
            });
        }

        // استدعاء الدالة عند تحميل الصفحة لضبط الحالة الأولية للأزرار
        updateSelectedState();
    }
    // --- END: تعديل وتطوير قسم الإجراءات الجماعية ---
});

