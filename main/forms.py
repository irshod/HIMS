from django import forms
from django.contrib.auth.models import Permission
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from .models import CustomUser, Role


class RoleCreationForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'dual-list'}),
        required=False,
        label="Permissions"
    )

    class Meta:
        model = Role  
        fields = ['name', 'permissions']
        labels = {'name': 'Role Name'}


class CustomUserCreationForm(DjangoUserCreationForm):
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),  
        required=True,
        label="Role"
    )
    birthdate = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    specialty = forms.CharField(required=False, max_length=100, label="Specialty")
    qualification = forms.CharField(required=False, max_length=100, label="Qualification")
    address = forms.CharField(required=False, max_length=255)
    contact_number = forms.CharField(required=False, max_length=15)

    class Meta(DjangoUserCreationForm.Meta):
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'birthdate', 
            'contact_number', 'address', 'role', 'password1', 'password2'
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            role = self.cleaned_data.get('role')
            if role:
                user.roles.add(role) 
        return user

class CustomUserEditForm(forms.ModelForm):
    role = forms.ModelChoiceField(queryset=Role.objects.all(), required=True, label="Role")

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'birthdate', 'address', 'contact_number']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            role = self.cleaned_data['role']
            user.roles.clear()
            user.roles.add(role)
        return user

