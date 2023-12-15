import os

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Count, OuterRef, Subquery
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited
from django.shortcuts import render
from django.urls import reverse

from .models import *
from . import helper


@login_required
def addchapter(request):
    if not request.user.author:
        raise Http404("Only authors can add chapters to their mangas")
    
    # retrieve the manga the user have and also the last chapter the user have uploaded to prevent confusion when trying to add new chapters
    latest_chapter_subquery = Chapter.objects.filter(manga=OuterRef('pk')).order_by('-chapter_number').values('chapter_number')[:1]
    mangas = Manga.objects.annotate(latest_chapter=Subquery(latest_chapter_subquery)).filter(author=request.user).order_by('name')

    def error(message):
        return render(request, 'mangaweb/addchapter.html', {'mangas': mangas, 'message': message})
    
    if request.method == 'GET':
        return render(request, 'mangaweb/addchapter.html', {'mangas': mangas})
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
        return HttpResponseRedirect(reverse('mangapage', args=[manga.id]))


@login_required
def addmanga(request):
    if not request.user.author:
        raise Http404("Only authors can add mangas")
    genre_entries = Genre.objects.all().order_by('genre')
    if request.method == 'GET':
        return render(request, 'mangaweb/addmanga.html', {'genres': genre_entries})
    elif request.method == 'POST':
        def error(message):
            return render(request, 'mangaweb/addmanga.html', {'genres': genre_entries, 'message': message})

        manga = Manga(name=request.POST["manga_name"].strip(), author=request.user, status=request.POST["status"], sinopse=request.POST["sinopse"])
        releasedate = request.POST["releasedate"]
        if releasedate: manga.releasedate = releasedate
        enddate = request.POST["enddate"]
        if enddate: manga.enddate = enddate
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
        check = helper.image_size_validation(thumb, 5)
        if check:
            manga.thumb = thumb
            try:
                manga.full_clean()
            except:
                return error("Invalid information was given")
            else:
                manga.save()
                for genre in genres:
                    if len(genre) > 20:
                        return error('Custom genre size is larger than 20 characters')
                    entry, created = Genre.objects.get_or_create(genre=genre.strip().capitalize())
                    manga.genres.add(entry)
                return HttpResponseRedirect(reverse('addchapter'))
        else:
            return error('Invalid image')


@login_required
def authorregister(request):
    if not request.user.author:
        request.user.author = True
        request.user.save()
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'Invalid status'})


@login_required
def edit(request, manga_id):
    # validation
    if not request.user.author:
        raise Http404()
    try:
        manga = Manga.objects.get(id=manga_id)
    except:
        raise Http404("Manga not found")
    if request.user != manga.author:
        raise Http404("Manga not found")
    
    if request.method == "GET":
        genres = Genre.objects.all().order_by('genre')
        return render(request, "mangaweb/edit.html", {'manga': manga, 'genres': genres})
    else:
        def error(message):
            return render(request, 'mangaweb/edit.html', {'genres': Genre.objects.all().order_by('genre'), 'message': message})


        # Setting the new fields
        manga.status = request.POST['status']
        manga.sinopse = request.POST['sinopse']
        if request.POST["releasedate"]: manga.releasedate = request.POST["releasedate"]
        if request.POST["enddate"]: manga.enddate = request.POST["enddate"]
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
        check = helper.image_size_validation(thumb, 5)

        # delete the older image in case a new one is provided
        if thumb and check and manga.thumb:
            default_storage.delete(manga.thumb.path)


        if check:
            if thumb: manga.thumb = thumb
            try:
                manga.full_clean()
            except:
                return error("Invalid information was given")
            else:
                manga.save()
                for genre in genres:
                    if len(genre) > 20:
                        return error('Custom genre size is larger than 20 characters')
                    entry, created = Genre.objects.get_or_create(genre=genre.strip().capitalize())
                    manga.genres.add(entry)
                return HttpResponseRedirect(reverse('addchapter'))
        else:
            return error('Invalid image')
    

@login_required
def edituser(request):
    if request.method == 'GET':
        return render(request, 'mangaweb/edituser.html')
    else:
        def error(message):
            return render(request, 'mangaweb/edituser.html', {'message': message})

        user = request.user

        if request.POST["old_password"]:
            try:
                if not helper.change_password(user, request.POST["old_password"], request.POST["password"], request.POST["confirmation"]):
                    return error('Cant change the password')
                else:
                    user.set_password(request.POST["password"])
            except Ratelimited:
                return error(f'Rate limit exceeded for changing password')
    
        username = request.POST["username"]
        if username:
            if not User.objects.filter(username=username).exists():
                user.username = username

        icon = request.FILES.get("icon")
        if icon:
            if not helper.image_size_validation(icon, 2):
                return error("Invalid icon")
            else:
                # delete the older icon in case a new one is provided
                if icon and user.icon:
                    default_storage.delete(user.icon.path)
                user.icon = icon

        user.save()
        logout(request)
        return HttpResponseRedirect(reverse('login'))


@login_required
def follow(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except:
        return JsonResponse({'status': 'Invalid user ID'})
    
    if user == request.user:
        return JsonResponse({'status': 'Can not follow yourself'})

    if request.method == "GET":
        return JsonResponse({'status': 'success', 'following': user.followed_by.filter(id=request.user.id).exists()})
    else:
        if user.followed_by.filter(id=request.user.id).exists():
            user.followed_by.remove(request.user)
            following = False
        else:
            user.followed_by.add(request.user)
            following = True
        return JsonResponse({'status': 'success', 'following': following, 'following_count': user.followed_by.count()})



def index(request):
    return HttpResponseRedirect(reverse('mangas'))


@login_required
def like(request, manga_id):
    try:
        manga = Manga.objects.get(id=manga_id)
    except:
        return JsonResponse({'status': 'Manga entry not found'})
    
    if request.method == "GET":
        return JsonResponse({'status': 'success', 'liked': manga.likes.filter(id=request.user.id).exists()})
    else:
        if manga.likes.filter(id=request.user.id).exists():
            manga.likes.remove(request.user)
            liked = False
        else:
            manga.likes.add(request.user)
            liked = True

        return JsonResponse({'status': 'success', 'liked': liked, 'likes': manga.likes.count()})


def login_view(request):
    if request.method != "POST":
        return render(request, "mangaweb/login.html")
    else:
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user:
            try:
                helper.login_user(request, user)
                return HttpResponseRedirect(reverse("index"))
            except Ratelimited:
                return render(request, "mangaweb/login.html", {'message': 'Too many login requests, wait some time before trying to login again'})
        else:
            return render(request, "mangaweb/login.html", {"message": "Invalid username and/or password."})


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def mangapage(request, mangaid):
    if request.method != "GET":
        return HttpResponseRedirect(reverse("index"))
    else:
        try:
            manga = Manga.objects.get(id=mangaid)
        except:
            raise Http404("Manga not found")
        views = 0
        for chapter in manga.chapters.all():
            views += chapter.read.count()
        chapters = manga.chapters.all().order_by('chapter_number')
        chapters = Paginator(chapters, 50 if request.user_agent.is_mobile else 100)
        page = int(request.GET.get('page')) if request.GET.get('page') else 1
        data = {'page': page, 'num_pages': chapters.num_pages, 'before': page-1 > 0, 'after': page+1 <= chapters.num_pages}
        return render(request, "mangaweb/mangapage.html", {"manga": manga, "views": views, "chapters": chapters.page(page), 'data': data})


def mangaread(request, manga_id, chapter_number):
    try:
        manga = Manga.objects.get(id=manga_id)
        chapter = manga.chapters.get(chapter_number=chapter_number)
    except:
        raise Http404("Manga not found or chapter not found")
    
    data = dict()
    data['next'] = manga.chapters.filter(chapter_number=chapter_number+1).exists()
    data['previous'] = manga.chapters.filter(chapter_number=chapter_number-1).exists()
    print(request.user_agent.is_mobile)
    return render(request, 'mangaweb/mangaread.html' if not request.user_agent.is_mobile else 'mangaweb/mangaread_mobile.html', {'chapter': chapter, 'data': data})


def mangas(request):
    def error(message):
        return render(request, 'mangaweb/index.html', {'mangas': mangas, 'genres': dropdown_genres, 'message': message})

    # Base variables
    filters = dict()
    query = request.GET.get('query')
    if query:
        mangas = Manga.objects.filter(name__icontains=query)
        filters['query'] = query
    else:
        mangas = Manga.objects.all()
    dropdown_genres = Genre.objects.all().order_by('genre')


    # change the mangas query depending on the filters requested by the user
    if request.user.is_authenticated:
        if request.GET.get('liked'):
            mangas = mangas.filter(likes=request.user)
            filters['liked'] = True
        if request.GET.get('authors'):
            mangas = mangas.filter(author__in=request.user.following.all())
            filters['authors'] = True

    status = request.GET.getlist('status')
    if status:
        mangas = mangas.filter(status__in=status)
        filters['status'] = status

    genres = request.GET.getlist('genres')
    if genres:
        mangas = mangas.filter(genres__in=dropdown_genres.filter(genre__in=genres))
        filters['genres'] = genres
    sort = request.GET.get('sort')
    if sort:
        if sort == 'az':
            mangas = mangas.order_by('name')
            filters['sort'] = 'az'
        elif sort == 'za':
            mangas = mangas.order_by('-name')
            filters['sort'] = 'za'
        elif sort == 'imp':
            mangas = mangas.annotate(num_likes=Count('likes'), num_views=Count('chapters__read')).order_by('num_likes', 'num_views', 'name')
            filters['sort'] = 'imp'
        elif sort == 'pop':
            mangas = mangas.annotate(num_likes=Count('likes'), num_views=Count('chapters__read')).order_by('-num_likes', '-num_views', 'name')
            filters['sort'] = 'pop'
    else:
        mangas = mangas.annotate(num_likes=Count('likes'), num_views=Count('chapters__read')).order_by('-num_likes', '-num_views', 'name')

    mangas = Paginator(mangas, 10 if request.user_agent.is_mobile else 20)
    page = int(request.GET.get('page')) if request.GET.get('page') else 1
    data = {'page': page, 'num_pages': mangas.num_pages, 'before': page-1 > 0, 'after': page+1 <= mangas.num_pages, 'filters': ''}
    for k in filters.keys():
        if type(filters[k]) == list:
            for v in filters[k]:
                data['filters'] += f'{k}={v}&'
        else:
            data['filters'] += f'{k}={filters[k]}&'
    data['filters'] = data['filters'].rstrip('&')


    return render(request, 'mangaweb/index.html', {'mangas': mangas.page(page), 'genres': dropdown_genres, 'filters': filters, 'data': data})


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
            if not helper.image_size_validation(icon, 2):
                return error("invalid image")
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


def userpage(request, user_id):
    if request.method == 'GET':
        try:
            user = User.objects.get(id=user_id)
        except:
            raise Http404('User not found')
        if user.author:
            mangas = Manga.objects.filter(author=user)
        else:
            mangas = None
        return render(request, 'mangaweb/user.html', {'pageuser': user, 'mangas': mangas})
    

@login_required
def visualization(request, manga_id, chapter):
    try:
        chapter = Manga.objects.get(id=manga_id).chapters.get(chapter_number=chapter)
        chapter.read.add(request.user)
        return JsonResponse({'status': 'success'})
    except:
        return JsonResponse({'status': 'fail'})