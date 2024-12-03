from django.db import models

class Medication(models.Model):
    name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=50, null=True, blank=True) 
    quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=10)  # Low-stock threshold
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.dosage})" if self.dosage else self.name

    def is_low_stock(self):
        return self.quantity <= self.reorder_level


class Consumable(models.Model):
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=10)  # Low-stock threshold
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name

    def is_low_stock(self):
        return self.quantity <= self.reorder_level
