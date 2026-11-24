// Main JavaScript for Transport Fleet & Logistics Management System (FMS)

document.addEventListener('DOMContentLoaded', function () {
    // Enable Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-dismiss standard alerts after 5 seconds
    var alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 6000);
    });

    // Sidebar Toggle for mobile screens
    var menuToggle = document.getElementById('menu-toggle');
    if (menuToggle) {
        menuToggle.addEventListener('click', function (e) {
            e.preventDefault();
            document.getElementById('wrapper').classList.toggle('toggled');
        });
    }

    // Dynamic cost calculator helper in maintenance form
    var spareCostInput = document.getElementById('id_spare_parts_cost');
    var labourCostInput = document.getElementById('id_labour_cost');
    var totalCostDisplay = document.getElementById('calculated_total_cost');

    function updateTotalCost() {
        if (spareCostInput && labourCostInput && totalCostDisplay) {
            var spare = parseFloat(spareCostInput.value) || 0;
            var labour = parseFloat(labourCostInput.value) || 0;
            var total = spare + labour;
            totalCostDisplay.textContent = '₹ ' + total.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        }
    }

    if (spareCostInput && labourCostInput) {
        spareCostInput.addEventListener('input', updateTotalCost);
        labourCostInput.addEventListener('input', updateTotalCost);
        updateTotalCost();
    }

    // Dynamic fuel total calculator helper in fuel form
    var fuelQtyInput = document.getElementById('id_fuel_qty');
    var fuelPriceInput = document.getElementById('id_fuel_price');
    var fuelTotalDisplay = document.getElementById('calculated_fuel_total');

    function updateFuelTotal() {
        if (fuelQtyInput && fuelPriceInput && fuelTotalDisplay) {
            var qty = parseFloat(fuelQtyInput.value) || 0;
            var price = parseFloat(fuelPriceInput.value) || 0;
            var total = qty * price;
            fuelTotalDisplay.textContent = '₹ ' + total.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        }
    }

    if (fuelQtyInput && fuelPriceInput) {
        fuelQtyInput.addEventListener('input', updateFuelTotal);
        fuelPriceInput.addEventListener('input', updateFuelTotal);
        updateFuelTotal();
    }
});
