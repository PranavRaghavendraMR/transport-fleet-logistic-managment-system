from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


class ReportsModuleTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin_reports', password='Password@123', is_superuser=True)
        self.client.login(username='admin_reports', password='Password@123')

    def test_reports_views_render_successfully(self):
        report_urls = [
            'reports:reports_home',
            'reports:vehicle_inventory_report',
            'reports:vehicle_availability_report',
            'reports:driver_report',
            'reports:route_performance_report',
            'reports:maintenance_history_report',
            'reports:maintenance_expense_report',
            'reports:safety_incident_report',
            'reports:fuel_expense_report',
            'reports:vehicle_mileage_report',
        ]
        for name in report_urls:
            res = self.client.get(reverse(name))
            self.assertEqual(res.status_code, 200, f"Report {name} failed to render with code {res.status_code}")
