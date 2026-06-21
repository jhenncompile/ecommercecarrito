import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'public') AND schema_name NOT LIKE 'pg_toast%';")
    schemas = [row[0] for row in cursor.fetchall()]
    print('TENANT SCHEMAS:', schemas)

    cursor.execute("SELECT COUNT(*) FROM customers_client;")
    print('CLIENT COUNT:', cursor.fetchone()[0])
