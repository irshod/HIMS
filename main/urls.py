from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # User URLs
    path('user_list/', views.list_user, name='user_list'),
    path('user_add/', views.add_user, name='add_user'),
    path('user_edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('user_delete/<int:pk>/delete/', views.delete_user, name='delete_user'),
    path('user_view/<int:user_id>/', views.view_user, name='view_user'),  

    # Role URLs
    path('role_list/', views.list_role, name='role_list'),
    path('role_add/', views.add_role, name='add_role'),
    path('role_edit/<int:role_id>/', views.edit_role, name='edit_role'),
    path('role_delete/<int:pk>/delete/', views.delete_role, name='delete_role'),
    path('role_view/<int:role_id>/', views.view_role, name='view_role'),  

    # Notifications
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/mark-as-read/', views.notification_as_read, name='mark_notifications_as_read'),

    # Error Page
    path('users/not_found/', views.not_found, name='not_found'),
]
