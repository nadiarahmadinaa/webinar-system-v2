# Generated by Django 5.1.4 on 2025-01-10 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0005_formsubmission_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='form',
            name='type',
            field=models.CharField(choices=[('Registration', 'Registration'), ('Attendance', 'Attendance')], max_length=36),
        ),
    ]
