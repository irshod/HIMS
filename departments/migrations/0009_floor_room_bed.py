# Generated by Django 5.1.3 on 2024-11-26 18:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('departments', '0008_remove_doctorprofile_default_availability'),
        ('patient', '0008_patient_patient_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Floor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('floor_number', models.IntegerField(unique=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('room_type', models.CharField(choices=[('general', 'General Ward'), ('private', 'Private Room'), ('icu', 'ICU')], default='general', max_length=10)),
                ('description', models.TextField(blank=True, null=True)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rooms', to='departments.department')),
                ('floor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rooms', to='departments.floor')),
            ],
        ),
        migrations.CreateModel(
            name='Bed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bed_number', models.CharField(max_length=10, unique=True)),
                ('status', models.CharField(choices=[('available', 'Available'), ('occupied', 'Occupied'), ('maintenance', 'Maintenance')], default='available', max_length=15)),
                ('current_patient', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bed', to='patient.patient')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='beds', to='departments.room')),
            ],
        ),
    ]
