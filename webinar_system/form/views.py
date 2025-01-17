from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import uuid
import requests
import json
from common.decorators import role_required
from django.contrib.auth.decorators import login_required
from photo.models import Photos
import cloudinary
from webinar.models import Webinar
from .forms import FormBuilderForm, DynamicForm
from .models import Form, FormSubmission
from authentication.models import WebinarJoin
from django.core.exceptions import ValidationError


# Create your views here.
@login_required(login_url="/login/")
@csrf_exempt
def view_form(request, form_id):
    form_instance = get_object_or_404(Form, id=form_id)
    form_data = form_instance.fields  # Get the field definitions from the Form model

    if request.method == 'POST':
        dynamic_form = DynamicForm(request.POST, fields=form_data)
        if dynamic_form.is_valid():
            try:
                submission = dynamic_form.save_submission(form_instance, request.user)
                return JsonResponse({'status': 'success', 'message': 'Form submitted successfully!'})
            except ValidationError as e:
                # Convert ValidationError into a dictionary
                errors = e.message_dict if hasattr(e, 'message_dict') else {None: e.messages}
                return JsonResponse({'status': 'error', 'errors': errors})
        else:
            return JsonResponse({'status': 'error', 'errors': dynamic_form.errors})
    
    dynamic_form = DynamicForm(fields=form_data)
    if request.user.role =="H":
        return render(request, 'view_form.html', {'form': dynamic_form, 'form_instance': form_instance})
    elif form_instance.active:
        return render(request, 'view_form.html', {'form': dynamic_form, 'form_instance': form_instance})
    else:
        return render(request, 'closed_form.html')


@login_required(login_url="/login/")
@role_required(allowed_roles=["H"])
@csrf_exempt
def make_form(request, webinar_id):
    webinar = get_object_or_404(Webinar, id=webinar_id)
    if webinar.user != request.user:
        return HttpResponseForbidden("You don't have permission to create a form for this webinar")
    
    if request.method == "POST":
        form = FormBuilderForm(request.POST)
        if form.is_valid():
            form_instance = form.save(commit=False)
            form_instance.user = request.user
            form_instance.webinar = webinar
            
            # Process the dynamic fields from JSON
            fields_data = json.loads(request.POST.get('fields', '[]'))
            form_instance.fields = fields_data
            print('INIIII')
            print(fields_data)
            
            form_instance.save()
            return JsonResponse({
                'status': 'success', 
                'id': str(form_instance.id),
                'redirect_url': reverse('webinar:webinar_home')
                                        # , kwargs={'form_id': str(form_instance.id)})
            })
        return JsonResponse({'status': 'error', 'errors': form.errors})
    
    form = FormBuilderForm()
    return render(request, 'make_form.html', {
        'form': form,
        'webinar': webinar,
        'field_types': FormBuilderForm.FIELD_TYPES
    })

@login_required(login_url="/login/")
@role_required(allowed_roles=["H"])
@csrf_exempt
def update_verified(request, form_id):
    form_instance = get_object_or_404(Form, id=form_id)
    submissions = form_instance.submissions.all()

    if request.method == 'POST':
        for submission in submissions:
            checkbox_name = f'verify_{submission.id}'
            if checkbox_name in request.POST:
                submission.verified = True
                sub = WebinarJoin.objects.filter(user=submission.user,regist_form=form_instance).first()
                sub.verified = True
                sub.save()
            else:
                submission.verified = False
                sub = WebinarJoin.objects.filter(user=submission.user,regist_form=form_instance).first()
                sub.verified = False
                sub.save()
            submission.save()

        return redirect('webinar:view_webinar', webinar_id=form_instance.webinar.id)
    
    return HttpResponseBadRequest("Invalid request")

@login_required(login_url="/login/")
@role_required(allowed_roles=["H"])
@csrf_exempt
def edit_form(request, form_id):
    form_instance = get_object_or_404(Form, id=form_id)
    
    # Check if the user is the owner of the form
    if form_instance.user != request.user:
        return HttpResponseForbidden("You don't have permission to edit this form")

    if request.method == "POST":
        form = FormBuilderForm(request.POST, instance=form_instance)
        
        if form.is_valid():
            form_instance = form.save(commit=False)
            form_instance.user = request.user

            # Process the dynamic fields from JSON
            fields_data = json.loads(request.POST.get('fields', '[]'))
            form_instance.fields = fields_data
            form_instance.save()
            
            return JsonResponse({
                'status': 'success', 
                'id': str(form_instance.id),
                'redirect_url': reverse('webinar:webinar_home')
            })
        return JsonResponse({'status': 'error', 'errors': form.errors})

    # For GET requests, we need to render the form with the existing data
    form = FormBuilderForm(instance=form_instance)
    context = {
        'form': form,
        'form_instance': form_instance,
        'field_types': FormBuilderForm.FIELD_TYPES,
    }
    return render(request, 'edit_form.html', context)

@login_required(login_url="/login/")
@role_required(allowed_roles=["H"])
@csrf_exempt
def delete_form(request, form_id):
    form_instance = get_object_or_404(Form, id=form_id)
    webinar_id = form_instance.webinar.id
    form_instance.delete()
    messages.success(request, 'Form deleted successfully.')
    return redirect('webinar:view_webinar', webinar_id=webinar_id)

@login_required(login_url="/login/")
@role_required(allowed_roles=["H"])  # Assuming 'H' role is for admin
@csrf_exempt
def form_submission(request, form_id):
    # Get the form object or return a 404 if not found
    form_instance = get_object_or_404(Form, id=form_id)

    # Get all form submissions related to this form
    submissions = FormSubmission.objects.filter(form=form_instance)
    print(submissions)

    if request.method == 'POST':
        for submission in submissions:
            checkbox_name = f'verify_{submission.id}'
            if checkbox_name in request.POST:
                submission.verified = True
                # Update the related WebinarJoin instance
                WebinarJoin.objects.filter(
                    user=submission.user,
                    regist_form=form_instance
                ).update(verified=True)
            else:
                submission.verified = False
                WebinarJoin.objects.filter(
                    user=submission.user,
                    regist_form=form_instance
                ).update(verified=False)
            submission.save()

    # Pass form and submissions to the template
    context = {
        'form_instance': form_instance,
        'submissions': submissions
    }

    return render(request, 'form_submission.html', context)

@login_required(login_url="/login/")
@role_required(allowed_roles=["H"])
@csrf_exempt
def api_form(request):
    return
