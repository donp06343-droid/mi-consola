# Mi Consola v5 (Modular)

Lanzador a pantalla completa + centro de descargas de juegos (emuladores + PC).

## Caracteristicas

- Frontend de emulacion (NES, SNES, N64, PS1, PS2, Switch, etc.)
- Lanzador de juegos de PC (Steam, Epic, carpetas genericas)
- **Portadas automaticas mejoradas** (Steam CDN + Libretro + matching inteligente)
- Favoritos, busqueda, ordenamiento
- Centro de descargas + tienda de juegos gratis/legales
- Controles configurables (teclado + gamepad)
- Lobby con estrellas parallax

## Estructura modular

```
mi-consola/
├── main.py              # Punto de entrada
├── config.py            # Rutas, colores, sistemas, emuladores
├── covers.py            # Sistema de portadas (mejorado)
├── library.py           # Escaneo de biblioteca + favoritos
├── launcher.py          # Lanzamiento de juegos/emuladores
├── downloads.py         # Cola de descargas
├── store.py             # Tienda + resolver de enlaces
├── controls.py          # Controles teclado/joystick
├── ui/
│   ├── stars.py         # Campo de estrellas
│   └── cards.py         # Tarjetas de juegos
├── requirements.txt
└── README.md
```

## Requisitos

```bash
pip install pygame
# Opcional:
pip install pywebview
```

## Uso

```bash
python main.py
```

La carpeta base por defecto es `D:\\Emulacion` (configurable con `MI_CONSOLA_BASE`).

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
| M | Spotify |
| Esc | Volver / Salir |

## Mejoras v5 (portadas)

- Matching de nombres mas inteligente (ignora regiones, codigos, articulos)
- Score de similitud para elegir la mejor imagen local
- Prioridad clara: Steam cache → Covers/ → junto a ROM → descarga
- Placeholders mas limpios
- Descarga concurrente controlada

## Version

v5.0-modular
