from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from website.models import Service, SubjectArea


class InvalidStatusTransition(Exception):
    """Raised when transition_to() is asked to make a move the state
    machine doesn't allow. Deliberately not a ValidationError — this is
    a programming/workflow error, not user input to redisplay on a form."""


class Assignment(models.Model):
    """
    The central workflow object (spec section 10). Deliberately narrow
    for Phase 4: no Quote, Payment, Delivery, RevisionRequest,
    AssignmentFile, or AuditLog yet — those are Phases 5 and 9-16.

    Ownership is single-editor for now (assigned_editor, nullable) —
    no AssignmentEditor through-model. Multi-editor support is a real
    design decision (word-count splitting, payment allocation, deadline
    ownership) deferred until it's actually needed, not inferred from
    this field's cardinality.
    """

    class Status(models.TextChoices):
        DRAFT = "DRAFT", _("Draft")
        SUBMITTED = "SUBMITTED", _("Submitted")
        UNDER_REVIEW = "UNDER_REVIEW", _("Under Review")
        QUOTE_PENDING = "QUOTE_PENDING", _("Quote Pending")
        QUOTE_SENT = "QUOTE_SENT", _("Quote Sent")
        QUOTE_ACCEPTED = "QUOTE_ACCEPTED", _("Quote Accepted")
        AWAITING_PAYMENT = "AWAITING_PAYMENT", _("Awaiting Payment")
        PAID = "PAID", _("Paid")
        ASSIGNED = "ASSIGNED", _("Assigned")
        IN_PROGRESS = "IN_PROGRESS", _("In Progress")
        QUALITY_REVIEW = "QUALITY_REVIEW", _("Quality Review")
        AWAITING_CLIENT = "AWAITING_CLIENT", _("Awaiting Client")
        REVISION_REQUESTED = "REVISION_REQUESTED", _("Revision Requested")
        COMPLETED = "COMPLETED", _("Completed")
        CANCELLED = "CANCELLED", _("Cancelled")
        DECLINED = "DECLINED", _("Declined")
        DISPUTED = "DISPUTED", _("Disputed")

    class Priority(models.TextChoices):
        LOW = "LOW", _("Low")
        NORMAL = "NORMAL", _("Normal")
        HIGH = "HIGH", _("High")
        URGENT = "URGENT", _("Urgent")

    class Currency(models.TextChoices):
        KES = "KES", _("Kenyan Shilling")
        USD = "USD", _("US Dollar")
        EUR = "EUR", _("Euro")
        GBP = "GBP", _("British Pound")
        JPY = "JPY", _("Japanese Yen")
        KRW = "KRW", _("South Korean Won")
        CNY = "CNY", _("Chinese Yuan")
        AED = "AED", _("UAE Dirham")
        SAR = "SAR", _("Saudi Riyal")

    # Every permitted move, defined explicitly — no status is reachable
    # from "most" states by convention. CANCELLED/DECLINED/DISPUTED are
    # each listed only where they actually apply, not blanket-added.
    ALLOWED_TRANSITIONS = {
        Status.DRAFT: {Status.SUBMITTED, Status.CANCELLED},
        Status.SUBMITTED: {Status.UNDER_REVIEW, Status.DECLINED, Status.CANCELLED},
        Status.UNDER_REVIEW: {Status.QUOTE_PENDING, Status.DECLINED, Status.CANCELLED},
        Status.QUOTE_PENDING: {Status.QUOTE_SENT, Status.DECLINED, Status.CANCELLED},
        Status.QUOTE_SENT: {Status.QUOTE_ACCEPTED, Status.DECLINED, Status.CANCELLED},
        Status.QUOTE_ACCEPTED: {Status.AWAITING_PAYMENT, Status.CANCELLED},
        Status.AWAITING_PAYMENT: {Status.PAID, Status.CANCELLED},
        Status.PAID: {Status.ASSIGNED, Status.DISPUTED},
        Status.ASSIGNED: {Status.IN_PROGRESS, Status.DISPUTED},
        Status.IN_PROGRESS: {Status.QUALITY_REVIEW, Status.DISPUTED},
        # Senior review can bounce work back to the editor before the
        # client ever sees it, not just move forward.
        Status.QUALITY_REVIEW: {Status.AWAITING_CLIENT, Status.IN_PROGRESS, Status.DISPUTED},
        Status.AWAITING_CLIENT: {Status.COMPLETED, Status.REVISION_REQUESTED, Status.DISPUTED},
        Status.REVISION_REQUESTED: {Status.IN_PROGRESS, Status.DISPUTED},
        # A dispute can resolve back into work, get cancelled, or turn
        # out to have been fine after all.
        Status.DISPUTED: {Status.IN_PROGRESS, Status.CANCELLED, Status.COMPLETED},
        # Terminal states — no transitions out.
        Status.COMPLETED: set(),
        Status.CANCELLED: set(),
        Status.DECLINED: set(),
    }

    reference = models.CharField(
        max_length=32, unique=True, editable=False, db_index=True,
        help_text=_("Auto-generated, e.g. UETC-2026-0012."),
    )

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="assignments_as_client",
    )
    assigned_editor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True,
        related_name="assignments_as_editor",
    )
    senior_editor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True,
        related_name="assignments_as_senior_editor",
    )

    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name="assignments")
    subject_area = models.ForeignKey(SubjectArea, on_delete=models.PROTECT, related_name="assignments")

    document_type = models.CharField(max_length=100, blank=True)

    # Word count — see spec section 16. Only client_declared_word_count
    # is populated in Phase 4; the other two exist now so Phase 5's
    # migration doesn't need to revisit this model, but stay null/unused
    # until there's an uploaded document to calculate from.
    client_declared_word_count = models.PositiveIntegerField(null=True, blank=True)
    system_calculated_word_count = models.PositiveIntegerField(null=True, blank=True)
    billable_word_count = models.PositiveIntegerField(null=True, blank=True)

    citation_style = models.CharField(max_length=100, blank=True)
    journal = models.CharField(max_length=255, blank=True)
    journal_guidelines = models.TextField(blank=True)

    requested_deadline = models.DateField()
    confirmed_deadline = models.DateField(null=True, blank=True)

    client_instructions = models.TextField(blank=True)
    internal_notes = models.TextField(
        blank=True,
        help_text=_("Staff-only. Never rendered on any client-facing view."),
    )

    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.KES)

    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.NORMAL)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("assignment")
        verbose_name_plural = _("assignments")
        ordering = ["-created_at"]

    def __str__(self):
        return self.reference

    # --- Validation ---------------------------------------------------
    # Role correctness is enforced here, not only in forms — a FK can't
    # express "must be a User with role=CLIENT" at the database level,
    # so it's checked in clean() and run via full_clean() on every save.

    def clean(self):
        errors = {}
        if self.client_id and self.client.role != User.Role.CLIENT:
            errors["client"] = _("The client on an assignment must have the CLIENT role.")
        if self.assigned_editor_id and self.assigned_editor.role not in {
            User.Role.EDITOR, User.Role.SENIOR_EDITOR,
        }:
            errors["assigned_editor"] = _("The assigned editor must have the EDITOR or SENIOR_EDITOR role.")
        if self.senior_editor_id and self.senior_editor.role != User.Role.SENIOR_EDITOR:
            errors["senior_editor"] = _("The senior editor must have the SENIOR_EDITOR role.")
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self._generate_reference()
        self.full_clean()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_reference():
        """
        Format: UETC-<year>-<4-digit sequence>, per spec section 15's
        example (UETC-2026-0012). Sequence resets each calendar year.

        Note: this reads-then-writes without a DB-level lock, so two
        assignments created in the same instant could theoretically
        race for the same sequence number. Acceptable for a single- or
        few-editor operation at Phase 4's scale; revisit with a
        select_for_update or a dedicated sequence table if concurrent
        creation ever becomes frequent enough to matter.
        """
        year = timezone.now().year
        prefix = f"UETC-{year}-"
        last = (
            Assignment.objects.filter(reference__startswith=prefix)
            .order_by("-reference")
            .values_list("reference", flat=True)
            .first()
        )
        next_seq = int(last.rsplit("-", 1)[-1]) + 1 if last else 1
        return f"{prefix}{next_seq:04d}"

    # --- Status transitions --------------------------------------------
    # The only application-level route for changing status. Never set
    # assignment.status directly outside this method or a migration.

    def transition_to(self, new_status, by_user):
        """
        Move to new_status if the current status allows it. `by_user`
        isn't used for anything yet — it's part of the signature now so
        every call site is already passing what Phase 16's AuditLog
        will need, rather than that being a breaking change later.
        """
        allowed = self.ALLOWED_TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise InvalidStatusTransition(
                f"Cannot transition assignment {self.reference} from "
                f"{self.status} to {new_status}."
            )
        self.status = new_status
        if new_status == self.Status.COMPLETED:
            self.completed_at = timezone.now()
        self.save(update_fields=["status", "completed_at", "updated_at"])
        return self