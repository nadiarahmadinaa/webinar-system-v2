from django.urls import path

from authentication.views import get_user_data, login_user, logout_user, register, show_main

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("user/", get_user_data, name="get_user_data"),
]
