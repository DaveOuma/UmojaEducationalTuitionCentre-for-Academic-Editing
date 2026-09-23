from django.urls import path

from . import views

app_name = "website"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("services/", views.services_list, name="services"),
    path("subject-areas/", views.subject_areas_list, name="subject_areas"),
    path("how-it-works/", views.HowItWorksView.as_view(), name="how_it_works"),
    path("researchers/", views.ForResearchersView.as_view(), name="for_researchers"),
    path("universities/", views.ForUniversitiesView.as_view(), name="for_universities"),
    path("students/", views.ForStudentsView.as_view(), name="for_students"),
    path("pricing/", views.PricingView.as_view(), name="pricing"),
    path("request-a-quote/", views.RequestQuoteView.as_view(), name="request_a_quote"),
    path("faq/", views.FAQView.as_view(), name="faq"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("privacy/", views.PrivacyPolicyView.as_view(), name="privacy"),
    path("terms/", views.TermsOfServiceView.as_view(), name="terms"),
    path("confidentiality/", views.ConfidentialityPolicyView.as_view(), name="confidentiality"),
    path("refund-cancellation/", views.RefundCancellationPolicyView.as_view(), name="refund_cancellation"),
]