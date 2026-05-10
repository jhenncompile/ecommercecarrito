import os
import socket
from django.core.management.base import BaseCommand
from django.conf import settings
from customers.models import Client, Domain

class Command(BaseCommand):
    help = 'Crea el tenant publico y sincroniza los dominios con la IP actual del servidor.'

    def handle(self, *args, **options):
        self.stdout.write("--- Iniciando Saneamiento de Dominios ---")

        # 1. Obtener la IP actual o dominio base
        # Intentamos obtener la IP publica/local del servidor
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            current_ip = s.getsockname()[0]
            s.close()
        except Exception:
            current_ip = "localhost"

        # Priorizar DOMAIN_MAIN del .env si existe
        base_domain = getattr(settings, 'DOMAIN_MAIN', current_ip)
        if base_domain == 'localhost' or base_domain == '127.0.0.1':
            base_domain = current_ip

        self.stdout.write(f"IP/Dominio detectado: {base_domain}")

        # 2. Asegurar que existe el tenant 'public'
        public_tenant, created = Client.objects.get_or_create(
            schema_name='public',
            defaults={'name': 'Public Marketplace'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Creado tenant 'public'"))

        # 3. Asegurar que el dominio base apunta a 'public'
        # Probamos con la IP pura y con .nip.io por si acaso
        domains_to_check = [base_domain]
        if not base_domain.endswith('.nip.io') and base_domain != 'localhost':
            domains_to_check.append(f"{base_domain}.nip.io")

        for d_name in domains_to_check:
            Domain.objects.get_or_create(
                domain=d_name,
                tenant=public_tenant,
                defaults={'is_primary': d_name == base_domain}
            )
            self.stdout.write(f"Asegurado dominio publico: {d_name}")

        # 4. Actualizar dominios de los tenants existentes
        # Si la IP cambió (ej: de 192.168... a 157.173...), hay que actualizar
        all_domains = Domain.objects.exclude(tenant=public_tenant)
        for dom in all_domains:
            # Si el dominio actual contiene una IP o .nip.io, intentamos migrarlo
            old_domain = dom.domain
            schema = dom.tenant.schema_name
            
            # Nuevo formato: schema.base_domain
            new_domain = f"{schema}.{base_domain}"
            if base_domain != 'localhost' and not new_domain.endswith('.nip.io'):
                new_domain = f"{new_domain}.nip.io"
            
            if old_domain != new_domain:
                dom.domain = new_domain
                dom.save()
                self.stdout.write(self.style.WARNING(f"Actualizado: {old_domain} -> {new_domain}"))

        self.stdout.write(self.style.SUCCESS("--- Saneamiento finalizado ---"))
