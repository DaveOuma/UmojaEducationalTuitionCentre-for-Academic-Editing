from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("signup/", views.ClientSignupView.as_view(), name="signup"),
    path("dashboard/", views.dashboard_redirect, name="dashboard_redirect"),
]