# Generated by Django 3.0.6 on 2020-05-21 10:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20200521_0715'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='useractivation',
            options={'verbose_name': 'Активация', 'verbose_name_plural': 'Активации'},
        ),
        migrations.AddField(
            model_name='useractivation',
            name='email',
            field=models.EmailField(default=None, max_length=254, verbose_name='Email'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='useractivation',
            name='user',
            field=models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='activation', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]
