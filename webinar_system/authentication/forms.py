from django import forms
from django.contrib.auth.forms import UserCreationForm

from authentication.models import User


class CustomRegisterForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    email = forms.EmailField(max_length=70, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + (
            "role",
            "phone_number",
            "email",
        )

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if phone_number and not phone_number.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        return phone_number
