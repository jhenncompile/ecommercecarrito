#!/usr/bin/env python
# ========================================================================
# SCRIPT DE RESET DE BASE DE DATOS
# ========================================================================
# Gestiona reset y limpieza de BD con opciones
# Uso: python scripts_utiles/db_reset.py [opción]

import os
import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = PROJECT_ROOT / 'backend'

def confirm_destructive():
    """Pide confirmación para operación destructiva"""
    print("\n" + "="*60)
    print("âš ï¸  OPERACIÓN DESTRUCTIVA - Se eliminará la base de datos")
    print("="*60)
    print("\nEsto eliminará:")
    print("  âœ— Todos los datos de la BD")
    print("  âœ— Todos los tenants")
    print("  âœ— Todos los usuarios")
    print("  âœ— Todas las tablas")
    print("\n")
    
    confirm = input("Escribe 'ELIMINAR' en mayúsculas para confirmar: ").strip()
    
    if confirm != "ELIMINAR":
        print("[CANCELADO] Operación abortada")
        return False
    
    return True

def reset_all():
    """Reset completo: elimina BD y recrea desde cero (PostgreSQL)"""
    if not confirm_destructive():
        return False
    
    print("\n[+] Iniciando reset completo (DROP SCHEMAS)...")
    os.chdir(BACKEND_DIR)
    
    from django.db import connection
    from django.conf import settings
    
    try:
        with connection.cursor() as cursor:
            # Encontrar todos los schemas creados (tenants)
            print("[1/4] Eliminando todos los schemas de PostgreSQL...")
            cursor.execute("""
                SELECT schema_name FROM information_schema.schemata 
                WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast');
            """)
            schemas = [row[0] for row in cursor.fetchall()]
            for sch in schemas:
                cursor.execute(f"DROP SCHEMA IF EXISTS {sch} CASCADE;")
            
            # Recrear public schema
            print("[2/4] Recreando schema public...")
            cursor.execute("CREATE SCHEMA public;")
            try:
                db_user = settings.DATABASES['default']['USER']
                cursor.execute(f"GRANT ALL ON SCHEMA public TO {db_user};")
            except Exception:
                pass
    except Exception as e:
        print(f"[ERROR] Falló el drop schemas: {e}")
        return False
        
    print("[3/4] Creando y aplicando migraciones...")
    try:
        # Borrar archivos de migraciones si existen (excepto __init__.py)
        for app in ['customers', 'negocio']:
            mig_dir = BACKEND_DIR / app / 'migrations'
            if mig_dir.exists():
                for f in mig_dir.glob('0*.py'):
                    f.unlink()
    except Exception as e:
        pass
        
    subprocess.run([sys.executable, 'manage.py', 'makemigrations', '--settings=config.settings'], capture_output=True)
    subprocess.run([sys.executable, 'manage.py', 'migrate_schemas', '--shared', '--settings=config.settings'], capture_output=True)
    subprocess.run([sys.executable, 'manage.py', 'migrate', '--settings=config.settings'], capture_output=True)
    
    # Crear superuser
    print("[4/4] Creando superuser...")
    from django.conf import settings
    
    try:
        from apps.customers.models import Usuario
        email = input("  Email del admin: ").strip()
        password = input("  Contraseña: ").strip()
        
        Usuario.objects.create_superuser(
            email=email,
            password=password,
            is_active=True
        )
        print(f"[OK] Superuser creado: {email}")
    except Exception as e:
        print(f"[WARN] No se pudo crear superuser: {e}")
    
    print("[OK] Reset completo finalizado")
    return True

def reset_data_only():
    """Reset solo de datos (mantiene estructura)"""
    print("\n[+] Limpiando solo datos (tablas vacías)...")
    os.chdir(BACKEND_DIR)
    
    print("[1/2] Truncando tablas...")
    try:
        from django.db import connection
        cursor = connection.cursor()
        
        # Obtener todas las tablas
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        # Truncar (excepto migraciones)
        exclude = ['django_migrations', 'django_session', 'django_content_type']
        for table in tables:
            if table not in exclude:
                cursor.execute(f"TRUNCATE TABLE {table} CASCADE")
        
        connection.commit()
        print(f"[OK] {len(tables)} tablas vaciadas")
    except Exception as e:
        print(f"[ERROR] {e}")
        return False
    
    print("[2/2] Completado")
    return True

def reset_tenants():
    """Reset solo de tenants (mantiene usuarios principales)"""
    print("\n[+] Eliminando solo TENANTS...")
    os.chdir(BACKEND_DIR)
    
    try:
        from apps.customers.models import Client
        count = Client.objects.count()
        
        print(f"[?] Se eliminarán {count} tenants")
        confirm = input("Â¿Confirmar? (yes/no): ").strip()
        
        if confirm.lower() == 'yes':
            Client.objects.all().delete()
            print(f"[OK] {count} tenants eliminados")
        else:
            print("[CANCELADO]")
    except Exception as e:
        print(f"[ERROR] {e}")
        return False
    
    return True

def reset_users():
    """Reset solo de usuarios (mantiene todo lo demás)"""
    print("\n[+] Eliminando solo USUARIOS...")
    os.chdir(BACKEND_DIR)
    
    try:
        from apps.customers.models import Usuario
        count = Usuario.objects.count()
        
        print(f"[?] Se eliminarán {count} usuarios")
        confirm = input("Â¿Confirmar? (yes/no): ").strip()
        
        if confirm.lower() == 'yes':
            # Mantener al menos un admin
            Usuario.objects.filter(is_superuser=False).delete()
            print(f"[OK] Usuarios eliminados (admin mantenido)")
        else:
            print("[CANCELADO]")
    except Exception as e:
        print(f"[ERROR] {e}")
        return False
    
    return True

def main():
    if len(sys.argv) < 2:
        print("Uso: python db_reset.py [comando]")
        print("\nComandos disponibles:")
        print("  all        - Reset completo (estructura + datos + usuarios)")
        print("  data       - Limpiar solo datos (mantiene estructura)")
        print("  tenants    - Eliminar solo tenants")
        print("  users      - Eliminar solo usuarios")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'all':
        reset_all()
    elif cmd == 'data':
        reset_data_only()
    elif cmd == 'tenants':
        reset_tenants()
    elif cmd == 'users':
        reset_users()
    else:
        print(f"[ERROR] Comando desconocido: {cmd}")
        sys.exit(1)

if __name__ == '__main__':
    # Configurar Django
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    BACKEND_DIR = PROJECT_ROOT / 'backend'
    sys.path.insert(0, str(BACKEND_DIR))
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    import django
    django.setup()
    
    main()

