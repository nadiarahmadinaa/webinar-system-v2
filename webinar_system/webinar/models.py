from django.db import models
import uuid
from authentication.models import User
import json

# Create your models here.
class Webinar(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    webinar_name = models.CharField(max_length=200, null=False)
    user = models.ForeignKey("authentication.User", on_delete=models.CASCADE)
    date = models.DateField(null=False)
    time = models.TimeField(null=False)
    organizer = models.CharField(max_length=200, null=False)
    description = models.TextField(max_length=1000, blank=True)
    serial_format = models.CharField(max_length=255, blank=True, null=True)
    serial_increment = models.IntegerField(blank=True, null=True)
    certified_participants = models.TextField(blank=True, null=True)
    certificate = models.URLField(max_length=200, blank=True)
    qr = models.URLField(max_length=200, blank=True)
    data_keys = models.TextField(blank=True, null=True)
    full_data = models.TextField(blank=True, null=True)
    auto_verify = models.BooleanField(default=True)

    def get_data_keys(self):
        if self.data_keys:
            return json.loads(self.data_keys)
        return []

    def set_data_keys(self, keys):
        self.data_keys = json.dumps(keys)

    def set_full_data(self, info):
        if isinstance(info, dict):
            self.full_data = json.dumps(info)
        else:
            raise ValueError("Info must be a dictionary")
        self.save()

    def get_full_data(self):
        if self.full_data:
            return json.loads(self.full_data)
        return {}

    def get_value_by_key(self, key):
        full_data = self.get_full_data()
        return full_data.get(key)

    def __str__(self):
        return self.webinar_name
