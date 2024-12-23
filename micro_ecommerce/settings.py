"""
Django settings for micro_ecommerce project.

Generated by 'django-admin startproject' using Django 4.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "config, default=None)"
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = "atpecommercesc@gmail.com"
EMAIL_HOST_PASSWORD = "zjij lyks ckkq wbqx"
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"


ALLOWED_HOSTS = []


RECAPTCHA_SITE_KEY = '6LcnADUqAAAAAGGBPz-GXhRPlO1qLlBL3WMm8qwf'
RECAPTCHA_SECRET_KEY = '6LcnADUqAAAAAHLSWcI46yELCdJzo4P3A4k1esAe'
# RECAPTCHA_MIN_SCORE = 0.5


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # internal
    'products',
    'carro',
    'usuario',
    'extra',
    'ventas',
    'pedidos_stripe',
    'treebeard',
    'django_filters',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'micro_ecommerce.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'micro_ecommerce.context_processors.global_settings',
                'carro.context_processor.importe_total_carro',
                'products.context_processor.cantidad_like',
            ],
        },
    },
]

WSGI_APPLICATION = 'micro_ecommerce.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Add these at the top of your settings.py
#
# PGHOST='ep-lucky-butterfly-a58zhsw9-pooler.us-east-2.aws.neon.tech'
# PGDATABASE='EComerce'
# PGUSER='EComerce_owner'
# PGPASSWORD='9fXU8IcYazuR'
# # Replace the DATABASES section of your settings.py with this
#
# DATABASES = {
#   'default': {
#     'ENGINE': 'django.db.backends.postgresql',
#     'NAME': PGDATABASE,
#     'USER': PGUSER,
#     'PASSWORD': PGPASSWORD,
#     'HOST': PGHOST,
#     'PORT':  5432,
#     'OPTIONS': {
#       'sslmode': 'require',
#     },
#
#   }
# }


#
# local postgre
#
# DATABASES = {
#   'default': {
#     'ENGINE': 'django.db.backends.postgresql',
#     'NAME': 'Ecomerce',
#     'USER': 'postgres',
#     'PASSWORD': 'root',
#     'HOST': 'localhost',
#     'PORT':  5432,
#     'OPTIONS': {
#       'sslmode': 'prefer',
#     },
#
#   }
# }


#
# DATABASES = {
#     'default': dj_database_url.config()
# }

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'es'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT= BASE_DIR / "local-cdn" / "static"
MEDIA_ROOT= BASE_DIR / "local-cdn" / "media"
PROTECTED_MEDIA_ROOT= BASE_DIR / "local-cdn" / "protected"
MEDIA_URL= "media/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
