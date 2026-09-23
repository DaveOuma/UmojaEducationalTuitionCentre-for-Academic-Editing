from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Organization(models.Model):
    """
    Institutional/university client accounts (spec section 33).
    `billing_info` is a plain text field for now, kept deliberately
    minimal until a real institutional-billing model is designed —
    same reasoning as deferring EditorProfile.internal_rate.
    """

    class OrgType(models.TextChoices):
        UNIVERSITY = "UNIVERSITY", _("University")
        RESEARCH_INSTITUTION = "RESEARCH_INSTITUTION", _("Research institution")
        DEPARTMENT = "DEPARTMENT", _("Academic department")
        COMPANY = "COMPANY", _("Company")
        OTHER = "OTHER", _("Other")

    name = models.CharField(max_length=255)
    org_type = models.CharField(max_length=30, choices=OrgType.choices)
    country = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    billing_info = models.TextField(
        blank=True,
        help_text=_("Free-text for now — structured billing/PO fields are a later phase."),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="OrganizationMembership",
        related_name="organizations",
    )

    class Meta:
        verbose_name = _("organization")
        verbose_name_plural = _("organizations")
        ordering = ["name"]

    def __str__(self):
        return self.name


class OrganizationMembership(models.Model):
    """
    Join model between Organization and User. `role` here is
    intentionally separate from the platform-wide User.role — a
    platform CLIENT can be an ORG_ADMIN within their own organization
    without that changing their platform-level permissions at all.
    """

    class MembershipRole(models.TextChoices):
        MEMBER = "MEMBER", _("Member")
        ORG_ADMIN = "ORG_ADMIN", _("Organization Administrator")

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="memberships"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organization_memberships",
    )
    role = models.CharField(
        max_length=20, choices=MembershipRole.choices, default=MembershipRole.MEMBER
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("organization membership")
        verbose_name_plural = _("organization memberships")
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "user"], name="unique_membership_per_org"
            )
        ]
        permissions = [
            ("change_membership_role", "Can change an organization membership's role"),
        ]

    def __str__(self):
        return f"{self.user.email} @ {self.organization.name} ({self.role})"