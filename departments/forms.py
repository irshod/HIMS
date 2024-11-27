from django import forms
from .models import Service, Department, DoctorProfile, NurseProfile
from main.models import CustomUser
from .models import Floor, Room, Bed
from patient.models import Patient

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'price', 'duration', 'special_notes']

class DepartmentForm(forms.ModelForm):
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'dual-listbox'})
    )
    doctors = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.filter(roles__name='Doctor'),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'dual-listbox'})
    )
    nurses = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.filter(roles__name='Nurse'),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'dual-listbox'})
    )

    class Meta:
        model = Department
        fields = ['name', 'description', 'services', 'doctors', 'nurses']


class DoctorProfileForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=CustomUser.objects.filter(roles__name='Doctor'))
    assigned_services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(), 
        required=False, 
        widget=forms.SelectMultiple(attrs={'class': 'dual-listbox'})
    )

    class Meta:
        model = DoctorProfile
        fields = ['user', 'specialty', 'qualification', 'employment_type', 'base_salary', 'salary_per_service', 'assigned_services']

class NurseProfileForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=CustomUser.objects.filter(roles__name='Nurse'))
    assigned_services = forms.ModelMultipleChoiceField(queryset=Service.objects.all(), required=False, widget=forms.SelectMultiple)

    class Meta:
        model = NurseProfile
        fields = ['user', 'qualification', 'shift', 'hourly_rate', 'assigned_services']



class FloorForm(forms.ModelForm):
    class Meta:
        model = Floor
        fields = ['floor_number', 'description']
        widgets = {
            'floor_number': forms.NumberInput(attrs={
                'placeholder': 'Enter floor number',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Enter a brief description of the floor',
                'class': 'form-control'
            }),
        }
        labels = {
            'floor_number': 'Floor Number',
            'description': 'Description',
        }


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'room_type', 'floor', 'department', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter a brief description of the room'}),
        }
        labels = {
            'name': 'Room Name',
            'room_type': 'Room Type',
            'floor': 'Floor',
            'department': 'Department',
            'description': 'Description',
        }


class BedForm(forms.ModelForm):
    current_patient = forms.ModelChoiceField(
        queryset=None,  # Will be overridden in the form initialization
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Bed
        fields = ['bed_number', 'room', 'status', 'current_patient']
        widgets = {
            'bed_number': forms.TextInput(attrs={'placeholder': 'Enter Bed Number'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'bed_number': 'Bed Number',
            'room': 'Room',
            'status': 'Status',
            'current_patient': 'Assigned Patient (IPD Only)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['current_patient'].queryset = Patient.objects.filter(patient_type='IPD')
