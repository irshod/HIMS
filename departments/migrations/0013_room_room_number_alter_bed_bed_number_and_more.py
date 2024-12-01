# Generated by Django 5.1.3 on 2024-12-01 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('departments', '0012_alter_bed_unique_together_alter_room_unique_together_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='room_number',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='bed',
            name='bed_number',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='room',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterUniqueTogether(
            name='bed',
            unique_together={('room', 'bed_number')},
        ),
        migrations.AlterUniqueTogether(
            name='room',
            unique_together={('floor', 'room_number')},
        ),
    ]