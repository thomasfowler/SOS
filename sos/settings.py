"""Django settings for sos project."""
import os
from pathlib import Path
from urllib.parse import urlparse

from environs import Env

# Environs Config
env = Env()
env.read_env()

# Determine the Environment Config

DEBUG = env.bool('DEBUG', False)
ADMIN_ENABLED = env.bool('ADMIN_ENABLED', False)
IS_LOCAL = env.bool('IS_LOCAL', False)
SECRET_KEY = env.str('SECRET_KEY')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# CloudRun Suggested config including CSRF_TRUSTED_ORIGINS
# Note the CLOUDRUN_SERVICE_URL is not automatically set. It's a manual env var on Cloud Run based on what is generated.
CLOUDRUN_SERVICE_URL = env.str('CLOUDRUN_SERVICE_URL', None)
CUSTOM_DOMAIN = env.str('CUSTOM_DOMAIN', None)
if CLOUDRUN_SERVICE_URL and CUSTOM_DOMAIN:
    # Add the CloudRun host
    ALLOWED_HOSTS = [urlparse(CLOUDRUN_SERVICE_URL).netloc]
    CSRF_COOKIE_SECURE = True
    CSRF_TRUSTED_ORIGINS = [CLOUDRUN_SERVICE_URL, CUSTOM_DOMAIN]
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # Because we are using Firebase Hosting for our custom domain, it strips the cookie (which is dumb).
    # See docs here: https://firebase.google.com/docs/hosting/manage-cache#using_cookies
    # So we need the session cookie to be __session instead of the default sessionid
    SESSION_COOKIE_NAME = '__session'
else:
    ALLOWED_HOSTS = ['*']
    CSRF_TRUSTED_ORIGINS = [
        'http://localhost',
        'http://127.0.0.1',
    ]
    CORS_ALLOW_ALL_ORIGINS = True


# Application definition

INSTALLED_APPS = [
    # Django Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Local Apps
    'portfolio_planner',
    # 3rd Party Apps
    'django_bootstrap5',
    'widget_tweaks',
    'django_htmx',
    'djmoney',
    'nested_admin',
    'django_tables2',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
]

ROOT_URLCONF = 'sos.urls'

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
                'portfolio_planner.context_processors.current_path',
            ],
        },
    },
]

WSGI_APPLICATION = 'sos.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env.str('DJANGO_DB_DATABASE'),
        'USER': env.str('DJANGO_DB_USERNAME'),
        'PASSWORD': env.str('DJANGO_DB_PASSWORD'),
        'HOST': env.str('DJANGO_DB_HOST', 'localhost'),
    }
}

port = env.str('DJANGO_DB_PORT', '5432')

if port != 'unix':
    DATABASES['default']['PORT'] = port

# Fixtures
FIXTURE_DIRS = (
    # Master Data
    '/portfolio_planner/fixtures/',
    # Test Data
    '/portfolio_planner/tests/fixtures/'
)


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

LANGUAGE_CODE = 'en-za'

TIME_ZONE = 'Africa/Johannesburg'

USE_I18N = True

USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

# add the correct application credentials
env.str('GOOGLE_APPLICATION_CREDENTIALS', 'gcp-service-account.json')

# Static file for dev and prod. Prod is on GCP.
# define the URL where static files will be served from
STATIC_URL = '/static/'
if DEBUG and IS_LOCAL:
    # define the path where static files will be collected
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
    # Ensure you add in all the apps static dirs here
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'portfolio_planner/static'),
    ]
else:
    STORAGES = {
        'default': {'BACKEND': 'storages.backends.gcloud.GoogleCloudStorage'},
        'staticfiles': {'BACKEND': 'storages.backends.gcloud.GoogleCloudStorage'}
    }

    # Bucket names and config
    GS_BUCKET_NAME = env.str('GOOGLE_STATIC_BUCKET_NAME')
    GS_DEFAULT_ACL = 'publicRead'

# Bootstrap Settings
BOOTSTRAP5 = {
    'javascript_in_head': True
}

# Django Tables2 Settings
DJANGO_TABLES2_TEMPLATE = "django_tables2/bootstrap5.html"

# Django-money Settings
CURRENCIES = (
    'ZAR',
)

# Login behaviour
LOGIN_REDIRECT_URL = '/'

# Custom Application Settings

# What CALENDAR period does this fiscal year start on? 1 is January, 12 is December.
FISCAL_YEAR_START_MONTH = env.int('FISCAL_YEAR_START_MONTH')
