from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import ClientSignupForm
from .models import User


class LoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class LogoutView(auth_views.LogoutView):
    pass


class ClientSignupView(CreateView):
    """
    Public self-service signup. Always creates a CLIENT — see
    ClientSignupForm and UserManager.create_user, which is the only path
    that assigns the role, so there is nowhere in this view a different
    role could be introduced.
    """

    form_class = ClientSignupForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("accounts:login")


@login_required
def dashboard_redirect(request):
    """
    Sends a just-logged-in user to the dashboard for their role. The
    actual dashboards are built in Phases 6-8; until then this renders a
    minimal placeholder so the login flow is fully testable end to end.
    """
    role = request.user.role
    context = {"role": role, "role_label": User.Role(role).label}
    return render(request, "accounts/dashboard_placeholder.html", context)