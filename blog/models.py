from django.db import models
from django.db.models import Q
from users.models import MainUser, City
from utils import upload, validators


class BlogPostCategory(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False, verbose_name='Название')

    class Meta:
        verbose_name = 'Категория блога'
        verbose_name_plural = 'Категории блога'

    def __str__(self):
        return f'{self.id}: {self.name}'


class BlogPostManager(models.Manager):
    def search(self, arg, request=None):
        queryset = self.filter(Q(title__icontains=arg) |
                               Q(subtitle__icontains=arg) |
                               Q(text__icontains=arg))
        if request:
            if request.data.get('categories'):
                queryset = queryset.filter(category_id__in=request.data.get('categories'))
            queryset = queryset.order_by(
                request.data.get('order_by') if request.data.get('order_by') else '-creation_date')
        return queryset.distinct()


class BlogPost(models.Model):
    title = models.CharField(max_length=100, null=False, blank=False, verbose_name="Заголовок")
    subtitle = models.CharField(max_length=100, null=False, blank=False, verbose_name="Подзаголовок")
    text = models.CharField(max_length=10000, null=False, blank=False, verbose_name="Основоной текст")
    user = models.ForeignKey(MainUser,
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False,
                             related_name='blog_posts',
                             verbose_name='Создатель')
    creation_date = models.DateTimeField(auto_now=True, verbose_name='Дата создания')
    user_likes = models.ManyToManyField(MainUser,
                                        related_name='blog_post_likes',
                                        verbose_name='Лайки пользователей')
    category = models.ForeignKey(BlogPostCategory,
                                 on_delete=models.DO_NOTHING,
                                 null=True,
                                 blank=False,
                                 default=None,
                                 related_name='blog_posts',
                                 verbose_name='Категория')
    is_main = models.BooleanField(default=False,
                                  null=False,
                                  blank=True,
                                  verbose_name='На главной')
    city = models.ForeignKey(City,
                             on_delete=models.DO_NOTHING,
                             null=True,
                             blank=False,
                             related_name='blog_posts',
                             verbose_name='Город')

    objects = BlogPostManager()

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return f'{self.id}: {self.title[0:15]}...'


class PostDocument(models.Model):
    post = models.ForeignKey(BlogPost,
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False,
                             related_name='documents',
                             verbose_name='Пост')
    document = models.FileField(upload_to=upload.blog_post_document_path,
                                validators=[validators.validate_file_size, validators.basic_validate_images],
                                verbose_name='Документ')

    class Meta:
        verbose_name = 'Документ блога'
        verbose_name_plural = 'Документы блога'

    def __str__(self):
        return f'{self.id}: пост({self.post.id})'


class MainPageBlogPost(models.Model):
    post = models.OneToOneField(BlogPost,
                                on_delete=models.CASCADE,
                                null=False,
                                blank=False,
                                related_name='main_page',
                                verbose_name='Пост')

    class Meta:
        verbose_name = 'Пост на главной странице'
        verbose_name_plural = 'Посты на главной странице'

    def __str__(self):
        return f'{self.id}: {self.post.title[0:15]}'
