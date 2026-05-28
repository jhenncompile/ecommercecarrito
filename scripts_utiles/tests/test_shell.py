#!/usr/bin/env python
# ========================================================================
# SHELL INTERACTIVO DE PRUEBAS
# ========================================================================
# Consola interactiva con datos de prueba precargados
# Uso: python scripts_utiles/test_shell.py

import os
import sys
import code
try:
    import readline
    import rlcompleter
    if 'libedit' in readline.__doc__:
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind("tab: complete")
except ImportError:
    # Readline no esta disponible en Windows por defecto
    pass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = PROJECT_ROOT / 'backend'
sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django_tenants.utils import schema_context
from django.db import connection

# Importar modelos y utilidades
from apps.customers.models import Client, Usuario, Domain
from apps.negocio.models import Producto
from django.utils import timezone
from django.db.models import Q, Count
import random
from datetime import datetime, timedelta

# ========================================================================
# UTILIDADES DE PRUEBA
# ========================================================================

def crear_tenant_test(nombre="Test Tenant"):
    """Crea un tenant de prueba"""
    tenant, created = Client.objects.get_or_create(
        schema_name=nombre.lower().replace(' ', '_'),
        defaults={'name': nombre}
    )
    print(f"{'[+] Creado:' if created else '[i] Existente:'} {tenant.name}")
    return tenant

def crear_usuario_test(email, password="test123456", es_admin=False):
    """Crea un usuario de prueba"""
    user, created = Usuario.objects.get_or_create(
        email=email,
        defaults={
            'password': password,
            'first_name': email.split('@')[0],
            'last_name': 'Test',
            'is_staff': es_admin,
            'is_superuser': es_admin,
            'is_active': True
        }
    )
    if created:
        user.set_password(password)
        user.save()
        print(f"[+] Usuario creado: {email}")
    else:
        print(f"[i] Usuario existente: {email}")
    return user

def crear_productos_test(cantidad=10):
    """Crea productos de prueba"""
    nombres = [
        f"Producto {i}" for i in range(1, cantidad + 1)
    ]
    
    productos = []
    categorias = ['Electrónica', 'Ropa', 'Libros', 'Hogar', 'Deportes']
    
    for nombre in nombres:
        prod, created = Producto.objects.get_or_create(
            nombre=nombre,
            defaults={
                'descripcion': f"Descripción de {nombre}",
                'precio': round(random.uniform(10, 1000), 2),
                'categoria': random.choice(categorias),
                'stock': random.randint(0, 100),
                'activo': random.choice([True, True, False])
            }
        )
        if created:
            productos.append(prod)
    
    print(f"[+] {len(productos)} productos creados/existentes")
    return productos

# ========================================================================
# CONTEXTO INICIAL
# ========================================================================

def setup_inicial():
    """Setup inicial de datos de prueba"""
    print("\n" + "="*70)
    print("SHELL INTERACTIVO - CONSOLA DE PRUEBAS")
    print("="*70)
    
    print("\n[+] Inicializando datos de prueba...")
    
    # Crear tenant
    tenant = crear_tenant_test("Shell Test")
    
    # Crear usuarios
    print("\n[+] Creando usuarios...")
    admin = crear_usuario_test("admin@test.local", es_admin=True)
    user1 = crear_usuario_test("usuario1@test.local")
    user2 = crear_usuario_test("usuario2@test.local")
    
    # Crear productos y asignar contexto de tenant
    print("\n[+] Configurando esquema del tenant...")
    connection.set_tenant(tenant)
    
    with schema_context(tenant.schema_name):
        print("\n[+] Creando productos...")
        productos = crear_productos_test(15)
    
    print("\n" + "="*70)
    print("VARIABLES DISPONIBLES:")
    print("="*70)
    print("""
  MODELOS:
    - Client, Usuario, Domain, Producto
    - timezone, datetime, timedelta, random
    - Q (queries)

  DATOS DE PRUEBA:
    - tenant       : Tenant de prueba
    - admin        : Usuario admin (admin@test.local / test123456)
    - user1, user2 : Usuarios de prueba
    - productos    : Lista de 15 productos

  FUNCIONES ÃšTILES:
    - crear_tenant_test(nombre)
    - crear_usuario_test(email, password, es_admin)
    - crear_productos_test(cantidad)
    - contar_usuarios()
    - contar_productos()
    - contar_tenants()

  EJEMPLOS:
    >>> tenant.usuarios.count()
    >>> Producto.objects.filter(precio__gt=100)
    >>> user1.email
    >>> admin.is_superuser
    >>> Usuario.objects.all()
    >>> Producto.objects.filter(activo=True).count()

  SALIR:
    >>> exit()
""")
    print("="*70 + "\n")

# ========================================================================
# FUNCIONES HELPER
# ========================================================================

def contar_usuarios():
    """Cuenta usuarios activos"""
    total = Usuario.objects.count()
    activos = Usuario.objects.filter(is_active=True).count()
    print(f"Usuarios: {activos} activos de {total} totales")
    return activos

def contar_productos():
    """Cuenta productos"""
    total = Producto.objects.count()
    activos = Producto.objects.filter(activo=True).count()
    print(f"Productos: {activos} activos de {total} totales")
    return total

def contar_tenants():
    """Cuenta tenants"""
    total = Client.objects.count()
    print(f"Tenants: {total}")
    return total

def listar_usuarios(activos_solo=False):
    """Lista usuarios"""
    query = Usuario.objects.all()
    if activos_solo:
        query = query.filter(is_active=True)
    
    print(f"\n{'Email':<30} {'Nombre':<25} {'Admin'}")
    print("-" * 60)
    for u in query[:10]:
        print(f"{u.email:<30} {u.first_name} {u.last_name:<15} {'Si' if u.is_superuser else ''}")
    if query.count() > 10:
        print(f"...y {query.count() - 10} más")
    return query

def listar_productos():
    """Lista productos"""
    print(f"\n{'ID':<5} {'Nombre':<30} {'Precio':<10} {'Stock':<7} {'Estado'}")
    print("-" * 65)
    for p in Producto.objects.all()[:10]:
        estado = "Activo" if p.activo else "Inactivo"
        print(f"{p.id:<5} {p.nombre:<30} ${p.precio:<9} {p.stock:<7} {estado}")
    if Producto.objects.count() > 10:
        print(f"...y {Producto.objects.count() - 10} más")
    return Producto.objects.all()

# ========================================================================
# MAIN
# ========================================================================

if __name__ == '__main__':
    # Setup inicial
    setup_inicial()
    
    # Crear namespace con variables disponibles
    local_vars = {
        # Modelos
        'Client': Client,
        'Usuario': Usuario,
        'Domain': Domain,
        'Producto': Producto,
        
        # Imports útiles
        'Q': Q,
        'Count': Count,
        'timezone': timezone,
        'datetime': datetime,
        'timedelta': timedelta,
        'random': random,
        
        # Datos precargados
        'tenant': Client.objects.first() or None,
        'admin': Usuario.objects.filter(is_superuser=True).first() or None,
        'user1': Usuario.objects.filter(is_superuser=False).first() or None,
        'user2': Usuario.objects.filter(is_superuser=False).exclude(email=Usuario.objects.filter(is_superuser=False).first().email if Usuario.objects.filter(is_superuser=False).exists() else '').first() or None,
        'productos': list(Producto.objects.all()[:15]),
        
        # Funciones helper
        'crear_tenant_test': crear_tenant_test,
        'crear_usuario_test': crear_usuario_test,
        'crear_productos_test': crear_productos_test,
        'contar_usuarios': contar_usuarios,
        'contar_productos': contar_productos,
        'contar_tenants': contar_tenants,
        'listar_usuarios': listar_usuarios,
        'listar_productos': listar_productos,
    }
    
    # Lanzar shell interactivo
    shell = code.InteractiveConsole(local_vars)
    shell.interact(banner="", exitmsg="[OK] Saliendo del shell de pruebas...")

