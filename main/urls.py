from django.urls import path
from . import views


urlpatterns = [
    # Authentication
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # User URLs
    path('user_list/', views.list_user, name='user_list'),
    path('user_add/', views.add_user, name='add_user'),
    path('user_edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('user_delete/<int:pk>/delete/', views.delete_user, name='delete_user'),
    path('user_view/<int:user_id>/', views.view_user, name='view_user'),
    path('profile/', views.user_profile_view, name='user_profile_view'),

    # Role URLs
    path('role_list/', views.list_role, name='role_list'),
    path('role_add/', views.add_role, name='add_role'),
    path('role_edit/<int:role_id>/', views.edit_role, name='edit_role'),
    path('role_delete/<int:pk>/delete/', views.delete_role, name='delete_role'),
    path('role_view/<int:role_id>/', views.view_role, name='view_role'),  

    # Dashboards
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('doctor_dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('nurse_dashboard/', views.nurse_dashboard, name='nurse_dashboard'),
    path('receptionist_dashboard/', views.receptionist_dashboard, name='receptionist_dashboard'),
    
    # Notifications
    path("notifications/", views.notifications_view, name="notifications_view"),
    path("notifications/read/", views.mark_notification_as_read, name="mark_notification_as_read"),
    
    # Search Result
    path('search/', views.search_results, name='search_results'),
    path('help/', views.help_view, name='help'),
]




