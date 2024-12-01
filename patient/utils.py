from appointments.models import Prescription, PatientMedicalHistory, Diagnosis

def get_patient_history(patient):
    return {
        "prescriptions": Prescription.objects.filter(patient=patient).order_by('-created_at'),
        "medical_histories": PatientMedicalHistory.objects.filter(patient=patient).order_by('-created_at'),
        "diagnoses": Diagnosis.objects.filter(patient=patient).order_by('-created_at'),
    }
