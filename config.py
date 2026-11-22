"""
Mi Consola - Configuracion central
"""
import os
from pathlib import Path

NOMBRE = "Mi Consola"
VERSION = "5.2-emuladores"

BASE = os.environ.get("MI_CONSOLA_BASE", r"D:\Emulacion")

JUEGOS = os.path.join(BASE, "Juegos")
COVERS = os.path.join(BASE, "Covers")
CFG = os.path.join(BASE, "consola_config.json")
CONTROLES_CFG = os.path.join(BASE, "consola_controles.json")
FAVORITOS_CFG = os.path.join(BASE, "consola_favoritos.json")
CACHE_IMG = os.path.join(BASE, "cache_portadas")

DESTINOS = [
    "Retro", "NES", "SNES", "N64", "GB", "GBA", "NDS", "3DS",
    "PS1", "PS2", "PS3", "PS4", "PSP", "PSVita",
    "GC", "Wii", "WiiU", "Switch",
    "Dreamcast", "Saturn", "MegaDrive", "Arcade",
    "PC", "Xbox"
]

EXT_ROM = {
    "NES": {".nes", ".fds", ".unf", ".unif"},
    "SNES": {".sfc", ".smc", ".fig", ".swc"},
    "N64": {".n64", ".z64", ".v64"},
    "GB": {".gb", ".gbc"},
    "GBA": {".gba"},
    "NDS": {".nds"},
    "3DS": {".3ds", ".cia", ".cxi"},
    "PS1": {".bin", ".cue", ".img", ".iso", ".pbp", ".chd"},
    "PS2": {".iso", ".bin", ".chd", ".cso"},
    "PS3": {".iso", ".pkg"},
    "PS4": {".pkg", ".bin"},
    "PSP": {".iso", ".cso", ".pbp"},
    "PSVita": {".vpk"},
    "GC": {".iso", ".gcm", ".gcz", ".rvz"},
    "Wii": {".iso", ".wbfs", ".rvz", ".wad"},
    "WiiU": {".wud", ".wux", ".iso"},
    "Switch": {".nsp", ".xci", ".nca"},
    "Dreamcast": {".cdi", ".gdi", ".chd"},
    "Saturn": {".cue", ".iso", ".chd"},
    "MegaDrive": {".md", ".gen", ".bin", ".smd"},
    "Arcade": {".zip", ".7z"},
    "Xbox": {".iso", ".xbe"},
}

FONDO = (8, 14, 32)
PANEL = (18, 32, 68)
PANEL2 = (28, 48, 98)
TEXTO = (240, 245, 255)
SUAVE = (130, 155, 210)
AZUL = (70, 160, 255)
VERDE = (80, 230, 160)
ROJO = (255, 110, 110)
DORADO = (255, 200, 80)
MORADO = (160, 100, 255)
CIAN = (80, 220, 255)
NARANJA = (255, 160, 60)

EMU_DEFECTO = {
    "Retro": [os.path.join(BASE, "RetroBat", "retrobat.exe")],
    "NES":   [os.path.join(BASE, "emulators", "mesen", "Mesen.exe"), "{rom}"],
    "SNES":  [os.path.join(BASE, "emulators", "snes9x", "snes9x-x64.exe"), "{rom}"],
    "N64":   [os.path.join(BASE, "emulators", "project64", "Project64.exe"), "{rom}"],
    "GB":    [os.path.join(BASE, "emulators", "bgb", "bgb.exe"), "{rom}"],
    "GBA":   [os.path.join(BASE, "emulators", "mGBA", "mGBA.exe"), "{rom}"],
    "NDS":   [os.path.join(BASE, "emulators", "melonDS", "melonDS.exe"), "{rom}"],
    "3DS":   [os.path.join(BASE, "emulators", "azahar", "azahar.exe"), "{rom}"],
    "GC":    [os.path.join(BASE, "emulators", "dolphin", "Dolphin.exe"), "-e", "{rom}"],
    "Wii":   [os.path.join(BASE, "emulators", "dolphin", "Dolphin.exe"), "-e", "{rom}"],
    "WiiU":  [os.path.join(BASE, "emulators", "cemu", "Cemu.exe"), "-g", "{rom}"],
    "Switch":[os.path.join(BASE, "emulators", "eden", "eden.exe"), "{rom}"],
    "PS1":   [os.path.join(BASE, "emulators", "duckstation", "duckstation-qt-x64-ReleaseLTCG.exe"), "{rom}"],
    "PS2":   [os.path.join(BASE, "emulators", "pcsx2", "pcsx2-qt.exe"), "{rom}"],
    "PS3":   [os.path.join(BASE, "emulators", "rpcs3", "rpcs3.exe"), "{rom}"],
    "PS4":   [os.path.join(BASE, "shadPS4", "shadPS4.exe"), "-g", "{rom}"],
    "PSP":   [os.path.join(BASE, "emulators", "ppsspp", "PPSSPPWindows64.exe"), "{rom}"],
    "PSVita":[os.path.join(BASE, "emulators", "vita3k", "Vita3K.exe"), "{rom}"],
    "Dreamcast": [os.path.join(BASE, "emulators", "redream", "redream.exe"), "{rom}"],
    "Saturn":    [os.path.join(BASE, "emulators", "mednafen", "mednafen.exe"), "{rom}"],
    "MegaDrive": [os.path.join(BASE, "emulators", "gens", "gens.exe"), "{rom}"],
    "Arcade": [os.path.join(BASE, "emulators", "mame", "mame.exe"), "{rom}"],
    "Xbox":   [os.path.join(BASE, "emulators", "xemu", "xemu.exe"), "{rom}"],
}

# Rutas alternativas si el nombre del .exe o la carpeta difieren (NO VERIFICADO nombres exactos dentro de zips)
EMU_ALTERNATIVAS = {
    "3DS": [
        os.path.join(BASE, "emulators", "azahar", "azahar.exe"),
        os.path.join(BASE, "emulators", "citra", "citra-qt.exe"),
        os.path.join(BASE, "emulators", "lime3ds", "lime3ds.exe"),
    ],
    "Switch": [
        os.path.join(BASE, "emulators", "eden", "eden.exe"),
        os.path.join(BASE, "emulators", "ryujinx", "Ryujinx.exe"),
        os.path.join(BASE, "emulators", "ryubing", "Ryujinx.exe"),
    ],
    "PS1": [
        os.path.join(BASE, "emulators", "duckstation", "duckstation-qt-x64-ReleaseLTCG.exe"),
        os.path.join(BASE, "emulators", "duckstation", "duckstation-qt-x64-Release.exe"),
        os.path.join(BASE, "emulators", "duckstation", "duckstation.exe"),
    ],
    "PS2": [
        os.path.join(BASE, "emulators", "pcsx2", "pcsx2-qt.exe"),
        os.path.join(BASE, "emulators", "pcsx2", "pcsx2.exe"),
    ],
    "PS3": [
        os.path.join(BASE, "emulators", "rpcs3", "rpcs3.exe"),
    ],
    "PS4": [
        os.path.join(BASE, "shadPS4", "shadPS4.exe"),
    ],
    "PSP": [
        os.path.join(BASE, "emulators", "ppsspp", "PPSSPPWindows64.exe"),
        os.path.join(BASE, "emulators", "ppsspp", "PPSSPPWindows.exe"),
    ],
    "GBA": [
        os.path.join(BASE, "emulators", "mGBA", "mGBA.exe"),
    ],
    "NDS": [
        os.path.join(BASE, "emulators", "melonDS", "melonDS.exe"),
    ],
    "GC": [
        os.path.join(BASE, "emulators", "dolphin", "Dolphin.exe"),
    ],
    "Wii": [
        os.path.join(BASE, "emulators", "dolphin", "Dolphin.exe"),
    ],
    "WiiU": [
        os.path.join(BASE, "emulators", "cemu", "Cemu.exe"),
    ],
}

LIBRETRO_SISTEMAS = {
    "NES": "Nintendo_-_Nintendo_Entertainment_System",
    "SNES": "Nintendo_-_Super_Nintendo_Entertainment_System",
    "N64": "Nintendo_-_Nintendo_64",
    "GB": "Nintendo_-_Game_Boy",
    "GBA": "Nintendo_-_Game_Boy_Advance",
    "NDS": "Nintendo_-_Nintendo_DS",
    "3DS": "Nintendo_-_Nintendo_3DS",
    "GC": "Nintendo_-_GameCube",
    "Wii": "Nintendo_-_Wii",
    "WiiU": "Nintendo_-_Wii_U",
    "Switch": "Nintendo_-_Nintendo_Switch",
    "PS1": "Sony_-_PlayStation",
    "PS2": "Sony_-_PlayStation_2",
    "PS3": "Sony_-_PlayStation_3",
    "PSP": "Sony_-_PlayStation_Portable",
    "PSVita": "Sony_-_PlayStation_Vita",
    "Dreamcast": "Sega_-_Dreamcast",
    "Saturn": "Sega_-_Saturn",
    "MegaDrive": "Sega_-_Mega_Drive_-_Genesis",
    "Arcade": "FBNeo_-_Arcade_Games",
    "Xbox": "Microsoft_-_Xbox",
}

NOMBRES_PORTADA = (
    "cover.jpg", "cover.png", "boxart.jpg", "boxart.png",
    "folder.jpg", "folder.png", "poster.jpg", "poster.png",
    "front.jpg", "front.png", "box.jpg", "box.png",
    "coverart.jpg", "coverart.png", "thumb.jpg", "thumb.png",
    "boxart_front.jpg", "boxart_front.png",
)
