from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Service, Department, DoctorProfile, NurseProfile, StaffAvailability
from .forms import ServiceForm, DepartmentForm, DoctorProfileForm, NurseProfileForm
from django.http import JsonResponse

# Department Management
@login_required
def list_department(request):
    departments = Department.objects.prefetch_related('services', 'doctors', 'nurses').all()
    paginator = Paginator(departments, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    return render(request, 'departments/department_list.html', {'page_obj': page_obj})

@login_required
def view_department(request, department_id):
    department = get_object_or_404(Department.objects.prefetch_related('services', 'doctors', 'nurses'), id=department_id)
    
    # Fetch doctors and their statuses
    doctors_with_status = []
    for doctor in department.doctors.all():
        status = doctor.staffavailability.first()  # Get the first availability record if exists
        doctors_with_status.append({
            'doctor': doctor,
            'status': status
        })

    return render(request, 'departments/department_view.html', {
        'department': department,
        'doctors_with_status': doctors_with_status
    })


@login_required
def add_department(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save()
            doctor_status = request.POST.get('doctor_status', 'available')  # Get doctor status from the request
            nurse_status = request.POST.get('nurse_status', 'available')  # Get nurse status from the request

            for doctor in department.doctors.all():
                StaffAvailability.objects.create(user=doctor, status=doctor_status)

            for nurse in department.nurses.all():
                StaffAvailability.objects.create(user=nurse, status=nurse_status)


            messages.success(request, "Department added successfully.")
            return redirect('department_list')
        else:
            messages.error(request, "There was an error adding the department.")
    else:
        form = DepartmentForm()
    return render(request, 'departments/department_add.html', {'form': form})


@login_required
def edit_department(request, department_id):
    department = get_object_or_404(Department, id=department_id)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            department = form.save()
            doctor_status = request.POST.get('doctor_status', 'available')  # Get doctor status from the request
            nurse_status = request.POST.get('nurse_status', 'available')  # Get nurse status from the request

            # Update availability status for doctors
            for doctor in department.doctors.all():
                StaffAvailability.objects.update_or_create(
                    user=doctor,
                    defaults={'status': doctor_status}
                )

            for nurse in department.nurses.all():
                StaffAvailability.objects.update_or_create(
                    user=nurse,
                    defaults={'status': nurse_status}
                )


            messages.success(request, "Department updated successfully.")
            return redirect('department_list')
        else:
            messages.error(request, "There was an error updating the department.")
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'departments/department_edit.html', {'form': form, 'department': department})



@login_required
def delete_department(request, department_id):
    department = get_object_or_404(Department, id=department_id)
    if request.method == 'POST':
        department.delete()
        messages.success(request, f"Department '{department.name}' has been deleted.")
        return redirect('department_list')
    return render(request, 'departments/department_list.html', {'department': department})

# Service Management
@login_required
def list_service(request):
    services = Service.objects.all()
    return render(request, 'services/service_list.html', {'services': services})

@login_required
def add_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Service added successfully.")
            return redirect('service_list')
        else:
            messages.error(request, "There was an error adding the service. Please correct it.")
    else:
        form = ServiceForm()
    return render(request, 'services/service_add.html', {'form': form})

@login_required
def edit_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, "Service updated successfully.")
            return redirect('list_service')
        else:
            messages.error(request, "There was an error updating the service. Please correct it.")
    else:
        form = ServiceForm(instance=service)
    return render(request, 'services/service_edit.html', {'form': form, 'service': service})

@login_required
def delete_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if request.method == 'POST':
        service.delete()
        messages.success(request, "Service deleted successfully.")
        return JsonResponse({"status": "success", "message": f"User '{service.name}' deleted successfully"})
    return JsonResponse({"status": "error", "message": "Invalid request"})


        
@login_required
def list_doctor(request):
    doctors = DoctorProfile.objects.select_related('user').prefetch_related('assigned_services')
    paginator = Paginator(doctors, 10)  # Pagination with 10 items per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    return render(request, 'doctors/doctor_list.html', {'page_obj': page_obj})


@login_required
def add_doctor(request):
    service_queryset = Service.objects.all()  # Fetch available services
    if request.method == 'POST':
        form = DoctorProfileForm(request.POST)
        if form.is_valid():
            doctor = form.save(commit=False)  # Save the doctor object without committing
            doctor.save()  # Commit to the database
            form.save_m2m()  # Save many-to-many relationships, including assigned_services
            # Save default availability
            availability = form.cleaned_data.get('default_availability', 'available')
            StaffAvailability.objects.create(
                user=doctor.user,
                status=availability
            )
            messages.success(request, "Doctor added successfully.")
            return redirect('list_doctor')
        else:
            messages.error(request, "There was an error adding the doctor.")
    else:
        form = DoctorProfileForm()
    return render(request, 'doctors/doctor_add.html', {'form': form, 'service_queryset': service_queryset})


@login_required
def edit_doctor(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, id=doctor_id)
    service_queryset = Service.objects.all()  # Fetch all available services

    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, instance=doctor)
        if form.is_valid():
            doctor = form.save(commit=False)  # Save the doctor without committing
            doctor.save()  # Save to the database
            form.save_m2m()  # Save many-to-many relationships (e.g., assigned_services)

            # Update availability without assigning a default department
            availability = form.cleaned_data.get('default_availability', 'available')
            StaffAvailability.objects.update_or_create(
                user=doctor.user,
                defaults={'status': availability}  # Removed department from update_or_create
            )

            messages.success(request, "Doctor profile updated successfully.")
            return redirect('list_doctor')
        else:
            messages.error(request, "There was an error updating the doctor profile.")
    else:
        form = DoctorProfileForm(instance=doctor)

    return render(request, 'doctors/doctor_edit.html', {
        'form': form,
        'service_queryset': service_queryset,
        'doctor': doctor
    })





@login_required
def view_doctor(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, id=doctor_id)
    return render(request, 'doctors/doctor_view.html', {'doctor': doctor})

# Nurse Management

@login_required
def list_nurse(request):
    nurses = NurseProfile.objects.all()
    paginator = Paginator(nurses, 10)  # Pagination with 10 items per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    return render(request, 'nurses/nurse_list.html', {'page_obj': page_obj})

@login_required
def add_nurse(request):
    service_queryset = Service.objects.all()  # Fetch all available services
    if request.method == 'POST':
        form = NurseProfileForm(request.POST)
        if form.is_valid():
            nurse = form.save(commit=False)
            nurse.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, "Nurse profile added successfully.")
            return redirect('list_nurse')
        else:
            messages.error(request, "There was an error adding the nurse profile.")
    else:
        form = NurseProfileForm()
    return render(request, 'nurses/nurse_add.html', {'form': form, 'service_queryset': service_queryset})


@login_required
def edit_nurse(request, nurse_id):
    nurse = get_object_or_404(NurseProfile, id=nurse_id)
    service_queryset = Service.objects.all()  # Fetch all available services
    if request.method == 'POST':
        form = NurseProfileForm(request.POST, instance=nurse)
        if form.is_valid():
            nurse = form.save(commit=False)
            nurse.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, "Nurse profile updated successfully.")
            return redirect('list_nurse')
        else:
            messages.error(request, "There was an error updating the nurse profile.")
    else:
        form = NurseProfileForm(instance=nurse)
    return render(request, 'nurses/nurse_edit.html', {'form': form, 'service_queryset': service_queryset, 'nurse': nurse})


@login_required
def view_nurse(request, nurse_id):
    nurse = get_object_or_404(NurseProfile, id=nurse_id)
    return render(request, 'nurses/nurse_view.html', {'nurse': nurse})