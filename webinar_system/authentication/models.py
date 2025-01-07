from django.db import models

# Create your models here.
import uuid
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import PermissionDenied

class User(AbstractUser):
    PARTICIPANT = "P"
    HOST = "H"
    ROLE_CHOICES = [
        (HOST, "Host"),
        (PARTICIPANT, "Participant"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=1, choices=ROLE_CHOICES, default=PARTICIPANT)
    phone_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField(max_length=70, blank=True, unique=True)

    def __str__(self):
        return str(id)
