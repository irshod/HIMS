from django import forms
from .models import Service, Department, DoctorProfile, NurseProfile
from main.models import CustomUser


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