#!/usr/bin/env python
# ========================================================================
# CONFIGURADOR DE BASE DE DATOS
# ========================================================================
# Configuración interactiva y completa de PostgreSQL
# Uso: python scripts_utiles/db_config.py

import os
import sys
from pathlib import Path
from dotenv import load_dotenv, set_key
import time

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_FILE = PROJECT_ROOT / '.env'

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
    UNDERLINE = '\033[4m'
    DIM = '\033[2m'
    
    # Para Windows (fallback)
    WIN_HEADER = '' if sys.platform == 'win32' else HEADER
    WIN_BLUE = '' if sys.platform == 'win32' else BLUE
    WIN_CYAN = '' if sys.platform == 'win32' else CYAN
    WIN_GREEN = '' if sys.platform == 'win32' else GREEN
    WIN_YELLOW = '' if sys.platform == 'win32' else YELLOW
    WIN_RED = '' if sys.platform == 'win32' else RED

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

def loading_animation(duration=2, text="Guardando"):
    """Animación de carga"""
    frames = ['â ‹', 'â ™', 'â ¹', 'â ¸', 'â ¼', 'â ´', 'â ¦', 'â §', 'â ‡', 'â ']
    end_time = time.time() + duration
    i = 0
    
    while time.time() < end_time:
        print(f"\r{frames[i % len(frames)]} {text}...", end='', flush=True)
        time.sleep(0.1)
        i += 1
    
    print(f"\râœ“ Completado        ", flush=True)

# ========================================================================
# FUNCIONES DE CONFIGURACIÓN
# ========================================================================

def load_current_config():
    """Carga configuración actual de .env"""
    load_dotenv(ENV_FILE)
    
    config = {
        'ENGINE': os.getenv('DATABASE_ENGINE', 'django_tenants.postgresql_backend'),
        'NAME': os.getenv('DATABASE_NAME', 'mi_saas_db'),
        'USER': os.getenv('DATABASE_USER', 'postgres'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'adm123'),
        'HOST': os.getenv('DATABASE_HOST', '127.0.0.1'),
        'PORT': os.getenv('DATABASE_PORT', '5432'),
    }
    
    return config

def show_current_config():
    """Muestra configuración actual de forma bonita"""
    config = load_current_config()
    
    print_header("CONFIGURACIÓN ACTUAL DE BASE DE DATOS")
    
    print(f"{Colors.BOLD}Tipo de Base de Datos:{Colors.ENDC}")
    print(f"  Engine: {Colors.CYAN}{config['ENGINE']}{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Conexión:{Colors.ENDC}")
    print(f"  Host:   {Colors.YELLOW}{config['HOST']}{Colors.ENDC}:{Colors.YELLOW}{config['PORT']}{Colors.ENDC}")
    print(f"  BD:     {Colors.CYAN}{config['NAME']}{Colors.ENDC}")
    print(f"  User:   {Colors.CYAN}{config['USER']}{Colors.ENDC}")
    print(f"  Pass:   {Colors.DIM}{'*' * len(config['PASSWORD'])}{Colors.ENDC}")
    
    print()

def test_connection(host, port, user, password, db_name):
    """Intenta conectar a la BD"""
    try:
        import psycopg2
        
        print_info("Intentando conectar a la base de datos...")
        
        conn = psycopg2.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=db_name
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        print_success("Conexión exitosa")
        print_info(f"PostgreSQL: {version.split(',')[0]}")
        return True
        
    except ImportError:
        print_warning("psycopg2 no está instalado - no se puede probar conexión")
        print_info("Instala con: pip install psycopg2-binary")
        return None
    except Exception as e:
        print_error(f"No se puede conectar: {str(e)}")
        return False

def configure_basic():
    """Configuración básica"""
    print_header("CONFIGURACIÓN BÁSICA")
    
    print(f"{Colors.BOLD}Presets disponibles:{Colors.ENDC}\n")
    print("  1. {:<30} Desarrollo Local (localhost:5432)".format("LOCAL"))
    print("  2. {:<30} Servidor Remoto".format("REMOTE"))
    print("  3. {:<30} Docker (postgres:5432)".format("DOCKER"))
    print("  4. {:<30} AWS RDS".format("AWS"))
    print("  5. {:<30} DigitalOcean Managed DB".format("DO"))
    
    choice = input(f"\n{Colors.BOLD}Selecciona un preset (1-5): {Colors.ENDC}").strip()
    
    presets = {
        '1': {
            'HOST': '127.0.0.1',
            'PORT': '5432',
            'NAME': 'mi_saas_db',
            'USER': 'postgres',
            'PASSWORD': 'adm123',
        },
        '2': {
            'HOST': input("Host/IP del servidor: "),
            'PORT': input("Puerto (default 5432): ") or '5432',
            'NAME': input("Nombre de la BD: "),
            'USER': input("Usuario: "),
            'PASSWORD': __import__('getpass').getpass("Contraseña: "),
        },
        '3': {
            'HOST': 'postgres',
            'PORT': '5432',
            'NAME': 'mi_saas_db',
            'USER': 'postgres',
            'PASSWORD': 'postgres',
        },
        '4': {
            'HOST': input("Endpoint RDS (ej: db.xxx.rds.amazonaws.com): "),
            'PORT': input("Puerto (default 5432): ") or '5432',
            'NAME': input("Nombre de la BD: "),
            'USER': input("Usuario: "),
            'PASSWORD': __import__('getpass').getpass("Contraseña: "),
        },
        '5': {
            'HOST': input("Hostname DigitalOcean: "),
            'PORT': input("Puerto (default 25060): ") or '25060',
            'NAME': input("Nombre de la BD: "),
            'USER': input("Usuario: "),
            'PASSWORD': __import__('getpass').getpass("Contraseña: "),
        },
    }
    
    if choice in presets:
        config = presets[choice]
        
        # Test de conexión
        print()
        if input(f"\n{Colors.BOLD}Â¿Probar conexión? (s/n): {Colors.ENDC}").lower() == 's':
            test_connection(
                config['HOST'], config['PORT'],
                config['USER'], config['PASSWORD'],
                config['NAME']
            )
        
        # Guardar
        if input(f"\n{Colors.BOLD}Â¿Guardar configuración? (s/n): {Colors.ENDC}").lower() == 's':
            loading_animation(1, "Guardando configuración")
            
            set_key(ENV_FILE, 'DATABASE_HOST', config['HOST'])
            set_key(ENV_FILE, 'DATABASE_PORT', config['PORT'])
            set_key(ENV_FILE, 'DATABASE_NAME', config['NAME'])
            set_key(ENV_FILE, 'DATABASE_USER', config['USER'])
            set_key(ENV_FILE, 'DATABASE_PASSWORD', config['PASSWORD'])
            
            print_success("Configuración guardada en .env")
            
            return True
    else:
        print_error("Opción inválida")
    
    return False

def configure_advanced():
    """Configuración avanzada (personalizada)"""
    print_header("CONFIGURACIÓN AVANZADA")
    
    config = load_current_config()
    
    print(f"{Colors.BOLD}Configuración actual:{Colors.ENDC}")
    print(f"  Host: {Colors.YELLOW}{config['HOST']}{Colors.ENDC}")
    print(f"  Port: {Colors.YELLOW}{config['PORT']}{Colors.ENDC}")
    print(f"  Name: {Colors.YELLOW}{config['NAME']}{Colors.ENDC}")
    print(f"  User: {Colors.YELLOW}{config['USER']}{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Ingresa nuevos valores (Enter para mantener):{Colors.ENDC}\n")
    
    new_config = {}
    
    # Host
    new_host = input(f"Host [{Colors.DIM}{config['HOST']}{Colors.ENDC}]: ").strip()
    new_config['HOST'] = new_host or config['HOST']
    
    # Port
    new_port = input(f"Puerto [{Colors.DIM}{config['PORT']}{Colors.ENDC}]: ").strip()
    if new_port:
        try:
            int(new_port)
            new_config['PORT'] = new_port
        except ValueError:
            print_error("Puerto debe ser un número")
            new_config['PORT'] = config['PORT']
    else:
        new_config['PORT'] = config['PORT']
    
    # BD Name
    new_name = input(f"Nombre BD [{Colors.DIM}{config['NAME']}{Colors.ENDC}]: ").strip()
    new_config['NAME'] = new_name or config['NAME']
    
    # User
    new_user = input(f"Usuario [{Colors.DIM}{config['USER']}{Colors.ENDC}]: ").strip()
    new_config['USER'] = new_user or config['USER']
    
    # Password
    import getpass
    print(f"Contraseña [{Colors.DIM}(sin cambios){Colors.ENDC}]:")
    new_password = getpass.getpass()
    new_config['PASSWORD'] = new_password or config['PASSWORD']
    
    # Resumen de cambios
    print(f"\n{Colors.BOLD}Cambios a aplicar:{Colors.ENDC}\n")
    
    cambios = 0
    if new_config['HOST'] != config['HOST']:
        print(f"  Host: {Colors.DIM}{config['HOST']}{Colors.ENDC} â†’ {Colors.YELLOW}{new_config['HOST']}{Colors.ENDC}")
        cambios += 1
    if new_config['PORT'] != config['PORT']:
        print(f"  Port: {Colors.DIM}{config['PORT']}{Colors.ENDC} â†’ {Colors.YELLOW}{new_config['PORT']}{Colors.ENDC}")
        cambios += 1
    if new_config['NAME'] != config['NAME']:
        print(f"  Name: {Colors.DIM}{config['NAME']}{Colors.ENDC} â†’ {Colors.YELLOW}{new_config['NAME']}{Colors.ENDC}")
        cambios += 1
    if new_config['USER'] != config['USER']:
        print(f"  User: {Colors.DIM}{config['USER']}{Colors.ENDC} â†’ {Colors.YELLOW}{new_config['USER']}{Colors.ENDC}")
        cambios += 1
    if new_config['PASSWORD'] != config['PASSWORD']:
        print(f"  Pass: {Colors.DIM}***{Colors.ENDC} â†’ {Colors.YELLOW}***{Colors.ENDC}")
        cambios += 1
    
    if cambios == 0:
        print("  (Sin cambios)")
    else:
        print(f"\n  Total: {Colors.BOLD}{cambios}{Colors.ENDC} cambio(s)")
    
    # Confirmar
    if cambios > 0 and input(f"\n{Colors.BOLD}Â¿Aplicar cambios? (s/n): {Colors.ENDC}").lower() == 's':
        
        # Test
        if input(f"{Colors.BOLD}Â¿Probar conexión primero? (s/n): {Colors.ENDC}").lower() == 's':
            if not test_connection(
                new_config['HOST'], new_config['PORT'],
                new_config['USER'], new_config['PASSWORD'],
                new_config['NAME']
            ):
                if input(f"{Colors.BOLD}Â¿Continuar de todos modos? (s/n): {Colors.ENDC}").lower() != 's':
                    return False
        
        # Guardar
        loading_animation(1, "Guardando cambios")
        
        set_key(ENV_FILE, 'DATABASE_HOST', new_config['HOST'])
        set_key(ENV_FILE, 'DATABASE_PORT', new_config['PORT'])
        set_key(ENV_FILE, 'DATABASE_NAME', new_config['NAME'])
        set_key(ENV_FILE, 'DATABASE_USER', new_config['USER'])
        set_key(ENV_FILE, 'DATABASE_PASSWORD', new_config['PASSWORD'])
        
        print_success("Cambios guardados exitosamente")
        return True
    
    return False

def configure_field():
    """Configurar un campo específico"""
    print_header("CONFIGURAR CAMPO ESPECÍFICO")
    
    config = load_current_config()
    
    print(f"{Colors.BOLD}Campos disponibles:{Colors.ENDC}\n")
    print("  1. HOST           - Servidor de BD")
    print("  2. PORT           - Puerto (default: 5432)")
    print("  3. NAME           - Nombre de Base de Datos")
    print("  4. USER           - Usuario")
    print("  5. PASSWORD       - Contraseña")
    print("  6. ENGINE         - Motor de BD")
    
    choice = input(f"\n{Colors.BOLD}Selecciona campo (1-6): {Colors.ENDC}").strip()
    
    fields = {
        '1': ('HOST', 'Host/IP de la BD'),
        '2': ('PORT', 'Puerto (ej: 5432)'),
        '3': ('NAME', 'Nombre de la BD'),
        '4': ('USER', 'Usuario de la BD'),
        '5': ('PASSWORD', 'Contraseña'),
        '6': ('ENGINE', 'Engine de Django'),
    }
    
    if choice in fields:
        field_name, field_desc = fields[choice]
        
        print(f"\n{Colors.BOLD}{field_desc}{Colors.ENDC}")
        print(f"Valor actual: {Colors.DIM}{config[field_name]}{Colors.ENDC}\n")
        
        if choice == '5':
            import getpass
            nuevo_valor = getpass.getpass("Nuevo valor: ")
        else:
            nuevo_valor = input("Nuevo valor: ").strip()
        
        if nuevo_valor and nuevo_valor != config[field_name]:
            print(f"\n{Colors.DIM}{config[field_name]}{Colors.ENDC} â†’ {Colors.YELLOW}{nuevo_valor}{Colors.ENDC}")
            
            if input(f"\n{Colors.BOLD}Â¿Confirmar cambio? (s/n): {Colors.ENDC}").lower() == 's':
                loading_animation(0.5)
                set_key(ENV_FILE, f'DATABASE_{field_name}', nuevo_valor)
                print_success(f"{field_name} actualizado")
        else:
            print_warning("Sin cambios")
    else:
        print_error("Opción inválida")

def show_presets():
    """Muestra presets disponibles"""
    print_header("PRESETS DE CONFIGURACIÓN")
    
    presets = {
        'LOCAL': {
            'desc': 'Desarrollo Local',
            'host': '127.0.0.1',
            'port': '5432',
            'user': 'postgres',
            'db': 'mi_saas_db'
        },
        'DOCKER': {
            'desc': 'Docker Compose',
            'host': 'postgres',
            'port': '5432',
            'user': 'postgres',
            'db': 'mi_saas_db'
        },
        'AWS_RDS': {
            'desc': 'AWS RDS Aurora',
            'host': 'xxx.rds.amazonaws.com',
            'port': '5432',
            'user': 'admin',
            'db': 'produccion'
        },
        'DO_MANAGED': {
            'desc': 'DigitalOcean Managed DB',
            'host': 'xxx-xxx.ondigitalocean.com',
            'port': '25060',
            'user': 'dbuser',
            'db': 'defaultdb'
        },
        'LINODE': {
            'desc': 'Linode Managed DB',
            'host': 'xxx-xxx.linodelabs.com',
            'port': '5432',
            'user': 'root',
            'db': 'postgres'
        },
    }
    
    for key, preset in presets.items():
        print(f"{Colors.BOLD}{key}:{Colors.ENDC}")
        print(f"  Descripción: {preset['desc']}")
        print(f"  Host: {Colors.CYAN}{preset['host']}{Colors.ENDC}")
        print(f"  Port: {Colors.CYAN}{preset['port']}{Colors.ENDC}")
        print(f"  User: {Colors.CYAN}{preset['user']}{Colors.ENDC}")
        print(f"  DB:   {Colors.CYAN}{preset['db']}{Colors.ENDC}")
        print()

def main():
    if len(sys.argv) < 2:
        print_header("CONFIGURADOR DE BASE DE DATOS")
        
        print(f"{Colors.BOLD}Opciones:{Colors.ENDC}\n")
        print("  1. Ver configuración actual")
        print("  2. Configuración básica (presets)")
        print("  3. Configuración avanzada (personalizada)")
        print("  4. Configurar un campo")
        print("  5. Ver presets disponibles")
        print("  0. Salir")
        
        choice = input(f"\n{Colors.BOLD}Selecciona opción (0-5): {Colors.ENDC}").strip()
        
        if choice == '1':
            show_current_config()
        elif choice == '2':
            configure_basic()
        elif choice == '3':
            configure_advanced()
        elif choice == '4':
            configure_field()
        elif choice == '5':
            show_presets()
        elif choice == '0':
            print_info("Saliendo...")
        else:
            print_error("Opción inválida")
    else:
        cmd = sys.argv[1]
        
        if cmd == 'show':
            show_current_config()
        elif cmd == 'basic':
            configure_basic()
        elif cmd == 'advanced':
            configure_advanced()
        elif cmd == 'field':
            configure_field()
        elif cmd == 'presets':
            show_presets()
        elif cmd == 'test':
            config = load_current_config()
            test_connection(config['HOST'], config['PORT'], config['USER'], config['PASSWORD'], config['NAME'])
        else:
            print_error(f"Comando desconocido: {cmd}")

if __name__ == '__main__':
    main()

