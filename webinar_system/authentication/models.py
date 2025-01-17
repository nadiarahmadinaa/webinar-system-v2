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
    joined_webinars = models.ManyToManyField(
        'webinar.Webinar', related_name='joined_users', through='WebinarJoin'
    )

    def __str__(self):
        return str(id)
    
class WebinarJoin(models.Model):
    user = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    webinar = models.ForeignKey('webinar.Webinar', on_delete=models.CASCADE)
    regist_form = models.ForeignKey('form.Form', on_delete=models.CASCADE, blank=True, null=True)
    join_date = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)
    certified = models.BooleanField(default=False)
    form_submission = models.ForeignKey('form.FormSubmission', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} joined {self.webinar.webinar_name} with stats verified {self.verified} and certified {self.certified}"
    
class AttendanceForm(models.Model):
    webinar_join = models.ForeignKey(WebinarJoin, on_delete=models.CASCADE, related_name='attendance_form')
    attendance_form = models.ForeignKey('form.Form', on_delete=models.CASCADE, blank=True, null=True)
    attendance_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attendance on {self.attendance_date} for {self.webinar_join.user.username} in {self.webinar_join.webinar.webinar_name}"
