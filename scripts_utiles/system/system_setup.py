#!/usr/bin/env python3
# ========================================================================
# ASISTENTE DE INSTALACIÓN RÁPIDA (Plug & Play)
# ========================================================================
# Configura el entorno completo del proyecto de forma interactiva.
# Te pregunta el modo de despliegue (Nginx o IP directa) y ajusta
# automáticamente todas las variables del .env relevantes.
#
# Lo que NO toca (configuración manual):
#   - DATABASE_* (usuario, contraseña, host, nombre)
#   - EMAIL_HOST_USER / EMAIL_HOST_PASSWORD
#
# Uso: python scripts_utiles/system_setup.py
# ========================================================================

import os
import sys
import subprocess
import secrets
import platform
import socket
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR  = PROJECT_ROOT / 'backend'
FRONTEND_DIR = PROJECT_ROOT / 'frontend'
ENV_PATH     = PROJECT_ROOT / '.env'

ES_WINDOWS = platform.system() == 'Windows'

# â”€â”€ Colores â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
class C:
    GREEN   = '\033[92m'
    CYAN    = '\033[96m'
    YELLOW  = '\033[93m'
    RED     = '\033[91m'
    BLUE    = '\033[94m'
    BOLD    = '\033[1m'
    RESET   = '\033[0m'

def ok(t):    print(f"{C.GREEN}[OK]{C.RESET}  {t}")
def err(t):   print(f"{C.RED}[X]{C.RESET}   {t}")
def info(t):  print(f"{C.BLUE}[i]{C.RESET}   {t}")
def warn(t):  print(f"{C.YELLOW}[!]{C.RESET}  {t}")
def step(n, t): print(f"\n{C.CYAN}{C.BOLD}â”€â”€ Paso {n}: {t}{C.RESET}")

def header(t):
    print(f"\n{C.BOLD}{C.GREEN}{'='*62}{C.RESET}")
    print(f"{C.BOLD}{C.GREEN}  {t}{C.RESET}")
    print(f"{C.BOLD}{C.GREEN}{'='*62}{C.RESET}\n")

# â”€â”€ Helpers .env â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def load_env():
    """Carga el .env actual como diccionario {clave: (valor, linea_completa)}."""
    result = {}
    if ENV_PATH.exists():
        with open(ENV_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith('#') or '=' not in stripped:
                    continue
                key, value = stripped.split('=', 1)
                result[key.strip()] = value.strip().strip("'\"")
    return result


def write_env_key(key, value):
    """Actualiza o añade una clave en el .env. Respeta comentarios y estructura."""
    lines = []
    found = False
    if ENV_PATH.exists():
        with open(ENV_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith(f'{key}='):
                    lines.append(f'{key}={value}\n')
                    found = True
                else:
                    lines.append(line)
    if not found:
        lines.append(f'{key}={value}\n')
    with open(ENV_PATH, 'w', encoding='utf-8') as f:
        f.writelines(lines)


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

# â”€â”€ PASO 0: Modo de despliegue â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def ask_deployment_mode():
    """
    Pregunta al usuario el modo de despliegue.
    Retorna (modo, ip, django_port, react_port)
    """
    print(f"\n{C.BOLD}Â¿Cómo quieres desplegar el proyecto?{C.RESET}")
    print(f"  {C.GREEN}1{C.RESET} - Nginx (Producción) â€” gunicorn + build estático + Nginx")
    print(f"  {C.CYAN}2{C.RESET} - IP directa         â€” Django runserver/gunicorn + React start")
    print(f"  {C.BLUE}3{C.RESET} - Localhost           â€” Solo esta PC, desarrollo puro")
    print()

    while True:
        choice = input(f"  {C.BOLD}? [1/2/3]: {C.RESET}").strip()
        if choice in ('1', '2', '3'):
            break
        print("  Opción inválida, elige 1, 2 o 3.")

    env = load_env()
    django_port = env.get('DJANGO_PORT', '8001')
    react_port  = env.get('REACT_PORT',  '3000')

    if choice == '1':
        # â”€â”€ Nginx â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        detected = get_local_ip()
        info(f"IP detectada: {C.YELLOW}{detected}{C.RESET}")
        manual = input(f"  IP o dominio del VPS ({detected}): ").strip()
        ip = manual if manual else detected

        return 'nginx', ip, django_port, react_port

    elif choice == '2':
        # â”€â”€ IP directa â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        detected = get_local_ip()
        info(f"IP detectada: {C.YELLOW}{detected}{C.RESET}")
        manual = input(f"  Confirma o escribe otra IP ({detected}): ").strip()
        ip = manual if manual else detected

        return 'ip', ip, django_port, react_port

    else:
        # â”€â”€ Localhost â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        return 'localhost', 'localhost', django_port, react_port


def configure_env(modo, ip, django_port, react_port):
    """Actualiza el .env con la configuración del modo elegido."""
    step('0', 'Configurando variables de entorno (.env)')

    if not ENV_PATH.exists():
        warn(".env no existe. Creando desde plantilla mínima...")
        _create_minimal_env()

    if modo == 'nginx':
        write_env_key('ENVIRONMENT',                   'production')
        write_env_key('DEBUG',                         'False')
        write_env_key('DOMAIN_MAIN',                   ip)
        write_env_key('TENANT_DOMAIN_SUFFIX',          f'.{ip}.nip.io')
        write_env_key('REACT_APP_BASE_DOMAIN',         ip)
        write_env_key('REACT_APP_TENANT_DOMAIN_SUFFIX', f'.{ip}.nip.io')
        write_env_key('REACT_APP_API_URL',             '/api')           # Nginx hace el proxy
        ok(f"Modo Nginx â€” dominio base: {ip}")
        ok(f"Sufijo tenants: .{ip}.nip.io")

    elif modo == 'ip':
        write_env_key('ENVIRONMENT',                   'development')
        write_env_key('DEBUG',                         'True')
        write_env_key('DOMAIN_MAIN',                   ip)
        write_env_key('TENANT_DOMAIN_SUFFIX',          f'.{ip}.nip.io')
        write_env_key('REACT_APP_BASE_DOMAIN',         ip)
        write_env_key('REACT_APP_TENANT_DOMAIN_SUFFIX', f'.{ip}.nip.io')
        write_env_key('REACT_APP_API_URL',             f'http://{ip}:{django_port}/api')
        ok(f"Modo IP directa â€” acceso en http://{ip}:{react_port}")
        ok(f"Backend API en http://{ip}:{django_port}/api")

    else:  # localhost
        write_env_key('ENVIRONMENT',                   'development')
        write_env_key('DEBUG',                         'True')
        write_env_key('DOMAIN_MAIN',                   'localhost')
        write_env_key('TENANT_DOMAIN_SUFFIX',          '.localhost')
        write_env_key('REACT_APP_BASE_DOMAIN',         'localhost')
        write_env_key('REACT_APP_TENANT_DOMAIN_SUFFIX', '.localhost')
        write_env_key('REACT_APP_API_URL',             f'http://localhost:{django_port}/api')
        ok("Modo Localhost configurado")


def _create_minimal_env():
    """Crea un .env mínimo de arranque si no existe."""
    sk = secrets.token_urlsafe(50)
    content = f"""ENVIRONMENT=development
DEBUG=True
DJANGO_SECRET_KEY={sk}
DJANGO_PORT=8001
REACT_PORT=3000
NGINX_PORT=80
DOMAIN_MAIN=localhost
TENANT_DOMAIN_SUFFIX=.localhost
REACT_APP_BASE_DOMAIN=localhost
REACT_APP_API_URL=http://localhost:8001/api
DATABASE_ENGINE=django_tenants.postgresql_backend
DATABASE_NAME=mi_saas_db
DATABASE_USER=postgres
DATABASE_PASSWORD=
DATABASE_HOST=127.0.0.1
DATABASE_PORT=5432
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
TENANT_MODEL=customers.Client
TENANT_DOMAIN_MODEL=customers.Domain
LOG_LEVEL=INFO
"""
    with open(ENV_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    ok(".env creado")

# â”€â”€ PASO 0b: Credenciales â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def ask_credentials(ip):
    """
    Pregunta las credenciales de email y base de datos.
    Si el usuario no ingresa nada, se usan los defaults.
    """
    step('0b', 'Configuración de credenciales (Enter = dejar como está / usar default)')

    env = load_env()

    print(f"\n  {C.BOLD}â”€â”€ Correo (Gmail){C.RESET}")
    current_email = env.get('EMAIL_HOST_USER', '')
    hint = f"actual: {current_email}" if current_email else "ej: tu@gmail.com"
    email_val = input(f"  Email [{hint}]: ").strip()
    if email_val:
        write_env_key('EMAIL_HOST_USER', email_val)
        ok(f"Email configurado: {email_val}")
    elif current_email:
        ok(f"Email sin cambios: {current_email}")
    else:
        warn("Email no configurado (recuperar contraseña no funcionará)")

    current_pass = env.get('EMAIL_HOST_PASSWORD', '')
    hint_pass = "configurada" if current_pass else "sin configurar"
    app_pass = input(f"  App Password de Gmail [{hint_pass}]: ").strip()
    if app_pass:
        write_env_key('EMAIL_HOST_PASSWORD', app_pass)
        ok("App Password guardada")
    elif current_pass:
        ok("App Password sin cambios")
    else:
        warn("App Password no configurada")

    print(f"\n  {C.BOLD}â”€â”€ Base de Datos (PostgreSQL){C.RESET}")

    # Nombre de la BD
    current_db = env.get('DATABASE_NAME', 'mi_saas_db')
    db_name = input(f"  Nombre de BD [{current_db}]: ").strip()
    db_name = db_name if db_name else current_db
    write_env_key('DATABASE_NAME', db_name)
    ok(f"BD: {db_name}")

    # Host = misma IP del despliegue (solo confirmar)
    current_host = env.get('DATABASE_HOST', ip)
    db_host = input(f"  Host de BD [{current_host}]: ").strip()
    db_host = db_host if db_host else current_host
    write_env_key('DATABASE_HOST', db_host)
    ok(f"Host BD: {db_host}")

    # Puerto â€” siempre 5432 por default
    write_env_key('DATABASE_PORT', '5432')
    ok("Puerto BD: 5432 (default)")

    # Usuario
    current_user = env.get('DATABASE_USER', 'postgres')
    db_user = input(f"  Usuario de BD [{current_user}]: ").strip()
    db_user = db_user if db_user else current_user
    write_env_key('DATABASE_USER', db_user)
    ok(f"Usuario BD: {db_user}")

    # Contraseña
    current_pw = env.get('DATABASE_PASSWORD', '')
    hint_pw = "configurada" if current_pw else "vacía (postgres sin contraseña)"
    db_pw = input(f"  Contraseña de BD [{hint_pw}]: ").strip()
    if db_pw:
        write_env_key('DATABASE_PASSWORD', db_pw)
        ok("Contraseña BD guardada")
    elif current_pw:
        ok("Contraseña BD sin cambios")
    else:
        warn("Contraseña BD vacía â€” asegúrate de que postgres lo permita")


# â”€â”€ PASO 1: Backend â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def setup_backend():
    step('1', 'Configurando Backend (Django + venv)')

    venv_path  = BACKEND_DIR / 'venv'
    python_exe = venv_path / ('Scripts/python.exe' if ES_WINDOWS else 'bin/python')
    pip_exe    = venv_path / ('Scripts/pip.exe'    if ES_WINDOWS else 'bin/pip')

    if not venv_path.exists():
        info("Creando entorno virtual...")
        subprocess.run([sys.executable, '-m', 'venv', str(venv_path)], check=True)
        ok("Entorno virtual creado")
    else:
        ok("Entorno virtual ya existe")

    req = BACKEND_DIR / 'requirements.txt'
    if req.exists():
        info("Instalando dependencias Python...")
        try:
            subprocess.run([str(pip_exe), 'install', '-r', str(req)],
                           cwd=str(BACKEND_DIR), check=True)
            ok("Dependencias backend instaladas")
        except subprocess.CalledProcessError:
            err("Error instalando dependencias del backend")
    else:
        warn("requirements.txt no encontrado â€” omitiendo pip install")

# â”€â”€ PASO 2: Frontend â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def setup_frontend(modo):
    step('2', 'Configurando Frontend (React / Node)')

    npm = shutil.which('npm') or ('npm.cmd' if ES_WINDOWS else 'npm')

    if not FRONTEND_DIR.exists():
        err(f"Directorio frontend no encontrado: {FRONTEND_DIR}")
        return

    node_modules = FRONTEND_DIR / 'node_modules'
    if node_modules.exists():
        warn("node_modules ya existe â€” usando existente (usa Mantenimiento â†’ Limpieza si tienes problemas)")
    else:
        info("Ejecutando npm install...")
        try:
            subprocess.run([npm, 'install'], cwd=str(FRONTEND_DIR),
                           check=True, shell=ES_WINDOWS)
            ok("Dependencias del frontend instaladas")
        except subprocess.CalledProcessError:
            err("Error en npm install")
            return

    if modo == 'nginx':
        info("Generando build de producción (npm run build)...")
        try:
            subprocess.run([npm, 'run', 'build'], cwd=str(FRONTEND_DIR),
                           check=True, shell=ES_WINDOWS)
            ok("Build completado")
        except subprocess.CalledProcessError:
            err("Error en npm run build")

# â”€â”€ PASO 3: Migraciones y base de datos â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def run_migrations():
    step('3', 'Base de Datos: Reset + Migraciones')

    venv_path  = BACKEND_DIR / 'venv'
    python_exe = str(venv_path / ('Scripts/python.exe' if ES_WINDOWS else 'bin/python'))

    if not Path(python_exe).exists():
        err("Python del venv no encontrado â€” omitiendo migraciones")
        return

    env = load_env()
    db_name = env.get('DATABASE_NAME', 'mi_saas_db')
    db_user = env.get('DATABASE_USER', 'postgres')
    db_host = env.get('DATABASE_HOST', '127.0.0.1')
    db_port = env.get('DATABASE_PORT', '5432')
    db_pass = env.get('DATABASE_PASSWORD', '')

    # Entorno con password para psql
    pg_env = os.environ.copy()
    if db_pass:
        pg_env['PGPASSWORD'] = db_pass

    psql = shutil.which('psql') or 'psql'

    # â”€â”€ 3a. Drop + Create BD â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    warn(f"Se eliminará y recreará la BD '{db_name}' en {db_host}. Todos los datos se perderán.")
    confirm = input(f"  {C.BOLD}Â¿Continuar? (s/n): {C.RESET}").strip().lower()
    if confirm != 's':
        warn("Reset de BD cancelado. Saltando a migraciones sin reset.")
    else:
        try:
            info("Eliminando BD existente...")
            subprocess.run(
                [psql, '-h', db_host, '-p', db_port, '-U', db_user,
                 '-c', f'DROP DATABASE IF EXISTS "{db_name}";', 'postgres'],
                env=pg_env, check=True
            )
            info("Creando BD nueva...")
            subprocess.run(
                [psql, '-h', db_host, '-p', db_port, '-U', db_user,
                 '-c', f'CREATE DATABASE "{db_name}";', 'postgres'],
                env=pg_env, check=True
            )
            ok(f"BD '{db_name}' recreada")
        except Exception as e:
            warn(f"Error con psql ({e}). Intentando continuar con migraciones de todas formas...")

    # â”€â”€ 3b. makemigrations â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    try:
        info("Generando migraciones (makemigrations)...")
        subprocess.run([python_exe, 'manage.py', 'makemigrations'],
                       cwd=str(BACKEND_DIR), check=True)
        ok("makemigrations completado")
    except subprocess.CalledProcessError as e:
        err(f"makemigrations falló: {e}")
        return

    # â”€â”€ 3c. migrate (shared = public schema) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    try:
        info("Aplicando migraciones al schema público (migrate_schemas --shared)...")
        subprocess.run(
            [python_exe, 'manage.py', 'migrate_schemas', '--shared'],
            cwd=str(BACKEND_DIR), check=True
        )
        ok("Migraciones aplicadas al schema público")
    except subprocess.CalledProcessError:
        # Fallback: migrate estándar
        warn("migrate_schemas no disponible, usando migrate estándar...")
        try:
            subprocess.run([python_exe, 'manage.py', 'migrate'],
                           cwd=str(BACKEND_DIR), check=True)
            ok("migrate completado")
        except subprocess.CalledProcessError as e:
            err(f"migrate falló: {e}")
            return

    # â”€â”€ 3d. Seeders opcionales â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    seed = input(f"\n  {C.BOLD}Â¿Quieres poblar la BD con datos de prueba? (seeders) (s/n): {C.RESET}").strip().lower()
    if seed == 's':
        seed_script = BACKEND_DIR.parent / 'scripts_utiles' / 'db_seed.py'
        if not seed_script.exists():
            seed_script = Path(__file__).parent / 'db_seed.py'
        if seed_script.exists():
            try:
                subprocess.run([python_exe, str(seed_script)],
                               cwd=str(BACKEND_DIR), check=True)
                ok("Seeders ejecutados correctamente")
            except subprocess.CalledProcessError as e:
                err(f"Error en seeders: {e}")
        else:
            err("db_seed.py no encontrado")
    else:
        warn("Seeders omitidos")

# â”€â”€ Main â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def run_setup():
    header("ASISTENTE DE INSTALACIÓN RÁPIDA")

    print(f"{C.YELLOW}Este asistente configura automáticamente:{C.RESET}")
    print("  âœ“ Variables de entorno (.env) según el modo elegido")
    print("  âœ“ Entorno virtual Python (venv) + dependencias")
    print("  âœ“ Dependencias Node.js")
    print("  âœ“ Migraciones de base de datos")
    print()
    print(f"{C.YELLOW}Lo que debes configurar MANUALMENTE en .env:{C.RESET}")
    print("  â€¢ DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_NAME")
    print("  â€¢ EMAIL_HOST_USER, EMAIL_HOST_PASSWORD")
    print()

    if input(f"  {C.BOLD}Â¿Continuar? (s/n): {C.RESET}").strip().lower() != 's':
        print("Cancelado.")
        return

    # Paso 0: elegir modo
    modo, ip, django_port, react_port = ask_deployment_mode()
    configure_env(modo, ip, django_port, react_port)

    # Paso 0b: credenciales
    ask_credentials(ip)

    # Paso 1: backend
    setup_backend()

    # Paso 2: frontend
    setup_frontend(modo)

    # Paso 3: migraciones
    run_mig = input(f"\n  {C.BOLD}Â¿Aplicar migraciones ahora? (requiere BD activa) (s/n): {C.RESET}").strip().lower()
    if run_mig == 's':
        run_migrations()
    else:
        warn("Migraciones omitidas. Puedes correrlas luego desde el menú â†’ Gestión BD")

    # Resumen
    header("INSTALACIÓN COMPLETADA")
    print(f"  Modo:    {C.BOLD}{modo.upper()}{C.RESET}")
    if modo != 'localhost':
        print(f"  IP/Host: {C.YELLOW}{ip}{C.RESET}")
    print()
    print(f"{C.BOLD}Próximos pasos:{C.RESET}")
    if modo == 'nginx':
        print("  1. Configura DATABASE_* y EMAIL_* en .env")
        print("  2. Ve al menú â†’ Servicios â†’ Con Nginx para crear los servicios systemd")
    elif modo == 'ip':
        print("  1. Configura DATABASE_* y EMAIL_* en .env")
        print(f"  2. Desde el menú â†’ Opción 1 para Backend | Opción 2 para Frontend")
        print(f"  3. Accede en http://{ip}:{react_port}")
    else:
        print("  1. Ve al menú â†’ Opción 3 para iniciar todo")
        print(f"  2. Accede en http://localhost:{react_port}")
    print()


if __name__ == '__main__':
    run_setup()

