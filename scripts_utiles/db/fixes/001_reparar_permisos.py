import os
import sys
import django
from django.core.management import call_command
from scripts_utiles.ui import print_info

def run():
    print_info("Ejecutando seed_permisos para asegurar que roles y planes estén configurados...")
    
    if not os.environ.get('DJANGO_SETTINGS_MODULE'):
        sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'backend'))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        django.setup()
        
    try:
        call_command('seed_permisos')
        return True
    except Exception as e:
        print_info(f"Error al ejecutar seed_permisos: {e}")
        return False
