from django import forms
from accounts.models import User


class UserRoleForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("role",)
        labels = {"role": "Rol"}
