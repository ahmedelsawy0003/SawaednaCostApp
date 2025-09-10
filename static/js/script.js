document.addEventListener("DOMContentLoaded", function () {

    // --- START: ROBUST Sidebar Toggler ---
    function setupSidebar() {
        const togglers = document.querySelectorAll('.sidebar-toggler');
        togglers.forEach(toggler => {
            toggler.addEventListener('click', function (event) {
                event.preventDefault();
                const submenu = this.nextElementSibling;
                if (submenu && submenu.classList.contains('sidebar-submenu')) {
                    this.classList.toggle('is-active');
                    submenu.style.display = (submenu.style.display === 'block') ? 'none' : 'block';
                }
            });
        });
    }
    setupSidebar();
    // --- END: ROBUST Sidebar Toggler ---

    // Sidebar Toggle Functionality for mobile
    const sidebar = document.querySelector('.sidebar');
    const openSidebarBtn = document.getElementById('open-sidebar-btn');
    const closeSidebarBtn = document.getElementById('close-sidebar-btn');
    if (sidebar && openSidebarBtn && closeSidebarBtn) {
        openSidebarBtn.addEventListener('click', () => sidebar.classList.add('show'));
        closeSidebarBtn.addEventListener('click', () => sidebar.classList.remove('show'));
    }

    // Toast Functionality for Flash Messages
    const toastElList = document.querySelectorAll('.toast');
    [...toastElList].map(toastEl => {
        const toast = new bootstrap.Toast(toastEl, { autohide: true, delay: 5000 });
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
    const bulkEditForm = document.getElementById('bulk-edit-form');
    if (bulkEditForm) {
        const selectAllCheckbox = document.getElementById('select-all');
        const itemCheckboxes = document.querySelectorAll('.item-checkbox');

        const selectedCountDisplay = document.getElementById('selected-count-display');
        const bulkUpdateBtn = document.getElementById('bulk-update-btn');
        const bulkDeleteBtn = document.getElementById('bulk-delete-btn');
        const bulkDuplicateBtn = document.getElementById('bulk-duplicate-btn');

        const bulkDeleteCount = document.getElementById('bulk-delete-count');
        const confirmBulkDeleteBtn = document.getElementById('confirm-bulk-delete-btn');
        const confirmBulkDuplicateBtn = document.getElementById('confirm-bulk-duplicate-btn');

        function updateSelectedState() {
            const count = document.querySelectorAll('.item-checkbox:checked').length;
            if (selectedCountDisplay) selectedCountDisplay.textContent = count;
            if (bulkDeleteCount) bulkDeleteCount.textContent = count;

            const hasSelection = count > 0;
            if (bulkUpdateBtn) bulkUpdateBtn.disabled = !hasSelection;
            if (bulkDeleteBtn) bulkDeleteBtn.disabled = !hasSelection;
            if (bulkDuplicateBtn) bulkDuplicateBtn.disabled = !hasSelection;
        }

        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', function () {
                itemCheckboxes.forEach(checkbox => { checkbox.checked = this.checked; });
                updateSelectedState();
            });

            itemCheckboxes.forEach(checkbox => {
                checkbox.addEventListener('change', function () {
                    if (!this.checked) {
                        selectAllCheckbox.checked = false;
                    } else if (document.querySelectorAll('.item-checkbox:checked').length === itemCheckboxes.length) {
                        selectAllCheckbox.checked = true;
                    }
                    updateSelectedState();
                });
            });

            updateSelectedState();
        }

        if (bulkUpdateBtn) {
            bulkUpdateBtn.addEventListener('click', function (e) {
                e.preventDefault();
                bulkEditForm.action = bulkEditForm.dataset.updateUrl;
                bulkEditForm.submit();
            });
        }

        if (confirmBulkDeleteBtn) {
            confirmBulkDeleteBtn.addEventListener('click', function () {
                bulkEditForm.action = bulkEditForm.dataset.deleteUrl;
                bulkEditForm.submit();
            });
        }

        if (confirmBulkDuplicateBtn) {
            confirmBulkDuplicateBtn.addEventListener('click', function () {
                bulkEditForm.action = bulkEditForm.dataset.duplicateUrl;
                bulkEditForm.submit();
            });
        }
    }

    // START: Show Payment Items Modal
    const paymentItemsModal = document.getElementById('paymentItemsModal');
    if (paymentItemsModal) {
        paymentItemsModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const paymentId = button.getAttribute('data-payment-id');
            const paymentAmount = button.getAttribute('data-payment-amount');
            const paymentDate = button.getAttribute('data-payment-date');
            const paymentDescription = button.getAttribute('data-payment-description');

            const modalAmount = paymentItemsModal.querySelector('#modal-payment-amount');
            const modalDate = paymentItemsModal.querySelector('#modal-payment-date');
            const modalDescription = paymentItemsModal.querySelector('#modal-payment-description');
            const modalItemsList = paymentItemsModal.querySelector('#modal-items-list');

            modalAmount.textContent = parseFloat(paymentAmount).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
            modalDate.textContent = paymentDate;
            modalDescription.textContent = paymentDescription;
            modalItemsList.innerHTML = '<tr><td colspan="2" class="text-center text-muted">جاري التحميل...</td></tr>';

            // جرّب القراءة من الـ data-* أولًا ثم اسحب من API لو مفيش
            const paymentRow = button.closest('tr');
            const distributionsJsonAttr =
                button.getAttribute('data-distributions') ||
                (paymentRow ? paymentRow.getAttribute('data-distributions') : '');
            const distApiUrl = button.getAttribute('data-dist-url');

            const renderRows = (list) => {
                modalItemsList.innerHTML = '';
                if (list && list.length > 0) {
                    list.forEach(dist => {
                        const row = document.createElement('tr');
                        // اسم الحقل في الـ JSON: لو عندك description مباشر استخدمه،
                        // ولو قديم كان nested تحت invoice_item.description بدّل تلقائيًا.
                        const desc = (dist.description) ? dist.description :
                                     (dist.invoice_item && dist.invoice_item.description) ? dist.invoice_item.description : '-';
                        row.innerHTML = `
                            <td>${desc}</td>
                            <td class="text-end fw-bold text-success">${parseFloat(dist.amount).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ريال</td>
                        `;
                        modalItemsList.appendChild(row);
                    });
                } else {
                    modalItemsList.innerHTML = '<tr><td colspan="2" class="text-center">لا توجد بنود مرتبطة بهذه الدفعة.</td></tr>';
                }
            };

            // لو فيه JSON جاهز في الـ attributes استخدمه
            if (distributionsJsonAttr && distributionsJsonAttr.trim() !== '') {
                let parsed = [];
                try { parsed = JSON.parse(distributionsJsonAttr); } catch (e) { parsed = []; }
                renderRows(parsed);
            } else {
                // fallback للـ API
                const url = distApiUrl || `/payments/${paymentId}/distributions.json`;
                fetch(url, { credentials: 'same-origin' })
                    .then(r => r.ok ? r.json() : Promise.reject())
                    .then(data => {
                        // نتوقع { distributions: [...] }
                        renderRows(data.distributions || []);
                    })
                    .catch(() => {
                        renderRows([]);
                    });
            }
        });
    }
    // END: Show Payment Items Modal

});
