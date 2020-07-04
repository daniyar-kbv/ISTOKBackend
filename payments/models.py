from django.db import models
from django.core.exceptions import ValidationError
from users.models import MainUser
from main.models import Project
import constants


class PaidFeatureType(models.Model):
    type = models.PositiveSmallIntegerField(choices=constants.PAID_FEATURE_TYPES,
                                            default=constants.PAID_FEATURE_PRO,
                                            verbose_name='Тип')
    text = models.TextField(null=True, blank=True, verbose_name='Текст')
    price = models.FloatField(null=False, blank=False, default=0, verbose_name='Цена')
    time_amount = models.PositiveIntegerField(null=False, blank=False, default=1, verbose_name='Количество (время)')
    time_unit = models.PositiveSmallIntegerField(choices=constants.TIME_TYPES,
                                                 default=constants.TIME_DAY,
                                                 verbose_name='Еденицы измерения времени')
    beneficial = models.BooleanField(null=False, blank=True, default=False, verbose_name='Выгодный')
    position = models.IntegerField(default=0, null=False, blank=False, verbose_name='Позиция')

    class Meta:
        verbose_name = 'Тип платной услуги'
        verbose_name_plural = 'Типы платных услуг'
        ordering = ('position', )

    def __str__(self):
        return f'{self.id}: {constants.PAID_FEATURE_TYPES[self.type-1][1]}, {self.price}'


def is_top_detailed(value):
    type = PaidFeatureType.objects.get(id=value)
    if type.type != constants.PAID_FEATURE_TOP_DETAILED:
        raise ValidationError(f'{constants.RESPONSE_FEATURE_TYPES}: Топ и выделеный')
    return value


def is_detailed(value):
    type = PaidFeatureType.objects.get(id=value)
    if type.type != constants.PAID_FEATURE_DETAILED:
        raise ValidationError(f'{constants.RESPONSE_FEATURE_TYPES}: Выделеный')
    return value


def is_top(value):
    type = PaidFeatureType.objects.get(id=value)
    if type.type != constants.PAID_FEATURE_TOP:
        raise ValidationError(f'{constants.RESPONSE_FEATURE_TYPES}: Топ')
    return value


class ProjectLinkedPaidFeatures(models.Model):
    main_feature = models.ForeignKey(PaidFeatureType,
                                     on_delete=models.CASCADE,
                                     null=False,
                                     blank=False,
                                     related_name='linked_paid_features',
                                     verbose_name='Основная услуга проекта',
                                     validators=[is_top_detailed])
    first_feature = models.ForeignKey(PaidFeatureType,
                                      on_delete=models.CASCADE,
                                      null=False,
                                      blank=False,
                                      related_name='main_paid_feature_1',
                                      verbose_name='Связаная топ услуга',
                                      validators=[is_top])
    second_feature = models.ForeignKey(PaidFeatureType,
                                       on_delete=models.CASCADE,
                                       null=False,
                                       blank=False,
                                       related_name='main_paid_feature_2',
                                       verbose_name='Связаная выделеная услуга',
                                       validators=[is_detailed])

    class Meta:
        verbose_name = 'Связаные платные услуги'
        verbose_name_plural = 'Связаные платные услуги'

    def __str__(self):
        return f'{self.id}: Основная({self.main_feature_id}), Топ({self.first_feature_id}), Выделеная({self.second_feature_id})'


class PaidFeature(models.Model):
    type = models.ForeignKey(PaidFeatureType,
                             on_delete=models.CASCADE,
                             null=True,
                             blank=False,
                             verbose_name='Тип')
    refresh_count = models.PositiveSmallIntegerField(null=False, blank=True, default=0, verbose_name='Количество продлений')
    is_active = models.BooleanField(null=False, blank=True, default=False, verbose_name='Активный')
    created_at = models.DateTimeField(auto_now=True, blank=True, null=False, verbose_name='Дата создание')
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата истечения')

    class Meta:
        abstract = True


class UsersPaidFeature(PaidFeature):
    user = models.ForeignKey(MainUser,
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False,
                             related_name='features',
                             verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Платная услуга пользователя'
        verbose_name_plural = 'Платные услуги пользователей'

    def __str__(self):
        return f'{self.id}: {self.user.get_full_name()}({self.user.id}), {self.type.type}'


class ProjectPaidFeature(PaidFeature):
    project = models.ForeignKey(Project,
                                on_delete=models.CASCADE,
                                null=False,
                                blank=False,
                                related_name='features',
                                verbose_name='Проект')

    class Meta:
        verbose_name = 'Платная услуга проекта'
        verbose_name_plural = 'Платные услуги проектов'

    def __str__(self):
        return f'{self.id}: {self.project.name}({self.project.id}), {self.type.type}'


class Transaction(models.Model):
    creation_date = models.DateTimeField(auto_now=True, verbose_name='Дата создание')
    feature_type = models.ForeignKey(PaidFeatureType,
                             on_delete=models.CASCADE,
                             null=True,
                             blank=False,
                             verbose_name='Тип')
    sum = models.FloatField(null=False, blank=False, verbose_name='Сумма')
    succeeded = models.BooleanField(null=False, blank=True, default=False, verbose_name='Завершенная')
    type = models.PositiveSmallIntegerField(choices=constants.PAID_FEATURE_FOR_TYPES,
                                            default=constants.PAID_FEATURE_FOR_USER,
                                            verbose_name='Тип')
    user = models.ForeignKey(MainUser,
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False,
                             related_name='transactions',
                             verbose_name='Пользователь')
    project = models.ForeignKey(Project,
                                on_delete=models.CASCADE,
                                null=True,
                                blank=False,
                                related_name='transactions',
                                verbose_name='Проект')
    user_feature = models.ForeignKey(UsersPaidFeature,
                                     on_delete=models.DO_NOTHING,
                                     null=True,
                                     blank=False,
                                     default=None,
                                     related_name='transactions_as_users',
                                     verbose_name='Платная услуга пользователя')
    project_feature_main = models.ForeignKey(ProjectPaidFeature,
                                             on_delete=models.DO_NOTHING,
                                             null=True,
                                             blank=False,
                                             default=None,
                                             related_name='transactions_as_first',
                                             verbose_name='Основная платная услуга проекта')
    project_feature_secondary = models.ForeignKey(ProjectPaidFeature,
                                                  on_delete=models.DO_NOTHING,
                                                  null=True,
                                                  blank=False,
                                                  default=None,
                                                  related_name='transactions_as_second',
                                                  verbose_name='Вторая платная услуга проекта')

    class Meta:
        verbose_name = 'Оплата'
        verbose_name_plural = 'Оплаты'

    def __str__(self):
        return f'{self.id}: {self.id}'

