from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractUser, BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db.models.query_utils import DeferredAttribute
from utils.upload import user_avatar_path, profile_document_path, project_category_image_path, review_document_path, \
    review_reply_document_path
from utils.validators import validate_file_size, basic_validate_images
from itertools import chain
from constants import ROLES, ROLE_CLIENT, ROLE_MERCHANT
import os


class ProjectCategory(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False, verbose_name='Название')
    description = models.CharField(max_length=1000, null=False, blank=False, verbose_name='Описание')
    image = models.FileField(upload_to=project_category_image_path,
                             validators=[basic_validate_images, validate_file_size],
                             null=True,
                             blank=True,
                             verbose_name='Изображение')

    class Meta:
        verbose_name = 'Категория проектов'
        verbose_name_plural = 'Категории проектов'

    def __str__(self):
        return f'{self.id}: {self.name}'


class ProjectPurposeType(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False, verbose_name='Название')

    class Meta:
        verbose_name = 'Тип назначения'
        verbose_name_plural = 'Типы назначений'

    def __str__(self):
        return f'{self.id}: {self.name}'


class ProjectPurposeSubType(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False, verbose_name='Название')
    type = models.ForeignKey(ProjectPurposeType,
                           on_delete=models.CASCADE,
                           null=True,
                           blank=False,
                           related_name='subtypes',
                           verbose_name='Тип')

    class Meta:
        verbose_name = 'Подтип назначения'
        verbose_name_plural = 'Подтипы назначения'

    def __str__(self):
        return f'{self.id}: {self.name}'


class ProjectPurpose(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False, verbose_name='Название')
    type = models.ForeignKey(ProjectPurposeType,
                             on_delete=models.DO_NOTHING,
                             null=True,
                             blank=False,
                             related_name='purposes',
                             verbose_name='Тип')
    subtype = models.ForeignKey(ProjectPurposeSubType,
                                on_delete=models.DO_NOTHING,
                                null=True,
                                blank=True,
                                related_name='purposes',
                                verbose_name='Подтип')

    class Meta:
        verbose_name = 'Назначение'
        verbose_name_plural = 'Назначения'

    def __str__(self):
        return f'{self.id}: {self.name}'


class ProjectType(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False, verbose_name='Название')

    class Meta:
        verbose_name = 'Тип проекта'
        verbose_name_plural = 'Типы проекта'

    def __str__(self):
        return f'{self.id}: {self.name}'


class ProjectStyle(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False, verbose_name='Название')

    class Meta:
        verbose_name = 'Стиль'
        verbose_name_plural = 'Стили'

    def __str__(self):
        return f'{self.id}: {self.name}'


class ProjectTagManager(models.Manager):
    def search(self, arg):
        return self.filter(name__icontains=arg)


class ProjectTag(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False, verbose_name='Название')
    category = models.ForeignKey(ProjectCategory,
                                 on_delete=models.CASCADE,
                                 null=False,
                                 blank=False,
                                 related_name='tags',
                                 verbose_name='Категория')
    objects = ProjectTagManager()

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return f'{self.id}: {self.name}'


class Country(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False, verbose_name='Название')

    class Meta:
        verbose_name = 'Страна'
        verbose_name_plural = 'Страны'

    def __str__(self):
        return f'{self.id}: {self.name}'


class City(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False, verbose_name='Название')
    country = models.ForeignKey(Country,
                                on_delete=models.CASCADE,
                                null=False,
                                blank=False,
                                related_name='cities',
                                verbose_name='Страна')

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'

    def __str__(self):
        return f'{self.id}: {self.name}'


class Specialization(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False, verbose_name='Название')
    category = models.ForeignKey(ProjectCategory,
                                 on_delete=models.CASCADE,
                                 null=False,
                                 blank=False,
                                 related_name='specializations',
                                 verbose_name='Категория')

    class Meta:
        verbose_name = 'Специализация'
        verbose_name_plural = 'Специализации'

    def __str__(self):
        return f'{self.id}: {self.name}'


class MainUserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

    def search(self, arg=None, request=None):
        client_queryset = self.filter(role=ROLE_CLIENT)
        merchant_queryset = self.filter(role=ROLE_MERCHANT)
        if arg:
            merchant_queryset = merchant_queryset.filter(
                Q(email__icontains=arg) |
                Q(merchant_profile__first_name__icontains=arg) |
                Q(merchant_profile__last_name__icontains=arg) |
                Q(merchant_profile__company_name__icontains=arg) |
                Q(merchant_profile__description_full__icontains=arg) |
                Q(merchant_profile__description_short__icontains=arg))
            client_queryset = client_queryset.filter(
                Q(email=arg) |
                Q(client_profile__first_name__icontains=arg) |
                Q(client_profile__last_name__icontains=arg)
            )
        if request:
            filters = dict(request.GET)
            try:
                del filters['q']
            except KeyError:
                pass
            for key in filters:
                attribute = key.split('__')[0]
                attr_type = type(getattr(MainUser, attribute))
                if isinstance(filters[key], list) and len(filters[key]) == 1:
                    filters[key] = filters[key][0]
                if attr_type == bool or attribute == 'is_active' or attribute == 'is_staff' or attribute == 'role':
                    filters[key] = int(filters[key])
            print(filters)
            merchant_queryset = merchant_queryset.filter(**filters)
            client_queryset = client_queryset.filter(**filters)
        queryset = client_queryset.union(merchant_queryset)
        return queryset, True

    def merchant_search(self, arg=None, request=None):
        queryset = self.filter(role=ROLE_MERCHANT)
        if arg:
            queryset = queryset.filter(
                                Q(merchant_profile__first_name__icontains=arg) |
                                Q(merchant_profile__last_name__icontains=arg) |
                                Q(merchant_profile__company_name__icontains=arg) |
                                Q(merchant_profile__categories__name__icontains=arg) |
                                Q(merchant_profile__specializations__name__icontains=arg) |
                                Q(merchant_profile__tags__name__icontains=arg) |
                                Q(merchant_profile__description_full__icontains=arg) |
                                Q(merchant_profile__description_short__icontains=arg))
        if request:
            if request.data.get('cities'):
                queryset = queryset.filter(merchant_profile__city_id__in=request.data.get('cities'))
            if request.data.get('categories'):
                queryset = queryset.filter(merchant_profile__categories__in=request.data.get('categories'))
            if request.data.get('specializations'):
                queryset = queryset.filter(merchant_profile__specializations__in=request.data.get('specializations'))
            if request.data.get('tags'):
                queryset = queryset.filter(merchant_profile__tags__in=request.data.get('tags'))
            if request.data.get('area_from') and request.data.get('area_to'):
                queryset = queryset.filter(Q(area__gte=request.data.get('area_from')) &
                                           Q(area__lte=request.data.get('area_to')))
            if request.data.get('price_from') and request.data.get('price_to'):
                queryset = queryset.filter(Q(price__gte=request.data.get('price_from')) &
                                           Q(price__lte=request.data.get('price_to')))
            queryset = queryset.order_by(request.data.get('order_by') if request.data.get('order_by') else '-merchant_profile__rating')
        return queryset.distinct()


class MainUser(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True, verbose_name='Email')
    role = models.PositiveSmallIntegerField(choices=ROLES, default=ROLE_CLIENT, verbose_name='Роль')
    creation_date = models.DateTimeField(auto_now=True, null=False, blank=True, verbose_name='Дата регистрации')

    is_staff = models.BooleanField(default=False, verbose_name='Админ')
    is_active = models.BooleanField(default=True, verbose_name='Активный')

    objects = MainUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-id']

    def __str__(self):
        return f'{self.id}: {self.get_full_name()}'

    def get_full_name(self):
        try:
            return f'{self.client_profile.first_name} {self.client_profile.last_name}'
        except:
            try:
                if self.merchant_profile.company_name:
                    return self.merchant_profile.company_name
                elif self.merchant_profile.first_name and self.merchant_profile.last_name:
                    return f'{self.merchant_profile.first_name} {self.merchant_profile.last_name}'
            except:
                return f'{self.email}'

    @property
    def full_name(self):
        return self.get_full_name()

    @property
    def profile(self):
        if self.role == ROLE_CLIENT:
            try:
                return self.client_profile
            except:
                return self.merchant_profile
        elif self.role == ROLE_MERCHANT:
            try:
                return self.merchant_profile
            except:
                return self.client_profile


class ProfileDocument(models.Model):
    user = models.ForeignKey(MainUser,
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False,
                             related_name='documents',
                             verbose_name='Пользователь')
    document = models.FileField(upload_to=profile_document_path,
                                validators=[validate_file_size, basic_validate_images],
                                verbose_name='Документ')

    class Meta:
        verbose_name = 'Документ специалиста'
        verbose_name_plural = 'Документы специалистов'

    def __str__(self):
        return f'{self.id}: {self.document.name}'

    def filename(self):
        return os.path.basename(self.document.name)


class Profile(models.Model):
    first_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='Имя')
    last_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='Фамилия')
    rating = models.FloatField(null=True, blank=True, verbose_name='Рейтинг')

    avatar = models.FileField(upload_to=user_avatar_path,
                              validators=[validate_file_size, basic_validate_images],
                              null=True,
                              blank=True)

    class Meta:
        abstract = True

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'


class ClientProfile(Profile):
    date_of_birth = models.DateField(null=False, blank=False, verbose_name='Дата рождения')
    user = models.OneToOneField(MainUser,
                                on_delete=models.CASCADE,
                                null=False,
                                blank=False,
                                related_name='client_profile',
                                verbose_name='Профиль')

    class Meta:
        verbose_name = 'Профиль клиента'
        verbose_name_plural = 'Профили клиентов'

    def __str__(self):
        return f'{self.id}: {self.get_full_name()}'


class MerchantProfile(Profile):
    user = models.OneToOneField(MainUser,
                                on_delete=models.CASCADE,
                                null=False,
                                blank=False,
                                related_name='merchant_profile',
                                verbose_name='Профиль')
    company_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='Название компании')
    city = models.ForeignKey(City,
                             on_delete=models.DO_NOTHING,
                             null=True,
                             blank=False,
                             related_name='merchant_profiles',
                             verbose_name='Город')
    address = models.CharField(max_length=500, null=True, blank=True)
    categories = models.ManyToManyField(ProjectCategory,
                                        blank=False,
                                        related_name='merchant_profiles',
                                        verbose_name='Категория')
    specializations = models.ManyToManyField(Specialization,
                                             blank=False,
                                             related_name='merchant_profiles',
                                             verbose_name='Специалиация')
    tags = models.ManyToManyField(ProjectTag,
                                  blank=True,
                                  related_name='merchant_profiles',
                                  verbose_name='Тэги')
    description_short = models.CharField(max_length=160, null=False, blank=False, verbose_name='Краткое описание')
    description_full = models.CharField(max_length=1000, null=False, blank=False, verbose_name='Подробное описание')
    url = models.URLField(null=True, blank=True, verbose_name='Ссылка')
    documents_description = models.CharField(max_length=1000,
                                             null=True,
                                             blank=False,
                                             verbose_name='Описание документов')
    is_pro = models.BooleanField(default=False,
                              blank=True,
                              null=False,
                              verbose_name='Про аккаунт')
    rating = models.FloatField(default=0, null=True, blank=True, verbose_name='Рейтинг')

    class Meta:
        verbose_name = 'Профиль специалиста'
        verbose_name_plural = 'Профили специалистов'

    def __str__(self):
        if self.first_name and self.last_name:
            return f'{self.id}: {self.get_full_name()}'
        else:
            return f'{self.id}: {self.company_name}'


class UserActivation(models.Model):
    user = models.OneToOneField(MainUser,
                                on_delete=models.CASCADE,
                                null=True,
                                blank=True,
                                default=None,
                                related_name='activation',
                                verbose_name='Пользователь')
    email = models.EmailField(null=False, blank=False, verbose_name='Email')
    is_active = models.BooleanField(default=True, null=False, blank=False, verbose_name='Активный')
    creation_date = models.DateTimeField(auto_now=True, null=False, blank=True, verbose_name='Дата создания')
    role = models.PositiveSmallIntegerField(choices=ROLES, default=ROLE_CLIENT, verbose_name='Роль')
    name = models.CharField(max_length=100, null=True, blank=True, verbose_name='Имя')

    class Meta:
        verbose_name = 'Активация'
        verbose_name_plural = 'Активации'

    def __str__(self):
        return f'{self.id}: {self.user.email if self.user else ""}'


class MerchantPhone(models.Model):
    user = models.ForeignKey(MainUser,
                             null=True,
                             blank=True,
                             on_delete=models.CASCADE,
                             default=None,
                             related_name='phones',
                             verbose_name='Пользователь')
    phone = models.CharField(max_length=18, null=False, blank=False, verbose_name='Номер телефона')
    is_valid = models.BooleanField(default=False,
                                   null=False,
                                   blank=False,
                                   verbose_name='Подтвержден')

    class Meta:
        verbose_name = 'Номер телефона'
        verbose_name_plural = 'Номера телефона'

    def __str__(self):
        return f'{self.phone}'


class CodeVerification(models.Model):
    phone = models.OneToOneField(MerchantPhone,
                                 null=False,
                                 blank=False,
                                 on_delete=models.CASCADE,
                                 related_name='verification',
                                 verbose_name='Номер телефона')
    code = models.CharField(max_length=4, null=False, blank=False, verbose_name='Код')
    creation_date = models.DateTimeField(auto_now=True, null=False, blank=False, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Подтпреждение номера телефона'
        verbose_name_plural = 'Подтпреждения номеров телефона'

    def __str__(self):
        return f'{self.id}: {self.phone.phone}'


class MerchantReview(models.Model):
    user = models.ForeignKey(MainUser,
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False,
                             related_name='sent_reviews',
                             verbose_name='Отправитель',)
    merchant = models.ForeignKey(MainUser,
                                 on_delete=models.CASCADE,
                                 null=False,
                                 blank=False,
                                 related_name='received_reviews',
                                 verbose_name='Получатель')
    user_likes = models.ManyToManyField(MainUser,
                                        blank=True,
                                        related_name='reviews_likes',
                                        verbose_name='Пользователи лайки')
    likes_count = models.IntegerField(default=0, null=False, blank=True, verbose_name='Количество лайков')
    rating = models.FloatField(default=0,
                               null=False,
                               blank=True,
                               verbose_name='Рейтинг')
    text = models.CharField(max_length=500,
                            null=False,
                            blank=False,
                            verbose_name='Основной текст')
    creation_date = models.DateTimeField(auto_now=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'{self.id}: {self.user.id}:{self.user.get_full_name()} -> {self.merchant.id}:{self.merchant.get_full_name()}'


class ReviewDocument(models.Model):
    review = models.ForeignKey(MerchantReview,
                               on_delete=models.CASCADE,
                               null=False,
                               blank=False,
                               related_name='documents',
                               verbose_name='Отзыв')
    document = models.FileField(upload_to=review_document_path,
                                validators=[validate_file_size, basic_validate_images],
                                verbose_name='Документ')

    class Meta:
        verbose_name = 'Фото отзыва'
        verbose_name_plural = 'Фото отзывов'

    def __str__(self):
        return f'Документ ({self.id}) отзыва ({self.review.id})'


class ReviewReply(models.Model):
    user = models.ForeignKey(MainUser,
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False,
                             related_name='merchant_reviews_replies',
                             verbose_name='Пользователь')
    review = models.OneToOneField(MerchantReview,
                               on_delete=models.CASCADE,
                               null=False,
                               blank=False,
                               related_name='reply',
                               verbose_name='Отзыв')
    text = models.CharField(max_length=1000, blank=False, null=False, verbose_name='Основной текст')
    user_likes = models.ManyToManyField(MainUser,
                                        blank=True,
                                        related_name='reply_likes',
                                        verbose_name='Лайки')
    creation_date = models.DateTimeField(auto_now=True, null=False, blank=False)
    likes_count = models.IntegerField(default=0, null=False, blank=True, verbose_name='Количество лайков')

    class Meta:
        verbose_name = 'Ответ на отзыв'
        verbose_name_plural = 'Ответы на отзывы'

    def __str__(self):
        return f'{self.id}: отзыв ({self.review.id})'


class ReviewReplyDocument(models.Model):
    reply = models.ForeignKey(ReviewReply,
                               on_delete=models.CASCADE,
                               null=False,
                               blank=False,
                               related_name='documents',
                               verbose_name='Ответ на отзыв')
    document = models.FileField(upload_to=review_reply_document_path,
                                validators=[validate_file_size, basic_validate_images],
                                verbose_name='Документ')

    class Meta:
        verbose_name = 'Фото ответа на отзыв'
        verbose_name_plural = 'Фото ответов на отзывы'

    def __str__(self):
        return f'Документ ({self.id}) ответа на отзыв ({self.reply.id})'


class ClientRating(models.Model):
    user = models.ForeignKey(MainUser,
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False,
                             related_name='to_client_ratings',
                             verbose_name='Специалист')
    client = models.ForeignKey(MainUser,
                               on_delete=models.CASCADE,
                               null=False,
                               blank=False,
                               related_name='client_ratings',
                               verbose_name='Клиент')
    rating = models.FloatField(null=False, blank=False, default=0, verbose_name='Рейтинг')
    creation_date = models.DateTimeField(auto_now=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Рейтинг клиента'
        verbose_name_plural = 'Рейтинги клиентов'

    def __str__(self):
        return f'{self.id}: Специалист({self.user_id}) Клиент({self.client_id}) ({self.rating})'
