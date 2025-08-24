document.addEventListener("DOMContentLoaded", function() {
    
    // Auto-dismiss flash messages after 5 seconds
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach(alert => {
        setTimeout(() => {
            // Check if the alert still exists before trying to close it
            if (alert.parentElement) {
                new bootstrap.Alert(alert).close();
            }
        }, 5000);
    });

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

    // START: New Password Toggle Functionality
    const togglePassword = document.querySelector("#togglePassword");
    const passwordInput = document.querySelector("#password");

    if (togglePassword && passwordInput) {
        togglePassword.addEventListener("click", function () {
            // Toggle the type attribute
            const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
            passwordInput.setAttribute("type", type);
            
            // Toggle the icon
            this.classList.toggle("fa-eye");
            this.classList.toggle("fa-eye-slash");
        });
    }
    // END: New Password Toggle Functionality

});