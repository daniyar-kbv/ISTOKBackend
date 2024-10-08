# Generated by Django 3.0.6 on 2020-05-29 12:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0018_auto_20200529_1249'),
        ('main', '0005_auto_20200529_0747'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='users_favorites',
        ),
        migrations.AlterField(
            model_name='project',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='main', to='users.ProjectTag', verbose_name='Тэги'),
        ),
        migrations.CreateModel(
            name='ProjectUserFavorite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_date', models.DateTimeField(auto_now=True, verbose_name='Дата создания')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to='main.Project', verbose_name='Проект')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_favorites', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Проект избранное',
                'verbose_name_plural': 'Проекты избранное',
            },
        ),
    ]
