# Verificacion (v5.4-tiendas)

Leyenda: VERIFICADO = comprobado contra una fuente; NO VERIFICADO = hay que probarlo en una PC real.

## shadPS4 (verificado por Claude, 2026-11-22)
- Ultima estable: v0.21.0 (30-oct-2026), repo `shadps4-emu/shadPS4` - VERIFICADO
  (https://shadps4.net, https://sourceforge.net/projects/shadps4.mirror/files/)
- Asset Windows: `shadps4-win64-sdl-0.21.0.zip` (solo build SDL) - VERIFICADO (espejo SourceForge)
- Flags `-g` y `-f true` - segun README oficial (reportado por Grok) - NO VERIFICADO por Claude
- Que el build SDL abra una GUI sin argumentos (tecla G) - NO VERIFICADO

## Emuladores
Patrones en store.py. Nombres de .exe en EMU_DEFECTO: NO VERIFICADOS.
Si un patron no encuentra asset, la tienda abre la pagina oficial.

## Extraccion
- `.zip`: stdlib, aplanado y a prueba de path traversal
- `.7z`: py7zr o 7z.exe — extraccion real NO VERIFICADA en este entorno

## Tiendas conectadas (stores.py, v5.4) - verificado por Claude, 2026-11-22
- **Epic**: manifests en `ProgramData\\Epic\\EpicGamesLauncher\\Data\\Manifests\\*.item` con `AppName`,
  `DisplayName`, `InstallLocation`, `LaunchExecutable`, `bIsIncompleteInstall` - VERIFICADO
  (https://dev.epicgames.com/documentation/unreal-engine/academic-installation-of-unreal-engine, crate game-scanner)
- **Epic lanzar**: `com.epicgames.launcher://apps/<AppName>?action=launch&silent=true` - VERIFICADO (documento oficial de Epic,
  "Epic Games Protocol Activation"); tienda: `com.epicgames.launcher://store/product/<slug>` - VERIFICADO.
  `com.epicgames.launcher://store` (portada de la tienda) - NO VERIFICADO.
- **GOG**: registro `HKLM\\SOFTWARE\\GOG.com\\Games\\<id>` con `gameName`, `path`, `exe` - VERIFICADO
  (https://github.com/erri120/GameFinder/wiki/GOG-Galaxy). Se lanza el exe directo (GOG es DRM-free).
  `goggalaxy://` para abrir la tienda - NO VERIFICADO.
- **Steam**: `appmanifest_*.acf` + `libraryfolders.vdf` + `HKCU\\Software\\Valve\\Steam\\SteamPath` - VERIFICADO
  (GameFinder). `StateFlags & 4` = instalado por completo - de memoria (EAppState), NO VERIFICADO contra fuente.
  `steam://rungameid/<id>` y `steam://store/<id>` - de uso comun, NO VERIFICADO contra documentacion oficial.
- **Xbox / Microsoft Store**: `ms-windows-store://home` - NO VERIFICADO. Deteccion de juegos instalados: NO IMPLEMENTADA.
- **EA App, Ubisoft Connect, Battle.net, itch.io**: NO IMPLEMENTADOS.
- Probado con manifests/registro simulados (Linux). NO probado en Windows con tiendas reales.
