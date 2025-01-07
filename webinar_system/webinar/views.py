from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from .models import Webinar, User
from .forms import WebinarForm
from django.views.decorators.csrf import csrf_exempt
import uuid
import io
import zipfile
from PIL import Image
import requests
import json
from common.decorators import role_required
from django.contrib.auth.decorators import login_required

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png'}

def parse_form_fields(webinar):
    # Implement the form field parsing logic here
    pass

def get_specific_user_data(webinar, participants, field, name, email):
    # Implement specific user data retrieval logic here
    pass

def generate_serial_numbers(count):
    # Implement serial number generation logic here
    pass

def get_participant_data(webinar, passing_grade):
    # Implement participant data retrieval logic here
    pass

# CRUD webinar

@login_required(login_url="/login/")
@role_required(allowed_roles=["H"])
def webinar_home(request):
    webinars = Webinar.objects.filter(user=request.user)
    context = {
        'webinars' : webinars
    }
    return render(request, 'webinar_home.html', context)

@login_required(login_url="/login/")
@role_required(allowed_roles=["H"])
def view_webinar(request, webinar_id):
    webinar = get_object_or_404(Webinar, id=webinar_id)
    context = {
        'webinar': webinar
    }
    return render(request, 'view_webinar.html', context)

@login_required(login_url="/login/")
@role_required(allowed_roles=["H"])
@csrf_exempt
def make_webinar(request):
    context = {}  
    if request.method == 'POST':
        form = WebinarForm(request.POST)
        if form.is_valid():
            webinar = form.save(commit=False)
            webinar.user = request.user
            webinar.save()
            link = reverse('webinar:view_webinar', args=[webinar.id])
            return redirect('/webinar')
            # return render(request, 'webinar_home.html', {'messages': "Successfully created webinar"})
        else:
            context['form'] = form
    else:
        form = WebinarForm()
        context['form'] = form

    return render(request, 'make_webinar.html', context)


@login_required(login_url="/login/")
@role_required(allowed_roles=["H"])
@csrf_exempt
def edit_webinar(request, webinar_id):
    context = {}
    webinar = get_object_or_404(Webinar, id=webinar_id)
    if request.user != webinar.user:
        messages.error(request, 'You are not authorized to edit the webinar.')
        return redirect('webinar_home')

    if request.method == 'POST':
        form = WebinarForm(request.POST, instance=webinar)
        if form.is_valid():
            form.save()
            # link = reverse('view_webinar', args=[webinar.id])
            return redirect('/webinar')
        else:
            return render(request, 'edit_webinar.html', {'form': form, 'webinar': webinar})
    else:
        form = WebinarForm(instance=webinar)
        context = {
            'form': form, 
            'webinar': webinar,
        }
    return render(request, 'edit_webinar.html', context)

@login_required(login_url="/login/")
@role_required(allowed_roles=["H"])
@csrf_exempt
def delete_webinar(request, webinar_id):
    webinar = get_object_or_404(Webinar, id=webinar_id)
    if request.user != webinar.user:
        return redirect('/webinar')

    webinar.delete()
    return redirect('/webinar')

# CRUD API
@login_required(login_url="/login/")
@role_required(allowed_roles=["H"])
def api_webinar(request):
    webinars = Webinar.objects.all().values('id', 'webinar_name', 'date', 'time', 'organizer')
    return JsonResponse({'webinars': list(webinars)})

# certificate generation

@csrf_exempt
def generate_certificates(request, webinar_id):
    webinar = get_object_or_404(Webinar, id=webinar_id)
    if request.user != webinar.user:
        messages.error(request, 'You are not authorized to generate certificates.')
        return redirect('login')

    if request.method == 'POST':
        template_file = request.FILES.get('template')
        if not template_file or not allowed_file(template_file.name):
            messages.error(request, 'Please upload a PNG file.')
            return redirect('view_webinar', webinar_id=webinar.id)

        webinar_serial = request.POST.get('serial_number', '')
        webinar.serial_number = webinar_serial
        webinar.save()

        # Additional logic for generating certificates
        # ...

        return redirect('generate_certificates_preview', webinar_id=webinar.id)

    return render(request, 'generate_certificates.html', {'webinar': webinar})

def certif_verif(request, webinar_id):
    webinar = get_object_or_404(Webinar, id=webinar_id)
    if request.user != webinar.user:
        messages.error(request, 'You are not authorized to view the webinar.')
        return redirect('login')

    participants_data = [{'form_name': name, 'data': {}} for name, email in json.loads(webinar.certified_participants)]
    return render(request, 'certif_verif.html', {'webinar': webinar, 'participants_data': participants_data})

@login_required(login_url="/login/")
@role_required(allowed_roles=["H"])
@csrf_exempt
def generate_certificates_preview(request, webinar_id):
    webinar = get_object_or_404(Webinar, id=webinar_id)
    file_url = request.GET.get('file')
    qr_url = request.GET.get('qr_url')
    generate_qr = request.GET.get('generate_qr') == 'true'

    if request.method == 'POST':
        # Handle form submission logic
        # ...
        return JsonResponse({'status': 'success'})

    return render(request, 'generate_certificates_preview.html', {
        'webinar': webinar,
        'image_url': file_url,
        'qr_url': qr_url,
        'generate_qr': generate_qr
    })

