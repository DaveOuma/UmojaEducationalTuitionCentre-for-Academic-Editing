import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.models import User
from assignments.models import Assignment, InvalidStatusTransition
from website.models import Service, SubjectArea


def make_user(email, role):
    return User.objects.create_user(email=email, password="a-strong-password-1", role=role)


class AssignmentFactoryMixin:
    def setUp(self):
        self.client_user = make_user("client@example.com", User.Role.CLIENT)
        self.editor = make_user("editor@example.com", User.Role.EDITOR)
        self.senior_editor = make_user("senior@example.com", User.Role.SENIOR_EDITOR)
        self.service = Service.objects.create(
            name="Thesis Editing", category=Service.Category.ACADEMIC,
            pricing_model=Service.PricingModel.PER_WORD,
        )
        self.subject_area = SubjectArea.objects.create(name="Life Sciences")

    def make_assignment(self, **overrides):
        defaults = {
            "client": self.client_user,
            "service": self.service,
            "subject_area": self.subject_area,
            "requested_deadline": datetime.date.today() + datetime.timedelta(days=14),
        }
        defaults.update(overrides)
        return Assignment.objects.create(**defaults)


class ReferenceGenerationTests(AssignmentFactoryMixin, TestCase):
    def test_reference_auto_generated_on_create(self):
        assignment = self.make_assignment()
        self.assertRegex(assignment.reference, r"^UETC-\d{4}-\d{4}$")

    def test_sequence_increments_within_same_year(self):
        first = self.make_assignment()
        second = self.make_assignment()
        first_seq = int(first.reference.rsplit("-", 1)[-1])
        second_seq = int(second.reference.rsplit("-", 1)[-1])
        self.assertEqual(second_seq, first_seq + 1)

    def test_explicit_reference_preserved(self):
        assignment = self.make_assignment(reference="UETC-2099-9999")
        self.assertEqual(assignment.reference, "UETC-2099-9999")


class RoleValidationTests(AssignmentFactoryMixin, TestCase):
    def test_client_must_have_client_role(self):
        with self.assertRaises(ValidationError):
            self.make_assignment(client=self.editor)

    def test_assigned_editor_must_have_editor_role(self):
        with self.assertRaises(ValidationError):
            self.make_assignment(assigned_editor=self.client_user)

    def test_assigned_editor_accepts_editor_role(self):
        assignment = self.make_assignment(assigned_editor=self.editor)
        self.assertEqual(assignment.assigned_editor, self.editor)

    def test_assigned_editor_accepts_senior_editor_role(self):
        assignment = self.make_assignment(assigned_editor=self.senior_editor)
        self.assertEqual(assignment.assigned_editor, self.senior_editor)

    def test_senior_editor_field_rejects_plain_editor(self):
        with self.assertRaises(ValidationError):
            self.make_assignment(senior_editor=self.editor)

    def test_senior_editor_field_accepts_senior_editor_role(self):
        assignment = self.make_assignment(senior_editor=self.senior_editor)
        self.assertEqual(assignment.senior_editor, self.senior_editor)


class StatusTransitionTests(AssignmentFactoryMixin, TestCase):
    def test_new_assignment_starts_in_draft(self):
        assignment = self.make_assignment()
        self.assertEqual(assignment.status, Assignment.Status.DRAFT)

    def test_valid_transition_succeeds(self):
        assignment = self.make_assignment()
        assignment.transition_to(Assignment.Status.SUBMITTED, by_user=self.client_user)
        assignment.refresh_from_db()
        self.assertEqual(assignment.status, Assignment.Status.SUBMITTED)

    def test_invalid_transition_raises_and_does_not_change_status(self):
        assignment = self.make_assignment()
        with self.assertRaises(InvalidStatusTransition):
            assignment.transition_to(Assignment.Status.COMPLETED, by_user=self.client_user)
        assignment.refresh_from_db()
        self.assertEqual(assignment.status, Assignment.Status.DRAFT)

    def test_terminal_states_allow_no_further_transitions(self):
        assignment = self.make_assignment()
        assignment.transition_to(Assignment.Status.CANCELLED, by_user=self.client_user)
        with self.assertRaises(InvalidStatusTransition):
            assignment.transition_to(Assignment.Status.SUBMITTED, by_user=self.client_user)

    def test_every_status_has_an_explicit_entry_in_the_transition_map(self):
        # Guards against ever adding a new Status without also deciding
        # what it can and can't transition to.
        for status in Assignment.Status.values:
            self.assertIn(
                status, Assignment.ALLOWED_TRANSITIONS,
                f"{status} has no entry in ALLOWED_TRANSITIONS",
            )

    def test_completed_sets_completed_at(self):
        assignment = self.make_assignment()
        for step in [
            Assignment.Status.SUBMITTED, Assignment.Status.UNDER_REVIEW,
            Assignment.Status.QUOTE_PENDING, Assignment.Status.QUOTE_SENT,
            Assignment.Status.QUOTE_ACCEPTED, Assignment.Status.AWAITING_PAYMENT,
            Assignment.Status.PAID, Assignment.Status.ASSIGNED,
            Assignment.Status.IN_PROGRESS, Assignment.Status.QUALITY_REVIEW,
            Assignment.Status.AWAITING_CLIENT, Assignment.Status.COMPLETED,
        ]:
            assignment.transition_to(step, by_user=self.client_user)
        assignment.refresh_from_db()
        self.assertIsNotNone(assignment.completed_at)

    def test_quality_review_can_bounce_back_to_in_progress(self):
        assignment = self.make_assignment()
        for step in [
            Assignment.Status.SUBMITTED, Assignment.Status.UNDER_REVIEW,
            Assignment.Status.QUOTE_PENDING, Assignment.Status.QUOTE_SENT,
            Assignment.Status.QUOTE_ACCEPTED, Assignment.Status.AWAITING_PAYMENT,
            Assignment.Status.PAID, Assignment.Status.ASSIGNED,
            Assignment.Status.IN_PROGRESS, Assignment.Status.QUALITY_REVIEW,
        ]:
            assignment.transition_to(step, by_user=self.client_user)
        assignment.transition_to(Assignment.Status.IN_PROGRESS, by_user=self.senior_editor)
        assignment.refresh_from_db()
        self.assertEqual(assignment.status, Assignment.Status.IN_PROGRESS)

    def test_revision_requested_loops_back_to_in_progress(self):
        assignment = self.make_assignment(status=Assignment.Status.AWAITING_CLIENT)
        assignment.transition_to(Assignment.Status.REVISION_REQUESTED, by_user=self.client_user)
        assignment.transition_to(Assignment.Status.IN_PROGRESS, by_user=self.editor)
        assignment.refresh_from_db()
        self.assertEqual(assignment.status, Assignment.Status.IN_PROGRESS)


class AssignmentStrTests(AssignmentFactoryMixin, TestCase):
    def test_str_is_the_reference(self):
        assignment = self.make_assignment()
        self.assertEqual(str(assignment), assignment.reference)