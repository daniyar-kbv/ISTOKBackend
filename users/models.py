from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, AbstractBaseUser, PermissionsMixin

from utils.upload import user_avatar_path, profile_document_path, project_category_image_path
from utils.validators import validate_file_size, basic_validate_images

from constants import ROLES, ROLE_CLIENT


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


class ProjectPurposeSubType(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False, verbose_name='Название')

    class Meta:
        verbose_name = 'Подтип назначения'
        verbose_name_plural = 'Подтипы назначения'

    def __str__(self):
        return f'{self.id}: {self.name}'


class ProjectPurposeType(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False, verbose_name='Название')

    class Meta:
        verbose_name = 'Тип назначения'
        verbose_name_plural = 'Типы назначений'

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


class ProjectTag(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False, verbose_name='Название')
    category = models.ForeignKey(ProjectCategory,
                                 on_delete=models.CASCADE,
                                 null=False,
                                 blank=False,
                                 related_name='tags',
                                 verbose_name='Категория')

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


class MainUser(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True, verbose_name='Email')
    role = models.PositiveSmallIntegerField(choices=ROLES, default=ROLE_CLIENT, verbose_name='Роль')

    is_staff = models.BooleanField(default=False, verbose_name='Админ')
    is_active = models.BooleanField(default=True, verbose_name='Активный')

    objects = MainUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


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


class Profile(models.Model):
    first_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='Имя')
    last_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='Фамилия')
    rating = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Рейтинг')

    avatar = models.FileField(upload_to=user_avatar_path,
                              validators=[validate_file_size, basic_validate_images],
                              null=True,
                              blank=True)

    class Meta:
        abstract = True

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'


class ClientProfile(Profile):
    date_of_birth = models.DateTimeField(null=False, blank=False, verbose_name='Дата рождения')
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
    pro = models.BooleanField(default=False,
                              blank=True,
                              null=False,
                              verbose_name='Про аккаунт')

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
    is_active = models.BooleanField(default=False, null=False, blank=False, verbose_name='Активный')
    creation_date = models.DateTimeField(auto_now=True, null=False, blank=True, verbose_name='Дата создания')
    role = models.PositiveSmallIntegerField(choices=ROLES, default=ROLE_CLIENT, verbose_name='Роль')

    class Meta:
        verbose_name = 'Активация'
        verbose_name_plural = 'Активации'

    def __str__(self):
        return f'{self.id}: {self.user.email}'


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
