# -*- coding: utf-8 -*-
import os
import re
from pathlib import Path

LAUNCHER_PATH = Path('c:/Users/ldgd2/OneDrive/Documentos/Proyectos_lider/python/ecommerce/launcher.py')
SCRIPTS_DIR = Path('c:/Users/ldgd2/OneDrive/Documentos/Proyectos_lider/python/ecommerce/scripts_utiles')

content = LAUNCHER_PATH.read_text('utf-8')

# We need to split the file into sections.
# It has sections separated by `# === Menu Name ===`
# Let's extract UI first. UI is everything from start up to `# === Menú Flutter/Móvil ===` (or `MenÃº Flutter`)
# But wait, it's safer to just extract functions by parsing.

ui_code = """# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import time
import platform
import shutil
from pathlib import Path

# === SO ===
SISTEMA_OPERATIVO = platform.system()
ES_WINDOWS = SISTEMA_OPERATIVO == 'Windows'
ES_LINUX   = SISTEMA_OPERATIVO == 'Linux'
ES_MAC     = SISTEMA_OPERATIVO == 'Darwin'

# === Rutas ===
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR  = PROJECT_ROOT / 'backend'
FRONTEND_DIR = PROJECT_ROOT / 'frontend'
SCRIPTS_DIR  = PROJECT_ROOT / 'scripts_utiles'

# === Colores ANSI ===
class Colors:
    RED     = '\\033[91m'
    GREEN   = '\\033[92m'
    YELLOW  = '\\033[93m'
    BLUE    = '\\033[94m'
    CYAN    = '\\033[96m'
    MAGENTA = '\\033[95m'
    WHITE   = '\\033[97m'
    GRAY    = '\\033[90m'
    BOLD    = '\\033[1m'
    RESET   = '\\033[0m'
    CHECK   = '[OK]'
    CROSS   = '[X]'
    INFO    = '[i]'
    WARN    = '[!]'

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
                env_vars[key.strip()] = value.strip().strip(\"'\\\"\")
    return env_vars

ENV_CONFIG   = load_env_manual()
DJANGO_PORT  = ENV_CONFIG.get('DJANGO_PORT', '8001')
REACT_PORT   = ENV_CONFIG.get('REACT_PORT',  '3000')

def clear_screen():
    os.system('cls' if ES_WINDOWS else 'clear')

def print_header(text):
    print()
    print(f"{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD} {text}{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*70}{Colors.RESET}\\n")

def print_section(text):
    print(f"\\n{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")

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
    spinner = ['|', '/', '-', '\\\\']
    end_time = time.time() + duration
    idx = 0
    while time.time() < end_time:
        print(f"\\r{Colors.CYAN}{spinner[idx % len(spinner)]}{Colors.RESET} {text}...",
              end='', flush=True)
        idx += 1
        time.sleep(0.1)
    print(f"\\r{Colors.GREEN}{Colors.CHECK}{Colors.RESET} {text}... Listo    ")

def pause():
    input(f"\\n{Colors.BOLD}Presiona ENTER para continuar...{Colors.RESET}")

def run_script(script_name, *args, use_venv=True):
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
        print_warning("\\nProceso cancelado.")
    except Exception as e:
        print_error(f"Error: {e}")
    finally:
        os.chdir(old_cwd)

# Funciones de utilidad movidas aquí para acceso general
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
                    lines.append(f'{key}={value}\\n')
                    found = True
                else:
                    lines.append(line)
    if not found:
        lines.append(f'{key}={value}\\n')
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

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
"""

(SCRIPTS_DIR / 'ui.py').write_text(ui_code, 'utf-8')
(SCRIPTS_DIR / '__init__.py').touch()

# Ahora vamos a extraer cada menu por regex
def extract_function(name, content):
    pattern = rf"def {name}\(.*?\):[\s\S]*?(?=\ndef [a-zA-Z_]|\Z|# ===)"
    match = re.search(pattern, content)
    if match:
        return match.group(0).strip()
    return ""

def extract_section(start_marker, end_marker, content):
    start = content.find(start_marker)
    if start == -1: return ""
    end = content.find(end_marker, start)
    if end == -1: end = len(content)
    return content[start:end].strip()

# DB menu
db_menu_code = """# -*- coding: utf-8 -*-
from scripts_utiles.ui import *
import time

def show_data_menu():
""" + "\n".join("    " + line for line in extract_function("show_data_menu", content).split('\n')[1:])

# En las opciones importan otras, así que _show_users_menu puede referenciar
db_menu_code = db_menu_code.replace("show_users_menu()", "from scripts_utiles.users.menu import show_users_menu\\n            show_users_menu()")
(SCRIPTS_DIR / 'db' / 'menu.py').write_text(db_menu_code, 'utf-8')

# Users menu
users_menu_code = """# -*- coding: utf-8 -*-
from scripts_utiles.ui import *
import time

def show_users_menu():
""" + "\n".join("    " + line for line in extract_function("show_users_menu", content).split('\n')[1:])
(SCRIPTS_DIR / 'users' / 'menu.py').write_text(users_menu_code, 'utf-8')

# Config/Core menu
config_menu_code = """# -*- coding: utf-8 -*-
from scripts_utiles.ui import *
import time

def show_config_menu():
""" + "\n".join("    " + line for line in extract_function("show_config_menu", content).split('\n')[1:])
(SCRIPTS_DIR / 'core' / 'menu.py').write_text(config_menu_code, 'utf-8')

# System menu
system_menu_code = """# -*- coding: utf-8 -*-
from scripts_utiles.ui import *
import time
import subprocess

def show_services_menu():
""" + "\n".join("    " + line for line in extract_function("show_services_menu", content).split('\n')[1:]) + """

def show_system_menu():
""" + "\n".join("    " + line for line in extract_function("show_system_menu", content).split('\n')[1:]) + """

def show_vps_menu():
""" + "\n".join("    " + line for line in extract_function("show_vps_menu", content).split('\n')[1:])

system_menu_code = system_menu_code.replace("show_vps_menu()", "show_vps_menu()")
(SCRIPTS_DIR / 'system' / 'menu.py').write_text(system_menu_code, 'utf-8')

# Flutter menu
flutter_dir = SCRIPTS_DIR / 'flutter'
flutter_dir.mkdir(exist_ok=True)
flutter_code = """# -*- coding: utf-8 -*-
from scripts_utiles.ui import *
import time
import shutil
import subprocess

def _get_flutter_dart_defines():
""" + "\n".join("    " + line for line in extract_function("_get_flutter_dart_defines", content).split('\n')[1:]) + """

def _run_flutter(app_dir, extra_args=None):
""" + "\n".join("    " + line for line in extract_function("_run_flutter", content).split('\n')[1:]) + """

def show_flutter_menu():
""" + "\n".join("    " + line for line in extract_function("show_flutter_menu", content).split('\n')[1:])

flutter_code = flutter_code.replace('app_dir: Path', 'app_dir')
(flutter_dir / 'menu.py').write_text(flutter_code, 'utf-8')

# Utils / Scripts menu
utils_menu_code = """# -*- coding: utf-8 -*-
from scripts_utiles.ui import *
import time

def show_scripts_menu():
""" + "\n".join("    " + line for line in extract_function("show_scripts_menu", content).split('\n')[1:])
(SCRIPTS_DIR / 'utils' / 'menu.py').write_text(utils_menu_code, 'utf-8')


# Create the new launcher.py
new_launcher_code = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ========================================================================
# LANZADOR UNIVERSAL - WINDOWS / LINUX / MAC
# ========================================================================
import sys
import time
from scripts_utiles.ui import *

# Importar modulos de interfaz
from scripts_utiles.db.menu import show_data_menu
from scripts_utiles.users.menu import show_users_menu
from scripts_utiles.system.menu import show_system_menu, show_services_menu
from scripts_utiles.core.menu import show_config_menu
from scripts_utiles.flutter.menu import show_flutter_menu
from scripts_utiles.utils.menu import show_scripts_menu

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

        print_section("APPS MÓVILES (Flutter)")
        ip = ENV_CONFIG.get('DOMAIN_MAIN', '?')
        port = ENV_CONFIG.get('DJANGO_PORT', '8001')
        print_option(f"{Colors.BOLD}{Colors.CYAN}F{Colors.RESET} - {Colors.BOLD}Apps Móviles (movil / mcliente){Colors.RESET}  {Colors.GRAY}→ API: {ip}:{port}{Colors.RESET}")

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

        print_option(f"\\n{Colors.RED}0{Colors.RESET} - Salir")
        print()

        choice = input(f"{Colors.BOLD}  ? Selecciona: {Colors.RESET}").strip().lower()

        if choice == '1':
            run_script('core/run_services.py', 'backend', use_venv=False)
        elif choice == '2':
            run_script('core/run_services.py', 'frontend', use_venv=False)
        elif choice in ('3', 'a'):
            run_script('core/run_services.py', 'all', use_venv=False)
        elif choice == 'm':
            run_script('db/migrations.py', 'sync')
            pause()
        elif choice == '4':
            show_data_menu()
        elif choice == '5':
            show_users_menu()
        elif choice == 'i':
            run_script('system/system_setup.py', use_venv=False)
            pause()
        elif choice == '6':
            show_config_menu()
        elif choice == '7':
            show_services_menu()
        elif choice == '8':
            show_system_menu()
        elif choice == '9':
            run_script('tests/test_shell.py')
            pause()
        elif choice == '10':
            show_scripts_menu()
        elif choice == 'f':
            show_flutter_menu()
        elif choice == '0':
            print_info("¡Adiós!")
            sys.exit(0)
        else:
            print_error("Opción inválida")
            time.sleep(1)

if __name__ == '__main__':
    try:
        show_main_menu()
    except KeyboardInterrupt:
        print_info("\\nSaliendo...")
        sys.exit(0)
"""

LAUNCHER_PATH.write_text(new_launcher_code, 'utf-8')
print("Menús extraídos exitosamente y launcher.py actualizado.")
