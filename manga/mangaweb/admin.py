from django.contrib import admin
from .models import *


class chapterAdmin(admin.ModelAdmin):
    list_display = ['manga', 'chapter_number']


admin.site.register(User)
admin.site.register(Genre)
admin.site.register(Manga)
admin.site.register(Chapter, chapterAdmin)
admin.site.register(Page)