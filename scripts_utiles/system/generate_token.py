#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import secrets

# Asegurar que la ruta base esté en sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from scripts_utiles.ui import print_header, print_success, print_error, print_info, Colors, pause

def update_env_file(env_path, new_secret):
    if not os.path.exists(env_path):
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(f"MOBILE_UPLOAD_SECRET={new_secret}\n")
        return
    
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    found = False
    with open(env_path, 'w', encoding='utf-8') as f:
        for line in lines:
            if line.startswith('MOBILE_UPLOAD_SECRET='):
                f.write(f"MOBILE_UPLOAD_SECRET={new_secret}\n")
                found = True
            else:
                f.write(line)
        if not found:
            f.write(f"\nMOBILE_UPLOAD_SECRET={new_secret}\n")

def update_compile_script(script_path, new_secret):
    if not os.path.exists(script_path):
        return False
        
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    import re
    new_content = re.sub(r'UPLOAD_SECRET\s*=\s*".*?"', f'UPLOAD_SECRET = "{new_secret}"', content)
    
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return True

def main():
    print_header("GENERAR TOKEN SEGURO DE SUBIDA DE APPS")
    
    # Generar token aleatorio de 64 caracteres
    new_secret = secrets.token_hex(32)
    print_info("Generando nuevo token criptográfico...")
    print(f"Token generado: {Colors.CYAN}{new_secret}{Colors.RESET}")
    
    # 1. Actualizar .env
    env_path = os.path.join(BASE_DIR, '.env')
    try:
        update_env_file(env_path, new_secret)
        print_success("Archivo .env actualizado con éxito.")
    except Exception as e:
        print_error(f"Error actualizando .env: {e}")
        
    # 2. Actualizar compile_and_upload_apps.py
    compile_script_path = os.path.join(BASE_DIR, 'compile_and_upload_apps.py')
    try:
        if update_compile_script(compile_script_path, new_secret):
            print_success("Script compile_and_upload_apps.py actualizado con éxito.")
        else:
            print_error("No se encontró compile_and_upload_apps.py para actualizar.")
    except Exception as e:
        print_error(f"Error actualizando compile_and_upload_apps.py: {e}")
        
    print()
    print_success("¡TODO LISTO! La conexión entre tu compilador y el backend ahora es segura.")
    print_info("NOTA: Si despliegas a tu VPS, no olvides copiar este MOBILE_UPLOAD_SECRET")
    print_info("en el archivo .env de tu servidor para que acepte las subidas.")
    
if __name__ == '__main__':
    main()
