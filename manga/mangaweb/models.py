from django.contrib.auth.models import AbstractUser
from django.db import models

from . import helper


# User related fields
class User(AbstractUser):
    moderator = models.BooleanField(default=False)
    author = models.BooleanField(default=False)


class Banned(models.Model):
    email = models.EmailField()


# Content related fields
class Chapter(models.Model):
    manga = models.ForeignKey('Manga', on_delete=models.CASCADE, related_name='chapters')
    chapter_number = models.PositiveSmallIntegerField()


class Genre(models.Model):
    id  = models.AutoField(primary_key=True)
    genre = models.TextField(max_length=20)


class Manga(models.Model):
    STATUS_CHOICES = [
        ('F', 'Finished'),
        ('R', 'Releasing'),
        ('N', 'Not released')
    ]

    id = models.AutoField(primary_key=True)
    name = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='works')
    genres = models.ManyToManyField(Genre)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    views = models.PositiveIntegerField(default=0)
    thumb = models.ImageField(upload_to=helper.manga_thumb)
    likes = models.PositiveIntegerField(default=0)


class Page(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='pages')
    page_number = models.PositiveSmallIntegerField()
    page_content = models.ImageField(upload_to=helper.manga_page)