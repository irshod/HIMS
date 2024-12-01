import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.timezone import now
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Appointment, IPDAdmission, Invoice, Payment, TreatmentHistory
from .forms import AppointmentForm, AddServiceForm, AddMedicationForm, AddConsumableForm, IPDAdmissionForm, IPDDischargeForm, TreatmentHistoryForm
from patient.forms import DiagnosisForm, Diagnosis
from datetime import datetime, timedelta
from departments.models import Bed, Floor, Room, Service, Department
from django.http import JsonResponse, HttpResponse
from main.models import CustomUser 
from departments.utils import get_doctors_by_department, get_services_by_department
from reportlab.pdfgen import canvas
from decimal import Decimal, InvalidOperation
from collections import defaultdict
from django.utils.timezone import localdate
from django.db.models import Q
from django.db import transaction
from main.decorators import role_required, role_and_permission_required

# Create Appointment
@role_required(['Receptionist','Admin'])
def create_appointment(request):
    service_queryset = Service.objects.none()

    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)  # Save without committing for initial processing
            appointment.save()  # Save to assign an ID
            services_selected = form.cleaned_data.get('services', [])
            appointment.services.set(services_selected)  # Now safe to set many-to-many relationships
            messages.success(request, "Appointment created successfully.")
            return redirect('appointments_list')
    else:
        form = AppointmentForm()

    department_id = request.GET.get('department')
    if department_id:
        try:
            service_queryset = Service.objects.filter(department__id=int(department_id))
        except (ValueError, TypeError):
            service_queryset = Service.objects.none()
    else:
        service_queryset = Service.objects.all()

    return render(request, 'appointments/create_appointment.html', {
        'form': form,
        'service_queryset': service_queryset,
    })

def get_doctors_and_services(request):
    department_id = request.GET.get('department_id')
    doctors = []
    services = []

    if department_id:
        doctors = [
            {'id': doctor.id, 'name': f"{doctor.first_name} {doctor.last_name}"}
            for doctor in get_doctors_by_department(department_id)
        ]
        services = [
            {'id': service.id, 'name': service.name, 'price': service.price}
            for service in get_services_by_department(department_id)
        ]

    return JsonResponse({'doctors': doctors, 'services': services})

def get_doctors(request):
    department_id = request.GET.get("department_id")
    doctors = CustomUser.objects.filter(departments_as_doctor__id=department_id, roles__name="Doctor")
    data = [{"id": doctor.id, "first_name": doctor.first_name, "last_name": doctor.last_name} for doctor in doctors]
    return JsonResponse(data, safe=False)

def get_floors(request):
    department_id = request.GET.get("department_id")
    if department_id:
        floors = Floor.objects.filter(department_id=department_id)
    else:
        floors = Floor.objects.all()
    
    data = [{"id": floor.id, "floor_number": f"Floor {floor.floor_number}"} for floor in floors]
    return JsonResponse(data, safe=False)

def get_rooms(request):
    floor_id = request.GET.get("floor_id")
    rooms = Room.objects.filter(floor_id=floor_id)
    data = [{"id": room.id, "name": f"Room {room.room_number}"} for room in rooms]
    return JsonResponse(data, safe=False)

def get_beds(request):
    room_id = request.GET.get("room_id")
    beds = Bed.objects.filter(room_id=room_id, status='available')
    data = [{"id": bed.id, "bed_number": bed.bed_number, "status": bed.status} for bed in beds]
    return JsonResponse(data, safe=False)


@login_required
@transaction.atomic
def admit_patient(request):
    if request.method == 'POST':
        form = IPDAdmissionForm(request.POST)
        if form.is_valid():
            admission = form.save(commit=False)
            bed = form.cleaned_data['bed']
            
            if bed.status != 'available':
                messages.error(request, "The selected bed is not available.")
                return redirect('admit_patient')

            # Assign bed to patient and mark it as occupied
            bed.mark_as_occupied()
            admission.bed = bed
            admission.save()

            messages.success(request, f"Patient {admission.patient.first_name} admitted successfully.")
            return redirect('ipd_admissions_list')
    else:
        form = IPDAdmissionForm()

    return render(request, 'admissions/admit_patient.html', {'form': form})

@login_required
@login_required
def discharge_patient(request, admission_id):
    admission = get_object_or_404(IPDAdmission, id=admission_id)
    if request.method == 'POST':
        form = IPDDischargeForm(request.POST, instance=admission)
        if form.is_valid():
            discharge = form.save(commit=False)
            discharge.status = 'discharged'
            discharge.save(update_fields=['discharge_date', 'status'])
            
            if admission.bed:
                admission.bed.mark_as_available()  # Mark the bed as available
            
            messages.success(request, f"Patient {admission.patient.first_name} discharged successfully.")
            return redirect('ipd_admissions_list')
    else:
        form = IPDDischargeForm(instance=admission)
    return render(request, 'admissions/discharge_patient.html', {'form': form, 'admission': admission})


def ipd_admissions_list(request):
    query = Q()  # Initialize an empty query

    # Apply filters from the request
    status = request.GET.get('status')  # Get the status filter from the request
    if status in dict(IPDAdmission.STATUS_CHOICES):  # Validate the status value
        query &= Q(status=status)

    # Fetch filtered admissions
    admissions = IPDAdmission.objects.select_related(
        'patient', 'doctor', 'department', 'room', 'floor'
    ).filter(query).order_by('-admission_date')

    paginator = Paginator(admissions, 10)  # Paginate results
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'departments': Department.objects.all(),  # For filtering
        'status_choices': IPDAdmission.STATUS_CHOICES,  # Pass status choices to the template
    }
    return render(request, 'admissions/admissions_list.html', context)

def view_admission(request, admission_id):
    admission = get_object_or_404(IPDAdmission, id=admission_id)
    return render(request, 'admissions/view_admission.html', {'admission': admission})

# Generate Invoice
@role_required(['Receptionist','Admin'])
def generate_invoice(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    # Recalculate total cost of services dynamically
    appointment.calculate_total_cost()
    appointment.save()

    invoice, created = Invoice.objects.get_or_create(
        appointment=appointment,
        defaults={'total_amount': appointment.total_cost}
    )
    if not created:
        invoice.total_amount = appointment.total_cost
        invoice.save(update_fields=["total_amount"])

    # Update payment status
    if invoice.outstanding_balance() == 0:
        appointment.payment_status = "paid"
        appointment.save(update_fields=["payment_status"])

    return render(request, 'appointments/generate_invoice.html', {
        'appointment': appointment,
        'invoice': invoice,
    })

# Process Payment
@role_required(['Receptionist','Admin'])
def process_payment(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            payment_amount = body.get('amount', 0)

            # Ensure the payment amount is valid
            try:
                payment_amount = Decimal(payment_amount)
            except (InvalidOperation, ValueError):
                return JsonResponse({'success': False, 'error': 'Invalid payment amount format.'}, status=400)

            if payment_amount <= 0:
                return JsonResponse({'success': False, 'error': 'Payment amount must be greater than zero.'}, status=400)

            if payment_amount > invoice.outstanding_balance():
                return JsonResponse({'success': False, 'error': 'Payment amount exceeds outstanding balance.'}, status=400)

            # Create payment
            Payment.objects.create(
                invoice=invoice,
                amount=payment_amount,
                payment_method='cash',  # Replace with actual payment method if needed
            )

            # Update invoice status and appointment payment status
            if invoice.outstanding_balance() == 0:
                invoice.appointment.payment_status = "paid"
            else:
                invoice.appointment.payment_status = "unpaid"

            invoice.appointment.save(update_fields=["payment_status"])

            # Return updated data
            total_paid = invoice.total_paid()
            outstanding_balance = invoice.outstanding_balance()

            return JsonResponse({
                'success': True,
                'total_paid': float(total_paid),
                'outstanding_balance': float(outstanding_balance),
                'status': invoice.status,
            })

        except Exception as e:
            # Improved logging for debugging
            print(f"Error processing payment: {e}")
            return JsonResponse({'success': False, 'error': 'Internal server error.'}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

# PDF Invoice
@role_required(['Receptionist','Admin'])
def generate_pdf_invoice(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if not hasattr(appointment, 'invoice'):
        appointment.invoice = Invoice.objects.create(
            appointment=appointment,
            total_amount=appointment.total_cost,
            status=appointment.payment_status
        )

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="Invoice_{}.pdf"'.format(appointment_id)

    p = canvas.Canvas(response)
    p.setFont("Helvetica", 12)
    p.drawString(100, 800, f"Invoice for Appointment #{appointment.id}")
    p.drawString(100, 780, f"Patient: {appointment.patient}")
    p.drawString(100, 760, f"Doctor: {appointment.doctor}")
    y = 740
    for service in appointment.services.all():
        p.drawString(120, y, f"- {service.name} (${service.price})")
        y -= 20
    p.drawString(100, y - 20, f"Total Amount: ${appointment.invoice.total_amount}")
    p.drawString(100, y - 40, f"Status: {appointment.invoice.status}")
    p.showPage()
    p.save()

    return response

# View to list all appointments
@role_required(['Doctor', 'Nurse', 'Receptionist', 'Admin'])
def appointments_list(request):
    query = Q()

    # Filters based on user role
    if request.user.roles.filter(name='Doctor').exists():
        query &= Q(doctor=request.user)
    elif request.user.roles.filter(name='Nurse').exists():
        # You can add logic for nurses if needed, e.g., filter by department or assigned doctors
        pass

    # Additional filters from the request
    patient_name = request.GET.get('patient_name', '').strip()
    doctor_name = request.GET.get('doctor_name', '').strip()
    department_id = request.GET.get('department')
    status = request.GET.get('status')
    date_after = request.GET.get('date_after')
    date_before = request.GET.get('date_before')

    # Apply the filters
    if patient_name:
        query &= Q(patient__first_name__icontains=patient_name) | Q(patient__last_name__icontains=patient_name)

    if doctor_name:
        query &= Q(doctor__first_name__icontains=doctor_name) | Q(doctor__last_name__icontains=doctor_name)

    if department_id:
        query &= Q(department_id=department_id)

    if status and status in dict(Appointment.STATUS_CHOICES):  # Validate against STATUS_CHOICES
        query &= Q(status=status)

    if date_after:
        query &= Q(appointment_date__gte=date_after)

    if date_before:
        query &= Q(appointment_date__lte=date_before)

    # Query and paginate
    appointments = Appointment.objects.filter(query).order_by('-appointment_date')
    paginator = Paginator(appointments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Pass filters to the template
    context = {
        'page_obj': page_obj,
        'patient_name': patient_name,
        'doctor_name': doctor_name,
        'department_id': department_id,
        'current_status': status,  # Pass the current status filter
        'date_after': date_after,
        'date_before': date_before,
        'departments': Department.objects.all(),
        'status_choices': Appointment.STATUS_CHOICES,  # Pass STATUS_CHOICES to the template
    }

    return render(request, 'appointments/appointment_list.html', context)


@role_required(['Doctor','Nurse','Receptionist'])
def view_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Group history by date
    history_by_date = defaultdict(lambda: {
        "diagnosis": [],
        "services": [],
        "medications": [],
        "consumables": [],
        "notes": None,
    })

    # Fetch and group diagnoses (no doctor field in Diagnosis)
    for diagnosis in Diagnosis.objects.filter(appointment=appointment):
        date = localdate(diagnosis.date)
        history_by_date[date]["diagnosis"].append(diagnosis)

    # Fetch and group treatment history (includes doctor field)
    for treatment in TreatmentHistory.objects.filter(appointment=appointment).select_related('doctor'):
        date = localdate(treatment.date)
        history_by_date[date]["notes"] = treatment.treatment_notes
        history_by_date[date]["medications"].extend(treatment.treatment_medications.all())
        history_by_date[date]["consumables"].extend(treatment.treatment_consumables.all())
        history_by_date[date]["doctor"] = appointment.doctor  # Track doctor for treatments

    # Fetch and group services/tests
    for service in appointment.services.all():
        date = localdate(appointment.appointment_date)
        history_by_date[date]["services"].append(service)

    return render(request, 'appointments/view_appointment.html', {
        'appointment': appointment,
        'history_by_date': dict(history_by_date),  # Pass as a dictionary for template rendering
    })

# Update status to in-progress (doctor starts the appointment)
@role_required(['Doctor','Nurse'])
def start_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'in_progress'
    appointment.save()
    messages.success(request, "Appointment status updated to 'In Progress'.")
    return redirect('view_appointment', appointment_id=appointment.id)

# Update status to awaiting test (doctor orders a test)
@role_required(['Doctor','Nurse'])
def mark_awaiting_test(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'awaiting_test'
    appointment.save()
    messages.success(request, "Appointment status updated to 'Awaiting Test'.")
    return redirect('view_appointment', appointment_id=appointment.id)

# Update status to completed (doctor finishes the appointment)
@role_required(['Doctor','Nurse'])
def complete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'completed'
    appointment.save()
    messages.success(request, "Appointment marked as 'Completed'.")
    return redirect('view_appointment', appointment_id=appointment.id)

# Cancel an appointment (no delete functionality)
@role_required(['Receptionist'])
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if appointment.status == 'pending':
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, "Appointment has been successfully cancelled.")
    else:
        messages.error(request, "Only pending appointments can be cancelled.")
    return redirect('appointments_list')

# Calendar view showing appointment availability
@role_required(['Receptionist','Admin','Doctor','Nurse'])
def calendar_view(request):
    departments = Department.objects.all()
    doctors = CustomUser.objects.filter(roles__name='Doctor')  # Filter only doctors
    return render(request, 'appointments/calendar.html', {
        'departments': departments,
        'doctors': doctors,
    })

def appointment_events(request):
    date_str = request.GET.get('date', datetime.now().strftime('%Y-%m-%d'))
    selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()

    department_id = request.GET.get('department')
    doctor_id = request.GET.get('doctor')

    # Filter appointments by date
    appointments = Appointment.objects.filter(appointment_date__date=selected_date)

    # Apply department filter if provided
    if department_id:
        appointments = appointments.filter(department_id=department_id)

    # Apply doctor filter if provided
    if doctor_id:
        appointments = appointments.filter(doctor_id=doctor_id)

    events = [
        {
            "title": f"{appointment.patient.first_name} with Dr. {appointment.doctor.get_full_name()}",
            "start": appointment.appointment_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "end": (appointment.appointment_date + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S"),
            "extendedProps": {
                "type": appointment.get_appointment_type_display(),
                "status": appointment.get_status_display(),
                "department": appointment.department.name,
                "cost": appointment.total_cost,
                "payment_status": appointment.get_payment_status_display(),
            },
            "backgroundColor": "#28a745" if appointment.appointment_type == "opd" else "#007bff",
        }
        for appointment in appointments
    ]
    return JsonResponse(events, safe=False)

# Treatment Notes
@login_required
@user_passes_test(lambda u: u.has_perm("appointments.add_treatment_notes"))
def add_treatment_notes(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        form = TreatmentHistoryForm(request.POST)
        if form.is_valid():
            treatment_history = form.save(commit=False)
            treatment_history.appointment = appointment
            treatment_history.doctor = request.user
            treatment_history.save()
            messages.success(request, "Treatment notes added successfully.")
            return redirect('view_appointment', appointment_id=appointment_id)
    else:
        form = TreatmentHistoryForm()
    return render(request, 'treatment/add_treatment_notes.html', {'form': form, 'appointment': appointment})

@login_required
@user_passes_test(lambda u: u.has_perm("appointments.add_diagnosis"))
def add_diagnosis(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        form = DiagnosisForm(request.POST)
        if form.is_valid():
            diagnosis = form.save(commit=False)
            diagnosis.appointment = appointment
            diagnosis.save()
            messages.success(request, "Diagnosis added successfully.")
            return redirect('view_appointment', appointment_id=appointment_id)
    else:
        form = DiagnosisForm()

    return render(request, 'treatment/add_diagnosis.html', {
        'form': form,
        'appointment': appointment,
    })

# Add service after consultation or when needed
@login_required
@user_passes_test(lambda u: u.has_perm('appointments.add_service'))
def add_service_to_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    invoice, created = Invoice.objects.get_or_create(appointment=appointment)

    if request.method == 'POST':
        form = AddServiceForm(request.POST)
        if form.is_valid():
            # Use the save method of the form
            service = form.save(commit=False) if hasattr(form, 'save') else None
            if service:
                service.appointment = appointment
                service.save()

                # Update invoice total
                invoice.total_amount += service.price
                invoice.save()

            messages.success(request, "Service added successfully.")
            return redirect('view_appointment', appointment_id=appointment_id)
    else:
        form = AddServiceForm()

    return render(request, 'treatment/add_service.html', {
        'form': form,
        'appointment': appointment,
    })

# Add Medication to Treatment
@login_required
@user_passes_test(lambda u: u.has_perm("appointments.add_medication"))
def add_medication_to_treatment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    invoice, created = Invoice.objects.get_or_create(appointment=appointment)

    if request.method == 'POST':
        form = AddMedicationForm(request.POST)
        if form.is_valid():
            medication_data = form.save(appointment)

            # Update invoice total
            total_cost = medication_data['price'] * medication_data['quantity']
            invoice.total_amount += total_cost
            invoice.save()

            # Update appointment total cost
            appointment.total_cost += total_cost
            appointment.payment_status = 'unpaid'  # Mark as unpaid if the cost increases
            appointment.save()
            
            # Update payment status
            if invoice.outstanding_balance() == 0:
                appointment.payment_status = "paid"
            else:
                appointment.payment_status = "unpaid"
            appointment.save()

            messages.success(request, "Medication added successfully.")
            return redirect('view_appointment', appointment_id=appointment_id)
    else:
        form = AddMedicationForm()

    return render(request, 'treatment/add_medication.html', {
        'form': form,
        'appointment': appointment,
    })

@login_required
def update_total_cost(request, appointment_id):
    if request.method == "POST":
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            data = json.loads(request.body)
            additional_cost = data.get("additional_cost", 0)

            if additional_cost:
                appointment.total_cost += Decimal(additional_cost)
                appointment.save(update_fields=["total_cost"])

            return JsonResponse({"success": True, "total_cost": float(appointment.total_cost)})

        except Appointment.DoesNotExist:
            return JsonResponse({"success": False, "error": "Appointment not found."}, status=404)

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)

# Add Consumable to Treatment
@login_required
@user_passes_test(lambda u: u.has_perm("appointments.add_consumable"))
def add_consumable_to_treatment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Ensure the appointment has an associated invoice
    invoice, created = Invoice.objects.get_or_create(appointment=appointment)

    if request.method == 'POST':
        form = AddConsumableForm(request.POST)
        if form.is_valid():
            consumable = form.save(appointment)

            # Update invoice total if consumable has a price
            invoice.total_amount += consumable.total_cost
            invoice.save()

            messages.success(request, "Consumable added successfully.")
            return redirect('view_appointment', appointment_id=appointment_id)
    else:
        form = AddConsumableForm()

    return render(request, 'treatment/add_consumable.html', {
        'form': form,
        'appointment': appointment,
    })


def generate_medical_report(request, appointment_id):
    # Fetch appointment
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Build history_by_date
    history_by_date = defaultdict(lambda: {
        "diagnosis": [],
        "services": [],
        "medications": [],
        "consumables": [],
        "doctor": None,
        "notes": None,
    })

    for diagnosis in appointment.diagnoses.all():
        date = localdate(diagnosis.date)
        history_by_date[date]["diagnosis"].append(diagnosis)

    # Fetch and group treatment history
    for treatment in TreatmentHistory.objects.filter(appointment=appointment):
        date = localdate(treatment.date)
        history_by_date[date]["doctor"] = treatment.doctor
        history_by_date[date]["notes"] = treatment.treatment_notes
        history_by_date[date]["medications"].extend(treatment.treatment_medications.all())
        history_by_date[date]["consumables"].extend(treatment.treatment_consumables.all())

   

    # Populate services/tests
    for service in appointment.services.all():
        history_by_date[localdate(appointment.appointment_date)]["services"].append(service)

    # Generate PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="medical_report_{appointment_id}.pdf"'

    p = canvas.Canvas(response)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, 800, "Medical Report")
    p.setFont("Helvetica", 12)
    p.drawString(100, 780, f"Patient: {appointment.patient.first_name} {appointment.patient.last_name}")
    p.drawString(100, 760, f"Doctor: {appointment.doctor.get_full_name()}")
    y = 740

    for date, details in history_by_date.items():
        p.drawString(100, y, f"Date: {date}")
        y -= 20
        p.drawString(120, y, f"Diagnosis: {', '.join([d.treatment_notes for d in details['diagnosis']])}")
        y -= 20
        p.drawString(120, y, f"Notes: {details['notes']}")
        y -= 20
        for medication in details["medications"]:
            p.drawString(140, y, f"Medication: {medication.medication.name} (Qty: {medication.quantity})")
            y -= 15
        for consumable in details["consumables"]:
            p.drawString(140, y, f"Consumable: {consumable.consumable.name} (Qty: {consumable.quantity})")
            y -= 15
        for service in details["services"]:
            p.drawString(140, y, f"Test: {service.name}")
            y -= 15
        y -= 30

        if y < 50:  # Create a new page if the content exceeds the page
            p.showPage()
            y = 740

    p.showPage()
    p.save()
    return response