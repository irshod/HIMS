from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from main.templatetags.permissions import has_permission
from .models import Patient, Prescription, TreatmentHistory
from appointments.models import Appointment
from .forms import PatientRegistrationForm, PrescriptionForm, TreatmentHistoryForm

@login_required
@user_passes_test(lambda u: has_permission(u, "view_patient"))
def patient_list(request):
    filter_type = request.GET.get('filter', 'all')
    if filter_type == 'ipd':
        patients = Patient.objects.filter(patient_type='IPD')
    elif filter_type == 'opd':
        patients = Patient.objects.filter(patient_type='OPD')
    else:
        patients = Patient.objects.all()

    paginator = Paginator(patients, 10)  # 10 patients per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'patient/patient_list.html', {
        'patients': page_obj,
        'filter_type': filter_type
    })



@login_required
@user_passes_test(lambda u: has_permission(u, "add_patient"))
def add_patient(request):
    """View for adding a new patient."""
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Patient registered successfully.")
            return redirect('patient_list')
        else:
            messages.error(request, "Error in form submission. Please check the details.")
    else:
        form = PatientRegistrationForm()
    return render(request, 'patient/patient_add.html', {'form': form})


@login_required
@user_passes_test(lambda u: has_permission(u, "view_patient"))
def view_patient_profile(request, patient_id):
    """View for displaying a patient's profile."""
    patient = get_object_or_404(Patient, id=patient_id)
    prescriptions = patient.prescriptions.all().order_by('-created_at')
    treatment_history = patient.treatment_history.all().order_by('-date')
    return render(request, 'patient/patient_profile.html', {
        'patient': patient,
        'prescriptions': prescriptions,
        'treatment_history': treatment_history
    })


@login_required
@user_passes_test(lambda u: u.has_perm('patient.change_patient'))
def edit_patient(request, patient_id):
    """View for editing an existing patient's information."""
    patient = get_object_or_404(Patient, id=patient_id)

    # Only allow editing of patient details
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, f"Patient {patient.first_name} {patient.last_name} updated successfully.")
            return redirect('patient_list')
        else:
            messages.error(request, "Error updating patient information.")
    else:
        form = PatientRegistrationForm(instance=patient)

    # Prescriptions and treatment history are displayed but not editable
    prescriptions = patient.prescriptions.all().order_by('-created_at')
    treatment_history = patient.treatment_history.all().order_by('-date')

    return render(request, 'patient/patient_edit.html', {
        'form': form,
        'patient': patient,
        'prescriptions': prescriptions,  # Display only
        'treatment_history': treatment_history  # Display only
    })



@login_required
@user_passes_test(lambda u: has_permission(u, "add_prescription"))
def add_prescription(request, patient_id, appointment_id):
    """View for adding a prescription."""
    patient = get_object_or_404(Patient, id=patient_id)
    appointment = get_object_or_404(Appointment, id=appointment_id, status='active')

    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.patient = patient
            prescription.doctor = request.user
            prescription.appointment = appointment
            prescription.save()
            messages.success(request, "Prescription added successfully.")
            return redirect('patient_profile', patient_id=patient.id)
    else:
        form = PrescriptionForm()

    return render(request, 'patient/add_prescription.html', {'form': form, 'patient': patient})


@login_required
@user_passes_test(lambda u: has_permission(u, "add_treatment_history"))
def add_treatment_history(request, patient_id, appointment_id):
    """View for adding treatment notes."""
    patient = get_object_or_404(Patient, id=patient_id)
    appointment = get_object_or_404(Appointment, id=appointment_id, status='active')

    if request.method == 'POST':
        form = TreatmentHistoryForm(request.POST)
        if form.is_valid():
            treatment_history = form.save(commit=False)
            treatment_history.patient = patient
            treatment_history.doctor = request.user
            treatment_history.appointment = appointment
            treatment_history.save()
            messages.success(request, "Treatment notes added successfully.")
            return redirect('patient_profile', patient_id=patient.id)
    else:
        form = TreatmentHistoryForm()

    return render(request, 'patient/add_treatment_history.html', {'form': form, 'patient': patient})
