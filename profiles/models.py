from django.db import models
from users.models import MainUser
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
