import sys
from django.db import connection
from django.db.utils import OperationalError

def run_database_connection():
    """Verifica la conexion de la base de datos"""
    print("\n[+] 1/4 Verificando conexión a la base de datos...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            row = cursor.fetchone()
        if row == (1,):
            print("  [OK] La conexion de la base de datos es estable")
        else:
            print("  [ERROR] La BD conectó pero respondió con datos inesperados.")
            sys.exit(1)
    except OperationalError as e:
        print(f"  [ERROR] Fallo la conexion a la base de datos: {e}")
        sys.exit(1)

