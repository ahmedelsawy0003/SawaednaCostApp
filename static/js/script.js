document.addEventListener("DOMContentLoaded", function() {
    
    // START: New Toast Functionality for Flash Messages
    const toastElList = document.querySelectorAll('.toast');
    const toastList = [...toastElList].map(toastEl => {
        const toast = new bootstrap.Toast(toastEl, {
            autohide: true,
            delay: 5000 // The toast will disappear after 5 seconds
        });
        toast.show();
        return toast;
    });
    // END: New Toast Functionality

    // Generic search/filter for tables
    const searchInputs = document.querySelectorAll("input[type=\"search\"]");
    searchInputs.forEach(input => {
        input.addEventListener("keyup", function() {
            const searchTerm = this.value.toLowerCase();
            const table = this.closest(".card-body").querySelector("table");
            if (table) {
                const rows = table.querySelectorAll("tbody tr");
                rows.forEach(row => {
                    const textContent = row.textContent.toLowerCase();
                    if (textContent.includes(searchTerm)) {
                        row.style.display = "";
                    } else {
                        row.style.display = "none";
                    }
                });
            }
        });
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

    // Auto-calculation functionality for item costs
    const contractQty = document.getElementById('contract_quantity');
    const contractUnitCost = document.getElementById('contract_unit_cost');
    const contractTotal = document.getElementById('contract_total_cost');

    const actualQty = document.getElementById('actual_quantity');
    const actualUnitCost = document.getElementById('actual_unit_cost');
    const actualTotal = document.getElementById('actual_total_cost');

    function calculateTotal(qtyInput, unitCostInput, totalInput) {
        const quantity = parseFloat(qtyInput.value) || 0;
        const unitCostValue = unitCostInput.disabled 
            ? parseFloat(unitCostInput.value) || 0 
            : parseFloat(unitCostInput.value) || 0;
            
        if (unitCostInput.value === '') return;
            
        const total = quantity * unitCostValue;
        totalInput.value = total.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }
    
    if (contractQty && contractUnitCost && contractTotal) {
        const contractUnitCostDisabled = document.getElementById('contract_unit_cost_disabled');

        contractQty.addEventListener('input', () => calculateTotal(contractQty, contractUnitCost || contractUnitCostDisabled, contractTotal));
        if (contractUnitCost) {
           contractUnitCost.addEventListener('input', () => calculateTotal(contractQty, contractUnitCost, contractTotal));
        }
    }

    if (actualQty && actualUnitCost && actualTotal) {
        actualQty.addEventListener('input', () => calculateTotal(actualQty, actualUnitCost, actualTotal));
        actualUnitCost.addEventListener('input', () => calculateTotal(actualQty, actualUnitCost, actualTotal));
    }

});