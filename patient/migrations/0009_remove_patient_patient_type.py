# Generated by Django 5.1.3 on 2024-11-27 09:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0008_patient_patient_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='patient',
            name='patient_type',
        ),
    ]