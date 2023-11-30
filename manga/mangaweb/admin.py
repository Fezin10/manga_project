from django.contrib import admin
from .models import *

class mangaAdmin(admin.ModelAdmin):
    list_display = ['name', 'id']

admin.site.register(User)
admin.site.register(Genre)
admin.site.register(Manga, mangaAdmin)