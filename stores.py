"""
Mi Consola - Tiendas conectadas (deteccion de juegos INSTALADOS y lanzamiento)

Cada proveedor devuelve tuplas  (sistema, nombre, ruta_o_uri, appid)  igual que library.py.
  - Steam : appmanifest_*.acf        -> steam://rungameid/<id>
  - Epic  : Manifests\\*.item         -> com.epicgames.launcher://apps/<AppName>?action=launch&silent=true
  - GOG   : registro HKLM\\...\\GOG.com\\Games -> exe del juego (GOG es DRM-free, no necesita Galaxy)

Todo es lectura local: no pide cuentas, claves ni contrasenas.
Para agregar una tienda nueva: escribir detectar_xxx() y sumarla a PROVEEDORES.

Verificado (fuentes en VERIFICACION.md): Epic (manifests + protocolo), GOG (registro), Steam (acf).
NO implementado todavia: Xbox/Microsoft Store, EA App, Ubisoft Connect, Battle.net, itch.io.
"""
import json
import os
import re

try:                      # solo Windows
    import winreg
except ImportError:       # pragma: no cover
    winreg = None

# ----- URIs de las tiendas (para "comprar" sin salir de la consola) -----
TIENDAS_URI = {
    "Steam": "steam://store",
    "Epic": "com.epicgames.launcher://store",
    "GOG": "goggalaxy://",              # NO VERIFICADO
    "Xbox": "ms-windows-store://home",  # NO VERIFICADO
}

_BASURA_STEAM = re.compile(r"(?i)steamworks|redistributable|proton|directx|vc_?redist|steam linux runtime")


# ---------------------------------------------------------------------------
# Steam
# ---------------------------------------------------------------------------
def _carpetas_steam(extra=()):
    pf86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
    raices = {os.path.join(pf86, "Steam", "steamapps")}
    raices.update(extra)
    if winreg:                                   # carpeta real de Steam (HKCU\Software\Valve\Steam)
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as k:
                p = winreg.QueryValueEx(k, "SteamPath")[0]
                raices.add(os.path.join(p.replace("/", "\\"), "steamapps"))
        except OSError:
            pass
    for r in list(raices):                       # bibliotecas en otros discos
        vdf = os.path.join(r, "libraryfolders.vdf")
        try:
            with open(vdf, encoding="utf-8", errors="ignore") as fh:
                for p in re.findall(r'"path"\s+"([^"]+)"', fh.read()):
                    raices.add(os.path.join(p.replace("\\\\", "\\"), "steamapps"))
        except OSError:
            pass
    return [r for r in raices if os.path.isdir(r)]


def detectar_steam(extra=()):
    out, vistos = [], set()
    for b in _carpetas_steam(extra):
        for f in os.listdir(b):
            if not (f.startswith("appmanifest_") and f.endswith(".acf")):
                continue
            try:
                t = open(os.path.join(b, f), encoding="utf-8", errors="ignore").read()
                appid = re.search(r'"appid"\s+"(\d+)"', t)
                nombre = re.search(r'"name"\s+"([^"]+)"', t)
                flags = re.search(r'"StateFlags"\s+"(\d+)"', t)
                if not (appid and nombre) or appid.group(1) in vistos or _BASURA_STEAM.search(nombre.group(1)):
                    continue
                if flags and not (int(flags.group(1)) & 4):     # 4 = instalado por completo
                    continue
                vistos.add(appid.group(1))
                out.append(("Steam", nombre.group(1), f"steam://rungameid/{appid.group(1)}", appid.group(1)))
            except Exception:
                pass
    return out


# ---------------------------------------------------------------------------
# Epic Games Store
# ---------------------------------------------------------------------------
def detectar_epic():
    base = os.path.join(os.environ.get("ProgramData", r"C:\ProgramData"),
                        "Epic", "EpicGamesLauncher", "Data", "Manifests")
    out = []
    if not os.path.isdir(base):
        return out
    for f in os.listdir(base):
        if not f.endswith(".item"):
            continue
        try:
            with open(os.path.join(base, f), encoding="utf-8") as fh:
                m = json.load(fh)
            app = m.get("AppName", "")
            if not app or app.startswith("UE_") or "QuixelBridge" in app:   # motor / plugins
                continue
            if m.get("bIsIncompleteInstall"):
                continue
            if m.get("MainGameAppName") and m["MainGameAppName"] != app:    # DLC
                continue
            if not m.get("LaunchExecutable"):
                continue
            out.append(("Epic", m.get("DisplayName") or app,
                        f"com.epicgames.launcher://apps/{app}?action=launch&silent=true", None))
        except Exception:
            pass
    return out


# ---------------------------------------------------------------------------
# GOG (registro de Windows)
# ---------------------------------------------------------------------------
def _valor(k, nombre):
    try:
        return winreg.QueryValueEx(k, nombre)[0]
    except OSError:
        return None


def detectar_gog():
    out = []
    if not winreg:
        return out
    for vista in (getattr(winreg, "KEY_WOW64_64KEY", 0), getattr(winreg, "KEY_WOW64_32KEY", 0)):
        try:
            raiz = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\GOG.com\Games", 0,
                                  winreg.KEY_READ | vista)
        except OSError:
            continue
        with raiz:
            i = 0
            while True:
                try:
                    sub = winreg.EnumKey(raiz, i)
                except OSError:
                    break
                i += 1
                try:
                    with winreg.OpenKey(raiz, sub) as k:
                        nombre, carpeta, exe = _valor(k, "gameName"), _valor(k, "path"), _valor(k, "exe")
                    if not nombre or not carpeta:
                        continue
                    ruta = exe if exe and os.path.exists(exe) else carpeta
                    if not any(g[1] == nombre for g in out):
                        out.append(("GOG", nombre, ruta, None))
                except OSError:
                    pass
    return out


# ---------------------------------------------------------------------------
PROVEEDORES = (detectar_steam, detectar_epic, detectar_gog)


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
    """True si la ruta es un protocolo de tienda (steam://, com.epicgames.launcher://, etc.)."""
    return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9+.\-]{2,}://", str(ruta))) and not str(ruta).lower().startswith(("http://", "https://"))
