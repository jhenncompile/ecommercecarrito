import os
import subprocess
import sys

# Instalador automático de dependencias
try:
    import yaml
    import requests
    from dotenv import load_dotenv
    import requests_toolbelt
    import tqdm
except ImportError:
    print("❌ Faltan dependencias. Instalando pyyaml, requests, python-dotenv, requests-toolbelt y tqdm...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyyaml", "requests", "python-dotenv", "requests-toolbelt", "tqdm"])
    print("✅ Dependencias instaladas. Por favor, ejecuta el script de nuevo.")
    sys.exit(0)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

# ConfiguraciÃ³n
SERVER_IP = "157.173.102.129"
SERVER_PORT = "8001"
API_URL = f"http://{SERVER_IP}:{SERVER_PORT}/api/public/apps/upload/"
UPLOAD_SECRET = os.environ.get('MOBILE_UPLOAD_SECRET', 'miqhatu_super_secret_upload_token_2026')

# Rutas a los proyectos Flutter
APPS = {
    'cliente': {
        'path': os.path.join(BASE_DIR, 'mcliente'),
        'apk_path': os.path.join(BASE_DIR, 'mcliente', 'build', 'app', 'outputs', 'flutter-apk', 'app-release.apk')
    },
    'vendedor': {
        'path': os.path.join(BASE_DIR, 'movil'),
        'apk_path': os.path.join(BASE_DIR, 'movil', 'build', 'app', 'outputs', 'flutter-apk', 'app-release.apk')
    }
}

def get_version_from_pubspec(app_path):
    pubspec_path = os.path.join(app_path, 'pubspec.yaml')
    if not os.path.exists(pubspec_path):
        print(f"âŒ Error: No se encontrÃ³ {pubspec_path}")
        return None
    
    with open(pubspec_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        version_string = data.get('version', '1.0.0+1')
        # Version usually format like "1.0.0+1" or "1.0.0"
        version = version_string.split('+')[0]
        return version

def compile_and_upload(app_type, install=False):
    print(f"\n{'='*50}")
    print(f"🚀 INICIANDO COMPILACIÓN: APP {app_type.upper()}")
    print(f"{'='*50}")

    app_config = APPS[app_type]
    app_path = app_config['path']
    apk_path = app_config['apk_path']

    if not os.path.exists(app_path):
        print(f"❌ Error: La carpeta del proyecto {app_path} no existe.")
        return False

    version = get_version_from_pubspec(app_path)
    if not version:
        return False
    
    print(f"📦 Versión detectada: {version}")
    print("⏳ Compilando APK (Release)... Esto puede tardar varios minutos.")

    # Ejecutar flutter build apk con las variables inyectadas
    build_cmd = [
        "flutter", "build", "apk", "--release",
        f"--dart-define=API_IP={SERVER_IP}",
        f"--dart-define=API_PORT={SERVER_PORT}"
    ]
    
    print(f"🔧 Inyectando variables: API_IP={SERVER_IP}, API_PORT={SERVER_PORT}")
    
    result = subprocess.run(
        build_cmd,
        cwd=app_path,
        shell=True # Necesario en Windows para encontrar 'flutter' si estÃ¡ en el PATH
    )

    if result.returncode != 0:
        print(f"\n❌ Error durante la compilaciÃ³n de {app_type}. Abortando subida.")
        return False

    print("\n✅ CompilaciÃ³n terminada con Ã©xito.")
    
    if not os.path.exists(apk_path):
        print(f"❌ Error: No se encontrÃ³ el APK generado en {apk_path}.")
        return False

    if install:
        print("📱 Instalando APK en el dispositivo vía ADB...")
        install_cmd = ["adb", "install", "-r", apk_path]
        res = subprocess.run(install_cmd, shell=True)
        if res.returncode == 0:
            print("✅ Aplicación instalada en el dispositivo correctamente.")
        else:
            print("⚠️ Error al instalar la aplicación (¿Dispositivo no conectado?).")

    print("☁️  Subiendo APK al servidor...")
    
    try:
        from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
        from tqdm import tqdm
    except ImportError:
        print("❌ Faltan dependencias para la barra de progreso (requests_toolbelt, tqdm).")
        print("   Se instalarán la próxima vez que inicies el script. Subiendo sin barra por ahora...")
        with open(apk_path, 'rb') as f:
            files = {'file': (f"release_{app_type}_{version}.apk", f, 'application/vnd.android.package-archive')}
            data = {'app_type': app_type, 'version': version}
            headers = {'X-Upload-Secret': UPLOAD_SECRET}
            try:
                response = requests.post(API_URL, data=data, files=files, headers=headers)
                if response.status_code == 201:
                    res_data = response.json()
                    print(f"✅ ¡Éxito! APK subido correctamente.")
                    print(f"🔗 URL Pública: {res_data.get('url')}")
                else:
                    print(f"❌ Error del servidor al subir ({response.status_code}): {response.text}")
                    return False
            except requests.exceptions.RequestException as e:
                print(f"❌ Error de red al conectar con el servidor: {e}")
                return False
        return True

    with open(apk_path, 'rb') as f:
        encoder = MultipartEncoder(
            fields={
                'app_type': app_type,
                'version': version,
                'file': (f"release_{app_type}_{version}.apk", f, 'application/vnd.android.package-archive')
            }
        )
        
        with tqdm(total=encoder.len, unit='B', unit_scale=True, unit_divisor=1024, desc=f"🚀 Subiendo {app_type}") as bar:
            def callback(monitor):
                bar.update(monitor.bytes_read - bar.n)

            monitor = MultipartEncoderMonitor(encoder, callback)
            headers = {
                'Content-Type': monitor.content_type,
                'X-Upload-Secret': UPLOAD_SECRET
            }

            try:
                response = requests.post(API_URL, data=monitor, headers=headers)
                if response.status_code == 201:
                    res_data = response.json()
                    print(f"\n✅ ¡Éxito! APK subido correctamente.")
                    print(f"🔗 URL Pública: {res_data.get('url')}")
                else:
                    print(f"\n❌ Error del servidor al subir ({response.status_code}): {response.text}")
                    return False
            except requests.exceptions.RequestException as e:
                print(f"\n❌ Error de red al conectar con el servidor: {e}")
                return False

    return True

def main():
    while True:
        print("\n" + "="*50)
        print("   GESTOR DE RELEASES FLUTTER (MIQHATU)   ")
        print("="*50)
        print("1. Compilar y Subir App Cliente")
        print("2. Compilar y Subir App Vendedor")
        print("3. Compilar y Subir Ambas")
        print("-" * 50)
        print("4. Compilar, INSTALAR (vía ADB) y Subir App Cliente")
        print("5. Compilar, INSTALAR (vía ADB) y Subir App Vendedor")
        print("6. Compilar, INSTALAR (vía ADB) y Subir Ambas")
        print("-" * 50)
        print("7. Salir")
        print("="*50)
        
        try:
            opcion = input("Selecciona una opciÃ³n (1-7): ")
        except KeyboardInterrupt:
            print("\nSaliendo...")
            sys.exit(0)

        if opcion == '1':
            compile_and_upload('cliente')
        elif opcion == '2':
            compile_and_upload('vendedor')
        elif opcion == '3':
            if compile_and_upload('cliente'):
                compile_and_upload('vendedor')
        elif opcion == '4':
            compile_and_upload('cliente', install=True)
        elif opcion == '5':
            compile_and_upload('vendedor', install=True)
        elif opcion == '6':
            if compile_and_upload('cliente', install=True):
                compile_and_upload('vendedor', install=True)
        elif opcion == '7':
            print("Saliendo...")
            sys.exit(0)
        else:
            print("❌ Opción inválida.")

if __name__ == "__main__":
    main()
