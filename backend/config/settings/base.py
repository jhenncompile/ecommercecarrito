"""
config/settings/base.py
ConfiguraciÃ³n base compartida por todos los entornos.
Todas las settings de settings.py que NO son especÃ­ficas de entorno van aquÃ­.
"""
import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # backend/

# â”€â”€ USUARIO GLOBAL ÃšNICO â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
AUTH_USER_MODEL = 'customers.Usuario'

# â”€â”€ APPS MULTI-TENANT â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
SHARED_APPS = (
    'django_tenants',
    'apps.customers',
    'apps.gestionDeUsuarioySeguridad',
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
    'apps.gestionDeReportes.cu21_generar_backup.apps.Cu21Config',
)

TENANT_APPS = (
    'django.contrib.contenttypes',
    'apps.gestionDeProductoYCatalogo.cu7_gestionar_productos',
    'apps.gestionDeProductoYCatalogo.cu8_visualizar_listado_de_productos',
    'apps.gestionDeProductoYCatalogo.cu9_gestionar_categorias',
    'apps.gestionDeProductoYCatalogo.cu10_gestionar_inventario',
    'apps.gestionDeProductoYCatalogo.cu23_gestionar_filtro_de_producto',
    'apps.gestionDeVentasYFacturacion.cu11_gestion_carrito_de_compras',
    'apps.gestionDeVentasYFacturacion.cu12_gestionar_metodos_de_pago',
    'apps.gestionDeVentasYFacturacion.cu13_gestionar_estado_de_pedido',
    'apps.gestionDeVentasYFacturacion.cu14_generar_facturacion',
    'apps.gestionDeVentasYFacturacion.cu15_ver_historial_de_compras',
    'apps.gestionDeVentasYFacturacion.cu24_gestionar_logistica',
    'apps.gestionDeClientes.cu16_recomendar_productos',
    'apps.gestionDeClientes.cu17_analizar_comportamiento_del_cliente',
    'apps.gestionDeClientes.cu22_gestionar_prediccion_de_ventas',
    'apps.gestionDeClientes.cu25_gestionar_solicitud_de_restock',
    'apps.gestionDeClientes.cu26_gestionar_resenas',
    'apps.gestionDeReportes.cu18_gestionar_notificaciones.apps.Cu18Config',
    'apps.gestionDeReportes.cu19_generar_reportes_de_ventas.apps.Cu19Config',
    'apps.gestionDeReportes.cu20_gestionar_recordatorios.apps.Cu20Config',
    'apps.voice',
)

INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]

# â”€â”€ MIDDLEWARES â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
MIDDLEWARE = [
    'apps.gestionDeUsuarioySeguridad.cu3_gestion_de_usuario.middleware.TenantHostMiddleware',
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

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = 'config.tenant_urls'
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

# â”€â”€ BASE DE DATOS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
DATABASE_ROUTERS = ('django_tenants.routers.TenantSyncRouter',)

# â”€â”€ MODELOS DE TENANTS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
TENANT_MODEL = 'customers.Client'
TENANT_DOMAIN_MODEL = 'customers.Domain'
SHOW_PUBLIC_IF_NO_TENANT_FOUND = True

# â”€â”€ VALIDACIONES E INTERNACIONALIZACIÃ“N â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# â”€â”€ CORS Y REST FRAMEWORK â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'apps.gestionDeUsuarioySeguridad.cu1_iniciar_sesion.authentication.UsuarioJWTAuthentication',
        'apps.gestionDeUsuarioySeguridad.cu1_iniciar_sesion.authentication.ClienteJWTAuthentication',
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

# â”€â”€ STRIPE â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='')
STRIPE_PUBLISHABLE_KEY = config('STRIPE_PUBLISHABLE_KEY', default='')
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', default='')

if not STRIPE_SECRET_KEY:
    print("âš ï¸  ADVERTENCIA: STRIPE_SECRET_KEY no detectada en el entorno.")

# â”€â”€ AUDITORÃA â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
AUDIT_LOG_RETENTION_DAYS = 90

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}




