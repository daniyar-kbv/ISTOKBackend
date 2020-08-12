"""
Django settings for istok project.

Generated by 'django-admin startproject' using Django 1.11.24.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os, datetime

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.environ.get('DEBUG', default=0))

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS').split(' ')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'django.contrib.sites',

    'rest_framework',
    'django_celery_results',
    'phone_field',
    'corsheaders',
    'admin_reorder',
    'nested_inline',
    'admin_numeric_filter',

    'users',
    'main',
    'blog',
    'other',
    'profiles',
    'payments',
    'tests',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'admin_reorder.middleware.ModelAdminReorder',
]

ROOT_URLCONF = 'istok.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'istok.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', 5432)
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = "ru-ru"

TIME_ZONE = 'Asia/Almaty'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = "/api/staticfiles/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = '/api/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

ADDITIONAL_URL = 'api/additional/'
ADDITIONAL_ROOT = os.path.join(BASE_DIR, 'additional')

AUTH_USER_MODEL = 'users.MainUser'

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 5,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'EXCEPTION_HANDLER': 'utils.exceptions.custom_exception_handler'
}

JWT_AUTH = {
    'JWT_ENCODE_HANDLER':
    'rest_framework_jwt.utils.jwt_encode_handler',

    'JWT_DECODE_HANDLER':
    'rest_framework_jwt.utils.jwt_decode_handler',

    'JWT_PAYLOAD_HANDLER':
    # 'rest_framework_jwt.utils.jwt_payload_handler',
    'utils.jwt.jwt_payload_handler',


    'JWT_PAYLOAD_GET_USER_ID_HANDLER':
    'rest_framework_jwt.utils.jwt_get_user_id_from_payload_handler',

    'JWT_RESPONSE_PAYLOAD_HANDLER':
    'rest_framework_jwt.utils.jwt_response_payload_handler',

    'JWT_SECRET_KEY': SECRET_KEY,
    'JWT_GET_USER_SECRET_KEY': None,
    'JWT_PUBLIC_KEY': None,
    'JWT_PRIVATE_KEY': None,
    'JWT_ALGORITHM': os.environ.get('JWT_ALGORITHM', 'db'),
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_LEEWAY': 0,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(minutes=1000),
    'JWT_AUDIENCE': None,
    'JWT_ISSUER': None,

    'JWT_ALLOW_REFRESH': True,
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=7),

    'JWT_AUTH_HEADER_PREFIX': 'JWT',
    'JWT_AUTH_COOKIE': None,
}

CELERY_BROKER_URL = os.environ.get('BROKER_URL', 'amqp://localhost')
CELERY_IGNORE_RESULT = False
CELERY_RESULT_BACKEND = 'amqp'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s -- %(asctime)s -- %(message)s',
        },
        'simple': {
            'format': '%(levelname)s -- %(message)s',
        }
    },
    'handlers': {
        'blog_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs') + '/blog/blog.log',
            'formatter': 'verbose',
            'backupCount': 5,
            'maxBytes': 5000000
        },
        'main_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs') + '/main/main.log',
            'formatter': 'verbose',
            'backupCount': 5,
            'maxBytes': 5000000
        },
        'payments_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs') + '/payments/payments.log',
            'formatter': 'verbose',
            'backupCount': 5,
            'maxBytes': 5000000
        },
        'profiles_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs') + '/profiles/profiles.log',
            'formatter': 'verbose',
            'backupCount': 5,
            'maxBytes': 5000000
        },
        'users_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs') + '/users/users.log',
            'formatter': 'verbose',
            'backupCount': 5,
            'maxBytes': 5000000
        },
        'console_handler': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'blog': {
            'handlers': ['blog_file', 'console_handler'],
            'level': 'DEBUG',
            'propogate': True,
        },
        'main': {
            'handlers': ['main_file', 'console_handler'],
            'level': 'DEBUG',
            'propogate': True,
        },
        'payments': {
            'handlers': ['payments_file', 'console_handler'],
            'level': 'DEBUG',
            'propogate': True,
        },
        'profiles': {
            'handlers': ['profiles_file', 'console_handler'],
            'level': 'DEBUG',
            'propogate': True,
        },
        'users': {
            'handlers': ['users_file', 'console_handler'],
            'level': 'DEBUG',
            'propogate': True,
        },
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = int(os.environ.get('EMAIL_USE_TLS'))
EMAIL_USE_SSL = int(os.environ.get('EMAIL_USE_SSL'))
ACCOUNT_EMAIL_VERIFICATION = 'none'
SERVER_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'translations', 'locale'),
)

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_HEADERS = [
    'access-control-allow-origin',
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

ADMIN_REORDER = (
    {
        'app': 'main',
        'label': 'Основной',
        'models': (
            'main.Project',
            'main.ProjectComplain',
            'main.CommentComplain',
            'main.CommentReplyComplain',
            'main.ReviewComplain',
            'main.ReviewReplyComplain'
        )
    },
    {
        'app': 'users',
        'models': (
            'users.MainUser',
            'users.MerchantReview',
            'users.ClientRating',
            'users.MerchantPhone'
        )
    },
    {
        'app': 'profiles',
        'models': (
            {'model': 'profiles.FormQuestionGroup', 'label': 'Анкета'},
            'profiles.Application',
        )
    },
    {
        'app': 'payments',
        'models': (
            'payments.PaidFeatureType',
            'payments.UsersPaidFeature',
            'payments.ProjectPaidFeature',
            'payments.ProjectLinkedPaidFeatures',
            'payments.Transaction'
        )
    },
    {
        'app': 'other',
        'label': 'Другое',
        'models': (
            'users.ProjectCategory',
            {'model': 'users.ProjectPurposeType', 'label': 'Назначения'},
            'users.ProjectType',
            'users.ProjectStyle',
            'users.Specialization',
            {'model': 'users.Country', 'label': 'Города и Страны'},
            'other.FAQ',
            'other.MailingRecipient',
            'other.Mailing'
        )
    },
    {
        'app': 'blog',
        'models': (
            'blog.BlogPostCategory',
            'blog.BlogPost',
            'blog.MainPageBlogPost'
        )
    },
)

