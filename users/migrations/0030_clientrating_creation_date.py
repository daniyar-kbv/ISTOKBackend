# Generated by Django 3.0.6 on 2020-06-19 05:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0029_clientrating'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientrating',
            name='creation_date',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата создания'),
        ),
    ]
