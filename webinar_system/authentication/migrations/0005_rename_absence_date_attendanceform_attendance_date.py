# Generated by Django 5.1.4 on 2025-01-10 12:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_attendanceform'),
    ]

    operations = [
        migrations.RenameField(
            model_name='attendanceform',
            old_name='absence_date',
            new_name='attendance_date',
        ),
    ]