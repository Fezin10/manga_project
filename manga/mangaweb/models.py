import os
import shutil

from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.db import models

from . import uploaders


# User related fields
class User(AbstractUser):
    moderator = models.BooleanField(default=False)
    author = models.BooleanField(default=False)
    retained = models.BooleanField(default=False)
    retain_reason = models.TextField(blank=True, null=True)
    faults = models.PositiveSmallIntegerField(default=0)
    premium = models.BooleanField(default=False)
    icon = models.ImageField(upload_to=uploaders.user, null=True, blank=True)
    following = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='followed_by')


class Banned(models.Model):
    email = models.EmailField()


# Content related fields
class Chapter(models.Model):
    manga = models.ForeignKey('Manga', on_delete=models.CASCADE, related_name='chapters')
    read = models.ManyToManyField(User, blank=True)
    chapter_number = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'Chapter {self.chapter_number} Manga {self.manga}'


class Genre(models.Model):
    id  = models.AutoField(primary_key=True)
    genre = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.genre


class Manga(models.Model):
    STATUS_CHOICES = [
        ('F', 'Finished'),
        ('R', 'Releasing'),
        ('N', 'Not released'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='works')
    genres = models.ManyToManyField(Genre)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    thumb = models.ImageField(upload_to=uploaders.manga_thumb, null=True, blank=True)
    sinopse = models.TextField(max_length=300, null=True, blank=True)
    likes = models.ManyToManyField(User, related_name='liked_manga', blank=True)
    releasedate = models.DateField(null=True, blank=True)
    enddate = models.DateField(null=True, blank=True)
    retained = models.BooleanField(default=False)
    retained_reason = models.TextField(blank=True, null=True)


    def __str__(self):
        return f'{self.name} id:{self.id}'


class Page(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='pages')
    page_number = models.PositiveSmallIntegerField()
    page_content = models.ImageField(upload_to=uploaders.manga_page)

    def __str__(self):
        return f'Page {self.page_number} chapter {self.chapter.chapter_number} manga {self.chapter.manga}'


# Deletion handlers
@receiver(post_delete, sender=Chapter)
def delete_chapter(sender, instance, **kwargs):
    manga = instance.manga
    chapter_directory = os.path.join('media/manga/', manga.name, str(manga.id), str(instance.chapter_number))
    try:
        shutil.rmtree(chapter_directory)
        print(f"\033[1;34m{chapter_directory}\033[m directory deleted.")
    except OSError as error:
        print(f"\033[1;31m{error}\033[m directory doesn't exist.")


@receiver(post_delete, sender=Manga)
def delete_manga(sender, instance, **kwargs):
    manga_directory = os.path.join('media/manga', instance.name)
    try:
        manga_count = len(os.listdir(manga_directory))
        if manga_count == 1:
            shutil.rmtree(manga_directory)
        else:
            manga_directory = os.path.join(manga_directory, str(instance.id))
            shutil.rmtree(manga_directory)
        
        print(f"\033[1;34m{manga_directory}\033[m directory deleted.")
    except OSError as error:
        print(f"\033[1;31m{error}\033[m directory doesn't exist.")