from django.urls import path
from . import views

urlpatterns = [
    path('payments/', views.payment_list, name='payment_list'),
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('doctor-earnings/', views.doctor_earnings_list, name='doctor_earnings_list'),
]
