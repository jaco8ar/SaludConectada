from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models
from django.utils import timezone


User = settings.AUTH_USER_MODEL


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
