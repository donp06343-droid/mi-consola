@echo off
echo ========================================
echo   Mi Consola v5 - Instalador en D:
echo ========================================
echo.

set TARGET=D:\Emulacion
set REPO=https://github.com/donp06343-droid/mi-consola.git

echo Creando carpetas en %TARGET% ...
mkdir "%TARGET%" 2>nul
mkdir "%TARGET%\Juegos" 2>nul
mkdir "%TARGET%\Covers" 2>nul
mkdir "%TARGET%\emulators" 2>nul
mkdir "%TARGET%\cache_portadas" 2>nul

echo.
echo Descargando codigo desde GitHub...
cd /d "%TARGET%"

where git >nul 2>&1
if %ERRORLEVEL%==0 (
    if exist "%TARGET%\mi-consola\.git" (
        echo Actualizando repositorio existente...
        cd /d "%TARGET%\mi-consola"
        git pull
    ) else (
        git clone %REPO% mi-consola
    )
) else (
    echo Git no encontrado. Descargando ZIP...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/donp06343-droid/mi-consola/archive/refs/heads/main.zip' -OutFile '%TEMP%\mi-consola.zip'"
    powershell -Command "Expand-Archive -Path '%TEMP%\mi-consola.zip' -DestinationPath '%TARGET%' -Force"
    if exist "%TARGET%\mi-consola-main" (
        if exist "%TARGET%\mi-consola" rmdir /s /q "%TARGET%\mi-consola"
        ren "%TARGET%\mi-consola-main" mi-consola
    )
)

echo.
echo Instalando dependencias Python...
cd /d "%TARGET%\mi-consola"
python -m pip install -r requirements.txt

echo.
echo ========================================
echo   Listo!
echo   Ejecuta:  python "%TARGET%\mi-consola\main.py"
echo ========================================
pause
