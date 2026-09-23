from django import forms

from .models import Service, SubjectArea


class QuoteInquiryForm(forms.Form):
    """
    Lightweight public inquiry form (Phase 3 design). Deliberately a
    plain Form, not a ModelForm — nothing is persisted. The view emails
    the cleaned data to SUPPORT_EMAIL and that's the whole workflow for
    this phase:

        Inquiry -> Email notification

    This does NOT create an Assignment or Quote. That real workflow
    (Inquiry -> Assignment -> Documents -> Quote -> Payment) is Phase 4+.
    """

    name = forms.CharField(max_length=255)
    email = forms.EmailField()
    service = forms.ModelChoiceField(
        queryset=Service.objects.filter(is_active=True),
        required=False,
        empty_label="Not sure yet",
    )
    subject_area = forms.ModelChoiceField(
        queryset=SubjectArea.objects.all(),
        required=False,
        empty_label="Not sure yet",
    )
    message = forms.CharField(widget=forms.Textarea)