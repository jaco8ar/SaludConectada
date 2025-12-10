from django import forms
from django.utils import timezone

from accounts.models import User
from .models import Appointment


class PatientAppointmentForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(
        queryset=User.objects.filter(role=User.Roles.DOCTOR),
        label="Médico",
    )

    scheduled_datetime = forms.DateTimeField(
        label="Fecha y hora",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
    )

    class Meta:
        model = Appointment
        fields = ("doctor", "scheduled_datetime", "reason")

    def clean_scheduled_datetime(self):
        dt = self.cleaned_data["scheduled_datetime"]
        # Conversión mínima para que no se creen citas en el pasado
        if dt < timezone.now():
            raise forms.ValidationError("La fecha y hora deben ser en el futuro.")
        return dt

    def save(self, patient, commit=True):
        appointment: Appointment = super().save(commit=False)
        appointment.patient = patient
        if commit:
            appointment.save()
        return appointment
