from django.db import IntegrityError, transaction
from django.test import TestCase

from accounts.models import User
from organizations.models import Organization, OrganizationMembership


class OrganizationMembershipTests(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(
            name="Test University", org_type=Organization.OrgType.UNIVERSITY
        )
        self.user = User.objects.create_user(
            email="researcher@example.com", password="a-strong-password-1"
        )

    def test_default_role_is_member(self):
        membership = OrganizationMembership.objects.create(
            organization=self.org, user=self.user
        )
        self.assertEqual(membership.role, OrganizationMembership.MembershipRole.MEMBER)

    def test_role_independent_of_platform_role(self):
        # A platform CLIENT can be an ORG_ADMIN within their org.
        membership = OrganizationMembership.objects.create(
            organization=self.org,
            user=self.user,
            role=OrganizationMembership.MembershipRole.ORG_ADMIN,
        )
        self.assertEqual(self.user.role, User.Role.CLIENT)
        self.assertEqual(membership.role, OrganizationMembership.MembershipRole.ORG_ADMIN)

    def test_unique_membership_per_org(self):
        OrganizationMembership.objects.create(organization=self.org, user=self.user)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                OrganizationMembership.objects.create(organization=self.org, user=self.user)

    def test_user_can_belong_to_multiple_orgs(self):
        org2 = Organization.objects.create(
            name="Another University", org_type=Organization.OrgType.UNIVERSITY
        )
        OrganizationMembership.objects.create(organization=self.org, user=self.user)
        OrganizationMembership.objects.create(organization=org2, user=self.user)
        self.assertEqual(self.user.organizations.count(), 2)