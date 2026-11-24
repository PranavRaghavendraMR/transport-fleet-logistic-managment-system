from django.test import TestCase
from datetime import date, timedelta
from decimal import Decimal
from fleet.models import Vehicle, Driver
from safety.models import SafetyIncident, SafetyInspection


class SafetyManagementTests(TestCase):
    def setUp(self):
        self.today = date.today()
        self.vehicle = Vehicle.objects.create(
            registration_number='KA-01-SF-9999',
            vehicle_type=Vehicle.TYPE_VAN,
            manufacturer='Force Motors',
            model_name='Traveller',
            manufacturing_year=2022,
            capacity_kg=Decimal('3500.0'),
            fuel_type=Vehicle.FUEL_DIESEL,
            current_odometer=Decimal('50000.0'),
            insurance_expiry_date=self.today + timedelta(days=200),
            registration_expiry_date=self.today + timedelta(days=300),
            status=Vehicle.STATUS_AVAILABLE
        )
        self.driver = Driver.objects.create(
            name='Karthik Murthy',
            contact_number='+91 99999 88888',
            license_number='KA0120190099999',
            license_expiry_date=self.today + timedelta(days=250),
            address='Bengaluru',
            employment_status=Driver.STATUS_ACTIVE
        )

    def test_safety_incident_creation(self):
        inc = SafetyIncident.objects.create(
            incident_id='INC-TEST-001',
            vehicle=self.vehicle,
            driver=self.driver,
            incident_date=self.today,
            incident_location='NH-44 KM 32',
            incident_type=SafetyIncident.TYPE_MINOR_SCRAPE,
            description='Side scrape during parking.',
            damage_severity=SafetyIncident.SEVERITY_LOW,
            estimated_damage_cost=Decimal('2500.00'),
            action_taken='Settled with other party.',
            status=SafetyIncident.STATUS_RESOLVED
        )
        self.assertEqual(inc.incident_id, 'INC-TEST-001')
        self.assertEqual(inc.estimated_damage_cost, Decimal('2500.00'))

    def test_safety_inspection_creation(self):
        insp = SafetyInspection.objects.create(
            inspection_id='INSP-TEST-001',
            vehicle=self.vehicle,
            inspection_date=self.today,
            inspector_name='Chief Inspector Raman',
            brake_condition='Pass',
            tyre_condition='Pass',
            lights_condition='Pass',
            documents_verification='Valid',
            overall_inspection_result=SafetyInspection.RESULT_PASSED,
            remarks='Vehicle roadworthy and certified.'
        )
        self.assertEqual(insp.overall_inspection_result, SafetyInspection.RESULT_PASSED)
