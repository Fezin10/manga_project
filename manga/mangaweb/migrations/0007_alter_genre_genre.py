# Generated by Django 4.2.6 on 2023-11-29 23:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mangaweb', '0006_alter_genre_genre'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genre',
            name='genre',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]