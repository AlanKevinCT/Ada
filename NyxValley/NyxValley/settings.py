from pathlib import Path
from decouple import config

# ─── Rutas base ───────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ─── Seguridad ────────────────────────────────────────────────
# ADVERTENCIA: cambia esta clave antes de subir a producción
SECRET_KEY = config('SECRET_KEY')
DEBUG       = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = []


# ─── Correo electrónico ───────────────────────────────────────
EMAIL_BACKEND       = 'django.core.mail.backends.console.EmailBackend'  # cambiar a 'django.core.mail.backends.smtp.EmailBackend' al terminar el proyecto
EMAIL_HOST          = config('EMAIL_HOST')
EMAIL_PORT          = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS       = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER     = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL  = config('DEFAULT_FROM_EMAIL')

# ─── Aplicaciones instaladas ──────────────────────────────────
INSTALLED_APPS = [
    # Apps de Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #Para los forms
        'crispy_forms',
        'crispy_bootstrap5',

    # Nuestra app
    'Festival2026',
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ─── Middleware ───────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'NyxValley.urls'

# ─── Templates ────────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Carpeta global de templates en la raíz del proyecto
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'NyxValley.wsgi.application'

# ─── Base de datos ────────────────────────────────────────────
# SQLite para desarrollo — fácil, sin instalar nada extra
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ─── Validación de contraseñas ────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─── Internacionalización ─────────────────────────────────────
LANGUAGE_CODE = 'es-mx'          # Español de México
TIME_ZONE     = 'America/Mexico_City'
USE_I18N      = True
USE_TZ        = True

# ─── Archivos estáticos (CSS, JS, imágenes) ───────────────────
STATIC_URL  = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# ─── Archivos de medios subidos por usuarios ──────────────────
MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ─── Clave primaria por defecto ───────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── Sesiones ─────────────────────────────────────────────────
# La sesión expira tras 30 min de inactividad (RNF-08)
SESSION_COOKIE_AGE            = 1800   # segundos
SESSION_SAVE_EVERY_REQUEST    = True   # reinicia el contador con cada acción

# ─── Autenticación personalizada ──────────────────────────────
AUTH_USER_MODEL = 'Festival2026.Usuario'
LOGIN_URL          = '/login/'
LOGIN_REDIRECT_URL = '/'