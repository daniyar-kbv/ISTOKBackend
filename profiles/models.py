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
                               on_delete=models.CASCADE,
                               null=True,
                               blank=False,
                               default=None,
                               related_name='client_applications',
                               verbose_name='Клиент')
    merchant = models.ForeignKey(MainUser,
                                 on_delete=models.CASCADE,
                                 null=True,
                                 blank=False,
                                 default=None,
                                 related_name='merchant_applications',
                                 verbose_name='Специалист')
    category = models.ForeignKey(ProjectCategory,
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 blank=False,
                                 related_name='applications',
                                 verbose_name='Категория')
    creation_date = models.DateTimeField(auto_now=True, verbose_name='Дата создания')
    project = models.ForeignKey(Project,
                                on_delete=models.SET_NULL,
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
    creation_date = models.DateTimeField(auto_now_add=True, null=False, blank=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ('-creation_date', )

    def __str__(self):
        return f'{self.id}: {self.user}, {self.text[:15]}'

