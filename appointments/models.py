from django.db import models
from django.conf import settings
from departments.models import Service
from inventory.models import Medication, Consumable

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
        ('opd', 'Outpatient'),
        ('ipd', 'Inpatient'),
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

    def mark_as_paid(self):
        self.payment_status = 'paid'
        self.save(update_fields=['payment_status'])

    def mark_as_active(self):
        self.status = 'active'
        self.save(update_fields=['status'])

    def mark_as_completed(self):
        self.status = 'completed'
        self.save(update_fields=['status'])

    def add_service(self, service_id):
        service = Service.objects.get(id=service_id)
        self.services.add(service)
        self.total_cost += service.price
        self.save(update_fields=["total_cost"])

    def save(self, *args, **kwargs):
        # Ensure the instance has a primary key
        is_new = self.pk is None
        super().save(*args, **kwargs)
        # Calculate total cost only after saving for the first time
        if is_new:
            self.total_cost = sum(service.price for service in self.services.all())
            super().save(update_fields=["total_cost"])

    def __str__(self):
        return f"Appointment #{self.id} for {self.patient.first_name} {self.patient.last_name}"


class Invoice(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='invoice')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=[('paid', 'Paid'), ('unpaid', 'Unpaid')], default='unpaid')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice #{self.id} for Appointment #{self.appointment.id}"


class TreatmentHistory(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='treatment_history')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='treatment_history')
    date = models.DateTimeField(auto_now_add=True)
    treatment_notes = models.TextField(help_text="Notes on treatment and procedures performed")
    medications = models.ManyToManyField(Medication, through='TreatmentMedication')
    consumables = models.ManyToManyField(Consumable, through='TreatmentConsumable')

    def __str__(self):
        return f"Treatment for Appointment #{self.appointment.id} on {self.date.strftime('%Y-%m-%d')}"


class TreatmentMedication(models.Model):
    treatment_history = models.ForeignKey(TreatmentHistory, on_delete=models.CASCADE, related_name='treatment_medications')
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.medication.unit_price
        super().save(*args, **kwargs)
        if not self.pk:  # Deduct stock only on initial save
            self.medication.quantity -= self.quantity
            self.medication.save()

    def __str__(self):
        return f"{self.quantity} x {self.medication.name} for Treatment #{self.treatment_history.id}"


class TreatmentConsumable(models.Model):
    treatment_history = models.ForeignKey(TreatmentHistory, on_delete=models.CASCADE, related_name='treatment_consumables')
    consumable = models.ForeignKey(Consumable, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.consumable.unit_price
        super().save(*args, **kwargs)
        if not self.pk:  # Deduct stock only on initial save
            self.consumable.quantity -= self.quantity
            self.consumable.save()

    def __str__(self):
        return f"{self.quantity} x {self.consumable.name} for Treatment #{self.treatment_history.id}"
