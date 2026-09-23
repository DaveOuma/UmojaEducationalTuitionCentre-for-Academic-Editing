from django.urls import path

from . import views

app_name = "profiles"

urlpatterns = [
    path("client/", views.edit_client_profile, name="edit_client_profile"),
    path("editor/", views.edit_editor_profile, name="edit_editor_profile"),
]