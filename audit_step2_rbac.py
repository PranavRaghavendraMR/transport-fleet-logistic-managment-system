import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transport_fms.settings')
django.setup()

from django.test import Client
from fleet.models import Vehicle, Driver
from routing.models import Route
from maintenance.models import MaintenanceRecord
from safety.models import SafetyIncident
from fuel.models import FuelRecord

client = Client()

# Pick a vehicle and driver NOT on an active route for the confirmation page test
free_veh = Vehicle.objects.exclude(routes__status__in=['Scheduled', 'In Transit']).first()
free_drv = Driver.objects.exclude(routes__status__in=['Scheduled', 'In Transit']).first()
busy_veh = Vehicle.objects.filter(routes__status__in=['Scheduled', 'In Transit']).first()

rt = Route.objects.exclude(status='In Transit').first()
maint = MaintenanceRecord.objects.first()
inc = SafetyIncident.objects.first()
fuel = FuelRecord.objects.first()

print("=== STEP 2: ROLE-BASED ACCESS CONTROL AUDIT ===")

roles_to_test = [
    ('admin', 'Admin@123', 'Administrator'),
    ('manager', 'Manager@123', 'Fleet Manager'),
    ('mechanic', 'Mechanic@123', 'Maintenance Staff'),
    ('staff', 'Staff@123', 'General Staff'),
]

test_endpoints = [
    ('/users/', ['admin'], 'User Management / Access Control'),
    ('/fleet/vehicles/create/', ['admin', 'manager'], 'Register New Vehicle'),
    (f'/fleet/vehicles/{free_veh.id}/edit/', ['admin', 'manager'], 'Edit Vehicle Specs'),
    (f'/fleet/vehicles/{free_veh.id}/delete/', ['admin'], 'Delete Inactive Vehicle'),
    ('/fleet/drivers/create/', ['admin', 'manager'], 'Enroll New Driver'),
    (f'/fleet/drivers/{free_drv.id}/delete/', ['admin'], 'Delete Inactive Driver'),
    ('/routing/create/', ['admin', 'manager'], 'Schedule Transportation Route'),
    (f'/routing/{rt.id}/delete/', ['admin'], 'Delete Inactive Route'),
    ('/maintenance/create/', ['admin', 'mechanic'], 'Log Maintenance Work Order'),
    (f'/maintenance/{maint.id}/delete/', ['admin'], 'Delete Maintenance Record'),
    ('/fuel/create/', ['admin', 'manager', 'mechanic', 'staff'], 'Log Fuel Purchase'),
    (f'/fuel/{fuel.id}/delete/', ['admin'], 'Delete Fuel Record'),
    ('/safety/incidents/create/', ['admin', 'manager', 'mechanic', 'staff'], 'Report Safety Incident'),
    (f'/safety/incidents/{inc.id}/delete/', ['admin'], 'Delete Safety Incident'),
]

audit_results = []

for username, password, role_name in roles_to_test:
    client.logout()
    login_ok = client.login(username=username, password=password)
    assert login_ok, f"Failed to login as {username}"
    print(f"\n--- Testing Role: {username} ({role_name}) ---")
    
    for url, allowed_roles, desc in test_endpoints:
        res = client.get(url)
        is_allowed = (username in allowed_roles)
        expected_status = 200 if is_allowed else 302
        passed = (res.status_code == expected_status)
        
        status_text = f"HTTP {res.status_code} ({'PERMITTED' if res.status_code == 200 else 'REDIRECTED/BLOCKED'})"
        print(f"  [{'PASS' if passed else 'FAIL'}] {desc:38} | Direct URL: {url:30} | Result: {status_text} | Expected: {expected_status}")
        audit_results.append((username, desc, url, res.status_code, expected_status, passed))

# Also verify business safeguard: Admin attempting to delete a vehicle assigned to active route is blocked
client.logout()
client.login(username='admin', password='Admin@123')
res_busy = client.get(f'/fleet/vehicles/{busy_veh.id}/delete/')
print(f"\n[Safeguard Test] Admin deleting active vehicle {busy_veh.registration_number}: HTTP {res_busy.status_code} (Redirected back safely: {'PASS' if res_busy.status_code == 302 else 'FAIL'})")
client.logout()

all_passed = all(r[5] for r in audit_results)
print(f"\nRBAC Audit Overall Result: {'ALL 56 CHECKS PASSED (100% SUCCESS)' if all_passed else 'SOME CHECKS FAILED'}")
