from django.db import models
import uuid
from authentication.models import User

# Create your models here.
class Webinar(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    webinar_name = models.CharField(max_length=200, null=False)
    user = models.ForeignKey("authentication.User", on_delete=models.CASCADE)
    date = models.DateField(null=False)
    time = models.TimeField(null=False)
    organizer = models.CharField(max_length=200, null=False)
    description = models.TextField(max_length=1000, blank=True)
    serial_number = models.CharField(max_length=255, blank=True, null=True)
    certified_participants = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.webinar_name
