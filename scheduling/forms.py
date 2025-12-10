from django import forms
from django.utils import timezone
from accounts.models import User
from .models import Appointment, DoctorAvailability


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

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get("doctor")
        dt = cleaned_data.get("scheduled_datetime")

        if not doctor or not dt:
            return cleaned_data

        # 1. No permitir fechas en el pasado
        if dt <= timezone.now():
            raise forms.ValidationError(
                "La fecha y hora deben ser en el futuro."
            )

        # 2. Verificar disponibilidad del médico (día y franja)
        weekday = dt.weekday()
        time = dt.time()

        availability_qs = DoctorAvailability.objects.filter(
            doctor=doctor,
            is_active=True,
            weekday=weekday,
            start_time__lte=time,
            end_time__gt=time,  # simplificación: punto en el tiempo dentro del rango
        )

        if not availability_qs.exists():
            raise forms.ValidationError(
                "El médico no tiene disponibilidad configurada para ese día y hora."
            )

        # 3. Evitar choque con otra cita EXACTAMENTE a la misma fecha/hora
        conflict_qs = Appointment.objects.filter(
            doctor=doctor,
            scheduled_datetime=dt,
        ).exclude(status=Appointment.Status.CANCELED)

        if conflict_qs.exists():
            raise forms.ValidationError(
                "Ya existe una cita para ese médico en esa fecha y hora."
            )

        return cleaned_data

    def save(self, patient, commit=True):
        appointment: Appointment = super().save(commit=False)
        appointment.patient = patient
        if commit:
            appointment.save()
        return appointment

class DoctorAvailabilityForm(forms.ModelForm):
    class Meta:
        model = DoctorAvailability
        fields = ["weekday", "start_time", "end_time", "is_active"]
        widgets = {
            "weekday": forms.Select(),
            "start_time": forms.TimeInput(
                format="%H:%M",
                attrs={
                    "type": "time",   # selector nativo de hora
                    "step": 3600,     # 3600s = 1 hora → solo horas en punto
                    # no ponemos min/max para permitir 24h (madrugada incluida)
                },
            ),
            "end_time": forms.TimeInput(
                format="%H:%M",
                attrs={
                    "type": "time",
                    "step": 3600,
                },
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["start_time"].label = "Hora de inicio"
        self.fields["end_time"].label = "Hora de fin"
        self.fields["start_time"].help_text = "Selecciona la hora de inicio (solo horas en punto, formato 24h)."
        self.fields["end_time"].help_text = "Selecciona la hora de fin (solo horas en punto, formato 24h)."

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_time")
        end = cleaned_data.get("end_time")

        # Validar que haya datos
        if not start or not end:
            return cleaned_data

        # 1) La hora de fin debe ser mayor que la de inicio
        if start >= end:
            self.add_error("end_time", "La hora de fin debe ser mayor que la de inicio.")

        # 2) Solo horas en punto (minutos = 0, segundos = 0 si aplica)
        if start.minute != 0 or getattr(start, "second", 0) != 0:
            self.add_error(
                "start_time",
                "La hora de inicio debe ser una hora en punto (por ejemplo 08:00, 14:00, 23:00)."
            )
        if end.minute != 0 or getattr(end, "second", 0) != 0:
            self.add_error(
                "end_time",
                "La hora de fin debe ser una hora en punto (por ejemplo 09:00, 15:00, 00:00)."
            )

        return cleaned_data


class AppointmentSearchForm(forms.Form):
    """
    Paso 1: el paciente elige médico y fecha.
    """
    doctor = forms.ModelChoiceField(
        queryset=User.objects.filter(role=User.Roles.DOCTOR),
        label="Médico",
    )
    date = forms.DateField(
        label="Fecha",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.localdate()
        # Evitar fechas pasadas en el selector
        self.fields["date"].widget.attrs["min"] = today.isoformat()


class AppointmentSlotForm(forms.Form):
    """
    Paso 2: el paciente elige un slot concreto y escribe el motivo.
    """
    slot = forms.ChoiceField(
        label="Horario disponible",
        widget=forms.RadioSelect,  # 👈 aquí el cambio importante
    )
    reason = forms.CharField(
        label="Motivo de la consulta",
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    def __init__(self, *args, **kwargs):
        slots = kwargs.pop("slots", [])
        super().__init__(*args, **kwargs)

        choices = []
        for start, end in slots:
            value = start.isoformat()
            label = f"{start.time().strftime('%H:%M')} - {end.time().strftime('%H:%M')}"
            choices.append((value, label))

        self.fields["slot"].choices = choices

