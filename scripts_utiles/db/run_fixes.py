import os
import glob
import importlib.util
from scripts_utiles.ui import print_info, print_success, print_error, print_header

def main():
    print_header("ORQUESTADOR DE FIXES (REPARACIONES)")
    fixes_dir = os.path.join(os.path.dirname(__file__), 'fixes')
    
    if not os.path.exists(fixes_dir):
        os.makedirs(fixes_dir)
        print_info("Directorio de fixes creado.")
        
    fix_files = sorted(glob.glob(os.path.join(fixes_dir, '[0-9]*.py')))
    
    if not fix_files:
        print_info("No se encontraron scripts de fix para ejecutar.")
        return

    print_info(f"Se encontraron {len(fix_files)} fixes para ejecutar.\n")
    
    todos_exitosos = True
    
    for fix_path in fix_files:
        fix_name = os.path.basename(fix_path)
        print_info(f"--- Ejecutando Fix: {fix_name} ---")
        try:
            spec = importlib.util.spec_from_file_location(fix_name[:-3], fix_path)
            fix_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(fix_module)
            
            if hasattr(fix_module, 'run'):
                success = fix_module.run()
                if success:
                    print_success(f"[OK] {fix_name} ejecutado correctamente.\n")
                else:
                    print_error(f"[ERROR] {fix_name} reportó un fallo al ejecutarse.\n")
                    todos_exitosos = False
            else:
                print_error(f"[ERROR] {fix_name} no tiene una función run().\n")
                todos_exitosos = False
        except Exception as e:
            print_error(f"[EXCEPTION] Ocurrió un error en {fix_name}: {e}\n")
            todos_exitosos = False

    if todos_exitosos:
        print_success("Todos los fixes se aplicaron correctamente. El sistema está limpio y actualizado.")
    else:
        print_error("Algunos fixes fallaron. Revisa los logs arriba.")

if __name__ == '__main__':
    main()
