from django.urls import path
from . import views

urlpatterns = [
    # Patient Management
    path('list/', views.patient_list, name='patient_list'),
    path('add/', views.add_patient, name='add_patient'),
    path('edit/<int:patient_id>/', views.edit_patient, name='edit_patient'),
    path('<int:patient_id>/profile/', views.view_patient_profile, name='patient_profile'),

    # Prescription Management
    path('<int:patient_id>/prescription/add/<int:appointment_id>/', views.add_prescription, name='add_prescription'),

    # Medical History Management
    path('<int:patient_id>/medical-history/add/', views.add_medical_history, name='add_medical_history'),
    path('<int:patient_id>/medical-history/', views.view_medical_history, name='view_medical_history'),
    path('appointments/<int:appointment_id>/history/<str:date>/pdf/', views.generate_individual_pdf, name='generate_individual_pdf'),

    # Insurance Management
    path('<int:patient_id>/insurance/add/', views.add_insurance, name='add_insurance'),
    path('<int:patient_id>/insurance/', views.view_insurance, name='view_insurance'),  
]