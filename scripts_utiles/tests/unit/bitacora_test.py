import sys
from django.db import transaction
from apps.customers.models import Bitacora, Usuario, Client
from apps.customers.audit.services.bitacora_service import BitacoraService

def run_bitacora_test():
    """Prueba Profesional del Sistema de Auditoría (Bitácora)"""
    print("\n" + "="*70)
    print(f"{'TEST: AUDITORÍA Y SEGURIDAD (BITÁCORA)':^70}")
    print("="*70)
    
    try:
        with transaction.atomic():

            print("\n[1] Configurando entorno de prueba...")
            schema_name = 'test_audit_flow'
            tenant, _ = Client.objects.get_or_create(schema_name=schema_name, name="Audit Test Corp")
            
            user_admin = Usuario.objects.create_user(
                email='admin_test@audit.com', 
                password='Password123!', 
                first_name='Admin',
                last_name='Audit', 
                tenant=tenant
            )
            print(f"    [OK] Escenario listo para: {user_admin.email}")


            print("\n[2] Ejecutando acción de negocio con datos sensibles...")
            metadatos_producto = {
                'id_producto': 77,
                'nombre': 'IPhone 15 Pro',
                'precio': 999.00,
                'password_admin': 'Secreto_Confidencial' 
            }
            
            BitacoraService.registrar_accion(
                user=user_admin,
                modulo="Productos",
                accion="CREAR",
                metadatos=metadatos_producto
            )
            print("    [OK] Acción registrada vía BitacoraService.")


            print("\n[3] Verificando integridad del registro de auditoría...")
            registro = Bitacora.objects.filter(idUsuario=user_admin, modulo="Productos").first()
            
            if not registro:
                print("    [ERROR] No se encontró el registro en la base de datos.")
                sys.exit(1)


            if registro.idUsuario.id == user_admin.id:
                print(f"    [OK] Usuario vinculado correctamente: ID {registro.idUsuario.id}")

            if registro.metadatos.get('password_admin') == "********":
                print("    [OK] SEGURIDAD: Los datos sensibles han sido correctamente enmascarados.")
            else:
                print(f"    [ERROR] SEGURIDAD: Falló el filtro de datos sensibles. Valor: {registro.metadatos.get('password_admin')}")
                sys.exit(1)
            ip = registro.metadatos.get('ip')
            origen = registro.metadatos.get('browser')
            if ip and origen:
                print(f"    [OK] CONSISTENCIA: IP capturada ({ip}) y Origen capturado ({origen}).")
            else:
                print("    [ERROR] CONSISTENCIA: Faltan datos de IP u Origen en los metadatos.")
                sys.exit(1)

            print("\n" + "="*70)
            print(f"{'RESULTADO FINAL: TEST DE AUDITORÍA SUPERADO':^70}")
            print("="*70)
            raise Exception("ROLLBACK_FORZADO_DE_PRUEBA")

    except Exception as e:
        if str(e) == "ROLLBACK_FORZADO_DE_PRUEBA":
            pass
        else:
            print(f"\n[ERROR CRÍTICO] La prueba de bitácora ha fallado: {e}")
            sys.exit(1)

