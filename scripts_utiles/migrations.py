#!/usr/bin/env python
# ========================================================================
# SCRIPT DE MIGRACIONES (OPTIMIZADO)
# ========================================================================
# Gestiona migraciones de BD detectando cambios automáticamente.
# Uso: python scripts_utiles/migrations.py [comando]

import os
import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / 'backend'

def get_python_exe():
    """Retorna el ejecutable de python del venv si existe."""
    venv_py = BACKEND_DIR / 'venv' / 'Scripts' / 'python.exe' if os.name == 'nt' else BACKEND_DIR / 'venv' / 'bin' / 'python'
    return str(venv_py) if venv_py.exists() else sys.executable

def run_django_command(args):
    """Ejecuta un comando de manage.py con el venv."""
    python_exe = get_python_exe()
    os.chdir(BACKEND_DIR)
    
    env = os.environ.copy()
    env['PYTHONPATH'] = str(BACKEND_DIR) + (';' if os.name == 'nt' else ':') + env.get('PYTHONPATH', '')
    
    cmd = [python_exe, 'manage.py'] + args + ['--settings=config.settings']
    print(f"\n[Ejecutando] {' '.join(cmd)}")
    return subprocess.run(cmd, env=env)

def run_make_migrations():
    """Crea nuevas migraciones detectando cambios recursivamente"""
    print("\n[+] Analizando modelos en busca de cambios...")
    run_django_command(['makemigrations'])

def run_migrate():
    """Aplica migraciones al esquema público (Shared Apps)"""
    print("\n[+] Aplicando migraciones al esquema SHARED (Público)...")
    run_django_command(['migrate'])

def run_migrate_schemas():
    """Aplica migraciones a todos los esquemas de clientes (Tenants)"""
    print("\n[+] Aplicando migraciones a todos los TENANTS...")
    # django-tenants usa migrate_schemas para las TENANT_APPS
    run_django_command(['migrate_schemas'])

def run_full_sync():
    """Ejecuta el ciclo completo de sincronización de base de datos"""
    print("\n" + "="*60)
    print("SINCRONIZACIÓN TOTAL DE ESTRUCTURA DE BASE DE DATOS")
    print("="*60)
    
    # 1. Detectar cambios
    run_make_migrations()
    
    # 2. Aplicar a esquema compartido (Public)
    run_migrate()
    
    # 3. Aplicar a esquemas de clientes (Tenants)
    run_migrate_schemas()
    
    print("\n" + "="*60)
    print("[OK] Estructura sincronizada correctamente.")
    print("="*60)

def run_reset():
    """Llama al script de reset de base de datos"""
    python_exe = get_python_exe()
    script_path = PROJECT_ROOT / 'scripts_utiles' / 'db_reset.py'
    subprocess.run([python_exe, str(script_path), 'all'])

def run_seed():
    """Llama al script de seeding de base de datos"""
    python_exe = get_python_exe()
    script_path = PROJECT_ROOT / 'scripts_utiles' / 'db_seed.py'
    subprocess.run([python_exe, str(script_path)])

def show_migrations():
    """Muestra el estado de las migraciones"""
    run_django_command(['showmigrations'])

def main():
    if len(sys.argv) < 2:
        print("\n" + "="*60)
        print(" GESTOR DE BASE DE DATOS (mine.py / migrations.py)")
        print("="*60)
        print("\nComandos disponibles:")
        print("  sync         - Actualizar estructura (Make + Migrate Shared + Tenants)")
        print("  reset        - REINICIAR TODO (Borra BD, recrea estructura y pide admin)")
        print("  seed         - Cargar datos de prueba (Tiendas, Productos, Usuarios)")
        print("  make         - Solo detectar cambios en modelos (makemigrations)")
        print("  migrate      - Solo aplicar cambios al esquema público")
        print("  tenants      - Solo aplicar cambios a los esquemas de clientes")
        print("  show         - Mostrar estado de migraciones")
        print("="*60)
        sys.exit(1)
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'sync':
        run_full_sync()
    elif cmd == 'reset':
        run_reset()
    elif cmd == 'seed':
        run_seed()
    elif cmd == 'make':
        run_make_migrations()
    elif cmd == 'migrate':
        run_migrate()
    elif cmd == 'tenants':
        run_migrate_schemas()
    elif cmd == 'show':
        show_migrations()
    else:
        print(f"[ERROR] Comando desconocido: {cmd}")
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Operación cancelada por el usuario.")
    except Exception as e:
        print(f"\n[FATAL] Error inesperado: {e}")
