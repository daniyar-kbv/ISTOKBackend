# Generated by Django 3.0.6 on 2020-06-22 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0010_auto_20200622_1447'),
    ]

    operations = [
        migrations.RenameField(
            model_name='projectpaidfeature',
            old_name='expired_at',
            new_name='expires_at',
        ),
        migrations.RenameField(
            model_name='userspaidfeature',
            old_name='expired_at',
            new_name='expires_at',
        ),
        migrations.AddField(
            model_name='projectpaidfeature',
            name='is_active',
            field=models.BooleanField(blank=True, default=False, verbose_name='Активный'),
        ),
        migrations.AddField(
            model_name='userspaidfeature',
            name='is_active',
            field=models.BooleanField(blank=True, default=False, verbose_name='Активный'),
        ),
    ]
