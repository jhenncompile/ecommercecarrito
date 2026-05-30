#!/bin/bash
# ========================================================================
# SCRIPT DE PRODUCCIÓN - Deploy en VPS
# ========================================================================
# Uso:
#   sudo ./prod.sh tu_dominio.com tu_ip_vps
#   Ejemplo: sudo ./prod.sh empresa.com 45.33.44.55
#
# Este script:
# 1. Actualiza el sistema
# 3. Configura .env para producción
# 4. Levanta Django y React como servicios
# ========================================================================

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# ========================================================================
# VALIDAR ARGUMENTOS
# ========================================================================
if [ "$#" -ne 2 ]; then
    log_error "Uso: sudo ./prod.sh DOMINIO IP_VPS"
    log_error "Ejemplo: sudo ./prod.sh empresa.com 45.33.44.55"
    exit 1
fi

DOMAIN=$1
VPS_IP=$2

log_warn "⚠️  DEPLOYMENT A PRODUCCIÓN"
echo "Domain: $DOMAIN"
echo "VPS IP: $VPS_IP"
echo ""
read -p "¿Deseas continuar? (s/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    log_warn "Cancelado"
    exit 1
fi

# ========================================================================
# REQUISITOS: Ejecutar como root
# ========================================================================
if [ "$EUID" -ne 0 ]; then
    log_error "Este script debe ejecutarse como root (usa sudo)"
    exit 1
fi

# ========================================================================
# 1. ACTUALIZAR SISTEMA
# ========================================================================
log_info "Actualizando sistema..."
apt-get update -qq
apt-get upgrade -y -qq

log_success "Sistema actualizado"

# ========================================================================
# 2. INSTALAR DEPENDENCIAS
# ========================================================================
log_info "Instalando dependencias..."

# Python
if ! command -v python3 &> /dev/null; then
    apt-get install -y -qq python3 python3-pip python3-venv
fi

# Node.js
if ! command -v node &> /dev/null; then
    apt-get install -y -qq nodejs npm
fi

# PostgreSQL
if ! command -v psql &> /dev/null; then
    apt-get install -y -qq postgresql postgresql-contrib
    systemctl start postgresql
    systemctl enable postgresql
fi


# Supervisor (para mantener servicios corriendo)
if ! command -v supervisord &> /dev/null; then
    apt-get install -y -qq supervisor
    systemctl start supervisor
    systemctl enable supervisor
fi

log_success "Dependencias instaladas"

# ========================================================================
# 3. CLONAR/DESCARGAR PROYECTO (si no existe)
# ========================================================================
PROJECT_DIR="/var/www/ecommerce"

if [ ! -d "$PROJECT_DIR" ]; then
    log_info "Descargando proyecto..."
    # Aquí iría tu comando de clonación
    # git clone tu_repo $PROJECT_DIR
    log_warn "⚠️  Descarga manual requerida. Clona tu repositorio en: $PROJECT_DIR"
    exit 1
fi

cd $PROJECT_DIR

log_success "Proyecto en $PROJECT_DIR"

# ========================================================================
# 4. CREAR .env EN PRODUCCIÓN
# ========================================================================
log_info "Configurando .env para producción..."

cat > .env <<EOF
ENVIRONMENT=production
DOMAIN_MAIN=$DOMAIN
DOMAIN_ALLOWED_HOSTS=$DOMAIN,*.$DOMAIN

DJANGO_PORT=8001
REACT_PORT=3000

DJANGO_SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=False

CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://$DOMAIN,https://*.$DOMAIN

DATABASE_ENGINE=django_tenants.postgresql_backend
DATABASE_NAME=ecommerce_db
DATABASE_USER=postgres
DATABASE_PASSWORD=$(openssl rand -base64 32)
DATABASE_HOST=127.0.0.1
DATABASE_PORT=5432

JWT_EXPIRATION_MINUTES=1440

STATIC_ROOT=/var/www/ecommerce/static
STATIC_URL=/static/
MEDIA_ROOT=/var/www/ecommerce/media
MEDIA_URL=/media/
EOF

log_success ".env creado"

# ========================================================================
# 5. CONFIGURAR POSTGRESQL
# ========================================================================
log_info "Configurando PostgreSQL..."

sudo -u postgres psql <<EOF
CREATE DATABASE ecommerce_db;
CREATE USER postgres WITH PASSWORD '$(grep DATABASE_PASSWORD .env | cut -d= -f2)';
ALTER ROLE postgres SET client_encoding TO 'utf8';
ALTER ROLE postgres SET default_transaction_level TO 'read committed';
GRANT ALL PRIVILEGES ON DATABASE ecommerce_db TO postgres;
\q
EOF

log_success "PostgreSQL configurado"

# ========================================================================
# 6. CONFIGURAR BACKEND (Django)
# ========================================================================
log_info "Configurando Backend..."

cd backend

python3 -m venv venv
source venv/bin/activate

pip install -q -r requirements.txt

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

cd ..

log_success "Backend configurado"

# ========================================================================
# 7. CONFIGURAR FRONTEND (React)
# ========================================================================
log_info "Configurando Frontend..."

cd frontend
npm install
npm run build
cd ..

log_success "Frontend compilado"


# 10. CREAR SERVICIOS SYSTEMD
# ========================================================================
log_info "Creando servicios systemd..."

# Django
cat > /etc/systemd/system/ecommerce-django.service <<EOF
[Unit]
Description=E-Commerce Django Backend
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_DIR/backend
ExecStart=$PROJECT_DIR/backend/venv/bin/gunicorn \
    --workers 4 \
    --timeout 600 \
    --bind 0.0.0.0:8001 \
    config.wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# React (solo si necesitas compilar)
cat > /etc/systemd/system/ecommerce-react.service <<EOF
[Unit]
Description=E-Commerce React Frontend
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_DIR/frontend
ExecStart=$PROJECT_DIR/frontend/node_modules/.bin/serve -s build -l 3000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ecommerce-django.service
systemctl enable ecommerce-react.service
systemctl start ecommerce-django.service
systemctl start ecommerce-react.service

log_success "Servicios creados y iniciados"

# ========================================================================
# 11. CONFIGURAR FIREWALL
# ========================================================================
log_info "Configurando Firewall..."

if command -v ufw &> /dev/null; then
    ufw allow 22/tcp
    ufw allow 8001/tcp
    ufw allow 3000/tcp
    ufw --force enable
fi

log_success "Firewall configurado"

# ========================================================================
# FINALIZACIÓN
# ========================================================================
log_success "🎉 Deployment completado!"
echo ""
echo "tu_dominio: http://$DOMAIN:3000"
echo "Admin: http://$DOMAIN:8001/admin"
echo "API: http://$DOMAIN:8001/api"
echo ""
log_warn "Próximos pasos:"
echo "1. Verifica que Django y React están corriendo:"
echo "   systemctl status ecommerce-django"
echo "   systemctl status ecommerce-react"
echo ""
echo "2. Ver logs:"
echo "   journalctl -u ecommerce-django -f"
echo "   journalctl -u ecommerce-react -f"
echo ""
echo "3. Edita tenants en:"
echo "   https://$DOMAIN/admin/customers/domain/"
