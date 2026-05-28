import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

c = connection.cursor()
c.execute("SELECT conname, nspname FROM pg_constraint JOIN pg_namespace ON pg_namespace.oid = pg_constraint.connamespace WHERE conname = 'customers_rol_nombre_key';")
print('Orphan constraints:', c.fetchall())
