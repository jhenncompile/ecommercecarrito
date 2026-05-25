import os
from pathlib import Path
from decouple import config
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# CARGAR .ENV DESDE LA RAÃZ DEL PROYECTO
load_dotenv(os.path.join(BASE_DIR.parent, '.env'))

# ========================================================================
# CARGAR CONFIGURACIÃ“N LOCAL (desarrollo/producciÃ³n)
# ========================================================================
# 1. ENTORNO Y CONFIGURACIÃ“N BÃSICA
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. USUARIO GLOBAL ÃšNICO
AUTH_USER_MODEL = 'customers.Usuario'

# 3. APPS MULTI-TENANT
SHARED_APPS = (
    'django_tenants',
    'apps.customers',
    'rest_framework',
    'drf_spectacular',
    'corsheaders',
    'django_filters',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework_simplejwt.token_blacklist',
)

TENANT_APPS = (
    'django.contrib.contenttypes',
    'apps.negocio',
    'apps.voice',
)

INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]

# 4. MIDDLEWARES
MIDDLEWARE = [
    'apps.customers.users.middleware.TenantHostMiddleware',           
    'corsheaders.middleware.CorsMiddleware',                
    'django_tenants.middleware.main.TenantMainMiddleware',  
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Compatibilidad total con Nginx y Proxies
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = 'config.urls'
PUBLIC_SCHEMA_URLCONF = 'config.urls'
TENANT_URLCONF = 'config.tenant_urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'

# 6. BASE DE DATOS
# (DATABASES se configurarÃ¡ en settings_local.py)
DATABASE_ROUTERS = ('django_tenants.routers.TenantSyncRouter',)

# 7. MODELOS DE TENANTS
TENANT_MODEL = 'customers.Client'
TENANT_DOMAIN_MODEL = 'customers.Domain'
SHOW_PUBLIC_IF_NO_TENANT_FOUND = True

# 8. VALIDACIONES E INTERNACIONALIZACIÃ“N
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
LANGUAGE_CODE = 'es-bo'
TIME_ZONE = 'America/La_Paz'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR.parent, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR.parent, 'media')

# 10. CONFIGURACIÃ“N DE CAMPOS AUTO (Silencia warnings)
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 9. CORS Y API (REST FRAMEWORK & JWT)
CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'apps.customers.users.authentication.UsuarioJWTAuthentication',
        'apps.customers.users.authentication.ClienteJWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 12,
}

SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('Bearer',),
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Ecommerce API',
    'DESCRIPTION': 'Sistema Multi-tenant de Ecommerce con CRUDs completos',
    'VERSION': '1.0.0',
    'SERVE_PERMISSIONS': ['rest_framework.permissions.AllowAny'],
    'SERVE_INCLUDE_SCHEMA': True,
}

# 11. STRIPE CONFIGURATION
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='')
STRIPE_PUBLISHABLE_KEY = config('STRIPE_PUBLISHABLE_KEY', default='')
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', default='')

if not STRIPE_SECRET_KEY:
    print("âš ï¸ ADVERTENCIA: STRIPE_SECRET_KEY no detectada en el entorno.")

# ========================================================================
# CARGAR CONFIGURACIÃ“N LOCAL (desarrollo/producciÃ³n) Y .ENV
# ========================================================================
try:
    from .settings_local import *
except ImportError:
    # Si no existe settings_local, usar valores por defecto mÃ­nimos
    SECRET_KEY = config('DJANGO_SECRET_KEY', default='django-insecure-8dl7kzt3gurd5j=)2(7=6kkf-vfp(5qq=46*8(w)g_)9q8*t^*')
    DEBUG = config('DEBUG', default=True, cast=bool)
    ALLOWED_HOSTS = ['*']

# 12. AUDITORÃA
AUDIT_LOG_RETENTION_DAYS = 90




# FIREBASE CONFIG
FIREBASE_CREDENTIALS_PATH = config("FIREBASE_CREDENTIALS_PATH", default=os.path.join(BASE_DIR, "firebase-adminsdk.json"))

