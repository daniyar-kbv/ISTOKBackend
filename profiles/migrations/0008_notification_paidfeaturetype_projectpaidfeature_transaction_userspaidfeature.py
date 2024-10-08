# Generated by Django 3.0.6 on 2020-06-22 08:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_auto_20200603_1655'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('profiles', '0007_application_project'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaidFeatureType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('type', models.PositiveSmallIntegerField(choices=[(1, 'Про аккаунт'), (2, 'Топ проект'), (3, 'Выделеный проект')], default=1, verbose_name='Тип')),
                ('text', models.TextField(blank=True, null=True, verbose_name='Текст')),
                ('price', models.FloatField(default=0, verbose_name='Цена')),
                ('time_amount', models.PositiveIntegerField(default=1, verbose_name='Количество (время)')),
                ('time_unit', models.PositiveSmallIntegerField(choices=[(1, 'Дни'), (2, 'Месяца'), (3, 'Года')], default=1, verbose_name='Еденицы измерения времени')),
            ],
            options={
                'verbose_name': 'Тип платной услуги',
                'verbose_name_plural': 'Типы платных услуг',
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now=True, verbose_name='Дата создание')),
                ('number', models.TextField(verbose_name='Номер')),
            ],
            options={
                'verbose_name': 'Транзакция',
                'verbose_name_plural': 'Транзакции',
            },
        ),
        migrations.CreateModel(
            name='UsersPaidFeature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('beneficial', models.BooleanField(blank=True, default=False, verbose_name='Выгодный')),
                ('created_at', models.DateTimeField(auto_now=True, verbose_name='Дата создание')),
                ('expired_at', models.DateTimeField(blank=True, null=True, verbose_name='Дата истечения')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.Transaction', verbose_name='Транзакция')),
                ('type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='profiles.PaidFeatureType', verbose_name='Тип')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='features', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Платная услуга пользователя',
                'verbose_name_plural': 'Платные услуги пользователей',
            },
        ),
        migrations.CreateModel(
            name='ProjectPaidFeature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('beneficial', models.BooleanField(blank=True, default=False, verbose_name='Выгодный')),
                ('created_at', models.DateTimeField(auto_now=True, verbose_name='Дата создание')),
                ('expired_at', models.DateTimeField(blank=True, null=True, verbose_name='Дата истечения')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='features', to='main.Project', verbose_name='Проект')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.Transaction', verbose_name='Транзакция')),
                ('type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='profiles.PaidFeatureType', verbose_name='Тип')),
            ],
            options={
                'verbose_name': 'Платная услуга проекта',
                'verbose_name_plural': 'Платные услуги проектов',
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Содержание')),
                ('read', models.BooleanField(default=False, verbose_name='Прочитано')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Уведомление',
                'verbose_name_plural': 'Уведомления',
            },
        ),
    ]
