from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import User
from organizations.models import Organization, OrganizationMembership


class MembershipRolePermissionTests(TestCase):
    """
    Mirrors accounts' change_user_role test: OrganizationMembership.role
    is gated behind organizations.change_membership_role, not general
    change access, per the Phase 2 authorization principle.
    """

    def setUp(self):
        self.org = Organization.objects.create(
            name="Test University", org_type=Organization.OrgType.UNIVERSITY
        )
        self.member = User.objects.create_user(
            email="member@example.com", password="a-strong-password-1"
        )
        self.membership = OrganizationMembership.objects.create(
            organization=self.org, user=self.member
        )

    def _staff_client(self, with_role_permission):
        staff = User.objects.create_user(
            email="staffmember@example.com",
            password="a-strong-password-1",
            role=User.Role.ADMIN,
            is_staff=True,
        )
        staff.user_permissions.add(
            Permission.objects.get(codename="change_organizationmembership")
        )
        if with_role_permission:
            staff.user_permissions.add(
                Permission.objects.get(codename="change_membership_role")
            )
        client = Client()
        client.force_login(staff)
        return client

    def test_role_field_readonly_without_permission(self):
        admin_client = self._staff_client(with_role_permission=False)
        url = reverse("admin:organizations_organizationmembership_change", args=[self.membership.pk])
        response = admin_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'name="role"')

    def test_role_field_editable_with_permission(self):
        admin_client = self._staff_client(with_role_permission=True)
        url = reverse("admin:organizations_organizationmembership_change", args=[self.membership.pk])
        response = admin_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="role"')