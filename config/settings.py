"""
Django settings for config project.
...
"""

from pathlib import Path
import os
import sys
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega as variáveis do arquivo .env
load_dotenv()

# SECURITY WARNING: don't run with debug turned on in production!
# Lê do .env. Se DEBUG não estiver definido, fica False (seguro por padrão).
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# A SECRET_KEY é obrigatória: sem ela a aplicação não deve subir.
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ImproperlyConfigured(
        "Defina a variável SECRET_KEY no arquivo .env (veja o .env.example)."
    )

ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'embed_video',
    'blog',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # logo após o SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # escolhe o idioma (cookie > navegador > padrão)
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Django Debug Toolbar: apenas em desenvolvimento
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE.insert(
        MIDDLEWARE.index('django.middleware.clickjacking.XFrameOptionsMiddleware') + 1,
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )
    INTERNAL_IPS = ["127.0.0.1"]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'blog.context_processors.social_links',
                'blog.context_processors.site_theme',
                'blog.context_processors.js_strings',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en'

# Idiomas do site. A primeira visita usa o idioma do navegador (se for um destes); a escolha
# feita no seletor fica guardada em um cookie. Os arquivos de tradução ficam em locale/.
LANGUAGES = [
    ('en', 'English'),
    ('pt-br', 'Português'),
    ('ja', '日本語'),
]
LOCALE_PATHS = [BASE_DIR / 'locale']

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "blog" / "static",
]
# Pasta de destino do `collectstatic` (o WhiteNoise serve os arquivos daqui)
STATIC_ROOT = BASE_DIR / "staticfiles"

# Armazenamento de arquivos (Django 4.2+ / 5.x).
# "default" = uploads de mídia; "staticfiles" = estáticos com compressão + hash no nome.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Media files (User-uploaded files like images)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Configurações de Autenticação (redirecionamento após login/logout)
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

# Configuração de Email (exibe no console em vez de enviar)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Mensagens: o Bootstrap usa "danger" no lugar de "error"
from django.contrib.messages import constants as messages

MESSAGE_TAGS = {messages.ERROR: "danger"}

# Segurança extra quando DEBUG=False
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True


# Redes sociais exibidas no topo do site (URLs vindas do .env; vazio vira "#")
SOCIAL_LINKS = [
    {"name": "Instagram", "url": os.getenv("SOCIAL_INSTAGRAM_URL") or "#"},
    {"name": "Facebook", "url": os.getenv("SOCIAL_FACEBOOK_URL") or "#"},
    {"name": "TikTok", "url": os.getenv("SOCIAL_TIKTOK_URL") or "#"},
    {"name": "LinkedIn", "url": os.getenv("SOCIAL_LINKEDIN_URL") or "#"},
]

# Tema visual do site (escolhido no .env):
#   "magic"   - pergaminho e velas, com os modos Lumos (claro) e Nox (escuro)
#   "classic" - bege e marrom, o visual anterior (continua disponível)
SITE_THEME = os.getenv("SITE_THEME", "magic").strip().lower()
if SITE_THEME not in ("magic", "classic"):
    SITE_THEME = "magic"

# Nos testes não existe manifesto do collectstatic; sem isto, qualquer template
# que use {% static %} falharia com "Missing staticfiles manifest entry".
if "test" in sys.argv:
    STORAGES["staticfiles"] = {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    }


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# Permite que o YouTube receba a identificação necessária para incorporar o vídeo
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"