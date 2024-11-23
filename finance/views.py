# finance/views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import Payment, Invoice, DoctorEarnings
from .forms import PaymentForm, InvoiceForm  # Forms to be created for adding and editing payments/invoices

def payment_list(request):
    payments = Payment.objects.all()
    return render(request, 'finance/payment_list.html', {'payments': payments})

def invoice_list(request):
    invoices = Invoice.objects.all()
    return render(request, 'finance/invoice_list.html', {'invoices': invoices})

def doctor_earnings_list(request):
    earnings = DoctorEarnings.objects.all()
    return render(request, 'finance/doctor_earnings_list.html', {'earnings': earnings})
