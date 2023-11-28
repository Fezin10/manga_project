from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Max, Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import *

# Create your views here.
def index(request):
    # Get the most popular mangas that are finished or releasing
    mangas = Manga.objects.filter(status__in=['F', 'R']).annotate(num_likes=Count('likes')).order_by('-num_likes')
    return render(request, 'mangaweb/index.html', {'mangas': mangas})


def login_view(request):
    if request.method != "POST":
        return render(request, "mangaweb/login.html")
    else:
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "mangaweb/login.html", {"message": "Invalid username and/or password."})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def register_view(request):
    def error(message):
        return render(request, "mangaweb/register.html", {"message": message})
    
    if request.method != "POST":
        return render(request, "mangaweb/register.html")
    else:
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        


        if len(password) < 4:
            return error("Password must be at least 4 characters long.")
        if password != confirmation:
            return error("Passwords must match.")
        
        try:
            user = User.objects.create_user(username, email, password)

            try:
                icon = request.FILES.get("icon")

                if not icon.content_type.startswith('image'):
                    return error("Invalid file type.")
                if icon.size > 2097152:
                    return error("Image limit is 2 MB.")
                user.icon = icon
            except:
                pass

            user.save()
        except IntegrityError:
            return error("Username already taken.")
        
        login(request, user)
        return HttpResponseRedirect(reverse("index"))