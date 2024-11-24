from django.urls import path
from . import views

urlpatterns = [
    # Appointment Management
    path('', views.appointments_list, name='appointments_list'),
    path('add/', views.create_appointment, name='create_appointment'),
    path('<int:appointment_id>/', views.view_appointment, name='view_appointment'),
    path('<int:appointment_id>/start/', views.start_appointment, name='start_appointment'),
    path('<int:appointment_id>/awaiting_test/', views.mark_awaiting_test, name='mark_awaiting_test'),
    path('<int:appointment_id>/complete/', views.complete_appointment, name='complete_appointment'),
    path('<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('<int:appointment_id>/add-service/', views.add_service_to_appointment, name='add_service_to_appointment'),
    path('<int:appointment_id>/add-medication/', views.add_medication_to_treatment, name='add_medication_to_treatment'),
    path('<int:appointment_id>/add-consumable/', views.add_consumable_to_treatment, name='add_consumable_to_treatment'),
    path('<int:appointment_id>/add-notes/', views.add_treatment_notes, name='add_treatment_notes'),

    # Invoice and Payment Management
    path('appointments/<int:appointment_id>/generate_invoice/', views.generate_invoice, name='generate_invoice'),
    path('appointments/<int:appointment_id>/generate_pdf/', views.generate_pdf_invoice, name='generate_pdf_invoice'),
    path('appointments/<int:invoice_id>/process_payment/', views.process_payment, name='process_payment'),

    # Calendar View
    path('calendar/', views.calendar_view, name='calendar_view'),
    path('events/', views.appointment_events, name='appointment_events'),

    # Dynamic Filtering
    path('get_doctors_and_services/', views.get_doctors_and_services, name='get_doctors_and_services'),
]
