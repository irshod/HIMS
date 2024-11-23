from django import forms
from django.contrib.auth import get_user_model
from departments.models import Department, Service
from .models import Appointment

User = get_user_model()

class AppointmentForm(forms.ModelForm):
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        required=False,
        widget=forms.SelectMultiple
    )

    class Meta:
        model = Appointment
        fields = ['patient', 'department', 'doctor', 'appointment_date', 'appointment_type']
        widgets = {
            'appointment_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Default queryset for doctors and services
        self.fields['doctor'].queryset = User.objects.filter(roles__name='Doctor', is_active=True)
        self.fields['services'].queryset = Service.objects.none()

        # Dynamically filter doctors and services based on the department
        if 'department' in self.data:
            try:
                department_id = int(self.data.get('department'))
                department = Department.objects.get(id=department_id)
                self.fields['doctor'].queryset = department.doctors.filter(roles__name='Doctor', is_active=True)
                self.fields['services'].queryset = department.services.all()
            except (ValueError, TypeError, Department.DoesNotExist):
                pass
        elif self.instance.pk:
            department = self.instance.department
            self.fields['doctor'].queryset = department.doctors.filter(roles__name='Doctor', is_active=True)
            self.fields['services'].queryset = department.services.all()


