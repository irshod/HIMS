from django import forms
from .models import Patient, PatientMedicalHistory, PatientInsurance, Prescription

class PatientRegistrationForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender',
            'contact_number', 'address',
            'emergency_contact_name', 'emergency_contact_relationship',
            'emergency_contact_number', 'emergency_contact_email',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Enter address'}),
            'emergency_contact_relationship': forms.TextInput(attrs={'placeholder': 'e.g., Parent, Sibling'}),
        }
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'date_of_birth': 'Date of Birth',
            'gender': 'Gender',
            'contact_number': 'Contact Number',
            'address': 'Address',
            'emergency_contact_name': 'Emergency Contact Name',
            'emergency_contact_relationship': 'Relationship',
            'emergency_contact_number': 'Emergency Contact Number',
            'emergency_contact_email': 'Emergency Contact Email',
        }




class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['medication', 'dosage', 'recommendations']
        widgets = {
            'medication': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Enter medication details (e.g., Paracetamol 500mg)',
                'class': 'form-control'
            }),
            'dosage': forms.TextInput(attrs={
                'placeholder': 'e.g., Take 1 tablet every 8 hours',
                'class': 'form-control'
            }),
            'recommendations': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Additional treatment recommendations (e.g., avoid alcohol)',
                'class': 'form-control'
            }),
        }
        labels = {
            'medication': 'Medication Details',
            'dosage': 'Dosage Instructions',
            'recommendations': 'Additional Recommendations',
        }



class PatientMedicalHistoryForm(forms.ModelForm):
    class Meta:
        model = PatientMedicalHistory
        fields = ['condition', 'description', 'diagnosis_date']
        widgets = {
            'diagnosis_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Additional details about the condition'}),
        }


class PatientInsuranceForm(forms.ModelForm):
    class Meta:
        model = PatientInsurance
        fields = ['provider_name', 'policy_number', 'coverage_start_date', 'coverage_end_date']
        widgets = {
            'coverage_start_date': forms.DateInput(attrs={'type': 'date'}),
            'coverage_end_date': forms.DateInput(attrs={'type': 'date'}),
        }
