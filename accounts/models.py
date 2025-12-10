from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    class Roles(models.TextChoices):
        PATIENT = "PATIENT", "Paciente"
        DOCTOR = "DOCTOR", "Médico"
        ADMIN = "ADMIN", "Administrador"

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.PATIENT,
        help_text="Rol del usuario en la plataforma",
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
