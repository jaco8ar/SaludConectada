from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class PatientSignUpForm(UserCreationForm):
    first_name = forms.CharField(label="Nombre", required=True)
    last_name = forms.CharField(label="Apellido", required=True)
    email = forms.EmailField(label="Correo electrónico", required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Roles.PATIENT
        if commit:
            user.save()
        return user
