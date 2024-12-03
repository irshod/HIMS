from django.test import TestCase
from decimal import Decimal
from .models import Department, Service, Floor, Room, Bed
from main.models import CustomUser
from patient.models import Patient


class DepartmentModelTests(TestCase):
    def setUp(self):
        # Basic setup
        self.department = Department.objects.create(name="Cardiology")
        self.service = Service.objects.create(name="ECG", price=Decimal("100.00"))
        self.patient = Patient.objects.create(first_name="John", last_name="Doe", date_of_birth="1990-01-01")
        self.doctor = CustomUser.objects.create(email="doctor@example.com", first_name="Jane", last_name="Smith")
        self.nurse = CustomUser.objects.create(email="nurse@example.com", first_name="Anna", last_name="Taylor")

    def test_department_creation(self):
        self.assertEqual(Department.objects.count(), 1)
        self.assertEqual(self.department.name, "Cardiology")

    def test_service_creation(self):
        self.assertEqual(Service.objects.count(), 1)
        self.assertEqual(self.service.name, "ECG")
        self.assertEqual(self.service.price, Decimal("100.00"))

    def test_floor_creation(self):
        floor = Floor.objects.create(floor_number=1, description="First Floor")
        self.assertEqual(Floor.objects.count(), 1)
        self.assertEqual(floor.floor_number, 1)

    def test_room_creation(self):
        floor = Floor.objects.create(floor_number=1)
        room = Room.objects.create(
            name="Room 101",
            room_number=101,
            room_type="general",
            floor=floor,
            department=self.department,
        )
        self.assertEqual(Room.objects.count(), 1)
        self.assertEqual(room.room_number, 101)
        self.assertEqual(room.department.name, "Cardiology")

    def test_bed_creation(self):
        floor = Floor.objects.create(floor_number=1)
        room = Room.objects.create(
            name="Room 101",
            room_number=101,
            room_type="general",
            floor=floor,
            department=self.department,
        )
        bed = Bed.objects.create(
            bed_number=1,
            room=room,
            status="available",
            price=Decimal("50.00"),
        )
        self.assertEqual(Bed.objects.count(), 1)
        self.assertEqual(bed.status, "available")
        self.assertEqual(bed.price, Decimal("50.00"))
