from django.shortcuts import render, redirect
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            if not request.user.roles.filter(name__in=allowed_roles).exists():
                return render(request, 'main/error.html', {
                    'error_message': "You do not have permission to view this page."
                }, status=403)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def role_and_permission_required(allowed_roles, required_permission):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            if not request.user.roles.filter(name__in=allowed_roles).exists():
                raise PermissionDenied("You do not have the required role.")
            
            if not request.user.has_perm(required_permission):
                raise PermissionDenied("You do not have the required permission.")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
