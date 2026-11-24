from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date, timedelta
from decimal import Decimal
from fleet.models import Vehicle, Driver
from accounts.models import UserProfile


class FleetVehicleAndDriverTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(username='admin_fleet', password='Password@123', is_superuser=True)
        self.client.login(username='admin_fleet', password='Password@123')
        self.today = date.today()

    def test_vehicle_crud(self):
        # 1. Create Vehicle
        create_url = reverse('fleet:vehicle_create')
        data = {
            'registration_number': 'KA-01-EQ-9999',
            'vehicle_type': Vehicle.TYPE_TRUCK,
            'manufacturer': 'Tata Motors',
            'model_name': 'Prima 4028.S',
            'manufacturing_year': 2023,
            'capacity_kg': '25000.00',
            'fuel_type': Vehicle.FUEL_DIESEL,
            'current_odometer': '15000.0',
            'insurance_expiry_date': (self.today + timedelta(days=200)).strftime('%Y-%m-%d'),
            'registration_expiry_date': (self.today + timedelta(days=400)).strftime('%Y-%m-%d'),
            'status': Vehicle.STATUS_AVAILABLE,
            'notes': 'Heavy freight truck'
        }
        res = self.client.post(create_url, data)
        self.assertEqual(res.status_code, 302)
        self.assertTrue(Vehicle.objects.filter(registration_number='KA-01-EQ-9999').exists())

        # 2. Read Vehicle Details
        v = Vehicle.objects.get(registration_number='KA-01-EQ-9999')
        res = self.client.get(reverse('fleet:vehicle_detail', args=[v.pk]))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'KA-01-EQ-9999')

        # 3. Update Vehicle
        update_url = reverse('fleet:vehicle_update', args=[v.pk])
        data['capacity_kg'] = '26000.00'
        res = self.client.post(update_url, data)
        self.assertEqual(res.status_code, 302)
        v.refresh_from_db()
        self.assertEqual(v.capacity_kg, Decimal('26000.00'))

        # 4. Delete Vehicle
        delete_url = reverse('fleet:vehicle_delete', args=[v.pk])
        res = self.client.post(delete_url)
        self.assertEqual(res.status_code, 302)
        self.assertFalse(Vehicle.objects.filter(registration_number='KA-01-EQ-9999').exists())

    def test_duplicate_registration_prevented(self):
        Vehicle.objects.create(
            registration_number='KA-01-AA-1111',
            vehicle_type=Vehicle.TYPE_VAN,
            manufacturer='Force Motors',
            model_name='Traveller',
            manufacturing_year=2022,
            capacity_kg=Decimal('3000.0'),
            fuel_type=Vehicle.FUEL_DIESEL,
            current_odometer=Decimal('5000.0'),
            insurance_expiry_date=self.today + timedelta(days=100),
            registration_expiry_date=self.today + timedelta(days=300),
            status=Vehicle.STATUS_AVAILABLE
        )
        res = self.client.post(reverse('fleet:vehicle_create'), {
            'registration_number': 'KA-01-AA-1111',
            'vehicle_type': Vehicle.TYPE_VAN,
            'manufacturer': 'Force Motors',
            'model_name': 'Traveller',
            'manufacturing_year': 2022,
            'capacity_kg': '3000.00',
            'fuel_type': Vehicle.FUEL_DIESEL,
            'current_odometer': '6000.0',
            'insurance_expiry_date': (self.today + timedelta(days=100)).strftime('%Y-%m-%d'),
            'registration_expiry_date': (self.today + timedelta(days=300)).strftime('%Y-%m-%d'),
            'status': Vehicle.STATUS_AVAILABLE
        })
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'already exists')

    def test_driver_crud(self):
        res = self.client.post(reverse('fleet:driver_create'), {
            'name': 'Praveen Kumar',
            'contact_number': '+91 98888 77777',
            'license_number': 'KA0120200088888',
            'license_expiry_date': (self.today + timedelta(days=350)).strftime('%Y-%m-%d'),
            'address': 'Koramangala 4th Block, Bengaluru',
            'employment_status': Driver.STATUS_ACTIVE,
            'experience_years': 7,
            'emergency_contact': '+91 98888 77700'
        })
        self.assertEqual(res.status_code, 302)
        self.assertTrue(Driver.objects.filter(license_number='KA0120200088888').exists())
