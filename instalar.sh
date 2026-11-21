#!/bin/bash
set -e
TARGET="${MI_CONSOLA_BASE:-$HOME/Emulacion}"
REPO="https://github.com/donp06343-droid/mi-consola.git"

echo "=== Mi Consola v5 - Instalador ==="
mkdir -p "$TARGET"/{Juegos,Covers,emulators,cache_portadas}

if command -v git &>/dev/null; then
  if [ -d "$TARGET/mi-consola/.git" ]; then
    echo "Actualizando..."
    (cd "$TARGET/mi-consola" && git pull)
  else
    git clone "$REPO" "$TARGET/mi-consola"
  fi
else
  echo "Descargando ZIP..."
  curl -L "https://github.com/donp06343-droid/mi-consola/archive/refs/heads/main.zip" -o /tmp/mi-consola.zip
  unzip -o /tmp/mi-consola.zip -d "$TARGET"
  rm -rf "$TARGET/mi-consola"
  mv "$TARGET/mi-consola-main" "$TARGET/mi-consola"
fi

cd "$TARGET/mi-consola"
python3 -m pip install -r requirements.txt
echo "Listo. Ejecuta: python3 $TARGET/mi-consola/main.py"
