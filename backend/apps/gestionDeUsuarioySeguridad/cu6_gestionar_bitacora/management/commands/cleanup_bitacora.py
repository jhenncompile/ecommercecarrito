from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from apps.gestionDeUsuarioySeguridad.cu6_gestionar_bitacora.models.bitacora import Bitacora
from datetime import timedelta

class Command(BaseCommand):
    help = 'Elimina registros de bitácora antiguos según el periodo de retención configurado.'

    def handle(self, *args, **options):
        retention_days = getattr(settings, 'AUDIT_LOG_RETENTION_DAYS', 90)
        cutoff_date = timezone.now() - timedelta(days=retention_days)
        
        old_logs = Bitacora.objects.filter(fecha__lt=cutoff_date)
        count = old_logs.count()
        
        if count > 0:
            old_logs.delete()
            self.stdout.write(self.style.SUCCESS(f'Se eliminaron {count} registros de bitácora anteriores a {cutoff_date}.'))
        else:
            self.stdout.write(self.style.SUCCESS('No se encontraron registros antiguos para eliminar.'))
