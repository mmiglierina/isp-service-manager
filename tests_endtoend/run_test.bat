@echo off
SETLOCAL EnableDelayedExpansion

echo ====================================================
echo  Configurando Entorno y Ejecutando Tests
echo ====================================================

:: 1. Eliminar archivo de bloqueo residual si existe
if exist "C:\Users\Markitos\.wdm\.wdm-lock-chromedriver-win64" (
    del /f /q "C:\Users\Markitos\.wdm\.wdm-lock-chromedriver-win64" >nul 2>&1
)

:: 2. Crear el entorno virtual si no existe
if not exist "venv" (
    echo [INFO] Creando entorno virtual 'venv'...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b %ERRORLEVEL%
    )
)

:: 3. Activar el entorno virtual
call venv\Scripts\activate

:: 4. Actualizar pip e instalar Selenium y dependencias
echo [INFO] Instalando dependencias necesarias...
python -m pip install --upgrade pip >nul 2>&1

if exist "requirements.txt" (
    python -m pip install -r requirements.txt >nul 2>&1
) else (
    python -m pip install "selenium>=4.0.0" webdriver-manager >nul 2>&1
)

echo ====================================================
echo  EJECUTANDO PRUEBAS END TO END
echo ====================================================
echo.

:: Detectamos la estructura real e invocamos unittest discover
if exist "search" (
    python -m unittest discover -s search -p "Search*.py" -v
) else (
    echo [ERROR] No se encontro la carpeta 'search' con los tests.
    echo Asegurate de ejecutar este .bat desde la carpeta madre 'tests_endtoend'.
)

echo.
echo ====================================================
echo  Proceso Finalizado
echo ====================================================
pause