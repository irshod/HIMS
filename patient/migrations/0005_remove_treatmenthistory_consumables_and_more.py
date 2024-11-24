# Generated by Django 5.1.3 on 2024-11-24 10:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0009_treatmentconsumable_treatmenthistory_and_more'),
        ('patient', '0004_remove_ipdmedication_medication_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='treatmenthistory',
            name='consumables',
        ),
        migrations.RemoveField(
            model_name='treatmenthistory',
            name='appointment',
        ),
        migrations.RemoveField(
            model_name='treatmenthistory',
            name='doctor',
        ),
        migrations.RemoveField(
            model_name='treatmenthistory',
            name='medications',
        ),
        migrations.RemoveField(
            model_name='treatmenthistory',
            name='patient',
        ),
        migrations.RemoveField(
            model_name='treatmentmedication',
            name='treatment_history',
        ),
        migrations.RemoveField(
            model_name='treatmentmedication',
            name='medication',
        ),
        migrations.RenameField(
            model_name='patient',
            old_name='email',
            new_name='emergency_contact_email',
        ),
        migrations.RenameField(
            model_name='patient',
            old_name='emergency_contact',
            new_name='emergency_contact_number',
        ),
        migrations.RemoveField(
            model_name='patient',
            name='patient_type',
        ),
        migrations.AddField(
            model_name='patient',
            name='emergency_contact_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='patient',
            name='emergency_contact_relationship',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='prescription',
            name='appointment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='appointments.appointment'),
        ),
        migrations.CreateModel(
            name='PatientInsurance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider_name', models.CharField(help_text='Insurance provider name', max_length=100)),
                ('policy_number', models.CharField(help_text='Insurance policy number', max_length=50)),
                ('coverage_start_date', models.DateField()),
                ('coverage_end_date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='insurance_details', to='patient.patient')),
            ],
        ),
        migrations.CreateModel(
            name='PatientMedicalHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('condition', models.CharField(help_text='Medical condition or diagnosis', max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('diagnosis_date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medical_history', to='patient.patient')),
            ],
        ),
        migrations.DeleteModel(
            name='TreatmentConsumable',
        ),
        migrations.DeleteModel(
            name='TreatmentHistory',
        ),
        migrations.DeleteModel(
            name='TreatmentMedication',
        ),
    ]