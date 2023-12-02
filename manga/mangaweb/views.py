from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Max, Count
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse

from .models import *
from . import helper


@login_required
def addchapter(request):
    if not request.user.author:
        raise Http404("Only authors can add chapters to their mangas")
    def error(message):
        return render(request, 'mangaweb/addchapter.html', {'mangas': Manga.objects.filter(author=request.user), 'message': message})
    
    if request.method == 'GET':
        return render(request, 'mangaweb/addchapter.html', {'mangas': Manga.objects.filter(author=request.user)})
    else:
        chapter_number = request.POST['chapter']
        # check if the manga exists
        try:
            manga = Manga.objects.get(id=request.POST['manga'])
        except:
            return error('Invalid manga selected!')
        
        # check if the chapter is free to use
        try:
            Chapter.objects.get(manga=manga, chapter_number=chapter_number)
            return error('Chapter already exists!')
        except:
            pass

        chapter = Chapter(chapter_number=chapter_number, manga=manga)
        if request.FILES:
            chapter.save()
            for i, image in enumerate(request.FILES.getlist('pages'), start=1):
                if not image.content_type.startswith('image'):
                    chapter.delete()
                    return error('Invalid file type sended as image, chapter not saved!')
                                
                Page(chapter=chapter, page_number=i, page_content=image).save()
        else:
            return error('No images provided')
        return HttpResponse('OK')


@login_required
def addmanga(request):
    if not request.user.author:
        raise Http404("Only authors can add mangas")
    if request.method == 'GET':
        return render(request, 'mangaweb/addmanga.html', {'genres': Genre.objects.all().order_by('-genre')})
    elif request.method == 'POST':
        def error(message):
            return render(request, 'mangaweb/addmanga.html', {'genres': Genre.objects.all().order_by('-genre'), 'message': message})

        manga = Manga()
        manga.name = request.POST["manga_name"].strip()
        manga.author = request.user
        manga.status = request.POST["status"]
        try:
            thumb = request.FILES["thumb"]
        except:
            thumb = None
        genres = request.POST.getlist("genres")
        custom = request.POST["custom_genre"].split(',')
        
        # check if the custom genre exists and them add all genres to the manga, create them if dont exist
        if custom and len(custom) > 1 or custom[0] != '': genres.extend(custom)
        if len(genres) < 1:
            return error('You must provide at least 1 genre')
        check = helper.manga_check(manga, thumb)
        if check == 'success':
            manga.save()
            manga.thumb = thumb
            manga.save()
            for genre in genres:
                if len(genre) > 20:
                    return error('Custom genre size is larger than 20 characters')
                entry, created = Genre.objects.get_or_create(genre=genre.strip().capitalize())
                manga.genres.add(entry)
            return HttpResponseRedirect(reverse('addchapter'))
        else:
            return error(check)


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
    # helper error function to return errors quickly
    def error(message):
        return render(request, "mangaweb/register.html", {"message": message})
    
    if request.method != "POST":
        return render(request, "mangaweb/register.html")
    else:
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        icon = request.FILES.get("icon")
        
        # check if the user is trying to register with a banned email
        try:
            Banned.objects.get(email=email)
            return error("You're banned")
        except Banned.DoesNotExist:
            pass

        # validation of the icon, password and email
        if icon:
            if not icon.content_type.startswith('image'):
                return error("Invalid file type.")
            if icon.size > 2097152:
                return error("Image limit is 2 MB.")
        if len(password) < 4:
            return error("Password must be at least 4 characters long.")
        if password != confirmation:
            return error("Passwords must match.")
        
        try:
            user = User.objects.create_user(username, email, password)
            user.icon = icon
            user.save()
        except IntegrityError:
            return error("Username already taken.")
        
        login(request, user)
        return HttpResponseRedirect(reverse("index"))