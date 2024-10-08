# Generated by Django 3.0.6 on 2020-06-09 12:12

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpost',
            name='user_likes',
            field=models.ManyToManyField(blank=True, related_name='blog_post_likes', to=settings.AUTH_USER_MODEL, verbose_name='Лайки пользователей'),
        ),
    ]
