from django.contrib import admin

from .models import Organization, OrganizationMembership


class OrganizationMembershipInline(admin.TabularInline):
    model = OrganizationMembership
    extra = 0
    autocomplete_fields = ("user",)
    readonly_fields = ("joined_at",)

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        # Same principle as accounts.change_user_role: membership role is
        # an authorization field, gated behind a dedicated permission
        # rather than editable by any staff member with org access.
        if not request.user.has_perm("organizations.change_membership_role"):
            readonly.append("role")
        return readonly


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "org_type", "country", "contact_email", "created_at")
    list_filter = ("org_type", "country")
    search_fields = ("name", "contact_email")
    readonly_fields = ("created_at",)
    inlines = [OrganizationMembershipInline]


@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "organization", "role", "joined_at")
    list_filter = ("role",)
    search_fields = ("user__email", "organization__name")
    autocomplete_fields = ("user", "organization")
    readonly_fields = ("joined_at",)

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if not request.user.has_perm("organizations.change_membership_role"):
            readonly.append("role")
        return readonly