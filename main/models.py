from django.db import models
from users.models import MainUser, ProjectCategory, ProjectTag, ProjectStyle, ProjectPurpose, ProjectType


class Project(models.Model):
    user = models.ForeignKey(MainUser,
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False,
                             related_name='main',
                             verbose_name='Пользователь')
    users_favorites = models.ManyToManyField(MainUser.Project,
                                             null=True,
                                             blank=True,
                                             related_name='favorites',
                                             verbose_name='Пользователи избранное')
    name = models.CharField(max_length=100, null=False, blank=False, verbose_name='Название')
    category = models.ForeignKey(ProjectCategory,
                                 on_delete=models.DO_NOTHING,
                                 null=True,
                                 blank=False,
                                 related_name='main',
                                 verbose_name='Категория')
    purpose = models.ForeignKey(ProjectPurpose,
                                on_delete=models.DO_NOTHING,
                                null=True,
                                blank=False,
                                related_name='main',
                                verbose_name='Назначение')
    type = models.ForeignKey(ProjectType,
                             on_delete=models.DO_NOTHING,
                             null=True,
                             blank=False,
                             related_name='main',
                             verbose_name='Тип')
    style = models.ForeignKey(ProjectStyle,
                              on_delete=models.DO_NOTHING,
                              null=True,
                              blank=False,
                              related_name='main',
                              verbose_name='Стиль')
    tags = models.ManyToManyField(ProjectTag, null=True, blank=False, related_name='main', verbose_name='Тэги')
    area = models.FloatField(null=False, blank=False, verbose_name='Площадь')
    price_from = models.FloatField(null=False, blank=False, verbose_name='Цена от')
    price_to = models.FloatField(null=False, blank=False, verbose_name='Цена до')
    description = models.CharField(max_length=1000, null=False, blank=False, verbose_name='Описание')
