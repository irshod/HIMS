from django import forms
from .models import Payment, Invoice

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['patient', 'appointment', 'amount', 'status', 'method']

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['patient', 'appointment', 'total_amount', 'paid']