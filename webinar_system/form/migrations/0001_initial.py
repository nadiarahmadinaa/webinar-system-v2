# Generated by Django 5.1.4 on 2025-01-07 10:18

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('webinar', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Form',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('fields', models.JSONField()),
                ('type', models.CharField(max_length=36)),
                ('active', models.BooleanField(default=True)),
                ('webinar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webinar.webinar')),
            ],
        ),
    ]
