import os
import importlib
from pathlib import Path

# ========================================================================
# AUTO-DISCOVERY DE MODELOS PARA customers (Monolithic Migrations)
# ========================================================================
# Este script escanea dinámicamente todos los subdirectorios 'models' 
# dentro de 'apps/' (excluyendo 'apps/negocio' que está en refactorización).
# De esta manera, cada vez que creas un nuevo modelo, `makemigrations customers`
# lo detecta automáticamente sin que tengas que agregarlo a mano aquí.

apps_dir = Path(__file__).resolve().parent.parent.parent
backend_dir = apps_dir.parent

# Importamos primero los del propio customers para mantener la precedencia
from apps.customers.tenants.models.tenant import *
from apps.customers.tenants.models.plan import *
from apps.customers.tenants.models.suscripcion import *
from apps.customers.clientes.models.cliente import *
from apps.customers.models.mobile_release import *

# Escaneo dinámico para todos los demás modelos en gestionDe*
for root, dirs, files in os.walk(apps_dir):
    # Excluir 'negocio' para no chocar con la refactorización actual
    if 'negocio' in Path(root).parts:
        continue
        
    if os.path.basename(root) == 'models':
        for filename in files:
            if filename.endswith('.py') and filename != '__init__.py':
                rel_path = os.path.relpath(os.path.join(root, filename), backend_dir)
                module_path = rel_path.replace(os.sep, '.')[:-3]
                try:
                    module = importlib.import_module(module_path)
                    for name in dir(module):
                        # Evitar importar privados y re-importar módulos estándar
                        if not name.startswith('_') and name not in ['models', 'os']:
                            globals()[name] = getattr(module, name)
                except Exception as e:
                    print(f"[!] Autodiscovery info: No se pudo auto-importar {module_path} ({e})")