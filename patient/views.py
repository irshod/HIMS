from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from main.templatetags.permissions import has_permission
from .models import Patient
from appointments.models import Appointment
from .forms import PatientRegistrationForm
from .models import Patient
from .forms import PrescriptionForm, PatientRegistrationForm, PatientMedicalHistoryForm, PatientInsuranceForm

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
    medical_history = patient.medical_history.all().order_by('-diagnosis_date')
    insurance_details = patient.insurance_details.all().order_by('-coverage_start_date')
    prescriptions = patient.prescriptions.all().order_by('-created_at')

    return render(request, 'patient/patient_profile.html', {
        'patient': patient,
        'medical_history': medical_history,
        'insurance_details': insurance_details,
        'prescriptions': prescriptions,
    })



@login_required
@user_passes_test(lambda u: u.has_perm('patient.change_patient'))
def edit_patient(request, patient_id):
    """View for editing an existing patient's information."""
    patient = get_object_or_404(Patient, id=patient_id)

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

    return render(request, 'patient/patient_edit.html', {
        'form': form,
        'patient': patient
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
@user_passes_test(lambda u: has_permission(u, "add_patientmedicalhistory"))
def add_medical_history(request, patient_id):
    """Add medical history for a patient."""
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == 'POST':
        form = PatientMedicalHistoryForm(request.POST)
        if form.is_valid():
            medical_history = form.save(commit=False)
            medical_history.patient = patient
            medical_history.save()
            messages.success(request, "Medical history added successfully.")
            return redirect('view_patient_profile', patient_id=patient.id)
    else:
        form = PatientMedicalHistoryForm()

    return render(request, 'patient/add_medical_history.html', {
        'form': form,
        'patient': patient,
    })

@login_required
@user_passes_test(lambda u: has_permission(u, "view_patientmedicalhistory"))
def view_medical_history(request, patient_id):
    """View all medical history for a patient."""
    patient = get_object_or_404(Patient, id=patient_id)
    medical_history = patient.medical_history.all().order_by('-diagnosis_date')
    return render(request, 'patient/medical_history.html', {
        'patient': patient,
        'medical_history': medical_history,
    })

@login_required
@user_passes_test(lambda u: has_permission(u, "add_patientinsurance"))
def add_insurance(request, patient_id):
    """Add insurance details for a patient."""
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == 'POST':
        form = PatientInsuranceForm(request.POST)
        if form.is_valid():
            insurance = form.save(commit=False)
            insurance.patient = patient
            insurance.save()
            messages.success(request, "Insurance details added successfully.")
            return redirect('view_patient_profile', patient_id=patient.id)
    else:
        form = PatientInsuranceForm()

    return render(request, 'patient/add_insurance.html', {
        'form': form,
        'patient': patient,
    })

@login_required
@user_passes_test(lambda u: has_permission(u, "view_patientinsurance"))
def view_insurance(request, patient_id):
    """View insurance details for a patient."""
    patient = get_object_or_404(Patient, id=patient_id)
    insurance_details = patient.insurance_details.all().order_by('-coverage_start_date')
    return render(request, 'patient/insurance_details.html', {
        'patient': patient,
        'insurance_details': insurance_details,
    })
