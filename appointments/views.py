import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from main.templatetags.permissions import has_permission  
from django.contrib import messages
from .models import Appointment, Invoice
from .forms import AppointmentForm, AddServiceForm, AddMedicationForm, AddConsumableForm
from datetime import datetime, timedelta
from departments.models import Service, Department
from django.http import JsonResponse
from main.models import CustomUser 
from departments.utils import get_doctors_by_department, get_services_by_department
from django.http import HttpResponse
from reportlab.pdfgen import canvas


# Create Appointment
@login_required
@user_passes_test(lambda u: has_permission(u, "add_appointment"))
def create_appointment(request):
    service_queryset = Service.objects.none()

    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            # Save the appointment instance first
            appointment = form.save(commit=False)
            appointment.save()

            # Now set the many-to-many relationship
            services_selected = form.cleaned_data.get('services', [])
            appointment.services.set(services_selected)

            # Calculate and save total cost
            appointment.total_cost = sum(service.price for service in services_selected)
            appointment.save(update_fields=["total_cost"])

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


# Generate Bills
@login_required
@user_passes_test(lambda u: has_permission(u, "generate_invoice"))
def generate_invoice(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Create or retrieve the invoice
    invoice, created = Invoice.objects.get_or_create(
        appointment=appointment,
        defaults={"total_amount": appointment.total_cost, "status": "unpaid"},
    )

    if request.method == "POST":
        # Update invoice status
        invoice.status = "paid"
        invoice.save()

        # Update appointment status
        appointment.payment_status = "paid"
        appointment.save(update_fields=["payment_status"])

        messages.success(request, f"Payment for Appointment #{appointment.id} has been marked as paid.")
        return redirect("appointments_list")

    return render(request, 'appointments/generate_invoice.html', {
        'appointment': appointment,
        'invoice': invoice,
    })



# PDF Invoice
@login_required
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
@login_required
@user_passes_test(lambda u: has_permission(u, "view_appointment"))
def appointments_list(request):
    appointments = Appointment.objects.all()
    return render(request, 'appointments/appointment_list.html', {'appointments': appointments})


# View details of a specific appointment
@login_required
@user_passes_test(lambda u: has_permission(u, "view_appointment"))
def view_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    return render(request, 'appointments/view_appointment.html', {'appointment': appointment})

# Update status to in-progress (doctor starts the appointment)
@login_required
@user_passes_test(lambda u: has_permission(u, "update_appointment_status"))
def start_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'in_progress'
    appointment.save()
    messages.success(request, "Appointment status updated to 'In Progress'.")
    return redirect('view_appointment', appointment_id=appointment.id)

# Update status to awaiting test (doctor orders a test)
@login_required
@user_passes_test(lambda u: has_permission(u, "update_appointment_status"))
def mark_awaiting_test(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'awaiting_test'
    appointment.save()
    messages.success(request, "Appointment status updated to 'Awaiting Test'.")
    return redirect('view_appointment', appointment_id=appointment.id)

# Update status to completed (doctor finishes the appointment)
@login_required
@user_passes_test(lambda u: has_permission(u, "update_appointment_status"))
def complete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'completed'
    appointment.save()
    messages.success(request, "Appointment marked as 'Completed'.")
    return redirect('view_appointment', appointment_id=appointment.id)



# Cancel an appointment (no delete functionality)
@login_required
@user_passes_test(lambda u: u.has_perm('appointments.cancel_appointment'))  
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
@login_required
@user_passes_test(lambda u: has_permission(u, "view_calendar"))
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


@login_required
def process_payment(request, appointment_id):
    if request.method == 'POST':
        appointment = get_object_or_404(Appointment, id=appointment_id)

        # Ensure the invoice exists
        invoice, created = Invoice.objects.get_or_create(
            appointment=appointment,
            defaults={"total_amount": appointment.total_cost, "status": "unpaid"}
        )

        # Mark the invoice and appointment as paid
        invoice.status = 'paid'
        invoice.save()
        appointment.payment_status = 'paid'
        appointment.save(update_fields=['payment_status'])

        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)





@login_required
@user_passes_test(lambda u: u.has_perm('appointments.add_service'))
def add_service_to_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        form = AddServiceForm(request.POST)
        if form.is_valid():
            service = form.cleaned_data['service']
            try:
                appointment.add_service(service.id)
                messages.success(request, f"Service {service.name} added successfully.")
            except Exception as e:
                messages.error(request, str(e))
            return redirect('view_appointment', appointment_id=appointment.id)
    else:
        form = AddServiceForm()
    return render(request, 'appointments/add_service.html', {'form': form, 'appointment': appointment})

@login_required
@user_passes_test(lambda u: u.has_perm('appointments.add_medication'))
def add_medication_to_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        form = AddMedicationForm(request.POST)
        if form.is_valid():
            medication = form.cleaned_data['medication']
            quantity = form.cleaned_data['quantity']
            try:
                appointment.add_medication(medication.id, quantity)
                messages.success(request, f"Medication {medication.name} added successfully.")
            except Exception as e:
                messages.error(request, str(e))
            return redirect('view_appointment', appointment_id=appointment.id)
    else:
        form = AddMedicationForm()
    return render(request, 'appointments/add_medication.html', {'form': form, 'appointment': appointment})

@login_required
@user_passes_test(lambda u: u.has_perm('appointments.add_consumable'))
def add_consumable_to_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        form = AddConsumableForm(request.POST)
        if form.is_valid():
            consumable = form.cleaned_data['consumable']
            quantity = form.cleaned_data['quantity']
            try:
                appointment.add_consumable(consumable.id, quantity)
                messages.success(request, f"Consumable {consumable.name} added successfully.")
            except Exception as e:
                messages.error(request, str(e))
            return redirect('view_appointment', appointment_id=appointment.id)
    else:
        form = AddConsumableForm()
    return render(request, 'appointments/add_consumable.html', {'form': form, 'appointment': appointment})
