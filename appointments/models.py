from django.db import models
from django.conf import settings
from departments.models import Service
from inventory.models import Medication, Consumable
from django.core.exceptions import ValidationError
from decimal import Decimal

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
    ]
    APPOINTMENT_TYPE_CHOICES = [
        ('IPD', 'Outpatient'),
        ('OPD', 'Inpatient'),
    ]

    patient = models.ForeignKey('patient.Patient', on_delete=models.CASCADE, related_name='appointments')
    department = models.ForeignKey('departments.Department', on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments')
    services = models.ManyToManyField(Service, related_name='appointments')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    appointment_type = models.CharField(max_length=10, choices=APPOINTMENT_TYPE_CHOICES, default='opd')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    appointment_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_total_cost(self):
        """Calculate the total cost of all associated services."""
        if self.id:  # Ensure the object is saved before accessing the ManyToManyField
            self.total_cost = sum(service.price for service in self.services.all())

    def save(self, *args, **kwargs):
        """Override save to calculate total cost."""
        super().save(*args, **kwargs)  # Save first to ensure `id` is assigned
        self.calculate_total_cost()    # Calculate the total cost
        super().save(update_fields=['total_cost'])

    def mark_as_active(self):
        if self.status not in ['pending']:
            raise ValidationError("Can only activate a pending appointment.")
        self.status = 'active'
        self.save(update_fields=['status'])

    def mark_as_completed(self):
        if self.status not in ['active']:
            raise ValidationError("Can only complete an active appointment.")
        self.status = 'completed'
        self.save(update_fields=['status'])

    def mark_as_canceled(self):
        if self.status in ['completed']:
            raise ValidationError("Cannot cancel a completed appointment.")
        self.status = 'canceled'
        self.save(update_fields=['status'])

    def mark_as_paid(self):
        self.payment_status = 'paid'
        self.save(update_fields=['payment_status'])

    def __str__(self):
        return f"Appointment #{self.id} for {self.patient.first_name} {self.patient.last_name}"
    


class Invoice(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='invoice')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_paid(self):
        return sum(payment.amount for payment in self.payments.all())

    def outstanding_balance(self):
        return max(self.total_amount - self.total_paid(), Decimal('0.00'))

    @property
    def status(self):
        if self.outstanding_balance() <= 0:
            return 'paid'
        elif self.total_paid() > 0:
            return 'partial'
        return 'unpaid'
    
    def update_payment_status(self):
        if self.outstanding_balance() == 0:
            self.appointment.payment_status = "paid"
        else:
            self.appointment.payment_status = "unpaid"
        self.appointment.save(update_fields=["payment_status"])


class Payment(models.Model):
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, choices=[('cash', 'Cash'), ('card', 'Card'), ('online', 'Online')])

    def save(self, *args, **kwargs):
        if self.invoice.outstanding_balance() < self.amount:
            raise ValidationError("Payment amount exceeds the outstanding balance.")
        super().save(*args, **kwargs)



class TreatmentHistory(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='treatment_history')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='treatment_history')
    date = models.DateTimeField(auto_now_add=True)
    treatment_notes = models.TextField(help_text="Notes on treatment and procedures performed")
    medications = models.ManyToManyField(Medication, through='TreatmentMedication')
    consumables = models.ManyToManyField(Consumable, through='TreatmentConsumable')

    def add_medication(self, medication, quantity):
        """Add a medication to the treatment."""
        treatment_medication = TreatmentMedication.objects.create(
            treatment_history=self,
            medication=medication,
            quantity=quantity
        )
        return treatment_medication

    def add_consumable(self, consumable, quantity):
        """Add a consumable to the treatment."""
        treatment_consumable = TreatmentConsumable.objects.create(
            treatment_history=self,
            consumable=consumable,
            quantity=quantity
        )
        return treatment_consumable
    

    def __str__(self):
        return f"Treatment for Appointment #{self.appointment.id} on {self.date.strftime('%Y-%m-%d')}"


def validate_and_update_stock(item, quantity):
    if quantity <= 0:
        raise ValidationError("Quantity must be greater than zero.")
    if quantity > item.quantity:
        raise ValidationError(f"Insufficient stock for {item.name}. Available: {item.quantity}")
    item.quantity -= quantity
    item.save()

class TreatmentMedication(models.Model):
    treatment_history = models.ForeignKey(TreatmentHistory, on_delete=models.CASCADE, related_name='treatment_medications')
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        if not self.pk:  # Validate only on creation
            validate_and_update_stock(self.medication, self.quantity)
        self.total_cost = self.quantity * self.medication.unit_price
        super().save(*args, **kwargs)

class TreatmentConsumable(models.Model):
    treatment_history = models.ForeignKey(TreatmentHistory, on_delete=models.CASCADE, related_name='treatment_consumables')
    consumable = models.ForeignKey(Consumable, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        if not self.pk:  # Validate only on creation
            validate_and_update_stock(self.consumable, self.quantity)
        self.total_cost = self.quantity * self.consumable.unit_price
        super().save(*args, **kwargs)
