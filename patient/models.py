from django.db import models
from django.conf import settings

class Patient(models.Model):
    PATIENT_TYPE_CHOICES = [
        ('IPD', 'In-Patient'),
        ('OPD', 'Out-Patient'),
    ]
    patient_type = models.CharField(
        max_length=3,
        choices=PATIENT_TYPE_CHOICES,
        default='OPD',
    )
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    contact_number = models.CharField(max_length=15, unique=True)
    address = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.contact_number})"

class IPDMedication(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medications')
    medication = models.ForeignKey('inventory.Medication', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.medication.price_per_unit
        super().save(*args, **kwargs)
        self.medication.stock -= self.quantity
        self.medication.save()

class IPDConsumable(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='consumables')
    consumable = models.ForeignKey('inventory.Consumable', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.consumable.price_per_unit
        super().save(*args, **kwargs)
        self.consumable.stock -= self.quantity
        self.consumable.save()

        

class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prescriptions')
    appointment = models.ForeignKey('appointments.Appointment', on_delete=models.CASCADE, related_name='prescriptions')
    created_at = models.DateTimeField(auto_now_add=True)
    medication = models.TextField(help_text="Enter prescribed medication details")
    dosage = models.CharField(max_length=100, help_text="Dosage instructions")
    recommendations = models.TextField(help_text="Additional treatment recommendations", blank=True, null=True)

    class Meta:
        unique_together = ('patient', 'doctor', 'created_at')

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise ValueError("Updates are not allowed for prescriptions. Create a new record instead.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Prescription for {self.patient.first_name} by Dr. {self.doctor.get_full_name()} on {self.created_at}"

class TreatmentHistory(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='treatment_history')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='treatment_history')
    appointment = models.ForeignKey('appointments.Appointment', on_delete=models.CASCADE, related_name='treatment_history')
    date = models.DateTimeField(auto_now_add=True)
    treatment_notes = models.TextField(help_text="Notes on treatment and procedures performed")

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise ValueError("Updates are not allowed for treatment history. Create a new record instead.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Treatment History for {self.patient.first_name} on {self.date.strftime('%Y-%m-%d')} by Dr. {self.doctor.get_full_name()}"
