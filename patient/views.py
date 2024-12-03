from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from main.decorators import role_required
from main.templatetags.permissions import has_permission
from .models import Diagnosis, Patient, Prescription
from appointments.models import Appointment, TreatmentHistory
from .forms import PatientRegistrationForm
from .models import Patient
from .forms import PrescriptionForm, PatientRegistrationForm, PatientMedicalHistoryForm, PatientInsuranceForm
from django.db.models import Q
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from django.utils.timezone import datetime
from django.http import HttpResponse
from collections import defaultdict

@login_required
@user_passes_test(lambda u: has_permission(u, "view_patient"))
def patient_list(request):
    query = Q()

    age_min = request.GET.get('age_min')
    age_max = request.GET.get('age_max')
    if age_min:
        age_min_date = datetime.now() - timedelta(days=int(age_min) * 365)
        query &= Q(date_of_birth__lte=age_min_date)
    if age_max:
        age_max_date = datetime.now() - timedelta(days=int(age_max) * 365)
        query &= Q(date_of_birth__gte=age_max_date)
    
    created_after = request.GET.get('created_after')
    created_before = request.GET.get('created_before')
    if created_after:
        query &= Q(created_at__gte=created_after)
    if created_before:
        query &= Q(created_at__lte=created_before)
    
    search = request.GET.get('search', '')
    if search:
        query &= Q(first_name__icontains=search) | Q(last_name__icontains=search)
    
    patients = Patient.objects.filter(query).distinct()
    paginator = Paginator(patients, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'patient/patient_list.html', {
        'patients': page_obj,
        'search': search,
        'age_min': age_min,
        'age_max': age_max,
        'created_after': created_after,
        'created_before': created_before,
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


from collections import defaultdict
from django.utils.timezone import localdate

@login_required
@user_passes_test(lambda u: has_permission(u, "view_patient"))
def view_patient_profile(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    medical_history = defaultdict(lambda: {
        "diagnosis": [],
        "notes": [],
        "medications": [],
        "consumables": [],
        "services": [],
    })

    for diagnosis in Diagnosis.objects.filter(appointment__patient=patient):
        date = localdate(diagnosis.date)
        medical_history[date]["diagnosis"].append(diagnosis.treatment_notes)

    for treatment in TreatmentHistory.objects.filter(appointment__patient=patient).select_related('doctor'):
        date = localdate(treatment.date)
        medical_history[date]["notes"].append(treatment.treatment_notes)
        medical_history[date]["medications"].extend([
            f"{medication.medication.name} ({medication.quantity})"
            for medication in treatment.treatment_medications.all()
        ])
        medical_history[date]["consumables"].extend([
            f"{consumable.consumable.name} ({consumable.quantity})"
            for consumable in treatment.treatment_consumables.all()
        ])

    for appointment in Appointment.objects.filter(patient=patient).prefetch_related('services'):
        date = localdate(appointment.appointment_date)
        medical_history[date]["services"].extend(appointment.services.all())

    return render(request, 'patient/patient_profile.html', {
        'patient': patient,
        'medical_history': dict(medical_history), 
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

from collections import defaultdict
from django.utils.timezone import localdate

@login_required
@user_passes_test(lambda u: has_permission(u, "view_patient"))
def view_medical_history(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    history_by_date = defaultdict(lambda: {
        "diagnosis": [],
        "services": [],
        "medications": [],
        "consumables": [],
        "notes": None,
    })

    for diagnosis in Diagnosis.objects.filter(appointment__patient=patient):
        date = localdate(diagnosis.date)
        history_by_date[date]["diagnosis"].append(diagnosis.treatment_notes)

    for treatment in TreatmentHistory.objects.filter(appointment__patient=patient).select_related('doctor'):
        date = localdate(treatment.date)
        history_by_date[date]["notes"] = treatment.treatment_notes
        history_by_date[date]["medications"].extend([
            f"{medication.medication.name} ({medication.quantity})"
            for medication in treatment.treatment_medications.all()
        ])
        history_by_date[date]["consumables"].extend([
            f"{consumable.consumable.name} ({consumable.quantity})"
            for consumable in treatment.treatment_consumables.all()
        ])

    for prescription in Prescription.objects.filter(patient=patient):
        date = localdate(prescription.created_at)
        history_by_date[date]["medications"].append(f"{prescription.medication} (Prescribed)")

    for appointment in Appointment.objects.filter(patient=patient).prefetch_related('services'):
        date = localdate(appointment.appointment_date)
        history_by_date[date]["services"].extend([service.name for service in appointment.services.all()])

    return render(request, 'patient/medical_history.html', {
        'patient': patient,
        'history_by_date': dict(history_by_date),
    })

@login_required
def add_insurance(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == 'POST':
        form = PatientInsuranceForm(request.POST)
        if form.is_valid():
            insurance = form.save(commit=False)
            insurance.patient = patient
            insurance.save()
            messages.success(request, "Insurance details added successfully.")
            return redirect('patient_profile', patient_id=patient.id)
    else:
        form = PatientInsuranceForm()

    return render(request, 'patient/add_insurance.html', {
        'form': form,
        'patient': patient,
    })

@login_required
def view_insurance(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    insurance_details = patient.insurance_details.all().order_by('-coverage_start_date')
    return render(request, 'patient/insurance_details.html', {
        'patient': patient,
        'insurance_details': insurance_details,
    })


@role_required(['Doctor', 'Nurse', 'Receptionist'])
def generate_individual_pdf(request, appointment_id, date):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    patient = appointment.patient
    date_object = datetime.strptime(date, "%Y-%m-%d").date()
    history_by_date = defaultdict(lambda: {
        "diagnosis": [],
        "services": [],
        "medications": [],
        "consumables": [],
        "doctor": None,
        "notes": None,
    })

    for diagnosis in Diagnosis.objects.filter(appointment=appointment):
        history_by_date[date_object]["diagnosis"].append(diagnosis)

    for treatment in TreatmentHistory.objects.filter(appointment=appointment):
        history_by_date[date_object]["doctor"] = treatment.doctor
        history_by_date[date_object]["notes"] = treatment.treatment_notes
        history_by_date[date_object]["medications"].extend(treatment.treatment_medications.all())
        history_by_date[date_object]["consumables"].extend(treatment.treatment_consumables.all())

    if localdate(appointment.appointment_date) == date_object:
        for service in appointment.services.all():
            history_by_date[date_object]["services"].append(service)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="medical_history_{date}.pdf"'

    p = canvas.Canvas(response)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, 800, "Medical History Report")
    p.setFont("Helvetica", 12)
    p.drawString(100, 780, f"Patient: {patient.first_name} {patient.last_name}")
    p.drawString(100, 760, f"Date: {date}")

    details = history_by_date[date_object]
    y = 740
    if details["doctor"]:
        p.drawString(100, y, f"Doctor: {details['doctor'].get_full_name()}")
        y -= 20
    p.drawString(100, y, f"Notes: {details['notes'] or 'No notes'}")
    y -= 20

    for diagnosis in details["diagnosis"]:
        p.drawString(100, y, f"Diagnosis: {diagnosis.treatment_notes}")
        y -= 20

    for medication in details["medications"]:
        p.drawString(100, y, f"Medication: {medication.medication.name} (Qty: {medication.quantity})")
        y -= 15

    for consumable in details["consumables"]:
        p.drawString(100, y, f"Consumable: {consumable.consumable.name} (Qty: {consumable.quantity})")
        y -= 15

    for service in details["services"]:
        p.drawString(100, y, f"Service/Test: {service.name}")
        y -= 15

    if y < 50:
        p.showPage()
        y = 740
    p.showPage()
    p.save()
    return response