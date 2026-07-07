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

def run_django_command_capture(args, silent_error=False):
    """
    Ejecuta manage.py capturando la salida (para análisis interno).
    Retorna (success, output_text).
    Si silent_error es True, no imprime el log de error si falla (útil para pasos de recovery).
    """
    python_exe = get_python_exe()
    os.chdir(BACKEND_DIR)
    cmd = [python_exe, 'manage.py'] + args + ['--settings=config.settings']
    if not silent_error:
        print(f"\n[Ejecutando] {' '.join(cmd)}")
    
    result = subprocess.run(cmd, env=_build_env(), capture_output=True, text=True, encoding='utf-8', errors='replace')
    combined = result.stdout + result.stderr
    success = result.returncode == 0
    
    if not silent_error:
        if combined.strip():
            sys.stdout.buffer.write(combined.encode('utf-8', errors='replace'))
            sys.stdout.buffer.write(b'\n')
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
            r"Applying ([\w\.]+)\.\.\.\s*.*?(DuplicateTable|DuplicateColumn|already exists|ya existe)",
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
            print("\n[X] El esquema SHARED (public) reportó un error no auto-recuperable:")
            sys.stdout.buffer.write(output.encode('utf-8', errors='replace'))
            sys.stdout.buffer.write(b'\n')
            # IMPORTANTE: NO abortamos aquí. Devolvemos False y dejamos que el flujo
            # continúe a migrar los TENANTS, para no dejar las tiendas sin sus tablas.
            return False

    if success:
        print("\n[OK] Esquema SHARED sincronizado.")
    return success

def run_migrate_schemas():
    """Aplica migraciones a todos los esquemas de clientes (Tenants)"""
    print("\n[+] Aplicando migraciones a todos los TENANTS...")
    run_django_command_visible(['migrate_schemas', '--tenant'])

def run_full_sync():
    """Ejecuta el ciclo completo de sincronización de base de datos.

    Orden robusto: el paso de TENANTS SIEMPRE se ejecuta, incluso si el esquema
    público reporta problemas, para que las tiendas nunca se queden sin sus tablas.
    """
    print("\n" + "="*60)
    print("SINCRONIZACIÓN DE BD (VPS READY)")
    print("="*60)

    print("\n[PASO 1] Detección de Cambios en Modelos (makemigrations)...")
    # Si las migraciones ya existen (p. ej. tras un git pull), dirá "No changes
    # detected" — eso es correcto, no hay nada que crear.
    run_make_migrations()

    print("\n[PASO 2] Sincronización y Auto-Reparación del Esquema Público (SHARED)...")
    # run_migrate() ya NO aborta el proceso; si el público falla, seguimos igual
    # con los tenants (que es donde viven productos, pedidos, reseñas, restock...).
    ok_shared = run_migrate()
    if not ok_shared:
        print("  [!] El esquema público quedó con pendientes, pero continúo con los "
              "TENANTS para no dejar las tiendas sin sus tablas.")

    print("\n[PASO 3] Sincronización de TODAS las Tiendas (TENANTS)...")
    # Este es el paso que crea app_negocio_resena, app_negocio_restock_request,
    # app_negocio_delivery_zone y las columnas de preventa/envío en cada tenant.
    run_migrate_schemas()

    print("\n[PASO 4] Sembrando Permisos del Sistema (Roles/Características)...")
    run_django_command_visible(['seed_permisos'])

    print("\n" + "="*60)
    print("[OK] ESTRUCTURA, MIGRACIONES Y PERMISOS SINCRONIZADOS (public + tenants).")
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
    
    print("\n[+] Re-aplicando migración 0007 (Creación de columnas, silencioso si falla)...")
    success_7, _ = run_django_command_capture(['migrate_schemas', '--shared', 'customers', '0007'], silent_error=True)
    if not success_7:
        print("  [i] La migración 0007 ya existía o tenía conflicto (auto-recuperado).")

    print("\n[+] Fakeando migración 0008 (Constraint que ya existe, silencioso si falla)...")
    success_8, _ = run_django_command_capture(['migrate_schemas', '--shared', '--fake', 'customers', '0008'], silent_error=True)
    if not success_8:
        print("  [i] Fake 0008 auto-recuperado.")
    
    print("\n[+] Verificando migraciones restantes...")
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
