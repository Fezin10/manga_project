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
    mangas = Manga.objects.filter(status__in=['F', 'R']).annotate(num_likes=Count('likes')).order_by('-num_likes')
    return render(request, 'mangaweb/index.html', {'mangas': mangas})