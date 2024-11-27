from django.db import models
from django.conf import settings
from appointments.models import Appointment

class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    contact_number = models.CharField(max_length=15, unique=True)
    address = models.TextField(blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True, null=True)
    emergency_contact_number = models.CharField(max_length=15, blank=True, null=True)
    emergency_contact_email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.contact_number})"


class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prescriptions')
    appointment = models.ForeignKey('appointments.Appointment', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    medication = models.TextField(help_text="Enter prescribed medication details")
    dosage = models.CharField(max_length=100, help_text="Dosage instructions")
    recommendations = models.TextField(help_text="Additional treatment recommendations", blank=True, null=True)

    class Meta:
        unique_together = ('patient', 'doctor', 'created_at')

    def __str__(self):
        return f"Prescription for {self.patient.first_name} by Dr. {self.doctor.get_full_name()} on {self.created_at}"

class Diagnosis(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name="diagnoses")
    treatment_notes = models.TextField(help_text="Notes on treatment and procedures performed")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Diagnosis for {self.appointment.patient.first_name} on {self.date}"


class PatientMedicalHistory(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_history')
    condition = models.CharField(max_length=255, help_text="Medical condition or diagnosis")
    description = models.TextField(blank=True, null=True)
    diagnosis_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.condition} for {self.patient.first_name} {self.patient.last_name}"


class PatientInsurance(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='insurance_details')
    provider_name = models.CharField(max_length=100, help_text="Insurance provider name")
    policy_number = models.CharField(max_length=50, help_text="Insurance policy number")
    coverage_start_date = models.DateField()
    coverage_end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Insurance for {self.patient.first_name} by {self.provider_name}"
