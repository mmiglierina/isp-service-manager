@echo off
:: ====================================================================
:: ISP Management System - Startup and Environment Configuration Script
:: ====================================================================

:: Set local scope for variables and enable command extensions
setlocal enabledelayedexpansion

:: Global Configuration Variables
set "VENV_DIR=.venv"
set "REQUIREMENTS_FILE=requirements.txt"
set "ENTRY_POINT=app.py"

echo [INFO] Iniciando el proceso de despliegue local...
echo --------------------------------------------------

:: Main Execution Flow
call :check_python_installation
if !errorlevel! neq 0 (
    echo [ERROR] Python no esta instalado o no se encuentra en el PATH.
    exit /b 1
)

call :verify_or_create_venv
if !errorlevel! neq 0 (
    echo [ERROR] No se pudo configurar el entorno virtual.
    exit /b 1
)

call :install_dependencies
if !errorlevel! neq 0 (
    echo [ERROR] Fallo la instalacion de dependencias.
    exit /b 1
)

call :execute_application
exit /b %errorlevel%


:: ====================================================================
:: Functions Definitions (Internal Procedures)
:: ====================================================================

:check_python_installation
    echo [PROCESS] Verificando instalacion de Python...
    where python >nul 2>&1
    exit /b %errorlevel%

:verify_or_create_venv
    echo [PROCESS] Verificando entorno virtual en la carpeta "!VENV_DIR!"...
    if not exist "!VENV_DIR!\Scripts\activate.bat" (
        echo [WARN] No se encontro el entorno virtual. Creando uno nuevo...
        python -m venv "!VENV_DIR!"
    ) else (
        echo [INFO] Entorno virtual detectado correctamente.
    )
    exit /b %errorlevel%

:install_dependencies
    echo [PROCESS] Activando entorno virtual e instalando requerimientos...
    
    :: Activate the virtual environment locally
    call "!VENV_DIR!\Scripts\activate.bat"
    
    if exist "!REQUIREMENTS_FILE!" (
        echo [INFO] Instalando dependencias desde !REQUIREMENTS_FILE!...
        pip install --upgrade pip
        pip install -r "!REQUIREMENTS_FILE!"
    ) else (
        echo [WARN] No se encontro el archivo !REQUIREMENTS_FILE!. Se omitira este paso.
    )
    exit /b %errorlevel%

:execute_application
    echo [PROCESS] Lanzando la aplicacion Flask...
    echo --------------------------------------------------
    
    :: Ensure the environment is active before launching
    call "!VENV_DIR!\Scripts\activate.bat"
    
    if exist "!ENTRY_POINT!" (
        python "!ENTRY_POINT!"
    ) else (
        echo [ERROR] El archivo de entrada !ENTRY_POINT! no existe en este directorio.
        exit /b 1
    )
    exit /b %errorlevel%