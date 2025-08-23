<<<<<<< HEAD
/**
 * Main JavaScript file for Project Cost Management System
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initTooltips();
    
    // Initialize popovers
    initPopovers();
    
    // Setup form validations
    setupFormValidations();
    
    // Setup search functionality
    setupSearch();
    
    // Setup dynamic calculations
    setupCalculations();
    
    // Setup status updates
    setupStatusUpdates();
    
    // Setup Google Sheets integration
    setupGoogleSheetsIntegration();
    
    // Setup charts if they exist on the page
    setupCharts();
});

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize Bootstrap popovers
 */
function initPopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Setup form validations
 */
function setupFormValidations() {
    // Get all forms that need validation
    const forms = document.querySelectorAll('.needs-validation');
    
    // Loop over them and prevent submission
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * Setup search functionality
 */
function setupSearch() {
    const searchInputs = document.querySelectorAll('.search-input');
    
    searchInputs.forEach(input => {
        input.addEventListener('keyup', function() {
            const searchValue = this.value.toLowerCase();
            const targetId = this.getAttribute('data-target');
            const targetTable = document.getElementById(targetId);
            
            if (targetTable) {
                const rows = targetTable.querySelectorAll('tbody tr');
                
                rows.forEach(row => {
                    let found = false;
                    const cells = row.querySelectorAll('td');
                    
                    cells.forEach(cell => {
                        if (cell.textContent.toLowerCase().indexOf(searchValue) > -1) {
                            found = true;
                        }
                    });
                    
                    if (found) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
=======
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
>>>>>>> 7a3713e (Initial commit with updated files)
                    }
                });
            }
        });
    });
<<<<<<< HEAD
}

/**
 * Setup dynamic calculations for forms
 */
function setupCalculations() {
    // Contract cost calculations
    setupCostCalculation('contract_quantity', 'contract_unit_cost', 'contract_total_cost');
    
    // Actual cost calculations
    setupCostCalculation('actual_quantity', 'actual_unit_cost', 'actual_total_cost');
    
    // Remaining amount calculations
    setupRemainingCalculation();
}

/**
 * Setup cost calculation between quantity, unit cost and total cost
 */
function setupCostCalculation(quantityId, unitCostId, totalCostId) {
    const quantityInput = document.getElementById(quantityId);
    const unitCostInput = document.getElementById(unitCostId);
    const totalCostInput = document.getElementById(totalCostId);
    
    if (quantityInput && unitCostInput && totalCostInput) {
        const calculateTotal = function() {
            const quantity = parseFloat(quantityInput.value) || 0;
            const unitCost = parseFloat(unitCostInput.value) || 0;
            const total = quantity * unitCost;
            
            totalCostInput.value = total.toFixed(2);
            
            // If this is for actual costs, also update remaining amount
            if (quantityId === 'actual_quantity') {
                setupRemainingCalculation();
            }
        };
        
        quantityInput.addEventListener('input', calculateTotal);
        unitCostInput.addEventListener('input', calculateTotal);
        
        // Initial calculation
        calculateTotal();
    }
}

/**
 * Setup remaining amount calculation
 */
function setupRemainingCalculation() {
    const actualTotalCostInput = document.getElementById('actual_total_cost');
    const contractTotalCostInput = document.getElementById('contract_total_cost');
    const paidAmountInput = document.getElementById('paid_amount');
    const remainingAmountInput = document.getElementById('remaining_amount');
    
    if (paidAmountInput && remainingAmountInput) {
        const calculateRemaining = function() {
            const paidAmount = parseFloat(paidAmountInput.value) || 0;
            let totalCost = 0;
            
            // Use actual cost if available, otherwise use contract cost
            if (actualTotalCostInput && parseFloat(actualTotalCostInput.value) > 0) {
                totalCost = parseFloat(actualTotalCostInput.value);
            } else if (contractTotalCostInput) {
                totalCost = parseFloat(contractTotalCostInput.value) || 0;
            }
            
            const remaining = totalCost - paidAmount;
            remainingAmountInput.value = remaining.toFixed(2);
        };
        
        paidAmountInput.addEventListener('input', calculateRemaining);
        
        // Initial calculation
        calculateRemaining();
    }
}

/**
 * Setup status updates for items
 */
function setupStatusUpdates() {
    const statusSelects = document.querySelectorAll('.item-status-select');
    
    statusSelects.forEach(select => {
        select.addEventListener('change', function() {
            const itemId = this.getAttribute('data-item-id');
            const status = this.value;
            
            if (itemId && status) {
                // Send AJAX request to update status
                fetch(`/items/${itemId}/status`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: `status=${status}`
                })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        showAlert('danger', data.error);
                    } else {
                        showAlert('success', 'تم تحديث حالة البند بنجاح');
                    }
                })
                .catch(error => {
                    console.error('Error updating item status:', error);
                    showAlert('danger', 'حدث خطأ أثناء تحديث حالة البند');
                });
            }
        });
    });
}

/**
 * Setup Google Sheets integration
 */
function setupGoogleSheetsIntegration() {
    // Create new sheet button
    const createSheetBtn = document.getElementById('create-sheet-btn');
    if (createSheetBtn) {
        createSheetBtn.addEventListener('click', function() {
            const projectId = this.getAttribute('data-project-id');
            
            if (projectId) {
                this.disabled = true;
                this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> جاري الإنشاء...';
                
                // Send AJAX request to create sheet
                fetch(`/sheets/project/${projectId}/create`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        showAlert('danger', data.error);
                    } else {
                        showAlert('success', 'تم إنشاء جدول البيانات بنجاح');
                        
                        // Update UI with new spreadsheet info
                        const spreadsheetIdElement = document.getElementById('spreadsheet-id');
                        const spreadsheetLinkElement = document.getElementById('spreadsheet-link');
                        
                        if (spreadsheetIdElement) {
                            spreadsheetIdElement.textContent = data.spreadsheet_id;
                        }
                        
                        if (spreadsheetLinkElement) {
                            spreadsheetLinkElement.href = data.url;
                            spreadsheetLinkElement.style.display = 'inline-block';
                        }
                        
                        // Reload page after short delay
                        setTimeout(() => {
                            window.location.reload();
                        }, 2000);
                    }
                })
                .catch(error => {
                    console.error('Error creating sheet:', error);
                    showAlert('danger', 'حدث خطأ أثناء إنشاء جدول البيانات');
                })
                .finally(() => {
                    this.disabled = false;
                    this.innerHTML = '<i class="fas fa-plus me-1"></i> إنشاء جدول بيانات جديد';
                });
            }
        });
    }
    
    // Sync sheet button
    const syncSheetBtn = document.getElementById('sync-sheet-btn');
    if (syncSheetBtn) {
        syncSheetBtn.addEventListener('click', function() {
            const projectId = this.getAttribute('data-project-id');
            
            if (projectId) {
                this.disabled = true;
                this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> جاري المزامنة...';
                
                // Send AJAX request to sync sheet
                fetch(`/sheets/project/${projectId}/sync`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        showAlert('danger', data.error);
                    } else {
                        showAlert('success', 'تم مزامنة البيانات بنجاح');
                    }
                })
                .catch(error => {
                    console.error('Error syncing sheet:', error);
                    showAlert('danger', 'حدث خطأ أثناء مزامنة البيانات');
                })
                .finally(() => {
                    this.disabled = false;
                    this.innerHTML = '<i class="fas fa-sync me-1"></i> مزامنة البيانات';
                });
            }
        });
    }
    
    // Import from sheet button
    const importSheetBtn = document.getElementById('import-sheet-btn');
    if (importSheetBtn) {
        importSheetBtn.addEventListener('click', function() {
            const projectId = this.getAttribute('data-project-id');
            
            if (projectId) {
                this.disabled = true;
                this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> جاري الاستيراد...';
                
                // Send AJAX request to import from sheet
                fetch(`/sheets/project/${projectId}/import`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        showAlert('danger', data.error);
                    } else {
                        showAlert('success', `تم استيراد ${data.count} بند بنجاح`);
                        
                        // Reload page after short delay
                        setTimeout(() => {
                            window.location.reload();
                        }, 2000);
                    }
                })
                .catch(error => {
                    console.error('Error importing from sheet:', error);
                    showAlert('danger', 'حدث خطأ أثناء استيراد البيانات');
                })
                .finally(() => {
                    this.disabled = false;
                    this.innerHTML = '<i class="fas fa-download me-1"></i> استيراد من الجدول';
                });
            }
        });
    }
}

/**
 * Setup charts on dashboard
 */
function setupCharts() {
    // Cost comparison chart
    setupCostComparisonChart();
    
    // Item status chart
    setupItemStatusChart();
    
    // Contractor cost chart
    setupContractorCostChart();
}

/**
 * Setup cost comparison chart
 */
function setupCostComparisonChart() {
    const costChartCanvas = document.getElementById('costComparisonChart');
    
    if (costChartCanvas && typeof Chart !== 'undefined') {
        // Get project data from data attribute
        const projectData = JSON.parse(costChartCanvas.getAttribute('data-project') || '{}');
        
        if (projectData.total_contract_cost) {
            new Chart(costChartCanvas.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: ['التكلفة التعاقدية', 'التكلفة الفعلية'],
                    datasets: [{
                        label: 'التكاليف',
                        data: [
                            projectData.total_contract_cost,
                            projectData.total_actual_cost || 0
                        ],
                        backgroundColor: [
                            'rgba(54, 162, 235, 0.7)',
                            'rgba(75, 192, 192, 0.7)'
                        ],
                        borderColor: [
                            'rgba(54, 162, 235, 1)',
                            'rgba(75, 192, 192, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: 'مقارنة التكاليف التعاقدية والفعلية'
                        }
                    }
                }
            });
        }
    }
}

/**
 * Setup item status chart
 */
function setupItemStatusChart() {
    const statusChartCanvas = document.getElementById('itemStatusChart');
    
    if (statusChartCanvas && typeof Chart !== 'undefined') {
        // Get items data from data attribute
        const itemsData = JSON.parse(statusChartCanvas.getAttribute('data-items') || '[]');
        
        if (itemsData.length > 0) {
            // Count items by status
            const statusCounts = {
                'نشط': 0,
                'مكتمل': 0,
                'متوقف': 0
            };
            
            itemsData.forEach(item => {
                if (item.status in statusCounts) {
                    statusCounts[item.status]++;
                }
            });
            
            new Chart(statusChartCanvas.getContext('2d'), {
                type: 'pie',
                data: {
                    labels: Object.keys(statusCounts),
                    datasets: [{
                        data: Object.values(statusCounts),
                        backgroundColor: [
                            'rgba(255, 205, 86, 0.7)',
                            'rgba(75, 192, 192, 0.7)',
                            'rgba(255, 99, 132, 0.7)'
                        ],
                        borderColor: [
                            'rgba(255, 205, 86, 1)',
                            'rgba(75, 192, 192, 1)',
                            'rgba(255, 99, 132, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'توزيع البنود حسب الحالة'
                        }
                    }
                }
            });
        }
    }
}

/**
 * Setup contractor cost chart
 */
function setupContractorCostChart() {
    const contractorChartCanvas = document.getElementById('contractorCostChart');
    
    if (contractorChartCanvas && typeof Chart !== 'undefined') {
        // Get items data from data attribute
        const itemsData = JSON.parse(contractorChartCanvas.getAttribute('data-items') || '[]');
        
        if (itemsData.length > 0) {
            // Calculate costs by contractor
            const contractorCosts = {};
            
            itemsData.forEach(item => {
                if (item.contractor_name) {
                    if (!contractorCosts[item.contractor_name]) {
                        contractorCosts[item.contractor_name] = 0;
                    }
                    
                    contractorCosts[item.contractor_name] += item.actual_total_cost || item.contract_total_cost;
                }
            });
            
            const contractorLabels = Object.keys(contractorCosts);
            const contractorValues = Object.values(contractorCosts);
            
            if (contractorLabels.length > 0) {
                new Chart(contractorChartCanvas.getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: contractorLabels,
                        datasets: [{
                            label: 'التكلفة',
                            data: contractorValues,
                            backgroundColor: 'rgba(153, 102, 255, 0.7)',
                            borderColor: 'rgba(153, 102, 255, 1)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        indexAxis: 'y',
                        responsive: true,
                        scales: {
                            x: {
                                beginAtZero: true
                            }
                        },
                        plugins: {
                            title: {
                                display: true,
                                text: 'توزيع التكاليف حسب المقاولين'
                            }
                        }
                    }
                });
            }
        }
    }
}

/**
 * Show alert message
 */
function showAlert(type, message) {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    
    // Add message
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Find alert container
    let alertContainer = document.querySelector('.alert-container');
    
    // If no container exists, create one
    if (!alertContainer) {
        alertContainer = document.createElement('div');
        alertContainer.className = 'alert-container position-fixed top-0 end-0 p-3';
        alertContainer.style.zIndex = '1050';
        document.body.appendChild(alertContainer);
    }
    
    // Add alert to container
    alertContainer.appendChild(alertDiv);
    
    // Initialize Bootstrap alert
    const bsAlert = new bootstrap.Alert(alertDiv);
    
    // Auto close after 5 seconds
    setTimeout(() => {
        bsAlert.close();
    }, 5000);
}

/**
 * Format number as currency
 */
function formatCurrency(value) {
    return parseFloat(value).toLocaleString('ar-SA', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

/**
 * Format percentage
 */
function formatPercentage(value) {
    return parseFloat(value).toLocaleString('ar-SA', {
        minimumFractionDigits: 1,
        maximumFractionDigits: 1
    }) + '%';
}
=======

    // Auto-save functionality for forms with data-auto-save attribute
    const autoSaveForms = document.querySelectorAll("form[data-auto-save]");
    autoSaveForms.forEach(form => {
        let timeoutId;
        form.addEventListener("input", function() {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                // In a real application, you'd send an AJAX request here
                // For now, we'll just log that it's 

>>>>>>> 7a3713e (Initial commit with updated files)
