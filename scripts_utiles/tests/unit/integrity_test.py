import sys
from django.db import transaction, IntegrityError
from apps.customers.models import Client, Usuario

def run_integrity_check():
    """Verificar la integridad de las tablas (Restricciones UNIQUE, etc)"""
    print("\n[+] 3/4 Verificando integridad de tablas (Restricciones)...")
    try:
        with transaction.atomic():
            tenant = Client.objects.create(schema_name='tenant_integridad', name="Tenant Test")
            
            # 1. Probamos que funcione insertar un usuario normal
            Usuario.objects.create_user(email='unico@test.com', password='123', first_name='Juan', tenant=tenant)
            
            # 2. Forzamos el error de integridad (Mismo correo)
            try:

                with transaction.atomic(): 
                    Usuario.objects.create_user(email='unico@test.com', password='456', first_name='Pedro', tenant=tenant)
                

                print("  [ERROR] La base de datos PERMITIÓ guardar un correo duplicado. Revisa tus modelos.")
                sys.exit(1)
            except IntegrityError:
                print("  [OK] La base de datos BLOQUEÓ el correo duplicado correctamente.")
            
            # Limpiamos la BD
            raise Exception("ROLLBACK_INTENCIONAL")
    except Exception as e:
        if str(e) == "ROLLBACK_INTENCIONAL":
            pass
        else:
            print(f"  [ERROR] Falló la prueba de integridad: {e}")
            sys.exit(1)

