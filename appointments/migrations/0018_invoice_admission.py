# Generated by Django 5.1.3 on 2024-12-03 09:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0017_ipdadmission_bed_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='admission',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invoice', to='appointments.ipdadmission'),
        ),
    ]
