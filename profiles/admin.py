from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import ClientProfile, EditorProfile


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "institution", "country", "preferred_citation_style", "created_at")
    list_filter = ("preferred_citation_style", "country")
    search_fields = ("user__email", "institution", "department")
    autocomplete_fields = ("user",)
    readonly_fields = ("created_at",)


@admin.register(EditorProfile)
class EditorProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "professional_name", "availability_status", "is_active", "years_of_experience")
    list_filter = ("availability_status", "is_active")
    search_fields = ("user__email", "professional_name", "subject_areas")
    autocomplete_fields = ("user",)
    readonly_fields = ("created_at",)