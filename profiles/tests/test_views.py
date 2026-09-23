from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from profiles.models import ClientProfile, EditorProfile


class ClientProfileViewTests(TestCase):
    def test_requires_login(self):
        response = self.client.get(reverse("profiles:edit_client_profile"))
        self.assertEqual(response.status_code, 302)

    def test_editor_cannot_access_client_profile_edit(self):
        editor = User.objects.create_user(
            email="editor@example.com", password="a-strong-password-1", role=User.Role.EDITOR
        )
        self.client.force_login(editor)
        response = self.client.get(reverse("profiles:edit_client_profile"))
        self.assertEqual(response.status_code, 403)

    def test_client_can_create_and_update_own_profile(self):
        client_user = User.objects.create_user(
            email="client@example.com", password="a-strong-password-1", role=User.Role.CLIENT
        )
        self.client.force_login(client_user)
        response = self.client.post(reverse("profiles:edit_client_profile"), {
            "institution": "Test University",
            "department": "",
            "academic_role": "",
            "country": "Kenya",
            "city": "",
            "phone": "",
            "preferred_communication_method": "",
            "research_interests": "",
            "orcid": "",
            "website": "",
            "preferred_citation_style": "",
        })
        self.assertEqual(response.status_code, 302)
        profile = ClientProfile.objects.get(user=client_user)
        self.assertEqual(profile.institution, "Test University")
        self.assertEqual(profile.country, "Kenya")


class EditorProfileViewTests(TestCase):
    def test_client_cannot_access_editor_profile_edit(self):
        client_user = User.objects.create_user(
            email="client2@example.com", password="a-strong-password-1", role=User.Role.CLIENT
        )
        self.client.force_login(client_user)
        response = self.client.get(reverse("profiles:edit_editor_profile"))
        self.assertEqual(response.status_code, 403)

    def test_editor_can_create_own_profile(self):
        editor = User.objects.create_user(
            email="editor2@example.com", password="a-strong-password-1", role=User.Role.EDITOR
        )
        self.client.force_login(editor)
        response = self.client.post(reverse("profiles:edit_editor_profile"), {
            "professional_name": "Jane Editor",
            "professional_title": "",
            "biography": "",
            "academic_background": "",
            "professional_experience": "",
            "subject_areas": "Medicine, Life Sciences",
            "editing_specializations": "",
            "citation_styles": "",
            "years_of_experience": 5,
            "languages": "English",
            "availability_status": "AVAILABLE",
        })
        self.assertEqual(response.status_code, 302)
        profile = EditorProfile.objects.get(user=editor)
        self.assertEqual(profile.professional_name, "Jane Editor")

    def test_senior_editor_also_allowed(self):
        senior = User.objects.create_user(
            email="senior@example.com", password="a-strong-password-1", role=User.Role.SENIOR_EDITOR
        )
        self.client.force_login(senior)
        response = self.client.get(reverse("profiles:edit_editor_profile"))
        self.assertEqual(response.status_code, 200)