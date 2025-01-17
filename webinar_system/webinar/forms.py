from django import forms
from .models import Webinar
from datetime import date
import re
from form.models import Form
from django.shortcuts import get_object_or_404

class WebinarForm(forms.ModelForm):
    class Meta:
        model = Webinar
        fields = ['webinar_name', 'date', 'time', 'organizer', 'description', 'auto_verify']
        widgets = {
            'webinar_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Webinar Name'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'organizer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Organizer Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Description'}),
            'auto_verify': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    def clean_date(self):
        date_input = self.cleaned_data.get('date')
        if date_input and date_input <= date.today():
            raise forms.ValidationError("The webinar date must be in the future.")
        return date_input
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        description = re.sub(r'<[^>]+>', '', description)
        return description
    
    def clean_webinar_name(self):
        webinar_name = self.cleaned_data.get('webinar_name')
        return webinar_name

    def clean_organizer(self):
        organizer = self.cleaned_data.get('organizer')
        organizer = re.sub(r'<[^>]+>', '', organizer)
        return organizer
    
    def clean_time(self):
        time_input = self.cleaned_data.get('time')
        return time_input
    
class GenerateCertificateForm(forms.Form):
    qr_make = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'slider-toggle'}),
        label="Generate QR Code for Verification?"
    )

    serial_make = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'slider-toggle'}),
        label="Generate Serial Number?"
    )

    serial_format = forms.CharField(
        max_length=100,
        required=False,
        label="Serial Number Format (Replace incremental value with #)",
        widget=forms.TextInput(attrs={'placeholder': 'e.g., SN-#'})
    )
    
    serial_increment = forms.IntegerField(
        required=False,
        label="Serial Increment Value",
        min_value=1,
        initial=1
    )

    attendance_make = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'slider-toggle'}),
        label="Count Attendance?"
    )

    attendance_percentage = forms.FloatField(
        required=False,
        label="Attendance percentage",
        min_value=0,
        initial=0
    )

    def __init__(self, *args, **kwargs):
        # Initialize form with dynamic choices for selected_data field
        webinar_id = kwargs.pop('webinar_id', None)
        webinar = get_object_or_404(Webinar, id=webinar_id)
        super().__init__(*args, **kwargs)

        if webinar_id:
            # Fetch related Form objects
            related_forms = Form.objects.filter(webinar=webinar)
            # Get all unique keys from the Form.data JSON field
            data_keys = set()
            full_data = {}
            for form in related_forms:
                for field in form.fields:
                    print(field['label'])
                    data_keys.add(field['label'])
                    full_data[field['label']] = form.name
            print(data_keys)
            print(full_data)

            webinar.set_full_data(full_data)
            webinar.set_data_keys(list(data_keys))
            webinar.save()

class CertificateGenerationForm(forms.Form):
    template = forms.FileField(required=True, label='Upload Template')
    serial_number = forms.CharField(max_length=100, required=True, label='Serial Number', 
                                    widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Serial Number'}))
    generate_qr = forms.BooleanField(required=False, label='Generate QR Code')
    passing_grade = forms.FloatField(required=True, label='Passing Grade',
                                     widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Passing Grade'}))
    font_size = forms.FloatField(required=True, label='Font Size',
                                 widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Font Size'}))
    input_method = forms.ChoiceField(choices=[('placeholder', 'Placeholder'), ('manual', 'Manual')], required=True, label='Input Method',
                                     widget=forms.Select(attrs={'class': 'form-control'}))
    placeholder = forms.CharField(required=False, label='Placeholder Data',
                                  widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Placeholder Data'}))
    text_data = forms.CharField(required=True, label='Text Data',
                                widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Text Data'}))
    use_qr = forms.BooleanField(required=False, label='Use QR Code')
    qr_data = forms.CharField(required=False, label='QR Code Data',
                              widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter QR Code Data'}))
    qr_url = forms.URLField(required=False, label='QR Code URL',
                            widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter QR Code URL'}))
    preview_width = forms.FloatField(required=False, label='Preview Width',
                                     widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Preview Width'}))
