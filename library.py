"""
Mi Consola - Biblioteca de juegos
Escaneo de ROMs + deteccion PC (Steam, Epic, genericos)
"""
import os
import re
import json
import time
import string
import threading

from config import BASE, JUEGOS, CFG, DESTINOS, EXT_ROM, FAVORITOS_CFG, EMU_DEFECTO
import ps4
import stores


def cargar_cfg():
    """Carga los comandos de emulador del usuario y completa con los valores por defecto."""
    cfg = {sistema: list(comando) for sistema, comando in EMU_DEFECTO.items()}
    try:
        if os.path.isfile(CFG):
            with open(CFG, encoding="utf-8") as archivo:
                personalizada = json.load(archivo)
            if isinstance(personalizada, dict):
                for sistema, comando in personalizada.items():
                    if (
                        isinstance(sistema, str)
                        and isinstance(comando, list)
                        and comando
                        and all(isinstance(arg, str) for arg in comando)
                    ):
                        cfg[sistema] = comando
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as error:
        print(f"No se pudo cargar {CFG}; se usan los emuladores por defecto: {error}")
    return cfg


def cargar_favoritos():
    if os.path.exists(FAVORITOS_CFG):
        try:
            with open(FAVORITOS_CFG, encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            pass
    return set()


def guardar_favoritos(favs):
    try:
        with open(FAVORITOS_CFG, "w", encoding="utf-8") as f:
            json.dump(sorted(list(favs)), f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("No se pudo guardar favoritos:", e)


def clave_juego(sis, nom):
    return f"{sis}::{nom}".lower()


EXCLUIR = {
    "windows", "windows.old", "windowsapps", "program files", "program files (x86)", "programdata",
    "users", "perflogs", "recovery", "$recycle.bin", "system volume information", "common files",
    "intel", "amd", "nvidia", "nvidia corporation", "google", "adobe", "steam", "epic games",
    "java", "dotnet", "python", "mozilla firefox", "emulacion", "microsoft", "appdata", "temp",
    "7-zip", "7zip", "winrar", "winzip", "notepad++", "notepadpp",
    "autodesk", "autocad", "revit", "maya", "3ds max", "3dsmax",
    "internet explorer", "ie", "edge", "chrome", "firefox", "opera", "brave",
    "bluestacks", "bluestacks nxt", "bluestacks x", "nox", "ldplayer", "gameloop",
    "vmware", "virtualbox", "docker", "git", "github desktop", "vs code", "vscode",
    "visual studio", "visual studio code", "jetbrains", "intellij", "pycharm",
    "office", "microsoft office", "onedrive", "teams", "skype", "zoom", "discord",
    "obs-studio", "obs studio", "streamlabs", "nvidia geforce experience",
    "radeon", "realtek", "drivers", "driver", "installer", "installshield",
    "c++", "msvc", "vcredist", "directx", "runtime", "redistributable",
    "filmora", "davinci", "premiere", "after effects", "photoshop", "illustrator",
    "netmod", "vpn", "wireguard", "openvpn", "nordvpn",
    "windows defender", "malwarebytes", "avast", "avg", "kaspersky",
    "hp", "dell", "lenovo", "asus", "acer", "logitech", "razer synapse",
}

NOMBRES_NO_JUEGO = re.compile(
    r"(?i)^(7-?zip|winrar|winzip|autodesk|autocad|internet\\s*explorer|"
    r"bluestacks|filmora|netmod|notepad|chrome|firefox|edge|discord|"
    r"obs|docker|git|python|java|office|teams|skype|zoom).*$"
)

CARPETAS_JUEGOS = {
    "games", "juegos", "my games", "mis juegos", "game", "juegos pc", "pc games",
    "steamapps", "common", "origin games", "ubisoft", "gog galaxy", "gog games",
    "battle.net", "riot games", "xbox games", "downloads", "descargas",
}

MARCAS = {
    "unityplayer.dll", "gameassembly.dll", "steam_api.dll", "steam_api64.dll",
    "galaxy64.dll", "eossdk-win64-shipping.dll", "binkw64.dll", "data.win",
    "renpy.exe", "ue4game.exe", "ue5game.exe", "engine.ini", "gameinfo.txt",
}

NO_EXE = re.compile(
    r"(?i)unins|crash|redist|dxsetup|dotnet|setup|helper|updater|cleanup|"
    r"oalinst|physx|dxwebsetup|vc_?runtime|notification|launcher|bootstrap|install|uninstall|repair"
)


def _es_juego(d, max_depth=3):
    base = d.count(os.sep)
    try:
        for r, ds, fs in os.walk(d):
            depth = r.count(os.sep) - base
            if depth >= max_depth:
                ds[:] = []
                continue
            low_fs = {x.lower() for x in fs}
            if any(m in low_fs for m in MARCAS):
                return True
            if r == d and any(x.lower().endswith("_data") for x in ds) and any(x.lower().endswith(".exe") for x in fs):
                return True
            low_ds = {x.lower() for x in ds}
            if {"binaries", "engine"} <= low_ds or {"bin", "data"} <= low_ds:
                return True
    except Exception:
        pass
    return False


def _mejor_exe(d, max_depth=3):
    mejor, tam, base = None, 1 << 18, d.count(os.sep)
    try:
        for r, ds, fs in os.walk(d):
            if r.count(os.sep) - base >= max_depth:
                ds[:] = []
                continue
            for f in fs:
                if f.lower().endswith(".exe") and not NO_EXE.search(f):
                    p = os.path.join(r, f)
                    try:
                        s = os.path.getsize(p)
                        if s > tam:
                            mejor, tam = p, s
                    except Exception:
                        pass
    except Exception:
        pass
    return mejor


def _buscar_generico(vistos):
    try:
        extra = json.load(open(CFG, encoding="utf-8")).get("carpetas_pc", [])
    except Exception:
        extra = []
    candidatos, carpetas_juegos = [], list(extra)

    for pf in (os.environ.get("ProgramFiles", r"C:\\Program Files"),
               os.environ.get("ProgramFiles(x86)", r"C:\\Program Files (x86)")):
        if os.path.isdir(pf):
            try:
                candidatos += [e.path for e in os.scandir(pf) if e.is_dir()]
            except Exception:
                pass

    for c in string.ascii_uppercase:
        root = f"{c}:\\"
        if not os.path.isdir(root):
            continue
        try:
            for e in os.scandir(root):
                if not e.is_dir():
                    continue
                low = e.name.lower()
                if low in EXCLUIR or low.startswith("$"):
                    continue
                if low in CARPETAS_JUEGOS:
                    carpetas_juegos.append(e.path)
                else:
                    candidatos.append(e.path)
        except Exception:
            pass

    hallados = []
    for cj in carpetas_juegos:
        try:
            for e in os.scandir(cj):
                if e.is_dir() and e.name.lower() not in EXCLUIR:
                    hallados.append((e.path, True))
        except Exception:
            pass
    hallados += [(c, False) for c in candidatos
                 if os.path.basename(c).lower() not in EXCLUIR
                 and not os.path.basename(c).lower().startswith("microsoft")]

    out = []
    for d, seguro in hallados:
        low = d.lower().replace("/", "\\")
        if "\\steamapps\\" in low or low.startswith(BASE.lower().replace("/", "\\")):
            continue
        nom = re.sub(r"[_.]+", " ", os.path.basename(d)).strip()
        if not nom or nom.lower() in vistos:
            continue
        if NOMBRES_NO_JUEGO.match(nom):
            continue
        if seguro or _es_juego(d):
            exe = _mejor_exe(d)
            if exe:
                out.append(("PC", nom, exe, None))
                vistos.add(nom.lower())
    return out


_cache_pc = {"t": 0, "lista": [], "corriendo": False, "progreso": ""}


def _buscar_pc():
    lista = stores.detectar_tiendas()
    lista += [g for g in stores.detectar_steam(extra=[os.path.join(BASE, "Steam", "steamapps")])
              if g[3] not in {x[3] for x in lista if x[0] == "Steam"}]
    lista += _buscar_generico({n.lower() for _, n, _, _ in lista})
    return lista


def detectar_pc(forzar=False):
    ahora = time.time()
    if (forzar or ahora - _cache_pc["t"] > 90) and not _cache_pc.get("corriendo"):
        _cache_pc["corriendo"] = True
        _cache_pc["progreso"] = "Escaneando discos..."
        def tarea():
            try:
                _cache_pc["lista"] = _buscar_pc()
                _cache_pc["progreso"] = f"Encontrados {len(_cache_pc['lista'])} juegos"
            except Exception as e:
                _cache_pc["progreso"] = f"Error: {e}"
            _cache_pc["t"] = time.time()
            _cache_pc["corriendo"] = False
        threading.Thread(target=tarea, daemon=True).start()
    return _cache_pc["lista"]


def _es_rom_valida(nombre, sistema):
    ext = os.path.splitext(nombre)[1].lower()
    if sistema in EXT_ROM:
        return ext in EXT_ROM[sistema]
    if sistema in ("Retro", "PC", "Arcade"):
        return ext not in {".part", ".txt", ".jpg", ".png", ".nfo", ".url"} and not nombre.startswith(".")
    return ext not in {".part", ".txt", ".jpg", ".png", ".nfo"}


def escanear(forzar=False):
    out = []
    for sis, nom, ruta, appid in detectar_pc(forzar):
        out.append((sis, nom, ruta, appid))
    try:
        for sis in sorted(os.listdir(JUEGOS)):
            d = os.path.join(JUEGOS, sis)
            if not os.path.isdir(d):
                continue
            for root, dirs, files in os.walk(d):
                dirs[:] = [x for x in dirs if not x.startswith(".")]
                for f in files:
                    if _es_rom_valida(f, sis):
                        out.append((sis, os.path.splitext(f)[0], os.path.join(root, f), None))
                if sis == "PS4":
                    for sub in dirs:
                        p = os.path.join(root, sub)
                        if os.path.exists(os.path.join(p, "eboot.bin")):
                            out.append(("PS4", sub, p, None))
    except Exception as e:
        print("Error escaneando ROMs:", e)
    try:
        out += ps4.listar_instalados()
    except Exception:
        pass
    return out
