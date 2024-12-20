# Generated by Django 5.1.3 on 2024-11-30 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('departments', '0009_floor_room_bed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bed',
            name='bed_number',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='room',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterUniqueTogether(
            name='bed',
            unique_together={('bed_number', 'room')},
        ),
        migrations.AlterUniqueTogether(
            name='room',
            unique_together={('name', 'floor')},
        ),
    ]
