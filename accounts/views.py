
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from .forms import PatientSignUpForm
from .models import User
from django.contrib import messages
from accounts.decorators import role_required

def home(request):
    return render(request, "home.html")



def register_patient(request):
    if request.method == "POST":
        form = PatientSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Más adelante redirigiremos a un dashboard por rol
            return redirect("home")
    else:
        form = PatientSignUpForm()

    return render(request, "accounts/register.html", {"form": form})


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"

    def get_success_url(self):
        # Más adelante podemos redirigir según rol (paciente, médico, admin)
        return "/"



def logout_view(request):
    logout(request)
    return redirect("accounts:home")

