# -*- coding: utf-8 -*-
from scripts_utiles.ui import *
import time

def show_users_menu():
        while True:
            clear_screen()
            print_header("GESTIÓN DE USUARIOS")
    
            print_section("Operaciones Básicas (CRUD)")
            print_option(f"{Colors.YELLOW}1{Colors.RESET} - Crear nuevo usuario")
            print_option(f"{Colors.YELLOW}2{Colors.RESET} - Listar usuarios")
            print_option(f"{Colors.YELLOW}3{Colors.RESET} - Cambiar contraseña de usuario")
            print_option(f"{Colors.YELLOW}4{Colors.RESET} - Eliminar usuario")
    
            print_section("Estado y Control de Acceso")
            print_option(f"{Colors.CYAN}5{Colors.RESET} - Ver estado")
            print_option(f"{Colors.GREEN}6{Colors.RESET} - Activar usuario")
            print_option(f"{Colors.RED}7{Colors.RESET} - Desactivar usuario")
    
            print_section("Roles y Permisos")
            print_option(f"{Colors.CYAN}8{Colors.RESET} - Ver roles disponibles")
            print_option(f"{Colors.MAGENTA}9{Colors.RESET} - Asignar ROL a usuario")
            print_option(f"{Colors.YELLOW}I{Colors.RESET} - Inicializar Roles y Permisos básicos")
            print_option(f"{Colors.YELLOW}S{Colors.RESET} - {Colors.BOLD}Sincronizar/Ajustar ROLES (Fix){Colors.RESET}")
    
            print_option(f"\n{Colors.RED}b{Colors.RESET} - Volver")
            print()
    
            choice = input(f"{Colors.BOLD}  ? Selecciona: {Colors.RESET}").strip().lower()
    
            if choice == '1':
                email = input("Email del nuevo usuario: ").strip()
                password = input("Contraseña del nuevo usuario: ").strip()
                if email and password:
                    run_script('users/manage_users.py', '--create', email, '--pass', password)
                else:
                    print_error("Email y contraseña requeridos.")
                pause()
            elif choice == '2':
                run_script('users/manage_users.py', '--list')
                pause()
            elif choice == '3':
                email = input("Email del usuario a modificar: ").strip()
                password = input("Nueva contraseña: ").strip()
                if email and password:
                    run_script('users/manage_users.py', '--edit', email, '--pass', password)
                else:
                    print_error("Email y contraseña requeridos.")
                pause()
            elif choice == '4':
                email = input("Email del usuario a eliminar: ").strip()
                if email:
                    confirm = input(f"¿Seguro que deseas eliminar a {email}? (s/n): ").strip().lower()
                    if confirm == 's':
                        run_script('users/manage_users.py', '--delete', email)
                else:
                    print_error("Email requerido.")
                pause()
            elif choice == '5':
                email = input("Email del usuario: ").strip()
                if email:
                    run_script('users/manage_users.py', '--status', email)
                else:
                    print_error("Email requerido.")
                pause()
            elif choice == '6':
                email = input("Email del usuario a activar: ").strip()
                if email:
                    run_script('users/manage_users.py', '--activate', email)
                else:
                    print_error("Email requerido.")
                pause()
            elif choice == '7':
                email = input("Email del usuario a desactivar: ").strip()
                if email:
                    run_script('users/manage_users.py', '--disable', email)
                else:
                    print_error("Email requerido.")
                pause()
            elif choice == '8':
                run_script('users/manage_users.py', '--list-roles')
                pause()
            elif choice == '9':
                email = input("Email del usuario: ").strip()
                if email:
                    print("\nRoles disponibles:")
                    print("1 - Super Usuario (Admin)")
                    print("2 - Vendedor")
                    print("3 - Cliente")
                    rol_choice = input("Selecciona el rol (1-3): ").strip()
                    if rol_choice == '1':
                        run_script('users/manage_users.py', '--set-su', email)
                    elif rol_choice == '2':
                        run_script('users/manage_users.py', '--set-vendedor', email)
                    elif rol_choice == '3':
                        run_script('users/manage_users.py', '--set-cliente', email)
                    else:
                        print_error("Opción de rol inválida.")
                else:
                    print_error("Email requerido.")
                pause()
            elif choice == 'i':
                run_script('users/manage_users.py', '--init')
                pause()
            elif choice == 's':
                run_script('users/fix_roles.py')
                pause()
            elif choice == 'b':
                break
            else:
                print_error("Opción inválida"); time.sleep(1)