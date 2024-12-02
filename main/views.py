from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.http import HttpResponseForbidden, JsonResponse
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Count, Sum, F, Q
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
import calendar
import json
from .models import CustomUser, Role
from .forms import CustomUserCreationForm, CustomUserEditForm, RoleCreationForm
from appointments.models import Appointment, IPDAdmission, Invoice
from patient.models import Patient
from departments.models import DoctorProfile, NurseProfile
from inventory.models import Medication, Consumable
from .decorators import role_required

User = get_user_model()  # Reference to custom user model

def login_view(request):
    if request.method == 'POST':
        email = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            print(f"Authenticated user: {user.email}, Roles: {[role.name for role in user.roles.all()]}")
            if user.has_role('Admin'):
                return redirect('admin_dashboard')
            elif user.has_role('Doctor'):
                return redirect('doctor_dashboard')
            elif user.has_role('Nurse'):
                return redirect('nurse_dashboard')
            elif user.has_role('Receptionist'):
                return redirect('receptionist_dashboard')
        else:
            return render(request, 'main/login.html', {'error': 'Invalid email or password'})
    return render(request, 'main/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('login')

@role_required(['Admin'])
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

@role_required(['Doctor'])
def doctor_dashboard(request):
    if not request.user.roles.filter(name='Doctor').exists():
        return HttpResponseForbidden("Access Denied")

    doctor_profile = DoctorProfile.objects.filter(user=request.user).first()

    # Fetch stats
    total_appointments = Appointment.objects.filter(doctor=request.user).count()
    appointments_today = Appointment.objects.filter(
        doctor=request.user,
        appointment_date__date=now().date()
    ).count()

    # IPD Patients (Admitted only)
    ipd_patients = IPDAdmission.objects.filter(
        doctor=request.user, status='admitted'
    ).select_related('patient', 'room', 'floor')

    # Pending Patients
    pending_patients = Appointment.objects.filter(
        doctor=request.user, status='pending'
    ).select_related('patient')

    # Today's Patients
    todays_patients = Appointment.objects.filter(
        doctor=request.user, appointment_date__date=now().date()
    ).select_related('patient')

    # All Patients Treated by This Doctor
    all_patients = Patient.objects.filter(
        appointment_related__doctor=request.user
    ).distinct()

    context = {
        "doctor_profile": doctor_profile,
        "total_appointments": total_appointments,
        "appointments_today": appointments_today,
        "ipd_patients": ipd_patients,
        "pending_patients": pending_patients,
        "todays_patients": todays_patients,
        "all_patients": all_patients,
    }
    return render(request, 'main/dashboards/doctor_dashboard.html', context)



@role_required(['Nurse'])
def nurse_dashboard(request):
    if not request.user.roles.filter(name='Nurse').exists():
        return HttpResponseForbidden("Access Denied")

    data = {
        "assigned_patients": Patient.objects.filter(appointments__nurse=request.user).count(),
        "appointments_today": Appointment.objects.filter(nurse=request.user, appointment_date__date=now().date()).count(),
    }
    return render(request, 'main/dashboards/nurse_dashboard.html', data)

@role_required(['Receptionist'])
def receptionist_dashboard(request):
    total_patients = Patient.objects.count()
    total_appointments = Appointment.objects.filter(appointment_date__month=now().month).count()
    unpaid_invoices = Invoice.objects.filter(total_amount__gt=0, payments__isnull=True).count()
    total_doctors = CustomUser.objects.filter(roles__name="Doctor", is_active=True).count()
    todays_patients = Appointment.objects.filter(appointment_date__date=now().date()).select_related('patient', 'doctor')
    today_appointments = Appointment.objects.filter(appointment_date__date=now().date()).count()
    unregistered_patients = Patient.objects.filter(appointment_related=None).count() 

    recent_activities = [
        {"timestamp": p.created_at, "message": f"New patient registered: {p.first_name} {p.last_name}"}
        for p in Patient.objects.order_by("-created_at")[:5]
    ] + [
        {"timestamp": a.created_at, "message": f"Appointment scheduled for Dr. {a.doctor}"}
        for a in Appointment.objects.order_by("-created_at")[:5]
    ] + [
        {"timestamp": a.created_at, "message": f"IPD Admission admited for Dr. {a.doctor}"}
        for a in IPDAdmission.objects.order_by("-created_at")[:5]
    ] + [
        {"timestamp": i.created_at, "message": f"Invoice #{i.id} marked as {'Paid' if i.payments.exists() else 'Unpaid'}"}
        for i in Invoice.objects.order_by("-created_at")[:5]
    ]
    recent_activities = sorted(recent_activities, key=lambda x: x['timestamp'], reverse=True)[:10]
    
    context = {
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'unpaid_invoices': unpaid_invoices,
        'total_doctors': total_doctors,
        'recent_activities': recent_activities,
        'todays_patients': todays_patients,
        'today_appointments': today_appointments,
        'unregistered_patients': unregistered_patients,
    }

    return render(request, 'main/dashboards/receptionist_dashboard.html', context)



# User Management
@role_required(['Admin'])
def list_user(request):
    users = CustomUser.objects.all()
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    return render(request, 'main/users/user_list.html', {'page_obj': page_obj})

@role_required(['Admin'])
def view_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    context = {
        'user': user,
        'roles': user.roles.all(),
    }
    return render(request, 'main/users/user_view.html', context)
    

@role_required(['Admin'])
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

@role_required(['Admin'])
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

@role_required(['Admin'])
def delete_user(request, pk):
    user = get_object_or_404(CustomUser, id=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, f"User '{user.email}' has been deleted successfully.")
        return redirect('user_list')
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

# Role Management
@role_required(['Admin'])
def list_role(request):
    roles = Role.objects.all()
    paginator = Paginator(roles, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    return render(request, 'main/roles/role_list.html', {'page_obj': page_obj})


@role_required(['Admin'])
def view_role(request, role_id):
    role = get_object_or_404(Role, id=role_id)
    permissions = role.permissions.all()
    return render(request, 'main/roles/role_view.html', {'role': role, 'permissions': permissions})


@role_required(['Admin'])
def add_role(request):
    if request.method == 'POST':
        form = RoleCreationForm(request.POST)
        if form.is_valid():
            role = form.save(commit=False)
            role.save()
            permissions = form.cleaned_data.get('permissions')
            if permissions:
                role.permissions.set(permissions)            
            messages.success(request, f"Role '{role.name}' has been added successfully with {permissions.count()} permissions.")
            return redirect('role_list')
        else:
            messages.error(request, 'There was an error with the form submission. Please review the details and try again.')
    else:
        form = RoleCreationForm()
    return render(request, 'main/roles/role_add.html', {'form': form})

@role_required(['Admin'])
def edit_role(request, role_id):
    role = get_object_or_404(Role, id=role_id)
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


@role_required(['Admin'])
def delete_role(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        role.delete()
        messages.success(request, f"'{role.name}' has been deleted.")
        return redirect('role_list')
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

""" General-purpose error handler.
- error_message: Message to display to the user.
- status: HTTP status code for the error. """
def error_page(request, error_message, status=400):
    return render(request, 'main/error.html', {'error_message': error_message}, status=status)

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



def search_results(request):
    query = request.GET.get('query', '').strip()  # Get the search query from the request
    patients = []
    
    if query:
        # Assuming you have Patient and Doctor models
        from patient.models import Patient
        patients = Patient.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )
    
    return render(request, 'main/search_results.html', {'query': query, 'patients': patients})

@login_required
def user_profile_view(request):
    user = request.user
    doctor_profile = None
    nurse_profile = None

    # Check if the user has a doctor or nurse profile
    if user.has_role('Doctor'):
        doctor_profile = DoctorProfile.objects.filter(user=user).first()
    elif user.has_role('Nurse'):
        nurse_profile = NurseProfile.objects.filter(user=user).first()

    return render(request, 'main/user_profile.html', {
        'user': user,
        'doctor_profile': doctor_profile,
        'nurse_profile': nurse_profile,
    })

@login_required
def help_view(request):
    return render(request, 'main/help.html')
