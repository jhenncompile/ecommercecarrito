# -*- coding: utf-8 -*-
from scripts_utiles.ui import *
import time
import shutil
import subprocess

def _get_flutter_dart_defines():
        """Construye los flags --dart-define a partir del .env."""
        ip   = ENV_CONFIG.get('DOMAIN_MAIN', 'localhost')
        port = ENV_CONFIG.get('DJANGO_PORT', '8001')
        return [f'--dart-define=API_IP={ip}', f'--dart-define=API_PORT={port}']

def _run_flutter(app_dir, extra_args=None):
        """Ejecuta un comando flutter pasando los dart-defines del .env."""
        flutter = shutil.which('flutter') or 'flutter'
        defines = _get_flutter_dart_defines()
        cmd = [flutter] + (extra_args or []) + defines
        print_info(f"Directorio: {app_dir}")
        print_info(f"Comando: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, cwd=str(app_dir))
        except KeyboardInterrupt:
            print_warning("\nCancelado.")
        except FileNotFoundError:
            print_error("flutter no encontrado en el PATH. Instala Flutter SDK.")

def show_flutter_menu():
        global ENV_CONFIG
        MOVIL_DIR   = PROJECT_ROOT / 'movil'
        MCLIENTE_DIR = PROJECT_ROOT / 'mcliente'
    
        while True:
            clear_screen()
            ip   = ENV_CONFIG.get('DOMAIN_MAIN', '?')
            port = ENV_CONFIG.get('DJANGO_PORT', '8001')
            print_header("APPS MÓVILES (Flutter)")
            print_info(f"API configurada: {Colors.YELLOW}http://{ip}:{port}/api{Colors.RESET}")
            print_info(f"Sufijo tenants:  {Colors.YELLOW}.<ip>.nip.io{Colors.RESET}")
            print()
    
            print_section("movil (App del Vendedor)")
            print_option(f"{Colors.GREEN}1{Colors.RESET} - flutter run  (debug, con IP del .env)")
            print_option(f"{Colors.CYAN}2{Colors.RESET} - flutter build apk  (release)")
            print_option(f"{Colors.CYAN}3{Colors.RESET} - flutter build apk --debug")
    
            print_section("mcliente (App del Cliente/Comprador)")
            print_option(f"{Colors.GREEN}4{Colors.RESET} - flutter run  (debug, con IP del .env)")
            print_option(f"{Colors.CYAN}5{Colors.RESET} - flutter build apk  (release)")
            print_option(f"{Colors.CYAN}6{Colors.RESET} - flutter build apk --debug")
    
            print_section("Configuración")
            print_option(f"{Colors.YELLOW}C{Colors.RESET} - Cambiar IP/Puerto de la API (edita .env)")
    
            print_option(f"\n{Colors.RED}b{Colors.RESET} - Volver")
            print()
    
            choice = input(f"{Colors.BOLD}  ? Selecciona: {Colors.RESET}").strip().lower()
    
            if choice == '1':
                _run_flutter(MOVIL_DIR, ['run'])
            elif choice == '2':
                _run_flutter(MOVIL_DIR, ['build', 'apk', '--release'])
                print_success(f"APK en: {MOVIL_DIR}/build/app/outputs/flutter-apk/app-release.apk")
                pause()
            elif choice == '3':
                _run_flutter(MOVIL_DIR, ['build', 'apk', '--debug'])
                print_success(f"APK en: {MOVIL_DIR}/build/app/outputs/flutter-apk/app-debug.apk")
                pause()
            elif choice == '4':
                _run_flutter(MCLIENTE_DIR, ['run'])
            elif choice == '5':
                _run_flutter(MCLIENTE_DIR, ['build', 'apk', '--release'])
                print_success(f"APK en: {MCLIENTE_DIR}/build/app/outputs/flutter-apk/app-release.apk")
                pause()
            elif choice == '6':
                _run_flutter(MCLIENTE_DIR, ['build', 'apk', '--debug'])
                print_success(f"APK en: {MCLIENTE_DIR}/build/app/outputs/flutter-apk/app-debug.apk")
                pause()
            elif choice == 'c':
                new_ip = input(f"  Nueva IP/dominio del servidor [{ip}]: ").strip()
                if new_ip:
                    # Re-usar la función de escritura del launcher
                    env_path = PROJECT_ROOT / '.env'
                    lines = []
                    found = False
                    if env_path.exists():
                        with open(env_path, 'r', encoding='utf-8') as f:
                            for line in f:
                                if line.strip().startswith('DOMAIN_MAIN='):
                                    lines.append(f'DOMAIN_MAIN={new_ip}\n')
                                    found = True
                                else:
                                    lines.append(line)
                    if not found:
                        lines.append(f'DOMAIN_MAIN={new_ip}\n')
                    with open(env_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    # Recargar config
                    ENV_CONFIG = load_env_manual()
                    print_success(f"IP actualizada a: {new_ip}")
                pause()
            elif choice == 'b':
                break
            else:
                print_error("Opción inválida")
                time.sleep(1)