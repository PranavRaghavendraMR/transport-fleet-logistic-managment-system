import requests
import re

BASE_URL = "http://127.0.0.1:8000"
session = requests.Session()

print("=== STEP 5: LIVE HTTP BROWSER & DOM AUDIT ===")

# 1. Fetch Login Page
r_login = session.get(f"{BASE_URL}/login/")
print(f"1. Login Page ({BASE_URL}/login/): HTTP {r_login.status_code}")
assert r_login.status_code == 200
assert "Sign In to Fleet Portal" in r_login.text
assert "Chanakya University" in r_login.text
assert "Pranavraghavendra M R" in r_login.text
assert "csrfmiddlewaretoken" in r_login.text
assert "Admin@123" in r_login.text
print("   [PASS] Login page structure, branding, demo credentials, and CSRF token verified.")

# Extract CSRF token
csrf_token = session.cookies.get('csrftoken')
if not csrf_token:
    m = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', r_login.text)
    if m:
        csrf_token = m.group(1)

# 2. Perform Login via HTTP POST
login_data = {
    'username': 'admin',
    'password': 'Admin@123',
    'csrfmiddlewaretoken': csrf_token
}
r_auth = session.post(f"{BASE_URL}/login/", data=login_data, headers={'Referer': f"{BASE_URL}/login/"})
print(f"2. Authenticate as 'admin': HTTP {r_auth.status_code} (Redirected to Dashboard: {'PASS' if r_auth.status_code in [200, 302] else 'FAIL'})")

# 3. Inspect Executive Dashboard
r_dash = session.get(f"{BASE_URL}/")
print(f"3. Executive Dashboard ({BASE_URL}/): HTTP {r_dash.status_code}")
assert r_dash.status_code == 200
# Check 10 KPI Cards
kpi_markers = [
    "Total Fleet", "Available", "In Use", "Maintenance", "Active Drivers", 
    "Active Routes", "Pending Maintenance", "Total Fuel Expenses", 
    "Maintenance Costs", "Open Safety Incidents"
]
for marker in kpi_markers:
    assert marker in r_dash.text, f"Missing KPI marker: {marker}"
print(f"   [PASS] All 10 KPI cards verified on Executive Dashboard.")

# Check Charts
assert 'id="statusChart"' in r_dash.text
assert 'id="expensesChart"' in r_dash.text
print("   [PASS] Chart.js canvas elements 'statusChart' and 'expensesChart' loaded.")

# Check Recent Routes & Compliance Table
assert "Recent Transportation Activities" in r_dash.text
assert "Upcoming Workshop Reminders" in r_dash.text
assert "Compliance" in r_dash.text
print("   [PASS] Operational tables and compliance watchlist verified.")

# 4. Inspect Pages across all modules
pages_to_audit = [
    ("/fleet/vehicles/", "Vehicle Management", ["Registration No.", "Make & Model", "Capacity (kg)", "Status"]),
    ("/fleet/drivers/", "Driver Management", ["Driver Name", "Licence Number", "Licence Expiry", "Status"]),
    ("/routing/", "Route Dispatch", ["Route Code", "Origin & Destination", "Assigned Vehicle", "Status"]),
    ("/maintenance/dashboard/", "Workshop Maintenance Dashboard", ["Total Records", "In Progress", "Completed Work", "Maintenance Costs"]),
    ("/maintenance/", "Service Work Orders", ["Maintenance Type", "Service Date", "Workshop", "Total Cost"]),
    ("/safety/dashboard/", "Safety & Compliance Dashboard", ["Total Incidents", "Open Incidents", "Vehicles Requiring Safety Inspection"]),
    ("/safety/incidents/", "Safety Incidents Directory", ["Incident ID", "Vehicle & Driver", "Severity", "Estimated Damage Cost"]),
    ("/safety/inspections/", "Vehicle Inspections", ["Inspection ID", "Brakes", "Tyres", "Lights", "Documents", "Overall Result"]),
    ("/fuel/dashboard/", "Fuel Analytics", ["Total Fuel Expenses", "Total Fuel Consumed", "Fleet Average Mileage"]),
    ("/fuel/", "Fuel Purchase Logs", ["Quantity (L)", "Price/L", "Total Cost", "Odometer", "Mileage"]),
    ("/reports/", "Reports & Analytics Center", ["Vehicle Inventory Report", "Vehicle Availability Report", "Maintenance Expense Report", "Vehicle Mileage"]),
    ("/reports/vehicles/inventory/", "Vehicle Inventory Report", ["Vehicle Inventory Report", "Payload (kg)", "Print / Export PDF"]),
    ("/reports/vehicles/availability/", "Vehicle Availability Report", ["Available & Ready", "In Transit / Deployed", "Under Maintenance"]),
    ("/reports/drivers/", "Driver Information Report", ["Driver Name", "Licence Number", "Experience"]),
    ("/reports/routes/performance/", "Route Performance Report", ["Cumulative Distance Travelled", "Trip"]),
    ("/reports/maintenance/history/", "Maintenance History Report", ["Spare Parts Expenditure", "Technician Labour Costs", "Total Maintenance Cost"]),
    ("/reports/maintenance/expenses/", "Maintenance Expense Report", ["Total Fleet Maintenance Expenditure", "Service Visits"]),
    ("/reports/safety/incidents/", "Safety Incident Report", ["Total Estimated Damage Cost", "Severity"]),
    ("/reports/fuel/expenses/", "Fuel Expense Report", ["Total Volume Consumed", "Total Fuel Expenditure"]),
    ("/reports/fuel/mileage/", "Vehicle Mileage Report", ["Vehicle Mileage & Fuel Efficiency Report", "Average Mileage (km/L)", "Best Mileage"]),
    ("/users/", "User Access Control", ["User Access & Role Management", "Administrator", "Fleet Manager", "Maintenance Staff"]),
]

print("\n4. Auditing All Module Pages and Reports:")
for path, title, required_snippets in pages_to_audit:
    r = session.get(f"{BASE_URL}{path}")
    assert r.status_code == 200, f"Page {path} failed with code {r.status_code}"
    for snip in required_snippets:
        assert snip in r.text, f"Page {path} missing snippet: '{snip}'"
    print(f"   [PASS HTTP 200] {title:38} ({path:32}) -> Verified DOM elements.")

print("\n=== ALL LIVE HTTP AND DOM INSPECTION CHECKS PASSED (100%) ===")
