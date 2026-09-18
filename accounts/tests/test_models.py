from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.models import User


class UserManagerTests(TestCase):
    def test_create_user_defaults_to_client_role(self):
        user = User.objects.create_user(email="client@example.com", password="a-strong-password-1")
        self.assertEqual(user.role, User.Role.CLIENT)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_normalizes_email(self):
        user = User.objects.create_user(email="Client@Example.com", password="a-strong-password-1")
        self.assertEqual(user.email, "Client@example.com")

    def test_create_user_requires_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="a-strong-password-1")

    def test_create_superuser_sets_super_admin_role_and_flags(self):
        user = User.objects.create_superuser(email="root@example.com", password="a-strong-password-1")
        self.assertEqual(user.role, User.Role.SUPER_ADMIN)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_superuser_rejects_is_staff_false(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="root2@example.com", password="a-strong-password-1", is_staff=False
            )

    def test_editor_can_be_created_with_explicit_role(self):
        user = User.objects.create_user(
            email="editor@example.com", password="a-strong-password-1", role=User.Role.EDITOR
        )
        self.assertTrue(user.is_editor)
        self.assertFalse(user.is_client)
        self.assertFalse(user.is_senior_editor)

    def test_role_helpers(self):
        senior = User.objects.create_user(
            email="senior@example.com", password="a-strong-password-1", role=User.Role.SENIOR_EDITOR
        )
        self.assertTrue(senior.is_editor)
        self.assertTrue(senior.is_senior_editor)

        admin = User.objects.create_user(
            email="admin@example.com", password="a-strong-password-1", role=User.Role.ADMIN
        )
        self.assertTrue(admin.is_admin_role)
        self.assertFalse(admin.is_client)

    def test_str_and_full_name(self):
        user = User.objects.create_user(
            email="jane@example.com", password="a-strong-password-1",
            first_name="Jane", last_name="Doe",
        )
        self.assertEqual(str(user), "jane@example.com")
        self.assertEqual(user.get_full_name(), "Jane Doe")

    def test_full_name_falls_back_to_email(self):
        user = User.objects.create_user(email="noname@example.com", password="a-strong-password-1")
        self.assertEqual(user.get_full_name(), "noname@example.com")

    def test_duplicate_email_rejected(self):
        User.objects.create_user(email="dupe@example.com", password="a-strong-password-1")
        with self.assertRaises(ValidationError):
            User.objects.create_user(email="dupe@example.com", password="another-strong-pw-1")