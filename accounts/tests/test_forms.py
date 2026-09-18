from django.test import TestCase

from accounts.forms import ClientSignupForm, ProfileUpdateForm
from accounts.models import User


class ClientSignupFormTests(TestCase):
    def test_signup_form_has_no_role_field(self):
        form = ClientSignupForm()
        self.assertNotIn("role", form.fields)

    def test_signup_always_creates_a_client(self):
        form = ClientSignupForm(data={
            "email": "newclient@example.com",
            "first_name": "New",
            "last_name": "Client",
            "password1": "a-strong-password-1",
            "password2": "a-strong-password-1",
        })
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.role, User.Role.CLIENT)


class ProfileUpdateFormTests(TestCase):
    def test_profile_form_excludes_role_and_permission_fields(self):
        form = ProfileUpdateForm()
        for field in ("role", "is_active", "is_staff", "is_superuser", "groups", "user_permissions"):
            self.assertNotIn(field, form.fields)