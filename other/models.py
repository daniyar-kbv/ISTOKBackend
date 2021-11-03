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
