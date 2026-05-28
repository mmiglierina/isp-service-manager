@echo off
title Generador Seguro de Administradores - ISP
cls

echo ===================================================
echo   Iniciando Entorno para Creacion de Administrador
echo ===================================================
echo.

rem Asegurar que nos paramos en la carpeta del script
cd /d "%~dp0"

rem Activar el entorno virtual si existe
if exist .venv\Scripts\activate.bat call .venv\Scripts\activate.bat

echo [INFO] Ejecutando script desde la carpeta /scripts...
echo.

rem Lanzar Python directamente buscando el archivo en la nueva carpeta
python scripts\seed.py

echo.
echo ===================================================
echo   Proceso finalizado. Presione una tecla para salir.
echo ===================================================
pause > nul