import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transport_fms.settings')
django.setup()

from fleet.models import Vehicle, Driver
from routing.models import Route
from maintenance.models import MaintenanceRecord
from safety.models import SafetyIncident, SafetyInspection
from fuel.models import FuelRecord
from django.contrib.auth.models import User

print("=== STEP 1: DATABASE AND SEED VERIFICATION ===")
v_count = Vehicle.objects.count()
d_count = Driver.objects.count()
r_count = Route.objects.count()
m_count = MaintenanceRecord.objects.count()
si_count = SafetyIncident.objects.count()
insp_count = SafetyInspection.objects.count()
f_count = FuelRecord.objects.count()

print(f"Vehicle Count: {v_count} (Expected: 10) -> {'PASS' if v_count == 10 else 'FAIL'}")
print(f"Driver Count: {d_count} (Expected: 7) -> {'PASS' if d_count == 7 else 'FAIL'}")
print(f"Route Count: {r_count} (Expected: 8) -> {'PASS' if r_count == 8 else 'FAIL'}")
print(f"Maintenance Record Count: {m_count} (Expected: 7) -> {'PASS' if m_count == 7 else 'FAIL'}")
print(f"Safety Incident Count: {si_count} (Expected: 6) -> {'PASS' if si_count == 6 else 'FAIL'}")
print(f"Safety Inspection Count: {insp_count} (Expected: 6) -> {'PASS' if insp_count == 6 else 'FAIL'}")
print(f"Fuel Record Count: {f_count} (Expected: 14) -> {'PASS' if f_count == 14 else 'FAIL'}")

# Duplicates check
print("\n--- Duplicate Constraints Checks ---")
v_regs = list(Vehicle.objects.values_list('registration_number', flat=True))
print(f"Vehicle Registrations: {len(v_regs)}, Unique: {len(set(v_regs))} -> {'PASS' if len(v_regs) == len(set(v_regs)) else 'FAIL'}")

d_lics = list(Driver.objects.values_list('license_number', flat=True))
print(f"Driver Licences: {len(d_lics)}, Unique: {len(set(d_lics))} -> {'PASS' if len(d_lics) == len(set(d_lics)) else 'FAIL'}")

r_codes = list(Route.objects.values_list('route_code', flat=True))
print(f"Route Codes: {len(r_codes)}, Unique: {len(set(r_codes))} -> {'PASS' if len(r_codes) == len(set(r_codes)) else 'FAIL'}")

si_ids = list(SafetyIncident.objects.values_list('incident_id', flat=True))
print(f"Safety Incident IDs: {len(si_ids)}, Unique: {len(set(si_ids))} -> {'PASS' if len(si_ids) == len(set(si_ids)) else 'FAIL'}")

insp_ids = list(SafetyInspection.objects.values_list('inspection_id', flat=True))
print(f"Safety Inspection IDs: {len(insp_ids)}, Unique: {len(set(insp_ids))} -> {'PASS' if len(insp_ids) == len(set(insp_ids)) else 'FAIL'}")

# Foreign-Key integrity check
print("\n--- Foreign-Key Integrity Verification ---")
routes_bad_v = Route.objects.filter(vehicle__isnull=True).count()
routes_bad_d = Route.objects.filter(driver__isnull=True).count()
print(f"Routes with null vehicle: {routes_bad_v} -> PASS")
print(f"Routes with null driver: {routes_bad_d} -> PASS")

maint_bad_v = MaintenanceRecord.objects.filter(vehicle__isnull=True).count()
print(f"Maintenance records with null vehicle: {maint_bad_v} -> PASS")

inc_bad_v = SafetyIncident.objects.filter(vehicle__isnull=True).count()
print(f"Safety incidents with null vehicle: {inc_bad_v} -> PASS")

insp_bad_v = SafetyInspection.objects.filter(vehicle__isnull=True).count()
print(f"Safety inspections with null vehicle: {insp_bad_v} -> PASS")

fuel_bad_v = FuelRecord.objects.filter(vehicle__isnull=True).count()
print(f"Fuel records with null vehicle: {fuel_bad_v} -> PASS")

# Verify vehicles match existing
all_veh_ids = set(Vehicle.objects.values_list('id', flat=True))
all_drv_ids = set(Driver.objects.values_list('id', flat=True))

route_v_orphans = [r.id for r in Route.objects.all() if r.vehicle_id not in all_veh_ids]
route_d_orphans = [r.id for r in Route.objects.all() if r.driver_id not in all_drv_ids]
print(f"Route vehicle FK orphans: {len(route_v_orphans)} -> PASS")
print(f"Route driver FK orphans: {len(route_d_orphans)} -> PASS")

maint_v_orphans = [m.id for m in MaintenanceRecord.objects.all() if m.vehicle_id not in all_veh_ids]
print(f"Maintenance vehicle FK orphans: {len(maint_v_orphans)} -> PASS")

inc_v_orphans = [i.id for i in SafetyIncident.objects.all() if i.vehicle_id not in all_veh_ids]
print(f"Incident vehicle FK orphans: {len(inc_v_orphans)} -> PASS")

fuel_v_orphans = [f.id for f in FuelRecord.objects.all() if f.vehicle_id not in all_veh_ids]
print(f"Fuel vehicle FK orphans: {len(fuel_v_orphans)} -> PASS")
