from django.shortcuts import render
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required
from accounts.models import User
from scheduling.models import Appointment
from .forms import PatientMedicalRecordForm, DoctorConsultationForm
from .models import MedicalRecord, Consultation


@role_required(User.Roles.PATIENT)
def patient_medical_record(request):
    """
    El paciente crea/edita su propio historial médico (CU003).
    """
    record, _ = MedicalRecord.objects.get_or_create(patient=request.user)

    if request.method == "POST":
        form = PatientMedicalRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, "Historial médico actualizado.")
            return redirect("clinical:patient_medical_record")
    else:
        form = PatientMedicalRecordForm(instance=record)

    return render(request, "clinical/patient_medical_record.html", {"form": form})


@role_required(User.Roles.DOCTOR)
def doctor_patient_record(request, appointment_id):
    """
    El médico ve el historial del paciente de una cita concreta (CU010/CU011).
    Solo si la cita es suya.
    """
    appointment = get_object_or_404(Appointment, pk=appointment_id)

    if appointment.doctor_id != request.user.id:
        raise PermissionDenied()

    record, _ = MedicalRecord.objects.get_or_create(patient=appointment.patient)

    context = {
        "appointment": appointment,
        "record": record,
    }
    return render(request, "clinical/doctor_patient_record.html", context)


@role_required(User.Roles.DOCTOR)
def manage_consultation(request, appointment_id):
    """
    El médico registra notas y recomendaciones de la consulta.
    """
    appointment = get_object_or_404(Appointment, pk=appointment_id)

    if appointment.doctor_id != request.user.id:
        raise PermissionDenied()

    consultation, _ = Consultation.objects.get_or_create(appointment=appointment)

    if request.method == "POST":
        form = DoctorConsultationForm(request.POST, instance=consultation)
        if form.is_valid():
            form.save()
            # Marcamos la cita como completada (simplificación del flujo CU006)
            from scheduling.models import Appointment as Appt
            if appointment.status != Appt.Status.CANCELED:
                appointment.status = Appt.Status.COMPLETED
                appointment.save()
            messages.success(request, "Consulta guardada correctamente.")
            return redirect("scheduling:doctor_appointments")
    else:
        form = DoctorConsultationForm(instance=consultation)

    context = {
        "appointment": appointment,
        "form": form,
    }
    return render(request, "clinical/manage_consultation.html", context)


@role_required(User.Roles.PATIENT, User.Roles.DOCTOR)
def video_call_placeholder(request, appointment_id):
    """
    Placeholder visual y de código para la videollamada (CU006/CU007).
    Solo pueden entrar el paciente y el médico de la cita.
    """
    appointment = get_object_or_404(Appointment, pk=appointment_id)

    user = request.user
    if user.id not in (appointment.patient_id, appointment.doctor_id):
        raise PermissionDenied()

    # Aquí en el futuro integraríamos el proveedor real de videollamada.
    # Por ahora solo mostramos una pantalla simulada.
    context = {
        "appointment": appointment,
    }
    return render(request, "clinical/video_call.html", context)

