from django.apps import AppConfig


class CustomersConfig(AppConfig):
    name = 'apps.customers'
    label = 'customers'

    def ready(self):
        import os
        import sys
        
        # Ignorar en comandos de consola (migraciones, shell, etc.)
        if not any(cmd in sys.argv for cmd in ['makemigrations', 'migrate', 'collectstatic', 'shell', 'test', 'dbshell', 'createsuperuser']):
            # Si se usa runserver, solo ejecutar si RUN_MAIN=true para evitar ejecución doble (reloader)
            if 'runserver' not in sys.argv or os.environ.get('RUN_MAIN') == 'true':
                try:
                    from apps.gestionDeReportes.cu21_generar_backup.services.scheduler import start_scheduler
                    start_scheduler()
                except ImportError as e:
                    print(f"Error importando scheduler: {e}")
                
        # Registrar señales de tenants (límites de plan, etc)
        try:
            import apps.customers.tenants.signals
        except ImportError:
            pass
