// Main JavaScript for Transport Fleet & Logistics Management System (FMS)
// Chanakya University - School of Engineering - BCA V Sem (DAT501)
// Student: Pranavraghavendra M R (Reg No: 24UG00220)

document.addEventListener('DOMContentLoaded', function () {
    // 1. Theme Management (Light / Dark Mode)
    var themeToggleBtn = document.getElementById('themeToggleBtn');
    var themeIcon = document.getElementById('themeIcon');

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-bs-theme', theme);
        localStorage.setItem('fms_theme', theme);
        if (themeIcon) {
            if (theme === 'dark') {
                themeIcon.classList.remove('bi-moon-stars');
                themeIcon.classList.add('bi-sun-fill');
            } else {
                themeIcon.classList.remove('bi-sun-fill');
                themeIcon.classList.add('bi-moon-stars');
            }
        }
    }

    var currentTheme = localStorage.getItem('fms_theme') || 'light';
    applyTheme(currentTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', function () {
            var newTheme = document.documentElement.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark';
            applyTheme(newTheme);
            // Notify charts if any need redraw
            window.dispatchEvent(new Event('themeChanged'));
        });
    }

    // 2. Enable Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 3. Auto-dismiss alerts
    var alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            try {
                var bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } catch (e) {}
        }, 6000);
    });

    // 4. Sidebar Toggle for Mobile & Tablet Screens
    var menuToggle = document.getElementById('menu-toggle');
    var sidebarCloseBtn = document.getElementById('sidebar-close-btn');
    var wrapper = document.getElementById('wrapper');

    if (menuToggle && wrapper) {
        menuToggle.addEventListener('click', function (e) {
            e.preventDefault();
            wrapper.classList.toggle('toggled');
        });
    }

    if (sidebarCloseBtn && wrapper) {
        sidebarCloseBtn.addEventListener('click', function (e) {
            e.preventDefault();
            wrapper.classList.remove('toggled');
        });
    }

    // 5. Dynamic cost calculator helper in maintenance form
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

    // 6. Dynamic fuel total calculator helper in fuel form
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
