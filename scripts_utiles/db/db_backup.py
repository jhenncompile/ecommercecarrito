#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = PROJECT_ROOT / 'backend'

sys.path.append(str(BACKEND_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

def get_db_config():
    import django
    from django.conf import settings
    django.setup()
    return settings.DATABASES['default']

def create_backup():
    print("\n[+] INICIANDO RESPALDO DE BASE DE DATOS")
    try:
        db = get_db_config()
        engine = db['ENGINE']
        db_name = db['NAME']
        
        backup_dir = PROJECT_ROOT / 'backups'
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if 'sqlite3' in engine:
            backup_file = backup_dir / f"backup_sqlite_{timestamp}.sqlite3"
            print(f"Copiando base de datos SQLite a {backup_file}...")
            import shutil
            shutil.copy2(db_name, backup_file)
            print(f"[OK] Respaldo guardado en: {backup_file}")
            
        elif 'postgresql' in engine:
            backup_file = backup_dir / f"backup_pg_{timestamp}.sql.gz"
            user = db['USER']
            host = db['HOST']
            password = db['PASSWORD']
            
            env = os.environ.copy()
            if password:
                env['PGPASSWORD'] = password
            
            print(f"Exportando base de datos PostgreSQL a {backup_file}...")
            cmd = f"pg_dump -U {user} -h {host} {db_name} | gzip > {backup_file}"
            
            result = subprocess.run(cmd, shell=True, env=env, stderr=subprocess.PIPE)
            if result.returncode == 0:
                print(f"[OK] Respaldo guardado en: {backup_file}")
            else:
                print(f"[ERROR] Falló pg_dump: {result.stderr.decode('utf-8', errors='ignore')}")
        else:
            print(f"[ERROR] Motor no soportado: {engine}")
    except Exception as e:
        print(f"[ERROR] {e}")

def restore_backup(file_path):
    print(f"\n[+] INICIANDO RESTAURACIÓN DESDE: {file_path}")
    try:
        db = get_db_config()
        engine = db['ENGINE']
        db_name = db['NAME']
        
        if not os.path.exists(file_path):
            print("[ERROR] Archivo no encontrado")
            return
            
        if 'sqlite3' in engine:
            import shutil
            print("Sobreescribiendo archivo SQLite...")
            shutil.copy2(file_path, db_name)
            print("[OK] Base de datos restaurada.")
            
        elif 'postgresql' in engine:
            user = db['USER']
            host = db['HOST']
            password = db['PASSWORD']
            
            env = os.environ.copy()
            if password:
                env['PGPASSWORD'] = password
                
            print("Restaurando datos en PostgreSQL...")
            if str(file_path).endswith('.gz'):
                cmd = f"zcat {file_path} | psql -U {user} -h {host} {db_name}"
            else:
                cmd = f"psql -U {user} -h {host} {db_name} < {file_path}"
                
            result = subprocess.run(cmd, shell=True, env=env, stderr=subprocess.PIPE)
            if result.returncode == 0:
                print("[OK] Base de datos restaurada.")
            else:
                print(f"[ERROR] Falló la restauración: {result.stderr.decode('utf-8', errors='ignore')}")
    except Exception as e:
        print(f"[ERROR] {e}")

def list_backups_and_restore():
    backup_dir = PROJECT_ROOT / 'backups'
    if not backup_dir.exists():
        print("No hay directorio de backups.")
        return
        
    backups = sorted(list(backup_dir.glob("backup_*")), key=os.path.getmtime, reverse=True)
    if not backups:
        print("No se encontraron backups.")
        return
        
    print("\n--- BACKUPS DISPONIBLES EN DISCO ---")
    for i, b in enumerate(backups):
        size = b.stat().st_size / (1024*1024)
        print(f"{i+1}. {b.name} ({size:.2f} MB)")
        
    try:
        choice = int(input("\nSelecciona ID para RESTAURAR (0 para cancelar): "))
        if choice > 0 and choice <= len(backups):
            restore_backup(backups[choice-1])
    except ValueError:
        print("Cancelado.")

def vacuum_db():
    print("\n[+] INICIANDO OPTIMIZACIÓN (VACUUM)")
    try:
        db = get_db_config()
        engine = db['ENGINE']
        db_name = db['NAME']
        
        if 'sqlite3' in engine:
            print("Ejecutando VACUUM en SQLite...")
            if sys.platform != "win32":
                python_exe = str(PROJECT_ROOT / 'backend' / 'venv' / 'bin' / 'python')
            else:
                python_exe = str(PROJECT_ROOT / 'backend' / 'venv' / 'Scripts' / 'python.exe')
            
            manage_py = str(PROJECT_ROOT / 'backend' / 'manage.py')
            cmd = "from django.db import connection; cursor=connection.cursor(); cursor.execute('VACUUM;'); print('OK')"
            subprocess.run([python_exe, manage_py, "shell", "-c", cmd], check=True)
            print("[OK] Base de datos optimizada.")
            
        elif 'postgresql' in engine:
            user = db['USER']
            host = db['HOST']
            password = db['PASSWORD']
            
            env = os.environ.copy()
            if password:
                env['PGPASSWORD'] = password
            
            print("Ejecutando VACUUM ANALYZE en PostgreSQL...")
            cmd = f"vacuumdb -U {user} -h {host} -d {db_name} --analyze --verbose"
            result = subprocess.run(cmd, shell=True, env=env)
            if result.returncode == 0:
                print("[OK] Base de datos optimizada.")
            else:
                print("[ERROR] Falló la optimización")
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == 'backup':
            create_backup()
        elif cmd == 'restore':
            list_backups_and_restore()
        elif cmd == 'vacuum':
            vacuum_db()
