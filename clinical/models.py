from django.conf import settings
from django.db import models

from scheduling.models import Appointment  # vínculo con citas


User = settings.AUTH_USER_MODEL


class MedicalRecord(models.Model):
    patient = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="medical_record",
    )
    blood_type = models.CharField("Tipo de sangre", max_length=5, blank=True)
    allergies = models.TextField("Alergias", blank=True)
    chronic_conditions = models.TextField("Enfermedades crónicas", blank=True)
    medications = models.TextField("Medicamentos actuales", blank=True)
    notes = models.TextField("Notas adicionales", blank=True)

    def __str__(self):
        return f"Historial médico de {self.patient}"


class Consultation(models.Model):
    """
    Representa la consulta asociada a una cita específica.
    """
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name="consultation",
    )
    doctor_notes = models.TextField("Notas del médico", blank=True)
    recommendations = models.TextField("Recomendaciones / tratamiento", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Consulta para cita {self.appointment_id}"

