from django.test import TestCase
from .models import Patient, Prescription, PatientMedicalHistory, PatientInsurance
from django.contrib.auth import get_user_model

User = get_user_model()

class SimplifiedModelTests(TestCase):
    def setUp(self):
        # Create a Patient instance
        self.patient = Patient.objects.create(
            first_name="John",
            last_name="Doe",
            date_of_birth="1990-01-01",
            gender="M",
            contact_number="1234567890",
        )

        # Mock user (doctor)
        self.doctor = User.objects.create_user(
            email="doctor@example.com",
            password="securepassword",
            first_name="Jane",
            last_name="Smith",
        )

    def test_patient_creation(self):
        """Test creation of Patient instance"""
        self.assertEqual(Patient.objects.count(), 1)
        self.assertEqual(str(self.patient), "John Doe (1234567890)")

    def test_prescription_creation(self):
        """Test creation of Prescription instance"""
        # Create Prescription with minimal fields
        prescription = Prescription.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            medication="Paracetamol",
            dosage="500mg twice a day",
        )
        self.assertEqual(Prescription.objects.count(), 1)
        self.assertEqual(prescription.medication, "Paracetamol")
        self.assertEqual(prescription.dosage, "500mg twice a day")

    def test_medical_history_creation(self):
        """Test creation of PatientMedicalHistory instance"""
        # Create Medical History with minimal fields
        medical_history = PatientMedicalHistory.objects.create(
            patient=self.patient,
            condition="Hypertension",
            diagnosis_date="2020-01-01",
        )
        self.assertEqual(PatientMedicalHistory.objects.count(), 1)
        self.assertEqual(medical_history.condition, "Hypertension")

    def test_insurance_creation(self):
        """Test creation of PatientInsurance instance"""
        # Create Insurance with minimal fields
        insurance = PatientInsurance.objects.create(
            patient=self.patient,
            provider_name="Health Insurance Co.",
            policy_number="POL123456",
            coverage_start_date="2023-01-01",
            coverage_end_date="2024-01-01",
        )
        self.assertEqual(PatientInsurance.objects.count(), 1)
        self.assertEqual(insurance.provider_name, "Health Insurance Co.")
