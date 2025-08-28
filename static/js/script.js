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
    // New selector for the count display in the accordion button
    const selectedCountDisplay = document.getElementById('selected-count-display'); 

    if (selectAllCheckbox && itemCheckboxes.length > 0 && bulkEditForm) {
        
        function updateSelectedCount() {
            const count = document.querySelectorAll('.item-checkbox:checked').length;
            // Update the new span inside the accordion button
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
        
        // Initial count update on page load
        updateSelectedCount();
    }
    // END: Updated Bulk Edit Functionality
});