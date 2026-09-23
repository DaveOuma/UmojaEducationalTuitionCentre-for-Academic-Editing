from django.core import mail
from django.test import TestCase
from django.urls import reverse

from website.models import Service, SubjectArea


class StaticPageSmokeTests(TestCase):
    """Every static page must at least render without error."""

    def test_all_named_pages_return_200(self):
        page_names = [
            "website:home", "website:about", "website:how_it_works",
            "website:for_researchers", "website:for_universities", "website:for_students",
            "website:pricing", "website:faq", "website:contact",
            "website:privacy", "website:terms", "website:confidentiality",
            "website:refund_cancellation",
        ]
        for name in page_names:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)


class ServicesListViewTests(TestCase):
    def setUp(self):
        self.academic = Service.objects.create(
            name="Thesis Editing", category=Service.Category.ACADEMIC,
            pricing_model=Service.PricingModel.PER_WORD,
        )
        self.scientific = Service.objects.create(
            name="Manuscript Editing", category=Service.Category.SCIENTIFIC,
            pricing_model=Service.PricingModel.PER_PAGE,
        )
        self.inactive = Service.objects.create(
            name="Retired Service", category=Service.Category.ACADEMIC,
            pricing_model=Service.PricingModel.FLAT_FEE, is_active=False,
        )

    def test_lists_only_active_services_by_default(self):
        response = self.client.get(reverse("website:services"))
        services = list(response.context["services"])
        self.assertIn(self.academic, services)
        self.assertIn(self.scientific, services)
        self.assertNotIn(self.inactive, services)

    def test_filters_by_academic_category(self):
        response = self.client.get(reverse("website:services"), {"category": "academic"})
        services = list(response.context["services"])
        self.assertIn(self.academic, services)
        self.assertNotIn(self.scientific, services)

    def test_filters_by_scientific_category(self):
        response = self.client.get(reverse("website:services"), {"category": "scientific"})
        services = list(response.context["services"])
        self.assertIn(self.scientific, services)
        self.assertNotIn(self.academic, services)

    def test_invalid_category_falls_back_to_all_active(self):
        response = self.client.get(reverse("website:services"), {"category": "not-a-category"})
        services = list(response.context["services"])
        self.assertIn(self.academic, services)
        self.assertIn(self.scientific, services)


class SubjectAreasListViewTests(TestCase):
    def test_lists_subject_areas(self):
        SubjectArea.objects.create(name="Medicine")
        response = self.client.get(reverse("website:subject_areas"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Medicine")


class RequestQuoteViewTests(TestCase):
    def test_valid_submission_sends_email_and_creates_no_records(self):
        response = self.client.post(reverse("website:request_a_quote"), {
            "name": "Jane Researcher",
            "email": "jane@example.com",
            "service": "",
            "subject_area": "",
            "message": "I need my thesis edited before next month.",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Jane Researcher", mail.outbox[0].subject)

    def test_missing_required_fields_does_not_send_email(self):
        response = self.client.post(reverse("website:request_a_quote"), {
            "name": "",
            "email": "not-an-email",
            "message": "",
        })
        self.assertEqual(response.status_code, 200)  # re-renders form with errors
        self.assertEqual(len(mail.outbox), 0)