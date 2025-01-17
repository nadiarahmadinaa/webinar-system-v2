# Generated by Django 5.1.4 on 2025-01-07 12:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photo', '0001_initial'),
        ('webinar', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='photos',
            name='webinar',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='webinar.webinar'),
        ),
    ]