from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('departments/', include('departments.urls')),
    path('patient/', include('patient.urls')),
    path('appointments/', include('appointments.urls')),
    path('finance/', include('finance.urls')),
]
