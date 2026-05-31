from scripts_utiles.ui import print_info, run_django_command

def run():
    print_info("Ejecutando seed_permisos para asegurar que roles y planes estén configurados...")
    return run_django_command('seed_permisos')
