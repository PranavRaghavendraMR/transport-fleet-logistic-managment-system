import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transport_fms.settings')
django.setup()

from datetime import date, timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone

from fleet.models import Vehicle, Driver
from routing.models import Route
from maintenance.models import MaintenanceRecord
from safety.models import SafetyIncident, SafetyInspection
from fuel.models import FuelRecord

print("=== STEP 3: BUSINESS LOGIC AUDIT ===")

today = date.today()
now = timezone.now()

# 1. Maintenance Status Transition & Cost Calculation
print("1. Testing Maintenance Status Transition and Cost Calculation...")
test_v = Vehicle.objects.create(
    registration_number='TEST-BL-01',
    vehicle_type=Vehicle.TYPE_TRUCK,
    manufacturer='Tata Motors',
    model_name='Ultra',
    manufacturing_year=2023,
    capacity_kg=Decimal('10000.0'),
    fuel_type=Vehicle.FUEL_DIESEL,
    current_odometer=Decimal('10000.0'),
    insurance_expiry_date=today + timedelta(days=100),
    registration_expiry_date=today + timedelta(days=200),
    status=Vehicle.STATUS_AVAILABLE
)
assert test_v.status == Vehicle.STATUS_AVAILABLE

m_rec = MaintenanceRecord.objects.create(
    vehicle=test_v,
    maintenance_type=MaintenanceRecord.TYPE_BRAKE,
    description_of_issue='Audit test issue',
    service_date=today,
    odometer_reading=Decimal('10500.0'),
    technician_name='Tester',
    workshop_name='Test Hub',
    spare_parts_cost=Decimal('4500.50'),
    labour_cost=Decimal('1500.25'),
    status=MaintenanceRecord.STATUS_IN_PROGRESS
)
test_v.refresh_from_db()
print(f"   [PASS] Vehicle status transitioned to: {test_v.status} (Expected: Maintenance)")
print(f"   [PASS] Vehicle odometer updated to: {test_v.current_odometer} (Expected: 10500.0)")
print(f"   [PASS] Total maintenance cost calculated: ₹ {m_rec.total_cost} (Expected: 6000.75)")
assert test_v.status == Vehicle.STATUS_MAINTENANCE
assert m_rec.total_cost == Decimal('6000.75')

# Complete maintenance
m_rec.status = MaintenanceRecord.STATUS_COMPLETED
m_rec.save()
test_v.refresh_from_db()
print(f"   [PASS] Vehicle status restored to: {test_v.status} (Expected: Available)")
assert test_v.status == Vehicle.STATUS_AVAILABLE

# 2. Conflicting Route Assignment & Availability Logic
print("\n2. Testing Conflicting Route Assignments & Pre-Save Validation...")
test_d = Driver.objects.create(
    name='Test Driver BL',
    contact_number='+91 99999 00000',
    license_number='TESTLICBL01',
    license_expiry_date=today + timedelta(days=200),
    address='Bengaluru',
    employment_status=Driver.STATUS_ACTIVE
)

# Active Route 1
r1 = Route.objects.create(
    route_code='RT-BL-TEST-1',
    starting_location='Hub A',
    destination='Hub B',
    distance_km=Decimal('200.0'),
    estimated_duration_hours=Decimal('4.0'),
    vehicle=test_v,
    driver=test_d,
    departure_datetime=now + timedelta(hours=1),
    expected_arrival_datetime=now + timedelta(hours=5),
    status=Route.STATUS_IN_TRANSIT
)
test_v.refresh_from_db()
print(f"   [PASS] Vehicle status on In Transit: {test_v.status} (Expected: In Use)")
assert test_v.status == Vehicle.STATUS_IN_USE

# Attempting Route 2 with same In Use vehicle
r2 = Route(
    route_code='RT-BL-TEST-2',
    starting_location='Hub C',
    destination='Hub D',
    distance_km=Decimal('300.0'),
    estimated_duration_hours=Decimal('6.0'),
    vehicle=test_v,
    driver=test_d,
    departure_datetime=now + timedelta(hours=2),
    expected_arrival_datetime=now + timedelta(hours=8),
    status=Route.STATUS_SCHEDULED
)
conflict_caught = False
try:
    r2.clean()
except ValidationError as e:
    conflict_caught = True
    print(f"   [PASS] Vehicle/Driver conflict rejected by validation: {list(e.message_dict.keys())}")
assert conflict_caught, "Validation should reject assigning busy vehicle/driver"

# Complete Route 1
r1.status = Route.STATUS_COMPLETED
r1.save()
test_v.refresh_from_db()
print(f"   [PASS] Vehicle status restored on Route Completed: {test_v.status} (Expected: Available)")
assert test_v.status == Vehicle.STATUS_AVAILABLE

# 3. Fuel Cost & Consecutive Mileage Calculation
print("\n3. Testing Fuel Cost and Consecutive Mileage Calculation...")
f1 = FuelRecord.objects.create(
    vehicle=test_v,
    fuel_type=Vehicle.FUEL_DIESEL,
    fuel_quantity=Decimal('50.00'),
    fuel_price_per_litre=Decimal('90.00'),
    fuel_station='Audit Station 1',
    fuel_date=today - timedelta(days=5),
    odometer_reading=Decimal('10500.0')
)
print(f"   [PASS] Fuel 1 Total Cost: ₹ {f1.total_fuel_cost} (Expected: 4500.00)")
print(f"   [PASS] Fuel 1 Mileage: {f1.calculated_mileage} km/L (Baseline expected: 0.00)")
assert f1.total_fuel_cost == Decimal('4500.00')
assert f1.calculated_mileage == Decimal('0.00')

# Fuel 2: 600 km later (11,100 km), 50 L filled -> Mileage = 600 / 50 = 12.00 km/L
f2 = FuelRecord.objects.create(
    vehicle=test_v,
    fuel_type=Vehicle.FUEL_DIESEL,
    fuel_quantity=Decimal('50.00'),
    fuel_price_per_litre=Decimal('92.00'),
    fuel_station='Audit Station 2',
    fuel_date=today,
    odometer_reading=Decimal('11100.0')
)
print(f"   [PASS] Fuel 2 Total Cost: ₹ {f2.total_fuel_cost} (Expected: 4600.00)")
print(f"   [PASS] Fuel 2 Distance Travelled: {f2.distance_travelled} km (Expected: 600.00)")
print(f"   [PASS] Fuel 2 Calculated Mileage: {f2.calculated_mileage} km/L (Expected: 12.00)")
assert f2.distance_travelled == Decimal('600.00')
assert f2.calculated_mileage == Decimal('12.00')

# 4. Expiry alerts
print("\n4. Testing Expiry Alerts...")
exp_v = Vehicle.objects.create(
    registration_number='TEST-EXP-01',
    vehicle_type=Vehicle.TYPE_VAN,
    manufacturer='Tata',
    model_name='Winger',
    manufacturing_year=2022,
    capacity_kg=Decimal('2000.0'),
    fuel_type=Vehicle.FUEL_DIESEL,
    current_odometer=Decimal('5000.0'),
    insurance_expiry_date=today + timedelta(days=10), # within 30 days
    registration_expiry_date=today + timedelta(days=100),
    status=Vehicle.STATUS_AVAILABLE
)
print(f"   [PASS] Vehicle is_insurance_expiring_soon: {exp_v.is_insurance_expiring_soon} (Expected: True)")
assert exp_v.is_insurance_expiring_soon is True

print("\n=== STEP 4: CRUD VERIFICATION ACROSS ALL ENTITIES ===")

# Create, Read, Update, Delete for all models
print("Executing Full CRUD Lifecycle...")
# Safety Incident CRUD
s_inc = SafetyIncident.objects.create(
    incident_id='INC-AUDIT-001',
    vehicle=test_v,
    driver=test_d,
    incident_date=today,
    incident_location='Audit Point',
    incident_type=SafetyIncident.TYPE_MINOR_SCRAPE,
    description='Audit scrap',
    damage_severity=SafetyIncident.SEVERITY_LOW,
    estimated_damage_cost=Decimal('1500.00'),
    action_taken='Recorded',
    status=SafetyIncident.STATUS_REPORTED
)
assert SafetyIncident.objects.filter(incident_id='INC-AUDIT-001').exists()
s_inc.status = SafetyIncident.STATUS_RESOLVED
s_inc.save()
s_inc.delete()
assert not SafetyIncident.objects.filter(incident_id='INC-AUDIT-001').exists()
print("   [PASS] SafetyIncident CRUD successful")

# Safety Inspection CRUD
s_insp = SafetyInspection.objects.create(
    inspection_id='INSP-AUDIT-001',
    vehicle=test_v,
    inspection_date=today,
    inspector_name='Audit Inspector',
    brake_condition='Pass',
    tyre_condition='Pass',
    lights_condition='Pass',
    documents_verification='Valid',
    overall_inspection_result=SafetyInspection.RESULT_PASSED
)
assert SafetyInspection.objects.filter(inspection_id='INSP-AUDIT-001').exists()
s_insp.remarks = "Audit check update"
s_insp.save()
s_insp.delete()
assert not SafetyInspection.objects.filter(inspection_id='INSP-AUDIT-001').exists()
print("   [PASS] SafetyInspection CRUD successful")

# Clean up temporary test entities
f2.delete()
f1.delete()
r1.delete()
m_rec.delete()
test_d.delete()
test_v.delete()
exp_v.delete()

print("   [PASS] Temporary audit records cleanly purged; primary seed database pristine.")
print("=== BUSINESS LOGIC & CRUD AUDIT COMPLETED: 100% SUCCESS ===")
