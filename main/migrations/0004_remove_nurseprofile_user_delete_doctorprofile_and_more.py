# Generated by Django 5.1 on 2024-11-17 09:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0002_alter_doctorearnings_doctor'),
        ('main', '0003_doctorprofile_nurseprofile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='nurseprofile',
            name='user',
        ),
        migrations.DeleteModel(
            name='DoctorProfile',
        ),
        migrations.DeleteModel(
            name='NurseProfile',
        ),
    ]
