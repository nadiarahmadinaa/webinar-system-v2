import datetime

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from authentication.forms import CustomRegisterForm


# Create your views here.
def show_main(request):
    context = {
        "user": request.user,
        "last_login": request.COOKIES.get("last_login"),
    }

    return render(request, "main.html", context)


def register(request):
    form = CustomRegisterForm()

    if request.method == "POST":
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully")
            return redirect("main:login")

    context = {"form": form}
    return render(request, "register.html", context)


def login_user(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            response = HttpResponseRedirect(reverse("main:show_main"))
            response.set_cookie(
                "last_login",
                str(datetime.datetime.now().strftime("%A, %B %d, %Y %I:%M %p")),
            )
            return response
        else:
            messages.error(request, "Invalid username or password. Please try again.")

    else:
        form = AuthenticationForm(request)
    context = {"form": form}
    return render(request, "login.html", context)


def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse("main:login"))
    response.delete_cookie("last_login")
    return redirect("main:login")


@login_required(login_url="/login/")
def get_user_data(request):

    user_data = {
        "id": request.user.id,
        "role": request.user.role,
        "username": request.user.username,
        "phone_number": request.user.phone_number,
        "email": request.user.email,
    }

    return JsonResponse(user_data)
