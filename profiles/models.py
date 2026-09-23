from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class ClientProfile(models.Model):
    """
    Client-specific information, kept separate from User itself (spec
    section 3). One profile per user; created on demand rather than
    automatically for every signup, since not every User is a client.
    """

    class CommunicationMethod(models.TextChoices):
        EMAIL = "EMAIL", _("Email")
        PHONE = "PHONE", _("Phone")
        WHATSAPP = "WHATSAPP", _("WhatsApp")

    class CitationStyle(models.TextChoices):
        APA = "APA", _("APA")
        MLA = "MLA", _("MLA")
        CHICAGO = "CHICAGO", _("Chicago")
        HARVARD = "HARVARD", _("Harvard")
        VANCOUVER = "VANCOUVER", _("Vancouver")
        IEEE = "IEEE", _("IEEE")
        OTHER = "OTHER", _("Other")

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_profile",
    )

    institution = models.CharField(max_length=255, blank=True)
    department = models.CharField(max_length=255, blank=True)
    academic_role = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    preferred_communication_method = models.CharField(
        max_length=20, choices=CommunicationMethod.choices, blank=True
    )
    research_interests = models.TextField(blank=True)
    orcid = models.CharField(
        max_length=19,
        blank=True,
        help_text=_("Format: 0000-0000-0000-0000"),
    )
    website = models.URLField(blank=True)
    preferred_citation_style = models.CharField(
        max_length=20, choices=CitationStyle.choices, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("client profile")
        verbose_name_plural = _("client profiles")

    def __str__(self):
        return f"Client profile: {self.user.email}"


class EditorProfile(models.Model):
    """
    Editor-specific information (spec section 4). `subject_areas` is a
    plain text field for now — a temporary stand-in until Phase 9
    introduces a real SubjectArea model and this becomes a proper
    relation. `internal_rate` is deliberately NOT included yet; see
    Phase 2 design notes — it waits for Phase 9's pricing model so its
    scope (editor default vs service-specific vs org-specific vs
    historical-on-assignment) can be decided correctly rather than
    guessed at now.
    """

    class Availability(models.TextChoices):
        AVAILABLE = "AVAILABLE", _("Available")
        LIMITED = "LIMITED", _("Limited availability")
        UNAVAILABLE = "UNAVAILABLE", _("Unavailable")

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="editor_profile",
    )

    professional_name = models.CharField(max_length=255, blank=True)
    professional_title = models.CharField(max_length=255, blank=True)
    biography = models.TextField(blank=True)
    academic_background = models.TextField(blank=True)
    professional_experience = models.TextField(blank=True)

    # Temporary — replaced by a proper SubjectArea relation in Phase 9.
    subject_areas = models.TextField(
        blank=True,
        help_text=_("Comma-separated for now; becomes a structured relation in Phase 9."),
    )
    editing_specializations = models.TextField(blank=True)
    citation_styles = models.TextField(
        blank=True,
        help_text=_("Comma-separated citation styles the editor is comfortable with."),
    )
    years_of_experience = models.PositiveSmallIntegerField(null=True, blank=True)
    languages = models.CharField(max_length=255, blank=True)
    availability_status = models.CharField(
        max_length=20, choices=Availability.choices, default=Availability.AVAILABLE
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Inactive editors are excluded from assignment matching."),
    )
    profile_photo = models.ImageField(
        upload_to="editor_photos/", null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("editor profile")
        verbose_name_plural = _("editor profiles")

    def __str__(self):
        return f"Editor profile: {self.user.email}"