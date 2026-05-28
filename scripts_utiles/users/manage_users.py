#!/usr/bin/env python
# ========================================================================
# GESTOR DE USUARIOS, ROLES Y PERMISOS V1.0
# ========================================================================
import os
import sys
from pathlib import Path

# Configuración de Entorno Django
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = PROJECT_ROOT / 'backend'
sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.customers.models import Usuario, Rol, Permiso, Client
from django.db import transaction
import re

def validar_password_fuerte(password):
    """Verifica si una contraseña cumple con los requisitos mínimos de seguridad"""
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres."
    if not re.search(r"[A-Z]", password):
        return False, "Debe incluir al menos una mayúscula."
    if not re.search(r"[a-z]", password):
        return False, "Debe incluir al menos una minúscula."
    if not re.search(r"\d", password):
        return False, "Debe incluir al menos un número."
    if not re.search(r"[@$!%*?&]", password):
        return False, "Debe incluir al menos un carácter especial (@$!%*?&)."
    return True, ""

def init_system():
    print("ðŸš€ Inicializando sistema de Roles y Permisos...")
    
    with transaction.atomic():
        # 1. Crear Permisos Básicos
        permisos_data = [
            # Módulo Productos
            ('Ver Productos', 'VER_PRODUCTOS', 'Productos'),
            ('Crear Productos', 'CREAR_PRODUCTOS', 'Productos'),
            ('Editar Productos', 'EDITAR_PRODUCTOS', 'Productos'),
            ('Eliminar Productos', 'ELIMINAR_PRODUCTOS', 'Productos'),
            # Módulo Ventas
            ('Ver Ventas', 'VER_VENTAS', 'Ventas'),
            ('Gestionar Pedidos', 'GESTIONAR_PEDIDOS', 'Ventas'),
            # Módulo Usuarios
            ('Ver Usuarios', 'VER_USUARIOS', 'Usuarios'),
            ('Gestionar Roles', 'GESTIONAR_ROLES', 'Usuarios'),
            # Módulo Sistema
            ('Ver Bitácora', 'VER_BITACORA', 'Sistema'),
            ('Gestionar Respaldos', 'GESTIONAR_RESPALDOS', 'Sistema'),
        ]

        perms_objs = []
        for nombre, codigo, modulo in permisos_data:
            p, _ = Permiso.objects.get_or_create(
                codigo=codigo, 
                defaults={'nombre': nombre, 'modulo': modulo}
            )
            perms_objs.append(p)
        print(f"  âœ… {len(perms_objs)} permisos sincronizados.")

        # 2. Crear Roles Estándar
        roles_config = [
            ('Super Usuario', 1, 'Acceso total al sistema', perms_objs),
            ('Vendedor', 2, 'Gestión de tienda y ventas', [p for p in perms_objs if p.modulo in ['Productos', 'Ventas']]),
            ('Cliente', 3, 'Acceso a compras y perfil', [p for p in perms_objs if p.codigo == 'VER_PRODUCTOS']),
        ]

        for nombre, nivel, desc, perms in roles_config:
            rol, _ = Rol.objects.get_or_create(
                nombre=nombre,
                defaults={'nivel': nivel, 'descripcion': desc}
            )
            rol.permisos.set(perms)
            print(f"  âœ… Rol '{nombre}' configurado.")

def set_user_role(email, role_name):
    try:
        user = Usuario.objects.get(email=email)
        rol = Rol.objects.get(nombre__iexact=role_name)
        
        user.roles.add(rol)
        
        # Ajustes de staff según nivel
        if rol.nivel <= 2:
            user.is_staff = True
        if rol.nivel == 1:
            user.is_superuser = True
            
        user.save()
        print(f"âœ¨ Ã‰XITO: Usuario {email} ahora tiene el rol {rol.nombre}")
    except Usuario.DoesNotExist:
        print(f"âŒ ERROR: No existe usuario con email {email}")
    except Rol.DoesNotExist:
        print(f"âŒ ERROR: El rol '{role_name}' no existe. Usa --init primero.")

def list_users():
    print("\n--- LISTADO DE USUARIOS ---")
    for u in Usuario.objects.all():
        roles = ", ".join([r.nombre for r in u.roles.all()])
        print(f"[{u.id}] {u.email} | Staff: {u.is_staff} | Roles: {roles or 'Ninguno'}")

def create_user(email, password):
    es_fuerte, error = validar_password_fuerte(password)
    if not es_fuerte:
        print(f"âŒ ERROR DE SEGURIDAD: {error}")
        return

    try:
        if Usuario.objects.filter(email=email).exists():
            print(f"âŒ ERROR: El usuario {email} ya existe.")
            return

        user = Usuario.objects.create_user(email=email, password=password)
        print(f"âœ… Usuario {email} creado exitosamente.")
        return user
    except Exception as e:
        print(f"âŒ ERROR al crear usuario: {e}")

def delete_user(email):
    try:
        user = Usuario.objects.get(email=email)
        user.delete()
        print(f"✅ Usuario {email} eliminado exitosamente.")
    except Usuario.DoesNotExist:
        print(f"❌ ERROR: No existe usuario con email {email}")

def get_user_status(email):
    try:
        user = Usuario.objects.get(email=email)
        roles = ", ".join([r.nombre for r in user.roles.all()])
        print(f"Usuario: {user.email}")
        print(f"Activo:  {'SÍ' if user.is_active else 'NO'}")
        print(f"Staff:   {'SÍ' if user.is_staff else 'NO'}")
        print(f"SuperUser: {'SÍ' if user.is_superuser else 'NO'}")
        print(f"Roles:   {roles or 'Ninguno'}")
    except Usuario.DoesNotExist:
        print(f"❌ ERROR: No existe usuario con email {email}")

def activate_user(email):
    try:
        user = Usuario.objects.get(email=email)
        user.is_active = True
        user.save()
        print(f"✅ Usuario {email} activado exitosamente.")
    except Usuario.DoesNotExist:
        print(f"❌ ERROR: No existe usuario con email {email}")

def disable_user(email):
    try:
        user = Usuario.objects.get(email=email)
        user.is_active = False
        user.save()
        print(f"✅ Usuario {email} desactivado exitosamente.")
    except Usuario.DoesNotExist:
        print(f"❌ ERROR: No existe usuario con email {email}")

def list_roles():
    print("\n--- ROLES DISPONIBLES ---")
    for r in Rol.objects.all():
        print(f"- {r.nombre} (Nivel {r.nivel}): {r.descripcion}")

def edit_user(email, new_password=None):
    try:
        user = Usuario.objects.get(email=email)
        if new_password:
            es_fuerte, error = validar_password_fuerte(new_password)
            if not es_fuerte:
                print(f"❌ ERROR DE SEGURIDAD: {error}")
                return
            user.set_password(new_password)
            user.save()
            print(f"✅ Contraseña de {email} actualizada exitosamente.")
        else:
            print(f"ℹ️ No se especificaron cambios para el usuario {email}.")
    except Usuario.DoesNotExist:
        print(f"❌ ERROR: No existe usuario con email {email}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Gestor de Usuarios y Roles")
    parser.add_argument('--init', action='store_true', help="Inicializa roles y permisos básicos")
    parser.add_argument('--list', action='store_true', help="Lista todos los usuarios")
    parser.add_argument('--create', type=str, help="Email del nuevo usuario")
    parser.add_argument('--pass', type=str, dest='password', help="Password del nuevo usuario")
    parser.add_argument('--set-su', type=str, help="Asigna rol Super Usuario a un email")
    parser.add_argument('--set-vendedor', type=str, help="Asigna rol Vendedor a un email")
    parser.add_argument('--set-cliente', type=str, help="Asigna rol Cliente a un email")
    parser.add_argument('--edit', type=str, help="Email del usuario a editar")
    parser.add_argument('--delete', type=str, help="Email del usuario a eliminar")
    parser.add_argument('--status', type=str, help="Email del usuario a consultar")
    parser.add_argument('--activate', type=str, help="Email del usuario a activar")
    parser.add_argument('--disable', type=str, help="Email del usuario a desactivar")
    parser.add_argument('--list-roles', action='store_true', help="Lista todos los roles disponibles")
    
    args = parser.parse_args()

    if args.init:
        init_system()
    elif args.list:
        list_users()
    elif args.create:
        if not args.password:
            print("❌ ERROR: Debes proporcionar una contraseña con --pass")
        else:
            create_user(args.create, args.password)
    elif args.set_su:
        set_user_role(args.set_su, "Super Usuario")
    elif args.set_vendedor:
        set_user_role(args.set_vendedor, "Vendedor")
    elif args.set_cliente:
        set_user_role(args.set_cliente, "Cliente")
    elif args.edit:
        if not args.password:
            print("❌ ERROR: Debes proporcionar una nueva contraseña con --pass")
        else:
            edit_user(args.edit, args.password)
    elif args.delete:
        delete_user(args.delete)
    elif args.status:
        get_user_status(args.status)
    elif args.activate:
        activate_user(args.activate)
    elif args.disable:
        disable_user(args.disable)
    elif args.list_roles:
        list_roles()
    else:
        parser.print_help()

