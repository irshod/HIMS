from django.urls import path
from . import views

urlpatterns = [
    #Department Management
    path('department/', views.list_department, name='department_list'),
    path('department/add/', views.add_department, name='add_department'),
    path('department/<int:department_id>/view/', views.view_department, name='view_department'),
    path('department/<int:department_id>/edit/', views.edit_department, name='edit_department'),
    path('department/<int:department_id>/delete/', views.delete_department, name='delete_department'),
    
    # Service Management
    path('services/', views.list_service, name='service_list'),
    path('services/add/', views.add_service, name='add_service'),
    path('services/edit/<int:service_id>/', views.edit_service, name='edit_service'),
    path('services/delete/<int:service_id>/', views.delete_service, name='delete_service'),

    # Doctor Management
    path('doctors/', views.list_doctor, name='list_doctor'),
    path('doctors/add/', views.add_doctor, name='add_doctor'),
    path('doctors/edit/<int:doctor_id>/', views.edit_doctor, name='edit_doctor'),
    path('doctors/view/<int:doctor_id>/', views.view_doctor, name='view_doctor'),

    # Nurse Management
    path('nurses/', views.list_nurse, name='list_nurse'),
    path('nurses/add/', views.add_nurse, name='add_nurse'),
    path('nurses/edit/<int:nurse_id>/', views.edit_nurse, name='edit_nurse'),
    path('nurses/view/<int:nurse_id>/', views.view_nurse, name='view_nurse'),
    
    # Floors URLs
    path('floors/', views.list_floor, name='list_floor'),
    path('floors/add/', views.add_floor, name='add_floor'),
    path('floors/edit/<int:floor_id>/', views.edit_floor, name='edit_floor'),
    path('floors/delete/<int:floor_id>/', views.delete_floor, name='delete_floor'),

    # Room Management
    path('rooms/', views.list_room, name='list_room'),
    path('rooms/add/', views.add_room, name='add_room'),
    path('rooms/edit/<int:room_id>/', views.edit_room, name='edit_room'),
    path('rooms/delete/<int:room_id>/', views.delete_room, name='delete_room'),
    
    # Bed Manangement
    path('beds/', views.list_bed, name='list_bed'),
    path('beds/add/', views.add_bed, name='add_bed'),
    path('beds/edit/<int:bed_id>/', views.edit_bed, name='edit_bed'),
    path('beds/delete/<int:bed_id>/', views.delete_bed, name='delete_bed'),
]

