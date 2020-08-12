from django.db import models


class FAQ(models.Model):
    question = models.CharField(max_length=500, null=False, blank=False, verbose_name='Вопрос')
    answer = models.CharField(max_length=5000, null=False, blank=False, verbose_name='Ответ')
    position = models.IntegerField(null=False, blank=False, verbose_name='Позиция')

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return f'{self.id}: {self.question[0:20]}...'


class MailingRecipient(models.Model):
    email = models.EmailField(unique=True, verbose_name='Email')
    subscription_date = models.DateTimeField(auto_now_add=True, null=False, blank=True, verbose_name='Дата подписки')

    is_subscribed = models.BooleanField(default=True, verbose_name='Подписан')

    class Meta:
        verbose_name = 'Получатель рассылки'
        verbose_name_plural = 'Получатели рассылки'

    def __str__(self):
        return f'{self.id}: {self.email}'


class Mailing(models.Model):
    title = models.CharField(max_length=100, null=False, blank=False, verbose_name="Заголовок")
    text = models.CharField(max_length=10000, null=False, blank=False, verbose_name="Основной текст")
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'

    def __str__(self):
        return f'{self.id}: {self.title}'
