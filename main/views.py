from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db import models
from .models import CustomUser, Role
from .forms import CustomUserCreationForm, CustomUserEditForm, RoleCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from appointments.models import Appointment, Invoice
from patient.models import Patient
from departments.models import DoctorProfile, NurseProfile, Department
from django.utils import timezone
from django.shortcuts import render
from django.utils.timezone import now

User = get_user_model()  # Reference to your custom user model

def login_view(request):
    if request.method == 'POST':
        email = request.POST['username']  # Assuming you're using email as the login identifier
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'main/login.html', {'error': 'Invalid email or password'})
    return render(request, 'main/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('login')

# @login_required
# def dashboard_view(request):
#     total_patients = Patient.objects.count()
#     total_appointments = Appointment.objects.filter(appointment_date__month=timezone.now().month).count()
#     unpaid_invoices = Invoice.objects.filter(total_amount__gt=0, payments__isnull=True).count()


#     total_doctors = DoctorProfile.objects.count()

#     # Example recent activity data
#     recent_activities = [
#         {"timestamp": p.created_at, "message": f"New patient registered: {p.first_name} {p.last_name}"}
#         for p in Patient.objects.order_by("-created_at")[:5]
#     ] + [
#         {"timestamp": a.created_at, "message": f"Appointment scheduled for Dr. {a.doctor}"}
#         for a in Appointment.objects.order_by("-created_at")[:5]
#     ] + [
#         {"timestamp": i.created_at, "message": f"Invoice #{i.id} marked as {'Paid' if i.payments.exists() else 'Unpaid'}"}
#         for i in Invoice.objects.order_by("-created_at")[:5]
#     ]

#     # Sort recent activities by timestamp
#     recent_activities = sorted(recent_activities, key=lambda x: x['timestamp'], reverse=True)[:10]

#     return render(request, 'main/dashboard.html', {
#         'total_patients': total_patients,
#         'total_appointments': total_appointments,
#         'unpaid_invoices': unpaid_invoices,
#         'total_doctors': total_doctors,
#         'recent_activities': recent_activities,
#     })

from django.db.models import Count, Sum, F
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
from django.utils.timezone import now
from django.shortcuts import render
from django.http import HttpResponseForbidden
from patient.models import Patient
from appointments.models import Appointment, Invoice
from inventory.models import Medication, Consumable
import calendar
import json


def admin_dashboard(request):
    if not request.user.roles.filter(name='Admin').exists():
        return HttpResponseForbidden("Access Denied")

    # Fetch stats
    total_patients = Patient.objects.count()
    total_appointments = Appointment.objects.filter(appointment_date__month=now().month).count()
    unpaid_invoices = Invoice.objects.filter(total_amount__gt=0, payments__isnull=True).count()
    total_revenue = Invoice.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_doctors = DoctorProfile.objects.count()

    # Low Inventory Items
    low_inventory_medications = Medication.objects.filter(quantity__lte=F('reorder_level')).values(
        'name', 'quantity', 'reorder_level'
    )
    low_inventory_consumables = Consumable.objects.filter(quantity__lte=F('reorder_level')).values(
        'name', 'quantity', 'reorder_level'
    )
    low_inventory_items = list(low_inventory_medications) + list(low_inventory_consumables)


    # Aggregate Admissions
    admissions_daily = Patient.objects.annotate(day=TruncDay('created_at')).values('day').annotate(total=Count('id'))
    admissions_weekly = Patient.objects.annotate(week=TruncWeek('created_at')).values('week').annotate(total=Count('id'))
    admissions_monthly = Patient.objects.annotate(month=TruncMonth('created_at')).values('month').annotate(total=Count('id'))
    admissions_yearly = Patient.objects.annotate(year=TruncYear('created_at')).values('year').annotate(total=Count('id'))

    # Prepare data for charts
    admissions_data = {
        "daily": [["Day", "Admissions"]] + [[item['day'].strftime('%Y-%m-%d'), item['total']] for item in admissions_daily],
        "weekly": [["Week", "Admissions"]] + [[item['week'].strftime('%Y-%U'), item['total']] for item in admissions_weekly],
        "monthly": [["Month", "Admissions"]] + [[calendar.month_name[item['month'].month], item['total']] for item in admissions_monthly],
        "yearly": [["Year", "Admissions"]] + [[item['year'].year, item['total']] for item in admissions_yearly],
    }

    # Revenue Data Aggregation
    revenue_daily = Invoice.objects.annotate(day=TruncDay('created_at')).values('day').annotate(total=Sum('total_amount'))
    revenue_weekly = Invoice.objects.annotate(week=TruncWeek('created_at')).values('week').annotate(total=Sum('total_amount'))
    revenue_monthly = Invoice.objects.annotate(month=TruncMonth('created_at')).values('month').annotate(total=Sum('total_amount'))
    revenue_yearly = Invoice.objects.annotate(year=TruncYear('created_at')).values('year').annotate(total=Sum('total_amount'))

    # Prepare data for Revenue Chart
    revenue_data = {
        "daily": [["Day", "Revenue"]] + [[item['day'].strftime('%Y-%m-%d'), float(item['total'])] for item in revenue_daily],
        "weekly": [["Week", "Revenue"]] + [[item['week'].strftime('%Y-%U'), float(item['total'])] for item in revenue_weekly],
        "monthly": [["Month", "Revenue"]] + [[calendar.month_name[item['month'].month], float(item['total'])] for item in revenue_monthly],
        "yearly": [["Year", "Revenue"]] + [[item['year'].year, float(item['total'])] for item in revenue_yearly],
    }
    # Example recent activity data
    recent_activities = [
        {"timestamp": p.created_at, "message": f"New patient registered: {p.first_name} {p.last_name}"}
        for p in Patient.objects.order_by("-created_at")[:5]
    ] + [
        {"timestamp": a.created_at, "message": f"Appointment scheduled for Dr. {a.doctor}"}
        for a in Appointment.objects.order_by("-created_at")[:5]
    ] + [
        {"timestamp": i.created_at, "message": f"Invoice #{i.id} marked as {'Paid' if i.payments.exists() else 'Unpaid'}"}
        for i in Invoice.objects.order_by("-created_at")[:5]
    ]

    # Sort recent activities by timestamp
    recent_activities = sorted(recent_activities, key=lambda x: x['timestamp'], reverse=True)[:10]

    context = {
        "total_patients": total_patients,
        "total_appointments": total_appointments,
        "unpaid_invoices": unpaid_invoices,
        "total_revenue": total_revenue,
        "total_doctors": total_doctors,
        "admissions_data": json.dumps(admissions_data),
        "revenue_data": json.dumps(revenue_data),
        "low_inventory_items": low_inventory_items,
        "recent_activities": recent_activities,
    }
    return render(request, "main/dashboards/admin_dashboard.html", context)



def doctor_dashboard(request):
    if not request.user.roles.filter(name='Doctor').exists():
        return HttpResponseForbidden("Access Denied")

    data = {
        "total_appointments": Appointment.objects.filter(doctor=request.user).count(),
        "patients_today": Appointment.objects.filter(doctor=request.user, appointment_date__date=now().date()).count(),
    }
    return render(request, 'doctor_dashboard.html', data)

def nurse_dashboard(request):
    if not request.user.roles.filter(name='Nurse').exists():
        return HttpResponseForbidden("Access Denied")

    data = {
        "assigned_patients": Patient.objects.filter(appointments__nurse=request.user).count(),
        "appointments_today": Appointment.objects.filter(nurse=request.user, appointment_date__date=now().date()).count(),
    }
    return render(request, 'nurse_dashboard.html', data)

def receptionist_dashboard(request):
    if not request.user.roles.filter(name='Receptionist').exists():
        return HttpResponseForbidden("Access Denied")

    data = {
        "today_appointments": Appointment.objects.filter(appointment_date__date=now().date()).count(),
        "unregistered_patients": Patient.objects.filter(appointments=None).count(),
    }
    return render(request, 'receptionist_dashboard.html', data)


# User Management
@login_required
def list_user(request):
    users = CustomUser.objects.all()
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    return render(request, 'main/users/user_list.html', {'page_obj': page_obj})

@login_required
def view_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    return render(request, 'main/users/user_view.html', {'user': user})

@login_required
def add_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            role = form.cleaned_data.get('role')
            if role:
                user.roles.add(role)
            messages.success(request, "User created successfully.")
            return redirect('user_list')
        else:
            messages.error(request, "There was an error with your form.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'main/users/user_add.html', {'form': form})


@login_required
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = CustomUserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"User '{user.email}' has been updated.")
            return redirect('user_list')
    else:
        form = CustomUserEditForm(instance=user)
    return render(request, 'main/users/user_edit.html', {'form': form})


@login_required
def delete_user(request, pk):
    user = get_object_or_404(CustomUser, id=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, f"User '{user.email}' has been deleted successfully.")
        return redirect('user_list')
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

    
    

# Role Management
@login_required
def list_role(request):
    roles = Role.objects.all()  # Updated to fetch Role model objects
    paginator = Paginator(roles, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    return render(request, 'main/roles/role_list.html', {'page_obj': page_obj})


@login_required
def view_role(request, role_id):
    role = get_object_or_404(Role, id=role_id)  # Updated to fetch Role model object
    permissions = role.permissions.all()
    return render(request, 'main/roles/role_view.html', {'role': role, 'permissions': permissions})


@login_required
def add_role(request):
    if request.method == 'POST':
        form = RoleCreationForm(request.POST)
        if form.is_valid():
            # Create and save the new role
            role = form.save(commit=False)
            role.save()  # Save role first to access permissions
            
            # Set permissions after role creation
            permissions = form.cleaned_data.get('permissions')
            if permissions:
                role.permissions.set(permissions)  # Set permissions for the role
            
            messages.success(request, f"Role '{role.name}' has been added successfully with {permissions.count()} permissions.")
            return redirect('role_list')
        else:
            messages.error(request, 'There was an error with the form submission. Please review the details and try again.')
    else:
        form = RoleCreationForm()

    # Display the form for GET requests
    return render(request, 'main/roles/role_add.html', {'form': form})

@login_required
def edit_role(request, role_id):
    role = get_object_or_404(Role, id=role_id)  # Updated to fetch Role model object
    if request.method == 'POST':
        form = RoleCreationForm(request.POST, instance=role)
        if form.is_valid():
            role = form.save(commit=False)
            permissions = form.cleaned_data['permissions']
            role.save()
            role.permissions.set(permissions)
            messages.success(request, f"Role '{role.name}' has been updated.")
            return redirect('role_list')
    else:
        form = RoleCreationForm(instance=role)
    return render(request, 'main/roles/role_edit.html', {'form': form})


@login_required
def delete_role(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        role.delete()
        messages.success(request, f"'{role.name}' has been deleted.")
        return redirect('role_list')
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

# Not Found Page
@login_required
def not_found(request):
    return render(request, 'users/404.html')

# Notification Handler
@login_required
def notifications_view(request):
    all_messages = messages.get_messages(request)
    notification = [
        {"message": str(msg), "tags": msg.tags} for msg in all_messages
    ]
    count = len([msg for msg in all_messages if msg.tags in ["success", "error"]])
    return JsonResponse({"notifications": notification, "count": count})

@login_required
def notification_as_read(request):
    if request.method == "POST":
        list(messages.get_messages(request))
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)

