from django.urls import path

from . import views

app_name = "scheduling"

urlpatterns = [
    path("paciente/citas/", views.patient_appointments, name="patient_appointments"),
    path("paciente/citas/nueva/", views.new_appointment_step1, name="new_appointment_step1"),
    path("paciente/citas/nueva/slots/", views.new_appointment_step2, name="new_appointment_step2"),
    path("medico/citas/", views.doctor_appointments, name="doctor_appointments"),
    path("citas/<int:pk>/cancelar/", views.cancel_appointment, name="cancel_appointment"),
    path("medico/disponibilidad/", views.doctor_availability, name="doctor_availability"),
    path(
        "medico/disponibilidad/<int:pk>/eliminar/",
        views.delete_doctor_availability,
        name="delete_doctor_availability",
    ),
    path(
        "citas/<int:appointment_id>/videollamada/",
        views.appointment_video_call,
        name="appointment_video_call",
    ),
]
