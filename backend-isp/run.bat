@echo off
SETLOCAL EnableExtensions

:: 1. Crear entorno si no existe
if not exist ".venv\" (
    echo [INFO] Creando entorno virtual...
    py -m venv .venv
)

:: 2. Activar entorno
call .venv\Scripts\activate.bat

:: 3. Instalar dependencias
echo [INFO] Asegurando dependencias...
python -m pip install --upgrade pip
if exist "requirements.txt" (
    pip install -r requirements.txt
)

:: 4. EJECUCIÓN CORRECTA
:: Ejecutamos uvicorn desde la raíz para que reconozca el módulo 'app'
echo [INFO] Iniciando servidor FastAPI...
python -m uvicorn app.main:app --reload

pause