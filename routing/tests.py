from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from fleet.models import Vehicle, Driver
from routing.models import Route


class RoutingAndAssignmentValidationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(username='admin_route', password='Password@123', is_superuser=True)
        self.client.login(username='admin_route', password='Password@123')
        self.today = date.today()
        self.now = timezone.now()

        # Available Vehicle
        self.vehicle_avail = Vehicle.objects.create(
            registration_number='KA-01-RT-1001',
            vehicle_type=Vehicle.TYPE_TRUCK,
            manufacturer='Tata Motors',
            model_name='Prima',
            manufacturing_year=2023,
            capacity_kg=Decimal('20000.0'),
            fuel_type=Vehicle.FUEL_DIESEL,
            current_odometer=Decimal('10000.0'),
            insurance_expiry_date=self.today + timedelta(days=200),
            registration_expiry_date=self.today + timedelta(days=300),
            status=Vehicle.STATUS_AVAILABLE
        )

        # Maintenance Vehicle
        self.vehicle_maint = Vehicle.objects.create(
            registration_number='KA-01-RT-1002',
            vehicle_type=Vehicle.TYPE_TRUCK,
            manufacturer='Ashok Leyland',
            model_name='Boss',
            manufacturing_year=2022,
            capacity_kg=Decimal('14000.0'),
            fuel_type=Vehicle.FUEL_DIESEL,
            current_odometer=Decimal('20000.0'),
            insurance_expiry_date=self.today + timedelta(days=200),
            registration_expiry_date=self.today + timedelta(days=300),
            status=Vehicle.STATUS_MAINTENANCE
        )

        # Active Driver
        self.driver_active = Driver.objects.create(
            name='Anand Rao',
            contact_number='+91 98450 11111',
            license_number='KA0120190011111',
            license_expiry_date=self.today + timedelta(days=300),
            address='Bengaluru',
            employment_status=Driver.STATUS_ACTIVE
        )

        # Suspended Driver
        self.driver_suspended = Driver.objects.create(
            name='Kiran Kumar',
            contact_number='+91 98450 22222',
            license_number='KA0120190022222',
            license_expiry_date=self.today + timedelta(days=300),
            address='Bengaluru',
            employment_status=Driver.STATUS_SUSPENDED
        )

    def test_prevent_assigning_vehicle_under_maintenance(self):
        route = Route(
            route_code='RT-TEST-001',
            starting_location='Bengaluru',
            destination='Chennai',
            distance_km=Decimal('350.0'),
            estimated_duration_hours=Decimal('7.0'),
            vehicle=self.vehicle_maint,
            driver=self.driver_active,
            departure_datetime=self.now + timedelta(hours=2),
            expected_arrival_datetime=self.now + timedelta(hours=9),
            status=Route.STATUS_SCHEDULED
        )
        with self.assertRaises(ValidationError) as ctx:
            route.clean()
        self.assertIn('vehicle', ctx.exception.message_dict)

    def test_prevent_assigning_suspended_driver(self):
        route = Route(
            route_code='RT-TEST-002',
            starting_location='Bengaluru',
            destination='Mysuru',
            distance_km=Decimal('150.0'),
            estimated_duration_hours=Decimal('3.0'),
            vehicle=self.vehicle_avail,
            driver=self.driver_suspended,
            departure_datetime=self.now + timedelta(hours=2),
            expected_arrival_datetime=self.now + timedelta(hours=5),
            status=Route.STATUS_SCHEDULED
        )
        with self.assertRaises(ValidationError) as ctx:
            route.clean()
        self.assertIn('driver', ctx.exception.message_dict)

    def test_vehicle_status_updates_on_route_transit_and_complete(self):
        # 1. Scheduled Route
        route = Route.objects.create(
            route_code='RT-TRANSIT-01',
            starting_location='Bengaluru',
            destination='Hyderabad',
            distance_km=Decimal('570.0'),
            estimated_duration_hours=Decimal('11.0'),
            vehicle=self.vehicle_avail,
            driver=self.driver_active,
            departure_datetime=self.now + timedelta(hours=1),
            expected_arrival_datetime=self.now + timedelta(hours=12),
            status=Route.STATUS_SCHEDULED
        )
        self.vehicle_avail.refresh_from_db()
        self.assertEqual(self.vehicle_avail.status, Vehicle.STATUS_AVAILABLE)

        # 2. Transit starts -> vehicle becomes In Use
        route.status = Route.STATUS_IN_TRANSIT
        route.save()
        self.vehicle_avail.refresh_from_db()
        self.assertEqual(self.vehicle_avail.status, Vehicle.STATUS_IN_USE)

        # 3. Route completes -> vehicle returns to Available
        route.status = Route.STATUS_COMPLETED
        route.save()
        self.vehicle_avail.refresh_from_db()
        self.assertEqual(self.vehicle_avail.status, Vehicle.STATUS_AVAILABLE)
