from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from accounts.models import User

from .forms import ClientProfileForm, EditorProfileForm
from .models import ClientProfile, EditorProfile


@login_required
def edit_client_profile(request):
    """
    A client edits their own profile only. There is no path here (or
    in ClientProfileForm) that accepts a target user — the profile is
    always looked up and created against request.user.
    """
    if not request.user.is_client:
        raise PermissionDenied

    profile, _created = ClientProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ClientProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("profiles:edit_client_profile")
    else:
        form = ClientProfileForm(instance=profile)

    return render(request, "profiles/edit_client_profile.html", {"form": form})


@login_required
def edit_editor_profile(request):
    """Same pattern as edit_client_profile, for EDITOR/SENIOR_EDITOR users."""
    if not request.user.is_editor:
        raise PermissionDenied

    profile, _created = EditorProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = EditorProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("profiles:edit_editor_profile")
    else:
        form = EditorProfileForm(instance=profile)

    return render(request, "profiles/edit_editor_profile.html", {"form": form})