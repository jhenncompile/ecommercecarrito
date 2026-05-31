import os
import sys
import django
from getpass import getpass

# Configurar entorno de Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.customers.users.models.usuario import Usuario

def main():
    print("=== CAMBIAR CONTRASEÑA DE USUARIO ===")
    email = input("Introduce el correo del usuario: ").strip()
    
    try:
        user = Usuario.objects.get(email=email)
        print(f"Usuario encontrado: {user.email}")
        
        new_password = getpass("Introduce la nueva contraseña: ")
        confirm_password = getpass("Confirma la nueva contraseña: ")
        
        if new_password != confirm_password:
            print("Error: Las contraseñas no coinciden.")
            return
            
        if not new_password:
            print("Error: La contraseña no puede estar vacía.")
            return
            
        user.set_password(new_password)
        user.save()
        print(f"¡Éxito! Contraseña cambiada correctamente para {email}.")
        
    except Usuario.DoesNotExist:
        print(f"Error: No se encontró ningún usuario con el correo '{email}'.")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    main()
