#!/usr/bin/env python
# ========================================================================
# SCRIPT DE USUARIOS
# ========================================================================
# Gestión completa de usuarios (crear, editar, eliminar, listar)
# Uso: python scripts_utiles/manage_users.py [comando]

import os
import sys
from pathlib import Path
import getpass
import re

PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / 'backend'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from customers.models import Usuario, Client
from django.contrib.auth.hashers import make_password

def validate_email(email):
    """Valida formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def list_users():
    """Lista todos los usuarios"""
    print("\n" + "="*80)
    print("USUARIOS DE LA PLATAFORMA")
    print("="*80)
    
    users = Usuario.objects.all().order_by('-date_joined')
    
    if not users.exists():
        print("No hay usuarios registrados")
        return
    
    print(f"\n{'Email':<30} {'Nombre':<25} {'Estado':<10} {'Admin':<5} {'Activo':<7}")
    print("-" * 80)
    
    for user in users:
        email = user.email[:28]
        name = f"{user.first_name} {user.last_name}"[:23]
        status = "Activo" if user.is_active else "Inactivo"
        admin = "✓" if user.is_superuser else ""
        active = "✓" if user.is_active else "✗"
        
        print(f"{email:<30} {name:<25} {status:<10} {admin:<5} {active:<7}")
    
    print("-" * 80)
    print(f"Total: {users.count()} usuarios\n")

def create_user():
    """Crea nuevo usuario interactivamente"""
    print("\n" + "="*60)
    print("CREAR NUEVO USUARIO")
    print("="*60)
    
    # Email
    while True:
        email = input("\nEmail del usuario: ").strip()
        if not email:
            print("[ERROR] Email requerido")
            continue
        if not validate_email(email):
            print("[ERROR] Email inválido")
            continue
        if Usuario.objects.filter(email=email).exists():
            print("[ERROR] El email ya existe")
            continue
        break
    
    # Nombre
    first_name = input("Nombre: ").strip() or "Usuario"
    last_name = input("Apellido: ").strip() or "NoDefinido"
    
    # Contraseña
    print("\nContraseña (mínimo 8 caracteres):")
    while True:
        password = getpass.getpass("Contraseña: ")
        if len(password) < 8:
            print("[ERROR] Contraseña muy corta (mínimo 8)")
            continue
        
        password_confirm = getpass.getpass("Confirmar contraseña: ")
        if password != password_confirm:
            print("[ERROR] Las contraseñas no coinciden")
            continue
        break
    
    # Permisos (Forzado a Superusuario por seguridad del script)
    print("\nPermisos:")
    print("[!] Este script ahora solo crea Super Usuarios (Admins Globales).")
    is_staff = True
    is_superuser = True
    is_active = input("¿Estado activo? (s/n): ").lower() in ['s', '']  # Default: sí
    
    # Crear usuario
    try:
        user = Usuario.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_staff=is_staff,
            is_superuser=is_superuser,
            is_active=is_active
        )
        
        print("\n" + "="*60)
        print("[OK] Usuario creado exitosamente")
        print("="*60)
        print(f"Email:      {user.email}")
        print(f"Nombre:     {user.first_name} {user.last_name}")
        print(f"Admin:      {'Sí' if user.is_staff else 'No'}")
        print(f"Super:      {'Sí' if user.is_superuser else 'No'}")
        print(f"Activo:     {'Sí' if user.is_active else 'No'}")
        print(f"ID:         {user.id}")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n[ERROR] {e}\n")

def edit_user():
    """Edita usuario existente"""
    print("\n" + "="*60)
    print("EDITAR USUARIO")
    print("="*60)
    
    email = input("\nEmail del usuario a editar: ").strip()
    
    try:
        user = Usuario.objects.get(email=email)
    except Usuario.DoesNotExist:
        print("[ERROR] Usuario no encontrado\n")
        return
    
    print(f"\nUsuario encontrado: {user.first_name} {user.last_name}")
    print("\nOpciones:")
    print("  1. Cambiar contraseña")
    print("  2. Cambiar nombre")
    print("  3. Cambiar permisos")
    print("  4. Activar/Desactivar")
    
    choice = input("\nOpciona: ").strip()
    
    if choice == '1':
        password = getpass.getpass("Nueva contraseña: ")
        user.set_password(password)
        user.save()
        print("[OK] Contraseña actualizada")
    
    elif choice == '2':
        user.first_name = input(f"Nombre [{user.first_name}]: ") or user.first_name
        user.last_name = input(f"Apellido [{user.last_name}]: ") or user.last_name
        user.save()
        print("[OK] Nombre actualizado")
    
    elif choice == '3':
        user.is_staff = input(f"¿Admin? (s/n) [{('s' if user.is_staff else 'n')}]: ").lower() == 's'
        user.is_superuser = input(f"¿Super? (s/n) [{('s' if user.is_superuser else 'n')}]: ").lower() == 's'
        user.save()
        print("[OK] Permisos actualizados")
    
    elif choice == '4':
        user.is_active = not user.is_active
        user.save()
        estado = "Activado" if user.is_active else "Desactivado"
        print(f"[OK] Usuario {estado}")
    
    else:
        print("[ERROR] Opción inválida")

def delete_user():
    """Elimina usuario"""
    print("\n" + "="*60)
    print("ELIMINAR USUARIO")
    print("="*60)
    
    email = input("\nEmail del usuario a eliminar: ").strip()
    
    try:
        user = Usuario.objects.get(email=email)
    except Usuario.DoesNotExist:
        print("[ERROR] Usuario no encontrado\n")
        return
    
    print(f"\nUsuario: {user.first_name} {user.last_name}")
    print(f"Email: {user.email}")
    
    confirm = input("\n¿Está seguro? (escriba 'ELIMINAR'): ").strip()
    
    if confirm == "ELIMINAR":
        user.delete()
        print("[OK] Usuario eliminado\n")
    else:
        print("[CANCELADO]\n")

def reset_password():
    """Reinicia contraseña de usuario a temporal"""
    print("\n" + "="*60)
    print("REINICIAR CONTRASEÑA")
    print("="*60)
    
    email = input("\nEmail del usuario: ").strip()
    
    try:
        user = Usuario.objects.get(email=email)
    except Usuario.DoesNotExist:
        print("[ERROR] Usuario no encontrado\n")
        return
    
    # Generar contraseña temporal
    temp_password = "TempPass" + ''.join([str(i % 10) for i in range(8)])
    user.set_password(temp_password)
    user.save()
    
    print("\n" + "="*60)
    print("[OK] Contraseña reiniciada")
    print("="*60)
    print(f"Email: {user.email}")
    print(f"Contraseña temporal: {temp_password}")
    print("⚠️  El usuario debe cambiarla en el primer login")
    print("="*60 + "\n")

def bulk_create_test_users():
    """Crea múltiples usuarios de prueba"""
    print("\n" + "="*60)
    print("CREAR USUARIOS DE PRUEBA (BATCH)")
    print("="*60)
    
    count = input("\n¿Cuántos usuarios crear? (1-50): ").strip()
    
    try:
        count = int(count)
        if count < 1 or count > 50:
            raise ValueError
    except ValueError:
        print("[ERROR] Número inválido")
        return
    
    base_password = "TestUser123!"
    created = 0
    
    print(f"\n[+] Creando {count} usuarios...")
    
    for i in range(1, count + 1):
        email = f'testuser{i:03d}@test.local'
        
        if not Usuario.objects.filter(email=email).exists():
            Usuario.objects.create_user(
                email=email,
                password=base_password,
                first_name=f'Test{i}',
                last_name='User',
                is_active=True
            )
            created += 1
        
        # Mostrar progreso
        if i % 10 == 0:
            print(f"  {i}/{count}...")
    
    print(f"\n[OK] {created} usuarios creados")
    print(f"[i] Contraseña para todos: {base_password}\n")

def status_user():
    """Consulta el estado del usuario """
    print("\n" + "="*60)
    print("CONSULTAR ESTADO DE USUARIO")
    print("="*60)
    email = input("\nEmail del usuario: ").strip()
    try:
        user = Usuario.objects.get(email=email)
        # Usa el método status() que construimos en el modelo
        estado = user.status()
        print(f"\n[OK] El usuario {user.email} se encuentra: {'Activo' if estado else 'Inactivo'}\n")
    except Usuario.DoesNotExist:
        print("[ERROR] Usuario no encontrado\n")

def activate_user():
    """Activa el usuario"""
    print("\n" + "="*60)
    print("ACTIVAR USUARIO")
    print("="*60)
    email = input("\nEmail del usuario: ").strip()
    try:
        user = Usuario.objects.get(email=email)
        # Usa el método activate() que construimos en el modelo
        user.activate()
        print(f"\n[OK] El usuario {user.email} ha sido activado exitosamente\n")
    except Usuario.DoesNotExist:
        print("[ERROR] Usuario no encontrado\n")

def disable_user():
    """Desactiva el usuario"""
    print("\n" + "="*60)
    print("DESACTIVAR USUARIO")
    print("="*60)
    email = input("\nEmail del usuario: ").strip()
    try:
        user = Usuario.objects.get(email=email)
        # Usa el método disable() que construimos en el modelo
        user.disable()
        print(f"\n[OK] El usuario {user.email} ha sido desactivado exitosamente\n")
    except Usuario.DoesNotExist:
        print("[ERROR] Usuario no encontrado\n")

def main():
    if len(sys.argv) < 2:
        print("Uso: python manage_users.py [comando]")
        print("\nComandos disponibles:")
        print("  list        - Listar todos los usuarios")
        print("  create      - Crear nuevo usuario")
        print("  edit        - Editar usuario existente")
        print("  delete      - Eliminar usuario")
        print("  reset       - Reiniciar contraseña")
        print("  bulk-create - Crear múltiples usuarios de prueba")
        print("  status      - Ver estado (activo/inactivo)")
        print("  activate    - Activar usuario")
        print("  disable     - Desactivar usuario")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'list':
        list_users()
    elif cmd == 'create':
        create_user()
    elif cmd == 'edit':
        edit_user()
    elif cmd == 'delete':
        delete_user()
    elif cmd == 'reset':
        reset_password()
    elif cmd == 'bulk-create':
        bulk_create_test_users()
    elif cmd == 'status':
        status_user()
    elif cmd == 'activate':
        activate_user()
    elif cmd == 'disable':
        disable_user()
    else:
        print(f"[ERROR] Comando desconocido: {cmd}")
        sys.exit(1)

if __name__ == '__main__':
    main()
