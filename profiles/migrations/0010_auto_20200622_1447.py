# Generated by Django 3.0.6 on 2020-06-22 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0009_remove_paidfeaturetype_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectpaidfeature',
            name='beneficial',
        ),
        migrations.RemoveField(
            model_name='userspaidfeature',
            name='beneficial',
        ),
        migrations.AddField(
            model_name='paidfeaturetype',
            name='beneficial',
            field=models.BooleanField(blank=True, default=False, verbose_name='Выгодный'),
        ),
    ]
