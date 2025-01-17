from django.db import models
from cloudinary.models import CloudinaryField
import uuid
from webinar.models import Webinar

# Create your models here.

class Photos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.URLField(max_length=200, blank=True)
    webinar = models.ForeignKey(Webinar, related_name='photos', on_delete=models.CASCADE, null=True, blank=True)