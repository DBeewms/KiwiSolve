"""config.settings
Archivo de configuración principal del proyecto Django.

Objetivo:
    Mantener una configuración clara, legible y fácil de extender siguiendo
    principios de Clean Code: nombres explícitos, agrupación lógica y comentarios
    que aporten intención (no repetir lo obvio).

Notas clave:
    - Usa django-environ para cargar variables desde .env (flexibilidad por entorno).
    - Define estructura mínima para iniciar rápidamente desarrollo local.
    - Más adelante se puede partir en base/dev/prod si la complejidad aumenta.
"""

from pathlib import Path  # Path: manejo de rutas sin depender de separadores del SO
import environ            # django-environ: facilita lectura/casting de variables .env

# BASE_DIR: raíz del proyecto (donde vive manage.py). Permite referencias coherentes.
BASE_DIR = Path(__file__).resolve().parent.parent

############################
# Variables de entorno     #
############################
# Se declara el esquema (tipo esperado) para poder castear automáticamente.
env = environ.Env(
    DEBUG=(bool, True),  # DEBUG se castea a bool; por defecto True en desarrollo.
)
# Carga el archivo .env si existe (silencioso si falta, permitiendo defaults).
environ.Env.read_env(BASE_DIR / ".env")

############################
# Core / Seguridad         #
############################
SECRET_KEY = env("SECRET_KEY", default="dev-insecure-key-change-me")  # Reemplazar en prod
DEBUG = env.bool("DEBUG", default=True)  # Nunca True en producción
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])  # Lista de hosts permitidos


############################
# Aplicaciones instaladas  #
############################
# Se incluyen las apps propias para mantener modularidad en /apps.

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Apps del proyecto
    "apps.pages",
    "apps.algebra",
]

############################
# Middleware               #
############################
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",            # Protecciones básicas
    "django.contrib.sessions.middleware.SessionMiddleware",     # Manejo de sesiones
    "django.middleware.common.CommonMiddleware",                # Funciones comunes (headers, etc.)
    "django.middleware.csrf.CsrfViewMiddleware",                # Protección CSRF
    "django.contrib.auth.middleware.AuthenticationMiddleware",  # Autenticación de usuario
    "django.contrib.messages.middleware.MessageMiddleware",     # Sistema de mensajes flash
    "django.middleware.clickjacking.XFrameOptionsMiddleware",   # Mitiga clickjacking
]

ROOT_URLCONF = "config.urls"  # Archivo raíz de enrutamiento

############################
# Templates                #
############################
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # Directorio global (templates compartidos)
        "APP_DIRS": True,  # Busca templates dentro de cada app
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",  # Añade objeto request
                "django.contrib.auth.context_processors.auth", # Usuario autenticado
                "django.contrib.messages.context_processors.messages", # Mensajes flash
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"  # Punto de entrada WSGI (servidores tradicionales)


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

############################
# Base de Datos            #
############################
DATABASES = {
    "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
    # Para PostgreSQL: exportar DATABASE_URL=postgres://user:pass@host:5432/db
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

############################
# Validación de contraseñas#
############################
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},  # Evita similitud con atributos del usuario
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},           # Longitud mínima segura
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},         # Evita contraseñas comunes
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},        # Evita contraseñas solo numéricas
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

############################
# Internacionalización     #
############################
LANGUAGE_CODE = "es"  # Idioma por defecto (español)
TIME_ZONE = "UTC"     # Cambiar según región
USE_I18N = True       # I18N framework
USE_TZ = True         # Manejo de zonas horarias conscientes


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

############################
# Archivos estáticos       #
############################
STATIC_URL = "static/"                        # Prefijo en URLs
STATICFILES_DIRS = [BASE_DIR / "static"]      # Directorio para assets de desarrollo
STATIC_ROOT = BASE_DIR / "staticfiles"        # Directorio de colecta (collectstatic) para producción

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

############################
# Otros                    #
############################
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"  # Tipo de PK por defecto (auto incremental grande)
