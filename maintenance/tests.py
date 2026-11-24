from django.test import TestCase
from datetime import date, timedelta
from decimal import Decimal
from fleet.models import Vehicle
from maintenance.models import MaintenanceRecord


class WorkshopMaintenanceTests(TestCase):
    def setUp(self):
        self.today = date.today()
        self.vehicle = Vehicle.objects.create(
            registration_number='KA-01-MN-5555',
            vehicle_type=Vehicle.TYPE_TRUCK,
            manufacturer='Tata Motors',
            model_name='Prima 4440',
            manufacturing_year=2022,
            capacity_kg=Decimal('28000.0'),
            fuel_type=Vehicle.FUEL_DIESEL,
            current_odometer=Decimal('40000.0'),
            insurance_expiry_date=self.today + timedelta(days=200),
            registration_expiry_date=self.today + timedelta(days=300),
            status=Vehicle.STATUS_AVAILABLE
        )

    def test_maintenance_cost_calculation(self):
        rec = MaintenanceRecord.objects.create(
            vehicle=self.vehicle,
            maintenance_type=MaintenanceRecord.TYPE_BRAKE,
            description_of_issue='Brake shoe replacement',
            service_date=self.today,
            odometer_reading=Decimal('42000.0'),
            technician_name='Devendra Rao',
            workshop_name='Peenya Central Workshop',
            spare_parts_cost=Decimal('8500.00'),
            labour_cost=Decimal('2500.00'),
            status=MaintenanceRecord.STATUS_IN_PROGRESS
        )
        # Total cost must be spare + labour = 11,000
        self.assertEqual(rec.total_cost, Decimal('11000.00'))

    def test_vehicle_status_transitions_on_maintenance(self):
        # Initial: Vehicle is Available
        self.assertEqual(self.vehicle.status, Vehicle.STATUS_AVAILABLE)

        # 1. Starting maintenance updates vehicle to Maintenance
        rec = MaintenanceRecord.objects.create(
            vehicle=self.vehicle,
            maintenance_type=MaintenanceRecord.TYPE_ENGINE,
            description_of_issue='Oil pump repair',
            service_date=self.today,
            odometer_reading=Decimal('43000.0'),
            technician_name='Ravi S',
            workshop_name='Central Workshop',
            spare_parts_cost=Decimal('5000.00'),
            labour_cost=Decimal('1500.00'),
            status=MaintenanceRecord.STATUS_IN_PROGRESS
        )
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.status, Vehicle.STATUS_MAINTENANCE)
        self.assertEqual(self.vehicle.current_odometer, Decimal('43000.0'))

        # 2. Completing maintenance returns vehicle to Available
        rec.status = MaintenanceRecord.STATUS_COMPLETED
        rec.save()
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.status, Vehicle.STATUS_AVAILABLE)
