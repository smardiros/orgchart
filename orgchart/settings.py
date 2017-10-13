"""
Django settings for orgchart project.

Generated by 'django-admin startproject' using Django 1.11.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import ldap
from django_auth_ldap.config import LDAPSearch, LDAPGroupType, GroupOfNamesType

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*', 'http://dc-samweb.egpaf.com', 'localhost', '127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'dal',
    'dal_select2',
    'charts.apps.ChartsConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'guardian',
    'csvimport.app.CSVImportConf',
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

ROOT_URLCONF = 'orgchart.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'orgchart.wsgi.application'
LOGIN_REDIRECT_URL = '/charts'
AUTHENTICATION_BACKENDS = [
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
]

AUTH_LDAP_SERVER_URI = "ldap://dc-net1.egpaf.com"

AUTH_LDAP_BIND_AS_AUTHENTICATING_USER = True
AUTH_LDAP_BIND_DN = "CN=Sam-egpaf,OU=Administrators,OU=IT Service & Utility Accounts / Groups,OU=Consultants\, Service & Utility Accts,OU=Information Technology,OU=- Washington DC,OU=EGPAF Users - Active Accounts,DC=egpaf,DC=com"
AUTH_LDAP_BIND_PASSWORD = "Tuesday_2017!"
AUTH_LDAP_USER_SEARCH = LDAPSearch("OU= - Washington DC, OU=EGPAF Users - Active Accounts, DC=egpaf, DC=com",
    ldap.SCOPE_SUBTREE, filterstr="(sAMAccountName=%(user)s)")


AUTH_LDAP_CONNECTION_OPTIONS = {
    ldap.OPT_DEBUG_LEVEL: 1,
    ldap.OPT_REFERRALS: 0,
}

AUTH_LDAP_MIRROR_GROUPS = True

AUTH_LDAP_GROUP_SEARCH = LDAPSearch("OU=IT Service & Utility Accounts / Groups,OU=Consultants\, Service & Utility Accts,OU=Information Technology,OU=- Washington DC,OU=EGPAF Users - Active Accounts,DC=egpaf,DC=com",
    ldap.SCOPE_SUBTREE, "(objectClass=top)"
)
AUTH_LDAP_GROUP_TYPE = GroupOfNamesType()


AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    "is_active": "CN=Sam's Fabulous Org Chart Group,OU=IT Service & Utility Accounts / Groups,OU=Consultants\, Service & Utility Accts,OU=Information Technology,OU=- Washington DC,OU=EGPAF Users - Active Accounts,DC=egpaf,DC=com",
    "is_staff": "CN=Sam's Fabulous Org Chart Group,OU=IT Service & Utility Accounts / Groups,OU=Consultants\, Service & Utility Accts,OU=Information Technology,OU=- Washington DC,OU=EGPAF Users - Active Accounts,DC=egpaf,DC=com",
    "is_superuser": "CN=Sam's Fabulous Org Chart Group,OU=IT Service & Utility Accounts / Groups,OU=Consultants\, Service & Utility Accts,OU=Information Technology,OU=- Washington DC,OU=EGPAF Users - Active Accounts,DC=egpaf,DC=com",
}

# Use LDAP group membership to calculate group permissions.
AUTH_LDAP_FIND_GROUP_PERMS = True


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'django',                      
        'USER': 'postgres',
        'PASSWORD': os.environ['DATABASE_PASSWORD'],
        'HOST': 'localhost',
        'PORT': '5432',
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


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'stream_to_console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django_auth_ldap': {
            'handlers': ['stream_to_console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
STATIC_ROOT = os.path.abspath(os.path.join(BASE_DIR, 'orgchart', 'static'))    
STATIC_URL = '/static/'

MEDIA_URL = '/media/'
