from django.db import models
from django.db.models import Q
from users.models import MainUser, ProjectCategory, ProjectTag, ProjectStyle, ProjectPurpose, ProjectType, City, \
    MerchantReview, ReviewReply

from utils import upload, validators


class ProjectManager(models.Manager):
    def search(self, arg=None, request=None):
        if arg:
            queryset = self.filter(Q(name__icontains=arg) |
                                   Q(category__name__icontains=arg) |
                                   Q(purpose__name__icontains=arg) |
                                   Q(type__name__icontains=arg) |
                                   Q(style__name__icontains=arg) |
                                   Q(tags__name__icontains=arg) |
                                   Q(description__icontains=arg))
        else:
            queryset = self.all()
        if request:
            if request.data.get('cities'):
                queryset = queryset.filter(user__merchant_profile__city_id__in=request.data.get('cities'))
            if request.data.get('categories'):
                queryset = queryset.filter(category_id__in=request.data.get('categories'))
            if request.data.get('types'):
                queryset = queryset.filter(type_id__in=request.data.get('types'))
            if request.data.get('purposes'):
                queryset = queryset.filter(purpose_id__in=request.data.get('purposes'))
            if request.data.get('styles'):
                queryset = queryset.filter(style_id__in=request.data.get('styles'))
            if request.data.get('area_from'):
                queryset = queryset.filter(area_from__gte=request.data.get('area_from'))
            if request.data.get('area_to'):
                queryset = queryset.filter(area_to__lte=request.data.get('area_to'))
            if request.data.get('price_from'):
                queryset = queryset.filter(price_from__gte=request.data.get('price_from'))
            if request.data.get('price_to'):
                queryset = queryset.filter(price_to__lte=request.data.get('price_to'))
            queryset = queryset.order_by(request.data.get('order_by') if request.data.get('order_by') else '-creation_date')
        return queryset.distinct()


class Project(models.Model):
    user = models.ForeignKey(MainUser,
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False,
                             related_name='projects',
                             verbose_name='Пользователь')
    name = models.CharField(max_length=100, null=False, blank=False, verbose_name='Название')
    category = models.ForeignKey(ProjectCategory,
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 blank=False,
                                 related_name='main',
                                 verbose_name='Категория')
    purpose = models.ForeignKey(ProjectPurpose,
                                on_delete=models.SET_NULL,
                                null=True,
                                blank=False,
                                related_name='main',
                                verbose_name='Назначение')
    type = models.ForeignKey(ProjectType,
                             on_delete=models.SET_NULL,
                             null=True,
                             blank=False,
                             related_name='main',
                             verbose_name='Тип')
    style = models.ForeignKey(ProjectStyle,
                              on_delete=models.SET_NULL,
                              null=True,
                              blank=False,
                              related_name='main',
                              verbose_name='Стиль')
    tags = models.ManyToManyField(ProjectTag, blank=True, related_name='main', verbose_name='Тэги')
    area = models.FloatField(null=False, blank=False, verbose_name='Площадь')
    price_from = models.FloatField(null=False, blank=False, verbose_name='Цена от')
    price_to = models.FloatField(null=False, blank=False, verbose_name='Цена до')
    description = models.CharField(max_length=1000, null=False, blank=False, verbose_name='Описание')
    is_top = models.BooleanField(default=False, verbose_name='Топ')
    is_detailed = models.BooleanField(default=False, verbose_name='Выделенный')
    creation_date = models.DateTimeField(auto_now=True, verbose_name='Дата создания')
    rating = models.FloatField(null=False, blank=True, default=0, verbose_name='Рейтинг')
    to_profile_count = models.PositiveSmallIntegerField(null=False, blank=True, default=0,
                                                        verbose_name='Переходы в профиль')

    objects = ProjectManager()

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    def __str__(self):
        return f'{self.id}: {self.name} ({self.user})'


class ProjectUserFavorite(models.Model):
    user = models.ForeignKey(MainUser,
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False,
                             related_name='favorites',
                             verbose_name='Пользователь')
    project = models.ForeignKey(Project,
                                on_delete=models.CASCADE,
                                null=False,
                                blank=False,
                                related_name='user_favorites',
                                verbose_name='Проект')
    creation_date = models.DateTimeField(auto_now=True, null=False, blank=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Проект избранное'
        verbose_name_plural = 'Проекты избранное'

    def __str__(self):
        return f'{self.id}: {self.user.id} - {self.project.id}'


class ProjectDocument(models.Model):
    project = models.ForeignKey(Project,
                                on_delete=models.CASCADE,
                                null=False,
                                blank=False,
                                related_name='documents',
                                verbose_name='Проект')
    document = models.FileField(upload_to=upload.project_document_path,
                                validators=[validators.validate_file_size, validators.basic_validate_images],
                                verbose_name='Документ')

    class Meta:
        verbose_name = 'Фото проекта'
        verbose_name_plural = 'Фото проектов'

    def __str__(self):
        return f'{self.id}: проект ({self.project.name[0:10]}...)'


class Render360(models.Model):
    project = models.OneToOneField(Project,
                                   on_delete=models.CASCADE,
                                   null=True,
                                   blank=False,
                                   related_name='render360',
                                   verbose_name='Проект')
    document = models.FileField(upload_to=upload.project_render360_path,
                                validators=[validators.validate_file_size, validators.basic_validate_images],
                                verbose_name='Документ')

    class Meta:
        verbose_name = 'Фото 360 проекта'
        verbose_name_plural = 'Фото 360 проектов'

    def __str__(self):
        return f'{self.id}: проект ({self.project.name[0:10]}...)'


class ProjectView(models.Model):
    user = models.ForeignKey(MainUser,
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False,
                             related_name='views',
                             verbose_name='Пользователь')
    project = models.ForeignKey(Project,
                                on_delete=models.CASCADE,
                                null=False,
                                blank=False,
                                related_name='views',
                                verbose_name='Пользователь')
    creation_date = models.DateTimeField(auto_now=True, null=False, blank=True)

    class Meta:
        verbose_name = 'Просмотр проета'
        verbose_name_plural = 'Просмотры проектов'

    def __str__(self):
        return f'{self.id}: пользователь({self.user_id}) - проект({self.project_id})'


class ProjectComment(models.Model):
    user = models.ForeignKey(MainUser,
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False,
                             related_name='project_comments',
                             verbose_name='Пользователь')
    user_likes = models.ManyToManyField(MainUser,
                                        blank=True,
                                        related_name='project_comments_likes',
                                        verbose_name='Лайки пользователь')
    project = models.ForeignKey(Project,
                                on_delete=models.CASCADE,
                                null=False,
                                blank=False,
                                related_name='comments',
                                verbose_name='Проект')
    likes_count = models.IntegerField(default=0, null=False, blank=True, verbose_name='Количество лайков')
    rating = models.FloatField(null=False, blank=True, default=0, verbose_name='Рейтинг')
    text = models.CharField(max_length=1000, blank=False, null=False, verbose_name='Основной текст')
    creation_date = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name='Дата')

    class Meta:
        verbose_name = 'Комментарий проекта'
        verbose_name_plural = 'Комментарии проектов'

    def __str__(self):
        return f'{self.id}: проект({self.project.id}) текст: {self.text[:15]}'


class ProjectCommentReply(models.Model):
    user = models.ForeignKey(MainUser,
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False,
                             related_name='project_comments_replies',
                             verbose_name='Пользователь')
    comment = models.OneToOneField(ProjectComment,
                                   on_delete=models.CASCADE,
                                   null=False,
                                   blank=False,
                                   related_name='reply',
                                   verbose_name='Комментарий')
    text = models.CharField(max_length=1000, blank=False, null=False, verbose_name='Основной текст')
    creation_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    user_likes = models.ManyToManyField(MainUser,
                                        blank=True,
                                        related_name='project_comments_reply_likes',
                                        verbose_name='Лайки пользователь')
    likes_count = models.IntegerField(default=0, null=False, blank=True, verbose_name='Количество лайков')

    class Meta:
        verbose_name = 'Ответ на комментарий проекта'
        verbose_name_plural = 'Ответы на комментарии пректов'

    def __str__(self):
        return f'{self.id}: коммент({self.comment.id}) текст: {self.text[:15]}'


class ProjectCommentDocument(models.Model):
    comment = models.ForeignKey(ProjectComment,
                                on_delete=models.CASCADE,
                                null=False,
                                blank=False,
                                related_name='documents',
                                verbose_name='Комментарий')
    document = models.FileField(upload_to=upload.project_comment_document_path,
                                validators=[validators.validate_file_size, validators.basic_validate_images],
                                verbose_name='Документ')

    class Meta:
        verbose_name = 'Документ комментария'
        verbose_name_plural = 'Документы комментариев'

    def __str__(self):
        return f'{self.id}: коммент({self.comment.id}), документ({self.document.name})'


class ProjectCommentReplyDocument(models.Model):
    reply = models.ForeignKey(ProjectCommentReply,
                                on_delete=models.CASCADE,
                                null=False,
                                blank=False,
                                related_name='documents',
                                verbose_name='Ответ на комментарий')
    document = models.FileField(upload_to=upload.project_comment_reply_document_path,
                                validators=[validators.validate_file_size, validators.basic_validate_images],
                                verbose_name='Документ')

    class Meta:
        verbose_name = 'Документ ответа на комментарий'
        verbose_name_plural = 'Документы ответов на комментарии'

    def __str__(self):
        return f'{self.id}: ответ на коммент({self.comment.id}), документ({self.document.name})'


class Complain(models.Model):
    user = models.ForeignKey(MainUser,
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False,
                             verbose_name='Пользователь')
    text = models.CharField(max_length=1000, null=False, blank=False, verbose_name='Причина')
    creation_date = models.DateTimeField(auto_now=True, null=False, blank=True, verbose_name='Дата')
    is_active = models.BooleanField(default=True, null=False, blank=True, verbose_name='Активная')

    class Meta:
        abstract = True


class ProjectComplain(Complain):
    project = models.ForeignKey(Project,
                                on_delete=models.CASCADE,
                                null=False,
                                blank=False,
                                related_name='complaints',
                                verbose_name='Проект')

    class Meta:
        verbose_name = 'Жалоба на проект'
        verbose_name_plural = 'Жалобы на проекты'
        ordering = ['-creation_date', ]

    def __str__(self):
        return f'{self.id}: проект({self.project.id}): {self.text[:15]}...'


class CommentComplain(Complain):
    comment = models.ForeignKey(ProjectComment,
                                on_delete=models.CASCADE,
                                null=False,
                                blank=False,
                                related_name='complaints',
                                verbose_name='Комментарий')

    class Meta:
        verbose_name = 'Жалоба на комментарий'
        verbose_name_plural = 'Жалобы на комментарии'
        ordering = ['-creation_date', ]

    def __str__(self):
        return f'{self.id}: коммент({self.comment.id}): {self.text[:15]}...'


class CommentReplyComplain(Complain):
    reply = models.ForeignKey(ProjectCommentReply,
                                on_delete=models.CASCADE,
                                null=False,
                                blank=False,
                                related_name='complaints',
                                verbose_name='Ответ на комментарий')

    class Meta:
        verbose_name = 'Жалоба на ответ на комментарий'
        verbose_name_plural = 'Жалобы на ответы на комментарии'
        ordering = ['-creation_date', ]

    def __str__(self):
        return f'{self.id}: коммент({self.reply.id}): {self.text[:15]}...'


class ReviewComplain(Complain):
    review = models.ForeignKey(MerchantReview,
                               on_delete=models.CASCADE,
                               null=False,
                               blank=False,
                               related_name='complaints',
                               verbose_name='Отзыв')

    class Meta:
        verbose_name = 'Жалоба на отзыв'
        verbose_name_plural = 'Жалобы на отзывы'
        ordering = ['-creation_date', ]

    def __str__(self):
        return f'{self.id}: коммент({self.review.id}): {self.text[:15]}...'


class ReviewReplyComplain(Complain):
    reply = models.ForeignKey(ReviewReply,
                              on_delete=models.CASCADE,
                              null=False,
                              blank=False,
                              related_name='complaints',
                              verbose_name='Ответ на отзыв')

    class Meta:
        verbose_name = 'Жалоба на ответ на отзыв'
        verbose_name_plural = 'Жалобы на ответы на отзывы'
        ordering = ['-creation_date', ]

    def __str__(self):
        return f'{self.id}: коммент({self.reply.id}): {self.text[:15]}...'
