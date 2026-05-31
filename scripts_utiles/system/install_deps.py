#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = PROJECT_ROOT / 'backend'
FRONTEND_DIR = PROJECT_ROOT / 'frontend'
FLUTTER_MOVIL_DIR = PROJECT_ROOT / 'movil'
FLUTTER_MCLIENTE_DIR = PROJECT_ROOT / 'mcliente'

ES_WINDOWS = sys.platform == 'win32'

def print_header(text):
    print(f"\n{'='*50}\n[+] {text}\n{'='*50}")

def print_ok(text):
    print(f" [OK] {text}")

def print_err(text):
    print(f" [ERROR] {text}")

def run_command(cmd, cwd, env=None):
    try:
        subprocess.run(cmd, cwd=str(cwd), check=True, shell=ES_WINDOWS, env=env)
        return True
    except subprocess.CalledProcessError as e:
        print_err(f"Comando falló: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
        return False
    except FileNotFoundError:
        print_err(f"No se encontró el comando: {cmd[0] if isinstance(cmd, list) else cmd}")
        return False

def install_backend():
    print_header("Instalando Dependencias Backend (Django)")
    venv_path = BACKEND_DIR / 'venv'
    python_exe = venv_path / ('Scripts/python.exe' if ES_WINDOWS else 'bin/python')
    pip_exe = venv_path / ('Scripts/pip.exe' if ES_WINDOWS else 'bin/pip')

    if not venv_path.exists():
        print(" [i] Creando entorno virtual...")
        run_command([sys.executable, '-m', 'venv', str(venv_path)], cwd=BACKEND_DIR)
    
    req_file = BACKEND_DIR / 'requirements' / 'local.txt'
    if req_file.exists():
        print(" [i] Ejecutando pip install...")
        if run_command([str(pip_exe), 'install', '-r', str(req_file)], cwd=BACKEND_DIR):
            print_ok("Backend instalado correctamente.")
    else:
        print_err("No se encontró requirements/local.txt en el backend.")

def install_frontend():
    print_header("Instalando Dependencias Frontend (React)")
    if FRONTEND_DIR.exists():
        npm_cmd = 'npm.cmd' if ES_WINDOWS else 'npm'
        print(" [i] Ejecutando npm install...")
        if run_command([npm_cmd, 'install', '--legacy-peer-deps'], cwd=FRONTEND_DIR):
            print_ok("Frontend instalado correctamente.")
    else:
        print_err("Directorio frontend no encontrado.")

def install_flutter(app_dir, name):
    print_header(f"Instalando Dependencias Flutter ({name})")
    if app_dir.exists():
        flutter_cmd = 'flutter.bat' if ES_WINDOWS else 'flutter'
        print(" [i] Ejecutando flutter pub get...")
        if run_command([flutter_cmd, 'pub', 'get'], cwd=app_dir):
            print_ok(f"Flutter {name} instalado correctamente.")
    else:
        print_err(f"Directorio {app_dir.name} no encontrado. Saltando...")

def main():
    print_header("INSTALACIÓN RÁPIDA DE DEPENDENCIAS")
    
    install_backend()
    install_frontend()
    install_flutter(FLUTTER_MOVIL_DIR, "movil")
    install_flutter(FLUTTER_MCLIENTE_DIR, "mcliente")

    print_header("PROCESO FINALIZADO")
    print("Todas las dependencias solicitadas han sido instaladas.")

if __name__ == '__main__':
    main()
