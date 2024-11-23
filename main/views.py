from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import CustomUser, Role
from .forms import CustomUserCreationForm, CustomUserEditForm, RoleCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator

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

@login_required
def dashboard_view(request):
    return render(request, 'main/dashboard.html')

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
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, f"User '{user.email}' has been deleted.")
        return JsonResponse({"status": "success", "message": f"User '{user.email}' deleted successfully"})
    return JsonResponse({"status": "error", "message": "Invalid request"})

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
def delete_role(request, role_id):
    role = get_object_or_404(Role, id=role_id)  # Updated to fetch Role model object
    if request.method == 'POST':
        role.delete()
        messages.success(request, f"Role '{role.name}' has been deleted.")
        return JsonResponse({"status": "success", "message": f"Role '{role.name}' deleted successfully"})
    return JsonResponse({"status": "error", "message": "Invalid request"})

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

