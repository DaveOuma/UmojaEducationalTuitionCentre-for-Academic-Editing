from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import EmailValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for the platform. Email is the login identifier —
    there is no username field, which suits an international client base
    better than Django's default.

    `role` is a coarse, always-present label used for the common case
    ("is this a client, an editor, an admin?"). It is deliberately NOT
    the only authorization mechanism: Django's Group/Permission system
    sits on top of it for anything more granular (see groups.py), and
    `is_superuser` remains Django's own ultimate override — SUPER_ADMIN
    is a role label for UI/business purposes, not a re-implementation
    of is_superuser.

    Role changes must go through an authorized-admin-only path (enforced
    in accounts/admin.py and accounts/forms.py, not here) — a user must
    never be able to set their own role.
    """

    class Role(models.TextChoices):
        CLIENT = "CLIENT", _("Client")
        EDITOR = "EDITOR", _("Editor")
        SENIOR_EDITOR = "SENIOR_EDITOR", _("Senior Editor")
        ADMIN = "ADMIN", _("Administrator")
        SUPER_ADMIN = "SUPER_ADMIN", _("Super Administrator")

    email = models.EmailField(
        _("email address"),
        unique=True,
        validators=[EmailValidator()],
        db_index=True,
    )
    role = models.CharField(
        _("role"),
        max_length=20,
        choices=Role.choices,
        default=Role.CLIENT,
    )

    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)

    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Unselect instead of deleting accounts to preserve assignment "
            "and audit history."
        ),
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Whether the user can access the Django admin site."),
    )

    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    last_login_ip = models.GenericIPAddressField(
        _("last login IP"), null=True, blank=True
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # email + password are the only fields required by createsuperuser

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-date_joined"]
        permissions = [
            ("change_user_role", "Can change a user's role"),
        ]

    def __str__(self):
        return self.email

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.email

    def get_short_name(self):
        return self.first_name or self.email

    # --- Role helpers -----------------------------------------------------
    # Convenience checks for templates/views. These read the role field;
    # they do not grant permissions themselves. Use Django permissions
    # (has_perm) for anything that should be independently grantable.

    @property
    def is_client(self):
        return self.role == self.Role.CLIENT

    @property
    def is_editor(self):
        return self.role in {self.Role.EDITOR, self.Role.SENIOR_EDITOR}

    @property
    def is_senior_editor(self):
        return self.role == self.Role.SENIOR_EDITOR

    @property
    def is_admin_role(self):
        return self.role in {self.Role.ADMIN, self.Role.SUPER_ADMIN}