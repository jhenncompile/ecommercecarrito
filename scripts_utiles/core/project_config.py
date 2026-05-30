#!/usr/bin/env python
# ========================================================================
# SCRIPT DE CONFIGURACIÓN
# ========================================================================
# Gestiona configuración del ambiente
# Uso: python scripts_utiles/config.py [comando]

import os
import sys
import socket
from pathlib import Path
from dotenv import load_dotenv, set_key

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

def load_env():
    """Carga variables de entorno"""
    env_file = PROJECT_ROOT / '.env'
    load_dotenv(env_file)

def show_config():
    """Muestra configuración actual"""
    load_env()
    
    print("\n" + "="*60)
    print("CONFIGURACIÓN ACTUAL")
    print("="*60)
    
    vars_to_show = [
        'ENVIRONMENT',
        'DEBUG',
        'DOMAIN_MAIN',
        'DOMAIN_ALLOWED_HOSTS',
        'DJANGO_PORT',
        'REACT_PORT',
        'DATABASE_HOST',
        'DATABASE_NAME',
        'DATABASE_USER',
    ]
    
    for var in vars_to_show:
        value = os.getenv(var, '(no definido)')
        # Ocultar contraseñas
        if 'PASSWORD' in var:
            value = '***' if value else '(no definido)'
        print(f"  {var:<25} = {value}")
    
    print(f"\n  Hostname del dispositivo: {socket.gethostname()}")
    print("="*60 + "\n")

def setup_development():
    """Configura para ambiente de desarrollo"""
    env_file = PROJECT_ROOT / '.env'
    
    print("\n[+] Configurando para DESARROLLO...")
    
    set_key(env_file, 'ENVIRONMENT', 'development')
    set_key(env_file, 'DEBUG', 'True')
    set_key(env_file, 'CORS_ALLOW_ALL_ORIGINS', 'True')
    set_key(env_file, 'DOMAIN_MAIN', 'localhost')
    
    print("[OK] Ambiente configurado para DESARROLLO")
    print(f"[i] .env actualizado: {env_file}")

def setup_production():
    """Configura para ambiente de producción"""
    env_file = PROJECT_ROOT / '.env'
    
    print("\n[+] Configurando para PRODUCCIÓN...")
    
    set_key(env_file, 'ENVIRONMENT', 'production')
    set_key(env_file, 'DEBUG', 'False')
    set_key(env_file, 'CORS_ALLOW_ALL_ORIGINS', 'False')
    
    print("[!] Ingresa datos de producción:")
    domain = input("  Dominio principal: ").strip()
    allowed_hosts = input("  Dominios adicionales (separados por coma): ").strip()
    
    set_key(env_file, 'DOMAIN_MAIN', domain)
    if allowed_hosts:
        set_key(env_file, 'DOMAIN_ALLOWED_HOSTS', allowed_hosts)
    
    print("[OK] Ambiente configurado para PRODUCCIÓN")
    print(f"[âš ] Recuerda cambiar SECRET_KEY en .env")

def check_env():
    """Verifica que el .env existe y es válido"""
    env_file = PROJECT_ROOT / '.env'
    
    if not env_file.exists():
        print(f"[ERROR] {env_file} no existe")
        example_file = PROJECT_ROOT / '.env.example'
        if example_file.exists():
            print(f"[i] Copiando desde .env.example...")
            with open(example_file) as f:
                content = f.read()
            with open(env_file, 'w') as f:
                f.write(content)
            print(f"[OK] .env creado")
        else:
            print("[ERROR] .env.example tampoco existe")
            return False
    
    return True


def interactive_wizard():
    """Asistente interactivo para configurar el .env"""
    print("\n[+] ASISTENTE INTERACTIVO DE CONFIGURACIÓN (.env)")
    env_file = PROJECT_ROOT / '.env'
    
    # Base de Datos
    if input("\n¿Configurar Base de Datos externa? (s/N): ").lower() == 's':
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
    if input("\n¿Configurar Servidor de Correos (SMTP)? (s/N): ").lower() == 's':
        set_key(env_file, 'EMAIL_HOST', input("  Host (ej. smtp.gmail.com): "))
        set_key(env_file, 'EMAIL_PORT', input("  Puerto (ej. 587): "))
        set_key(env_file, 'EMAIL_HOST_USER', input("  Usuario SMTP: "))
        set_key(env_file, 'EMAIL_HOST_PASSWORD', input("  Contraseña SMTP: "))
        
    # Stripe
    if input("\n¿Configurar Stripe? (s/N): ").lower() == 's':
        set_key(env_file, 'STRIPE_PUBLIC_KEY', input("  Stripe Public Key: "))
        set_key(env_file, 'STRIPE_SECRET_KEY', input("  Stripe Secret Key: "))
        set_key(env_file, 'STRIPE_WEBHOOK_SECRET', input("  Stripe Webhook Secret: "))
        
    print("\n[OK] Configuración actualizada correctamente.")

def port_manager():
    """Gestor interactivo de puertos"""
    print("\n[+] GESTOR DE PUERTOS")
    env_file = PROJECT_ROOT / '.env'
    load_dotenv(env_file)
    
    print(f"  Backend actual: {os.getenv('DJANGO_PORT', '8001')}")
    print(f"  Frontend actual: {os.getenv('REACT_PORT', '3000')}")
    
    if input("\n¿Deseas modificar los puertos? (s/N): ").lower() == 's':
        backend = input("  Nuevo puerto Backend (Intro para omitir): ")
        if backend: set_key(env_file, 'DJANGO_PORT', backend)
        
        frontend = input("  Nuevo puerto Frontend (Intro para omitir): ")
        if frontend: set_key(env_file, 'REACT_PORT', frontend)
        
        print("[OK] Puertos actualizados.")

def main():
    if len(sys.argv) < 2:
        show_config()
        return
    
    cmd = sys.argv[1]
    
    if cmd == 'show':
        show_config()
    elif cmd == 'dev':
        if check_env():
            setup_development()
            show_config()
    elif cmd == 'prod':
        if check_env():
            setup_production()
            show_config()
    elif cmd == 'check':
        if check_env():
            print("[OK] Configuración inicial verificada")
    else:
        print(f"[ERROR] Comando desconocido: {cmd}")
        print("\nComandos disponibles:")
        print("  show   - Mostrar configuración actual")
        print("  check  - Verificar .env existe")
        print("  dev    - Configurar para DESARROLLO")
        print("  prod   - Configurar para PRODUCCIÓN")
        print("  wizard - Asistente interactivo .env")
        print("  ports  - Gestor de puertos")
        sys.exit(1)

if __name__ == '__main__':
    main()

