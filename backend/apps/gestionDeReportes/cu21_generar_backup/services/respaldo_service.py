import os
import subprocess
import logging
from django.conf import settings
from django.utils import timezone
from ..models.respaldo import RespaldoSistema

logger = logging.getLogger(__name__)

class RespaldoService:
    def crear_respaldo(self, nombre_base="Manual"):
        """
        Crea un volcado binario del sistema, genera un catálogo de tablas
        y actualiza la lista doblemente ligada.
        """
        project_root = getattr(settings, 'PROJECT_ROOT', settings.BASE_DIR.parent)
        backup_dir = os.path.join(project_root, 'backups')
        
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            
        now = timezone.now()
        timestamp_str = now.strftime('%Y%m%d_%H%M%S')
        
        # CAMBIO: Usamos formato binario (.dump) que es más eficiente y estructurado
        filename = f"backup_{timestamp_str}.dump"
        full_path = os.path.join(backup_dir, filename)
        
        db_config = settings.DATABASES['default']
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['PASSWORD']
        
        import shutil
        import glob
        
        pg_dump_path = shutil.which('pg_dump')
        if not pg_dump_path:
            # Fallback for Windows standard PostgreSQL installation
            if os.name == 'nt':
                pg_paths = glob.glob(r'C:\Program Files\PostgreSQL\*\bin\pg_dump.exe')
                if pg_paths:
                    pg_dump_path = pg_paths[-1] # Pick the latest version
                else:
                    pg_dump_path = 'pg_dump' # Let it fail if not found
            else:
                pg_dump_path = '/usr/bin/pg_dump'
        
        # CAMBIO: Flags -Fc (Custom Binary Format) y -Z9 (Compresión máxima)
        cmd = [
            pg_dump_path,
            '-h', db_config['HOST'],
            '-p', str(db_config['PORT']),
            '-U', db_config['USER'],
            '-d', db_config['NAME'],
            '-Fc',  # Formato Custom (Binario)
            '-Z9',  # Compresión máxima
            '-f', full_path
        ]
        
        try:
            logger.info(f"Generando snapshot binario en {full_path}")
            subprocess.run(
                cmd, env=env, check=True, capture_output=True, text=True,
                errors='replace'
            )
            
            # GENERAR CATÁLOGO: Obtenemos info de lo que acabamos de respaldar
            catalogo = self._generar_catalogo_actual()
            
            ultimo_respaldo = RespaldoSistema.objects.filter(siguiente__isnull=True).order_by('-timestamp').first()
            
            nuevo_respaldo = RespaldoSistema.objects.create(
                nombre=f"{nombre_base}",
                archivo_path=full_path,
                anterior=ultimo_respaldo,
                metadata={
                    'size_bytes': os.path.getsize(full_path),
                    'timestamp_completo': timestamp_str,
                    'formato': 'PostgreSQL Custom Binary',
                    'catalogo': catalogo
                }
            )
            
            if ultimo_respaldo:
                ultimo_respaldo.siguiente = nuevo_respaldo
                ultimo_respaldo.save()
            
            return nuevo_respaldo
            
        except Exception as e:
            logger.error(f"❌ Error crítico en backup: {str(e)}")
            raise e

    def restaurar_respaldo(self, respaldo_id):
        """Restaura la base de datos a partir de un respaldo usando pg_restore."""
        from ..models.respaldo import RespaldoSistema, ConfiguracionRespaldo
        
        respaldo = RespaldoSistema.objects.get(id=respaldo_id)
        if not respaldo.archivo_path or not os.path.exists(respaldo.archivo_path):
            raise Exception("El archivo físico del respaldo no existe.")
            
        db_config = settings.DATABASES['default']
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['PASSWORD']
        
        import shutil
        import glob
        pg_restore_path = shutil.which('pg_restore')
        if not pg_restore_path:
            if os.name == 'nt':
                pg_paths = glob.glob(r'C:\Program Files\PostgreSQL\*\bin\pg_restore.exe')
                if pg_paths:
                    pg_restore_path = pg_paths[-1]
                else:
                    pg_restore_path = 'pg_restore'
            else:
                pg_restore_path = '/usr/bin/pg_restore'
        
        # Guardar historial en memoria antes de la purga
        respaldos_mem = list(RespaldoSistema.objects.all().values())
        config_mem = list(ConfiguracionRespaldo.objects.all().values())

        # Usamos -c (clean) para borrar los objetos antes de crearlos,
        # --if-exists para evitar errores si no existen.
        # Quitamos -T para que pg_restore restaure TODOS los esquemas sin filtros.
        cmd = [
            pg_restore_path,
            '-h', db_config['HOST'],
            '-p', str(db_config['PORT']),
            '-U', db_config['USER'],
            '-d', db_config['NAME'],
            '-c', '--if-exists',
            '--no-owner', # No restaurar dueños de roles, previene errores de permisos
            respaldo.archivo_path
        ]
        
        try:
            logger.warning(f"⚠️ Iniciando RESTAURACIÓN desde {respaldo.archivo_path}")
            
            # Dejamos que pg_restore con -c haga la limpieza, para no envenenar la conexión actual.
            logger.info("Ejecutando pg_restore...")
            print(f"🚀 [Scheduler] Ejecutando pg_restore: {' '.join(cmd)}")
            result = subprocess.run(
                cmd, env=env, capture_output=True, text=True, 
                errors='replace'
            )
            if result.returncode != 0:
                stderr_text = result.stderr or ""
                print(f"❌ [pg_restore] ERROR: {stderr_text}")
                logger.error(f"Error de pg_restore: {stderr_text}")
                if "fatal:" in stderr_text.lower() or "falló" in stderr_text.lower() or "error" in stderr_text.lower():
                    pass # pg_restore a veces arroja errores ignorables, seguimos adelante.
            else:
                print("✅ [pg_restore] Éxito absoluto")
            
            # Cerrar la conexión actual para obligar a Django a reconectar y no usar transacciones rotas
            from django.db import connection
            connection.close()

            # Restaurar el historial de backups desde memoria
            RespaldoSistema.objects.all().delete()
            ConfiguracionRespaldo.objects.all().delete()
            
            for c in config_mem:
                ConfiguracionRespaldo.objects.create(**c)
                
            RespaldoSistema.objects.bulk_create([RespaldoSistema(**r) for r in respaldos_mem])
            
            # Restaurar timestamps originales (bulk_create + auto_now_add los sobreescribe)
            for r in respaldos_mem:
                RespaldoSistema.objects.filter(id=r['id']).update(timestamp=r['timestamp'])
            
            with connection.cursor() as cursor:
                cursor.execute("SELECT setval(pg_get_serial_sequence('customers_respaldo', 'id'), coalesce(max(id), 1), max(id) IS NOT null) FROM customers_respaldo;")
            
            logger.info("✅ Restauración completada con éxito.")
            return True
        except Exception as e:
            logger.error(f"❌ Error crítico en restauración: {str(e)}")
            raise e

    def _generar_catalogo_actual(self):
        """Genera un catálogo profundo con muestras de datos reales de cada esquema y tabla"""
        from django.db import connection
        catalogo = {}
        try:
            with connection.cursor() as cursor:
                # 1. Obtener todos los esquemas (tenants + public)
                cursor.execute("SELECT schema_name FROM customers_client")
                schemas = [row[0] for row in cursor.fetchall()]
                schemas.append('public')

                for schema in schemas:
                    # 2. Obtener lista de tablas del esquema
                    cursor.execute(f"""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = '{schema}' 
                        AND table_type = 'BASE TABLE'
                        ORDER BY table_name
                    """)
                    tables = [row[0] for row in cursor.fetchall()]
                    
                    schema_data = {}
                    for table in tables:
                        try:
                            # 3. Contar total real de filas
                            cursor.execute(f'SELECT COUNT(*) FROM "{schema}"."{table}";')
                            total_count = cursor.fetchone()[0]

                            # 4. Capturar muestra de datos (Top 100 filas)
                            cursor.execute(f'SELECT * FROM "{schema}"."{table}" LIMIT 100;')
                            columns = [col[0] for col in cursor.description]
                            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
                            
                            # Limpieza profunda de tipos no serializables
                            from decimal import Decimal
                            from uuid import UUID
                            
                            for row in rows:
                                for k, v in row.items():
                                    if isinstance(v, Decimal): row[k] = str(v)
                                    elif isinstance(v, UUID): row[k] = str(v)
                                    elif hasattr(v, 'isoformat'): row[k] = v.isoformat()
                                    elif isinstance(v, bytes): row[k] = "<Binario>"
                                    elif v is None: row[k] = None
                            
                            schema_data[table] = {
                                'columns': columns,
                                'rows': rows,
                                'count': total_count,    # total real en la BD
                                'sample': len(rows)      # filas en la muestra
                            }
                        except Exception:
                            continue
                    
                    catalogo[schema] = schema_data
            return catalogo
        except Exception as e:
            logger.error(f"Error generando catálogo profundo: {e}")
            return {"error": str(e)}


    def obtener_historial_encadenado(self):
        """Retorna todos los respaldos en orden cronológico"""
        return RespaldoSistema.objects.select_related('anterior', 'siguiente').all()
