#!/usr/bin/env python
# ========================================================================
# GESTOR DE USUARIOS, ROLES Y PERMISOS V1.0
# ========================================================================
import os
import sys
from pathlib import Path

# Configuración de Entorno Django
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / 'backend'
sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from customers.models import Usuario, Rol, Permiso, Client
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
    print("🚀 Inicializando sistema de Roles y Permisos...")
    
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
        print(f"  ✅ {len(perms_objs)} permisos sincronizados.")

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
            print(f"  ✅ Rol '{nombre}' configurado.")

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
        print(f"✨ ÉXITO: Usuario {email} ahora tiene el rol {rol.nombre}")
    except Usuario.DoesNotExist:
        print(f"❌ ERROR: No existe usuario con email {email}")
    except Rol.DoesNotExist:
        print(f"❌ ERROR: El rol '{role_name}' no existe. Usa --init primero.")

def list_users():
    print("\n--- LISTADO DE USUARIOS ---")
    for u in Usuario.objects.all():
        roles = ", ".join([r.nombre for r in u.roles.all()])
        print(f"[{u.id}] {u.email} | Staff: {u.is_staff} | Roles: {roles or 'Ninguno'}")

def create_user(email, password):
    es_fuerte, error = validar_password_fuerte(password)
    if not es_fuerte:
        print(f"❌ ERROR DE SEGURIDAD: {error}")
        return

    try:
        if Usuario.objects.filter(email=email).exists():
            print(f"❌ ERROR: El usuario {email} ya existe.")
            return

        user = Usuario.objects.create_user(email=email, password=password)
        print(f"✅ Usuario {email} creado exitosamente.")
        return user
    except Exception as e:
        print(f"❌ ERROR al crear usuario: {e}")

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
    else:
        parser.print_help()
