@echo off
REM ========================================================================
REM SCRIPT DE DESARROLLO PARA WINDOWS (Batch)
REM ========================================================================
REM Levanta Django + React DIRECTAMENTE - SIN NGINX
REM
REM Uso: dev.bat
REM ========================================================================

setlocal enabledelayedexpansion

REM ========================================================================
REM ACTIVAR ENTORNO VIRTUAL PYTHON (Backend)
REM ========================================================================
if exist "backend\venv\Scripts\activate.bat" (
    call backend\venv\Scripts\activate.bat
) else (
    echo [WARN] Entorno virtual no encontrado en: backend\venv\Scripts\activate.bat
    echo [INFO] Creando entorno virtual en backend...
    python -m venv backend\venv
    call backend\venv\Scripts\activate.bat
)

REM ========================================================================
REM VERIFICACIONES
REM ========================================================================
echo [INFO] Verificando requisitos...

where python >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] Python no disponible
    exit /b 1
)

where node >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] Node.js no disponible
    exit /b 1
)

where npm >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] npm no disponible
    exit /b 1
)

echo [OK] Requisitos verificados

REM ========================================================================
REM VERIFICACIÓN DE .env (ÚNICO .env en la raíz)
REM ========================================================================
if not exist ".env" (
    echo [WARN] .env no existe en la raiz
    if exist ".env.example" (
        copy .env.example .env
        echo [OK] .env creado desde .env.example
    ) else (
        echo [ERROR] .env.example tampoco existe
        exit /b 1
    )
)
echo [OK] .env central verificado

REM ========================================================================
REM BACKEND
REM ========================================================================
echo [INFO] Configurando Backend...

cd backend

if not exist "venv" (
    echo [INFO] Creando venv...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo [INFO] Instalando dependencias...
pip install -q -r requirements.txt

echo [INFO] Migraciones...
python manage.py migrate --skip-checks

cd ..

echo [OK] Backend listo

REM ========================================================================
REM FRONTEND
REM ========================================================================
echo [INFO] Configurando Frontend...

cd frontend

if not exist "node_modules" (
    echo [INFO] Instalando dependencias...
    call npm install
)

cd ..

echo [OK] Frontend listo

REM ========================================================================
REM INSTRUCCIONES
REM ========================================================================
echo.
echo [TIP] Usa el LANZADOR para iniciar todo automaticamente:
echo   python launcher.py
echo.
echo O abre DOS ventanas de CMD nuevas para desarrollo:
echo.
echo Terminal 1 - BACKEND:
echo   cd backend
echo   venv\Scripts\activate.bat
echo   python manage.py runserver 0.0.0.0:8001
echo.
echo Terminal 2 - FRONTEND:
echo   cd frontend
echo   npm start
echo.
echo ACCESOS:
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:8001
echo   Admin:     http://localhost:8001/admin
