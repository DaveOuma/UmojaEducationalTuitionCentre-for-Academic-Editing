import datetime

from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from assignments.models import Assignment
from website.models import Service, SubjectArea


class AssignmentAdminTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            email="staff@example.com", password="a-strong-password-1",
            role=User.Role.ADMIN, is_staff=True,
        )
        self.staff.user_permissions.add(
            *Permission.objects.filter(
                codename__in=["view_assignment", "change_assignment"],
                content_type__app_label="assignments",
            )
        )
        self.client_user = User.objects.create_user(
            email="client@example.com", password="a-strong-password-1", role=User.Role.CLIENT,
        )
        self.service = Service.objects.create(
            name="Thesis Editing", category=Service.Category.ACADEMIC,
            pricing_model=Service.PricingModel.PER_WORD,
        )
        self.subject_area = SubjectArea.objects.create(name="Life Sciences")
        self.assignment = Assignment.objects.create(
            client=self.client_user, service=self.service, subject_area=self.subject_area,
            requested_deadline=datetime.date.today() + datetime.timedelta(days=14),
        )
        self.django_client = self.client_class()
        self.django_client.force_login(self.staff)

    def test_status_field_is_not_directly_editable(self):
        url = reverse("admin:assignments_assignment_change", args=[self.assignment.pk])
        response = self.django_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<select name="status"')

    def test_transition_action_moves_valid_assignment(self):
        url = reverse("admin:assignments_assignment_changelist")
        response = self.django_client.post(url, {
            "action": "transition_to_submitted",
            "_selected_action": [str(self.assignment.pk)],
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assignment.refresh_from_db()
        self.assertEqual(self.assignment.status, Assignment.Status.SUBMITTED)

    def test_transition_action_skips_invalid_assignment(self):
        url = reverse("admin:assignments_assignment_changelist")
        response = self.django_client.post(url, {
            "action": "transition_to_completed",
            "_selected_action": [str(self.assignment.pk)],
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assignment.refresh_from_db()
        # DRAFT -> COMPLETED isn't a valid edge, so nothing should move.
        self.assertEqual(self.assignment.status, Assignment.Status.DRAFT)