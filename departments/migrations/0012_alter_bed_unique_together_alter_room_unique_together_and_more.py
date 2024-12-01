# Generated by Django 5.1.3 on 2024-12-01 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('departments', '0011_bed_price'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='bed',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='room',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='bed',
            name='bed_number',
            field=models.CharField(max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='room',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.RemoveField(
            model_name='bed',
            name='price',
        ),
    ]