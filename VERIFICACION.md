# Verificacion — Tarea 2 + base v5.2

Fecha: 2026-11-22. Fuentes consultadas via API de GitHub y sitios oficiales.

## Sucesores de emuladores discontinuados

| Sistema | Antes | Ahora | Estado | Fuente |
|---------|-------|-------|--------|--------|
| 3DS | Citra | **Azahar** (`azahar-emu/azahar`) | VERIFICADO | https://azahar-emu.org — https://github.com/azahar-emu/azahar/releases |
| Switch | Ryujinx / Yuzu | **Eden** / **Ryubing** | VERIFICADO (existencia) | https://eden-emu.dev |
| Switch assets GitHub | — | — | **NO VERIFICADO** (DMCA) | Solo pagina oficial |

## Assets de release

| Emulador | Repo | Asset ejemplo | Fuente |
|----------|------|---------------|--------|
| shadPS4 | shadps4-emu/shadPS4 | `shadps4-win64-sdl-*.zip` | https://github.com/shadps4-emu/shadPS4/releases |
| PPSSPP | hrydgard/ppsspp | `PPSSPP-*-Windows-x64.zip` | https://github.com/hrydgard/ppsspp/releases |
| DuckStation | stenzek/duckstation | `duckstation-windows-x64-release.zip` | https://github.com/stenzek/duckstation/releases |
| PCSX2 | PCSX2/pcsx2 | `pcsx2-*-windows-x64-Qt.7z` | https://github.com/PCSX2/pcsx2/releases |
| RPCS3 | RPCS3/rpcs3-binaries-win | `rpcs3-*-win64*.7z` | https://github.com/RPCS3/rpcs3-binaries-win/releases |
| mGBA | mgba-emu/mgba | `mGBA-*-win64.7z` | https://github.com/mgba-emu/mgba/releases |
| melonDS | melonDS-emu/melonDS | `melonDS-*-windows-x86_64.zip` | https://github.com/melonDS-emu/melonDS/releases |
| Cemu | cemu-project/Cemu | `cemu-*-windows-x64.zip` | https://github.com/cemu-project/Cemu/releases |
| Azahar | azahar-emu/azahar | `azahar-windows-msvc-*.zip` | https://github.com/azahar-emu/azahar/releases |
| Dolphin | — | (web) | **NO VERIFICADO** en GitHub Releases |

## Ejecutables dentro de los zips/7z

Todos los nombres en `EMU_DEFECTO` / `EMU_ALTERNATIVAS`: **NO VERIFICADO** (no se descomprimieron binarios Windows en este entorno).

## Flags shadPS4

- `-g` / `--game` y `-f` / `--fullscreen true|false`: VERIFICADO en README  
  https://github.com/shadps4-emu/shadPS4/blob/main/README.md
