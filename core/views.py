from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password != password2:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("register")

        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(user=user)
        login(request, user)
        messages.success(request, f"Welcome {username}!")
        return redirect("home")

    return render(request, "core/register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {username}!")
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")

    return render(request, "core/login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect("home")


def home_view(request):
    return render(request, "core/home.html")


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, "core/profile.html", {"profile": profile})
