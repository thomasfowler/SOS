"""Django settings for sos project."""
import io
import os
from pathlib import Path
from urllib.parse import urlparse

import environ
from google.cloud import secretmanager

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Environs Config
env = environ.Env()
env_file = os.path.join(BASE_DIR, ".env")

if os.path.isfile(env_file):
    # Use a local secret file, if provided
    print(f'Found .env file: {env_file}')
    env.read_env(env_file)
elif os.environ.get("GOOGLE_CLOUD_PROJECT", None):
    # Pull secrets from Secret Manager
    # This block of code is typically only used during the build phase so we can easily pull secrets into
    # the build images. During a typical Cloud Run deployment, we prefer to use normal environment variables
    # provided by secret manager.
    print(f'Using Google Cloud')
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")

    client = secretmanager.SecretManagerServiceClient()
    settings_name = os.environ.get("SETTINGS_NAME")

    if not settings_name:
        raise ValueError("SETTINGS_NAME environment variable not set")

    print(f'Attempting to use secret from secret manager {settings_name}')
    name = f"projects/{project_id}/secrets/{settings_name}/versions/latest"
    payload = client.access_secret_version(name=name).payload.data.decode("UTF-8")

    env.read_env(io.StringIO(payload))
else:
    print("No local .env or GOOGLE_CLOUD_PROJECT detected. Proceeding to use environment variables")

# Determine the Environment Config

DEBUG = env.bool('DEBUG', False)
ADMIN_ENABLED = env.bool('ADMIN_ENABLED', False)
IS_LOCAL = env.bool('IS_LOCAL', False)
SECRET_KEY = env.str('SECRET_KEY')

# CloudRun Suggested config including CSRF_TRUSTED_ORIGINS
# Note the CLOUDRUN_SERVICE_URL is not automatically set. It's a manual env var on Cloud Run based on what is generated.
CLOUDRUN_SERVICE_URL = env.str('CLOUDRUN_SERVICE_URL', None)
CUSTOM_DOMAIN = env.str('CUSTOM_DOMAIN', None)
if CLOUDRUN_SERVICE_URL and CUSTOM_DOMAIN:
    # Add the CloudRun host
    print(f'Using CLOUDRUN_SERVICE_URL: {CLOUDRUN_SERVICE_URL}')
    print(f'Using CUSTOM_DOMAIN: {CUSTOM_DOMAIN}')
    ALLOWED_HOSTS = [
        urlparse(CLOUDRUN_SERVICE_URL).netloc,
        urlparse(CUSTOM_DOMAIN).netloc
    ]
    CSRF_COOKIE_SECURE = True
    CSRF_TRUSTED_ORIGINS = [
        CLOUDRUN_SERVICE_URL,
        CUSTOM_DOMAIN
    ]
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
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
    # 3rd Party Apps
    'django_use_email_as_username.apps.DjangoUseEmailAsUsernameConfig',
    'rolepermissions',
    'django_bootstrap5',
    'widget_tweaks',
    'django_htmx',
    'djmoney',
    'nested_admin',
    'django_tables2',
    # Local Apps
    'portfolio_planner',
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
        'DIRS': [
            BASE_DIR / "portfolio_planner/templates",
        ],
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

if IS_LOCAL:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env.str('DJANGO_DB_DATABASE'),
            'USER': env.str('DJANGO_DB_USERNAME'),
            'PASSWORD': env.str('DJANGO_DB_PASSWORD'),
            'HOST': env.str('DJANGO_DB_HOST', 'localhost'),
        }
    }
else:
    # This usues the environs DB string parser to parse the DB string from the env var
    # See the docs for an explanation.
    DATABASES = {"default": env.db()}

    # If the flag as been set, configure to use proxy
    if os.getenv("USE_CLOUD_SQL_AUTH_PROXY", None):
        DATABASES["default"]["HOST"] = "127.0.0.1"
        DATABASES["default"]["PORT"] = 5432

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

# Custom Auth User
AUTH_USER_MODEL = 'portfolio_planner.User'
ROLEPERMISSIONS_MODULE = 'sos.roles'

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
LOGIN_URL = '/login/'

# Custom Application Settings

# What CALENDAR period does this fiscal year start on? 1 is January, 12 is December.
FISCAL_YEAR_START_MONTH = env.int('FISCAL_YEAR_START_MONTH')

# Sendgrid
SENDGRID_API_KEY = env.str('SENDGRID_API_KEY')
PASSWORD_REST_EMAIL_TEMPLATE_ID = env.str('PASSWORD_REST_EMAIL_TEMPLATE_ID')
PASSWORD_RESET_EMAIL_FROM = env.str('PASSWORD_RESET_EMAIL_FROM')
