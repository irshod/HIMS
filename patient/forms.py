from django import forms
from .models import Patient, Prescription, TreatmentHistory

class PatientRegistrationForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender',
            'contact_number', 'address', 'emergency_contact', 'email',
            'patient_type',  
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'date_of_birth': 'Date of Birth',
            'gender': 'Gender',
            'contact_number': 'Contact Number',
            'address': 'Address',
            'emergency_contact': 'Emergency Contact Number',
            'email': 'Email Address',
        }

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['medication', 'dosage', 'recommendations']
        widgets = {
            'medication': forms.Textarea(attrs={'rows': 3}),
            'recommendations': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'medication': 'Medication Details',
            'dosage': 'Dosage Instructions',
            'recommendations': 'Treatment Recommendations',
        }

class TreatmentHistoryForm(forms.ModelForm):
    class Meta:
        model = TreatmentHistory
        fields = ['treatment_notes']
        widgets = {
            'treatment_notes': forms.Textarea(attrs={'rows': 5}),
        }
        labels = {
            'treatment_notes': 'Treatment Notes',
        }
