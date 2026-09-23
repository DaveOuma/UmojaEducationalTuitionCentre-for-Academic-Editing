from django.test import TestCase

from accounts.models import User
from profiles.models import ClientProfile, EditorProfile


class ClientProfileTests(TestCase):
    def test_one_profile_per_user(self):
        user = User.objects.create_user(email="client@example.com", password="a-strong-password-1")
        ClientProfile.objects.create(user=user, institution="Test University")
        with self.assertRaises(Exception):
            ClientProfile.objects.create(user=user, institution="Duplicate")

    def test_str(self):
        user = User.objects.create_user(email="client2@example.com", password="a-strong-password-1")
        profile = ClientProfile.objects.create(user=user)
        self.assertIn(user.email, str(profile))


class EditorProfileTests(TestCase):
    def test_defaults(self):
        user = User.objects.create_user(
            email="editor@example.com", password="a-strong-password-1", role=User.Role.EDITOR
        )
        profile = EditorProfile.objects.create(user=user)
        self.assertTrue(profile.is_active)
        self.assertEqual(profile.availability_status, EditorProfile.Availability.AVAILABLE)

    def test_one_profile_per_user(self):
        user = User.objects.create_user(
            email="editor2@example.com", password="a-strong-password-1", role=User.Role.EDITOR
        )
        EditorProfile.objects.create(user=user)
        with self.assertRaises(Exception):
            EditorProfile.objects.create(user=user)