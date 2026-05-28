
import os, sys, zlib, hashlib
from pathlib import Path
import django
from datetime import datetime

# Setup Django
sys.path.append(str(Path(__file__).resolve().parent.parent.parent / 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.customers.models import RespaldoSistema
from django.conf import settings
import subprocess

def run():
    target = sys.argv[1] if len(sys.argv) > 1 else "SNAPSHOT"
    
    if target == "LIST_AND_RESTORE":
        backups = RespaldoSistema.objects.all()[:10]
        if not backups:
            print("No hay snapshots guardados en la base de datos.")
            return

        print("\n--- SNAPSHOTS DISPONIBLES EN BD ---")
        for i, b in enumerate(backups):
            print(f"{i+1}. {b.nombre} ({b.timestamp.strftime('%Y-%m-%d %H:%M')}) - {b.size_mb} MB")
        
        try:
            choice = int(input("\nSelecciona el ID para RESTAURAR (0 para cancelar): "))
            if choice == 0: return
            res = backups[choice-1]
            
            print(f"\n[!] RESTAURANDO SNAPSHOT: {res.nombre}...")
            blob = res.blob_data
            MAGIC = b"MQHT-V1-BIN"
            
            if not blob.startswith(MAGIC):
                print("Error: Formato de snapshot inválido")
                return
            
            # Extraer checksum y datos
            parts = blob[len(MAGIC):].split(b"||", 1)
            checksum = parts[0].decode()
            compressed = parts[1]
            
            # Verificar integridad
            if hashlib.sha256(compressed).hexdigest() != checksum:
                print("Error: El snapshot está corrupto (checksum mismatch)")
                return
            
            sql_data = zlib.decompress(compressed)
            
            # Aplicar SQL
            db_conf = settings.DATABASES['default']
            env = os.environ.copy()
            if db_conf['PASSWORD']: env['PGPASSWORD'] = db_conf['PASSWORD']
            
            print("Importando datos...")
            proc = subprocess.Popen(['psql', '-U', db_conf['USER'], '-h', db_conf['HOST'], db_conf['NAME']], 
                                   stdin=subprocess.PIPE, env=env)
            proc.communicate(input=sql_data)
            print("\n[EXITO] Sistema restaurado al estado del snapshot.")
            
        except FileNotFoundError:
            print("\n❌ ERROR: El comando 'psql' no está instalado o no se encuentra en el PATH del sistema.")
            if os.name == 'nt':
                print("👉 Por favor, instala PostgreSQL y asegúrate de añadir la carpeta 'bin' (ej. C:\\Program Files\\PostgreSQL\\16\\bin) a las Variables de Entorno del Sistema (PATH).")
            else:
                print("👉 Por favor, instala 'postgresql-client' en tu sistema (ej: sudo apt install postgresql-client).")
        except Exception as e:
            print(f"Error en restauración: {e}")
            
    else:
        nombre = target
        db_conf = settings.DATABASES['default']
        print(f"Exportando Snapshot: {nombre}...")
        
        try:
            env = os.environ.copy()
            if db_conf['PASSWORD']: env['PGPASSWORD'] = db_conf['PASSWORD']
                
            cmd = ['pg_dump', '-U', db_conf['USER'], '-h', db_conf['HOST'], db_conf['NAME']]
            result = subprocess.run(cmd, env=env, capture_output=True, check=True)
            sql_data = result.stdout
            
            # Formato Propietario MQHT-V1
            MAGIC = b"MQHT-V1-BIN"
            compressed = zlib.compress(sql_data)
            checksum = hashlib.sha256(compressed).hexdigest()
            blob = MAGIC + checksum.encode() + b"||" + compressed
            
            RespaldoSistema.objects.create(
                nombre=nombre,
                blob_data=blob,
                metadata={
                    "source": "vps_tool", 
                    "raw_size": len(sql_data),
                    "checksum": checksum
                }
            )
            print(f"SNAPSHOT GUARDADO EXITOSAMENTE: {nombre}")
        except FileNotFoundError:
            print("\n❌ ERROR: El comando 'pg_dump' no está instalado o no se encuentra en el PATH del sistema.")
            if os.name == 'nt':
                print("👉 Por favor, instala PostgreSQL y asegúrate de añadir la carpeta 'bin' (ej. C:\\Program Files\\PostgreSQL\\16\\bin) a las Variables de Entorno del Sistema (PATH).")
            else:
                print("👉 Por favor, instala 'postgresql-client' en tu sistema (ej: sudo apt install postgresql-client).")
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == '__main__':
    run()
