from django.urls import path
from . import views

urlpatterns = [
    path('payments/', views.payment_report, name='payment_report'),
    path('invoices/', views.invoice_summary, name='invoice_summary'),
    path('doctor-earnings/', views.doctor_earnings_report, name='doctor_earnings_report'),
]
