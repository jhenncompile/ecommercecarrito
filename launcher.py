#!/usr/bin/env python3
# ========================================================================
# LANZADOR UNIVERSAL - WINDOWS / LINUX / MAC
# ========================================================================
# Menu interactivo multiplataforma.
# Toda la lógica de negocio vive en scripts_utiles/*.py
# Este archivo es SOLO navegación de menú.
#
# Uso: python launcher.py
# ========================================================================

import os
import sys
import subprocess
import time
import platform
import shutil
from pathlib import Path

# ── SO ───────────────────────────────────────────────────────────────────
SISTEMA_OPERATIVO = platform.system()
ES_WINDOWS = SISTEMA_OPERATIVO == 'Windows'
ES_LINUX   = SISTEMA_OPERATIVO == 'Linux'
ES_MAC     = SISTEMA_OPERATIVO == 'Darwin'

# ── Rutas ─────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent
BACKEND_DIR  = PROJECT_ROOT / 'backend'
FRONTEND_DIR = PROJECT_ROOT / 'frontend'
SCRIPTS_DIR  = PROJECT_ROOT / 'scripts_utiles'

# ── Colores ANSI ──────────────────────────────────────────────────────────
class Colors:
    RED     = '\033[91m'
    GREEN   = '\033[92m'
    YELLOW  = '\033[93m'
    BLUE    = '\033[94m'
    CYAN    = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE   = '\033[97m'
    GRAY    = '\033[90m'
    BOLD    = '\033[1m'
    RESET   = '\033[0m'
    CHECK   = '[OK]'
    CROSS   = '[X]'
    INFO    = '[i]'
    WARN    = '[!]'

# ── Cargar .env ───────────────────────────────────────────────────────────
def load_env_manual():
    env_vars = {}
    env_path = PROJECT_ROOT / '.env'
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip().strip("'\"")
    return env_vars

ENV_CONFIG   = load_env_manual()
DJANGO_PORT  = ENV_CONFIG.get('DJANGO_PORT', '8001')
REACT_PORT   = ENV_CONFIG.get('REACT_PORT',  '3000')

# ── Presentación ──────────────────────────────────────────────────────────
def clear_screen():
    os.system('cls' if ES_WINDOWS else 'clear')

def print_header(text):
    print()
    print(f"{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD} {text}{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*70}{Colors.RESET}\n")

def print_section(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")

def print_option(text):
    print(f"  {text}")

def print_success(text):
    print(f"{Colors.GREEN}{Colors.CHECK}{Colors.RESET} {text}")

def print_error(text):
    print(f"{Colors.RED}{Colors.CROSS}{Colors.RESET} {text}")

def print_info(text):
    print(f"{Colors.BLUE}{Colors.INFO}{Colors.RESET} {text}")

def print_warning(text):
    print(f"{Colors.YELLOW}{Colors.WARN}{Colors.RESET} {text}")

def loading_animation(duration=2, text="Cargando"):
    spinner = ['|', '/', '-', '\\']
    end_time = time.time() + duration
    idx = 0
    while time.time() < end_time:
        print(f"\r{Colors.CYAN}{spinner[idx % len(spinner)]}{Colors.RESET} {text}...",
              end='', flush=True)
        idx += 1
        time.sleep(0.1)
    print(f"\r{Colors.GREEN}{Colors.CHECK}{Colors.RESET} {text}... Listo    ")

def pause():
    input(f"\n{Colors.BOLD}Presiona ENTER para continuar...{Colors.RESET}")

# ── Ejecutor de scripts ───────────────────────────────────────────────────
def run_script(script_name, *args, use_venv=True):
    """Ejecuta un script en scripts_utiles/ con el Python del venv."""
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        print_error(f"Script no encontrado: {script_path}")
        return

    python_exe = sys.executable
    if use_venv:
        venv_py = (BACKEND_DIR / 'venv' / 'Scripts' / 'python.exe' if ES_WINDOWS
                   else BACKEND_DIR / 'venv' / 'bin' / 'python')
        if venv_py.exists():
            python_exe = str(venv_py)
        else:
            print_warning("Venv no encontrado, usando Python del sistema...")

    old_cwd = os.getcwd()
    os.chdir(BACKEND_DIR)

    env = os.environ.copy()
    bp = str(BACKEND_DIR)
    sep = ';' if ES_WINDOWS else ':'
    env['PYTHONPATH'] = f"{bp}{sep}{env.get('PYTHONPATH', '')}"

    try:
        subprocess.run([python_exe, str(script_path)] + list(args), env=env)
    except KeyboardInterrupt:
        print_warning("\nProceso cancelado.")
    except Exception as e:
        print_error(f"Error: {e}")
    finally:
        os.chdir(old_cwd)

# ── Menú Principal ────────────────────────────────────────────────────────
def show_main_menu():
    while True:
        clear_screen()
        print_header("LANZADOR DE PROYECTO")
        print_section(f"Sistema Operativo: {SISTEMA_OPERATIVO}")

        print_section("EJECUCIÓN")
        print_option(f"{Colors.GREEN}1{Colors.RESET} - Iniciar Backend (Django)")
        print_option(f"{Colors.GREEN}2{Colors.RESET} - Iniciar Frontend (React)")
        print_option(f"{Colors.BOLD}{Colors.GREEN}3{Colors.RESET} - {Colors.BOLD}INICIAR TODO (Backend + Frontend){Colors.RESET}")
        print_option(f"{Colors.BOLD}{Colors.YELLOW}M{Colors.RESET} - {Colors.BOLD}SINCRONIZAR BASE DE DATOS (Migrations){Colors.RESET}")

        print_section("DATOS Y USUARIOS")
        print_option(f"{Colors.CYAN}4{Colors.RESET} - Gestión de Base de Datos y Usuarios")
        print_option(f"{Colors.CYAN}5{Colors.RESET} - Gestión de Usuarios (Acceso Rápido)")

        print_section("CONFIGURACIÓN Y SISTEMA")
        print_option(f"{Colors.YELLOW}I{Colors.RESET} - Instalación Rápida (Plug & Play)")
        print_option(f"{Colors.CYAN}6{Colors.RESET} - Configuración de Entorno (.env)")
        print_option(f"{Colors.CYAN}7{Colors.RESET} - Servicios del Sistema (Nginx / IP directa)")
        print_option(f"{Colors.CYAN}8{Colors.RESET} - Mantenimiento del Sistema")

        print_section("DESARROLLO")
        print_option(f"{Colors.BLUE}9{Colors.RESET}  - Consola de Pruebas (Django Shell)")
        print_option(f"{Colors.BLUE}10{Colors.RESET} - Todos los Scripts (Avanzado)")
        print_option(f"{Colors.BLUE}11{Colors.RESET} - Información del Sistema")
        print_option(f"{Colors.BLUE}12{Colors.RESET} - Ayuda General")

        print_section("PRUEBAS Y CALIDAD")
        print_option(f"{Colors.MAGENTA}P{Colors.RESET} - Menú de Pruebas Unitarias")

        print_option(f"\n{Colors.RED}0{Colors.RESET} - Salir")
        print()

        choice = input(f"{Colors.BOLD}  ? Selecciona: {Colors.RESET}").strip().lower()

        if choice == '1':
            run_script('run_services.py', 'backend', use_venv=False)
        elif choice == '2':
            run_script('run_services.py', 'frontend', use_venv=False)
        elif choice in ('3', 'a'):
            run_script('run_services.py', 'all', use_venv=False)
        elif choice == 'm':
            run_script('migrations.py', 'sync')
            pause()
        elif choice == '4':
            show_data_menu()
        elif choice == '5':
            show_users_menu()
        elif choice == 'i':
            run_script('system_setup.py', use_venv=False)
            pause()
        elif choice == '6':
            show_config_menu()
        elif choice == '7':
            show_services_menu()
        elif choice == '8':
            show_system_menu()
        elif choice == '9':
            run_script('test_shell.py')
            pause()
        elif choice == '10':
            show_scripts_menu()
        elif choice == '11':
            show_system_info()
        elif choice == '12':
            show_help()
        elif choice == 'p':
            show_tests_menu()
        elif choice == '0':
            print_info("¡Adiós!")
            sys.exit(0)
        else:
            print_error("Opción inválida")
            time.sleep(1)

# ── Menú de Datos ─────────────────────────────────────────────────────────
def show_data_menu():
    while True:
        clear_screen()
        print_header("GESTIÓN DE BASE DE DATOS Y DATOS")

        print_section("1. Configuración")
        print_option(f"{Colors.CYAN}1{Colors.RESET} - Configurar Conexión (db_config.py)")
        print_option(f"{Colors.CYAN}2{Colors.RESET} - Probar Conexión")

        print_section("2. Estructura y Migraciones")
        print_option(f"{Colors.BLUE}3{Colors.RESET} - Sincronización Total (makemigrations + migrate)")
        print_option(f"{Colors.BLUE}4{Colors.RESET} - Ver historial de Migraciones")

        print_section("3. Contenido")
        print_option(f"{Colors.YELLOW}5{Colors.RESET} - Gestión de Usuarios (CRUD Completo)")
        print_option(f"{Colors.YELLOW}6{Colors.RESET} - Ejecutar Seeders (Poblar con datos de prueba)")

        print_section("4. Auditoría")
        print_option(f"{Colors.MAGENTA}7{Colors.RESET} - Ver Auditoría Reciente (Bitácora)")

        print_section("5. Limpieza (CUIDADO)")
        print_option(f"{Colors.RED}8{Colors.RESET} - Resetear BD Completa")

        print_section("6. Utilidades")
        print_option(f"{Colors.YELLOW}9{Colors.RESET} - Sanear Dominios de Tenants (quitar guiones bajos)")

        print_option(f"\n{Colors.RED}b{Colors.RESET} - Volver")
        print()

        choice = input(f"{Colors.BOLD}  ? Selyecciona: {Colors.RESET}").strip().lower()

        if choice == '1':
            run_script('db_config.py'); pause()
        elif choice == '2':
            run_script('db_config.py', 'test'); pause()
        elif choice == '3':
            run_script('migrations.py', 'sync'); pause()
        elif choice == '4':
            run_script('migrations.py', 'show'); pause()
        elif choice == '5':
            show_users_menu()
        elif choice == '6':
            run_script('db_seed.py'); pause()
        elif choice == '7':
            run_script('testUnit/verify_audit.py'); pause()
        elif choice == '8':
            if input(f"{Colors.RED}¿SEGURO? Borra todo. (s/n): {Colors.RESET}").lower() == 's':
                run_script('db_reset.py', 'all')
            pause()
        elif choice == '9':
            print_info("Buscando dominios con guiones bajos...")
            run_script('fix_tenant_domains.py'); pause()
        elif choice == 'b':
            break
        else:
            print_error("Opción inválida"); time.sleep(1)

# ── Menú de Usuarios ──────────────────────────────────────────────────────
def show_users_menu():
    while True:
        clear_screen()
        print_header("GESTIÓN DE USUARIOS")

        print_section("Operaciones Básicas (CRUD)")
        print_option(f"{Colors.YELLOW}1{Colors.RESET} - Crear nuevo usuario")
        print_option(f"{Colors.YELLOW}2{Colors.RESET} - Listar usuarios")
        print_option(f"{Colors.YELLOW}3{Colors.RESET} - Editar usuario")
        print_option(f"{Colors.YELLOW}4{Colors.RESET} - Eliminar usuario")

        print_section("Estado y Control de Acceso")
        print_option(f"{Colors.CYAN}5{Colors.RESET} - Ver estado")
        print_option(f"{Colors.GREEN}6{Colors.RESET} - Activar usuario")
        print_option(f"{Colors.RED}7{Colors.RESET} - Desactivar usuario")

        print_option(f"\n{Colors.RED}b{Colors.RESET} - Volver")
        print()

        choice = input(f"{Colors.BOLD}  ? Selecciona: {Colors.RESET}").strip().lower()
        cmds = {
            '1': 'create', '2': 'list', '3': 'edit',
            '4': 'delete', '5': 'status', '6': 'activate', '7': 'disable'
        }
        if choice in cmds:
            run_script('manage_users.py', cmds[choice]); pause()
        elif choice == 'b':
            break
        else:
            print_error("Opción inválida"); time.sleep(1)

# ── Menú de Configuración ─────────────────────────────────────────────────
def show_config_menu():
    while True:
        clear_screen()
        print_header("CONFIGURACIÓN")

        print_section("Entorno")
        print_option(f"{Colors.CYAN}1{Colors.RESET} - Ver .env")
        print_option(f"{Colors.CYAN}2{Colors.RESET} - Editar .env")
        print_option(f"{Colors.CYAN}r{Colors.RESET} - Restablecer .env desde plantilla")

        print_section("Proyecto")
        print_option(f"{Colors.CYAN}3{Colors.RESET} - Info del proyecto")
        print_option(f"{Colors.CYAN}4{Colors.RESET} - Configuración avanzada (project_config.py)")
        print_option(f"{Colors.CYAN}5{Colors.RESET} - Configurar Dominio SaaS")

        print_option(f"\n{Colors.RED}b{Colors.RESET} - Volver")
        print()

        choice = input(f"{Colors.BOLD}  ? Selecciona: {Colors.RESET}").strip().lower()

        if choice == '1':
            env_file = PROJECT_ROOT / '.env'
            if env_file.exists():
                print_section("Contenido de .env")
                print(env_file.read_text(encoding='utf-8'))
            else:
                print_warning(".env no existe")
            pause()
        elif choice == '2':
            _open_file(PROJECT_ROOT / '.env'); pause()
        elif choice == 'r':
            _reset_env(); pause()
        elif choice == '3':
            print_section("Información del Proyecto")
            print(f"  Ruta:     {PROJECT_ROOT}")
            print(f"  Backend:  {BACKEND_DIR}")
            print(f"  Frontend: {FRONTEND_DIR}")
            print(f"  Scripts:  {SCRIPTS_DIR}")
            pause()
        elif choice == '4':
            run_script('project_config.py'); pause()
        elif choice == '5':
            _setup_saas_domain(); pause()
        elif choice == 'b':
            break
        else:
            print_error("Opción inválida"); time.sleep(1)

def _open_file(path):
    if ES_WINDOWS:
        os.startfile(path)
    elif ES_MAC:
        subprocess.run(['open', str(path)])
    else:
        subprocess.run(['xdg-open', str(path)])
    print_success("Abierto en editor")

def _reset_env():
    env_file = PROJECT_ROOT / '.env'
    template = PROJECT_ROOT / '.env.example'
    if input(f"{Colors.YELLOW}¿Restablecer .env? Se perderán cambios. (s/n): {Colors.RESET}").lower() == 's':
        if template.exists():
            shutil.copy(template, env_file)
            print_success(".env restablecido desde plantilla")
        else:
            print_error(".env.example no encontrado")

def _setup_saas_domain():
    """Configura el sufijo de dominio SaaS."""
    print_header("CONFIGURAR DOMINIO SAAS")
    print_info("Selecciona modo de dominio para los tenants:")
    print_option("1. Localhost (.localhost)")
    print_option("2. VPS con nip.io")
    print_option("3. Personalizado")
    print_option("0. Cancelar")

    env_vars = load_env_manual()
    choice = input(f"  ? ").strip()
    new_suffix = None

    if choice == '1':
        new_suffix = '.localhost'
    elif choice == '2':
        vps_ip = env_vars.get('DOMAIN_MAIN', '')
        if not vps_ip or vps_ip == 'localhost':
            vps_ip = input("IP del VPS: ").strip()
        new_suffix = f'.{vps_ip}.nip.io'
    elif choice == '3':
        new_suffix = input("Sufijo (debe empezar con punto): ").strip()
        if not new_suffix.startswith('.'):
            new_suffix = '.' + new_suffix

    if new_suffix:
        _write_env_key('TENANT_DOMAIN_SUFFIX', f"'{new_suffix}'")
        print_success(f"Sufijo configurado: {new_suffix}")

def _write_env_key(key, value):
    env_path = PROJECT_ROOT / '.env'
    lines = []
    found = False
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith(f'{key}='):
                    lines.append(f'{key}={value}\n')
                    found = True
                else:
                    lines.append(line)
    if not found:
        lines.append(f'{key}={value}\n')
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

# ── Menú de Servicios (Nginx / IP) ────────────────────────────────────────
def show_services_menu():
    while True:
        clear_screen()
        print_header("SERVICIOS DEL SISTEMA")

        print_section("Crear paquete completo de servicios")
        print_option(f"  {Colors.GREEN}1{Colors.RESET} - {Colors.BOLD}Con Nginx{Colors.RESET} (Producción: gunicorn + build + Nginx)")
        print_option(f"  {Colors.CYAN}2{Colors.RESET} - {Colors.BOLD}IP directa{Colors.RESET} (Sin Nginx: puertos directos)")

        print_section("Mantenimiento")
        print_option(f"  {Colors.CYAN}3{Colors.RESET} - Ver estado servicios")
        print_option(f"  {Colors.CYAN}4{Colors.RESET} - Ver logs")
        print_option(f"  {Colors.CYAN}5{Colors.RESET} - Recargar Nginx")
        print_option(f"  {Colors.CYAN}6{Colors.RESET} - Reiniciar todo")
        print_option(f"  {Colors.CYAN}7{Colors.RESET} - Consultar Dominios / Tenants")

        print_section("Peligro")
        print_option(f"  {Colors.RED}D{Colors.RESET} - Eliminar TODOS los servicios")

        print_option(f"\n  {Colors.RED}b{Colors.RESET} - Volver")
        print()

        choice = input(f"{Colors.BOLD}  ? Selecciona: {Colors.RESET}").strip().lower()

        if choice == '1':
            loading_animation(1, "Preparando servicios Nginx")
            run_script('nginx_config.py', 'create-all-nginx'); pause()
        elif choice == '2':
            loading_animation(1, "Preparando servicios IP directa")
            run_script('nginx_config.py', 'create-all-ip'); pause()
        elif choice == '3':
            run_script('nginx_config.py', 'status'); pause()
        elif choice == '4':
            run_script('nginx_config.py', 'logs'); pause()
        elif choice == '5':
            run_script('nginx_config.py', 'reload-nginx'); pause()
        elif choice == '6':
            run_script('nginx_config.py', 'restart'); pause()
        elif choice == '7':
            run_script('query_domains.py'); pause()
        elif choice == 'd':
            if input(f"{Colors.RED}  ¿Eliminar TODOS los servicios? (s/n): {Colors.RESET}").lower() == 's':
                run_script('nginx_config.py', 'delete-all')
            pause()
        elif choice == 'b':
            break
        else:
            print_error("Opción inválida"); time.sleep(1)

# ── Menú de Mantenimiento ─────────────────────────────────────────────────
def show_system_menu():
    while True:
        clear_screen()
        print_header("GESTIÓN DE SISTEMA Y MANTENIMIENTO")

        print_section("Actualización")
        print_option(f"{Colors.CYAN}1{Colors.RESET} - Actualizar Django (pip install)")
        print_option(f"{Colors.CYAN}2{Colors.RESET} - Reinstalación limpia de Frontend (npm install)")
        print_option(f"{Colors.CYAN}3{Colors.RESET} - Actualizar Sistema Operativo (apt)")

        print_section("Seguridad y VPS")
        print_option(f"{Colors.MAGENTA}V{Colors.RESET} - Panel de Control VPS")
        print_option(f"{Colors.CYAN}4{Colors.RESET} - Generar Secrets (JWT/Django)")

        print_section("Estado")
        print_option(f"{Colors.CYAN}6{Colors.RESET} - Salud del Sistema")

        print_option(f"\n{Colors.RED}b{Colors.RESET} - Volver")
        print()

        choice = input(f"{Colors.BOLD}  ? Selecciona: {Colors.RESET}").strip().lower()

        if choice == '1':
            loading_animation(2, "Actualizando")
            run_script('system_manager.py', 'update-django'); pause()
        elif choice == '2':
            loading_animation(2, "Actualizando")
            run_script('system_manager.py', 'update-npm'); pause()
        elif choice == '3':
            loading_animation(3, "Actualizando")
            run_script('system_manager.py', 'update-system'); pause()
        elif choice == 'v':
            show_vps_menu()
        elif choice == '4':
            run_script('system_manager.py', 'generate-secrets'); pause()
        elif choice == '6':
            run_script('system_manager.py', 'health-check'); pause()
        elif choice == 'b':
            break
        else:
            print_error("Opción inválida"); time.sleep(1)

# ── Menú VPS ──────────────────────────────────────────────────────────────
def show_vps_menu():
    while True:
        clear_screen()
        print_header("PANEL DE CONTROL VPS")

        print_section("Resiliencia y Monitoreo")
        print_option(f"{Colors.GREEN}1{Colors.RESET} - Estado y Auto-Healing")
        print_option(f"{Colors.CYAN}2{Colors.RESET} - Auditoría de Firewall (UFW)")
        print_option(f"{Colors.CYAN}3{Colors.RESET} - Prueba de Renovación SSL")

        print_section("Respaldos")
        print_option(f"{Colors.YELLOW}S{Colors.RESET} - Crear SNAPSHOT")
        print_option(f"{Colors.YELLOW}R{Colors.RESET} - Restaurar desde SNAPSHOT")

        print_section("Mantenimiento")
        print_option(f"{Colors.CYAN}4{Colors.RESET} - Limpieza del Sistema")
        print_option(f"{Colors.CYAN}7{Colors.RESET} - Limpieza Profunda Frontend (borrar build y reconstruir)")
        print_option(f"{Colors.CYAN}5{Colors.RESET} - Crear Usuario de Sistema")

        print_option(f"\n{Colors.RED}b{Colors.RESET} - Volver")
        print()

        choice = input(f"{Colors.BOLD}  ? Selecciona: {Colors.RESET}").strip().lower()

        if choice == '1':
            run_script('vps.py', 'services', 'AUTOHEAL'); pause()
        elif choice == '2':
            run_script('vps.py', 'security', 'FW'); pause()
        elif choice == '3':
            run_script('vps.py', 'ssl', 'RENEW'); pause()
        elif choice == 's':
            name = input("Nombre del snapshot: ").strip()
            run_script('vps.py', 'backup', 'SNAPSHOT', name); pause()
        elif choice == 'r':
            run_script('vps.py', 'backup', 'RESTORE'); pause()
        elif choice == '4':
            run_script('vps.py', 'system', 'CLEAN'); pause()
        elif choice == '7':
            _deep_clean_frontend(); pause()
        elif choice == '5':
            user = input("Nombre de usuario: ")
            pw   = input("Contraseña: ")
            run_script('vps.py', 'user', 'CREATE', user, pw); pause()
        elif choice == 'b':
            break
        else:
            print_error("Opción inválida"); time.sleep(1)

def _deep_clean_frontend():
    print_header("LIMPIEZA PROFUNDA FRONTEND")
    print_warning("Detendrá el frontend, borrará 'build' y lo reconstruirá.")
    if input("¿Continuar? (s/n): ").lower() != 's':
        return
    subprocess.run(['sudo', 'systemctl', 'stop', 'frontend_saas'], check=False)
    subprocess.run(['sudo', 'fuser', '-k', '3000/tcp'], capture_output=True)
    build_dir = FRONTEND_DIR / 'build'
    if build_dir.exists():
        shutil.rmtree(build_dir)
        print_info("Carpeta build eliminada")
    try:
        subprocess.run('npm run build', cwd=str(FRONTEND_DIR), check=True, shell=True)
        print_success("Build completado")
    except Exception as e:
        print_error(f"Error en build: {e}")
    subprocess.run(['sudo', 'systemctl', 'start', 'frontend_saas'], check=False)
    print_success("Servicio Frontend reiniciado")

# ── Menú Scripts ──────────────────────────────────────────────────────────
def show_scripts_menu():
    while True:
        clear_screen()
        print_header("SCRIPTS ÚTILES")
        print_option(f"{Colors.CYAN}1{Colors.RESET} - db_reset.py")
        print_option(f"{Colors.CYAN}2{Colors.RESET} - db_seed.py")
        print_option(f"{Colors.CYAN}3{Colors.RESET} - manage_users.py")
        print_option(f"{Colors.CYAN}4{Colors.RESET} - test_shell.py")
        print_option(f"\n{Colors.RED}b{Colors.RESET} - Volver")
        print()

        choice = input(f"{Colors.BOLD}  ? Selecciona: {Colors.RESET}").strip().lower()
        scripts = {'1': 'db_reset.py', '2': 'db_seed.py',
                   '3': 'manage_users.py', '4': 'test_shell.py'}
        if choice in scripts:
            run_script(scripts[choice]); pause()
        elif choice == 'b':
            break
        else:
            print_error("Opción inválida"); time.sleep(1)

# ── Menú Pruebas ──────────────────────────────────────────────────────────
def show_tests_menu():
    while True:
        clear_screen()
        print_header("MENÚ DE PRUEBAS UNITARIAS")

        print_section("1. Pruebas Estándar (Django)")
        print_option(f"{Colors.MAGENTA}1{Colors.RESET} - Ejecutar Todos los Tests")
        print_option(f"{Colors.MAGENTA}2{Colors.RESET} - Tests Módulo Usuarios")
        print_option(f"{Colors.MAGENTA}3{Colors.RESET} - Tests Módulo Negocio")

        print_section("2. Escenarios de Integridad")
        print_option(f"{Colors.CYAN}4{Colors.RESET} - Chequeo de Conexión y Esquemas")
        print_option(f"{Colors.CYAN}5{Colors.RESET} - Prueba de Integridad de Datos")
        print_option(f"{Colors.CYAN}6{Colors.RESET} - Prueba de Auditoría")
        print_option(f"{Colors.CYAN}7{Colors.RESET} - Ejecutar Pack Completo (Sprint 1)")
        print_option(f"{Colors.CYAN}8{Colors.RESET} - Ver Bitácora / Auditoría")

        print_section("3. Mantenimiento")
        print_option(f"{Colors.YELLOW}9{Colors.RESET}  - Verificar Migraciones Pendientes")
        print_option(f"{Colors.YELLOW}10{Colors.RESET} - Ejecutar Linter")

        print_option(f"\n{Colors.RED}b{Colors.RESET} - Volver")
        print()

        choice = input(f"{Colors.BOLD}  ? Selecciona: {Colors.RESET}").strip().lower()

        test_cmds = {
            '1': ['test.py', 'django'],
            '2': ['test.py', 'django', 'customers'],
            '3': ['test.py', 'django', 'app_negocio'],
            '5': ['test.py', 'integrity'],
            '6': ['test.py', 'bitacora'],
            '7': ['test.py', 'sprint1'],
            '9': ['test.py', 'migrations'],
            '10': ['test.py', 'lint'],
        }
        if choice in test_cmds:
            run_script(*test_cmds[choice]); pause()
        elif choice == '4':
            run_script('test.py', 'connection')
            run_script('test.py', 'schema'); pause()
        elif choice == '8':
            run_script('testUnit/verify_audit.py'); pause()
        elif choice == 'b':
            break
        else:
            print_error("Opción inválida"); time.sleep(1)

# ── Info del Sistema ──────────────────────────────────────────────────────
def show_system_info():
    clear_screen()
    print_header("INFORMACIÓN DEL SISTEMA")

    print(f"\n{Colors.BOLD}Sistema Operativo:{Colors.RESET}")
    print(f"  {SISTEMA_OPERATIVO} {platform.release()}")

    print(f"\n{Colors.BOLD}Python:{Colors.RESET}")
    print(f"  {sys.version}")
    print(f"  {sys.executable}")

    print(f"\n{Colors.BOLD}Proyecto:{Colors.RESET}")
    print(f"  Ruta:     {PROJECT_ROOT}")
    print(f"  Backend:  {BACKEND_DIR} {'[OK]' if BACKEND_DIR.exists() else '[X]'}")
    print(f"  Frontend: {FRONTEND_DIR} {'[OK]' if FRONTEND_DIR.exists() else '[X]'}")

    for tool, name in [('node', 'Node.js'), ('psql', 'PostgreSQL'), ('nginx', 'Nginx')]:
        exe = shutil.which(tool)
        if exe:
            try:
                result = subprocess.run([exe, '--version'], capture_output=True, text=True)
                ver = result.stdout.strip() or result.stderr.strip()
                print(f"\n{Colors.BOLD}{name}:{Colors.RESET}")
                print(f"  {ver}")
            except Exception:
                print(f"\n{Colors.BOLD}{name}:{Colors.RESET} instalado")
        else:
            print(f"\n{Colors.BOLD}{name}:{Colors.RESET} no instalado")

    pause()

# ── Ayuda ─────────────────────────────────────────────────────────────────
def show_help():
    clear_screen()
    print_header("AYUDA")
    print(f"{Colors.BOLD}Estructura del proyecto:{Colors.RESET}")
    print("  launcher.py          → Este menú interactivo")
    print("  scripts_utiles/      → Toda la lógica de negocio:")
    print("    run_services.py    → Arrancar backend/frontend")
    print("    nginx_config.py    → Servicios systemd + Nginx")
    print("    db_seed.py         → Poblar la base de datos")
    print("    db_reset.py        → Resetear la base de datos")
    print("    manage_users.py    → CRUD de usuarios")
    print("    fix_tenant_domains.py → Sanear dominios inválidos")
    print("    system_manager.py  → Actualización y salud del sistema")
    print("    vps.py             → Control avanzado del VPS")

    print(f"\n{Colors.BOLD}Requisitos:{Colors.RESET}")
    print("  - Python 3.8+")
    print("  - Node.js 14+")
    print("  - PostgreSQL 12+")
    pause()

# ── Main ──────────────────────────────────────────────────────────────────
def main():
    show_main_menu()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Cancelado{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.RESET}")
        sys.exit(1)
