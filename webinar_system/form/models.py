from django.db import models
import uuid
from webinar.models import Webinar

# Create your models here.
class Form(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, null=False)
    webinar = models.ForeignKey(Webinar, on_delete=models.CASCADE)
    fields = models.JSONField(null=False)  # Using JSONField for storing JSON data
    type = models.CharField(max_length=36, null=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name