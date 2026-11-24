from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import UserProfile
from fleet.models import Vehicle


class AccountsAndRBACSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create users with different roles
        self.admin_user = User.objects.create_user(username='admintest', password='Password@123', is_superuser=True)
        self.manager_user = User.objects.create_user(username='managertest', password='Password@123')
        self.manager_user.profile.role = UserProfile.ROLE_FLEET_MANAGER
        self.manager_user.profile.save()

        self.mechanic_user = User.objects.create_user(username='mechanictest', password='Password@123')
        self.mechanic_user.profile.role = UserProfile.ROLE_MAINTENANCE_STAFF
        self.mechanic_user.profile.save()

        self.staff_user = User.objects.create_user(username='stafftest', password='Password@123')
        self.staff_user.profile.role = UserProfile.ROLE_GENERAL_STAFF
        self.staff_user.profile.save()

    def test_login_flow(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'admintest',
            'password': 'Password@123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_invalid_login(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'admintest',
            'password': 'WrongPassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_anonymous_access_redirects_to_login(self):
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)

    def test_general_staff_cannot_access_user_management(self):
        self.client.login(username='stafftest', password='Password@123')
        response = self.client.get(reverse('accounts:users_list'))
        # Should be redirected with Access Denied message
        self.assertEqual(response.status_code, 302)

    def test_admin_can_access_user_management(self):
        self.client.login(username='admintest', password='Password@123')
        response = self.client.get(reverse('accounts:users_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'User Access & Role Management')
