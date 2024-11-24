from django import forms
from django.contrib.auth import get_user_model
from departments.models import Department, Service
from inventory.models import Medication, Consumable
from .models import Appointment, Invoice, Payment, TreatmentHistory

User = get_user_model()

# Appointment Form
class AppointmentForm(forms.ModelForm):
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Appointment
        fields = ['patient', 'department', 'doctor', 'appointment_date', 'appointment_type']
        widgets = {
            'appointment_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'appointment_type': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'appointment_date': 'Date & Time',
            'appointment_type': 'Type',
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


# Add Service Form
class AddServiceForm(forms.Form):
    class Meta:
        model = Service
    service = forms.ModelChoiceField(
        queryset=Service.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Select Service"
    )


# Add Medication Form
class AddMedicationForm(forms.Form):
    medication = forms.ModelChoiceField(
        queryset=Medication.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Select Medication"
    )
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Quantity"
    )


# Add Consumable Form
class AddConsumableForm(forms.Form):
    consumable = forms.ModelChoiceField(
        queryset=Consumable.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Select Consumable"
    )
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Quantity"
    )


# Treatment History Form
class TreatmentHistoryForm(forms.ModelForm):
    class Meta:
        model = TreatmentHistory
        fields = ['treatment_notes']
        widgets = {
            'treatment_notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Enter treatment details'}),
        }
        labels = {
            'treatment_notes': 'Treatment Notes',
        }


# Invoice Form
class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['total_amount']
        widgets = {
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter total amount'}),
        }
        labels = {
            'total_amount': 'Total Amount',
        }


# Payment Form
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter payment amount'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'amount': 'Payment Amount',
            'payment_method': 'Payment Method',
        }
