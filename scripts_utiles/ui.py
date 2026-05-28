# -*- coding: utf-8 -*-
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
        print_warning("\nProceso cancelado.")
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
                    lines.append(f'{key}={value}\n')
                    found = True
                else:
                    lines.append(line)
    if not found:
        lines.append(f'{key}={value}\n')
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
