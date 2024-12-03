from django.db import models
from main.models import CustomUser

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    services = models.ManyToManyField('Service', related_name='departments', blank=True)
    doctors = models.ManyToManyField(
        CustomUser,
        related_name='departments_as_doctor',
        limit_choices_to={'roles__name': 'Doctor'},
        blank=True
    )
    nurses = models.ManyToManyField(
        CustomUser,
        related_name='departments_as_nurse',
        limit_choices_to={'roles__name': 'Nurse'},
        blank=True
    )

    def __str__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.DurationField(blank=True, null=True)
    special_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class DoctorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='doctor_profile')
    specialty = models.CharField(max_length=100)
    qualification = models.CharField(max_length=100)
    employment_type = models.CharField(max_length=20, choices=[('Full-time', 'Full-time'), ('Part-time', 'Part-time')])
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_per_service = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    assigned_services = models.ManyToManyField(Service, related_name='doctors', blank=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.specialty}"

  
class NurseProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='nurse_profile')
    qualification = models.CharField(max_length=100)
    shift = models.CharField(max_length=50, choices=[('Day', 'Day'), ('Night', 'Night')])
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    assigned_services = models.ManyToManyField(Service, related_name='nurses', blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - Nurse"
    
class StaffAvailability(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('unavailable', 'Unavailable'),
        ('vacation', 'Vacation'),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='staffavailability')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.status}"



class Floor(models.Model):
    floor_number = models.IntegerField(unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Floor {self.floor_number}"

    def get_rooms(self):
        return self.rooms.all()

class Room(models.Model):
    ROOM_TYPE_CHOICES = [
        ('general', 'General Ward'),
        ('private', 'Private Room'),
        ('icu', 'ICU'),
    ]

    name = models.CharField(max_length=100)
    room_number = models.IntegerField()
    room_type = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES, default='general')
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='rooms')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='rooms')
    description = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('floor', 'room_number')

    def __str__(self):
        return f"Room {self.room_number} ({self.get_room_type_display()}) on Floor {self.floor.floor_number}"


class Bed(models.Model):
    bed_number = models.IntegerField()
    BED_STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Maintenance'),
    ]

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='beds')
    status = models.CharField(max_length=15, choices=BED_STATUS_CHOICES, default='available')
    current_patient = models.OneToOneField(
        'patient.Patient',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bed'
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    class Meta:
        unique_together = ('room', 'bed_number')

    def mark_as_occupied(self):
        self.status = 'occupied'
        self.save(update_fields=['status'])

    def mark_as_available(self):
        self.status = 'available'
        self.save(update_fields=['status'])

    def save(self, *args, **kwargs):
        self.clean()  # Validate before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Bed {self.bed_number} in Room {self.room.name} ({self.get_status_display()}) - Price: {self.price}"


