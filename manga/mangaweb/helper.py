from django.contrib.auth import login
from django.contrib.auth.hashers import check_password
from django.http import Http404
from django.db.models import Count
from django_ratelimit.decorators import ratelimit
from .models import *


@ratelimit(key='user', rate='1/2d', block=True)
def change_password(user, old, new, check):
    if check_password(old):
        if new == check and len(new) > 4:
            return True
        else:
            return False
    else:
        return False


# apply the filters to a mangas query and return the filtered query
def filters(request):
    filters = dict()    
    
    query = request.GET.get('query')
    if query:
        mangas = Manga.objects.filter(name__icontains=request.GET.get('query')).exclude(retained=True).exclude(author__retained=True)
        filters['query'] = request.GET.get('query')
    else:
        mangas = Manga.objects.exclude(retained=True).exclude(author__retained=True)

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

    dropdown_genres = Genre.objects.all().order_by('genre')
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
    
    return mangas, filters, dropdown_genres


# Create an url to be used in get requests from the filters
def filters_to_url(filters):
    url = ''
    for k in filters.keys():
        if type(filters[k]) == list:
            for v in filters[k]:
                url += f'{k}={v}&'
        else:
            url += f'{k}={filters[k]}&'
    return url.rstrip('&')


# check if a given manga have correct data
def image_size_validation(image, size):
    if image != None:
        if not image.content_type.startswith('image'):
            return False
        if image.size > size*1024*1024:
            return False
    return True


@ratelimit(key='user', rate='1/m', block=True)
def login_user(request, user):
    login(request, user)

def moderator_required(view):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.moderator:
            return view(request, *args, **kwargs)
        else:
            raise Http404()
    return wrapper
