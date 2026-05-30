# -*- coding: utf-8 -*-
from scripts_utiles.ui import *
import time
import subprocess

def show_services_menu():
        while True:
            clear_screen()
            print_header("SERVICIOS DEL SISTEMA")
    
            print_option(f"  {Colors.CYAN}1{Colors.RESET} - {Colors.BOLD}IP directa{Colors.RESET} (Crear servicios systemd)")
    
            print_section("Mantenimiento")
            print_option(f"  {Colors.CYAN}2{Colors.RESET} - Ver estado servicios")
            print_option(f"  {Colors.CYAN}3{Colors.RESET} - Ver logs")
            print_option(f"  {Colors.CYAN}4{Colors.RESET} - Reiniciar todo")
            print_option(f"  {Colors.CYAN}5{Colors.RESET} - Consultar Dominios / Tenants")
    
            print_section("Peligro")
            print_option(f"  {Colors.RED}D{Colors.RESET} - Eliminar TODOS los servicios")
    
            print_option(f"\n  {Colors.RED}b{Colors.RESET} - Volver")
            print()
    
            choice = input(f"{Colors.BOLD}  ? Selecciona: {Colors.RESET}").strip().lower()
    
            if choice == '1':
                loading_animation(1, "Preparando servicios IP directa")
                run_script('system/services.py', 'create-all-ip'); pause()
            elif choice == '2':
                run_script('system/services.py', 'status'); pause()
            elif choice == '3':
                run_script('system/services.py', 'logs'); pause()
            elif choice == '4':
                run_script('system/services.py', 'restart'); pause()
            elif choice == '5':
                run_script('utils/query_domains.py'); pause()
            elif choice == 'd':
                if input(f"{Colors.RED}  ¿Eliminar TODOS los servicios? (s/n): {Colors.RESET}").lower() == 's':
                    run_script('system/services.py', 'delete-all')
                pause()
            elif choice == 'b':
                break
            else:
                print_error("Opción inválida"); time.sleep(1)

def show_system_menu():
        while True:
            clear_screen()
            print_header("GESTIÓN DE SISTEMA Y MANTENIMIENTO")
    
            print_section("Actualización")
            print_option(f"{Colors.CYAN}1{Colors.RESET} - Actualizar Django (pip install)")
            print_option(f"{Colors.CYAN}2{Colors.RESET} - Reinstalación limpia de Frontend (npm install)")
            print_option(f"{Colors.CYAN}3{Colors.RESET} - Actualizar Sistema Operativo (apt)")
    
            print_section("Seguridad y VPS")
            print_option(f"{Colors.MAGENTA}V{Colors.RESET} - Panel de Control VPS")
            print_option(f"{Colors.CYAN}4{Colors.RESET} - Generar Secrets (JWT/Django)")
    
            print_section("Estado y Mantenimiento")
            print_option(f"{Colors.CYAN}6{Colors.RESET} - Salud del Sistema")
            print_option(f"{Colors.YELLOW}C{Colors.RESET} - Limpiar Caché (Django/Pyc)")
            print_option(f"{Colors.YELLOW}M{Colors.RESET} - Limpiar Imágenes Huérfanas (Media)")
            print_option(f"{Colors.YELLOW}L{Colors.RESET} - Configurar Logrotate (Linux)")

            print_option(f"\n{Colors.RED}b{Colors.RESET} - Volver")
            print()
    
            choice = input(f"{Colors.BOLD}  ? Selecciona: {Colors.RESET}").strip().lower()
    
            if choice == '1':
                loading_animation(2, "Actualizando")
                run_script('system/system_manager.py', 'update-django'); pause()
            elif choice == '2':
                loading_animation(2, "Actualizando")
                run_script('system/system_manager.py', 'update-npm'); pause()
            elif choice == '3':
                loading_animation(3, "Actualizando")
                run_script('system/system_manager.py', 'update-system'); pause()
            elif choice == 'v':
                show_vps_menu()
            elif choice == '4':
                run_script('system/system_manager.py', 'generate-secrets'); pause()
            elif choice == '6':
                run_script('system/system_manager.py', 'health-check'); pause()
            elif choice == 'c':
                run_script('system/system_manager.py', 'clean-cache'); pause()
            elif choice == 'm':
                run_script('system/system_manager.py', 'clean-media'); pause()
            elif choice == 'l':
                run_script('system/system_manager.py', 'setup-logrotate'); pause()
            elif choice == 'b':
                break
            else:
                print_error("Opción inválida"); time.sleep(1)

def show_vps_menu():
        while True:
            clear_screen()
            print_header("PANEL DE CONTROL VPS")
    
            print_section("Resiliencia y Monitoreo")
            print_option(f"{Colors.GREEN}1{Colors.RESET} - Estado y Auto-Healing")
            print_option(f"{Colors.GREEN}M{Colors.RESET} - Monitor de Recursos en Vivo (CPU/RAM)")
            print_option(f"{Colors.CYAN}2{Colors.RESET} - Auditoría de Firewall (UFW)")
            print_option(f"{Colors.RED}F{Colors.RESET} - Instalar y Configurar Fail2Ban")
            print_option(f"{Colors.YELLOW}L{Colors.RESET} - Log Analyzer (Ver Logs en vivo)")

            print_section("Certificados SSL")
            print_option(f"{Colors.CYAN}3{Colors.RESET} - Prueba de Renovación SSL")
            print_option(f"{Colors.GREEN}C{Colors.RESET} - Crear Nuevo Certificado SSL (Certbot)")

            print_section("Respaldos")
            print_option(f"{Colors.YELLOW}S{Colors.RESET} - Crear SNAPSHOT")
            print_option(f"{Colors.YELLOW}R{Colors.RESET} - Restaurar desde SNAPSHOT")

            print_section("Mantenimiento")
            print_option(f"{Colors.CYAN}4{Colors.RESET} - Limpieza del Sistema")
            print_option(f"{Colors.CYAN}7{Colors.RESET} - Limpieza Profunda Frontend (borrar build y reconstruir)")
            print_option(f"{Colors.CYAN}5{Colors.RESET} - Crear Usuario de Sistema")
            print_option(f"{Colors.GREEN}8{Colors.RESET} - {Colors.BOLD}Sincronizar Hora (La Paz, UTC-4){Colors.RESET}")
    
            print_option(f"\n{Colors.RED}b{Colors.RESET} - Volver")
            print()
    
            choice = input(f"{Colors.BOLD}  ? Selecciona: {Colors.RESET}").strip().lower()
    
            if choice == '1':
                run_script('system/vps.py', 'services', 'AUTOHEAL'); pause()
            elif choice == 'm':
                run_script('system/vps.py', 'services', 'MONITOR')
            elif choice == '2':
                run_script('system/vps.py', 'security', 'FW'); pause()
            elif choice == 'f':
                run_script('system/vps.py', 'security', 'FAIL2BAN'); pause()
            elif choice == 'l':
                svc = input("¿Qué servicio? (django/syslog): ").strip().lower()
                run_script('system/vps.py', 'logs', 'ANALYZE', svc)
            elif choice == '3':
                run_script('system/vps.py', 'ssl', 'RENEW'); pause()
            elif choice == 'c':
                dom = input("Dominio (ej: saas.com): ").strip()
                email = input("Email para registro SSL: ").strip()
                run_script('system/vps.py', 'ssl', 'CREATE', dom, email); pause()
            elif choice == 's':
                name = input("Nombre del snapshot: ").strip()
                run_script('system/vps.py', 'backup', 'SNAPSHOT', name); pause()
            elif choice == 'r':
                run_script('system/vps.py', 'backup', 'RESTORE'); pause()
            elif choice == '4':
                run_script('system/vps.py', 'system', 'CLEAN'); pause()
            elif choice == '7':
                _deep_clean_frontend(); pause()
            elif choice == '5':
                user = input("Nombre de usuario: ")
                pw   = input("Contraseña: ")
                run_script('system/vps.py', 'user', 'CREATE', user, pw); pause()
            elif choice == '8':
                print_info("Sincronizando reloj con America/La_Paz...")
                subprocess.run(['sudo', 'timedatectl', 'set-timezone', 'America/La_Paz'], check=False)
                print_success("Hora del sistema actualizada:")
                subprocess.run(['date'], check=False)
                pause()
            elif choice == 'b':
                break
            else:
                print_error("Opción inválida"); time.sleep(1)