from django.conf import settings
from django.db import models
from django.utils import timezone
from departments.models import Service, DoctorProfile
from appointments.models import Appointment


class DoctorEarnings(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='earnings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='doctor_earnings')
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='doctor_earnings')
    earnings_date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Earnings for Dr. {self.doctor.user.get_full_name()} - {self.amount}"
    

