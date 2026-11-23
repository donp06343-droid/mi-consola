@echo off
setlocal
REM ==========================================================
REM  Mi Consola - Instalar todo y ejecutar (un solo doble clic)
REM  Colocar este archivo DENTRO de la carpeta mi-consola-main
REM  (junto a main.py).
REM ==========================================================
cd /d "%~dp0"

if not exist "main.py" (
    echo ERROR: No encuentro main.py aqui.
    echo Copia este archivo dentro de la carpeta mi-consola-main y vuelve a abrirlo.
    pause
    exit /b 1
)

set PYVER=

REM 1) Buscar Python 3.12 o 3.13 ya instalado
py -3.12 --version >nul 2>&1
if %ERRORLEVEL%==0 set PYVER=3.12
if "%PYVER%"=="" (
    py -3.13 --version >nul 2>&1
    if %ERRORLEVEL%==0 set PYVER=3.13
)
if "%PYVER%"=="" (
    py -3 --version >nul 2>&1
    if %ERRORLEVEL%==0 set PYVER=3
)

REM 2) Si no existe, instalar Python 3.12 con winget
if "%PYVER%"=="" (
    echo No se encontro Python 3.12/3.13. Instalando Python 3.12 ...
    winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
    py -3.12 --version >nul 2>&1
    if %ERRORLEVEL%==0 (
        set PYVER=3.12
    ) else (
        echo.
        echo No se pudo instalar automaticamente.
        echo Instala Python 3.12 desde https://www.python.org/downloads/
        echo marcando "Add python.exe to PATH", y vuelve a abrir este archivo.
        pause
        exit /b 1
    )
)

echo Usando Python %PYVER%
echo.
echo Instalando dependencias ...
py -%PYVER% -m pip install --upgrade pip
py -%PYVER% -m pip install -r requirements.txt
if not %ERRORLEVEL%==0 (
    echo.
    echo Fallo la instalacion de dependencias. Copia el mensaje de error y pegalo en el chat.
    pause
    exit /b 1
)

echo.
echo Iniciando Mi Consola (modo normal) ...
py -%PYVER% main.py --mode normal
if not %ERRORLEVEL%==0 (
    echo.
    echo El programa termino con error. Copia el mensaje de arriba y pegalo en el chat.
)
pause
