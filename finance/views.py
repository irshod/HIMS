from django.shortcuts import render
from django.core.paginator import Paginator
from departments.models import DoctorProfile
from appointments.models import Appointment, Invoice, Payment
from django.db.models import Sum

def payment_report(request):
    payments_list = Payment.objects.select_related(
        'invoice__appointment__patient'
    ).all()

    paginator = Paginator(payments_list, 10)  
    page_number = request.GET.get('page')
    payments = paginator.get_page(page_number)

    total_revenue = payments_list.aggregate(total=Sum('amount'))['total']

    return render(request, 'finance/payment_report.html', {
        'payments': payments,
        'total_revenue': total_revenue,
    })

def invoice_summary(request):
    invoices = Invoice.objects.all()
    unpaid_invoices = invoices.filter(appointment__payment_status='unpaid').count()
    total_outstanding = sum(invoice.outstanding_balance() for invoice in invoices)

    return render(request, 'finance/invoice_summary.html', {
        'invoices': invoices,
        'unpaid_invoices': unpaid_invoices,
        'total_outstanding': total_outstanding,
    })

def doctor_earnings_report(request):
    earnings = []
    doctors = DoctorProfile.objects.select_related('user').all()

    for doctor in doctors:
        appointments = Appointment.objects.filter(doctor=doctor.user)

        total_earnings = sum(
            service.price for appointment in appointments for service in appointment.services.all()
        )
        earnings.append({'doctor': doctor, 'total_earnings': total_earnings})

    return render(request, 'finance/doctor_earnings_report.html', {'earnings': earnings})

