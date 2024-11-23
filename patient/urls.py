from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.patient_list, name='patient_list'),
    path('add/', views.add_patient, name='add_patient'),
    path('edit/<int:patient_id>/', views.edit_patient, name='edit_patient'),
    path('<int:patient_id>/profile/', views.view_patient_profile, name='patient_profile'),  # Patient profile
    path('<int:patient_id>/prescription/add/<int:appointment_id>/', views.add_prescription, name='patient_add_prescription'),  # Add prescription
    path('<int:patient_id>/treatment/add/<int:appointment_id>/', views.add_treatment_history, name='patient_add_treatment'),  # Add treatment history
]
