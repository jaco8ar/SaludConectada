from django.urls import path

from . import views

app_name = "scheduling"

urlpatterns = [
    path("paciente/citas/", views.patient_appointments, name="patient_appointments"),
    path("medico/citas/", views.doctor_appointments, name="doctor_appointments"),
    path("citas/<int:pk>/cancelar/", views.cancel_appointment, name="cancel_appointment"),
    path("medico/disponibilidad/", views.doctor_availability, name="doctor_availability"),
    path(
        "medico/disponibilidad/<int:pk>/eliminar/",
        views.delete_doctor_availability,
        name="delete_doctor_availability",
    ),
]
