# Generated by Django 5.1.4 on 2025-01-08 04:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photo', '0002_photos_webinar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photos',
            name='image',
            field=models.URLField(blank=True),
        ),
    ]
