# Generated by Django 4.2.6 on 2023-11-27 22:16

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mangaweb', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='manga',
            name='likes',
        ),
        migrations.AddField(
            model_name='manga',
            name='likes',
            field=models.ManyToManyField(related_name='liked', to=settings.AUTH_USER_MODEL),
        ),
    ]