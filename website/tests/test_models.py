from django.test import TestCase

from website.models import Service, SubjectArea


class ServiceTests(TestCase):
    def test_slug_auto_generated(self):
        service = Service.objects.create(
            name="Thesis Editing",
            category=Service.Category.ACADEMIC,
            pricing_model=Service.PricingModel.PER_WORD,
        )
        self.assertEqual(service.slug, "thesis-editing")

    def test_explicit_slug_preserved(self):
        service = Service.objects.create(
            name="Thesis Editing",
            slug="custom-slug",
            category=Service.Category.ACADEMIC,
            pricing_model=Service.PricingModel.PER_WORD,
        )
        self.assertEqual(service.slug, "custom-slug")

    def test_ordering_by_display_order_then_name(self):
        Service.objects.create(
            name="B Service", category=Service.Category.ACADEMIC,
            pricing_model=Service.PricingModel.FLAT_FEE, display_order=2,
        )
        Service.objects.create(
            name="A Service", category=Service.Category.ACADEMIC,
            pricing_model=Service.PricingModel.FLAT_FEE, display_order=1,
        )
        names = list(Service.objects.values_list("name", flat=True))
        self.assertEqual(names, ["A Service", "B Service"])

    def test_str(self):
        service = Service.objects.create(
            name="Manuscript Editing", category=Service.Category.SCIENTIFIC,
            pricing_model=Service.PricingModel.PER_PAGE,
        )
        self.assertEqual(str(service), "Manuscript Editing")


class SubjectAreaTests(TestCase):
    def test_slug_auto_generated(self):
        area = SubjectArea.objects.create(name="Life Sciences")
        self.assertEqual(area.slug, "life-sciences")

    def test_str(self):
        area = SubjectArea.objects.create(name="Engineering")
        self.assertEqual(str(area), "Engineering")