from django.conf import settings
from django.db import models
from django.utils import timezone
from patient.models import Patient
from departments.models import Service, DoctorProfile
from appointments.models import Appointment

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    method = models.CharField(max_length=50)  # e.g., cash, credit card, insurance

    def __str__(self):
        return f"Payment for {self.patient} - {self.amount} - {self.status}"

class Invoice(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='invoices')
    invoice_date = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Invoice for {self.patient} - Total: {self.total_amount} - Paid: {self.paid}"

class DoctorEarnings(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='earnings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='doctor_earnings')
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='doctor_earnings')
    earnings_date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Earnings for Dr. {self.doctor.user.get_full_name()} - {self.amount}"
    
class Salary(models.Model):
    STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Unpaid', 'Unpaid'),
        ('Partial', 'Partial'),
    ]

    staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='salaries')
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    bonuses = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True)
    per_patient_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True)
    percentage_per_consultation = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, blank=True, null=True)
    total_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_patients_admitted = models.IntegerField(default=0, blank=True, null=True)
    total_consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True)
    payment_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Unpaid')
    payment_date = models.DateTimeField(blank=True, null=True)

    def calculate_total_salary(self):
        """Calculate total salary including bonuses, patient-related earnings, and percentages."""
        patient_earnings = self.per_patient_rate * self.total_patients_admitted if self.per_patient_rate else 0.00
        consultation_earnings = (self.percentage_per_consultation / 100) * self.total_consultation_fee if self.percentage_per_consultation else 0.00
        self.total_salary = self.base_salary + (self.bonuses or 0.00) + patient_earnings + consultation_earnings
        self.save(update_fields=['total_salary'])

    def __str__(self):
        return f"Salary for {self.staff.get_full_name()} - {self.payment_status}"


class SalaryConfiguration(models.Model):
    staff = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='salary_configuration')
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    bonuses = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True)
    per_patient_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True)
    percentage_per_consultation = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, blank=True, null=True)

    def __str__(self):
        return f"Salary Configuration for {self.staff.get_full_name()}"
