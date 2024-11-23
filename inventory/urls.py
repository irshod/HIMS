from django.urls import path
from . import views

urlpatterns = [
    path('medications/', views.medication_list, name='medication_list'),
    path('consumables/', views.consumable_list, name='consumable_list'),
]
