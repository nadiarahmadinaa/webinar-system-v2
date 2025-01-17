from django.shortcuts import render
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from .models import Webinar
from .forms import WebinarForm, GenerateCertificateForm
from authentication.models import WebinarJoin, AttendanceForm
from form.forms import Form
from form.models import FormSubmission
from django.views.decorators.csrf import csrf_exempt
import uuid
from io import BytesIO
import io
import zipfile
from PIL import Image, ImageDraw, ImageFont
import requests
import json
from common.decorators import role_required
from django.contrib.auth.decorators import login_required
from photo.models import Photos
import cloudinary
import qrcode

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

            certificate_url = request.POST.get('certificate_url')
            if certificate_url:
                webinar.certificate = certificate_url
                webinar.save()

            photos_urls = request.POST.get('photos_url')
            if photos_urls:
                photo_urls_list = photos_urls.split(',')
                for photo_url in photo_urls_list:
                    Photos.objects.create(webinar=webinar, image=photo_url)

            return redirect('/webinar')
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
    webinar = get_object_or_404(Webinar, id=webinar_id)
    if request.user != webinar.user:
        messages.error(request, 'You are not authorized to edit the webinar.')
        return redirect('webinar_home')

    if request.method == 'POST':
        form = WebinarForm(request.POST, request.FILES, instance=webinar)
        if form.is_valid():
            webinar = form.save()

            certificate_url = request.POST.get('certificate_url')
            if certificate_url:
                webinar.certificate = certificate_url
                webinar.save()

            photos_urls = request.POST.get('photos_url')
            if photos_urls:
                photo_urls_list = photos_urls.split(',')
                for photo_url in photo_urls_list:
                    Photos.objects.create(webinar=webinar, image=photo_url)

            return redirect('/webinar')
        else:
            return render(request, 'edit_webinar.html', {'form': form, 'webinar': webinar})
    else:
        form = WebinarForm(instance=webinar)
        return render(request, 'edit_webinar.html', {'form': form, 'webinar': webinar})


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

# Certificate generation

@login_required(login_url="/login/")
@role_required(allowed_roles=["H"])
@csrf_exempt
def generate_certificates(request, webinar_id):
    webinar = get_object_or_404(Webinar, id=webinar_id)
    
    if request.method == 'POST':
        form = GenerateCertificateForm(request.POST, webinar_id=webinar_id)
        if form.is_valid():
            generate_qr = form.cleaned_data.get('qr_make')
            if generate_qr:
                qr_data = request.build_absolute_uri(reverse('webinar:verify_page', kwargs={'webinar_id': webinar.id}))
                qr = qrcode.make(qr_data)
                qr_bytes = io.BytesIO()
                qr.save(qr_bytes, format='PNG')
                qr_bytes.seek(0)
                
                response = cloudinary.uploader.upload(qr_bytes, resource_type='image')
                webinar.qr = response['secure_url']
                webinar.save()

            generate_serial = form.cleaned_data.get('serial_make')
            if generate_serial:
                serial_format = form.cleaned_data.get('serial_format')
                serial_increment = form.cleaned_data.get('serial_increment')
                webinar.serial_format = serial_format
                webinar.serial_increment = serial_increment
                webinar.save()

            generate_attendance = form.cleaned_data.get('attendance_make')
            if generate_attendance:
                attendance_percentage = form.cleaned_data.get('attendance_percentage')
                all_attendance = Form.objects.filter(webinar=webinar, type='Attendance').count()
                print("ALL ATTENDANCE: ", all_attendance)
                all_participants = WebinarJoin.objects.filter(webinar=webinar)
                
                if all_attendance != 0:
                    for participant in all_participants:
                        attendance_forms = participant.attendance_form.all().count() 
                        print("ATTENDANCE ADMIN: ", attendance_forms)              
                        attendance_ratio = (attendance_forms / all_attendance) * 100
                        if attendance_ratio >= attendance_percentage:
                            participant.certified = True
                            print("=====>>>> DISINI")
                            print(participant)
                            participant.save()
            return JsonResponse({'status': 'success', 'message': "YAY"})
            # return HttpResponseRedirect(reverse('webinar:generate_certificates_preview', kwargs={'webinar_id': webinar.id}))
            # return redirect(f'/webinar/generate_certificates_preview/{webinar_id}/')
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})

    else:
        form = GenerateCertificateForm(webinar_id=webinar_id)
    
    return render(request, 'generate_certificate.html', {'form': form, 'webinar': webinar})

@login_required(login_url="/login/")
@role_required(allowed_roles=["H"])
@csrf_exempt
def generate_certificates_preview(request, webinar_id):
    webinar = get_object_or_404(Webinar, id=webinar_id)
    data_keys = webinar.get_data_keys()
    certificate_url = webinar.certificate

    response = requests.get(certificate_url)
    response.raise_for_status()

    certificate_image = Image.open(BytesIO(response.content))

    image_width, image_height = certificate_image.size

    if request.method == 'POST':
        qr_position = json.loads(request.POST.get('qr_position', '{}'))
        qr_size = request.POST.get('qr_size', '100px')
        text_data = json.loads(request.POST.get('text_data', '[]'))

        response = requests.get(webinar.certificate)
        if qr_position != {}:
            response_qr = requests.get(webinar.qr)
            qr_image = Image.open(BytesIO(response_qr.content))
        certificate_image = Image.open(BytesIO(response.content))

        print("QR Position:", qr_position)
        print("QR Size:", qr_size)
        print("Text Data:", text_data)
        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            verified_certified_users = WebinarJoin.objects.filter(
                webinar=webinar, verified=True, certified=True
            )
            for participant in verified_certified_users:
                draw = ImageDraw.Draw(certificate_image)
                for text_item in text_data:
                    content = text_item['content']
                    position = text_item['position']
                    size = text_item['size']
                    font_name = text_item['font']
                    color = text_item['color']

                    form_name = webinar.get_value_by_key(content)
                    if form_name:
                        form = Form.objects.filter(name=form_name).first()
                        if form:
                            form_submission = FormSubmission.objects.filter(form=form, user=participant.user).first()
                            if form_submission:
                                text_value = form_submission.data.get(content, '')

                                font_path = settings.FONTS_DIR / f'{font_name}.ttf'
                                print(f"Loading font from: {font_path}")
                                font = ImageFont.truetype(font_path, int(size.replace('px', '')))
 
                                text_bbox = font.getbbox(content)
                                text_height = text_bbox[3] - text_bbox[1]

                                # Adjust the top position by subtracting the text height
                                original_top = int(position['top'].replace('px', ''))
                                adjusted_top = original_top - text_height

                                draw.text(
                                    (int(position['left'].replace('px', '')), adjusted_top),
                                    text_value,
                                    font=font,
                                    fill=color 
                                )
                if qr_position:
                    qr_size_value = int(qr_size.replace('px', ''))
                    qr_image_resized = qr_image.resize((qr_size_value, qr_size_value))
                    certificate_image.paste(
                        qr_image_resized, 
                        (int(qr_position['left'].replace('px', '')), int(qr_position['top'].replace('px', ''))),
                        qr_image_resized.convert('RGBA')
                    )
            cert_buffer = BytesIO()
            certificate_image.save(cert_buffer, format='PDF')
            cert_buffer.seek(0)

            participant_name = participant.user.username.replace(" ", "_")
            zip_file.writestr(f'{participant_name}_certificate.pdf', cert_buffer.read())

        zip_buffer.seek(0)

        response_zip = HttpResponse(zip_buffer, content_type='application/zip')
        response_zip['Content-Disposition'] = f'attachment; filename="{webinar.webinar_name}_certificates.zip"'

        return response_zip
    
    return render(request, 'generate_certificates_preview.html', {
        'webinar': webinar,
        'data_keys': data_keys,
        'width': image_width,
        'height': image_height,
    })


@csrf_exempt
def verify_page(request, webinar_id):
    webinar = get_object_or_404(Webinar, id=webinar_id)
    verified_certified_users = WebinarJoin.objects.filter(
        webinar=webinar, verified=True, certified=True
    )
    
    context = {
        'webinar': webinar,
        'verified_certified_users': verified_certified_users,
    }
    return render(request, 'verify_page.html', context)

# @login_required(login_url="/login/")
# @role_required(allowed_roles=["H"])
# @csrf_exempt
# def generate_certificates_preview(request, webinar_id):
#     webinar = get_object_or_404(Webinar, id=webinar_id)
#     file_url = request.GET.get('file')
#     qr_url = request.GET.get('qr_url')
#     generate_qr = request.GET.get('generate_qr') == 'true'

#     if request.method == 'POST':
#         # Handle form submission logic
#         # ...
#         return JsonResponse({'status': 'success'})

#     return render(request, 'generate_certificates_preview.html', {
#         'webinar': webinar,
#         'image_url': file_url,
#         'qr_url': qr_url,
#         'generate_qr': generate_qr
#     })

