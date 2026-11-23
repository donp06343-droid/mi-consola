"""
Mi Consola - Tiendas conectadas (deteccion de juegos INSTALADOS y lanzamiento)

Cada proveedor devuelve tuplas  (sistema, nombre, ruta_o_uri, appid)  igual que library.py.
  - Steam : appmanifest_*.acf        -> steam://rungameid/<id>
  - Epic  : Manifests\\*.item         -> com.epicgames.launcher://apps/<AppName>?action=launch&silent=true
  - GOG   : registro HKLM\\...\\GOG.com\\Games -> exe del juego (GOG es DRM-free)
  - EA    : registro HKLM\\SOFTWARE\\EA Games y Origin Games -> origin:// o carpeta
  - Ubisoft: HKLM\\...\\Ubisoft\\Launcher\\Installs -> uplay://launch/<id>/0

Todo es lectura local: no pide cuentas, claves ni contrasenas.
Para agregar una tienda nueva: escribir detectar_xxx() y sumarla a PROVEEDORES.

Verificado / NO VERIFICADO: ver VERIFICACION.md.
"""
import json
import os
import re

try:                      # solo Windows
    import winreg
except ImportError:       # pragma: no cover
    winreg = None

# ----- URIs de las tiendas (para abrir el cliente sin navegador) -----
TIENDAS_URI = {
    "Steam": "steam://store",
    "Epic": "com.epicgames.launcher://store",
    "GOG": "goggalaxy://",              # NO VERIFICADO
    "Xbox": "ms-windows-store://home",  # NO VERIFICADO
    "EA": "origin2://library/open",     # NO VERIFICADO (alternativas: origin://, origin2://store/open)
    "Ubisoft": "uplay://",              # NO VERIFICADO (abre Ubisoft Connect)
}

INFO_STEAM = {}      # appid -> {'size': bytes, 'updated': epoch}

_BASURA_STEAM = re.compile(
    r"(?i)steamworks|redistributable|proton|directx|vc_?redist|steam linux runtime"
)


# ---------------------------------------------------------------------------
# Helpers registro
# ---------------------------------------------------------------------------
def _valor(k, nombre):
    try:
        return winreg.QueryValueEx(k, nombre)[0]
    except OSError:
        return None


def _enum_subkeys(raiz):
    i = 0
    while True:
        try:
            yield winreg.EnumKey(raiz, i)
        except OSError:
            break
        i += 1


def _open_hklm(path, vistas=None):
    """Abre HKLM\\path en 64 y/o 32 bits. Yield de handles abiertos."""
    if not winreg:
        return
    if vistas is None:
        vistas = (
            getattr(winreg, "KEY_WOW64_64KEY", 0),
            getattr(winreg, "KEY_WOW64_32KEY", 0),
        )
    for vista in vistas:
        try:
            yield winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_READ | vista)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Steam
# ---------------------------------------------------------------------------
def _carpetas_steam(extra=()):
    pf86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
    raices = {os.path.join(pf86, "Steam", "steamapps")}
    raices.update(extra)
    if winreg:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as k:
                p = winreg.QueryValueEx(k, "SteamPath")[0]
                raices.add(os.path.join(p.replace("/", "\\"), "steamapps"))
        except OSError:
            pass
    for r in list(raices):
        vdf = os.path.join(r, "libraryfolders.vdf")
        try:
            with open(vdf, encoding="utf-8", errors="ignore") as fh:
                for p in re.findall(r'"path"\s+"([^"]+)"', fh.read()):
                    raices.add(os.path.join(p.replace("\\\\", "\\"), "steamapps"))
        except OSError:
            pass
    return [x for x in raices if os.path.isdir(x)]


def detectar_steam(extra=()):
    out = []
    vistos = set()
    for apps in _carpetas_steam(extra):
        try:
            nombres = os.listdir(apps)
        except OSError:
            continue
        for fn in nombres:
            if not (fn.startswith("appmanifest_") and fn.endswith(".acf")):
                continue
            path = os.path.join(apps, fn)
            try:
                txt = open(path, encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            appid = re.search(r'"appid"\s+"(\d+)"', txt)
            nombre = re.search(r'"name"\s+"([^"]+)"', txt)
            estado = re.search(r'"StateFlags"\s+"(\d+)"', txt)
            tam = re.search(r'"SizeOnDisk"\s+"(\d+)"', txt)
            if not (appid and nombre) or appid.group(1) in vistos:
                continue
            if _BASURA_STEAM.search(nombre.group(1)):
                continue
            if estado and (int(estado.group(1)) & 4) == 0:
                continue
            vistos.add(appid.group(1))
            INFO_STEAM[appid.group(1)] = {
                "size": int(tam.group(1)) if tam else None,
                "updated": None,
            }
            out.append(("Steam", nombre.group(1), f"steam://rungameid/{appid.group(1)}", appid.group(1)))
    return out


# ---------------------------------------------------------------------------
# Epic
# ---------------------------------------------------------------------------
def detectar_epic():
    out = []
    bases = [
        os.path.join(os.environ.get("ProgramData", r"C:\ProgramData"),
                     "Epic", "EpicGamesLauncher", "Data", "Manifests"),
        os.path.join(os.environ.get("ProgramData", r"C:\ProgramData"),
                     "Epic", "EpicGamesLauncher", "Manifests"),
    ]
    for base in bases:
        if not os.path.isdir(base):
            continue
        try:
            files = os.listdir(base)
        except OSError:
            continue
        for fn in files:
            if not fn.endswith(".item"):
                continue
            path = os.path.join(base, fn)
            try:
                with open(path, encoding="utf-8", errors="ignore") as fh:
                    m = json.load(fh)
            except Exception:
                continue
            app = m.get("AppName") or m.get("CatalogNamespace")
            if not app:
                continue
            if m.get("MainGameAppName") and m["MainGameAppName"] != app:
                continue
            if not m.get("LaunchExecutable"):
                continue
            out.append((
                "Epic",
                m.get("DisplayName") or app,
                f"com.epicgames.launcher://apps/{app}?action=launch&silent=true",
                None,
            ))
    return out


# ---------------------------------------------------------------------------
# GOG
# ---------------------------------------------------------------------------
def detectar_gog():
    out = []
    if not winreg:
        return out
    for vista in (getattr(winreg, "KEY_WOW64_64KEY", 0), getattr(winreg, "KEY_WOW64_32KEY", 0)):
        try:
            raiz = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\GOG.com\Games", 0,
                winreg.KEY_READ | vista,
            )
        except OSError:
            continue
        with raiz:
            for sub in _enum_subkeys(raiz):
                try:
                    with winreg.OpenKey(raiz, sub) as k:
                        nombre = _valor(k, "gameName")
                        carpeta = _valor(k, "path")
                        exe = _valor(k, "exe")
                    if not nombre or not carpeta:
                        continue
                    ruta = exe if exe and os.path.exists(exe) else carpeta
                    if not any(g[1] == nombre for g in out):
                        out.append(("GOG", nombre, ruta, None))
                except OSError:
                    pass
    return out


# ---------------------------------------------------------------------------
# EA App / Origin (registro local; sin API ni login)
# ---------------------------------------------------------------------------
def detectar_ea():
    """
    Lee HKLM\\SOFTWARE\\EA Games\\<titulo>\\Install Dir y
    HKLM\\SOFTWARE\\WOW6432Node\\Origin Games\\<contentId>.
    Lanza por origin://launchgame/<id> cuando hay contentId; si no, por carpeta.
    Fuentes: Lutris#5160, Reddit EAApp, GameFinder wiki (registro como alternativa).
    Protocolo origin:// / origin2://: NO VERIFICADO en PC real.
    """
    out = []
    if not winreg:
        return out
    vistos = set()

    for k in _open_hklm(r"SOFTWARE\EA Games"):
        with k:
            for sub in _enum_subkeys(k):
                try:
                    with winreg.OpenKey(k, sub) as sk:
                        inst = _valor(sk, "Install Dir") or _valor(sk, "InstallDir")
                    if not inst:
                        continue
                    inst = str(inst).rstrip("\\/")
                    if not os.path.isdir(inst):
                        continue
                    key = sub.lower()
                    if key in vistos:
                        continue
                    vistos.add(key)
                    out.append(("EA", sub, inst, None))
                except OSError:
                    pass

    for path in (r"SOFTWARE\WOW6432Node\Origin Games", r"SOFTWARE\Origin Games"):
        for k in _open_hklm(path, vistas=(0,)):
            with k:
                for sub in _enum_subkeys(k):
                    try:
                        with winreg.OpenKey(k, sub) as sk:
                            display = _valor(sk, "DisplayName") or _valor(sk, "ProductName") or sub
                            inst = (
                                _valor(sk, "Install Dir")
                                or _valor(sk, "InstallDir")
                                or _valor(sk, "InstallLocation")
                            )
                        if sub in vistos:
                            continue
                        vistos.add(sub)
                        ruta = f"origin://launchgame/{sub}"
                        out.append(("EA", str(display), ruta, sub))
                    except OSError:
                        pass

    return out


# ---------------------------------------------------------------------------
# Ubisoft Connect (Uplay)
# ---------------------------------------------------------------------------
def detectar_ubisoft():
    """
    HKLM\\SOFTWARE\\WOW6432Node\\Ubisoft\\Launcher\\Installs\\<id>\\InstallDir
    Nombre: Uninstall\\Uplay Install {id}\\DisplayName (si existe).
    Lanza: uplay://launch/<id>/0
    Fuentes: modding.wiki Vortex, RizSavio/UplayGameIDs, Ubisoft Help.
    Protocolo uplay://: de uso comun, NO VERIFICADO contra doc oficial en esta PC.
    """
    out = []
    if not winreg:
        return out
    vistos = set()

    for path in (
        r"SOFTWARE\WOW6432Node\Ubisoft\Launcher\Installs",
        r"SOFTWARE\Ubisoft\Launcher\Installs",
    ):
        for k in _open_hklm(path, vistas=(0,)):
            with k:
                for sub in _enum_subkeys(k):
                    if sub in vistos:
                        continue
                    try:
                        with winreg.OpenKey(k, sub) as sk:
                            inst = _valor(sk, "InstallDir") or _valor(sk, "Install Dir")
                        nombre = None
                        for uninst in (
                            rf"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Uplay Install {sub}",
                            rf"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Uplay Install {sub}",
                        ):
                            for uk in _open_hklm(uninst, vistas=(0,)):
                                with uk:
                                    nombre = _valor(uk, "DisplayName")
                                if nombre:
                                    break
                            if nombre:
                                break
                        if not nombre:
                            if inst:
                                nombre = os.path.basename(str(inst).rstrip("\\/")) or f"Ubisoft {sub}"
                            else:
                                nombre = f"Ubisoft {sub}"
                        vistos.add(sub)
                        out.append(("Ubisoft", str(nombre), f"uplay://launch/{sub}/0", sub))
                    except OSError:
                        pass
    return out


# ---------------------------------------------------------------------------
PROVEEDORES = (
    detectar_steam,
    detectar_epic,
    detectar_gog,
    detectar_ea,
    detectar_ubisoft,
)


def detectar_tiendas():
    """Juegos instalados de todas las tiendas. Un proveedor que falla no rompe a los demas."""
    out = []
    for prov in PROVEEDORES:
        try:
            out += prov()
        except Exception:
            pass
    return out


def es_uri(ruta):
    """True si la ruta es un protocolo de tienda (steam://, uplay://, origin://, ...)."""
    return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9+.\-]{2,}://", str(ruta))) and not str(ruta).lower().startswith(
        ("http://", "https://")
    )
