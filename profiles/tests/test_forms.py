from django.test import TestCase

from profiles.forms import ClientProfileForm, EditorProfileForm


class ClientProfileFormTests(TestCase):
    def test_no_user_field(self):
        form = ClientProfileForm()
        self.assertNotIn("user", form.fields)


class EditorProfileFormTests(TestCase):
    def test_no_user_or_is_active_field(self):
        form = EditorProfileForm()
        self.assertNotIn("user", form.fields)
        self.assertNotIn("is_active", form.fields)

    def test_availability_status_is_editable(self):
        # Editors DO manage their own availability (spec section 25),
        # unlike is_active which is an admin-only matching toggle.
        form = EditorProfileForm()
        self.assertIn("availability_status", form.fields)