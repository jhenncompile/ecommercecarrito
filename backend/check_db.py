import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

c = connection.cursor()
c.execute("SELECT conname FROM pg_constraint WHERE conrelid = 'customers_rol'::regclass;")
print('Constraints:', [r[0] for r in c.fetchall()])

c.execute("SELECT indexname FROM pg_indexes WHERE tablename = 'customers_rol';")
print('Indexes:', [r[0] for r in c.fetchall()])
