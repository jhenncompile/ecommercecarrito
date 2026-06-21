import os
import sys
import django
from scripts_utiles.ui import print_info, print_success, print_error

def run():
    print_info("Actualizando planes y permisos (Reestructuración de 4 niveles)...")
    
    if not os.environ.get('DJANGO_SETTINGS_MODULE'):
        sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'backend'))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        django.setup()
        
    try:
        from apps.customers.tenants.models.plan import Plan
        from apps.gestionDeUsuarioySeguridad.cu5_gestionar_permisos.models.permiso import Permiso

        planes_config = [
            {
                "nombre": "Gratis", "precio_mensual": 0.0, "precio_anual": 0.0, 
                "max_usuarios": 2, "max_productos": 50, "facturacion_max": 1000.0,
                "permisos": []
            },
            {
                "nombre": "Standard", "precio_mensual": 29.0, "precio_anual": 290.0, 
                "max_usuarios": 5, "max_productos": 500, "facturacion_max": 10000.0,
                "permisos": ["REP_ESTATICO"]
            },
            {
                "nombre": "Gold", "precio_mensual": 69.0, "precio_anual": 690.0, 
                "max_usuarios": 15, "max_productos": 5000, "facturacion_max": 500000.0,
                "permisos": ["REP_ESTATICO", "VER_DASHBOARD_AVANZADO", "EXPORTAR_CLIENTES", "CONFIGURACION_PAGOS"]
            },
            {
                "nombre": "Profesional", "precio_mensual": 99.0, "precio_anual": 990.0, 
                "max_usuarios": 0, "max_productos": 0, "facturacion_max": None,
                "permisos": ["REP_ESTATICO", "VER_DASHBOARD_AVANZADO", "EXPORTAR_CLIENTES", "CONFIGURACION_PAGOS", "REP_DINAMICO", "REP_AUDIO"]
            }
        ]

        permisos_a_premium = ['PROCESAR_PEDIDOS', 'EMITIR_FACTURA', 'GESTIONAR_USUARIOS', 'GESTIONAR_ROLES', 'REP_ESTATICO']
        Permiso.objects.filter(codigo__in=permisos_a_premium).update(es_basico=False)

        permisos_db = {p.codigo: p for p in Permiso.objects.all()}

        for p_data in planes_config:
            plan, created = Plan.objects.get_or_create(
                nombre=p_data['nombre'],
                defaults={
                    'precio_mensual': p_data['precio_mensual'],
                    'precio_anual': p_data['precio_anual'],
                    'max_usuarios': p_data['max_usuarios'],
                    'max_productos': p_data['max_productos'],
                    'facturacion_max': p_data.get('facturacion_max', None),
                }
            )
            if not created:
                Plan.objects.filter(id=plan.id).update(
                    precio_mensual=p_data['precio_mensual'],
                    max_usuarios=p_data['max_usuarios'],
                    max_productos=p_data['max_productos'],
                    facturacion_max=p_data.get('facturacion_max', None)
                )
            
            # Asignar permisos si existen
            permisos_a_asignar = [permisos_db[c] for c in p_data['permisos'] if c in permisos_db]
            plan.permisos.set(permisos_a_asignar)
            print_success(f"Plan {plan.nombre} configurado con {len(permisos_a_asignar)} permisos premium.")

        # Limpiar planes viejos y migrar tiendas
        nuevos_nombres = [p['nombre'] for p in planes_config]
        planes_viejos = Plan.objects.exclude(nombre__in=nuevos_nombres)
        
        if planes_viejos.exists():
            from apps.customers.models import Client
            plan_default = Plan.objects.get(nombre='Gratis')
            plan_standard = Plan.objects.get(nombre='Standard')
            plan_gold = Plan.objects.get(nombre='Gold')
            
            for p_viejo in planes_viejos:
                if p_viejo.nombre == 'Básico':
                    nuevo_plan = plan_standard
                elif p_viejo.nombre == 'Medio':
                    nuevo_plan = plan_gold
                else:
                    nuevo_plan = plan_default
                    
                tenants = Client.objects.filter(plan=p_viejo)
                if tenants.exists():
                    print_info(f"Migrando {tenants.count()} tiendas de '{p_viejo.nombre}' a '{nuevo_plan.nombre}'")
                    tenants.update(plan=nuevo_plan)
                    
                print_info(f"Eliminando plan obsoleto: {p_viejo.nombre}")
                p_viejo.delete()

        return True
    except Exception as e:
        print_error(f"Error al actualizar planes: {e}")
        return False
