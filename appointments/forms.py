from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from .models import Appointment, Invoice, Payment, TreatmentConsumable, TreatmentHistory, Medication, IPDAdmission
from departments.models import Bed, Department, Floor, Room, Service
from inventory.models import Medication, Consumable

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
        fields = ['patient', 'department', 'doctor', 'appointment_date']
        widgets = {
            'appointment_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }
        labels = {
            'appointment_date': 'Date & Time',
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

        # Set default date and time
        self.fields['appointment_date'].initial = now().strftime("%Y-%m-%dT%H:%M")

class IPDAdmissionForm(forms.ModelForm):
    class Meta:
        model = IPDAdmission
        fields = ['patient', 'department', 'doctor', 'floor', 'room', 'bed', 'status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'bed': forms.Select(attrs={'class': 'form-control'}),
            'room': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'status': 'Status',
            'bed': 'Bed',
            'room': 'Room',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter beds based on availability
        self.fields['bed'].queryset = Bed.objects.filter(status='available')
        # Filter rooms dynamically based on floor (optional)
        if 'room' in self.fields:
            self.fields['room'].queryset = Room.objects.all()
        # Pre-select status (e.g., "admitted")
        self.fields['status'].initial = 'admitted'
        department = kwargs.get('initial', {}).get('department')
        if department:
            self.fields['floor'].queryset = Floor.objects.filter(department=department)
            self.fields['room'].queryset = Room.objects.filter(floor__department=department)
            self.fields['bed'].queryset = Bed.objects.filter(room__floor__department=department, status='available')
        
    def clean(self):
        cleaned_data = super().clean()
        bed = cleaned_data.get('bed')

        if bed and IPDAdmission.objects.filter(bed=bed, status='admitted').exists():
            raise ValidationError({'bed': 'This bed is already assigned to an admitted patient.'})

        return cleaned_data

class IPDDischargeForm(forms.ModelForm):
    class Meta:
        model = IPDAdmission
        fields = ['discharge_date']
        widgets = {
            'discharge_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }


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
    medicine = forms.ModelChoiceField(
        queryset=Medication.objects.all(),  # Fetch all medications from the inventory
        label="Medicine",
        widget=forms.Select(attrs={'class': 'form-control select2'})  # Enable searchable dropdown
    )
    quantity = forms.IntegerField(
        min_value=1, 
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    def save(self, appointment):
        # Save medication details to the treatment
        medicine = self.cleaned_data['medicine']
        quantity = self.cleaned_data['quantity']
        # Deduct the quantity from inventory
        medicine.quantity -= quantity
        medicine.save()

        # Return medication details for further processing
        return {
            'name': medicine.name,
            'dosage': medicine.dosage,
            'price': medicine.unit_price,
            'quantity': quantity
        }


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

    def save(self, appointment):
        consumable = self.cleaned_data['consumable']
        quantity = self.cleaned_data['quantity']

        # Deduct stock from inventory
        if consumable.quantity < quantity:
            raise ValidationError(f"Not enough stock for {consumable.name}. Available: {consumable.quantity}")
        consumable.quantity -= quantity
        consumable.save()

        # Create a TreatmentConsumable entry
        treatment_history, _ = TreatmentHistory.objects.get_or_create(appointment=appointment)
        treatment_consumable = TreatmentConsumable.objects.create(
            treatment_history=treatment_history,
            consumable=consumable,
            quantity=quantity,
            total_cost=consumable.unit_price * quantity
        )
        return treatment_consumable



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
            'doctor': 'Doctor',
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
