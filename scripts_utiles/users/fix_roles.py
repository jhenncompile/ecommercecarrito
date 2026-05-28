#!/usr/bin/env python
# ========================================================================
# SCRIPT PARA AJUSTAR ROLES DE USUARIO
# ========================================================================
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = PROJECT_ROOT / 'backend'
sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.customers.models import Usuario, Rol, Permiso

def setup_basic_permissions():
    """Crea permisos básicos si no existen"""
    print("[i] Verificando permisos básicos...")
    permisos_config = [
        # Módulo Productos
        {'nombre': 'Ver Productos', 'codigo': 'VER_PRODUCTOS', 'modulo': 'Productos'},
        {'nombre': 'Crear Producto', 'codigo': 'CREAR_PRODUCTO', 'modulo': 'Productos'},
        {'nombre': 'Editar Producto', 'codigo': 'EDITAR_PRODUCTO', 'modulo': 'Productos'},
        {'nombre': 'Eliminar Producto', 'codigo': 'ELIMINAR_PRODUCTO', 'modulo': 'Productos'},
        
        # Módulo Ventas
        {'nombre': 'Ver Ventas', 'codigo': 'VER_VENTAS', 'modulo': 'Ventas'},
        {'nombre': 'Ver Pedidos', 'codigo': 'VER_PEDIDOS', 'modulo': 'Ventas'},
        {'nombre': 'Gestionar Pedidos', 'codigo': 'GESTIONAR_PEDIDOS', 'modulo': 'Ventas'},
        
        # Módulo Usuarios/Clientes
        {'nombre': 'Gestionar Usuarios', 'codigo': 'GESTIONAR_USUARIOS', 'modulo': 'Usuarios'},
        {'nombre': 'Ver Clientes', 'codigo': 'VER_CLIENTES', 'modulo': 'Clientes'},
        
        # Módulo Cliente (Buyer)
        {'nombre': 'Realizar Pedido', 'codigo': 'REALIZAR_PEDIDO', 'modulo': 'Cliente'},
        {'nombre': 'Ver Mis Pedidos', 'codigo': 'VER_MIS_PEDIDOS', 'modulo': 'Cliente'},
    ]
    
    for p_data in permisos_config:
        permiso, created = Permiso.objects.get_or_create(
            codigo=p_data['codigo'],
            defaults={'nombre': p_data['nombre'], 'modulo': p_data['modulo']}
        )
        if created:
            print(f"  [+] Permiso creado: {permiso.codigo}")

def setup_basic_roles():
    """Asegura que los roles básicos existan y tengan sus permisos"""
    print("\n[i] Verificando roles básicos...")
    roles_config = [
        {'nombre': 'Administrador', 'nivel': 1, 'descripcion': 'Acceso total al sistema'},
        {'nombre': 'Vendedor', 'nivel': 2, 'descripcion': 'Gestión de tienda y ventas'},
        {'nombre': 'Cliente', 'nivel': 3, 'descripcion': 'Comprador en el marketplace'},
    ]
    
    all_perms = Permiso.objects.all()
    vendedor_perms = Permiso.objects.filter(codigo__in=[
        'VER_PRODUCTOS', 'CREAR_PRODUCTO', 'EDITAR_PRODUCTO', 'VER_VENTAS', 'VER_PEDIDOS', 'GESTIONAR_PEDIDOS', 'VER_CLIENTES'
    ])
    cliente_perms = Permiso.objects.filter(codigo__in=[
        'VER_PRODUCTOS', 'REALIZAR_PEDIDO', 'VER_MIS_PEDIDOS'
    ])

    for r_data in roles_config:
        rol, created = Rol.objects.get_or_create(
            nombre=r_data['nombre'],
            defaults={'nivel': r_data['nivel'], 'descripcion': r_data['descripcion']}
        )
        
        # Asignar permisos según el rol
        if rol.nivel == 1: # Admin
            rol.permisos.set(all_perms)
        elif rol.nivel == 2: # Vendedor
            rol.permisos.set(vendedor_perms)
        elif rol.nivel == 3: # Cliente
            rol.permisos.set(cliente_perms)
            
        if created:
            print(f"  [+] Rol creado: {rol.nombre}")
        else:
            print(f"  [OK] Rol verificado: {rol.nombre} ({rol.permisos.count()} permisos)")

def fix_missing_roles():
    """Asigna roles automáticamente basados en flags de Django si no tienen roles"""
    print("\n[i] Buscando usuarios sin roles asignados...")
    
    admin_rol = Rol.objects.filter(nivel=1).first()
    vendedor_rol = Rol.objects.filter(nivel=2).first()
    cliente_rol = Rol.objects.filter(nivel=3).first()
    
    if not admin_rol or not vendedor_rol or not cliente_rol:
        print("[ERROR] Roles básicos no encontrados. Ejecuta primero la configuración.")
        return

    usuarios_sin_rol = Usuario.objects.filter(roles__isnull=True)
    count = usuarios_sin_rol.count()
    
    if count == 0:
        print("[OK] Todos los usuarios tienen al menos un rol.")
        return

    print(f"  [!] Se encontraron {count} usuarios sin roles.")
    
    for user in usuarios_sin_rol:
        if user.is_superuser:
            user.roles.add(admin_rol)
            print(f"    [+] {user.email} -> Administrador (SU)")
        elif user.is_staff:
            user.roles.add(admin_rol)
            print(f"    [+] {user.email} -> Administrador (Dueño de Tienda)")
        else:
            # Si no es staff ni superuser, asumimos que es un usuario con rol Cliente
            # (Aunque en este sistema los compradores suelen ir a la tabla Cliente,
            # si están en Usuario, les asignamos este rol).
            user.roles.add(cliente_rol)
            print(f"    [+] {user.email} -> Cliente (Usuario final)")

def list_user_roles():
    """Muestra un resumen de usuarios y sus roles"""
    print("\n" + "="*80)
    print(f"{'Email':<35} {'Roles':<45}")
    print("-" * 80)
    for user in Usuario.objects.all():
        roles = ", ".join([r.nombre for r in user.roles.all()]) or "NINGUNO âš ï¸"
        print(f"{user.email:<35} {roles:<45}")
    print("="*80)

def main():
    print("\n=== UTILIDAD DE AJUSTE DE ROLES Y PERMISOS ===")
    setup_basic_permissions()
    setup_basic_roles()
    
    print("\nOpciones:")
    print("1. Ver resumen de usuarios y roles")
    print("2. Corregir roles automáticamente (basado en is_superuser/is_staff)")
    print("3. Salir")
    
    choice = input("\nSelecciona una opción: ").strip()
    
    if choice == '1':
        list_user_roles()
    elif choice == '2':
        fix_missing_roles()
        list_user_roles()
    elif choice == '3':
        return
    else:
        print("Opción inválida.")

if __name__ == '__main__':
    main()

