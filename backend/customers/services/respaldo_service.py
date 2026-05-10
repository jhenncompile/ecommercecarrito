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
        Crea un volcado de la base de datos, lo guarda en disco y
        actualiza la lista doblemente ligada de versiones.
        """
        # 1. Definir rutas (PROJECT_ROOT/backups)
        # PROJECT_ROOT está definido en settings_local como el padre de BASE_DIR
        project_root = getattr(settings, 'PROJECT_ROOT', settings.BASE_DIR.parent)
        backup_dir = os.path.join(project_root, 'backups')
        
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            
        now = timezone.now()
        timestamp_str = now.strftime('%Y%m%d_%H%M%S')
        fecha_display = now.strftime('%d/%m')
        
        filename = f"backup_{timestamp_str}.sql"
        full_path = os.path.join(backup_dir, filename)
        
        # 2. Obtener configuración de DB
        db_config = settings.DATABASES['default']
        # Usamos variables de entorno para evitar pasar pass en comando
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['PASSWORD']
        
        cmd = [
            'pg_dump',
            '-h', db_config['HOST'],
            '-p', str(db_config['PORT']),
            '-U', db_config['USER'],
            '-d', db_config['NAME'],
            '-f', full_path
        ]
        
        try:
            logger.info(f"🚀 Iniciando pg_dump en {full_path}")
            subprocess.run(cmd, env=env, check=True)
            
            # 3. Lógica de Punteros (Lista Doblemente Ligada)
            # Buscamos el respaldo que actualmente es el "último" (el que no tiene 'siguiente')
            ultimo_respaldo = RespaldoSistema.objects.filter(siguiente__isnull=True).order_by('-timestamp').first()
            
            nuevo_respaldo = RespaldoSistema.objects.create(
                nombre=f"{nombre_base}",
                archivo_path=full_path,
                anterior=ultimo_respaldo,
                metadata={
                    'size_bytes': os.path.getsize(full_path),
                    'timestamp_completo': timestamp_str,
                    'metodo': 'pg_dump'
                }
            )
            
            # Si había uno anterior, actualizamos su puntero 'siguiente'
            if ultimo_respaldo:
                ultimo_respaldo.siguiente = nuevo_respaldo
                ultimo_respaldo.save()
                logger.info(f"🔗 Enlazada versión {ultimo_respaldo.id} con la nueva {nuevo_respaldo.id}")
            
            logger.info(f"✅ Respaldo v.{fecha_display} creado exitosamente.")
            return nuevo_respaldo
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error en pg_dump: {e}")
            raise Exception("No se pudo ejecutar el volcado de base de datos. Verifique permisos de pg_dump.")
        except Exception as e:
            logger.error(f"❌ Error crítico en backup: {str(e)}")
            raise e

    def obtener_historial_encadenado(self):
        """Retorna todos los respaldos en orden cronológico"""
        return RespaldoSistema.objects.select_related('anterior', 'siguiente').all()
