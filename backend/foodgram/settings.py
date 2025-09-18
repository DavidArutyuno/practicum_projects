import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-key-0123456789')

DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

CSRF_TRUSTED_ORIGINS = os.getenv(
    'CSRF_TRUSTED_ORIGINS',
    'http://localhost:3000,http://127.0.0.1:3000',
).split(',')

CORS_ALLOWED_ORIGINS = os.getenv(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:3000,http://127.0.0.1:3000',
).split(',')

CORS_ALLOW_CREDENTIALS = os.getenv('CORS_ALLOW_CREDENTIALS', 'False') == 'True'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'django_filters',
    'corsheaders',

    'core.apps.CoreConfig',
    'api.apps.ApiConfig',
    'recipes.apps.RecipesConfig',
    'users.apps.UsersConfig',
    'debug_toolbar',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'foodgram.urls'

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

WSGI_APPLICATION = 'foodgram.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'django'),
        'USER': os.getenv('POSTGRES_USER', 'django'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', ''),
        'PORT': os.getenv('DB_PORT', 5432)
    }
}

# Password validation

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

LANGUAGE_CODE = 'ru-Ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True


STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'collected_static'

MEDIA_URL = '/media/'
MEDIA_ROOT = '/app/media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Debug toolbar

INTERNAL_IPS = [
    '127.0.0.1',
]


# Api

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 6,
}

DJOSER = {
    'LOGIN_FIELD': 'email',
    'SERIALIZERS': {
        'user': 'api.serializers.UserSerializer',
        'current_user': 'api.serializers.UserSerializer',
        'user_create': 'api.serializers.UserCreateSerializer',
        'token_create': 'djoser.serializers.TokenCreateSerializer',
    },
}


# User model settings

AUTH_USER_MODEL = 'users.User'
USER_NAME_LIMIT = 150
USER_EMAIL_LIMIT = 254
USER_AVATAR_DIR = 'users/avatars/'


# Recipe model settings

TAG_NAME_LIMIT = 32
INGREDIENT_NAME_LIMIT = 128
MEASUREMENT_UNIT_LIMIT = 64
RECIPE_NAME_LIMIT = 256
RECIPE_IMAGE_DIR = 'recipes/images/'


# Short_link

LENGTH = 8


# Admin panel: Common settings

EMPTY_VALUE_DISPLAY = '-пусто-'

SITE_HEADER = 'Панель администратора Foodgram'
INDEX_TITLE = 'Администрирование сайта Foodgram'


# Admin panel: User

USER_LIST_DISPLAY_LINKS = ('id', 'username',)
USER_LIST = ('first_name', 'last_name', 'email', 'avatar',)
USER_LIST_DISPLAY = USER_LIST_DISPLAY_LINKS + USER_LIST
USER_LIST_EDITABLE = USER_LIST
USER_LIST_FILTER = ('email', 'username',)
USER_EXTRA_FIELDS = ('avatar',)


# Admin panel: Tag, Ingredient, Recipe

RECIPE_LIST_DISPLAY_LINKS = ('id', 'name',)

TAG_LIST = ('slug',)
INGREDIENT_LIST = ('measurement_unit',)
RECIPE_LIST = ('author', 'favorites_count', 'created',)

TAG_LIST_DISPLAY = RECIPE_LIST_DISPLAY_LINKS + TAG_LIST
INGREDIENT_LIST_DISPLAY = RECIPE_LIST_DISPLAY_LINKS + INGREDIENT_LIST
RECIPE_LIST_DISPLAY = RECIPE_LIST_DISPLAY_LINKS + RECIPE_LIST

TAG_SEARCH_FIELDS = ('name', 'slug')

INGREDIENT_SEARCH_FIELDS = ('name',)
INGREDIENT_LIST_FILTER = ('measurement_unit',)

RECIPE_LIST_FILTER = ('tags', 'author', 'created')
RECIPE_SEARCH_FIELDS = ('name', 'author__username', 'author__email')
RECIPE_READONLY_FIELDS = ('favorites_count', 'created')
RECIPE_FILTER_HORIZONTAL = ('tags',)


# Admin panel: IngredientInRecipe (IIR)

IIR_LIST_DISPLAY_LINKS = ('id', 'recipe')
IIR_LIST_DISPLAY = IIR_LIST_DISPLAY_LINKS + ('ingredient', 'amount')
IIR_LIST_FILTER = ('recipe', 'ingredient')
IIR_SEARCH_FIELDS = ('recipe__name', 'ingredient__name')


# Admin panel: Favorite, ShoppingCart

FS_LIST_DISPLAY_LINKS = ('id', 'user')
FS_LIST_DISPLAY = ('id', 'user', 'recipe', 'get_author')
FS_LIST_FILTER = ('user', 'recipe')
FS_SEARCH_FIELDS = ('user__username', 'recipe__name')
