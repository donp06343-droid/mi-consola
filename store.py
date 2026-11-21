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

from downloads import agregar_enlaces

# Nucleo de juegos gratis/legales con descarga util
TIENDA = [
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
    dict(n="The Dark Mod", d="Stealth tipo Thief. Totalmente gratis.",
         web="https://www.thedarkmod.com", web_dl="https://www.thedarkmod.com/downloads/"),
    dict(n="Cataclysm: DDA", d="Supervivencia roguelike profundo.",
         web="https://cataclysmdda.org", web_dl="https://cataclysmdda.org/releases/"),
    dict(n="FreeDoom + GZDoom", d="Doom libre + motor moderno.",
         web="https://freedoom.github.io", web_dl="https://freedoom.github.io/download.html"),
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
            headers={"User-Agent": "MiConsola/5.0"}
        )
        rel = json.load(urllib.request.urlopen(req, timeout=15))
        ass = [a for a in rel.get("assets", []) if re.search(j.get("pat", r"."), a["name"])]
        ass.sort(key=lambda a: (
            0 if a["name"].lower().endswith((".zip", ".7z", ".exe", ".msi")) else 1,
            0 if re.search(r"(?i)win|windows|x64|64", a["name"]) else 1,
            -a.get("size", 0)
        ))
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
    if j.get("pago"):
        abrir_web(j.get("web") or "https://store.steampowered.com")
        return "web"
    url = resolver(j)
    if url:
        ok = agregar_enlaces(url, "PC", j["n"])
        return "descarga" if ok else "error"
    destino = j.get("web_dl") or j.get("web")
    if destino:
        abrir_web(destino)
    return "web"
