#!/usr/bin/env python3
# ========================================================================
# RUN SERVICES - Arranque de Backend y Frontend
# ========================================================================
# Gestiona el inicio del servidor Django y el servidor React.
# Soporta 3 modos: localhost, IP directa (red/VPS sin Nginx).
# Este script es llamado por el launcher.py pero también puede
# ejecutarse directamente:
#
#   python scripts_utiles/run_services.py backend
#   python scripts_utiles/run_services.py frontend
#   python scripts_utiles/run_services.py all
# ========================================================================

import os
import sys
import subprocess
import shutil
import time
import platform
from pathlib import Path

# ── Rutas ────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR  = PROJECT_ROOT / 'backend'
FRONTEND_DIR = PROJECT_ROOT / 'frontend'

# ── SO ───────────────────────────────────────────────────────────────────
SISTEMA = platform.system()
ES_WINDOWS = SISTEMA == 'Windows'
ES_LINUX   = SISTEMA == 'Linux'

# ── Colores ──────────────────────────────────────────────────────────────
class C:
    GREEN   = '\033[92m'
    CYAN    = '\033[96m'
    YELLOW  = '\033[93m'
    RED     = '\033[91m'
    BLUE    = '\033[94m'
    GRAY    = '\033[90m'
    BOLD    = '\033[1m'
    RESET   = '\033[0m'

def ok(t):   print(f"{C.GREEN}[OK]{C.RESET} {t}")
def err(t):  print(f"{C.RED}[X]{C.RESET} {t}")
def info(t): print(f"{C.BLUE}[i]{C.RESET} {t}")
def warn(t): print(f"{C.YELLOW}[!]{C.RESET} {t}")

# ── Helpers ──────────────────────────────────────────────────────────────

def load_env():
    """Carga variables del .env de la raíz de forma manual."""
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


def update_env_key(key, value):
    """Actualiza o añade una clave en el .env principal."""
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


def get_local_ip():
    """Detecta la IP de red de la máquina actual."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'


def find_npm():
    """Busca npm en el PATH del sistema."""
    npm = shutil.which('npm')
    if npm:
        return npm
    if ES_WINDOWS:
        for p in ['C:\\Program Files\\nodejs\\npm.cmd',
                  'C:\\Program Files (x86)\\nodejs\\npm.cmd']:
            if os.path.exists(p):
                return p
    return None


def get_venv_python():
    """Devuelve la ruta al Python del venv."""
    if ES_WINDOWS:
        return BACKEND_DIR / 'venv' / 'Scripts' / 'python.exe'
    return BACKEND_DIR / 'venv' / 'bin' / 'python'


def ensure_venv():
    """Crea el venv si no existe. Devuelve la ruta al python del venv."""
    venv_python = get_venv_python()
    if not venv_python.exists():
        warn("Entorno virtual no encontrado, creando...")
        subprocess.run([sys.executable, '-m', 'venv', str(BACKEND_DIR / 'venv')], check=True)
        ok("Entorno virtual creado")
    return venv_python


def ask_run_mode():
    """
    Pregunta el modo de ejecución al usuario.
    Retorna (modo, ip): modo = 'localhost' | 'ip'
    """
    cfg = load_env()
    django_port = cfg.get('DJANGO_PORT', '8001')

    print()
    print(f"  {C.BOLD}MODO DE EJECUCIÓN{C.RESET}")
    print(f"  {C.GREEN}a{C.RESET} - Localhost         (solo esta PC, desarrollo)")
    print(f"  {C.CYAN}b{C.RESET} - IP de la máquina  (red / VPS sin Nginx)")
    print()
    choice = input(f"  {C.BOLD}? [a/b]: {C.RESET}").strip().lower()

    if choice == 'b':
        detected = get_local_ip()
        info(f"IP detectada: {C.YELLOW}{detected}{C.RESET}")
        manual = input(f"  Confirma o escribe otra (Enter = {detected}): ").strip()
        ip = manual if manual else detected
        update_env_key('DOMAIN_MAIN', ip)
        update_env_key('REACT_APP_DOMAIN_MAIN', ip)
        ok(f"Modo IP directa: {ip}")
        return 'ip', ip
    else:
        update_env_key('DOMAIN_MAIN', 'localhost')
        update_env_key('REACT_APP_DOMAIN_MAIN', 'localhost')
        ok("Modo Localhost")
        return 'localhost', 'localhost'


# ── Arranque de servicios ─────────────────────────────────────────────────

def start_backend():
    """Inicia Django con selección de modo."""
    cfg = load_env()
    port = cfg.get('DJANGO_PORT', '8001')

    print(f"\n{'='*70}")
    print(f"  INICIAR BACKEND (DJANGO)")
    print(f"{'='*70}\n")

    if not BACKEND_DIR.exists():
        err(f"Directorio no encontrado: {BACKEND_DIR}")
        return

    if not (BACKEND_DIR / 'manage.py').exists():
        err("manage.py no encontrado")
        return

    venv_python = ensure_venv()
    modo, ip = ask_run_mode()
    bind = f'0.0.0.0:{port}' if modo == 'ip' else f'127.0.0.1:{port}'
    info(f"Bind: {bind}")
    warn("CTRL+C para detener")
    print('-' * 70)

    try:
        os.chdir(BACKEND_DIR)
        if ES_LINUX and modo == 'ip':
            gunicorn = BACKEND_DIR / 'venv' / 'bin' / 'gunicorn'
            if gunicorn.exists():
                info("Usando gunicorn...")
                subprocess.run([str(gunicorn), 'config.wsgi:application',
                                '--bind', bind, '--workers', '2', '--reload'])
            else:
                warn("gunicorn no encontrado, usando runserver")
                subprocess.run([str(venv_python), 'manage.py', 'runserver', bind])
        else:
            subprocess.run([str(venv_python), 'manage.py', 'runserver', bind])
    except KeyboardInterrupt:
        warn("\nServidor Django detenido")
    finally:
        os.chdir(PROJECT_ROOT)


def start_frontend():
    """Inicia React con selección de modo."""
    cfg = load_env()
    port = cfg.get('REACT_PORT', '3000')

    print(f"\n{'='*70}")
    print(f"  INICIAR FRONTEND (REACT)")
    print(f"{'='*70}\n")

    if not FRONTEND_DIR.exists():
        err("Directorio frontend no encontrado")
        return

    npm = find_npm()
    if not npm:
        err("npm no encontrado. Instala Node.js.")
        return

    if not (FRONTEND_DIR / 'node_modules').exists():
        warn("node_modules no encontrado, ejecutando npm install...")
        subprocess.run([npm, 'install'], cwd=str(FRONTEND_DIR),
                       check=True, shell=ES_WINDOWS)
        ok("Dependencias instaladas")

    modo, ip = ask_run_mode()
    env = os.environ.copy()
    env['PORT'] = port
    env['HOST'] = '0.0.0.0' if modo == 'ip' else 'localhost'
    django_port = cfg.get('DJANGO_PORT', '8001')
    env['REACT_APP_DOMAIN_MAIN'] = ip if modo == 'ip' else 'localhost'
    env['REACT_APP_TENANT_DOMAIN_SUFFIX'] = f'.{ip}.nip.io' if modo == 'ip' else '.localhost'
    env['REACT_APP_API_URL'] = f'http://{ip}:{django_port}/api' if modo == 'ip' else f'http://localhost:{django_port}/api'
    
    info(f"Accesible en http://{ip if modo == 'ip' else 'localhost'}:{port}")
    warn("CTRL+C para detener")
    print('-' * 70)

    try:
        os.chdir(FRONTEND_DIR)
        subprocess.run([npm, 'start'], shell=ES_WINDOWS, env=env)
    except KeyboardInterrupt:
        warn("\nServidor React detenido")
    finally:
        os.chdir(PROJECT_ROOT)


def start_all():
    """Inicia Backend + Frontend con logs entrelazados."""
    import threading

    cfg = load_env()
    django_port = cfg.get('DJANGO_PORT', '8001')
    react_port  = cfg.get('REACT_PORT', '3000')

    print(f"\n{'='*70}")
    print(f"  INICIAR TODO (BACKEND + FRONTEND)")
    print(f"{'='*70}\n")

    venv_python = get_venv_python()
    npm = find_npm() or 'npm'

    if not venv_python.exists():
        err("Entorno virtual no encontrado. Ejecuta opción 1 primero.")
        return

    modo, ip = ask_run_mode()
    django_bind = f'0.0.0.0:{django_port}' if modo == 'ip' else f'127.0.0.1:{django_port}'
    env_react = os.environ.copy()
    env_react['PORT'] = react_port
    env_react['HOST'] = '0.0.0.0' if modo == 'ip' else 'localhost'
    env_react['REACT_APP_DOMAIN_MAIN'] = ip if modo == 'ip' else 'localhost'
    env_react['REACT_APP_TENANT_DOMAIN_SUFFIX'] = f'.{ip}.nip.io' if modo == 'ip' else '.localhost'
    env_react['REACT_APP_API_URL'] = f'http://{ip}:{django_port}/api' if modo == 'ip' else f'http://localhost:{django_port}/api'
    
    host_label = ip if modo == 'ip' else 'localhost'

    info(f"Backend  → http://{host_label}:{django_port}")
    info(f"Frontend → http://{host_label}:{react_port}")
    warn("CTRL+C para detener ambos")
    print(f"{C.GRAY}{'-'*70}{C.RESET}")

    def log_output(pipe, prefix, color):
        try:
            for line in iter(pipe.readline, ''):
                if line:
                    print(f"{color}[{prefix}]{C.RESET} {line.rstrip()}")
        except ValueError:
            pass

    # Elegir comando de backend
    if ES_LINUX and modo == 'ip':
        gunicorn = BACKEND_DIR / 'venv' / 'bin' / 'gunicorn'
        if gunicorn.exists():
            backend_cmd = [str(gunicorn), 'config.wsgi:application',
                           '--bind', django_bind, '--workers', '2', '--reload']
        else:
            backend_cmd = [str(venv_python), 'manage.py', 'runserver', django_bind]
    else:
        backend_cmd = [str(venv_python), 'manage.py', 'runserver', django_bind]

    backend_proc = frontend_proc = None
    try:
        backend_proc = subprocess.Popen(
            backend_cmd, cwd=str(BACKEND_DIR),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
        )
        frontend_proc = subprocess.Popen(
            [npm, 'start'], cwd=str(FRONTEND_DIR), env=env_react,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            bufsize=1, shell=ES_WINDOWS
        )
        t1 = threading.Thread(target=log_output, args=(backend_proc.stdout,  'BACK', C.BLUE))
        t2 = threading.Thread(target=log_output, args=(frontend_proc.stdout, 'FRONT', C.CYAN))
        t1.daemon = t2.daemon = True
        t1.start(); t2.start()

        while backend_proc.poll() is None and frontend_proc.poll() is None:
            time.sleep(0.5)

    except KeyboardInterrupt:
        warn("\nDeteniendo servicios...")
    finally:
        for p in [backend_proc, frontend_proc]:
            try:
                if p:
                    p.terminate()
            except Exception:
                pass
        ok("Servicios detenidos")


# ── Entry point ───────────────────────────────────────────────────────────

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else None
    if cmd == 'backend':
        start_backend()
    elif cmd == 'frontend':
        start_frontend()
    elif cmd == 'all':
        start_all()
    else:
        print("Uso: python run_services.py [backend|frontend|all]")


if __name__ == '__main__':
    main()
