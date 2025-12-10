
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from .forms import PatientSignUpForm
from .models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect

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

