import os
import sys
from pathlib import Path

manager_path = Path('c:/Users/ldgd2/OneDrive/Documentos/Proyectos_lider/python/ecommerce/scripts_utiles/system/system_manager.py')
content = manager_path.read_text('utf-8')

new_code = '''
# ========================================================================
# MANTENIMIENTO AVANZADO
# ========================================================================

def clean_cache():
    """Limpia caché de Django y archivos temporales"""
    print_header("LIMPIEZA DE CACHÉ")
    
    # Limpiar pycache y .pyc
    print_info("Eliminando archivos .pyc y __pycache__...")
    subprocess.run(['find', str(PROJECT_ROOT), '-type', 'd', '-name', '__pycache__', '-exec', 'rm', '-rf', '{}', '+'], stderr=subprocess.DEVNULL)
    subprocess.run(['find', str(PROJECT_ROOT), '-type', 'f', '-name', '*.pyc', '-delete'], stderr=subprocess.DEVNULL)
    
    # Limpiar caché de Django usando el helper de db (Django ORM)
    print_info("Purgando caché de Django (Redis/DB)...")
    if sys.platform != "win32":
        python_exe = str(PROJECT_ROOT / 'backend' / 'venv' / 'bin' / 'python')
    else:
        python_exe = str(PROJECT_ROOT / 'backend' / 'venv' / 'Scripts' / 'python.exe')
        
    manage_py = str(PROJECT_ROOT / 'backend' / 'manage.py')
    
    try:
        # Comando para borrar la caché usando shell (snippet)
        cmd = "from django.core.cache import cache; cache.clear(); print('Caché limpiada')"
        subprocess.run([python_exe, manage_py, "shell", "-c", cmd], check=True)
        print_success("Caché purgada exitosamente")
    except:
        print_warning("No se pudo purgar la caché de Django")

def clean_media():
    """Elimina imágenes en /media que no existen en la base de datos"""
    print_header("LIMPIEZA DE ARCHIVOS MEDIA (Imágenes Huérfanas)")
    
    if sys.platform != "win32":
        python_exe = str(PROJECT_ROOT / 'backend' / 'venv' / 'bin' / 'python')
    else:
        python_exe = str(PROJECT_ROOT / 'backend' / 'venv' / 'Scripts' / 'python.exe')
        
    script_helper = PROJECT_ROOT / 'scripts_utiles' / 'media_cleaner.py'
    
    if not script_helper.exists():
        with open(script_helper, 'w', encoding='utf-8') as f:
            f.write("""import os, sys
from pathlib import Path
import django

# Setup Django
sys.path.append(str(Path(__file__).resolve().parent.parent / 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from apps.customers.tenants.models.product import Producto

def run():
    media_root = Path(settings.MEDIA_ROOT)
    if not media_root.exists():
        print("La carpeta media no existe.")
        return

    # Obtener todas las rutas de imágenes en la BD
    db_images = set()
    for p in Producto.objects.all():
        if p.imagen:
            db_images.add(str(Path(p.imagen.path).resolve()))
            
    # Listar todos los archivos en media (excepto carpetas vacías)
    deleted = 0
    size_saved = 0
    
    print("[!] Buscando archivos huérfanos...")
    for root, dirs, files in os.walk(media_root):
        for file in files:
            file_path = Path(root) / file
            if str(file_path.resolve()) not in db_images:
                try:
                    size = file_path.stat().st_size
                    file_path.unlink()
                    deleted += 1
                    size_saved += size
                    print(f"  [X] Eliminado: {file}")
                except Exception as e:
                    pass
                    
    print(f"\\n[EXITO] {deleted} archivos eliminados.")
    print(f"[EXITO] {size_saved / (1024*1024):.2f} MB liberados.")

if __name__ == '__main__':
    run()
""")

    subprocess.run([python_exe, str(script_helper)])

def setup_logrotate():
    """Configura logrotate para Django"""
    print_header("INSTALACIÓN DE LOGROTATE")
    if sys.platform == "win32" or os.geteuid() != 0:
        print_error("Requiere Linux y permisos de root")
        return
        
    print_info("Creando configuración para Django en /etc/logrotate.d/saas")
    
    config = """/var/www/saas/backend/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload django_saas > /dev/null 2>/dev/null || true
    endscript
}
"""
    try:
        with open('/etc/logrotate.d/saas', 'w') as f:
            f.write(config)
        print_success("Logrotate configurado (14 días, compresión activada).")
    except Exception as e:
        print_error(f"Error: {e}")

'''

parts = content.split('# ========================================================================\n# MAIN')
if len(parts) == 2:
    new_content = parts[0] + new_code + '\n# ========================================================================\n# MAIN' + parts[1]
    
    main_patch = '''
        elif cmd == 'clean-cache':
            clean_cache()
        elif cmd == 'clean-media':
            clean_media()
        elif cmd == 'setup-logrotate':
            setup_logrotate()
'''
    new_content = new_content.replace("        elif cmd == 'health-check':\n            check_system_health()", "        elif cmd == 'health-check':\n            check_system_health()" + main_patch)
    manager_path.write_text(new_content, 'utf-8')
    print('system_manager.py updated')
else:
    print('Failed to split system_manager.py')
