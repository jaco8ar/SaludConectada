from django.shortcuts import render

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required
from accounts.models import User
from .forms import PatientAppointmentForm
from .models import Appointment


@role_required(User.Roles.PATIENT)
def patient_appointments(request):
    """
    El paciente ve sus citas y puede crear nuevas.
    Más adelante podríamos separar la creación en otra vista.
    """
    appointments = (
        Appointment.objects
        .filter(patient=request.user)
        .order_by("-scheduled_datetime")
    )

    if request.method == "POST":
        form = PatientAppointmentForm(request.POST)
        if form.is_valid():
            form.save(patient=request.user)
            messages.success(request, "Cita creada correctamente.")
            return redirect("scheduling:patient_appointments")
    else:
        form = PatientAppointmentForm()

    context = {
        "appointments": appointments,
        "form": form,
    }
    return render(request, "scheduling/patient_appointments.html", context)


@role_required(User.Roles.DOCTOR)
def doctor_appointments(request):
    """
    El médico ve las citas en las que participa como doctor.
    """
    appointments = (
        Appointment.objects
        .filter(doctor=request.user)
        .order_by("-scheduled_datetime")
    )

    context = {
        "appointments": appointments,
    }
    return render(request, "scheduling/doctor_appointments.html", context)


@role_required(User.Roles.PATIENT, User.Roles.DOCTOR, User.Roles.ADMIN)
def cancel_appointment(request, pk):
    """
    Paciente, Médico o Admin pueden cancelar la cita.
    Regla mínima: 
    - Paciente solo cancela si es su cita.
    - Médico solo cancela si es su cita.
    - Admin puede cancelar cualquier cita.
    """
    appointment = get_object_or_404(Appointment, pk=pk)

    user: User = request.user
    # Paciente solo si es su cita
    if user.role == User.Roles.PATIENT and appointment.patient_id != user.id:
        raise PermissionDenied()
    # Médico solo si es su cita
    if user.role == User.Roles.DOCTOR and appointment.doctor_id != user.id:
        raise PermissionDenied()
    # Admin puede siempre

    appointment.cancel()
    messages.success(request, "La cita ha sido cancelada.")
    # Redirigimos según rol
    if user.role == User.Roles.DOCTOR:
        return redirect("scheduling:doctor_appointments")
    elif user.role == User.Roles.PATIENT:
        return redirect("scheduling:patient_appointments")
    else:
        # Admin: por ahora, al home
        return redirect("accounts:home")

