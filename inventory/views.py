from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Medication, Consumable
from .forms import MedicationForm, ConsumableForm
from django.http import JsonResponse

# Medication Views
def medication_list(request):
    medications = Medication.objects.all()
    return render(request, 'inventory/medication_list.html', {'medications': medications})

def medication_add(request):
    if request.method == 'POST':
        form = MedicationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Medication added successfully!")
            return redirect('medication_list')
    else:
        form = MedicationForm()
    return render(request, 'inventory/medication_form.html', {'form': form})

def medication_edit(request, pk):
    medication = get_object_or_404(Medication, pk=pk)
    if request.method == 'POST':
        form = MedicationForm(request.POST, instance=medication)
        if form.is_valid():
            form.save()
            messages.success(request, "Medication updated successfully!")
            return redirect('medication_list')
    else:
        form = MedicationForm(instance=medication)
    return render(request, 'inventory/medication_form.html', {'form': form})

@login_required
def medication_delete(request, pk):
    medication = get_object_or_404(Medication, pk=pk)
    if request.method == 'POST':
        medication.delete()
        messages.success(request, f"'{medication.name}' has been deleted.")
        return redirect('medication_list')
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

@login_required
def medicine_details(request, medicine_id):
    try:
        medicine = Medication.objects.get(id=medicine_id)
        return JsonResponse({
            'name': medicine.name,
            'dosage': medicine.dosage,
            'price': str(medicine.unit_price),  
        })
    except Medication.DoesNotExist:
        return JsonResponse({'error': 'Medicine not found'}, status=404)


# Consumable Views
def consumable_list(request):
    consumables = Consumable.objects.all()
    return render(request, 'inventory/consumable_list.html', {'consumables': consumables})

def consumable_add(request):
    if request.method == 'POST':
        form = ConsumableForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Consumable added successfully!")
            return redirect('consumable_list')
    else:
        form = ConsumableForm()
    return render(request, 'inventory/consumable_form.html', {'form': form})

def consumable_edit(request, pk):
    consumable = get_object_or_404(Consumable, pk=pk)
    if request.method == 'POST':
        form = ConsumableForm(request.POST, instance=consumable)
        if form.is_valid():
            form.save()
            messages.success(request, "Consumable updated successfully!")
            return redirect('consumable_list')
    else:
        form = ConsumableForm(instance=consumable)
    return render(request, 'inventory/consumable_form.html', {'form': form})

@login_required
def consumable_delete(request, pk):
    consumable = get_object_or_404(Consumable, pk=pk)
    if request.method == 'POST':
        consumable.delete()
        messages.success(request, f"'{consumable.name}' has been deleted.")
        return redirect('medication_list')
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)