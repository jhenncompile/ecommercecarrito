#!/usr/bin/env python
# ========================================================================
# SCRIPT DE TESTING (RUNNER)
# ========================================================================
# Ejecuta tests del proyecto importando lógica desde testUnit/
# Uso: python scripts_utiles/test.py [opciones]

import os
import sys
import subprocess
from pathlib import Path

# Directorio raíz
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# ========================================================================
# INICIALIZACIÓN DE DJANGO
# ========================================================================
sys.path.insert(0, str(PROJECT_ROOT / 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

# Importar pruebas individuales desde testUnit
from testUnit.db_connection_test import run_database_connection
from testUnit.schema_test import run_schema_check
from testUnit.integrity_test import run_integrity_check
from testUnit.bitacora_test import run_bitacora_test

# ========================================================================

def run_tests():
    """Ejecuta todos los tests"""
    os.chdir(PROJECT_ROOT / 'backend')
    subprocess.run([
        sys.executable, 'manage.py', 'test',
        '--settings=config.settings',
        '--verbosity=2'
    ])

def run_django_tests(app=None):
    """Ejecuta solo tests de Django"""
    os.chdir(PROJECT_ROOT / 'backend')
    cmd = [sys.executable, 'manage.py', 'test']
    if app:
        cmd.append(app)
    else:
        cmd.extend(['negocio', 'customers'])
    cmd.extend(['--verbosity=2'])
    subprocess.run(cmd)

def run_lint():
    """Ejecuta linter (flake8)"""
    print("[+] Ejecutando flake8...")
    subprocess.run([
        sys.executable, '-m', 'flake8',
        str(PROJECT_ROOT / 'backend'),
        '--exclude=venv,migrations',
        '--max-line-length=120'
    ])

def run_migrations_check():
    """Verifica que no hay migraciones pendientes"""
    os.chdir(PROJECT_ROOT / 'backend')
    subprocess.run([
        sys.executable, 'manage.py', 'makemigrations',
        '--dry-run', '--check'
    ])

def main():
    if len(sys.argv) < 2:
        print("Uso: python test.py [comando]")
        print("\nComandos disponibles:")
        print("  all        - Ejecutar todos los tests (Django)")
        print("  django     - Ejecutar tests de Django")
        print("  lint       - Ejecutar linter")
        print("  migrations - Verificar migraciones")
        print("  sprint1    - Ejecutar los checks de BD, Esquemas e Integridad")
        print("  bitacora   - Ejecutar la prueba del sistema de auditoría")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'all':
        run_tests()
    elif cmd == 'django':
        app = sys.argv[2] if len(sys.argv) > 2 else None
        run_django_tests(app)
    elif cmd == 'lint':
        run_lint()
    elif cmd == 'migrations':
        run_migrations_check()
    elif cmd == 'connection':
        run_database_connection()
    elif cmd == 'schema':
        run_schema_check()
    elif cmd == 'integrity':
        run_integrity_check()
    elif cmd == 'sprint1':
        run_database_connection()
        run_schema_check()
        run_integrity_check()
        print("\n[OK] Todas las pruebas del Sprint 1 completadas.")
    elif cmd == 'bitacora':
        run_bitacora_test()
    else:
        print(f"[ERROR] Comando desconocido: {cmd}")
        sys.exit(1)

if __name__ == '__main__':
    main()
