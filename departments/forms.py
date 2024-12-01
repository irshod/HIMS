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
        fields = ['name', 'room_number', 'room_type', 'floor', 'department', 'description']


class BedForm(forms.ModelForm):
    # Remove `current_patient` from the form fields
    class Meta:
        model = Bed
        fields = ['bed_number', 'room', 'status']
        widgets = {
            'bed_number': forms.TextInput(attrs={'placeholder': 'Enter Bed Number'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'bed_number': 'Bed Number',
            'room': 'Room',
            'status': 'Status',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter room options dynamically based on floor or other logic if needed
        if 'room' in self.fields:
            self.fields['room'].queryset = Room.objects.all()

