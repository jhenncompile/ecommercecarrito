import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.gestionDeReportes.cu21_generar_backup.services.respaldo_service import RespaldoService

try:
    s = RespaldoService()
    r = s.obtener_historial_encadenado().last()
    print('Restoring backup:', r.id, r.archivo_path)
    s.restaurar_respaldo(r.id)
    print('SUCCESS!')
except Exception as e:
    print('FAILED WITH EXCEPTION:', str(e))
    sys.exit(1)
