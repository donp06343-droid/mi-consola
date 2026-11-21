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

from config import BASE, JUEGOS, CFG, DESTINOS, EXT_ROM, FAVORITOS_CFG


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
}

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
            if depth <= 1 and sum(1 for f in fs if f.lower().endswith(".exe")) >= 2:
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

    for pf in (os.environ.get("ProgramFiles", r"C:\Program Files"),
               os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")):
        if os.path.isdir(pf):
            try:
                candidatos += [e.path for e in os.scandir(pf) if e.is_dir()]
            except Exception:
                pass

    for c in string.ascii_uppercase:
        raiz = f"{c}:\\"
        if not os.path.exists(raiz):
            continue
        try:
            for e in os.scandir(raiz):
                if not e.is_dir():
                    continue
                n = e.name.lower()
                if n in CARPETAS_JUEGOS:
                    carpetas_juegos.append(e.path)
                elif n not in EXCLUIR and not n.startswith("$") and not n.startswith("."):
                    candidatos.append(e.path)
        except Exception:
            pass

    userprofile = os.environ.get("USERPROFILE", "")
    if userprofile:
        for sub in ("Downloads", "Descargas", "Desktop", "Escritorio", "Documents", "Documentos", "Games", "Juegos"):
            p = os.path.join(userprofile, sub)
            if os.path.isdir(p):
                carpetas_juegos.append(p)

    hallados = []
    for g in carpetas_juegos:
        try:
            for e in os.scandir(g):
                if e.is_dir():
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
        if seguro or _es_juego(d):
            exe = _mejor_exe(d)
            if exe:
                out.append(("PC", nom, exe, None))
                vistos.add(nom.lower())
    return out


_cache_pc = {"t": 0, "lista": [], "corriendo": False, "progreso": ""}


def _buscar_pc():
    lista = []
    epic = os.path.join(os.environ.get("ProgramData", r"C:\ProgramData"), "Epic", "EpicGamesLauncher", "Data", "Manifests")
    if os.path.isdir(epic):
        for f in os.listdir(epic):
            if f.endswith(".item"):
                try:
                    with open(os.path.join(epic, f), encoding="utf-8") as fh:
                        m = json.load(fh)
                    exe = os.path.join(m.get("InstallLocation", ""), m.get("LaunchExecutable", ""))
                    if m.get("LaunchExecutable") and os.path.exists(exe):
                        lista.append(("Epic", m.get("DisplayName", "Epic Game"), exe, None))
                except Exception:
                    pass

    pf = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
    raiz = os.path.join(pf, "Steam", "steamapps")
    bibs = {raiz, os.path.join(BASE, "Steam", "steamapps")}
    try:
        vdf = os.path.join(raiz, "libraryfolders.vdf")
        if os.path.exists(vdf):
            with open(vdf, encoding="utf-8", errors="ignore") as fh:
                for p in re.findall(r'"path"\s+"([^"]+)"', fh.read()):
                    bibs.add(os.path.join(p.replace("\\\\", "\\"), "steamapps"))
    except Exception:
        pass

    for b in bibs:
        if os.path.isdir(b):
            for f in os.listdir(b):
                if f.startswith("appmanifest_") and f.endswith(".acf"):
                    try:
                        t = open(os.path.join(b, f), encoding="utf-8", errors="ignore").read()
                        appid_m = re.search(r'"appid"\s+"(\d+)"', t)
                        nom_m = re.search(r'"name"\s+"([^"]+)"', t)
                        if appid_m and nom_m:
                            nom = nom_m.group(1)
                            if not re.search(r"(?i)steamworks|redistributable|proton|directx|vc_?redist", nom):
                                lista.append(("Steam", nom, f"steam://rungameid/{appid_m.group(1)}", appid_m.group(1)))
                    except Exception:
                        pass

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
                dirs[:] = [x for x in dirs if not x.startswith(".") and x.lower() not in {
                    "cache", "saves", "savestates", "screenshots", "covers", "media"
                }]
                for e in sorted(files):
                    if e.endswith(".part") or e.startswith("."):
                        continue
                    if not _es_rom_valida(e, sis):
                        continue
                    ruta = os.path.join(root, e)
                    nom = os.path.splitext(e)[0]
                    nom = re.sub(r"[\(\[].*?[\)\]]", "", nom).strip()
                    nom = re.sub(r"[_.]+", " ", nom).strip()
                    if nom:
                        out.append((sis, nom, ruta, None))
                for carp in dirs:
                    eboot = os.path.join(root, carp, "eboot.bin")
                    if os.path.exists(eboot):
                        out.append((sis, carp, os.path.join(root, carp), None))
    except Exception:
        pass
    return out


def cargar_cfg():
    from config import EMU_DEFECTO
    os.makedirs(JUEGOS, exist_ok=True)
    os.makedirs(os.path.join(BASE, "Covers"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "cache_portadas"), exist_ok=True)
    for d in DESTINOS:
        os.makedirs(os.path.join(JUEGOS, d), exist_ok=True)
    os.makedirs(os.path.join(BASE, "emulators"), exist_ok=True)
    if not os.path.exists(CFG):
        with open(CFG, "w", encoding="utf-8") as f:
            json.dump(EMU_DEFECTO, f, indent=2, ensure_ascii=False)
    with open(CFG, encoding="utf-8") as f:
        cfg = json.load(f)
    for k, v in EMU_DEFECTO.items():
        if k not in cfg:
            cfg[k] = v
    return cfg
