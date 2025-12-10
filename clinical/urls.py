from django.urls import path

from . import views

app_name = "clinical"

urlpatterns = [
    path(
        "paciente/historial/",
        views.patient_medical_record,
        name="patient_medical_record",
    ),
    path(
        "medico/citas/<int:appointment_id>/historial/",
        views.doctor_patient_record,
        name="doctor_patient_record",
    ),
    path(
        "medico/citas/<int:appointment_id>/consulta/",
        views.manage_consultation,
        name="manage_consultation",
    ),
    path(
        "citas/<int:appointment_id>/videollamada/",
        views.video_call_placeholder,
        name="video_call",
    ),
]
