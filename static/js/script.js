document.addEventListener("DOMContentLoaded", function() {
    // Auto-dismiss flash messages after 5 seconds
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach(alert => {
        setTimeout(() => {
            new bootstrap.Alert(alert).close();
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

    // Auto-save functionality for forms with data-auto-save attribute
    const autoSaveForms = document.querySelectorAll("form[data-auto-save]");
    autoSaveForms.forEach(form => {
        let timeoutId;
        form.addEventListener("input", function() {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                // In a real application, you'd send an AJAX request here
                // For now, we'll just log that it's 

// Password toggle visibility
    const togglePassword = document.querySelector("#togglePassword");
    if (togglePassword) {
        togglePassword.addEventListener("click", function () {
            const password = document.querySelector("#password");
            // Toggle the type
            const type = password.getAttribute("type") === "password" ? "text" : "password";
            password.setAttribute("type", type);
            // Toggle the icon
            this.classList.toggle("fa-eye");
            this.classList.toggle("fa-eye-slash");
        });
    }
	