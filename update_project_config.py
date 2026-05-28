import os
import sys
from pathlib import Path

config_path = Path('c:/Users/ldgd2/OneDrive/Documentos/Proyectos_lider/python/ecommerce/scripts_utiles/core/project_config.py')
content = config_path.read_text('utf-8')

new_code = '''
def interactive_wizard():
    """Asistente interactivo para configurar el .env"""
    print("\\n[+] ASISTENTE INTERACTIVO DE CONFIGURACIÓN (.env)")
    env_file = PROJECT_ROOT / '.env'
    
    # Base de Datos
    if input("\\n¿Configurar Base de Datos externa? (s/N): ").lower() == 's':
        db_engine = input("  Engine (django.db.backends.postgresql): ") or "django.db.backends.postgresql"
        db_name = input("  Nombre BD: ")
        db_user = input("  Usuario: ")
        db_pass = input("  Contraseña: ")
        db_host = input("  Host (ej. localhost): ")
        db_port = input("  Puerto (ej. 5432): ")
        set_key(env_file, 'DATABASE_ENGINE', db_engine)
        set_key(env_file, 'DATABASE_NAME', db_name)
        set_key(env_file, 'DATABASE_USER', db_user)
        set_key(env_file, 'DATABASE_PASSWORD', db_pass)
        set_key(env_file, 'DATABASE_HOST', db_host)
        set_key(env_file, 'DATABASE_PORT', db_port)
        
    # SMTP
    if input("\\n¿Configurar Servidor de Correos (SMTP)? (s/N): ").lower() == 's':
        set_key(env_file, 'EMAIL_HOST', input("  Host (ej. smtp.gmail.com): "))
        set_key(env_file, 'EMAIL_PORT', input("  Puerto (ej. 587): "))
        set_key(env_file, 'EMAIL_HOST_USER', input("  Usuario SMTP: "))
        set_key(env_file, 'EMAIL_HOST_PASSWORD', input("  Contraseña SMTP: "))
        
    # Stripe
    if input("\\n¿Configurar Stripe? (s/N): ").lower() == 's':
        set_key(env_file, 'STRIPE_PUBLIC_KEY', input("  Stripe Public Key: "))
        set_key(env_file, 'STRIPE_SECRET_KEY', input("  Stripe Secret Key: "))
        set_key(env_file, 'STRIPE_WEBHOOK_SECRET', input("  Stripe Webhook Secret: "))
        
    print("\\n[OK] Configuración actualizada correctamente.")

def port_manager():
    """Gestor interactivo de puertos"""
    print("\\n[+] GESTOR DE PUERTOS")
    env_file = PROJECT_ROOT / '.env'
    load_dotenv(env_file)
    
    print(f"  Backend actual: {os.getenv('DJANGO_PORT', '8001')}")
    print(f"  Frontend actual: {os.getenv('REACT_PORT', '3000')}")
    print(f"  Nginx actual: {os.getenv('NGINX_PORT', '80')}")
    
    if input("\\n¿Deseas modificar los puertos? (s/N): ").lower() == 's':
        backend = input("  Nuevo puerto Backend (Intro para omitir): ")
        if backend: set_key(env_file, 'DJANGO_PORT', backend)
        
        frontend = input("  Nuevo puerto Frontend (Intro para omitir): ")
        if frontend: set_key(env_file, 'REACT_PORT', frontend)
        
        nginx = input("  Nuevo puerto Nginx (Intro para omitir): ")
        if nginx: set_key(env_file, 'NGINX_PORT', nginx)
        
        print("[OK] Puertos actualizados.")
'''

parts = content.split('def main():')
if len(parts) == 2:
    new_content = parts[0] + new_code + '\ndef main():' + parts[1]
    
    main_patch = '''
    elif cmd == 'wizard':
        if check_env():
            interactive_wizard()
    elif cmd == 'ports':
        if check_env():
            port_manager()
'''
    new_content = new_content.replace("        elif cmd == 'check':", main_patch + "        elif cmd == 'check':")
    
    # Update menu text in the py script too just in case
    new_content = new_content.replace('print("  prod   - Configurar para PRODUCCIÓN")', 'print("  prod   - Configurar para PRODUCCIÓN")\n        print("  wizard - Asistente interactivo .env")\n        print("  ports  - Gestor de puertos")')
    
    config_path.write_text(new_content, 'utf-8')
    print('project_config.py updated')
else:
    print('Failed to split project_config.py')
