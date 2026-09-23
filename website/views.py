from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.views.generic import FormView, TemplateView

from .forms import QuoteInquiryForm
from .models import Service, SubjectArea


class HomeView(TemplateView):
    template_name = "website/home.html"


class AboutView(TemplateView):
    template_name = "website/about.html"


class HowItWorksView(TemplateView):
    template_name = "website/how_it_works.html"


class ForResearchersView(TemplateView):
    template_name = "website/for_researchers.html"


class ForUniversitiesView(TemplateView):
    template_name = "website/for_universities.html"


class ForStudentsView(TemplateView):
    template_name = "website/for_students.html"


class PricingView(TemplateView):
    template_name = "website/pricing.html"


class FAQView(TemplateView):
    template_name = "website/faq.html"


class ContactView(TemplateView):
    template_name = "website/contact.html"


class PrivacyPolicyView(TemplateView):
    template_name = "website/legal/privacy_policy.html"


class TermsOfServiceView(TemplateView):
    template_name = "website/legal/terms_of_service.html"


class ConfidentialityPolicyView(TemplateView):
    template_name = "website/legal/confidentiality_policy.html"


class RefundCancellationPolicyView(TemplateView):
    template_name = "website/legal/refund_cancellation_policy.html"


def services_list(request):
    """
    Backs /services/, /services/?category=academic and
    /services/?category=scientific alike — one view, one template,
    the Service.category field doing the work (Phase 3 design decision
    to avoid duplicating "Academic Editing" / "Scientific Editing" as
    separate pages).
    """
    services = Service.objects.filter(is_active=True)

    category = request.GET.get("category", "").upper()
    if category in Service.Category.values:
        services = services.filter(category=category)

    context = {
        "services": services,
        "selected_category": category or None,
        "categories": Service.Category.choices,
    }
    return render(request, "website/services_list.html", context)


def subject_areas_list(request):
    subject_areas = SubjectArea.objects.all()
    return render(request, "website/subject_areas_list.html", {"subject_areas": subject_areas})


class RequestQuoteView(FormView):
    """
    Public inquiry form. On success, emails SUPPORT_EMAIL and redirects
    with a success message — nothing is written to the database here.
    See QuoteInquiryForm's docstring for why.
    """

    template_name = "website/request_a_quote.html"
    form_class = QuoteInquiryForm
    success_url = "/request-a-quote/"

    def form_valid(self, form):
        data = form.cleaned_data
        send_mail(
            subject=f"New quote inquiry from {data['name']}",
            message=(
                f"Name: {data['name']}\n"
                f"Email: {data['email']}\n"
                f"Service: {data['service']}\n"
                f"Subject area: {data['subject_area']}\n\n"
                f"Message:\n{data['message']}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.SUPPORT_EMAIL],
            fail_silently=False,
        )
        messages.success(
            self.request,
            "Thanks — your inquiry has been sent. We'll be in touch shortly.",
        )
        return super().form_valid(form)