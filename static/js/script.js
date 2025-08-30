document.addEventListener("DOMContentLoaded", function() {
    
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

    // Auto-calculation functionality for item costs (remains the same)
    const contractQty = document.getElementById('contract_quantity');
    const contractUnitCost = document.getElementById('contract_unit_cost');
    const contractTotal = document.getElementById('contract_total_cost');

    const actualQty = document.getElementById('actual_quantity');
    const actualUnitCost = document.getElementById('actual_unit_cost');
    const actualTotal = document.getElementById('actual_total_cost');

    function calculateTotal(qtyInput, unitCostInput, totalInput) {
        if (!qtyInput || !unitCostInput || !totalInput) return;
        const quantity = parseFloat(qtyInput.value) || 0;
        const unitCostValue = unitCostInput.disabled 
            ? parseFloat(unitCostInput.value) || 0 
            : parseFloat(unitCostInput.value) || 0;
            
        if (unitCostInput.value === '') return;
            
        const total = quantity * unitCostValue;
        totalInput.value = total.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }
    
    if (contractQty && contractUnitCost && contractTotal) {
        contractQty.addEventListener('input', () => calculateTotal(contractQty, contractUnitCost, contractTotal));
        contractUnitCost.addEventListener('input', () => calculateTotal(contractQty, contractUnitCost, contractTotal));
    }

    if (actualQty && actualUnitCost && actualTotal) {
        actualQty.addEventListener('input', () => calculateTotal(actualQty, actualUnitCost, actualTotal));
        actualUnitCost.addEventListener('input', () => calculateTotal(actualQty, actualUnitCost, actualTotal));
    }

    // START: Updated Bulk Edit Functionality
    const selectAllCheckbox = document.getElementById('select-all');
    const itemCheckboxes = document.querySelectorAll('.item-checkbox');
    const bulkEditForm = document.getElementById('bulk-edit-form');
    const selectedCountDisplay = document.getElementById('selected-count-display'); 

    if (selectAllCheckbox && itemCheckboxes.length > 0 && bulkEditForm) {
        
        function updateSelectedCount() {
            const count = document.querySelectorAll('.item-checkbox:checked').length;
            if (selectedCountDisplay) {
                selectedCountDisplay.textContent = count;
            }
            const submitButton = document.querySelector('button[form="bulk-edit-form"]');
            if (submitButton) {
                submitButton.disabled = count === 0;
            }
        }

        selectAllCheckbox.addEventListener('change', function() {
            itemCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            updateSelectedCount();
        });

        itemCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                if (!this.checked) {
                    selectAllCheckbox.checked = false;
                } else if (document.querySelectorAll('.item-checkbox:checked').length === itemCheckboxes.length) {
                    selectAllCheckbox.checked = true;
                }
                updateSelectedCount();
            });
        });
        
        updateSelectedCount();
    }
    // END: Updated Bulk Edit Functionality


    // START: --- Universal Payment Modal Logic ---
    const paymentModal = document.getElementById('addPaymentModal');
    if (paymentModal) {
        const contractorSelect = document.getElementById('payment_contractor_id');
        const projectSelect = document.getElementById('payment_project_id');
        const itemSelect = document.getElementById('payment_item_id');
        const detailSelect = document.getElementById('payment_cost_detail_id');

        // Helper function to populate a select dropdown
        function populateSelect(selectElement, data, placeholder) {
            selectElement.innerHTML = `<option value="" selected disabled>-- ${placeholder} --</option>`;
            data.forEach(item => {
                const option = new Option(item.name, item.id);
                selectElement.add(option);
            });
        }

        // Reset and disable subsequent dropdowns
        function resetSelects(...selects) {
            selects.forEach(select => {
                select.innerHTML = `<option value="" selected disabled>-- اختر --</option>`;
                select.disabled = true;
            });
        }
        
        // 1. When the modal is shown, populate the contractor list
        paymentModal.addEventListener('show.bs.modal', function() {
            // This assumes 'contractors' is available globally if passed from a specific page,
            // otherwise we would need another API to fetch all contractors.
            // Let's create an API for consistency.
            fetch('/api/contractors') // We need to create this API endpoint
                .then(res => res.json())
                .then(data => {
                    populateSelect(contractorSelect, data, 'اختر مقاول');
                });
            resetSelects(projectSelect, itemSelect, detailSelect);
        });

        // 2. When a contractor is selected, fetch their projects
        contractorSelect.addEventListener('change', function() {
            const contractorId = this.value;
            resetSelects(projectSelect, itemSelect, detailSelect);
            if (!contractorId) return;

            fetch(`/api/contractors/${contractorId}/projects`)
                .then(res => res.json())
                .then(data => {
                    populateSelect(projectSelect, data, 'اختر مشروع');
                    projectSelect.disabled = false;
                });
        });

        // 3. When a project is selected, fetch items for that contractor in that project
        projectSelect.addEventListener('change', function() {
            const projectId = this.value;
            const contractorId = contractorSelect.value;
            resetSelects(itemSelect, detailSelect);
            if (!projectId || !contractorId) return;

            fetch(`/api/projects/${projectId}/contractors/${contractorId}/items`)
                .then(res => res.json())
                .then(data => {
                    populateSelect(itemSelect, data, 'اختر بند');
                    itemSelect.disabled = false;
                });
        });

        // 4. When an item is selected, fetch its unpaid cost details
        itemSelect.addEventListener('change', function() {
            const itemId = this.value;
            const contractorId = contractorSelect.value;
            resetSelects(detailSelect);
            if (!itemId || !contractorId) return;

            fetch(`/api/items/${itemId}/contractors/${contractorId}/cost_details`)
                .then(res => res.json())
                .then(data => {
                    populateSelect(detailSelect, data, 'اختر تفصيل التكلفة');
                    detailSelect.disabled = false;
                });
        });
    }
    // END: --- Universal Payment Modal Logic ---

});