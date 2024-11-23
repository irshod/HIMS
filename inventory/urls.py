from django.urls import path
from . import views

urlpatterns = [
    # Medication URLs
    path('medications/', views.medication_list, name='medication_list'),
    path('medications/add/', views.medication_add, name='medication_add'),
    path('medications/<int:pk>/edit/', views.medication_edit, name='medication_update'),
    path('medications/<int:pk>/delete/', views.medication_delete, name='medication_delete'),
   

    # Consumable URLs
    path('consumables/', views.consumable_list, name='consumable_list'),
    path('consumables/add/', views.consumable_add, name='consumable_add'),
    path('consumables/<int:pk>/edit/', views.consumable_edit, name='consumable_update'),
    path('consumables/<int:pk>/delete/', views.consumable_delete, name='consumable_delete'),
]