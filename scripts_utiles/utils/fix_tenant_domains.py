#!/usr/bin/env python
# ========================================================================
# FIX TENANT DOMAINS
# ========================================================================
# Sanea los dominios existentes en la BD, reemplazando caracteres
# inválidos para DNS (guiones bajos) por 'x'.
#
# Ejemplo:   gerlex_tech777.157.173.102.129.nip.io
#         â†’  gerlextech777.157.173.102.129.nip.io
#
# Uso: python scripts_utiles/fix_tenant_domains.py
# ========================================================================

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = PROJECT_ROOT / 'backend'
sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django_tenants.utils import schema_context
from apps.customers.models import Domain


def sanitize(name: str) -> str:
    """Elimina caracteres inválidos para DNS reemplazándolos por 'x'."""
    return name.replace('_', 'x')


def fix_domains(dry_run: bool = False):
    """
    Busca todos los dominios con guiones bajos y los renombra.
    Si dry_run=True, solo muestra los cambios sin aplicarlos.
    """
    print("\n" + "=" * 70)
    print("  SANEADOR DE DOMINIOS DE TENANTS")
    print("=" * 70)

    with schema_context('public'):
        domains = Domain.objects.all()
        needs_fix = [(d, sanitize(d.domain)) for d in domains if '_' in d.domain]

        if not needs_fix:
            print("\n  [OK] No se encontraron dominios con caracteres invalidos.")
            return

        print(f"\n  Se encontraron {len(needs_fix)} dominio(s) con guion bajo:\n")
        for domain_obj, new_name in needs_fix:
            print(f"    {domain_obj.domain}")
            print(f"  â†’ {new_name}")
            print()

        if dry_run:
            print("  [i] Modo simulacion (dry-run). No se aplico ningun cambio.")
            return

        confirm = input("  Â¿Aplicar cambios? (s/n): ").strip().lower()
        if confirm != 's':
            print("  [!] Operacion cancelada.")
            return

        fixed = 0
        for domain_obj, new_name in needs_fix:
            old_name = domain_obj.domain
            domain_obj.domain = new_name
            domain_obj.save()
            print(f"  [OK] {old_name}  â†’  {new_name}")
            fixed += 1

        print(f"\n  [OK] {fixed} dominio(s) actualizado(s).")
        print("\n  [!] IMPORTANTE:")
        print("      - Los usuarios deben acceder por el nuevo subdominio.")
        print("      - Si tienes Nginx, el wildcard *.IP.nip.io sigue funcionando.")
        print("      - El schema_name en PostgreSQL NO cambia (no es necesario).")
        print()


if __name__ == '__main__':
    dry = '--dry-run' in sys.argv or '-n' in sys.argv
    fix_domains(dry_run=dry)

