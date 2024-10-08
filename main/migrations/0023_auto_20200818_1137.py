# Generated by Django 3.0.6 on 2020-08-18 05:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_mailing_subscriber'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commentcomplain',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата'),
        ),
        migrations.AlterField(
            model_name='commentreplycomplain',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата'),
        ),
        migrations.AlterField(
            model_name='project',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='projectcomment',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Дата'),
        ),
        migrations.AlterField(
            model_name='projectcommentreply',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='projectcomplain',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата'),
        ),
        migrations.AlterField(
            model_name='projectuserfavorite',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='projectview',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='reviewcomplain',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата'),
        ),
        migrations.AlterField(
            model_name='reviewreplycomplain',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата'),
        ),
    ]
