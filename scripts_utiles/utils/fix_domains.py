import os
import sys
from pathlib import Path

# Configurar el entorno de Django
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = PROJECT_ROOT / 'backend'
sys.path.append(str(BACKEND_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    import django
    django.setup()
except ImportError:
    print("Error: No se pudo cargar Django. Asegúrate de estar en el entorno virtual.")
    sys.exit(1)

from django.conf import settings
from apps.customers.models import Domain

def fix_domains():
    suffix = getattr(settings, 'TENANT_DOMAIN_SUFFIX', '.localhost')
    print(f"Sincronizando dominios con el sufijo actual: {suffix}")
    
    domains = Domain.objects.all()
    updated_count = 0
    ignored_count = 0
    
    if not domains:
        print("No se encontraron dominios para actualizar.")
        return

    print("-" * 50)
    for domain_obj in domains:
        # Extraer el prefix (el primer segmento antes del primer punto)
        # Ejemplo: tienda1.localhost -> tienda1
        # Ejemplo: tienda1.157.173.102.129.nip.io -> tienda1
        current_domain = domain_obj.domain
        schema_prefix = current_domain.split('.')[0]
        
        # El dominio correcto debería ser prefix + suffix
        # Nota: el suffix ya incluye el punto inicial (ej: .nip.io)
        correct_domain = f"{schema_prefix}{suffix}"
        
        if current_domain != correct_domain:
            print(f"[CAMBIO] {current_domain} -> {correct_domain}")
            domain_obj.domain = correct_domain
            domain_obj.save()
            updated_count += 1
        else:
            print(f"[OK] {current_domain} ya está actualizado.")
            ignored_count += 1
            
    print("-" * 50)
    print(f"Sincronización terminada.")
    print(f"  - Actualizados: {updated_count}")
    print(f"  - Ya correctos: {ignored_count}")
    print(f"  - Total: {updated_count + ignored_count}")

if __name__ == '__main__':
    fix_domains()

