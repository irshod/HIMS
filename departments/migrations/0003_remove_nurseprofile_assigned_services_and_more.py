# Generated by Django 5.1 on 2024-11-17 08:02

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('departments', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='nurseprofile',
            name='assigned_services',
        ),
        migrations.RemoveField(
            model_name='nurseprofile',
            name='user',
        ),
        migrations.RemoveField(
            model_name='department',
            name='doctors',
        ),
        migrations.RemoveField(
            model_name='department',
            name='nurses',
        ),
        migrations.AddField(
            model_name='service',
            name='category',
            field=models.CharField(blank=True, choices=[('diagnostics', 'Diagnostics'), ('surgery', 'Surgery'), ('consultation', 'Consultation')], max_length=50, null=True),
        ),
        migrations.CreateModel(
            name='StaffAvailability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('available', 'Available'), ('not_available', 'Not Available'), ('vacation', 'On Vacation')], default='available', max_length=15)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='staff_availability', to='departments.department')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='DoctorProfile',
        ),
        migrations.DeleteModel(
            name='NurseProfile',
        ),
    ]
