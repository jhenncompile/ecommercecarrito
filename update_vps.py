import os
import sys
from pathlib import Path

vps_path = Path('c:/Users/ldgd2/OneDrive/Documentos/Proyectos_lider/python/ecommerce/scripts_utiles/system/vps.py')
content = vps_path.read_text('utf-8')

new_code = '''
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

    print("\\n" + "="*50)
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
            
            sys.stdout.write(f"\\rCPU: {barra(cpu)} | RAM: {barra(ram.percent)} | DISCO: {barra(disk.percent)}")
            sys.stdout.flush()
    except KeyboardInterrupt:
        print("\\n[OK] Monitor detenido.")

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
"""
    with open("/etc/fail2ban/jail.local", "w") as f:
        f.write(jail_local)
    subprocess.run("systemctl restart fail2ban", shell=True)
    subprocess.run("systemctl enable fail2ban", shell=True)
    print("[OK] Fail2Ban configurado y activado para SSH.")

def advanced_ssl(domain, email):
    """Genera certificado SSL vía Certbot"""
    if not is_linux() or not is_root():
        print("[ERROR] Requiere Linux y permisos root.")
        return
    print(f"[+] Generando SSL para {domain}...")
    cmd = f"certbot certonly --standalone -d {domain} -m {email} --agree-tos --no-eff-email"
    subprocess.run(cmd, shell=True)
    print("[OK] SSL Configurado.")

def log_analyzer(service):
    """Visor de logs (tail)"""
    if not is_linux():
        print("[!] No disponible en Windows. Usa el visor de eventos.")
        return
    paths = {
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
'''

parts = content.split('# ========================================================================\n# FUNCIONES ORIGINALES (ACTUALIZADAS)')
if len(parts) == 2:
    new_content = parts[0] + new_code + '\n# ========================================================================\n# FUNCIONES ORIGINALES (ACTUALIZADAS)' + parts[1]
    
    new_content = new_content.replace('print("\\nADMINISTRACIÓN SAAS:")', 'print("\\nADMINISTRACIÓN SAAS:\\n  services MONITOR       - Monitor en tiempo real (CPU/RAM)\\n  security FAIL2BAN      - Instalar Fail2Ban\\n  logs ANALYZE [svc]     - Ver logs en vivo (django)\\n  ssl CREATE [dom] [em]  - Crear SSL avanzado")')
    
    main_patch = '''
    elif cmd == 'services' and len(sys.argv) > 2 and sys.argv[2] == 'MONITOR':
        resource_monitor()
    elif cmd == 'security' and len(sys.argv) > 2 and sys.argv[2] == 'FAIL2BAN':
        setup_fail2ban()
    elif cmd == 'ssl' and len(sys.argv) > 4 and sys.argv[2] == 'CREATE':
        advanced_ssl(sys.argv[3], sys.argv[4])
    elif cmd == 'logs' and len(sys.argv) > 3 and sys.argv[2] == 'ANALYZE':
        log_analyzer(sys.argv[3])
'''
    new_content = new_content.replace("    elif cmd == 'ssl':", main_patch + "    elif cmd == 'ssl':")
    vps_path.write_text(new_content, 'utf-8')
    print('vps.py updated')
else:
    print('Failed to split')
