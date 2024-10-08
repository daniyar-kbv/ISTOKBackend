# Generated by Django 3.0.6 on 2020-07-02 04:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0020_auto_20200702_1001'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaidFeatureType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.PositiveSmallIntegerField(choices=[(1, 'Про аккаунт'), (2, 'Топ проект'), (3, 'Выделеный проект'), (4, 'Топ и Выделеный проект')], default=1, verbose_name='Тип')),
                ('text', models.TextField(blank=True, null=True, verbose_name='Текст')),
                ('price', models.FloatField(default=0, verbose_name='Цена')),
                ('time_amount', models.PositiveIntegerField(default=1, verbose_name='Количество (время)')),
                ('time_unit', models.PositiveSmallIntegerField(choices=[(1, 'Дни'), (2, 'Месяца'), (3, 'Года')], default=1, verbose_name='Еденицы измерения времени')),
                ('beneficial', models.BooleanField(blank=True, default=False, verbose_name='Выгодный')),
                ('position', models.IntegerField(default=0, verbose_name='Позиция')),
            ],
            options={
                'verbose_name': 'Тип платной услуги',
                'verbose_name_plural': 'Типы платных услуг',
                'ordering': ('position',),
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
                ('refresh_count', models.PositiveSmallIntegerField(blank=True, default=0, verbose_name='Количество продлений')),
                ('is_active', models.BooleanField(blank=True, default=False, verbose_name='Активный')),
                ('created_at', models.DateTimeField(auto_now=True, verbose_name='Дата создание')),
                ('expires_at', models.DateTimeField(blank=True, null=True, verbose_name='Дата истечения')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payments.Transaction', verbose_name='Транзакция')),
                ('type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='payments.PaidFeatureType', verbose_name='Тип')),
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
                ('refresh_count', models.PositiveSmallIntegerField(blank=True, default=0, verbose_name='Количество продлений')),
                ('is_active', models.BooleanField(blank=True, default=False, verbose_name='Активный')),
                ('created_at', models.DateTimeField(auto_now=True, verbose_name='Дата создание')),
                ('expires_at', models.DateTimeField(blank=True, null=True, verbose_name='Дата истечения')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='features', to='main.Project', verbose_name='Проект')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payments.Transaction', verbose_name='Транзакция')),
                ('type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='payments.PaidFeatureType', verbose_name='Тип')),
            ],
            options={
                'verbose_name': 'Платная услуга проекта',
                'verbose_name_plural': 'Платные услуги проектов',
            },
        ),
    ]
