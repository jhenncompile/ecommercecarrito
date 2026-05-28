import sys
from django.db import connection, transaction
from apps.customers.models import Client

def run_schema_check():
    """Validar la creación de esquemas (Multi-tenant)"""
    print("\n[+] 2/4 Verificando creación automática de esquemas...")
    test_schema = 'esquema_prueba_qa'
    try:
        # Usamos transaction.atomic para poder deshacer todo al final
        with transaction.atomic():
            # Creamos el tenant
            Client.objects.create(schema_name=test_schema, name="Tenant de Prueba")
            
            # Verificamos directamente en PostgreSQL si el esquema existe
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT schema_name FROM information_schema.schemata WHERE schema_name = %s;",
                    [test_schema]
                )
                if cursor.fetchone():
                    print(f"  [OK] El esquema '{test_schema}' se creó correctamente en PostgreSQL.")
                else:
                    print(f"  [ERROR] El Tenant se guardó, pero el esquema '{test_schema}' NO se creó.")
                    sys.exit(1)
            
            # Forzamos un rollback para que este tenant de prueba no se guarde en tu BD real
            raise Exception("ROLLBACK_INTENCIONAL")
    except Exception as e:
        if str(e) == "ROLLBACK_INTENCIONAL":
            pass # Todo salió perfecto y limpiamos la BD
        else:
            print(f"  [ERROR] Falló la prueba de esquemas: {e}")
            sys.exit(1)

