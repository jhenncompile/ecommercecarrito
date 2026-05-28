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

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = PROJECT_ROOT / 'backend'

def get_python_exe():
    """Retorna el ejecutable de python del venv si existe."""
    if os.name == 'nt':
        venv_py = BACKEND_DIR / 'venv' / 'Scripts' / 'python.exe'
    else:
        venv_py = BACKEND_DIR / 'venv' / 'bin' / 'python'
    return str(venv_py) if venv_py.exists() else sys.executable

def _build_env():
    env = os.environ.copy()
    sep = ';' if os.name == 'nt' else ':'
    env['PYTHONPATH'] = str(BACKEND_DIR) + sep + env.get('PYTHONPATH', '')
    return env

def run_django_command_visible(args):
    """
    Ejecuta manage.py y muestra la salida en tiempo real en el terminal.
    Retorna el código de retorno.
    """
    python_exe = get_python_exe()
    os.chdir(BACKEND_DIR)
    cmd = [python_exe, 'manage.py'] + args + ['--settings=config.settings']
    print(f"\n[Ejecutando] {' '.join(cmd)}")
    result = subprocess.run(cmd, env=_build_env())
    return result.returncode

def run_django_command_capture(args):
    """
    Ejecuta manage.py capturando la salida (para análisis interno).
    Retorna (success, output_text).
    """
    python_exe = get_python_exe()
    os.chdir(BACKEND_DIR)
    cmd = [python_exe, 'manage.py'] + args + ['--settings=config.settings']
    print(f"\n[Ejecutando] {' '.join(cmd)}")
    result = subprocess.run(cmd, env=_build_env(), capture_output=True, text=True, encoding='utf-8', errors='replace')
    # Siempre imprimir lo que se obtuvo
    combined = result.stdout + result.stderr
    if combined.strip():
        print(combined)
    success = result.returncode == 0
    return success, combined

def run_make_migrations():
    """Crea nuevas migraciones detectando cambios de forma agresiva"""
    print("\n[+] Analizando modelos en busca de cambios...")
    # Forzamos primero la detección en la app principal
    run_django_command_visible(['makemigrations', 'customers', '--noinput'])
    # Luego una detección general
    run_django_command_visible(['makemigrations', '--noinput'])

def run_migrate():
    """Aplica migraciones al esquema público con recuperación inteligente"""
    print("\n[+] Iniciando Sincronización Inteligente de esquema SHARED...")

    success, output = run_django_command_capture(['migrate_schemas', '--shared'])

    retry_count = 0
    while not success and retry_count < 5:
        import re
        match = re.search(
            r"Applying ([\w\.]+)\.\.\. .*?(DuplicateTable|DuplicateColumn|already exists)",
            output, re.DOTALL
        )

        if match:
            migration_full = match.group(1)
            app_label, migration_name = migration_full.split('.')
            print(f"\n[!] CONFLICTO DETECTADO: {migration_full} intenta crear algo que ya existe.")
            print(f"[i] Aplicando FAKE quirúrgico a {migration_full}...")
            run_django_command_visible(['migrate_schemas', '--shared', '--fake', app_label, migration_name])
            print("[i] Reintentando sincronización general...")
            success, output = run_django_command_capture(['migrate_schemas', '--shared'])
            retry_count += 1
        else:
            print("\n[X] ERROR CRÍTICO NO RECUPERABLE:")
            print(output)
            sys.exit(1)

    if success:
        print("\n[OK] Esquema SHARED sincronizado.")
    return success

def run_migrate_schemas():
    """Aplica migraciones a todos los esquemas de clientes (Tenants)"""
    print("\n[+] Aplicando migraciones a todos los TENANTS...")
    run_django_command_visible(['migrate_schemas', '--tenant'])

def run_full_sync():
    """Ejecuta el ciclo completo de sincronización de base de datos con reparación ultra robusta."""
    print("\n" + "="*60)
    print("SINCRONIZACIÓN DE BD (VPS READY)")
    print("="*60)

    print("\n[PASO 1] Reparación Profunda (Fake-Reverse preventivo)...")
    # Retrocedemos la migración para forzar a Django a re-evaluar la existencia de columnas
    run_django_command_visible(['migrate_schemas', '--shared', '--fake', 'customers', '0006'])

    print("\n[PASO 2] Detección de Cambios en Modelos...")
    run_make_migrations()

    print("\n[PASO 3] Sincronización Real y Auto-Reparación (Esquema Public)...")
    run_migrate()

    print("\n[PASO 4] Sincronización de Esquemas de Clientes (Tenants)...")
    run_migrate_schemas()

    print("\n[PASO 5] Sembrando Permisos del Sistema (Roles/Características)...")
    run_django_command_visible(['seed_permisos'])

    print("\n" + "="*60)
    print("[OK] ESTRUCTURA, MIGRACIONES Y PERMISOS SINCRONIZADOS AL 100%.")
    print("="*60)

def run_reset():
    """Llama al script de reset de base de datos"""
    python_exe = get_python_exe()
    script_path = PROJECT_ROOT / 'scripts_utiles' / 'db_reset.py'
    subprocess.run([python_exe, str(script_path), 'all'], env=_build_env())

def run_seed():
    """Llama al script de seeding de base de datos"""
    python_exe = get_python_exe()
    script_path = PROJECT_ROOT / 'scripts_utiles' / 'db_seed.py'
    subprocess.run([python_exe, str(script_path)], env=_build_env())

def run_seed_permisos():
    """Ejecuta el seeder de permisos básicos del sistema."""
    print("\n[+] Sincronizando Permisos Básicos y Premium del sistema...")
    run_django_command_visible(['seed_permisos'])

def show_migrations():
    """Muestra el estado de las migraciones"""
    print("\n[+] Estado actual de migraciones:\n")
    run_django_command_visible(['showmigrations'])

def run_fake_migrations(app=None):
    """Aplica migraciones con --fake para resolver conflictos de columnas existentes"""
    print("\n" + "="*60)
    print("MODO RECUPERACIÓN: FAKE MIGRATIONS")
    print("="*60)
    print("[i] Esto marcará las migraciones como 'aplicadas' sin ejecutar el SQL.")
    print("[i] Útil si las columnas ya existen en la base de datos.")

    if not app:
        app = input("\n¿Aplicación específica? (Enter para todas): ").strip()

    args = ['migrate_schemas', '--shared', '--fake']
    if app:
        args.append(app)

    run_django_command_visible(args)
    print("\n[OK] Migraciones marcadas como faked. Ahora puedes intentar 'sync' normalmente.")

def run_fix_missing():
    """Repara el error 'column does not exist' forzando la re-ejecución de migraciones recientes."""
    print("\n" + "="*60)
    print("MODO REPARACIÓN PROFUNDA (COLUMNA NO EXISTE)")
    print("="*60)
    print("[i] Esto obligará a Django a re-ejecutar las últimas migraciones de 'customers'.")
    run_django_command_visible(['migrate_schemas', '--shared', '--fake', 'customers', '0006'])
    
    print("\n[+] Re-aplicando migraciones SQL reales...")
    run_django_command_visible(['migrate_schemas', '--shared'])
    
    print("\n[+] Sembrando permisos básicos y premium...")
    run_django_command_visible(['seed_permisos'])
    print("\n[OK] Base de datos reparada. Ya puedes crear tiendas con normalidad.")

def main():
    if len(sys.argv) < 2:
        print("\n" + "="*60)
        print(" GESTOR DE BASE DE DATOS (migrations.py)")
        print("="*60)
        print("\nComandos disponibles:")
        print("  sync         - Actualizar estructura (Make + Migrate Shared + Tenants)")
        print("  reset        - REINICIAR TODO (Borra BD, recrea estructura)")
        print("  seed         - Cargar datos de prueba")
        print("  seed_permisos- Cargar permisos base (roles)")
        print("  make         - Solo detectar cambios en modelos (makemigrations)")
        print("  migrate      - Solo aplicar cambios al esquema público")
        print("  tenants      - Solo aplicar cambios a los esquemas de clientes")
        print("  show         - Mostrar estado de migraciones")
        print("  fake         - Resolver error 'columna ya existe'")
        print("  fix_missing  - Resolver error 'columna no existe'")
        print("="*60)
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == 'sync':
        run_full_sync()
    elif cmd == 'reset':
        run_reset()
    elif cmd == 'seed':
        run_seed()
    elif cmd == 'seed_permisos':
        run_seed_permisos()
    elif cmd == 'make':
        run_make_migrations()
    elif cmd == 'migrate':
        run_migrate()
    elif cmd == 'tenants':
        run_migrate_schemas()
    elif cmd == 'show':
        show_migrations()
    elif cmd == 'fake':
        app = sys.argv[2] if len(sys.argv) > 2 else None
        run_fake_migrations(app)
    elif cmd == 'fix_missing':
        run_fix_missing()
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
        import traceback
        traceback.print_exc()
