import os
from pathlib import Path
from dotenv import load_dotenv

# Находим путь к файлу .env и загружаем переменные из него в окружение os.environ
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# Секретный ключ и режим отладки
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-key')
DEBUG = True

ALLOWED_HOSTS = []

# Обязательные базовые приложения Django + приложение mailings
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Приложение для рассылок
    'mailings',
]

# Промежуточные слои (исправляют ошибки (admin.E408), (admin.E409), (admin.E410) из терминала)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# Настройка шаблонов (исправляет ошибку (admin.E403) из терминала)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Путь к глобальным шаблонам, если понадобятся
        'APP_DIRS': True,  # Позволяет Django искать шаблоны внутри папок приложений
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

WSGI_APPLICATION = 'config.wsgi.application'

# Настройки подключения к PostgreSQL (загружаются из вашего .env)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # БЗ PostgresSQL
        'NAME': os.getenv('NAME'),                  # импорт из .env
        'USER': os.getenv('USER'),                  # импорт из .env
        'PASSWORD': os.getenv('PASSWORD'),          # импорт из .env
        'HOST': os.getenv('HOST'),                  # импорт из .env
        'PORT': os.getenv('PORT'),                  # импорт из .env
    }
}


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'coursework_04',          # Имя базы данных, которую создали в pgAdmin
#         'USER': 'postgres',            # Ваш логин от PostgreSQL (по умолчанию postgres)
#         'PASSWORD': 'ваш_пароль_от_pgadmin', # Впишите сюда ваш пароль от pgAdmin / Postgres
#         'HOST': '127.0.0.1',           # Локальный хост
#         'PORT': '5433',                # Стандартный порт PostgreSQL
#     }
# }

# Базовая валидация паролей
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

# Интернационализация (язык интерфейса админки и время)
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# Статические файлы (CSS, JavaScript, Images)
STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
