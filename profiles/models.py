from django.db import models
from users.models import MainUser, ProjectCategory
from main.models import Project
from utils import upload, validators
import constants


class FormQuestionGroup(models.Model):
    name = models.CharField(max_length=500, null=False, blank=False, verbose_name='Название')
    position = models.PositiveIntegerField(default=1, null=False, blank=False, verbose_name='Позиция')

    class Meta:
        verbose_name = 'Группа вопрсов'
        verbose_name_plural = 'Группы вопросов'

    def __str__(self):
        return f'{self.id}: {self.name[:15]}'


class FormQuestion(models.Model):
    question = models.CharField(max_length=500, null=False, blank=False, verbose_name='Вопрос')
    position = models.PositiveIntegerField(default=1, null=False, blank=False, verbose_name='Позиция')
    type = models.PositiveSmallIntegerField(choices=constants.QUESTION_TYPES,
                                            default=constants.QUESTION_RADIO,
                                            blank=False,
                                            verbose_name='Тип вопроса')
    group = models.ForeignKey(FormQuestionGroup,
                              on_delete=models.CASCADE,
                              null=False,
                              blank=False,
                              related_name='questions',
                              verbose_name='Группа')

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return f'{self.id}: {self.question[:15]}'


class FormAnswer(models.Model):
    answer = models.CharField(max_length=500, null=False, blank=False, verbose_name='Ответ')
    position = models.PositiveIntegerField(default=1, null=False, blank=False, verbose_name='Позиция')
    question = models.ForeignKey(FormQuestion,
                                 on_delete=models.CASCADE,
                                 null=False,
                                 blank=False,
                                 related_name='answers',
                                 verbose_name='Вопрос')

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'

    def __str__(self):
        return f'{self.id}: {self.answer[:15]}'


class FormUserAnswer(models.Model):
    user = models.ForeignKey(MainUser,
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False,
                             related_name='answers',
                             verbose_name='Пользователь')
    answer = models.ForeignKey(FormAnswer,
                               on_delete=models.CASCADE,
                               null=False,
                               blank=False,
                               related_name='user_answers',
                               verbose_name='Ответ')

    class Meta:
        verbose_name = 'Ответ клииента'
        verbose_name_plural = 'Ответы клиента'

    def __str__(self):
        return f'{self.id}: {self.user.id}({self.user}) -> {self.answer.id}({self.answer}))'


class Application(models.Model):
    client = models.ForeignKey(MainUser,
                               on_delete=models.DO_NOTHING,
                               null=True,
                               blank=False,
                               related_name='client_applications',
                               verbose_name='Клиент')
    merchant = models.ForeignKey(MainUser,
                                 on_delete=models.DO_NOTHING,
                                 null=True,
                                 blank=False,
                                 related_name='merchant_applications',
                                 verbose_name='Специалист')
    category = models.ForeignKey(ProjectCategory,
                                 on_delete=models.DO_NOTHING,
                                 null=True,
                                 blank=False,
                                 related_name='applications',
                                 verbose_name='Категория')
    creation_date = models.DateTimeField(auto_now=True, verbose_name='Дата создания')
    project = models.ForeignKey(Project,
                                on_delete=models.DO_NOTHING,
                                null=True,
                                blank=False,
                                related_name='applications',
                                verbose_name='Проект')
    status = models.PositiveSmallIntegerField(choices=constants.APPLICATION_STATUSES,
                                              default=constants.APPLICATION_CREATED,
                                              verbose_name='Статус')
    comment = models.CharField(max_length=1000,
                               null=True,
                               blank=True,
                               verbose_name='Комментарий')
    rating = models.FloatField(null=True,
                               blank=True,
                               verbose_name='Рейтинг')
    decline_reason = models.CharField(max_length=1000, null=True, blank=True, verbose_name='Причина отказа')

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-creation_date']

    def __str__(self):
        return f'{self.id}: {self.client}, {self.merchant}'


class ApplicationDocument(models.Model):
    application = models.ForeignKey(Application,
                                    on_delete=models.CASCADE,
                                    null=False,
                                    blank=False,
                                    related_name='documents',
                                    verbose_name='Заявка')
    document = models.FileField(upload_to=upload.application_document_path,
                                validators=[validators.basic_validate_images, validators.validate_file_size],
                                verbose_name='Документ')

    class Meta:
        verbose_name = 'Документ заявки'
        verbose_name_plural = 'Документы заявок'

    def __str__(self):
        return f'{self.id}: Заявка({self.application_id})'


class Notification(models.Model):
    user = models.ForeignKey(MainUser,
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False,
                             related_name='notifications',
                             verbose_name='Пользователь')
    text = models.TextField(null=False, blank=False, verbose_name='Содержание')
    read = models.BooleanField(default=False, blank=False, verbose_name='Прочитано')

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'

    def __str__(self):
        return f'{self.id}: {self.user}, {self.text[:15]}'


class Transaction(models.Model):
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создание')
    number = models.TextField(null=False, blank=False, verbose_name='Номер')

    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'

    def __str__(self):
        return f'{self.id}: {self.number}'


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


class PaidFeature(models.Model):
    type = models.ForeignKey(PaidFeatureType,
                             on_delete=models.CASCADE,
                             null=True,
                             blank=False,
                             verbose_name='Тип')
    transaction = models.ForeignKey(Transaction,
                                    on_delete=models.CASCADE,
                                    null=False,
                                    blank=False,
                                    verbose_name='Транзакция')
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
        return f'{self.id}: {self.user}, {self.type.type}'


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
        return f'{self.id}: {self.project}, {self.type.type}'


