# -*- coding: utf-8 -*-
from scripts_utiles.ui import *
import time

def show_data_menu():
        while True:
            clear_screen()
            print_header("GESTIÓN DE BASE DE DATOS Y DATOS")
    
            print_section("1. Configuración")
            print_option(f"{Colors.CYAN}1{Colors.RESET} - Configurar Conexión (db_config.py)")
            print_option(f"{Colors.CYAN}2{Colors.RESET} - Probar Conexión")
    
            print_section("2. Estructura y Migraciones")
            print_option(f"{Colors.BLUE}3{Colors.RESET} - Sincronización Total (makemigrations + migrate)")
            print_option(f"{Colors.BLUE}4{Colors.RESET} - Ver historial de Migraciones")
    
            print_section("3. Contenido")
            print_option(f"{Colors.YELLOW}5{Colors.RESET} - Gestión de Usuarios (CRUD Completo)")
            print_option(f"{Colors.YELLOW}6{Colors.RESET} - Ejecutar Seeders (Poblar con datos de prueba)")
            print_option(f"{Colors.YELLOW}P{Colors.RESET} - Sembrar Permisos del Sistema (Obligatorio 1ra vez)")
    
            print_section("4. Reparación y Emergencia")
            print_option(f"{Colors.RED}F{Colors.RESET} - Reparar Migraciones (Error: Columna ya existe)")
            print_option(f"{Colors.RED}C{Colors.RESET} - Corregir Migraciones (Error: Columna NO existe / es_basico)")
    
            print_section("4. Auditoría")
            print_option(f"{Colors.MAGENTA}7{Colors.RESET} - Ver Auditoría Reciente (Bitácora)")

            print_section("5. Respaldos y Optimización")
            print_option(f"{Colors.GREEN}S{Colors.RESET} - Respaldar Base de Datos (Backup)")
            print_option(f"{Colors.GREEN}R{Colors.RESET} - Restaurar Base de Datos (Restore)")
            print_option(f"{Colors.GREEN}V{Colors.RESET} - Optimizar Base de Datos (Vacuum)")
    
            print_section("6. Limpieza (CUIDADO)")
            print_option(f"{Colors.RED}8{Colors.RESET} - Resetear BD Completa")
    
            print_section("7. Utilidades")
            print_option(f"{Colors.YELLOW}9{Colors.RESET} - Sanear Dominios de Tenants (quitar guiones bajos)")
    
            print_option(f"\n{Colors.RED}b{Colors.RESET} - Volver")
            print()
    
            choice = input(f"{Colors.BOLD}  ? Selyecciona: {Colors.RESET}").strip().lower()
    
            if choice == '1':
                run_script('db/db_config.py'); pause()
            elif choice == '2':
                run_script('db/db_config.py', 'test'); pause()
            elif choice == '3':
                run_script('db/migrations.py', 'sync'); pause()
            elif choice == '4':
                run_script('db/migrations.py', 'show'); pause()
            elif choice == '5':
                from scripts_utiles.users.menu import show_users_menu
                show_users_menu()
            elif choice == '6':
                run_script('db/db_seed.py'); pause()
            elif choice == 'p':
                run_script('db/migrations.py', 'seed_permisos'); pause()
            elif choice == '7':
                run_script('tests/unit/verify_audit.py'); pause()
            elif choice == 's':
                run_script('db/db_backup.py', 'backup'); pause()
            elif choice == 'r':
                run_script('db/db_backup.py', 'restore'); pause()
            elif choice == 'v':
                run_script('db/db_backup.py', 'vacuum'); pause()
            elif choice == '8':
                if input(f"{Colors.RED}¿SEGURO? Borra todo. (s/n): {Colors.RESET}").lower() == 's':
                    run_script('db/db_reset.py', 'all')
                pause()
            elif choice == '9':
                print_info("Buscando dominios con guiones bajos...")
                run_script('utils/fix_tenant_domains.py'); pause()
            elif choice == 'f':
                run_script('db/migrations.py', 'fake'); pause()
            elif choice == 'c':
                run_script('db/migrations.py', 'fix_missing'); pause()
            elif choice == 'b':
                break
            else:
                print_error("Opción inválida"); time.sleep(1)