# Generated by Django 4.2.6 on 2023-12-13 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mangaweb', '0021_alter_user_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='author',
            field=models.BooleanField(default=False),
        ),
    ]