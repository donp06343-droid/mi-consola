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
