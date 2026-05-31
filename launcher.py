#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ========================================================================
# LANZADOR UNIVERSAL - WINDOWS / LINUX / MAC
# ========================================================================
import sys
import time
from scripts_utiles.ui import *

# Importar modulos de interfaz
from scripts_utiles.db.menu import show_data_menu
from scripts_utiles.users.menu import show_users_menu
from scripts_utiles.system.menu import show_system_menu, show_services_menu
from scripts_utiles.core.menu import show_config_menu
from scripts_utiles.flutter.menu import show_flutter_menu
from scripts_utiles.utils.menu import show_scripts_menu

def show_main_menu():
    while True:
        clear_screen()
        print_header("LANZADOR DE PROYECTO")
        print_section(f"Sistema Operativo: {SISTEMA_OPERATIVO}")

        print_section("EJECUCIÓN")
        print_option(f"{Colors.GREEN}1{Colors.RESET} - Iniciar Backend (Django)")
        print_option(f"{Colors.GREEN}2{Colors.RESET} - Iniciar Frontend (React)")
        print_option(f"{Colors.BOLD}{Colors.GREEN}3{Colors.RESET} - {Colors.BOLD}INICIAR TODO (Backend + Frontend){Colors.RESET}")
        print_option(f"{Colors.BOLD}{Colors.YELLOW}M{Colors.RESET} - {Colors.BOLD}SINCRONIZAR BASE DE DATOS (Migrations){Colors.RESET}")

        print_section("APPS MÓVILES (Flutter)")
        ip = ENV_CONFIG.get('DOMAIN_MAIN', '?')
        port = ENV_CONFIG.get('DJANGO_PORT', '8001')
        print_option(f"{Colors.BOLD}{Colors.CYAN}F{Colors.RESET} - {Colors.BOLD}Apps Móviles (movil / mcliente){Colors.RESET}  {Colors.GRAY}-> API: {ip}:{port}{Colors.RESET}")

        print_section("DATOS Y USUARIOS")
        print_option(f"{Colors.CYAN}4{Colors.RESET} - Gestión de Base de Datos y Usuarios")
        print_option(f"{Colors.CYAN}5{Colors.RESET} - Gestión de Usuarios (Acceso Rápido)")

        print_section("CONFIGURACIÓN Y SISTEMA")
        print_option(f"{Colors.YELLOW}I{Colors.RESET} - Instalación Rápida (Plug & Play)")
        print_option(f"{Colors.YELLOW}D{Colors.RESET} - Instalar Dependencias (Back, Front, Flutter)")
        print_option(f"{Colors.YELLOW}T{Colors.RESET} - Generar Token Seguro para subir Apps Móviles")
        print_option(f"{Colors.YELLOW}X{Colors.RESET} - Ejecutar Fixes y Reparaciones (VPS y Local)")
        print_option(f"{Colors.CYAN}6{Colors.RESET} - Configuración de Entorno (.env)")
        print_option(f"{Colors.CYAN}7{Colors.RESET} - Servicios del Sistema (IP directa)")
        print_option(f"{Colors.CYAN}8{Colors.RESET} - Mantenimiento del Sistema")

        print_section("DESARROLLO")
        print_option(f"{Colors.BLUE}9{Colors.RESET}  - Consola de Pruebas (Django Shell)")
        print_option(f"{Colors.BLUE}10{Colors.RESET} - Todos los Scripts (Avanzado)")

        print_option(f"\n{Colors.RED}0{Colors.RESET} - Salir")
        print()

        choice = input(f"{Colors.BOLD}  ? Selecciona: {Colors.RESET}").strip().lower()

        if choice == '1':
            run_script('core/run_services.py', 'backend', use_venv=False)
        elif choice == '2':
            run_script('core/run_services.py', 'frontend', use_venv=False)
        elif choice in ('3', 'a'):
            run_script('core/run_services.py', 'all', use_venv=False)
        elif choice == 'm':
            run_script('db/migrations.py', 'sync')
            pause()
        elif choice == '4':
            show_data_menu()
        elif choice == '5':
            show_users_menu()
        elif choice == 'i':
            run_script('system/system_setup.py', use_venv=False)
            pause()
        elif choice == 'd':
            run_script('system/install_deps.py', use_venv=False)
            pause()
        elif choice == 't':
            run_script('system/generate_token.py', use_venv=False)
            pause()
        elif choice == 'x':
            run_script('db/run_fixes.py')
            pause()
        elif choice == '6':
            show_config_menu()
        elif choice == '7':
            show_services_menu()
        elif choice == '8':
            show_system_menu()
        elif choice == '9':
            run_script('tests/test_shell.py')
            pause()
        elif choice == '10':
            show_scripts_menu()
        elif choice == 'f':
            show_flutter_menu()
        elif choice == '0':
            print_info("¡Adiós!")
            sys.exit(0)
        else:
            print_error("Opción inválida")
            time.sleep(1)

if __name__ == '__main__':
    try:
        show_main_menu()
    except KeyboardInterrupt:
        print_info("\nSaliendo...")
        sys.exit(0)
