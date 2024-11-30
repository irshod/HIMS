from django.contrib import admin
from django.urls import path, include
from main.views import error_page

# Global Error Handlers
def handler403(request, exception=None):
    return error_page(request, "You do not have permission to access this page.", status=403)

def handler404(request, exception=None):
    return error_page(request, "The page you are looking for was not found.", status=404)

def handler500(request):
    return error_page(request, "An internal server error occurred. Please try again later.", status=500)

# Register the handlers directly
handler403 = handler403
handler404 = handler404
handler500 = handler500


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('departments/', include('departments.urls')),
    path('patient/', include('patient.urls')),
    path('appointments/', include('appointments.urls')),
    path('finance/', include('finance.urls')),
    path('inventory/', include('inventory.urls')),
]
