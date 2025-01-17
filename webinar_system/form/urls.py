from django.urls import path

from form.views import view_form, edit_form, make_form, delete_form, form_submission, api_form, update_verified

app_name = "form"

urlpatterns = [
    path("<uuid:form_id>/", view_form, name="view_form"),
    path("edit_form/<uuid:form_id>/", edit_form, name="edit_form"),
    path("make_form/<uuid:webinar_id>/", make_form, name="make_form"),
    path("delete_form/<uuid:form_id>/", delete_form, name="delete_form"),
    path("submissions/<uuid:form_id>/", form_submission, name="form_submission"),
    path('api/', api_form, name='api_form'),
    path('update_verified/<uuid:form_id>/', update_verified, name='update_verified'),
]
