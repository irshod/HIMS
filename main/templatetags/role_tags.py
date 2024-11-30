from django import template

register = template.Library()

@register.filter
def has_role(user, role_name):
    return user.roles.filter(name=role_name).exists()

@register.filter
def has_multi_role(user, roles):
    role_list = [role.strip() for role in roles.split(",")]
    return user.roles.filter(name__in=role_list).exists()
