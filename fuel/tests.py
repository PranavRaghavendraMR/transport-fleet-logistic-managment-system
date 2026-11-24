from django.test import TestCase
from datetime import date, timedelta
from decimal import Decimal
from fleet.models import Vehicle
from fuel.models import FuelRecord


class FuelManagementAndMileageCalculationTests(TestCase):
    def setUp(self):
        self.today = date.today()
        self.vehicle = Vehicle.objects.create(
            registration_number='KA-01-FL-8888',
            vehicle_type=Vehicle.TYPE_TRUCK,
            manufacturer='Tata Motors',
            model_name='Prima 4440.S',
            manufacturing_year=2022,
            capacity_kg=Decimal('28000.0'),
            fuel_type=Vehicle.FUEL_DIESEL,
            current_odometer=Decimal('50000.0'),
            insurance_expiry_date=self.today + timedelta(days=200),
            registration_expiry_date=self.today + timedelta(days=300),
            status=Vehicle.STATUS_AVAILABLE
        )

    def test_fuel_cost_calculation(self):
        # 100 Litres at ₹ 95.00 = ₹ 9,500.00
        rec = FuelRecord.objects.create(
            vehicle=self.vehicle,
            fuel_type=Vehicle.FUEL_DIESEL,
            fuel_quantity=Decimal('100.00'),
            fuel_price_per_litre=Decimal('95.00'),
            fuel_station='Indian Oil Hub',
            fuel_date=self.today - timedelta(days=10),
            odometer_reading=Decimal('50000.0')
        )
        self.assertEqual(rec.total_fuel_cost, Decimal('9500.00'))

    def test_mileage_calculation_between_consecutive_records(self):
        # First refuel (baseline): Odometer 50,000 km, 100 L
        rec1 = FuelRecord.objects.create(
            vehicle=self.vehicle,
            fuel_type=Vehicle.FUEL_DIESEL,
            fuel_quantity=Decimal('100.00'),
            fuel_price_per_litre=Decimal('95.00'),
            fuel_station='Indian Oil Hub 1',
            fuel_date=self.today - timedelta(days=7),
            odometer_reading=Decimal('50000.0')
        )
        self.assertEqual(rec1.distance_travelled, Decimal('0.00'))
        self.assertEqual(rec1.calculated_mileage, Decimal('0.00'))

        # Second refuel: Odometer 50,500 km (Distance = 500 km), 100 L filled
        # Expected Mileage: 500 km / 100 L = 5.00 km/L
        rec2 = FuelRecord.objects.create(
            vehicle=self.vehicle,
            fuel_type=Vehicle.FUEL_DIESEL,
            fuel_quantity=Decimal('100.00'),
            fuel_price_per_litre=Decimal('95.50'),
            fuel_station='Indian Oil Hub 2',
            fuel_date=self.today,
            odometer_reading=Decimal('50500.0')
        )
        self.assertEqual(rec2.distance_travelled, Decimal('500.00'))
        self.assertEqual(rec2.calculated_mileage, Decimal('5.00'))
        self.assertEqual(rec2.total_fuel_cost, Decimal('9550.00'))
        
        # Vehicle current odometer updated
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.current_odometer, Decimal('50500.0'))
