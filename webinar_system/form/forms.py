from django import forms
from .models import Form, FormSubmission
from authentication.models import WebinarJoin, AttendanceForm

class FormBuilderForm(forms.ModelForm):
    FIELD_TYPES = [
        ('text', 'Text Input'),
        ('email', 'Email Input'),
        ('number', 'Number Input'),
        ('paragraph', 'Paragraph Text'),
        ('file', 'File Upload'),
        ('date', 'Date Input'),
        ('phone', 'Phone Number'),
        ('checkbox', 'Checkbox'),
        ('radio', 'Radio Buttons'),
        ('select', 'Dropdown Select')
    ]
    
    class Meta:
        model = Form
        fields = ['name', 'type', 'active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'active': forms.CheckboxInput(attrs={
                'class': 'sr-only peer'
            })
        }

class DynamicForm(forms.Form):
    FIELD_TYPE_MAPPING = {
        'text': forms.CharField,
        'email': forms.EmailField,
        'number': forms.IntegerField,
        'paragraph': lambda **kwargs: forms.CharField(widget=forms.Textarea, **kwargs),
        'file': forms.URLField,
        'date': forms.DateField,
        'phone': forms.CharField,  # You can add custom validation for phone numbers if needed
        'checkbox': lambda **kwargs: forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, **kwargs),
        'radio': lambda **kwargs: forms.ChoiceField(widget=forms.RadioSelect, **kwargs),
        'select': forms.ChoiceField,
    }

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', [])
        super(DynamicForm, self).__init__(*args, **kwargs)

        for field in fields:
            field_type = field.get('type')
            label = field.get('label', '')
            required = field.get('required', False)
            field_values = field.get('values', [])

            # Select the appropriate field class from the mapping
            field_class = self.FIELD_TYPE_MAPPING.get(field_type)
            if field_class:
                field_kwargs = {'label': label, 'required': required}

                # For 'checkbox', 'radio', and 'select', we handle choices separately
                if field_type in ['checkbox', 'radio', 'select']:
                    field_kwargs['choices'] = [(value, value) for value in field_values]
                
                # Create the field and add it to the form
                self.fields[label] = field_class(**field_kwargs)

    def save_submission(self, form, user):
        if self.is_valid():
            submission_data = {
                field_name: self.cleaned_data[field_name]
                for field_name in self.cleaned_data
            }
            print("+++>< HERE")
            print(submission_data)
            form_submission = FormSubmission(
                        form=form,
                        data=submission_data,
                        user=user
                    )
            form_submission.save()
            webinar = form.webinar
            if form.type == "Registration":                
                existing_registration = WebinarJoin.objects.filter(user=user, webinar=webinar).exists()
                
                if not existing_registration:
                    if webinar.auto_verify:
                        webinar_join = WebinarJoin(
                            user=user,
                            webinar=webinar,
                            regist_form=form,
                            form_submission = form_submission,
                            verified=True,
                        )
                    else:
                        webinar_join = WebinarJoin(
                            user=user,
                            regist_form=form,
                            webinar=webinar,
                            form_submission = form_submission,
                        )
                    print(webinar_join)
                    webinar_join.save()
                else:
                    print(f"User {user.username} has already registered for the webinar.")
                    raise forms.ValidationError("User has registered for this webinar.")
            else:
                existing_registration = WebinarJoin.objects.filter(user=user, webinar=webinar).exists()

                
                if existing_registration:
                    regform = WebinarJoin.objects.filter(user=user, webinar=webinar).first()
                    existing_attendance = AttendanceForm.objects.filter(webinar_join=regform, attendance_form = form).exists()
                    if not existing_attendance:
                        if regform.verified == True:
                            attendance = AttendanceForm(
                                webinar_join=regform,
                                attendance_form = form,
                            )
                            attendance.save()
                            print(attendance)
                        else:
                            raise forms.ValidationError("You have not been verified by the host.")
                    else:
                        raise forms.ValidationError("You have filled in this attendance form.")
                else:
                    print(f"User {user.username} have not registered for the webinar.")
                    raise forms.ValidationError("You have not registered for this webinar.")


            return form_submission
        else:
            raise forms.ValidationError("Form data is not valid.")
