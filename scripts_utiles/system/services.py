#!/usr/bin/env python
# ========================================================================
# CONFIGURADOR DE NGINX Y SERVICIOS
# ========================================================================
# Gestión de Nginx, servicios systemd, y logs
# Lee configuración de .env y crea servicios systemd
# Uso: python scripts_utiles/nginx_config.py

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_FILE = PROJECT_ROOT / '.env'

# Cargar .env
load_dotenv(ENV_FILE)

# ========================================================================
# COLORES Y ESTILOS
# ========================================================================
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

def print_header(text):
    print(f"\n{Colors.CYAN}{'='*70}{Colors.ENDC}")
    print(f"{Colors.CYAN}{Colors.BOLD}âœ¦ {text}{Colors.ENDC}")
    print(f"{Colors.CYAN}{'='*70}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.GREEN}âœ“{Colors.ENDC} {text}")

def print_error(text):
    print(f"{Colors.RED}âœ—{Colors.ENDC} {text}")

def print_info(text):
    print(f"{Colors.BLUE}â„¹{Colors.ENDC} {text}")

def print_warning(text):
    print(f"{Colors.YELLOW}âš {Colors.ENDC} {text}")

# ========================================================================
# CARGAR CONFIGURACIÓN DE .ENV
# ========================================================================

def get_env_config():
    """Obtiene configuración de .env"""
    config = {
        'DJANGO_PORT': os.getenv('DJANGO_PORT', '8001'),
        'REACT_PORT': os.getenv('REACT_PORT', '3000'),
        'ENVIRONMENT': os.getenv('ENVIRONMENT', 'development'),
        'DOMAIN_MAIN': os.getenv('DOMAIN_MAIN', 'localhost'),
        'DATABASE_HOST': os.getenv('DATABASE_HOST', '127.0.0.1'),
        'DATABASE_PORT': os.getenv('DATABASE_PORT', '5432'),
        'DATABASE_NAME': os.getenv('DATABASE_NAME', 'mi_saas_db'),
        'DATABASE_USER': os.getenv('DATABASE_USER', 'postgres'),
    }
    return config

def show_env_config():
    """Muestra la configuración del .env"""
    print_header("CONFIGURACIÓN DESDE .env")
    
    config = get_env_config()
    
    print(f"{Colors.BOLD}Servicios:{Colors.ENDC}")
    print(f"  Django Port:    {Colors.YELLOW}{config['DJANGO_PORT']}{Colors.ENDC}")
    print(f"  React Port:     {Colors.YELLOW}{config['REACT_PORT']}{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Ambiente:{Colors.ENDC}")
    print(f"  Environment:    {Colors.CYAN}{config['ENVIRONMENT']}{Colors.ENDC}")
    print(f"  Domain:         {Colors.CYAN}{config['DOMAIN_MAIN']}{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Base de Datos:{Colors.ENDC}")
    print(f"  Host:           {Colors.CYAN}{config['DATABASE_HOST']}{Colors.ENDC}")
    print(f"  Port:           {Colors.CYAN}{config['DATABASE_PORT']}{Colors.ENDC}")
    print(f"  Database:       {Colors.CYAN}{config['DATABASE_NAME']}{Colors.ENDC}")
    print(f"  User:           {Colors.CYAN}{config['DATABASE_USER']}{Colors.ENDC}")
    print()

# ========================================================================
# CREAR SERVICIOS
# ========================================================================

def service_exists(service_name):
    """Verifica si un servicio ya existe"""
    result = subprocess.run(['systemctl', 'list-unit-files', service_name + '.service'], 
                          capture_output=True, text=True)
    return service_name in result.stdout

def create_django_service():
    """Crea servicio systemd para Django"""
    print_header("CREAR SERVICIO DJANGO")
    
    if os.geteuid() != 0:
        print_error("Debes ejecutar como root (sudo)")
        return
    
    config = get_env_config()
    show_env_config()
    
    project_path = str(PROJECT_ROOT)
    
    # Detectar el usuario correcto basado en la ruta (www-data no puede acceder a /root)
    default_user = "root" if project_path.startswith('/root/') else "www-data"
    user_input = input(f"{Colors.BOLD}Usuario que correrá el servicio (default: {default_user}): {Colors.ENDC}").strip()
    run_user = user_input if user_input else default_user
    
    print(f"\n{Colors.BOLD}Servicio a crear:{Colors.ENDC}")
    print(f"  Nombre:         {Colors.YELLOW}django_saas{Colors.ENDC}")
    print(f"  Puerto:         {Colors.YELLOW}{config['DJANGO_PORT']}{Colors.ENDC}")
    print(f"  Usuario:        {Colors.YELLOW}{run_user}{Colors.ENDC}")
    print()
    
    service_name = "django_saas"
    service_file = f"/etc/systemd/system/{service_name}.service"
    
    confirm = input(f"{Colors.BOLD}Â¿Crear/Reemplazar servicio? (s/n): {Colors.ENDC}").lower()
    
    if confirm != 's':
        print_warning("Cancelado")
        return
    
    django_port = config['DJANGO_PORT']
    
    service_content = f"""[Unit]
Description=Django SaaS Application
After=network.target postgresql.service

[Service]
Type=simple
User={run_user}
Group={run_user}
WorkingDirectory={project_path}/backend
Environment="PATH={project_path}/backend/venv/bin"
ExecStart={project_path}/backend/venv/bin/python manage.py runserver 0.0.0.0:{django_port}
Restart=on-failure
RestartSec=5s
StandardOutput=append:/var/log/django_saas.log
StandardError=append:/var/log/django_saas_error.log

[Install]
WantedBy=multi-user.target
"""
    
    try:
        # Detener servicio si existe
        if service_exists(service_name):
            print_info(f"Deteniendo servicio existente {service_name}...")
            subprocess.run(['systemctl', 'stop', service_name], timeout=10)
        
        # Crear/reemplazar archivo
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        # Reload systemctl
        subprocess.run(['systemctl', 'daemon-reload'], check=True)
        print_success(f"Servicio creado/reemplazado: {service_file}")
        
        if input(f"\n{Colors.BOLD}Â¿Habilitar al iniciar? (s/n): {Colors.ENDC}").lower() == 's':
            subprocess.run(['systemctl', 'enable', service_name], check=True)
            print_success(f"{service_name} habilitado al inicio")
        
        if input(f"{Colors.BOLD}Â¿Iniciar servicio ahora? (s/n): {Colors.ENDC}").lower() == 's':
            subprocess.run(['systemctl', 'start', service_name], check=True)
            print_success(f"{service_name} iniciado")
            
    except Exception as e:
        print_error(f"Error: {str(e)}")

def create_frontend_service():
    """Crea servicio systemd para Frontend (React)"""
    print_header("CREAR SERVICIO FRONTEND (REACT)")
    
    if os.geteuid() != 0:
        print_error("Debes ejecutar como root (sudo)")
        return
    
    config = get_env_config()
    show_env_config()
    
    project_path = str(PROJECT_ROOT)
    
    # Detectar el usuario correcto basado en la ruta
    default_user = "root" if project_path.startswith('/root/') else "www-data"
    user_input = input(f"{Colors.BOLD}Usuario que correrá el servicio (default: {default_user}): {Colors.ENDC}").strip()
    run_user = user_input if user_input else default_user
    
    print(f"\n{Colors.BOLD}Servicio a crear:{Colors.ENDC}")
    print(f"  Nombre:         {Colors.YELLOW}frontend_saas{Colors.ENDC}")
    print(f"  Puerto:         {Colors.YELLOW}{config['REACT_PORT']}{Colors.ENDC}")
    print(f"  Usuario:        {Colors.YELLOW}{run_user}{Colors.ENDC}")
    print()
    
    service_name = "frontend_saas"
    service_file = f"/etc/systemd/system/{service_name}.service"
    
    confirm = input(f"{Colors.BOLD}Â¿Crear/Reemplazar servicio? (s/n): {Colors.ENDC}").lower()
    
    if confirm != 's':
        print_warning("Cancelado")
        return
    
    react_port = config['REACT_PORT']
    
    service_content = f"""[Unit]
Description=React Frontend SaaS
After=network.target

[Service]
Type=simple
User={run_user}
Group={run_user}
WorkingDirectory={project_path}/frontend
Environment="PATH={project_path}/frontend/node_modules/.bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin"
Environment="PORT={react_port}"
Environment="HOST=0.0.0.0"
ExecStart=/usr/bin/npx serve -s build -l {react_port}
Restart=on-failure
RestartSec=5s
StandardOutput=append:/var/log/frontend_saas.log
StandardError=append:/var/log/frontend_saas_error.log

[Install]
WantedBy=multi-user.target
"""
    
    try:
        # Detener servicio si existe
        if service_exists(service_name):
            print_info(f"Deteniendo servicio existente {service_name}...")
            subprocess.run(['systemctl', 'stop', service_name], timeout=10)
        
        # Limpiar procesos en puerto (Evita bloqueos de npm start manuales)
        print_info(f"Limpiando puerto {react_port} para evitar bloqueos de procesos huérfanos...")
        try:
            subprocess.run(['sudo', 'fuser', '-k', f'{react_port}/tcp'], capture_output=True)
        except:
            pass
        
        # Crear/reemplazar archivo
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        # Reload systemctl
        subprocess.run(['systemctl', 'daemon-reload'], check=True)
        print_success(f"Servicio creado/reemplazado: {service_file}")
        
        if input(f"\n{Colors.BOLD}Â¿Habilitar al iniciar? (s/n): {Colors.ENDC}").lower() == 's':
            subprocess.run(['systemctl', 'enable', service_name], check=True)
            print_success(f"{service_name} habilitado al inicio")
        
        if input(f"{Colors.BOLD}Â¿Iniciar servicio ahora? (s/n): {Colors.ENDC}").lower() == 's':
            subprocess.run(['systemctl', 'start', service_name], check=True)
            print_success(f"{service_name} iniciado")
            
    except Exception as e:
        print_error(f"Error: {str(e)}")

def delete_service():
    """Elimina un servicio systemd"""
    print_header("ELIMINAR SERVICIO")
    
    if os.geteuid() != 0:
        print_error("Debes ejecutar como root (sudo)")
        return
    
    print("1. Eliminar Django service (django_saas)")
    print("2. Eliminar Frontend service (frontend_saas)")
    print("0. Cancelar")
    print()
    
    choice = input("Selecciona: ").strip()
    
    services = {
        '1': 'django_saas',
        '2': 'frontend_saas',
    }
    
    if choice not in services:
        print_warning("Cancelado")
        return
    
    service_name = services[choice]
    service_file = f"/etc/systemd/system/{service_name}.service"
    
    confirm = input(f"\n{Colors.RED}Â¿ELIMINAR {service_name}? (s/n): {Colors.ENDC}").lower()
    
    if confirm != 's':
        print_warning("Cancelado")
        return
    
    try:
        # Detener servicio
        print_info(f"Deteniendo {service_name}...")
        subprocess.run(['systemctl', 'stop', service_name], timeout=10)
        
        # Desabilitar
        subprocess.run(['systemctl', 'disable', service_name], timeout=10)
        
        # Eliminar archivo
        os.remove(service_file)
        
        # Reload systemctl
        subprocess.run(['systemctl', 'daemon-reload'], check=True)
        
        print_success(f"Servicio {service_name} eliminado")
        
    except Exception as e:
        print_error(f"Error: {str(e)}")

def view_service_status():
    """Ver estado de los servicios"""
    print_header("ESTADO DE SERVICIOS")
    
    services = ['django_saas', 'frontend_saas', 'postgresql']
    
    for service in services:
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', service],
                capture_output=True,
                text=True,
                timeout=2
            )
            status = result.stdout.strip()
            
            if status == 'active':
                print(f"{Colors.GREEN}✓{Colors.ENDC} {service:<20} {Colors.GREEN}ACTIVO{Colors.ENDC}")
            else:
                print(f"{Colors.RED}✗{Colors.ENDC} {service:<20} {Colors.RED}{status.upper()}{Colors.ENDC}")
        except subprocess.TimeoutExpired:
            print(f"{Colors.YELLOW}⚠{Colors.ENDC} {service:<20} {Colors.YELLOW}TIMEOUT{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.YELLOW}?{Colors.ENDC} {service:<20} No disponible")
    
    print()

def view_logs():
    """Ver logs de servicios"""
    print_header("VER LOGS")
    
    print("1. Django logs")
    print("2. Frontend logs")
    print("3. PostgreSQL logs")
    print()
    
    choice = input("Selecciona log a ver: ").strip()
    
    logs = {
        '1': '/var/log/django_saas.log',
        '2': '/var/log/frontend_saas.log',
        '3': '/var/log/postgresql/postgresql.log',
    }
    
    if choice in logs:
        log_file = logs[choice]
        
        if os.path.exists(log_file):
            print(f"\n{Colors.CYAN}Últimas 50 líneas de {log_file}:{Colors.ENDC}\n")
            
            try:
                result = subprocess.run(
                    ['tail', '-50', log_file],
                    capture_output=True,
                    text=True
                )
                print(result.stdout)
            except Exception as e:
                print_error(f"Error al leer log: {str(e)}")
        else:
            print_warning(f"Log no existe: {log_file}")
    else:
        print_error("Opción inválida")

def restart_service():
    """Reinicia un servicio"""
    print_header("REINICIAR SERVICIO")
    
    if os.geteuid() != 0:
        print_error("Debes ejecutar como root (sudo)")
        return
    
    print("1. Django (Puerto 8001)")
    print("2. Frontend (Puerto 3000)")
    print("3. PostgreSQL")
    print("4. TODO (Backend + Frontend)")
    print()
    
    choice = input("Selecciona servicio: ").strip()
    
    services = {
        '1': 'django_saas',
        '2': 'frontend_saas',
        '3': 'postgresql',
        '4': ['django_saas', 'frontend_saas'],
    }
    
    if choice in services:
        svcs = services[choice] if isinstance(services[choice], list) else [services[choice]]
        
        project_path = str(PROJECT_ROOT)
        
        # 1. Actualizar dependencias de Backend si se reinicia Django o Todo
        if choice in ['1', '4']:
            print_info("ðŸ“¦ Actualizando dependencias de Backend...")
            subprocess.run([f"{project_path}/backend/venv/bin/pip", "install", "-r", f"{project_path}/backend/requirements.txt"], check=False)
            print_info("ðŸ—„ï¸  Ejecutando migraciones...")
            subprocess.run([f"{project_path}/backend/venv/bin/python", "manage.py", "migrate"], cwd=f"{project_path}/backend", check=False)

        if choice in ['2', '4']:
            print_info("ðŸ“¦ Actualizando Frontend (npm install)...")
            subprocess.run(["npm", "install"], cwd=f"{project_path}/frontend", check=False)
            print_info("ðŸ —ï¸  Generando Build de Frontend...")
            config = get_env_config()
            env = os.environ.copy()
            env['REACT_APP_DOMAIN_MAIN'] = config.get('DOMAIN_MAIN', 'localhost')
            env['REACT_APP_DJANGO_PORT'] = config.get('DJANGO_PORT', '8001')
            subprocess.run(["npm", "run", "build"], cwd=f"{project_path}/frontend", check=False, env=env)

        for svc in svcs:
            try:
                print_info(f"Reiniciando {svc}...")
                subprocess.run(['systemctl', 'restart', svc], check=True)
                print_success(f"{svc} reiniciado")
            except subprocess.CalledProcessError:
                print_error(f"Error reiniciando {svc}")
    else:
        print_error("Opción inválida")

# ========================================================================
# CREAR PAQUETES COMPLETOS
# ========================================================================

ALL_SERVICES = ['django_saas', 'frontend_saas']

def _auto_delete_services():
    """Elimina todos los servicios existentes silenciosamente antes de crear nuevos."""
    print_info("Limpiando servicios anteriores...")
    for svc in ALL_SERVICES:
        try:
            subprocess.run(['systemctl', 'stop', svc], capture_output=True, timeout=10)
            subprocess.run(['systemctl', 'disable', svc], capture_output=True, timeout=10)
            svc_file = f'/etc/systemd/system/{svc}.service'
            if os.path.exists(svc_file):
                os.remove(svc_file)
                print_success(f'Servicio anterior eliminado: {svc}')
        except Exception:
            pass
    try:
        subprocess.run(['systemctl', 'daemon-reload'], capture_output=True)
    except Exception:
        pass

def _run_user_from_path(project_path):
    return 'root' if str(project_path).startswith('/root/') else 'www-data'

def create_all_ip():
    """Crea django_saas + frontend_saas para acceso directo por IP (sin Nginx)."""
    print_header('CREAR SERVICIOS CON IP DIRECTA (SIN NGINX)')

    if os.geteuid() != 0:
        print_error('Debes ejecutar como root (sudo)')
        return

    config = get_env_config()
    project_path = str(PROJECT_ROOT)
    run_user = _run_user_from_path(project_path)
    django_port = config['DJANGO_PORT']
    react_port  = config['REACT_PORT']

    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        detected_ip = s.getsockname()[0]
        s.close()
    except Exception:
        detected_ip = '0.0.0.0'

    print_info(f'IP detectada: {detected_ip}')
    print_info(f'Django:   {detected_ip}:{django_port}')
    print_info(f'Frontend: {detected_ip}:{react_port}')
    print()

    confirm = input(f"{Colors.BOLD}Â¿Crear/reemplazar servicios con IP directa? (s/n): {Colors.ENDC}").lower()
    if confirm != 's':
        print_warning('Cancelado')
        return

    # 1. Eliminar existentes
    _auto_delete_services()

    # 2. Servicio Django
    # En Linux usamos gunicorn si existe, si no runserver
    gunicorn_bin = f'{project_path}/backend/venv/bin/gunicorn'
    venv_python  = f'{project_path}/backend/venv/bin/python'
    if os.path.exists(gunicorn_bin):
        exec_start = (f'{gunicorn_bin} config.wsgi:application '
                      f'--bind 0.0.0.0:{django_port} --workers 2 --threads 4 --timeout 600 --reload '
                      f'--access-logfile - --error-logfile -')
        print_info('Usando gunicorn para Django con logs en tiempo real')
    else:
        exec_start = f'{venv_python} manage.py runserver 0.0.0.0:{django_port}'
        print_warning('gunicorn no encontrado, usando runserver')

    django_service = f"""[Unit]
Description=Django SaaS - Standalone (Port 8001)
After=network.target postgresql.service

[Service]
Type=simple
User={run_user}
Group={run_user}
WorkingDirectory={project_path}/backend
Environment="PATH={project_path}/backend/venv/bin"
ExecStart={exec_start}
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
    with open('/etc/systemd/system/django_saas.service', 'w') as f:
        f.write(django_service)
    print_success('django_saas.service creado')

    frontend_service = f"""[Unit]
Description=Frontend SaaS - Standalone (Port 3000)
After=network.target

[Service]
Type=simple
User={run_user}
Group={run_user}
WorkingDirectory={project_path}/frontend
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin"
Environment="HOST=0.0.0.0"
Environment="PORT={react_port}"
ExecStart=/usr/bin/npx serve -s build -l {react_port}
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
    with open('/etc/systemd/system/frontend_saas.service', 'w') as f:
        f.write(frontend_service)
    print_success('frontend_saas.service creado')

    # 4. Construir frontend
    print_info('Construyendo frontend (npm run build)...')
    try:
        env = os.environ.copy()
        env['REACT_APP_DOMAIN_MAIN'] = config.get('DOMAIN_MAIN', 'localhost')
        env['REACT_APP_DJANGO_PORT'] = config.get('DJANGO_PORT', '8001')
        subprocess.run(['npm', 'run', 'build'], cwd=f'{project_path}/frontend', check=True, env=env)
        print_success('Build completado')
    except Exception as e:
        print_warning(f'Error en build: {e}')

    # 5. Activar y arrancar
    subprocess.run(['systemctl', 'daemon-reload'], check=True)
    for svc in ALL_SERVICES:
        subprocess.run(['systemctl', 'enable', svc], check=False)
        subprocess.run(['systemctl', 'start', svc], check=False)
        print_success(f'{svc} habilitado e iniciado')

    print_info(f'Accede al sistema en http://{detected_ip}:{react_port}')


def delete_all_services():
    """Elimina todos los servicios del sistema."""
    print_header('ELIMINAR TODOS LOS SERVICIOS DEL SISTEMA')

    if os.geteuid() != 0:
        print_error('Debes ejecutar como root (sudo)')
        return

    _auto_delete_services()
    print_success('Todos los servicios han sido eliminados')


def main():
    if len(sys.argv) < 2:
        while True:
            clear_screen()
            print_header("CONFIGURADOR DE SERVICIOS")
            
            print("1. Crear servicio Django (o reemplazar)")
            print("2. Crear servicio Frontend (o reemplazar)")
            print("3. Eliminar servicio")
            print("4. Ver estado de servicios")
            print("5. Ver logs")
            print("6. Reiniciar servicio")
            print("0. Salir")
            print()
            
            choice = input("Selecciona opción: ").strip()
            
            if choice == '1':
                create_django_service()
            elif choice == '2':
                create_frontend_service()
            elif choice == '3':
                delete_service()
            elif choice == '4':
                view_service_status()
            elif choice == '5':
                view_logs()
            elif choice == '6':
                restart_service()
            elif choice == '0':
                break
            else:
                print_error("Opción inválida")
                time.sleep(1)
    else:
        cmd = sys.argv[1]

        if cmd == 'django-service':
            create_django_service()
        elif cmd == 'frontend-service':
            create_frontend_service()
        elif cmd == 'delete-service':
            delete_service()
        elif cmd == 'delete-all':
            delete_all_services()
        elif cmd == 'create-all-ip':
            create_all_ip()
        elif cmd == 'status':
            view_service_status()
        elif cmd == 'logs':
            view_logs()
        elif cmd == 'restart':
            restart_service()

if __name__ == '__main__':
    main()

