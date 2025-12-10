from django import forms

from .models import MedicalRecord, Consultation


class PatientMedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = (
            "blood_type",
            "allergies",
            "chronic_conditions",
            "medications",
            "notes",
        )


class DoctorConsultationForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = ("doctor_notes", "recommendations")
        widgets = {
            "doctor_notes": forms.Textarea(attrs={"rows": 4}),
            "recommendations": forms.Textarea(attrs={"rows": 4}),
        }
