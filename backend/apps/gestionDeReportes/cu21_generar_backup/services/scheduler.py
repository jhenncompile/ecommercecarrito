from django.conf import settings
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.db.models.signals import post_save
from django.dispatch import receiver
import pytz
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(timezone=pytz.timezone(settings.TIME_ZONE) if hasattr(settings, 'TIME_ZONE') and settings.TIME_ZONE else pytz.utc)

def ejecutar_respaldo_automatico():
    from apps.gestionDeReportes.cu21_generar_backup.services.respaldo_service import RespaldoService
    from apps.gestionDeReportes.cu21_generar_backup.models.respaldo import ConfiguracionRespaldo
    from django.db import transaction, OperationalError
    
    print("🚀 [Scheduler] Intentando iniciar Respaldo Automático Programado...")
    logger.info("Intentando iniciar Respaldo Automático Programado...")
    try:
        with transaction.atomic():
            # Bloqueo atómico a nivel de fila (Postgres) para que solo un worker ejecute el respaldo a la vez
            config = ConfiguracionRespaldo.objects.select_for_update(nowait=True).first()
            if not config:
                print("⏭️ [Scheduler] No se encontró configuración.")
                return
                
            service = RespaldoService()
            service.crear_respaldo(nombre_base="Respaldo Automático")
            print("✅ [Scheduler] Respaldo Automático Exitoso")
            logger.info("✅ Respaldo Automático Exitoso")
    except OperationalError:
        logger.info("⏭️ Otro proceso ya está ejecutando el respaldo en este momento (Lock adquirido).")
    except Exception as e:
        logger.error(f"❌ Error en Respaldo Automático: {e}")

def actualizar_jobs_respaldo():
    """Lee la configuración de la BD y programa el job correspondiente"""
    from apps.gestionDeReportes.cu21_generar_backup.models.respaldo import ConfiguracionRespaldo
    
    # Remover el job anterior si existe
    if scheduler.get_job('job_respaldo'):
        scheduler.remove_job('job_respaldo')

    try:
        config = ConfiguracionRespaldo.objects.first()
        if not config or not config.activo:
            print("⏸️ [Scheduler] Respaldos automáticos desactivados.")
            logger.info("⏸️ Respaldos automáticos desactivados.")
            return

        hora = config.hora_ejecucion.hour
        minuto = config.hora_ejecucion.minute

        trigger = None
        if config.frecuencia == 'DIARIO':
            trigger = CronTrigger(hour=hora, minute=minuto)
        elif config.frecuencia == 'SEMANAL':
            trigger = CronTrigger(day_of_week=config.dia_referencia, hour=hora, minute=minuto)
        elif config.frecuencia == 'MENSUAL':
            trigger = CronTrigger(day=config.dia_referencia, hour=hora, minute=minuto)

        if trigger:
            scheduler.add_job(
                ejecutar_respaldo_automatico,
                trigger=trigger,
                id='job_respaldo',
                replace_existing=True
            )
            print(f"📅 [Scheduler] Respaldo Automático programado: {config.frecuencia} a las {config.hora_ejecucion}")
            logger.info(f"📅 Respaldo Automático programado: {config.frecuencia} a las {config.hora_ejecucion}")
    except Exception as e:
        print(f"❌ [Scheduler] Error al programar respaldos: {e}")
        logger.error(f"Error al programar respaldos: {e}")

def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        # Envolver en try-except por si la BD no está lista al arrancar
        try:
            actualizar_jobs_respaldo()
        except Exception:
            pass

@receiver(post_save, sender='cu21_generar_backup.ConfiguracionRespaldo')
def on_config_cambiada(sender, instance, **kwargs):
    logger.info("Configuracion de respaldo cambiada. Actualizando scheduler...")
    actualizar_jobs_respaldo()
