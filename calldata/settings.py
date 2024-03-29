"""
Django settings for calldata project.

Generated by 'django-admin startproject' using Django 4.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os
from urllib.parse import quote_plus



# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-*r+x4u)uc)qu!s!tse&y@e&h+ns)8x^ubm)5-lk1w#q%sek1@j'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['.vercel.app','10.0.2.2','127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'calldataapp',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'calldata.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templetes')],
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

WSGI_APPLICATION = 'calldata.wsgi.application'



username = "naveed78603"
password = "kashaf2016"
cluster_name = "cluster0.pzjqmxn.mongodb.net"    # Omit the port
database = "ztecall"

# Escape the username and password using quote_plus
escaped_username = quote_plus(username)
escaped_password = quote_plus(password)

# Create the MongoDB Atlas connection string with SRV record (without specifying port)
connection_string = f"mongodb+srv://{escaped_username}:{escaped_password}@{cluster_name}/{database}?retryWrites=true&w=majority"

DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'ztecall',
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
            'host': connection_string,
            'username': username,
            'password': password,
            'name': database,
        }
    }
}





# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME':'calldata',
#         'HOST':'localhost',
#         'USER':'root',
#         'PASSWORD':'',
#         'PORT':'3306',
#     }
# }
AUTH_USER_MODEL = 'calldataapp.User'


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-in'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT=os.path.join(BASE_DIR, '/static/')
STATICFILES_DIRS=[
    os.path.join(BASE_DIR,'static/')
]

MEDIA_URL='/media/'
MEDIA_ROOT=os.path.join(BASE_DIR,'media/')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
