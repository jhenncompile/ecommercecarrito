# -*- coding: utf-8 -*-
from scripts_utiles.ui import *
import time

def show_config_menu():
        while True:
            clear_screen()
            print_header("CONFIGURACIÓN")
    
            print_section("Entorno")
            print_option(f"{Colors.YELLOW}W{Colors.RESET} - Asistente Interactivo .env (Wizard)")
            print_option(f"{Colors.CYAN}1{Colors.RESET} - Ver .env")
            print_option(f"{Colors.CYAN}2{Colors.RESET} - Editar .env")
            print_option(f"{Colors.CYAN}r{Colors.RESET} - Restablecer .env desde plantilla")
    
            print_section("Proyecto y Puertos")
            print_option(f"{Colors.CYAN}P{Colors.RESET} - Gestor Rápido de Puertos (Backend/Frontend)")
            print_option(f"{Colors.CYAN}3{Colors.RESET} - Info del proyecto")
            print_option(f"{Colors.CYAN}4{Colors.RESET} - Configuración avanzada (project_config.py)")
            print_option(f"{Colors.CYAN}5{Colors.RESET} - Configurar Dominio SaaS")
    
            print_option(f"\n{Colors.RED}b{Colors.RESET} - Volver")
            print()
    
            choice = input(f"{Colors.BOLD}  ? Selecciona: {Colors.RESET}").strip().lower()
    
            if choice == '1':
                env_file = PROJECT_ROOT / '.env'
                if env_file.exists():
                    print_section("Contenido de .env")
                    print(env_file.read_text(encoding='utf-8'))
                else:
                    print_warning(".env no existe")
                pause()
            elif choice == '2':
                _open_file(PROJECT_ROOT / '.env'); pause()
            elif choice == 'w':
                run_script('core/project_config.py', 'wizard'); pause()
            elif choice == 'p':
                run_script('core/project_config.py', 'ports'); pause()
            elif choice == 'r':
                _reset_env(); pause()
            elif choice == '3':
                print_section("Información del Proyecto")
                print(f"  Ruta:     {PROJECT_ROOT}")
                print(f"  Backend:  {BACKEND_DIR}")
                print(f"  Frontend: {FRONTEND_DIR}")
                print(f"  Scripts:  {SCRIPTS_DIR}")
                pause()
            elif choice == '4':
                run_script('core/project_config.py'); pause()
            elif choice == '5':
                _setup_saas_domain(); pause()
            elif choice == 'b':
                break
            else:
                print_error("Opción inválida"); time.sleep(1)