# Generated by Django 5.1.3 on 2024-12-01 05:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('departments', '0010_alter_bed_bed_number_alter_room_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bed',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
