
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from .forms import PatientSignUpForm
from .models import User
from django.contrib import messages
from accounts.decorators import role_required
from django.urls import reverse

def home(request):
    if request.user.is_authenticated:
        return redirect(get_dashboard_url_for_user(request.user))
    return render(request, "home.html")

def register_patient(request):
    if request.method == "POST":
        form = PatientSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Ahora redirigimos al dashboard según rol (paciente en este caso)
            return redirect(get_dashboard_url_for_user(user))
    else:
        form = PatientSignUpForm()

    return render(request, "accounts/register.html", {"form": form})


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"

    def get_success_url(self):
        # Redirigir según rol del usuario logueado
        return get_dashboard_url_for_user(self.request.user)




def logout_view(request):
    logout(request)
    return redirect("accounts:home")

def get_dashboard_url_for_user(user) -> str:
    """
    Devuelve la URL (como string) del dashboard correspondiente al rol del usuario.
    """
    if not user.is_authenticated:
        return reverse("accounts:home")

    if user.role == User.Roles.PATIENT:
        return reverse("dashboard:patient_dashboard")
    elif user.role == User.Roles.DOCTOR:
        return reverse("dashboard:doctor_dashboard")
    elif user.role == User.Roles.ADMIN:
        return reverse("dashboard:admin_dashboard")

    # Fallback por si acaso
    return reverse("accounts:home")

