"""
Mi Consola - Tienda de juegos gratis / legales
"""
import os
import re
import json
import sys
import subprocess
import webbrowser
import urllib.request
import threading

from config import BASE
from downloads import agregar_enlaces

# ---------------------------------------------------------------------------
# Catalogo: SOLO software libre / gratuito / paginas oficiales.
#   repo=  -> descarga desde GitHub Releases (pat o pats = regex del asset)
#   web_dl -> abre la pagina oficial de descarga
#   emu=   -> se instala en BASE/<emu> (debe coincidir con EMU_DEFECTO)
# ---------------------------------------------------------------------------

TIENDA = [
    # --- Emuladores --------------------------------------------------------
    dict(n="shadPS4 (PS4)",
         d="Emulador de PS4. Se instala en shadPS4. Requiere Vulkan y tus propios juegos.",
         web="https://shadps4.net", web_dl="https://github.com/shadps4-emu/shadPS4/releases",
         repo="shadps4-emu/shadPS4",
         pats=[r"(?i)^shadps4-win64-sdl-[0-9.]+\.zip$"],
         emu="shadPS4", sistema="PS4"),
    dict(n="PPSSPP (PSP)",
         d="Emulador de PSP. Multiplataforma, open source.",
         web="https://www.ppsspp.org", web_dl="https://github.com/hrydgard/ppsspp/releases",
         repo="hrydgard/ppsspp",
         pats=[r"(?i)^PPSSPP-v[0-9.]+-Windows-x64\.zip$"],
         emu=os.path.join("emulators", "ppsspp"), sistema="PSP"),
    dict(n="Dolphin (GC/Wii)",
         d="Emulador de GameCube y Wii. Binarios en la web oficial (no en GitHub Releases).",
         web="https://dolphin-emu.org", web_dl="https://dolphin-emu.org/download/",
         emu=os.path.join("emulators", "dolphin"), sistema="GC"),
    dict(n="DuckStation (PS1)",
         d="Emulador de PlayStation 1. Precision y rendimiento.",
         web="https://www.duckstation.org", web_dl="https://github.com/stenzek/duckstation/releases",
         repo="stenzek/duckstation",
         pats=[r"(?i)^duckstation-windows-x64-release\.zip$"],
         emu=os.path.join("emulators", "duckstation"), sistema="PS1"),
    dict(n="PCSX2 (PS2)",
         d="Emulador de PlayStation 2. Release en .7z (py7zr o 7z.exe).",
         web="https://pcsx2.net", web_dl="https://github.com/PCSX2/pcsx2/releases",
         repo="PCSX2/pcsx2",
         pats=[r"(?i)^pcsx2-v[0-9.]+-windows-x64-Qt\.7z$"],
         emu=os.path.join("emulators", "pcsx2"), sistema="PS2"),
    dict(n="RPCS3 (PS3)",
         d="Emulador de PlayStation 3. Assets en repo de binarios win.",
         web="https://rpcs3.net", web_dl="https://github.com/RPCS3/rpcs3-binaries-win/releases",
         repo="RPCS3/rpcs3-binaries-win",
         pats=[r"(?i)^rpcs3-v[0-9.]+-[0-9]+-[0-9a-f]+_win64_msvc\.7z$"],
         emu=os.path.join("emulators", "rpcs3"), sistema="PS3"),
    dict(n="mGBA (GBA/GB)",
         d="Emulador de Game Boy Advance / Color / Classic.",
         web="https://mgba.io", web_dl="https://github.com/mgba-emu/mgba/releases",
         repo="mgba-emu/mgba",
         pats=[r"(?i)^mGBA-[0-9.]+-win64\.7z$"],
         emu=os.path.join("emulators", "mGBA"), sistema="GBA"),
    dict(n="melonDS (NDS)",
         d="Emulador de Nintendo DS. Open source.",
         web="https://melonds.kuribo64.net", web_dl="https://github.com/melonDS-emu/melonDS/releases",
         repo="melonDS-emu/melonDS",
         pats=[r"(?i)^melonDS-[0-9.]+-windows-x86_64\.zip$"],
         emu=os.path.join("emulators", "melonDS"), sistema="NDS"),
    dict(n="Cemu (Wii U)",
         d="Emulador de Wii U. Open source.",
         web="https://cemu.info", web_dl="https://github.com/cemu-project/Cemu/releases",
         repo="cemu-project/Cemu",
         pats=[r"(?i)^cemu-[0-9.]+-windows-x64\.zip$"],
         emu=os.path.join("emulators", "cemu"), sistema="WiiU"),
    dict(n="Azahar (3DS)",
         d="Sucesor activo de Citra/Lime3DS (2026). Emulador de Nintendo 3DS.",
         web="https://azahar-emu.org", web_dl="https://github.com/azahar-emu/azahar/releases",
         repo="azahar-emu/azahar",
         pats=[r"(?i)^azahar-windows-msvc-[0-9.]+\.zip$"],
         emu=os.path.join("emulators", "azahar"), sistema="3DS"),
    dict(n="Eden / Ryubing (Switch)",
         d="Sucesores de Yuzu/Ryujinx (2026). Descargá el build oficial y extráelo en emulators/eden. Sin firmware ni keys.",
         web="https://eden-emu.dev", web_dl="https://eden-emu.dev",
         # TODO verificar: hosts inestables; no hardcodear asset GitHub
         emu=os.path.join("emulators", "eden"), sistema="Switch"),

    # --- Juegos gratis / legales -------------------------------------------
    dict(n="SuperTuxKart", d="Carreras tipo Mario Kart. Hasta 4 jugadores local + online.",
         repo="supertuxkart/stk-code", pat=r"(?i)(win|windows).*\.(zip|exe)$", web="https://supertuxkart.net", web_dl="https://supertuxkart.net/Download"),
    dict(n="Xonotic", d="Shooter veloz tipo Quake. Split-screen y online.",
         web="https://xonotic.org", web_dl="https://xonotic.org/download/"),
    dict(n="Hedgewars", d="Estilo Worms por turnos. Ideal para varios en la misma PC.",
         web="https://www.hedgewars.org", web_dl="https://www.hedgewars.org/download.html"),
    dict(n="DDNet", d="Plataformas cooperativo online.",
         repo="ddnet/ddnet", pat=r"(?i)win64.*\.zip$", web="https://ddnet.org", web_dl="https://ddnet.org/downloads/"),
    dict(n="Luanti (Minetest)", d="Mundo de bloques open source.",
         repo="luanti-org/luanti", pat=r"(?i)win64.*\.zip$", web="https://www.luanti.org", web_dl="https://www.luanti.org/downloads/"),
    dict(n="0 A.D.", d="Estrategia historica RTS. Multijugador.",
         web="https://play0ad.com", web_dl="https://play0ad.com/download/"),
    dict(n="OpenRA", d="Command & Conquer / Red Alert / Dune.",
         repo="OpenRA/OpenRA", pat=r"(?i)(red.?alert|tiberian|dune).*x64.*\.exe$", web="https://www.openra.net", web_dl="https://www.openra.net/download/"),
    dict(n="Battle for Wesnoth", d="Estrategia por turnos. Local y online.",
         web="https://www.wesnoth.org", web_dl="https://www.wesnoth.org/downloads/"),
    dict(n="OpenTTD", d="Transport Tycoon. Multijugador excelente.",
         web="https://www.openttd.org", web_dl="https://www.openttd.org/downloads.html"),
    dict(n="Mindustry", d="Tower defense + automatizacion.",
         repo="Anuken/Mindustry", pat=r"(?i)windows.*\.zip$", web="https://mindustrygame.github.io", web_dl="https://mindustrygame.github.io/"),
    dict(n="SuperTux", d="Plataformas tipo Mario.",
         repo="SuperTux/supertux", pat=r"(?i)win.*\.(zip|exe)$", web="https://www.supertux.org", web_dl="https://www.supertux.org/download.html"),
    dict(n="Brawlhalla", d="Peleas tipo Smash. Gratis.",
         web="https://www.brawlhalla.com", web_dl="https://www.brawlhalla.com/"),
    dict(n="Warzone 2100", d="RTS 3D. LAN y online.",
         repo="Warzone2100/warzone2100", pat=r"(?i)win.*x64.*\.exe$", web="https://wz2100.net", web_dl="https://wz2100.net/download"),
    dict(n="Unciv", d="Clon de Civilization V ligero y open source.",
         repo="yairm210/Unciv", pat=r"(?i)windows64.*\.zip$", web="https://github.com/yairm210/Unciv", web_dl="https://github.com/yairm210/Unciv/releases"),
    dict(n="Teeworlds", d="Shooter 2D multijugador, partidas rapidas.",
         repo="teeworlds/teeworlds", pat=r"(?i)win64.*\.zip$", web="https://www.teeworlds.com", web_dl="https://www.teeworlds.com/?page=downloads"),
    dict(n="OpenArena", d="Arena shooter estilo Quake III. Gratis y libre.",
         web="https://openarena.ws", web_dl="https://openarena.ws/page.php?3"),
    dict(n="Counter-Strike 2", d="FPS tactico. Gratis en Steam.",
         web="https://www.counter-strike.net", web_dl="https://store.steampowered.com/app/730"),
    dict(n="Dota 2", d="MOBA. Gratis.",
         web="https://www.dota2.com", web_dl="https://store.steampowered.com/app/570"),
    dict(n="Team Fortress 2", d="FPS class-based. Gratis.",
         web="https://www.teamfortress.com", web_dl="https://store.steampowered.com/app/440"),
    dict(n="Warframe", d="Shooter cooperativo espacial. Gratis.",
         web="https://www.warframe.com", web_dl="https://www.warframe.com/download"),
]


def resolver(j):
    if j.get("dl"):
        return j["dl"]
    if not j.get("repo"):
        return None
    try:
        req = urllib.request.Request(
            f"https://api.github.com/repos/{j['repo']}/releases/latest",
            headers={"User-Agent": "MiConsola/5.2"}
        )
        rel = json.load(urllib.request.urlopen(req, timeout=15))
        pats = j.get("pats") or ([j["pat"]] if j.get("pat") else [r"."])
        ass = []
        for a in rel.get("assets", []):
            for p in pats:
                if re.search(p, a["name"]):
                    ass.append(a)
                    break
        def score(a):
            name = a["name"]
            for i, p in enumerate(pats):
                if re.search(p, name):
                    return (i, 0 if name.lower().endswith((".zip", ".7z", ".exe", ".msi")) else 1, -a.get("size", 0))
            return (99, 1, 0)
        ass.sort(key=score)
        return ass[0]["browser_download_url"] if ass else None
    except Exception:
        return None


def abrir_web(url):
    if not url:
        return
    try:
        import webview  # noqa
        subprocess.Popen([sys.executable, os.path.abspath(__file__), "--web", url])
        return
    except ImportError:
        pass
    if sys.platform == "win32":
        try:
            os.startfile(url)
            return
        except Exception:
            pass
    try:
        webbrowser.open(url, new=2)
    except Exception:
        try:
            if sys.platform == "win32":
                subprocess.Popen(["cmd", "/c", "start", "", url], shell=False)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", url])
            else:
                subprocess.Popen(["xdg-open", url])
        except Exception:
            pass


def pedir(j):
    try:
        if j.get("pago"):
            abrir_web(j.get("web") or "https://store.steampowered.com")
            return "web"
        url = resolver(j)
        if url and j.get("emu"):
            destino = os.path.join(BASE, j["emu"])
            ok = agregar_enlaces(url, "Emuladores", j["n"], destino=destino)
            return "descarga" if ok else "error"
        if url:
            ok = agregar_enlaces(url, "PC", j["n"])
            return "descarga" if ok else "error"
        destino = j.get("web_dl") or j.get("web")
        if destino:
            abrir_web(destino)
        return "web"
    except Exception:
        return "error"
