from departments.models import Department
from main.models import CustomUser


def get_doctors_by_department(department_id):
    try:
        department = Department.objects.get(id=department_id)
        return department.doctors.filter(roles__name__iexact='Doctor', is_active=True)
    except Department.DoesNotExist:
        return CustomUser.objects.none()


def get_services_by_department(department_id):
    try:
        department = Department.objects.get(id=department_id)
        return department.services.all()
    except Department.DoesNotExist:
        return []


def get_users_by_role(role_name):
    return CustomUser.objects.filter(roles__name__iexact=role_name, is_active=True)
