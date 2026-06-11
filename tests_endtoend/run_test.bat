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

:: 4. Actualizar pip e instalar Selenium 4 de forma explícita
echo [INFO] Instalando dependencias necesarias...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install "selenium>=4.0.0" webdriver-manager >nul 2>&1

if exist "requirements.txt" (
    python -m pip install -r requirements.txt >nul 2>&1
)

echo ====================================================
echo  EJECUTANDO PRUEBAS END TO END
echo ====================================================
echo.

:: Ejecución normal (sin -v, solo mostrará . F o E)
if exist "SearchTest" (
    python -m unittest discover -s SearchTest -p "*.py"
) else (
    for %%f in (Search*.py) do (
        python "%%f"
    )
)

echo.
echo ====================================================
echo  Proceso Finalizado
echo ====================================================
pause