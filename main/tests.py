from django.test import TestCase
from django.contrib.auth.models import Permission
from .models import Role, CustomUser


class MainModelTest(TestCase):
    def setUp(self):
        # Create a role with permissions
        self.permission = Permission.objects.create(
            codename='test_permission',
            name='Test Permission',
            content_type_id=1  # Assume a valid content type ID
        )
        self.role = Role.objects.create(name="Admin")
        self.role.permissions.add(self.permission)

        # Create a CustomUser
        self.user = CustomUser.objects.create_user(
            email="user@example.com",
            password="securepassword",
            first_name="John",
            last_name="Doe",
        )
        self.user.roles.add(self.role)

    def test_role_creation(self):
        # Verify Role creation
        self.assertEqual(Role.objects.count(), 1)
        self.assertEqual(self.role.name, "Admin")
        self.assertEqual(self.role.permissions.count(), 1)

    def test_custom_user_creation(self):
        # Verify CustomUser creation
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(self.user.email, "user@example.com")
        self.assertTrue(self.user.check_password("securepassword"))
        self.assertEqual(str(self.user), "John Doe (user@example.com)")

    def test_user_roles(self):
        # Verify roles and role methods
        self.assertEqual(self.user.roles.count(), 1)
        self.assertTrue(self.user.has_role("Admin"))
        self.assertFalse(self.user.has_role("NonExistentRole"))

    def test_user_full_name(self):
        # Verify get_full_name method
        self.assertEqual(self.user.get_full_name(), "John Doe")
