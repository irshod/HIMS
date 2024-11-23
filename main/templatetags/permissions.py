# permissions.py
from django import template
from main.models import Role

register = template.Library()

@register.filter(name='has_permission')
def has_permission(user, permission_name):
    if user.is_superuser:
        return True
    # Pre-fetch permissions to reduce query overhead
    roles = user.roles.prefetch_related('permissions').all()
    for role in roles:
        if role.permissions.filter(codename=permission_name).exists():
            return True
    return False
