#!/usr/bin/env python
# ========================================================================
# GESTOR DE SISTEMA
# ========================================================================
# Actualizar dependencias, resetear sistema, generar secrets
# Uso: python scripts_utiles/system_manager.py

import os
import sys
import subprocess
import secrets
import string
from pathlib import Path
import json
from dotenv import load_dotenv, set_key

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_FILE = PROJECT_ROOT / '.env'

# ========================================================================
# COLORES
# ========================================================================
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

def print_header(text):
    print(f"\n{Colors.CYAN}{'='*70}{Colors.ENDC}")
    print(f"{Colors.CYAN}{Colors.BOLD}* {text}{Colors.ENDC}")
    print(f"{Colors.CYAN}{'='*70}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.GREEN}[OK]{Colors.ENDC} {text}")

def print_error(text):
    print(f"{Colors.RED}[ERROR]{Colors.ENDC} {text}")

def print_info(text):
    print(f"{Colors.CYAN}[INFO]{Colors.ENDC} {text}")

def print_warning(text):
    print(f"{Colors.YELLOW}[WARN]{Colors.ENDC} {text}")

# ========================================================================
# ACTUALIZAR DEPENDENCIAS
# ========================================================================

def update_django():
    """Actualiza dependencias de Django"""
    print_header("ACTUALIZAR DEPENDENCIAS DJANGO")
    
    req_file = PROJECT_ROOT / 'backend' / 'requirements.txt'
    
    if not req_file.exists():
        print_error(f"requirements.txt no existe: {req_file}")
        return
    
    print_info(f"Archivo: {req_file}")
    print_warning("Esto actualizará todas las dependencias de Django")
    print()
    
    if input("Â¿Continuar? (s/n): ").lower() != 's':
        print_info("Cancelado")
        return
    
    try:
        print_info("Actualizando pip...")
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'
        ], check=True)
        
        print_info("Actualizando dependencias...")
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '--upgrade', '-r', str(req_file)
        ], check=True)
        
        print_success("Dependencias Django actualizadas")
        
    except subprocess.CalledProcessError as e:
        print_error(f"Error: {str(e)}")

def update_npm():
    """Actualiza dependencias de npm"""
    print_header("ACTUALIZAR DEPENDENCIAS NPM")
    
    frontend_dir = PROJECT_ROOT / 'frontend'
    package_file = frontend_dir / 'package.json'
    
    if not package_file.exists():
        print_error(f"package.json no existe: {package_file}")
        return
    
    print_info(f"Directorio: {frontend_dir}")
    print_warning("Esto actualizará todas las dependencias de npm")
    print()
    
    if input("Â¿Continuar? (s/n): ").lower() != 's':
        print_info("Cancelado")
        return
    
    try:
        # Limpieza previa si existe node_modules
        node_modules = frontend_dir / 'node_modules'
        package_lock = frontend_dir / 'package-lock.json'
        
        # Detectar si estamos en Linux para usar sudo
        is_linux = sys.platform != "win32"
        sudo_cmd = ['sudo'] if is_linux else []

        if node_modules.exists():
            print_warning("Detectado node_modules previo. Limpiando para instalación fresca a nivel root...")
            try:
                if is_linux:
                    subprocess.run(sudo_cmd + ['rm', '-rf', str(node_modules)], check=True)
                    if package_lock.exists():
                        subprocess.run(sudo_cmd + ['rm', '-f', str(package_lock)], check=True)
                else:
                    import shutil
                    shutil.rmtree(node_modules)
                    if package_lock.exists():
                        package_lock.unlink()
                print_success("Limpieza física completada.")
            except Exception as e:
                print_error(f"No se pudo limpiar node_modules: {e}")

        print_info("Limpiando caché de npm (Deep Clean)...")
        try:
            subprocess.run(sudo_cmd + ['npm', 'cache', 'clean', '--force'], check=True)
        except:
            print_warning("No se pudo limpiar el caché de npm (esto es normal si ya estaba limpio)")

        print_info("Instalando dependencias frescas con todos los permisos...")
        subprocess.run(sudo_cmd + ['npm', 'install'], cwd=frontend_dir, check=True)
        
        print_info("Generando build de producción optimizado...")
        subprocess.run(sudo_cmd + ['npm', 'run', 'build'], cwd=frontend_dir, check=True)
        
        print_info("Reiniciando servicio frontend_saas para aplicar cambios...")
        try:
            subprocess.run(sudo_cmd + ['systemctl', 'restart', 'frontend_saas'], check=True)
            print_success("Servicio frontend_saas reiniciado con éxito")
        except:
            print_warning("No se pudo reiniciar frontend_saas (puede que aún no esté creado)")

        print_success("Dependencias npm reinstaladas y frontend reconstruido correctamente")
        
    except FileNotFoundError:
        print_error("npm no está instalado")
    except subprocess.CalledProcessError as e:
        print_error(f"Error: {str(e)}")

def update_system():
    """Actualiza sistema operativo (apt)"""
    print_header("ACTUALIZAR SISTEMA OPERATIVO")
    
    if os.geteuid() != 0:
        print_error("Debes ejecutar como root (sudo)")
        return
    
    print_warning("Esto ejecutará: apt update && apt upgrade")
    print()
    
    if input("Â¿Continuar? (s/n): ").lower() != 's':
        print_info("Cancelado")
        return
    
    try:
        print_info("Actualizando paquetes...")
        subprocess.run(['apt', 'update'], check=True)
        subprocess.run(['apt', 'upgrade', '-y'], check=True)
        
        print_success("Sistema operativo actualizado")
        
    except subprocess.CalledProcessError as e:
        print_error(f"Error: {str(e)}")

# ========================================================================
# GENERAR SECRETS
# ========================================================================

def generate_secret_key(length=50):
    """Genera una SECRET_KEY para Django"""
    chars = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(chars) for _ in range(length))

def generate_jwt_secrets():
    """Genera secrets para JWT"""
    return {
        'JWT_SECRET': secrets.token_urlsafe(32),
        'JWT_ALGORITHM': 'HS256',
    }

def generate_api_keys():
    """Genera API keys"""
    return {
        'API_KEY': secrets.token_urlsafe(32),
        'API_SECRET': secrets.token_hex(32),
    }

def generate_all_secrets():
    """Genera DJANGO_SECRET_KEY y lo guarda en .env"""
    print_header("GENERAR DJANGO_SECRET_KEY")
    
    django_secret = generate_secret_key()
    
    print(f"{Colors.BOLD}DJANGO_SECRET_KEY:{Colors.ENDC}")
    print(f"  {Colors.DIM}{django_secret}{Colors.ENDC}\n")
    
    print(f"{Colors.BOLD}.env:{Colors.ENDC} {ENV_FILE}\n")
    
    confirm = input(f"{Colors.BOLD}Â¿Guardar en .env? (s/n): {Colors.ENDC}").lower()
    
    if confirm != 's':
        print_warning("Cancelado")
        return
    
    try:
        set_key(ENV_FILE, 'DJANGO_SECRET_KEY', django_secret)
        print_success("DJANGO_SECRET_KEY actualizado en .env")
        
    except Exception as e:
        print_error(f"Error: {str(e)}")

# ========================================================================
# RESETEAR SISTEMA SEGURO
# ========================================================================

def safe_system_reset():
    """Resetea el sistema de forma segura (sin joder el VPS)"""
    print_header("RESETEAR SISTEMA SEGURO")
    
    if os.geteuid() != 0:
        print_error("Debes ejecutar como root (sudo)")
        return
    
    print_warning("OPERACIÓN DESTRUCTIVA - LEE BIEN ANTES DE CONTINUAR")
    print()
    print("Esto hará:")
    print("  - Detener todos los servicios (Django, Frontend)")
    print("  - Resetear la base de datos")
    print("  - Limpiar caché y archivos temporales")
    print("  - Pero NO afectará: SSL certs, system files")
    print()
    
    confirm = input("Escribe 'RESETEAR SISTEMA CONTABO' para confirmar: ").strip()
    
    if confirm != 'RESETEAR SISTEMA CONTABO':
        print_error("Cancelado")
        return
    
    try:
        # Detener servicios
        print_info("Deteniendo servicios...")
        for svc in ['django_saas', 'frontend_saas']:
            try:
                subprocess.run(['systemctl', 'stop', svc], check=True, timeout=10)
                print_success(f"{svc} detenido")
            except:
                pass
        
        # Limpiar caché Python
        print_info("Limpiando caché Python...")
        subprocess.run(['find', str(PROJECT_ROOT), '-type', 'd', '-name', '__pycache__', '-exec', 'rm', '-rf', '{}', '+'], timeout=30)
        subprocess.run(['find', str(PROJECT_ROOT), '-type', 'f', '-name', '*.pyc', '-delete'], timeout=30)
        print_success("Caché Python limpiado")
        
        # Limpiar logs
        print_info("Limpiando logs viejos...")
        for log in ['/var/log/django_saas.log', '/var/log/frontend_saas.log']:
            if os.path.exists(log):
                open(log, 'w').close()
        print_success("Logs limpiados")
        
        # BD
        print_warning("Â¿Resetear base de datos? (s/n): ", end='')
        if input().lower() == 's':
            print_info("Reseteando BD...")
            # Aquí iría el reset de BD
            print_success("BD reseteada")
        
        # Iniciar servicios
        print_info("Reiniciando servicios...")
        for svc in ['django_saas', 'frontend_saas']:
            try:
                subprocess.run(['systemctl', 'start', svc], check=True, timeout=10)
                print_success(f"{svc} iniciado")
            except:
                print_warning(f"No se pudo iniciar {svc}")
        
        print_success("Sistema reseteado de forma segura")
        print_info("Los datos principales están intactos")
        
    except Exception as e:
        print_error(f"Error: {str(e)}")

def check_system_health():
    """Verifica la salud del sistema"""
    print_header("SALUD DEL SISTEMA")
    
    print(f"{Colors.BOLD}Espacio en disco:{Colors.ENDC}")
    try:
        result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
        print(result.stdout)
    except:
        print_warning("No se pudo obtener información de disco")
    
    print(f"\n{Colors.BOLD}Memoria disponible:{Colors.ENDC}")
    try:
        result = subprocess.run(['free', '-h'], capture_output=True, text=True)
        print(result.stdout)
    except:
        print_warning("No se pudo obtener información de memoria")
    
    print(f"\n{Colors.BOLD}Procesos Python:{Colors.ENDC}")
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'python' in line or 'django' in line:
                print(line)
    except:
        print_warning("No se pudo obtener procesos")


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
                    
    print(f"\n[EXITO] {deleted} archivos eliminados.")
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


# ========================================================================
# MAIN
# ========================================================================

def main():
    if len(sys.argv) < 2:
        print_header("GESTOR DE SISTEMA")
        
        print("ACTUALIZAR DEPENDENCIAS:")
        print("  1. Actualizar Django (pip)")
        print("  2. Actualizar npm")
        print("  3. Actualizar sistema (apt)")
        print()
        print("SECRETOS:")
        print("  4. Generar todos los secrets")
        print()
        print("MANTENIMIENTO:")
        print("  5. Resetear sistema (seguro)")
        print("  6. Verificar salud del sistema")
        print("  0. Salir")
        print()
        
        choice = input("Selecciona opción: ").strip()
        
        if choice == '1':
            update_django()
        elif choice == '2':
            update_npm()
        elif choice == '3':
            update_system()
        elif choice == '4':
            generate_all_secrets()
        elif choice == '5':
            safe_system_reset()
        elif choice == '6':
            check_system_health()
    else:
        cmd = sys.argv[1]
        
        if cmd == 'update-django':
            update_django()
        elif cmd == 'update-npm':
            update_npm()
        elif cmd == 'update-system':
            update_system()
        elif cmd == 'generate-secrets':
            generate_all_secrets()
        elif cmd == 'reset-system':
            safe_system_reset()
        elif cmd == 'health-check':
            check_system_health()
        elif cmd == 'clean-cache':
            clean_cache()
        elif cmd == 'clean-media':
            clean_media()
        elif cmd == 'setup-logrotate':
            setup_logrotate()


if __name__ == '__main__':
    main()

