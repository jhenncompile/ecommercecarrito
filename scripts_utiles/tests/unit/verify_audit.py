import os
import sys
from pathlib import Path

# Configurar entorno Django
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / 'backend'
sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.customers.models import Bitacora
from django.db import connection

def verify_audit():
    print("\n" + "="*80)
    print(f"{'VERIFICACIÓN DE BITÁCORA (ÃšLTIMOS 10 REGISTROS)':^80}")
    print("="*80)
    
    # Obtener registros directamente via ORM (que sabe que es Shared Model)
    registros = Bitacora.objects.all().order_by('-fecha')[:10]
    
    if not registros.exists():
        print("\n[!] No se encontraron registros en la bitácora.")
        return

    print(f"{'ID':<5} | {'USUARIO':<25} | {'MÓDULO':<15} | {'ACCIÓN':<10} | {'FECHA'}")
    print("-" * 80)
    
    for r in registros:
        user_display = f"{r.idUsuario.email}" if r.idUsuario else "N/A"
        fecha_str = r.fecha.strftime("%Y-%m-%d %H:%M")
        print(f"{r.id:<5} | {user_display:<25} | {r.modulo:<15} | {r.accion:<10} | {fecha_str}")

    print("\n" + "="*80)
    print("[OK] Verificación completada.")

if __name__ == "__main__":
    verify_audit()

