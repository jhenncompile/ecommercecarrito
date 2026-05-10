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

def run_django_command(args, check=True):
    """Ejecuta un comando de manage.py con el venv."""
    python_exe = get_python_exe()
    os.chdir(BACKEND_DIR)
    
    env = os.environ.copy()
    env['PYTHONPATH'] = str(BACKEND_DIR) + (';' if os.name == 'nt' else ':') + env.get('PYTHONPATH', '')
    
    cmd = [python_exe, 'manage.py'] + args + ['--settings=config.settings']
    print(f"\n[Ejecutando] {' '.join(cmd)}")
    try:
        return subprocess.run(cmd, env=env, check=check)
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR CRÍTICO] Falló la ejecución del comando: {' '.join(cmd)}")
        print(f"Código de salida: {e.returncode}")
        sys.exit(1)

def run_make_migrations():
    """Crea nuevas migraciones detectando cambios recursivamente"""
    print("\n[+] Analizando modelos en busca de cambios para la mega-migración...")
    # --noinput evita que el proceso se quede colgado en VPS esperando respuestas
    run_django_command(['makemigrations', '--noinput'], check=False)

def run_migrate():
    """Aplica migraciones al esquema público (Shared Apps)"""
    print("\n[+] Aplicando migraciones solo a los cambios faltantes en el esquema SHARED (Público)...")
    run_django_command(['migrate_schemas', '--shared'])

def run_migrate_schemas():
    """Aplica migraciones a todos los esquemas de clientes (Tenants)"""
    print("\n[+] Aplicando migraciones solo a los cambios faltantes en todos los TENANTS...")
    run_django_command(['migrate_schemas', '--tenant'])

def run_full_sync():
    """Ejecuta el ciclo completo de sincronización de base de datos de manera robusta para VPS"""
    print("\n" + "="*60)
    print("SINCRONIZACIÓN TOTAL ROBUSTA DE BD (VPS READY)")
    print("="*60)
    
    # 1. Detectar cambios (mega migración)
    run_make_migrations()
    
    # 2. Aplicar a esquema compartido (Public) explícitamente
    run_migrate()
    
    # 3. Aplicar a esquemas de clientes (Tenants) explícitamente
    run_migrate_schemas()
    
    print("\n" + "="*60)
    print("[OK] Estructura sincronizada correctamente. Solo se aplicaron las migraciones faltantes.")
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
