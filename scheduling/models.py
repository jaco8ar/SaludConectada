from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import timedelta
from .video_calls import create_daily_room_for_appointment


User = settings.AUTH_USER_MODEL
APPOINTMENT_SLOT_MINUTES = 20
APPOINTMENT_SLOT_DELTA = timedelta(minutes=APPOINTMENT_SLOT_MINUTES)

class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pendiente"
        CONFIRMED = "CONFIRMED", "Confirmada"
        IN_PROGRESS = "IN_PROGRESS", "En curso"
        COMPLETED = "COMPLETED", "Completada"
        CANCELED = "CANCELED", "Cancelada"

    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="patient_appointments",
    )
    doctor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="doctor_appointments",
    )
    scheduled_datetime = models.DateTimeField("Fecha y hora de la cita")
    reason = models.CharField("Motivo de consulta", max_length=255, blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    canceled_at = models.DateTimeField(null=True, blank=True)

    video_call_url = models.URLField(
        blank=True,
        null=True,
        help_text="Enlace a la sala de videollamada.",
    )

    def ensure_video_call_url(self, save=True):
        """
        Asegura que la cita tiene una sala de videollamada asignada.
        Ahora usa Daily para crearla si no existe.
        """
        if not self.video_call_url:
            url = create_daily_room_for_appointment(self)
            if url:
                self.video_call_url = url
                if save:
                    self.save(update_fields=["video_call_url"])
        return self.video_call_url

    def cancel(self):
        """
        Lógica central de cancelación.
        En el futuro, aquí podremos:
        - Liberar horario del médico.
        - Notificar al paciente/médico.
        - Registrar motivo de cancelación, etc.
        """
        if self.status == self.Status.CANCELED:
            return
        self.status = self.Status.CANCELED
        self.canceled_at = timezone.now()
        self.save()

    def __str__(self):
        return f"Cita {self.id} - {self.patient} con {self.doctor} el {self.scheduled_datetime}"

class DoctorAvailability(models.Model):
    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Lunes"
        TUESDAY = 1, "Martes"
        WEDNESDAY = 2, "Miércoles"
        THURSDAY = 3, "Jueves"
        FRIDAY = 4, "Viernes"
        SATURDAY = 5, "Sábado"
        SUNDAY = 6, "Domingo"

    doctor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="availabilities",
        limit_choices_to={"role": "DOCTOR"},
    )
    weekday = models.IntegerField(choices=Weekday.choices)
    start_time = models.TimeField("Hora inicio")
    end_time = models.TimeField("Hora fin")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Disponibilidad de médico"
        verbose_name_plural = "Disponibilidades de médicos"
        ordering = ("doctor", "weekday", "start_time")

    def __str__(self):
        return f"{self.doctor} - {self.get_weekday_display()} {self.start_time}–{self.end_time}"