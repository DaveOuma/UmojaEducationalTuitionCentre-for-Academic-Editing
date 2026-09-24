from django.contrib import admin, messages

from .models import Assignment, InvalidStatusTransition


def _make_transition_action(target_status):
    """
    Builds one admin action per Status value, generated from
    ALLOWED_TRANSITIONS rather than hand-written per status — so the
    action list can never drift out of sync with the state machine
    itself. Each action only moves assignments for which the transition
    is currently valid; anything else is reported, not silently skipped.
    """

    def action(modeladmin, request, queryset):
        moved, skipped = 0, 0
        for assignment in queryset:
            try:
                assignment.transition_to(target_status, by_user=request.user)
                moved += 1
            except InvalidStatusTransition:
                skipped += 1
        label = Assignment.Status(target_status).label
        if moved:
            modeladmin.message_user(request, f"Moved {moved} assignment(s) to {label}.")
        if skipped:
            modeladmin.message_user(
                request,
                f"Skipped {skipped} assignment(s) — not a valid transition to {label} "
                f"from their current status.",
                level=messages.WARNING,
            )

    action.__name__ = f"transition_to_{target_status.lower()}"
    action.short_description = f"Move selected to: {Assignment.Status(target_status).label}"
    return action


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "reference", "client", "service", "assigned_editor",
        "status", "priority", "requested_deadline", "created_at",
    )
    list_filter = ("status", "priority", "service", "currency")
    search_fields = ("reference", "client__email", "assigned_editor__email")
    autocomplete_fields = ("client", "assigned_editor", "senior_editor", "service", "subject_area")
    readonly_fields = ("reference", "status", "created_at", "updated_at", "completed_at")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("reference", "status", "priority")}),
        ("People", {"fields": ("client", "assigned_editor", "senior_editor")}),
        ("Service", {"fields": ("service", "subject_area", "document_type", "citation_style")}),
        ("Journal", {"fields": ("journal", "journal_guidelines")}),
        ("Word count", {
            "fields": (
                "client_declared_word_count",
                "system_calculated_word_count",
                "billable_word_count",
            ),
        }),
        ("Deadlines", {"fields": ("requested_deadline", "confirmed_deadline")}),
        ("Instructions", {"fields": ("client_instructions", "internal_notes")}),
        ("Pricing", {"fields": ("price", "currency")}),
        ("Timestamps", {"fields": ("created_at", "updated_at", "completed_at")}),
    )

    # One generated action per status — see _make_transition_action above.
    actions = [_make_transition_action(status) for status in Assignment.Status.values]