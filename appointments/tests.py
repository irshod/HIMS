from django.test import TestCase
from decimal import Decimal
from django.utils.timezone import now
from .models import Appointment, IPDAdmission, Invoice, Payment, TreatmentHistory
from departments.models import Department
from patient.models import Patient
from main.models import CustomUser


class AppointmentModelTests(TestCase):
    def setUp(self):
        # Create basic instances for testing
        self.department = Department.objects.create(name="Cardiology")
        self.patient = Patient.objects.create(first_name="John", last_name="Doe", date_of_birth="1990-01-01")
        self.doctor = CustomUser.objects.create(
            email="doctor@example.com",
            first_name="Jane",
            last_name="Smith",
            is_active=True
        )

    def test_create_appointment(self):
        # Test creating an Appointment
        appointment = Appointment.objects.create(
            patient=self.patient,
            department=self.department,
            doctor=self.doctor,
            appointment_date=now(),
            status="pending"
        )
        self.assertEqual(Appointment.objects.count(), 1)
        self.assertEqual(appointment.status, "pending")

    def test_calculate_total_cost(self):
        # Test total cost calculation for an appointment
        appointment = Appointment.objects.create(
            patient=self.patient,
            department=self.department,
            doctor=self.doctor,
            appointment_date=now(),
            status="pending"
        )
        self.assertEqual(appointment.total_cost, Decimal("0.00"))  # Initial cost should be 0

    def test_create_invoice(self):
        # Test creating an Invoice
        appointment = Appointment.objects.create(
            patient=self.patient,
            department=self.department,
            doctor=self.doctor,
            appointment_date=now(),
            status="pending"
        )
        invoice = Invoice.objects.create(appointment=appointment, total_amount=Decimal("300.00"))
        self.assertEqual(Invoice.objects.count(), 1)
        self.assertEqual(invoice.total_amount, Decimal("300.00"))

    def test_payment_creation(self):
        # Test creating a Payment and checking outstanding balance
        appointment = Appointment.objects.create(
            patient=self.patient,
            department=self.department,
            doctor=self.doctor,
            appointment_date=now(),
            status="pending"
        )
        invoice = Invoice.objects.create(appointment=appointment, total_amount=Decimal("500.00"))
        Payment.objects.create(invoice=invoice, amount=Decimal("200.00"), payment_method="cash")
        self.assertEqual(invoice.outstanding_balance(), Decimal("300.00"))  # 500 - 200 = 300

    def test_ipd_admission(self):
        # Test creating an IPD Admission
        ipd_admission = IPDAdmission.objects.create(
            patient=self.patient,
            department=self.department,
            doctor=self.doctor,
            status="admitted",
            visit_type="IPD"
        )
        self.assertEqual(IPDAdmission.objects.count(), 1)
        self.assertEqual(ipd_admission.status, "admitted")

    def test_treatment_history_creation(self):
        # Test adding treatment notes
        appointment = Appointment.objects.create(
            patient=self.patient,
            department=self.department,
            doctor=self.doctor,
            appointment_date=now(),
            status="pending"
        )
        treatment = TreatmentHistory.objects.create(
            appointment=appointment,
            doctor=self.doctor,
            treatment_notes="Prescribed medication and rest."
        )
        self.assertEqual(TreatmentHistory.objects.count(), 1)
        self.assertEqual(treatment.treatment_notes, "Prescribed medication and rest.")
