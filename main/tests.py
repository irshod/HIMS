from django.test import TestCase
from django.urls import reverse
from main.models import CustomUser, Role

class RoleBasedAccessTests(TestCase):
    def setUp(self):
        self.admin_role = Role.objects.create(name='Admin')
        self.admin_user = CustomUser.objects.create_user(email='admin@example.com', password='password')
        self.admin_user.roles.add(self.admin_role)

    def test_admin_access(self):
        self.client.login(email='admin@example.com', password='password')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
