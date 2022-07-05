"""
Django settings for srestate project.

Generated by 'django-admin startproject' using Django 3.0.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
import urllib

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'os*+e_tp3#-yj#5lr^da=2%4!omhenb%$@-emahbe63+qjpa-m'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["django-env.eba-z5zkmnuv.us-west-2.elasticbeanstalk.com","srestateapi.herokuapp.com","127.0.0.1","20f0-3-7-27-185.in.ngrok.io"]


# Application definition

INSTALLED_APPS = [
    'UserManagement',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'property',
    'rest_framework.authtoken',
    'rest_framework',
    'cloudinary',
    'chat'
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

ROOT_URLCONF = 'srestate.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

WSGI_APPLICATION = 'srestate.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
'DEFAULT_PERMISSION_CLASSES': [
    'rest_framework.permissions.IsAuthenticated',
]
}


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases





# mongo_uri = "mongodb://srestatedev1:"+str(urllib.parse.quote("changingbyte123$"))+"@docdb-2022-05-17-05-48-47.cluster-cckiz4syulr1.us-west-2.docdb.amazonaws.com:27017/?ssl=true&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false"
mongo_uri =  'mongodb+srv://srestateapi:' + str(urllib.parse.quote("changingbyte@123"))  +'@cluster0.0zdkv.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'

DATABASE_ROUTERS = ['chat.routers.chatRouter','UserManagement.routers.UserManagementRouter','property.routers.propertyRouter']

DATABASES = {
        'default': {
            'ENGINE': 'djongo',
            'NAME': 'your-db-name',
            'ENFORCE_SCHEMA': False,
            'CLIENT': {
                'host': mongo_uri
            }  
        },

        'messagedb':{
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        },
        'db2': {
            'ENGINE': 'djongo',
            'NAME': 'your-db-name',
            'ENFORCE_SCHEMA': False,
            'CLIENT': {
                'host': mongo_uri
            }  
        },


}

AUTH_USER_MODEL = "UserManagement.User" 
TWILIO_ACCOUNT_SID = "ACddd7e4be77b766c76196481b7f0bf1b2"
TWILIO_AUTH_TOKEN = "8def2942088e7b44d81fbee5b0f2d476"

import dj_database_url
db_from_env = dj_database_url.config(conn_max_age=600)
DATABASES['messagedb'].update(db_from_env)

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True



# adding config
cloudinary.config(
  cloud_name = "dsk7rqudu",
  api_key = "676392571798224",
  api_secret = "0-Vtu1ua0Rl3woq6S4PwTeBM2Wo"
)

ASGI_APPLICATION = "srestate.asgi.application"
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, "static"),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

