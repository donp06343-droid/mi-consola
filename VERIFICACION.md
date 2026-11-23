# Verificacion (v5.5.1-unificado)

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


## Tarea 2 — catálogo de emuladores y extracción

Versión base comprobada: \`config.VERSION = "5.5.1-unificado"\` (cumple el requisito mínimo 5.2).

### Assets de Windows comprobados contra las respuestas JSON de GitHub Releases consultadas el 2026-11-22

| Proyecto | Release consultada | Asset Windows observado | Estado |
|---|---|---|---|
| shadPS4 | https://api.github.com/repos/shadps4-emu/shadPS4/releases/latest | \`shadps4-win64-sdl-0.21.0.zip\` | VERIFICADO |
| PPSSPP | https://api.github.com/repos/hrydgard/ppsspp/releases/latest | \`PPSSPP-v1.20.4-Windows-x64.zip\` | VERIFICADO |
| DuckStation | https://api.github.com/repos/stenzek/duckstation/releases/latest | \`duckstation-windows-x64-release.zip\` | VERIFICADO |
| PCSX2 | https://api.github.com/repos/PCSX2/pcsx2/releases/latest | \`pcsx2-v2.8.2-windows-x64-Qt.7z\` | VERIFICADO |
| RPCS3 | https://api.github.com/repos/RPCS3/rpcs3-binaries-win/releases/latest | \`rpcs3-v0.0.43-20644-3bfac607_win64_msvc.7z\` | VERIFICADO |
| mGBA | https://api.github.com/repos/mgba-emu/mgba/releases/latest | \`mGBA-0.10.5-win64.7z\` | VERIFICADO |
| melonDS | https://api.github.com/repos/melonDS-emu/melonDS/releases/latest | \`melonDS-1.1-windows-x86_64.zip\` | VERIFICADO |
| Cemu | https://api.github.com/repos/cemu-project/Cemu/releases/latest | \`cemu-2.6-windows-x64.zip\` | VERIFICADO |
| Azahar | https://api.github.com/repos/azahar-emu/azahar/releases/latest | \`azahar-windows-msvc-2126.2.zip\` | VERIFICADO |

Las comprobaciones anteriores verifican que esos nombres aparecen en la API de releases consultada; no prueban la ejecución de los binarios en esta PC ni garantizan que sigan siendo los últimos en el futuro.

### Switch
- Eden: https://eden-emu.dev — se abre la página oficial; no se fija un asset de GitHub.
- Ryubing: NO VERIFICADO en esta tarea. No se fija un asset ni se afirma compatibilidad de ejecutables.
- La instalación automática desde la tienda no se declara verificada para ninguno de los dos.

### Extracción
- ZIP y 7z se extraen en un directorio temporal/destino, aplanando una única carpeta raíz.
- Se rechazan rutas absolutas, unidades y segmentos \`..\`; se usa \`os.path.commonpath\` en vez de comparar prefijos de texto.
- Los enlaces simbólicos presentes en ZIP/7z se omiten.
- .7z: py7zr o 7z/7za en PATH o \`BASE/tools/\`.
- **NO VERIFICADO en Windows:** extracción real con cada versión de py7zr/7-Zip y ejecución de cada emulador. La revisión del código no sustituye esas pruebas.
