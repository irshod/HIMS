from django.core.exceptions import ValidationError

class InventoryManager:
    @staticmethod
    def validate_stock(item, quantity):
        if quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")
        if quantity > item.quantity:
            raise ValidationError(f"Not enough stock for {item.name}. Available: {item.quantity}.")

    @staticmethod
    def deduct_stock(item, quantity):
        InventoryManager.validate_stock(item, quantity)
        item.quantity -= quantity
        item.save(update_fields=['quantity'])

    @staticmethod
    def replenish_stock(item, quantity):
        if quantity <= 0:
            raise ValidationError("Replenishment quantity must be greater than zero.")
        item.quantity += quantity
        item.save(update_fields=['quantity'])