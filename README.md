# Mi Consola 5.6 — frontend unificado para PC

Mi Consola reúne en una sola interfaz la biblioteca local, el escaneo de juegos de PC, los emuladores configurados, las portadas, la tienda de software gratuito/legal, las descargas y los controles.

## Funciones disponibles

- Lobby a pantalla completa con navegación por teclado, gamepad y pestañas clicables con mouse.
- Biblioteca local de ROMs y juegos instalados en PC (Steam, Epic, GOG, EA/Ubisoft y detección genérica según disponibilidad).
- Tarjetas con portadas: caché local de Steam, carpeta Covers, imágenes junto al juego y búsqueda de portadas de Steam/Libretro; se muestra un placeholder si no hay arte.
- Favoritos, búsqueda y ordenamiento por nombre/sistema/favoritos.
- Lanzamiento desde la biblioteca mediante la configuración de emuladores y ejecutables locales.
- Tienda curada de proyectos open-source y juegos gratuitos/legales. Los emuladores descargables se guardan en las carpetas configuradas y se lanzan desde la biblioteca.
- Descargas HTTP/HTTPS, extracción ZIP/7z, validación de rutas de extracción y mensajes de error.
- Ajustes para abrir las carpetas de datos y añadir carpetas extra de juegos de PC.
- Panel Estado: CPU/RAM/almacenamiento cuando psutil está disponible, sistema operativo, juegos detectados, emuladores encontrados y estadísticas locales.
- Estadísticas privadas guardadas localmente: lanzamientos, tiempo de proceso y juegos más usados. No hay telemetría ni envío de esos datos.

## Requisitos

Windows recomendado. Python 3.10+.

```bash
python -m pip install -r requirements.txt
```

También se puede iniciar con doble clic en `iniciar_mi_consola.bat`.

## Navegación

| Acción | Tecla |
|---|---|
| Moverse | Flechas / WASD |
| Confirmar / jugar | Enter / Espacio |
| Volver | Esc |
| Favorito | F |
| Buscar | / o F3 |
| Ordenar | O |
| Tienda | T |
| Descargas | Tab |
| Estado del PC | E |
| Ajustes de carpetas | U |
| Controles | C |
| Re-escanear PC | R |

Las pestañas superiores también se pueden pulsar con el mouse. Los controles de gamepad se pueden reasignar desde Controles.

## Carpetas

La carpeta base predeterminada es `D:\\Emulacion` (se puede cambiar con `MI_CONSOLA_BASE` antes de iniciar).

- Juegos: `BASE/Juegos/<sistema>/`
- Portadas: `BASE/Covers/`
- Emuladores: `BASE/emulators/<emulador>/` y las rutas específicas de `config.py`
- Configuración: `BASE/consola_config.json`
- Estadísticas: `BASE/consola_estadisticas.json`

Desde Ajustes se pueden añadir carpetas adicionales para el escaneo de juegos de PC.

## Límites conocidos

- La tienda incluida es un catálogo curado, no un índice de 100.000 juegos. La biblioteca muestra juegos que ya existen en tus carpetas o que se detectan en instalaciones locales.
- Las portadas dependen de que exista una imagen local o de que la fuente remota responda y tenga una coincidencia; no se garantiza arte para cada título.
- Mi Consola funciona como frontend: cada emulador conserva su propio ejecutable, configuración, BIOS/firmware y requisitos. No se fusiona el código fuente de todos los emuladores dentro de un único binario.
- No incluye ROMs, BIOS, firmware, claves ni juegos comerciales.
- GPU y temperatura aparecen como no disponibles cuando el sistema no ofrece una fuente fiable. No se inventan lecturas.
- No se ha verificado la ejecución en Windows de esta rama desde este entorno. Revisar VERIFICACION.md antes de considerarla lista para uso diario.

## Versión

`5.6.0-console`
