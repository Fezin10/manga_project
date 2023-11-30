from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.db import models

from . import helper


# User related fields
class User(AbstractUser):
    moderator = models.BooleanField(default=False)
    author = models.BooleanField(default=False)
    icon = models.ImageField(upload_to=helper.user, null=True)
    following = models.ManyToManyField('self', blank=True)


class Banned(models.Model):
    email = models.EmailField()


# Content related fields
class Chapter(models.Model):
    manga = models.ForeignKey('Manga', on_delete=models.CASCADE, related_name='chapters')
    chapter_number = models.PositiveSmallIntegerField()


class Genre(models.Model):
    id  = models.AutoField(primary_key=True)
    genre = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.genre


class Manga(models.Model):
    STATUS_CHOICES = [
        ('F', 'Finished'),
        ('R', 'Releasing'),
        ('N', 'Not released')
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='works')
    genres = models.ManyToManyField(Genre)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    views = models.PositiveIntegerField(default=0)
    thumb = models.ImageField(upload_to=helper.manga_thumb, null=True)
    likes = models.ManyToManyField(User, related_name='liked_manga')


class Page(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='pages')
    page_number = models.PositiveSmallIntegerField()
    page_content = models.ImageField(upload_to=helper.manga_page)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE)
    message = models.TextField(max_length=256)
    comment_likes = models.ManyToManyField(User, related_name='like_on_comment')

@receiver(post_delete, sender=Manga)
def delete_manga_thumb(sender, instance, **kwargs):
    instance.thumb.delete(False)