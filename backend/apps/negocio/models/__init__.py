import os
import importlib
from pathlib import Path

# =====================================================================
# AUTO-DISCOVERY DE MODELOS
# =====================================================================
# Este script busca dinámicamente cualquier archivo .py dentro de
# subdirectorios llamados "models/" dentro de "apps/negocio/" e importa
# todos sus modelos. De este modo, "makemigrations" y "migrate" siempre
# detectarán cualquier nuevo modelo de inmediato sin necesidad de
# importarlo manualmente aquí.

negocio_dir = Path(__file__).resolve().parent.parent
backend_dir = negocio_dir.parent.parent

for root, dirs, files in os.walk(negocio_dir):
    if os.path.basename(root) == 'models':
        for filename in files:
            if filename.endswith('.py') and filename != '__init__.py':
                rel_path = os.path.relpath(os.path.join(root, filename), backend_dir)
                module_path = rel_path.replace(os.sep, '.')[:-3]
                try:
                    module = importlib.import_module(module_path)
                    for name in dir(module):
                        if not name.startswith('_'):
                            globals()[name] = getattr(module, name)
                except Exception as e:
                    print(f"[!] Autodiscovery: Error al importar {module_path}: {e}")

