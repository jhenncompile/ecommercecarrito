import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / 'backend'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.customers.models import Domain
print("--- DOMAINS IN DB ---")
for d in Domain.objects.all():
    print(f"ID={d.id} | Domain='{d.domain}' | Tenant='{d.tenant.schema_name}'")

