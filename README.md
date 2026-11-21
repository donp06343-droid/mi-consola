# Mi Consola

Lanzador a pantalla completa + centro de descargas de juegos (emuladores + PC).

## Caracteristicas

- Frontend de emulacion (NES, SNES, N64, PS1, PS2, Switch, etc.)
- Lanzador de juegos de PC (Steam, Epic, carpetas genericas)
- **Portadas automaticas** (Steam CDN + Libretro Thumbnails)
- Favoritos, busqueda, ordenamiento
- Centro de descargas + tienda de juegos gratis/legales
- Controles configurables (teclado + gamepad)

## Requisitos

```bash
pip install pygame
# Opcional:
pip install pywebview
```

## Uso

```bash
python consola.py
```

La carpeta base por defecto es `D:\\Emulacion`.

## Estructura recomendada

```
D:\\Emulacion\\
├── Juegos\\
│   ├── NES\\
│   ├── SNES\\
│   ├── PS1\\
│   └── ...
├── Covers\\          # Portadas (se llenan solas)
├── emulators\\
└── consola.py
```

## Teclas principales

| Tecla | Accion |
|-------|--------|
| Flechas / WASD | Mover |
| Enter / Espacio | Jugar |
| F | Favorito |
| / o F3 | Buscar |
| O | Cambiar orden |
| Tab | Descargas |
| T | Tienda |
| R | Re-escanear |
| C | Controles |
| Esc | Volver / Salir |

## Version actual

v4.1 - Sistema de portadas automaticas
