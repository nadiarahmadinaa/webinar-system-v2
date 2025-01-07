from django.urls import path

from webinar.views import webinar_home, edit_webinar, make_webinar, delete_webinar, view_webinar, api_webinar

app_name = "webinar"

urlpatterns = [
    path("", webinar_home, name="webinar_home"),
    path("<uuid:webinar_id>/", view_webinar, name="view_webinar"),
    path("edit_webinar/<uuid:webinar_id>/", edit_webinar, name="edit_webinar"),
    path("make_webinar/", make_webinar, name="make_webinar"),
    path("delete_webinar/<uuid:webinar_id>/", delete_webinar, name="delete_webinar"),
    path('api/', api_webinar, name='api_webinar'),
]