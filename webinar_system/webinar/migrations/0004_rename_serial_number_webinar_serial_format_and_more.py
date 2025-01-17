# Generated by Django 5.1.4 on 2025-01-10 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webinar', '0003_webinar_auto_verify_webinar_data_keys_webinar_qr'),
    ]

    operations = [
        migrations.RenameField(
            model_name='webinar',
            old_name='serial_number',
            new_name='serial_format',
        ),
        migrations.AddField(
            model_name='webinar',
            name='serial_increment',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
