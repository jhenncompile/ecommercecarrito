import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.gestionDeReportes.cu21_generar_backup.services.respaldo_service import RespaldoService
import subprocess
s = RespaldoService()
r = s.obtener_historial_encadenado().last()

db_config = django.conf.settings.DATABASES['default']
import glob
pg_paths = glob.glob(r'C:\Program Files\PostgreSQL\*\bin\pg_restore.exe')
pg_restore_path = pg_paths[-1] if pg_paths else 'pg_restore'
os.environ['PGPASSWORD'] = db_config['PASSWORD']

cmd = [
    pg_restore_path,
    '-h', db_config['HOST'] or 'localhost',
    '-p', str(db_config['PORT']) or '5432',
    '-U', db_config['USER'],
    '-d', db_config['NAME'],
    '-c', '--if-exists',
    '--no-owner',
    '-T', 'customers_respaldo', 
    '-T', 'customers_configuracion_respaldo',
    r.archivo_path
]

print("Running command:", " ".join(cmd))
res = subprocess.run(cmd, capture_output=True, text=True, errors='replace')
print("RETURN CODE:", res.returncode)
print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)
