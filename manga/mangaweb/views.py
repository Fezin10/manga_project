from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Count, OuterRef, Subquery
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
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
        return HttpResponseRedirect(reverse('mangapage', args=[manga.name, manga.id]))


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

        manga = Manga(name=request.POST["manga_name"].strip(), author=request.user, status=request.POST["status"])
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
        check = helper.manga_check(manga, thumb)
        if check == 'success':
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
            return error(check)


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
    # Get the most popular mangas that are finished or releasing
    mangas = Manga.objects.filter(status__in=['F', 'R']).annotate(num_likes=Count('likes'), num_views=Count('chapters__read')).order_by('-num_likes', '-num_views', 'name')
    print(mangas)
    return render(request, 'mangaweb/index.html', {'mangas': mangas, 'genres': Genre.objects.all().order_by('genre')})


def mangas(request):
    def error(message):
        return render(request, 'mangaweb/index.html', {'mangas': mangas, 'genres': dropdown_genres, 'message': message})

    # Base variables
    mangas = Manga.objects.all()
    dropdown_genres = Genre.objects.all().order_by('genre')

    # change the mangas query depending on the filters requested by the user
    if request.user.is_authenticated:
        if request.GET.get('liked'):
            mangas = mangas.filter(likes=request.user)
        if request.GET.get('authors'):
            mangas = mangas.filter(author__in=request.user.following.all())

    status = request.GET.getlist('status')
    if status:
        mangas = mangas.filter(status__in=status)

    genres = request.GET.getlist('genres')
    if genres:
        mangas = mangas.filter(genres__in=dropdown_genres.filter(genre__in=genres))

    sort = request.GET.get('sort')
    if sort:
        if sort == 'az':
            mangas = mangas.order_by('name')
        elif sort == 'za':
            mangas = mangas.order_by('-name')
        elif sort == 'imp':
            mangas = mangas.annotate(num_likes=Count('likes'), num_views=Count('chapters__read')).order_by('num_likes', 'num_views', 'name')
        elif sort == 'pop':
            mangas = mangas.annotate(num_likes=Count('likes'), num_views=Count('chapters__read')).order_by('-num_likes', '-num_views', 'name')
    else:
        mangas = mangas.annotate(num_likes=Count('likes'), num_views=Count('chapters__read')).order_by('-num_likes', '-num_views', 'name')

    return render(request, 'mangaweb/index.html', {'mangas': mangas, 'genres': dropdown_genres})


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
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "mangaweb/login.html", {"message": "Invalid username and/or password."})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def mangapage(request, manganame, mangaid):
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
        return render(request, "mangaweb/mangapage.html", {"manga": manga, "views": views, "chapters": chapters})


def mangaread(request, manga_id, chapter):
    #TODO
    return HttpResponse(f'manga id: {manga_id}, chapter: {chapter}')


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