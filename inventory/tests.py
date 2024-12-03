from django.test import TestCase
from .models import Medication, Consumable

class InventoryModelTest(TestCase):
    def test_medication_creation(self):
        # Create a Medication instance
        medication = Medication.objects.create(
            name="Paracetamol",
            dosage="500mg",
            quantity=20,
            reorder_level=10,
            unit_price=1.50
        )
        self.assertEqual(Medication.objects.count(), 1)
        self.assertEqual(str(medication), "Paracetamol (500mg)")
        self.assertFalse(medication.is_low_stock())  # Stock is above reorder level

    def test_consumable_creation(self):
        # Create a Consumable instance
        consumable = Consumable.objects.create(
            name="Syringe",
            quantity=5,
            reorder_level=10,
            unit_price=0.75
        )
        self.assertEqual(Consumable.objects.count(), 1)
        self.assertEqual(str(consumable), "Syringe")
        self.assertTrue(consumable.is_low_stock())  # Stock is below reorder level
