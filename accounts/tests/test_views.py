from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import User


class SignupFlowTests(TestCase):
    def test_public_signup_creates_client_and_redirects_to_login(self):
        response = self.client.post(reverse("accounts:signup"), {
            "email": "newclient@example.com",
            "first_name": "New",
            "last_name": "Client",
            "password1": "a-strong-password-1",
            "password2": "a-strong-password-1",
        })
        self.assertRedirects(response, reverse("accounts:login"))
        user = User.objects.get(email="newclient@example.com")
        self.assertEqual(user.role, User.Role.CLIENT)


class DashboardRedirectTests(TestCase):
    def test_requires_login(self):
        response = self.client.get(reverse("accounts:dashboard_redirect"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_shows_role_for_logged_in_user(self):
        user = User.objects.create_user(
            email="editor@example.com", password="a-strong-password-1", role=User.Role.EDITOR
        )
        self.client.force_login(user)
        response = self.client.get(reverse("accounts:dashboard_redirect"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Editor")


class AdminRoleFieldPermissionTests(TestCase):
    """
    Confirms the admin safeguard from spec section 20 (users cannot change
    their own role) at the layer where it's enforced: only staff with the
    accounts.change_user_role permission can edit the role field.
    """

    def setUp(self):
        self.target = User.objects.create_user(
            email="target@example.com", password="a-strong-password-1", role=User.Role.CLIENT
        )

    def _staff_client(self, with_role_permission):
        staff = User.objects.create_user(
            email="staffmember@example.com",
            password="a-strong-password-1",
            role=User.Role.ADMIN,
            is_staff=True,
        )
        # change_user is required either way just to reach the admin change
        # form at all; change_user_role is the additional, role-specific
        # permission this test is actually about.
        staff.user_permissions.add(Permission.objects.get(codename="change_user"))
        if with_role_permission:
            staff.user_permissions.add(Permission.objects.get(codename="change_user_role"))
        client = Client()
        client.force_login(staff)
        return client

    def test_role_field_readonly_without_permission(self):
        admin_client = self._staff_client(with_role_permission=False)
        url = reverse("admin:accounts_user_change", args=[self.target.pk])
        response = admin_client.get(url)
        self.assertEqual(response.status_code, 200)
        # A readonly field is rendered without a name="role" input.
        self.assertNotContains(response, 'name="role"')

    def test_role_field_editable_with_permission(self):
        admin_client = self._staff_client(with_role_permission=True)
        url = reverse("admin:accounts_user_change", args=[self.target.pk])
        response = admin_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="role"')