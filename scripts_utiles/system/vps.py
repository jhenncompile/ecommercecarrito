import os
import sys
import subprocess
import platform
import zlib
import hashlib
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = PROJECT_ROOT / 'backend'
# Firma para el formato propietario (solo el sistema puede entenderlo)
MQHT_MAGIC = b"MQHT-V1-BIN"

def is_linux():
    """Verifica si es Linux/Unix"""
    return platform.system() in ['Linux', 'Darwin']

def is_root():
    """Verifica si corre como root"""
    if is_linux():
        return os.geteuid() == 0
    return False

# ========================================================================
# UTILIDADES DE SEGURIDAD Y LIMPIEZA
# ========================================================================

def check_firewall():
    """Verifica estado del firewall UFW y puertos SaaS"""
    print("\n" + "="*50)
    print("AUDITORÍA DE SEGURIDAD (FW)")
    print("="*50)
    
    if not is_linux():
        print("[!] No disponible en Windows")
        return

    try:
        result = subprocess.run("ufw status", shell=True, capture_output=True, text=True)
        print(result.stdout)
        
        puertos_criticos = ['80', '443', '8001', '3000']
        for p in puertos_criticos:
            if p in result.stdout:
                print(f"  [OK] Puerto {p} configurado")
            else:
                print(f"  [AVISO] Puerto {p} no detectado en UFW")
    except:
        print("[!] UFW no está instalado o activo")
    print("="*50 + "\n")

def system_clean():
    """Limpia archivos temporales y logs masivos"""
    print("[+] Iniciando limpieza de mantenimiento...")
    
    # Limpiar logs de nginx si son muy grandes
    if is_linux():
        try:
            subprocess.run("find /var/log/nginx/ -name '*.log' -size +100M -delete", shell=True)
            print("[OK] Logs de Nginx purgados (>100MB)")
        except: pass

    # Limpiar archivos .pyc y __pycache__
    try:
        subprocess.run(f"find {PROJECT_ROOT} -type d -name '__pycache__' -exec rm -rf {{}} +", shell=True)
        print("[OK] Caché de Python (__pycache__) eliminada")
    except: pass
    
    print("[Exito] Limpieza de sistema completada")

# ========================================================================
# AUTO-HEALING (AUTO-REPARACIÓN)
# ========================================================================

def auto_heal():
    """Escanea servicios y reinicia si están muertos"""
    print("[+] Ejecutando escaneo de Auto-Healing...")
    services = ['nginx', 'postgresql', 'django_saas', 'frontend_saas']
    
    if not is_linux():
        print("[!] Auto-heal solo disponible en Linux")
        return

    healed = 0
    for svc in services:
        result = subprocess.run(f"systemctl is-active {svc}", shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[AVISO] {svc} está CAÍDO. Intentando reanimación...")
            subprocess.run(f"systemctl restart {svc}", shell=True)
            healed += 1
    
    if healed == 0:
        print("[OK] Todos los servicios están saludables")
    else:
        print(f"[Hecho] Se han reanimado {healed} servicios")

# ========================================================================
# RESPALDOS INTERNOS (FORMATO PROPIETARIO)
# ========================================================================

def backup_internal(name="Manual"):
    """
    Crea un snapshot de la base de datos, lo comprime y lo 
    guarda en el formato binario propietario MQHT dentro de la propia DB.
    """
    print(f"[+] Iniciando Snapshot Interno (Formato Propietario MQHT)...")
    
    # Este comando se apoya en un script Django para la persistencia
    if is_linux():
        python_exe = str(BACKEND_DIR / 'venv' / 'bin' / 'python')
    else:
        python_exe = str(BACKEND_DIR / 'venv' / 'Scripts' / 'python.exe')
    
    # Script auxiliar para manejar el blob
    script_helper = PROJECT_ROOT / 'scripts_utiles' / 'internal_backup_helper.py'
    
    if not script_helper.exists():
        # Crear el helper si no existe
        with open(script_helper, 'w', encoding='utf-8') as f:
            f.write("""
import os, sys, zlib, hashlib
from pathlib import Path
import django
from datetime import datetime

# Setup Django
sys.path.append(str(Path(__file__).resolve().parent.parent.parent / 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.customers.models import RespaldoSistema
from django.conf import settings
import subprocess

def run():
    target = sys.argv[1] if len(sys.argv) > 1 else "SNAPSHOT"
    
    if target == "LIST_AND_RESTORE":
        backups = RespaldoSistema.objects.all()[:10]
        if not backups:
            print("No hay snapshots guardados en la base de datos.")
            return

        print("\\n--- SNAPSHOTS DISPONIBLES EN BD ---")
        for i, b in enumerate(backups):
            print(f"{i+1}. {b.nombre} ({b.timestamp.strftime('%Y-%m-%d %H:%M')}) - {b.size_mb} MB")
        
        try:
            choice = int(input("\\nSelecciona el ID para RESTAURAR (0 para cancelar): "))
            if choice == 0: return
            res = backups[choice-1]
            
            print(f"\\n[!] RESTAURANDO SNAPSHOT: {res.nombre}...")
            blob = res.blob_data
            MAGIC = b"MQHT-V1-BIN"
            
            if not blob.startswith(MAGIC):
                print("Error: Formato de snapshot inválido")
                return
            
            # Extraer checksum y datos
            parts = blob[len(MAGIC):].split(b"||", 1)
            checksum = parts[0].decode()
            compressed = parts[1]
            
            # Verificar integridad
            if hashlib.sha256(compressed).hexdigest() != checksum:
                print("Error: El snapshot está corrupto (checksum mismatch)")
                return
            
            sql_data = zlib.decompress(compressed)
            
            # Aplicar SQL
            db_conf = settings.DATABASES['default']
            env = os.environ.copy()
            if db_conf['PASSWORD']: env['PGPASSWORD'] = db_conf['PASSWORD']
            
            print("Importando datos...")
            proc = subprocess.Popen(['psql', '-U', db_conf['USER'], '-h', db_conf['HOST'], db_conf['NAME']], 
                                   stdin=subprocess.PIPE, env=env)
            proc.communicate(input=sql_data)
            print("\\n[EXITO] Sistema restaurado al estado del snapshot.")
            
        except FileNotFoundError:
            print("\\n❌ ERROR: El comando 'psql' no está instalado o no se encuentra en el PATH del sistema.")
            if os.name == 'nt':
                print("👉 Por favor, instala PostgreSQL y asegúrate de añadir la carpeta 'bin' (ej. C:\\\\Program Files\\\\PostgreSQL\\\\16\\\\bin) a las Variables de Entorno del Sistema (PATH).")
            else:
                print("👉 Por favor, instala 'postgresql-client' en tu sistema (ej: sudo apt install postgresql-client).")
        except Exception as e:
            print(f"Error en restauración: {e}")
            
    else:
        nombre = target
        db_conf = settings.DATABASES['default']
        print(f"Exportando Snapshot: {nombre}...")
        
        try:
            env = os.environ.copy()
            if db_conf['PASSWORD']: env['PGPASSWORD'] = db_conf['PASSWORD']
                
            cmd = ['pg_dump', '-U', db_conf['USER'], '-h', db_conf['HOST'], db_conf['NAME']]
            result = subprocess.run(cmd, env=env, capture_output=True, check=True)
            sql_data = result.stdout
            
            # Formato Propietario MQHT-V1
            MAGIC = b"MQHT-V1-BIN"
            compressed = zlib.compress(sql_data)
            checksum = hashlib.sha256(compressed).hexdigest()
            blob = MAGIC + checksum.encode() + b"||" + compressed
            
            RespaldoSistema.objects.create(
                nombre=nombre,
                blob_data=blob,
                metadata={
                    "source": "vps_tool", 
                    "raw_size": len(sql_data),
                    "checksum": checksum
                }
            )
            print(f"SNAPSHOT GUARDADO EXITOSAMENTE: {nombre}")
        except FileNotFoundError:
            print("\\n❌ ERROR: El comando 'pg_dump' no está instalado o no se encuentra en el PATH del sistema.")
            if os.name == 'nt':
                print("👉 Por favor, instala PostgreSQL y asegúrate de añadir la carpeta 'bin' (ej. C:\\\\Program Files\\\\PostgreSQL\\\\16\\\\bin) a las Variables de Entorno del Sistema (PATH).")
            else:
                print("👉 Por favor, instala 'postgresql-client' en tu sistema (ej: sudo apt install postgresql-client).")
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == '__main__':
    run()
""")

    subprocess.run([python_exe, str(script_helper), name])

def restore_internal():
    """Muestra lista de snapshots y restaura uno"""
    # Llama al helper con comando restore
    if is_linux():
        python_exe = str(BACKEND_DIR / 'venv' / 'bin' / 'python')
    else:
        python_exe = str(BACKEND_DIR / 'venv' / 'Scripts' / 'python.exe')
    
    script_helper = PROJECT_ROOT / 'scripts_utiles' / 'internal_backup_helper.py'
    
    # Añadir lógica de restore al helper (proyectado)
    print("[!] Listando snapshots disponibles en la base de datos...")
    # Por ahora ejecutamos el script con flag restore
    subprocess.run([python_exe, str(script_helper), "LIST_AND_RESTORE"])


# ========================================================================
# NUEVAS HERRAMIENTAS AVANZADAS
# ========================================================================

def resource_monitor():
    """Monitor de recursos en tiempo real"""
    import time
    try:
        import psutil
    except ImportError:
        print("[!] psutil no instalado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "psutil"])
        import psutil

    print("\n" + "="*50)
    print("MONITOR DE RECURSOS EN TIEMPO REAL (Ctrl+C para salir)")
    print("="*50)
    try:
        while True:
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Formato de barra
            def barra(percent):
                filled = int(percent / 5)
                return "[" + "#"*filled + "-"*(20-filled) + f"] {percent}%"
            
            sys.stdout.write(f"\rCPU: {barra(cpu)} | RAM: {barra(ram.percent)} | DISCO: {barra(disk.percent)}")
            sys.stdout.flush()
    except KeyboardInterrupt:
        print("\n[OK] Monitor detenido.")

def setup_fail2ban():
    """Instala y configura Fail2Ban en Linux"""
    if not is_linux() or not is_root():
        print("[ERROR] Requiere Linux y permisos root.")
        return
    print("[+] Instalando fail2ban...")
    subprocess.run("apt-get update && apt-get install -y fail2ban", shell=True)
    jail_local = """
[DEFAULT]
bantime  = 3600
findtime  = 600
maxretry = 5

[sshd]
enabled = true

[nginx-http-auth]
enabled = true
"""
    with open("/etc/fail2ban/jail.local", "w") as f:
        f.write(jail_local)
    subprocess.run("systemctl restart fail2ban", shell=True)
    subprocess.run("systemctl enable fail2ban", shell=True)
    print("[OK] Fail2Ban configurado y activado para SSH y Nginx.")

def advanced_ssl(domain, email):
    """Genera certificado SSL vía Certbot"""
    if not is_linux() or not is_root():
        print("[ERROR] Requiere Linux y permisos root.")
        return
    print(f"[+] Generando SSL para {domain}...")
    cmd = f"certbot --nginx -d {domain} -m {email} --agree-tos --no-eff-email --redirect"
    subprocess.run(cmd, shell=True)
    print("[OK] SSL Configurado.")

def log_analyzer(service):
    """Visor de logs (tail)"""
    if not is_linux():
        print("[!] No disponible en Windows. Usa el visor de eventos.")
        return
    paths = {
        'nginx': '/var/log/nginx/error.log',
        'django': '/var/www/saas/backend/logs/django.log',
        'syslog': '/var/log/syslog'
    }
    path = paths.get(service, '')
    if not path or not os.path.exists(path):
        print(f"[!] Log no encontrado para: {service}")
        return
    print(f"[+] Mostrando logs de {service} (Ctrl+C para salir)...")
    try:
        subprocess.run(f"tail -f {path}", shell=True)
    except KeyboardInterrupt:
        pass

# ========================================================================
# FUNCIONES ORIGINALES (ACTUALIZADAS)
# ========================================================================

def create_user(username, password, home_dir=None):
    if not is_linux() or not is_root():
        print("[ERROR] Requiere Linux y permisos root")
        return False
    
    print(f"[+] Creando usuario: {username}")
    cmd = f"useradd -s /bin/bash -m {username}"
    if home_dir: cmd = f"useradd -d {home_dir} -s /bin/bash -m {username}"
    
    if subprocess.run(cmd, shell=True).returncode == 0:
        subprocess.run(f"echo '{username}:{password}' | chpasswd", shell=True)
        print(f"[OK] Usuario {username} configurado")
        return True
    return False

def check_services():
    services = ['nginx', 'postgresql', 'django_saas', 'frontend_saas']
    print("\n" + "="*50)
    print("ESTADO DE SERVICIOS")
    print("="*50)
    for svc in services:
        if is_linux():
            res = subprocess.run(f"systemctl is-active {svc}", shell=True, capture_output=True, text=True)
            status = "âœ“ ACTIVO" if res.returncode == 0 else "âœ— INACTIVO"
        else:
            status = "? (Windows)"
        print(f"  {svc:<20} {status}")
    print("="*50 + "\n")

def main():
    if len(sys.argv) < 2:
        print("Uso: python vps.py [comando]")
        print("\nADMINISTRACIÓN SAAS:\n  services MONITOR       - Monitor en tiempo real (CPU/RAM)\n  security FAIL2BAN      - Instalar Fail2Ban\n  logs ANALYZE [svc]     - Ver logs en vivo (nginx/django)\n  ssl CREATE [dom] [em]  - Crear SSL avanzado")
        print("  services STATUS        - Ver salud de servicios")
        print("  services AUTOHEAL      - Reanimar servicios caídos")
        print("  security FW            - Auditoría de Firewall")
        print("  system CLEAN           - Limpieza de logs y temporales")
        print("\nRESPALDOS (BASE DE DATOS):")
        print("  backup SNAPSHOT [name] - Crear Snapshot INTERNO (Proprietary MQHT)")
        print("  backup RESTORE         - Listar y restaurar Snapshots")
        print("\nCONFIGURACIÓN VPS:")
        print("  user CREATE user pass  - Crear usuario del sistema")
        print("  ssl RENEW              - Probar renovación SSL")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'services':
        sub = sys.argv[2] if len(sys.argv) > 2 else 'STATUS'
        if sub == 'STATUS': check_services()
        elif sub == 'AUTOHEAL': auto_heal()
    
    elif cmd == 'security':
        if sys.argv[2] == 'FW': check_firewall()
    
    elif cmd == 'system':
        if sys.argv[2] == 'CLEAN': system_clean()
    
    elif cmd == 'backup':
        sub = sys.argv[2]
        if sub == 'SNAPSHOT':
            name = sys.argv[3] if len(sys.argv) > 3 else "Autosave"
            backup_internal(name)
        elif sub == 'RESTORE':
            restore_internal()
            
    elif cmd == 'user' and len(sys.argv) >= 5:
        if sys.argv[2] == 'CREATE': create_user(sys.argv[3], sys.argv[4])
        

    elif cmd == 'services' and len(sys.argv) > 2 and sys.argv[2] == 'MONITOR':
        resource_monitor()
    elif cmd == 'security' and len(sys.argv) > 2 and sys.argv[2] == 'FAIL2BAN':
        setup_fail2ban()
    elif cmd == 'ssl' and len(sys.argv) > 4 and sys.argv[2] == 'CREATE':
        advanced_ssl(sys.argv[3], sys.argv[4])
    elif cmd == 'logs' and len(sys.argv) > 3 and sys.argv[2] == 'ANALYZE':
        log_analyzer(sys.argv[3])
    elif cmd == 'ssl':
        if sys.argv[2] == 'RENEW':
             if is_linux(): subprocess.run("certbot renew --dry-run", shell=True)
             else: print("[!] No disponible")

if __name__ == '__main__':
    main()

