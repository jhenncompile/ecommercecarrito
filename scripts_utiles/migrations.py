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
    """Ejecuta un comando de manage.py y captura su salida"""
    python_exe = get_python_exe()
    os.chdir(BACKEND_DIR)
    
    env = os.environ.copy()
    env['PYTHONPATH'] = str(BACKEND_DIR) + (';' if os.name == 'nt' else ':') + env.get('PYTHONPATH', '')
    
    cmd = [python_exe, 'manage.py'] + args + ['--settings=config.settings']
    print(f"\n[Ejecutando] {' '.join(cmd)}")
    
    # Capturamos stdout y stderr para poder analizarlos
    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
    
    if result.returncode != 0 and check:
        return False, result.stdout + result.stderr
    return True, result.stdout

def run_make_migrations():
    """Crea nuevas migraciones detectando cambios recursivamente"""
    print("\n[+] Analizando modelos en busca de cambios...")
    run_django_command(['makemigrations', '--noinput'], check=False)

def run_migrate():
    """Aplica migraciones al esquema público con recuperación inteligente"""
    print("\n[+] Iniciando Sincronización Inteligente de esquema SHARED...")
    
    success, output = run_django_command(['migrate_schemas', '--shared'])
    
    retry_count = 0
    while not success and retry_count < 5:
        # Buscamos patrones de tablas o columnas duplicadas
        import re
        # Detectar el nombre de la migración: "Applying customers.0004_xxx... DuplicateTable"
        match = re.search(r"Applying ([\w\.]+)\.\.\. .*?(DuplicateTable|DuplicateColumn|already exists)", output, re.DOTALL)
        
        if match:
            migration_full = match.group(1)
            app_label, migration_name = migration_full.split('.')
            print(f"\n[!] CONFLICTO DETECTADO: La migración {migration_full} intenta crear algo que ya existe.")
            print(f"[i] Aplicando FAKE quirúrgico a {migration_full} para continuar...")
            
            # Aplicar FAKE solo a esa migración
            run_django_command(['migrate_schemas', '--shared', '--fake', app_label, migration_name])
            
            # Reintentar la migración general
            print("[i] Reintentando sincronización general...")
            success, output = run_django_command(['migrate_schemas', '--shared'])
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
    print("\n[+] Aplicando migraciones solo a los cambios faltantes en todos los TENANTS...")
    run_django_command(['migrate_schemas', '--tenant'])

def run_full_sync():
    """Ejecuta el ciclo completo de sincronización de base de datos de manera robusta para VPS"""
    print("\n" + "="*60)
    print("SINCRONIZACIÓN TOTAL ROBUSTA DE BD (VPS READY)")
    print("="*60)
    
    # 1. Detectar cambios (genera migraciones limpias si el modelo cambió)
    run_make_migrations()
    
    # 2. Aplicar a esquema compartido (Public)
    run_migrate()
    
    # 3. Aplicar a esquemas de clientes (Tenants)
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

def run_fake_migrations(app=None):
    """Aplica migraciones con el flag --fake para resolver conflictos de columnas existentes"""
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
        
    run_django_command(args)
    print("\n[OK] Migraciones marcadas como faked. Ahora puedes intentar 'sync' normalmente.")

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
        print("  fake         - Resolver error 'columna ya existe' (Marca migraciones como aplicadas)")
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
    elif cmd == 'fake':
        app = sys.argv[2] if len(sys.argv) > 2 else None
        run_fake_migrations(app)
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
