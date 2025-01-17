from django.db import models
import uuid
from webinar.models import Webinar
from authentication.models import User, WebinarJoin

# Create your models here.
class Form(models.Model):
    TYPE_CHOICES = [
        ('Registration', 'Registration'),
        ('Attendance', 'Attendance'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("authentication.User", on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=100, null=False)
    webinar = models.ForeignKey(Webinar, on_delete=models.CASCADE)
    fields = models.JSONField(null=False)
    type = models.CharField(max_length=36, null=False, choices=TYPE_CHOICES)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class FormSubmission(models.Model):
    form = models.ForeignKey(Form, related_name='submissions', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='user', on_delete=models.CASCADE, blank=True, null=True)
    data = models.JSONField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        webinar_join = WebinarJoin.objects.filter(form_submission=self).first()
        verified_status = webinar_join.verified if webinar_join else "No WebinarJoin"
        return f"Submission for {self.form.name} at {self.submitted_at} with verified status {verified_status}"