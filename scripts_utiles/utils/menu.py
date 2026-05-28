# -*- coding: utf-8 -*-
from scripts_utiles.ui import *
import time

def show_scripts_menu():
        while True:
            clear_screen()
            print_header("SCRIPTS ÚTILES")
            print_option(f"{Colors.CYAN}1{Colors.RESET} - db_reset.py")
            print_option(f"{Colors.CYAN}2{Colors.RESET} - db_seed.py")
            print_option(f"{Colors.CYAN}3{Colors.RESET} - manage_users.py")
            print_option(f"{Colors.CYAN}4{Colors.RESET} - test_shell.py")
            print_option(f"\n{Colors.RED}b{Colors.RESET} - Volver")
            print()
    
            choice = input(f"{Colors.BOLD}  ? Selecciona: {Colors.RESET}").strip().lower()
            scripts = {'1': 'db/db_reset.py', '2': 'db/db_seed.py',
                       '3': 'users/manage_users.py', '4': 'tests/test_shell.py'}
            if choice in scripts:
                run_script(scripts[choice]); pause()
            elif choice == 'b':
                break
            else:
                print_error("Opción inválida"); time.sleep(1)