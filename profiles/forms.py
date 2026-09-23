from django import forms

from .models import ClientProfile, EditorProfile


class ClientProfileForm(forms.ModelForm):
    """
    Self-service edit form for a client's own profile. `user` is
    excluded — it's set once, from request.user, in the view, never
    from form input, so there's no field through which someone could
    attach a profile to a different account.
    """

    class Meta:
        model = ClientProfile
        fields = [
            "institution",
            "department",
            "academic_role",
            "country",
            "city",
            "phone",
            "preferred_communication_method",
            "research_interests",
            "orcid",
            "website",
            "preferred_citation_style",
        ]


class EditorProfileForm(forms.ModelForm):
    """
    Self-service edit form for an editor's own profile. Excludes
    `user` and `is_active` deliberately — `is_active` controls whether
    the editor is excluded from assignment matching entirely (spec
    section 18), which is an administrative call, not a self-service
    toggle. `availability_status` IS included: editors are meant to
    update their own day-to-day availability (spec section 25).
    """

    class Meta:
        model = EditorProfile
        fields = [
            "professional_name",
            "professional_title",
            "biography",
            "academic_background",
            "professional_experience",
            "subject_areas",
            "editing_specializations",
            "citation_styles",
            "years_of_experience",
            "languages",
            "availability_status",
            "profile_photo",
        ]