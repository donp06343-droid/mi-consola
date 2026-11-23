# Verificacion (v5.5-ea-ubisoft)

Leyenda: VERIFICADO = comprobado contra una fuente; NO VERIFICADO = hay que probarlo en una PC real.

## shadPS4
- Asset estable: `shadps4-win64-sdl-*.zip` - VERIFICADO (releases GitHub / espejos)
- Flags `-g` / `-f true` - README oficial - NO VERIFICADO en esta PC
- GUI sin argumentos (tecla G) - NO VERIFICADO

## Emuladores
Patrones en store.py. Nombres de .exe en EMU_DEFECTO: NO VERIFICADOS.

## Extraccion
- `.zip`: stdlib
- `.7z`: py7zr o 7z.exe — NO VERIFICADO en este entorno

## Tiendas conectadas (stores.py)
- **Steam / Epic / GOG**: ver notas previas (v5.4). Lectura local sin cuentas.
- **Xbox**: `ms-windows-store://home` - NO VERIFICADO. Deteccion de juegos: NO IMPLEMENTADA.

## EA App y Ubisoft Connect (v5.5-ea-ubisoft)

### EA App / Origin
| Dato | Estado | Fuente |
|------|--------|--------|
| `HKLM\\SOFTWARE\\EA Games\\<titulo>\\Install Dir` | Usado | Reddit r/EAApp; Lutris#5160 |
| `HKLM\\SOFTWARE\\WOW6432Node\\Origin Games\\<contentId>` | Usado | Lutris issue #5160 |
| Archivo cifrado ProgramData\\EA Desktop\\...\\IS | NO usado | GameFinder wiki EA Desktop |
| `origin://launchgame/<id>` / `origin2://library/open` | **NO VERIFICADO** | Uso comun |

### Ubisoft Connect
| Dato | Estado | Fuente |
|------|--------|--------|
| `HKLM\\SOFTWARE\\WOW6432Node\\Ubisoft\\Launcher\\Installs\\<id>\\InstallDir` | Usado | modding.wiki Vortex; RizSavio/UplayGameIDs |
| Nombre via `Uninstall\\Uplay Install {id}\\DisplayName` | Usado | modding.wiki |
| `uplay://launch/<id>/0` | **NO VERIFICADO** | Uso comun (UplayGameIDs) |
| Ruta default juegos | Solo referencia | Ubisoft Help |

**Probado:** sintaxis Python. **NO probado** con EA App / Ubisoft Connect reales en Windows.

Battle.net e itch.io: NO IMPLEMENTADOS.


## Integración Mi Consola 5.6.0-console

Cambios incorporados en la rama `consola-unificada`:
- Se incorporó `cargar_cfg()` a `library.py` para corregir el import requerido por `main.py`.
- Se integraron mejoras de descarga: solo HTTP/HTTPS, nombres de archivo seguros, extracción ZIP/7z validada, manejo correcto de fallos y registro de la ruta extraída.
- Se añadió una vista Estado con CPU/RAM/almacenamiento cuando psutil está disponible, detección de emuladores y métricas de biblioteca.
- Se añadieron estadísticas locales de lanzamientos y tiempo de ejecución. No se transmiten.
- Se añadieron pestañas clicables y una vista Ajustes para abrir carpetas y registrar carpetas adicionales de juegos de PC.
- Se añadió psutil a requirements.txt; el panel conserva fallback parcial si no está instalado.
- La tienda mantiene un catálogo curado de software libre/gratuito. No equivale a 100.000 fichas.

### Verificación pendiente
- No se ejecutó la aplicación en Windows desde este entorno.
- No se ejecutaron pruebas de integración con cada emulador.
- No se verificó el comportamiento de los diálogos de selección de carpeta en el equipo del usuario.
- Las lecturas de GPU y temperatura no se presentan como valores reales porque no existe una fuente portable configurada.
- La comprobación estática de sintaxis y el smoke test en Windows siguen pendientes.
