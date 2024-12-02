from django.urls import path
from . import views

urlpatterns = [
    # Patient Management
    path('list/', views.patient_list, name='patient_list'),  # Patient list view
    path('add/', views.add_patient, name='add_patient'),  # Add new patient
    path('edit/<int:patient_id>/', views.edit_patient, name='edit_patient'),  # Edit patient information
    path('<int:patient_id>/profile/', views.view_patient_profile, name='patient_profile'),  # View patient profile

    # Prescription Management
    path('<int:patient_id>/prescription/add/<int:appointment_id>/', views.add_prescription, name='add_prescription'),  # Add prescription

    # Medical History Management
    path('<int:patient_id>/medical-history/add/', views.add_medical_history, name='add_medical_history'),  # Add medical history
    path('<int:patient_id>/medical-history/', views.view_medical_history, name='view_medical_history'),  # View medical history
    path('appointments/<int:appointment_id>/history/<str:date>/pdf/', views.generate_individual_pdf, name='generate_individual_pdf'),

    # Insurance Management
    path('<int:patient_id>/insurance/add/', views.add_insurance, name='add_insurance'),  # Add insurance details
    path('<int:patient_id>/insurance/', views.view_insurance, name='view_insurance'),  # View insurance details
]
