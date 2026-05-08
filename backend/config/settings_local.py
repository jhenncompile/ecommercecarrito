import os
import socket
import re
from pathlib import Path
from decouple import config
from dotenv import load_dotenv

# Forzar encoding UTF-8 para evitar errores de decodificación en Windows con locales en español
os.environ['PGCLIENTENCODING'] = 'UTF-8'

# BASE_DIR es backend/, PROJECT_ROOT es el raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent

# ========================================================================
# CARGAR .ENV DESDE LA RAÍZ DEL PROYECTO
# ========================================================================
ENV_FILE = PROJECT_ROOT / '.env'
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
else:
    # Error fatal si no existe el .env central
    raise FileNotFoundError(f"Archivo .env no encontrado en la raíz: {ENV_FILE}")

# ========================================================================
# 1. DETECTAR ENTORNO
# ========================================================================
ENVIRONMENT = config('ENVIRONMENT', default='development')
DEBUG = config('DEBUG', default=True, cast=bool)

# ========================================================================
# 2. CONFIGURACIÓN DE DOMINIOS (MUY IMPORTANTE)
# ========================================================================
DOMAIN_MAIN = config('DOMAIN_MAIN', default='localhost')

# Sufijo para subdominios (ej: .localhost o .157.173.102.129.nip.io)
# IMPORTANTE: Debe empezar con un punto.
TENANT_DOMAIN_SUFFIX = config('TENANT_DOMAIN_SUFFIX', default='.localhost')

# Obtener hostname del dispositivo
DEVICE_HOSTNAME = socket.gethostname()

# Basado en el entorno, configurar ALLOWED_HOSTS
if ENVIRONMENT == 'development':
    # Leer hosts adicionales del .env
    additional_hosts = config(
        'DOMAIN_ALLOWED_HOSTS',
        default='',
        cast=lambda v: [s.strip() for s in v.split(',') if s.strip()]
    )
    
    # Construir lista de hosts permitidos
    ALLOWED_HOSTS = [
        '*',              # Permitir cualquier host en entorno de desarrollo
        'localhost',
        '127.0.0.1',
        DEVICE_HOSTNAME,  # Hostname del dispositivo (ej: DESKTOP-ABC123)
        '.localhost',     # ← Wildcard correcto para *.localhost
    ]
    # Agregar hosts adicionales del .env
    ALLOWED_HOSTS.extend(additional_hosts)
    
    # Agregar el sufijo a ALLOWED_HOSTS si no está
    if TENANT_DOMAIN_SUFFIX not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(TENANT_DOMAIN_SUFFIX)
    
    # En desarrollo permitimos todos los orígenes y subdominios
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOW_CREDENTIALS = True
    
    # Soportar específicamente subdominios dinámicos (Sin SSL)
    CORS_ALLOWED_ORIGIN_REGEXES = [
        r"^http://.*\.localhost(:\d+)?$",
        r"^http://localhost(:\d+)?$",
        r"^http://.*" + re.escape(TENANT_DOMAIN_SUFFIX) + r"(:\d+)?$",
    ]

    # Permitir cabeceras comunes y necesarias
    CORS_ALLOW_HEADERS = [
        "accept",
        "accept-encoding",
        "authorization",
        "content-type",
        "dnt",
        "origin",
        "user-agent",
        "x-csrftoken",
        "x-requested-with",
    ]
    
    # CSRF Trusted para desarrollo
    CSRF_TRUSTED_ORIGINS = [
        "http://localhost",
        "http://127.0.0.1",
        f"http://{DOMAIN_MAIN}",
        f"http://{DOMAIN_MAIN}:8001",
        f"http://*{TENANT_DOMAIN_SUFFIX}"
    ]
    
elif ENVIRONMENT == 'production':
    # MODO NUKE: Permitir todo temporalmente para estabilizar producción
    ALLOWED_HOSTS = ['*']
    
    # En producción usando HTTP (Sin SSL)
    CORS_ALLOW_ALL_ORIGINS = True # Apertura total para estabilizar
    CORS_ALLOW_CREDENTIALS = True
    
    # Blindaje dinámico para subdominios nip.io vía Regex
    CORS_ALLOWED_ORIGIN_REGEXES = [
        r"^http://.*" + re.escape(TENANT_DOMAIN_SUFFIX) + r"$",
        r"^http://" + re.escape(DOMAIN_MAIN) + r"$",
    ]

    # CSRF Trusted Origins (Obligatorio para POST en subdominios)
    CSRF_TRUSTED_ORIGINS = [
        f"http://{DOMAIN_MAIN}",
        f"http://{DEVICE_HOSTNAME}",
        "http://*.nip.io", # Permitir cualquier subdominio de nip.io para estabilizar
        f"http://*{TENANT_DOMAIN_SUFFIX}"
    ]
    # Agregar la IP directamente si está en DOMAIN_MAIN
    if DOMAIN_MAIN not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(f"http://{DOMAIN_MAIN}")

# ========================================================================
# 3. SECRET KEY (CAMBIAR EN PRODUCCIÓN)
# ========================================================================
SECRET_KEY = config(
    'DJANGO_SECRET_KEY',
    default='django-insecure-8dl7kzt3gurd5j=)2(7=6kkf-vfp(5qq=46*8(w)g_)9q8*t^*'
)

# ========================================================================
# 4. BASE DE DATOS
# ========================================================================
DATABASES = {
    'default': {
        'ENGINE': config('DATABASE_ENGINE', default='django_tenants.postgresql_backend'),
        'NAME': config('DATABASE_NAME', default='mi_saas_db'),
        'USER': config('DATABASE_USER', default='postgres'),
        'PASSWORD': config('DATABASE_PASSWORD', default='123456789'),
        'HOST': config('DATABASE_HOST', default='127.0.0.1'),
        'PORT': config('DATABASE_PORT', default='5432'),
    }
}

# ========================================================================
# 5. JWT TOKENS
# ========================================================================
JWT_ALGORITHM = config('JWT_ALGORITHM', default='HS256')
JWT_EXPIRATION_MINUTES = config('JWT_EXPIRATION_MINUTES', default=60, cast=int)

# ========================================================================
# 6. CONFIGURACIÓN DE CORREO
# ========================================================================
EMAIL_HOST_USER     = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Configuración del backend de correo (Gmail con TLS)
EMAIL_BACKEND   = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST      = 'smtp.gmail.com'
EMAIL_PORT      = 587
EMAIL_USE_TLS   = True
EMAIL_USE_SSL   = False
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ========================================================================
# 7. ARCHIVOS ESTÁTICOS Y MEDIA
# ========================================================================
STATIC_URL = config('STATIC_URL', default='/static/')
STATIC_ROOT = config('STATIC_ROOT', default=os.path.join(BASE_DIR, 'staticfiles'))

MEDIA_URL = config('MEDIA_URL', default='/media/')
MEDIA_ROOT = config('MEDIA_ROOT', default=os.path.join(BASE_DIR, 'media'))

# ========================================================================
# 7. SECURITY EN PRODUCCIÓN
# ========================================================================
if ENVIRONMENT == 'production':
    # Desactivamos redirección SSL porque el entorno es HTTP plano (Puerto 80)
    SECURE_SSL_REDIRECT = False
    SECURE_HSTS_SECONDS = 0  # Desactivado para evitar bloqueos de navegador
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SESSION_COOKIE_SECURE = False  # Permitir cookies en HTTP plano
    CSRF_COOKIE_SECURE = False     # Permitir tokens CSRF en HTTP plano
else:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
