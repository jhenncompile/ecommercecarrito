import os
import sys
import django
from django.db import connection
from scripts_utiles.ui import print_info, print_error

def run():
    print_info("Sincronizando secuencias de PostgreSQL...")
    
    # Configurar el entorno Django si no lo está
    if not os.environ.get('DJANGO_SETTINGS_MODULE'):
        sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'backend'))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        django.setup()

    try:
        with connection.cursor() as cursor:
            # Obtener todas las tablas en todos los esquemas (public + tenants)
            cursor.execute("""
                SELECT table_schema, table_name 
                FROM information_schema.tables 
                WHERE table_type = 'BASE TABLE' 
                AND table_schema NOT IN ('information_schema', 'pg_catalog');
            """)
            tables = cursor.fetchall()

            # Paso 1: Encontrar el MAX(id) real para cada secuencia compartida o independiente
            sequence_max_id = {}
            for schema, table in tables:
                cursor.execute(f"""
                    SELECT column_default, is_identity 
                    FROM information_schema.columns 
                    WHERE table_schema = '{schema}' 
                    AND table_name = '{table}' 
                    AND column_name = 'id' 
                    AND (column_default LIKE 'nextval%' OR is_identity = 'YES');
                """)
                if cursor.fetchone():
                    try:
                        cursor.execute(f"SELECT pg_get_serial_sequence('\"{schema}\".\"{table}\"', 'id');")
                        seq_name = cursor.fetchone()[0]
                        if seq_name:
                            cursor.execute(f"SELECT MAX(id) FROM \"{schema}\".\"{table}\"")
                            max_id = cursor.fetchone()[0]
                            if max_id is not None:
                                if seq_name not in sequence_max_id or max_id > sequence_max_id[seq_name]:
                                    sequence_max_id[seq_name] = max_id
                    except Exception:
                        pass
                        
            # Paso 2: Actualizar cada secuencia con su máximo global real
            for seq_name, max_id in sequence_max_id.items():
                try:
                    cursor.execute(f"SELECT setval('{seq_name}', {max_id + 1}, false);")
                except Exception as e:
                    print_info(f"  [Advertencia] No se pudo sincronizar la secuencia {seq_name}: {e}")
        
        print_info("Todas las secuencias han sido actualizadas con exito al MAX(id) correspondiente.")
        return True
    except Exception as e:
        print_error(f"Error al sincronizar secuencias: {e}")
        return False
