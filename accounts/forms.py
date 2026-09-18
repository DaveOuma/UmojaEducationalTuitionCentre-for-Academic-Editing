from django.contrib.auth.forms import UserChangeForm as DjangoUserChangeForm
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm

from .models import User


class UserCreationForm(DjangoUserCreationForm):
    class Meta(DjangoUserCreationForm.Meta):
        model = User
        fields = ("email", "role")


class UserChangeForm(DjangoUserChangeForm):
    class Meta(DjangoUserChangeForm.Meta):
        model = User
        fields = "__all__"


class ClientSignupForm(DjangoUserCreationForm):
    """
    Public self-service signup form. Deliberately excludes `role` — the
    manager defaults new self-service users to CLIENT, and this form has
    no field through which that could be overridden.
    """

    class Meta(DjangoUserCreationForm.Meta):
        model = User
        fields = ("email", "first_name", "last_name")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.CLIENT
        if commit:
            user.save()
        return user


class ProfileUpdateForm(DjangoUserChangeForm):
    """
    Self-service "edit my own account" form for any authenticated user.
    Excludes role, is_active, is_staff, is_superuser, groups and
    user_permissions entirely, so there is no path for a user to escalate
    their own access through this form.
    """

    password = None  # remove the read-only password hash field from the base form

    class Meta(DjangoUserChangeForm.Meta):
        model = User
        fields = ("first_name", "last_name", "email")