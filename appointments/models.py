from django.db import models
from django.conf import settings
from departments.models import Service
from patient.models import Patient

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

    # Calculate the cost
    def save(self, *args, **kwargs):
        # Save the instance first to ensure it has a primary key
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Calculate total cost only after the instance is saved
        if is_new:
            self.total_cost = sum(service.price for service in self.services.all())
            super().save(update_fields=["total_cost"])



class Invoice(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='invoice')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=[('paid', 'Paid'), ('unpaid', 'Unpaid')], default='unpaid')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice #{self.id} for Appointment #{self.appointment.id}"
