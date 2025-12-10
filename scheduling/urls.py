from django.urls import path

from . import views

app_name = "scheduling"

urlpatterns = [
    path("paciente/citas/", views.patient_appointments, name="patient_appointments"),
    path("medico/citas/", views.doctor_appointments, name="doctor_appointments"),
    path("citas/<int:pk>/cancelar/", views.cancel_appointment, name="cancel_appointment"),
]
