"""
Mi Consola - Cola de descargas
"""
import os
import shutil
import time
import zipfile
import threading
import urllib.request
import urllib.parse
import subprocess

from config import JUEGOS, BASE

cola = []


def nombre_archivo(url, n):
    return os.path.basename(urllib.parse.unquote(urllib.parse.urlparse(url).path)) or f"archivo_{n}"


def soporte_7z():
    """True si se puede extraer .7z (py7zr o 7z en PATH/tools)."""
    try:
        import py7zr  # noqa: F401
        return True, "py7zr"
    except ImportError:
        pass
    except Exception:
        pass
    for c in ("7z", "7z.exe", "7za", "7za.exe",
              os.path.join(BASE, "tools", "7z.exe"),
              os.path.join(BASE, "tools", "7za.exe")):
        try:
            if os.path.isabs(c) and os.path.exists(c):
                return True, c
            found = shutil.which(c)
            if found:
                return True, found
        except Exception:
            continue
    return False, None


def _extraer_plano(zip_path, destino):
    """Extrae el zip en destino. Si todo viene dentro de UNA carpeta raiz,
    la quita para que el .exe quede directamente en destino."""
    with zipfile.ZipFile(zip_path) as z:
        nombres = [n for n in z.namelist() if n and not n.endswith("/")]
        raices = {n.split("/", 1)[0] for n in nombres}
        quitar = len(raices) == 1 and all("/" in n for n in nombres)
        base = os.path.realpath(destino)
        for info in z.infolist():
            rel = info.filename
            if quitar:
                rel = rel.split("/", 1)[1] if "/" in rel else ""
            if not rel:
                continue
            out = os.path.realpath(os.path.join(destino, rel))
            if not out.startswith(base):
                continue
            if info.is_dir():
                os.makedirs(out, exist_ok=True)
            else:
                os.makedirs(os.path.dirname(out), exist_ok=True)
                with z.open(info) as src, open(out, "wb") as dst:
                    shutil.copyfileobj(src, dst)


def _extraer_7z(arc_path, destino):
    """Extrae .7z a destino (aplanado si hay una sola carpeta raiz).
    Orden: py7zr -> 7z.exe en PATH o BASE/tools.
    """
    base = os.path.realpath(destino)
    os.makedirs(destino, exist_ok=True)

    def _aplanar_desde(tmp):
        entries = [e for e in os.listdir(tmp) if e not in (".", "..")]
        raiz = None
        if len(entries) == 1 and os.path.isdir(os.path.join(tmp, entries[0])):
            raiz = os.path.join(tmp, entries[0])
        src_root = raiz or tmp
        for root, dirs, files in os.walk(src_root):
            for f in files:
                full = os.path.join(root, f)
                rel = os.path.relpath(full, src_root)
                out = os.path.realpath(os.path.join(destino, rel))
                if not out.startswith(base):
                    continue
                os.makedirs(os.path.dirname(out), exist_ok=True)
                shutil.move(full, out)

    try:
        import py7zr  # type: ignore
        tmp = destino + ".__7z_tmp"
        if os.path.isdir(tmp):
            shutil.rmtree(tmp, ignore_errors=True)
        os.makedirs(tmp, exist_ok=True)
        with py7zr.SevenZipFile(arc_path, mode="r") as z:
            z.extractall(path=tmp)
        _aplanar_desde(tmp)
        shutil.rmtree(tmp, ignore_errors=True)
        return
    except ImportError:
        pass
    except Exception as e:
        raise RuntimeError(f"py7zr fallo: {e}") from e

    ok, exe = soporte_7z()
    if not ok or not exe or exe == "py7zr":
        # re-buscar 7z si py7zr no estaba
        candidatos = ["7z", "7z.exe", "7za", "7za.exe",
                      os.path.join(BASE, "tools", "7z.exe"),
                      os.path.join(BASE, "tools", "7za.exe")]
        exe = None
        for c in candidatos:
            if os.path.isabs(c) and os.path.exists(c):
                exe = c
                break
            found = shutil.which(c)
            if found:
                exe = found
                break
    if not exe or exe == "py7zr":
        raise RuntimeError(
            "No hay soporte .7z: pip install py7zr o pone 7z.exe en PATH / tools/"
        )

    tmp = destino + ".__7z_tmp"
    if os.path.isdir(tmp):
        shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp, exist_ok=True)
    r = subprocess.run(
        [exe, "x", "-y", f"-o{tmp}", arc_path],
        capture_output=True, text=True, timeout=600,
    )
    if r.returncode != 0:
        shutil.rmtree(tmp, ignore_errors=True)
        raise RuntimeError(f"7z fallo ({r.returncode}): {(r.stderr or r.stdout or '')[:120]}")
    _aplanar_desde(tmp)
    shutil.rmtree(tmp, ignore_errors=True)


def _extraer_archivo(path, destino_fijo, carpeta, nombre):
    low = path.lower()
    if low.endswith(".zip"):
        if destino_fijo:
            _extraer_plano(path, destino_fijo)
        else:
            dest_dir = os.path.join(carpeta, nombre)
            os.makedirs(dest_dir, exist_ok=True)
            zipfile.ZipFile(path).extractall(dest_dir)
        os.remove(path)
    elif low.endswith(".7z"):
        dest = destino_fijo or os.path.join(carpeta, nombre)
        _extraer_7z(path, dest)
        os.remove(path)


def trabajador():
    while True:
        item = next((i for i in cola if i["estado"] == "en cola"), None)
        if not item:
            time.sleep(0.8)
            continue
        item["estado"] = "bajando"
        try:
            destino_fijo = item.get("destino")
            carpeta = destino_fijo or os.path.join(JUEGOS, item["sistema"])
            os.makedirs(carpeta, exist_ok=True)
            for n, url in enumerate(item["urls"]):
                if n < len(item["listos"]):
                    continue
                item["parte"] = n + 1
                dest = os.path.join(carpeta, nombre_archivo(url, n))
                tmp = dest + ".part"
                tengo = os.path.getsize(tmp) if os.path.exists(tmp) else 0
                req = urllib.request.Request(
                    url,
                    headers={
                        "Range": f"bytes={tengo}-",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MiConsola/5.2",
                    },
                )
                with urllib.request.urlopen(req, timeout=45) as r:
                    largo = int(r.headers.get("Content-Length") or 0)
                    if r.status == 206:
                        modo, item["total"] = "ab", tengo + largo
                    else:
                        modo, tengo, item["total"] = "wb", 0, largo
                    item["hecho"] = tengo
                    with open(tmp, modo) as f:
                        while True:
                            if item["estado"] == "pausado":
                                raise InterruptedError
                            bloque = r.read(1 << 17)
                            if not bloque:
                                break
                            f.write(bloque)
                            item["hecho"] += len(bloque)
                os.replace(tmp, dest)
                if dest.lower().endswith((".zip", ".7z")):
                    try:
                        _extraer_archivo(dest, destino_fijo, carpeta, item["nombre"])
                    except Exception as e:
                        item["error"] = f"No se pudo extraer: {str(e)[:70]}"
                item["listos"].append(dest)
            item["estado"] = "listo"
        except InterruptedError:
            pass
        except Exception as e:
            item["estado"] = "error"
            item["error"] = str(e)[:100]


def agregar_enlaces(texto, sistema, nombre=None, destino=None):
    urls = [l.strip() for l in texto.splitlines() if l.strip().lower().startswith(("http://", "https://"))]
    if not urls:
        return False
    nombre = nombre or os.path.splitext(nombre_archivo(urls[0], 0))[0]
    cola.append({
        "nombre": nombre,
        "sistema": sistema,
        "destino": destino,
        "urls": urls,
        "listos": [],
        "estado": "en cola",
        "parte": 1,
        "hecho": 0,
        "total": 0,
        "error": "",
    })
    return True


def leer_portapapeles():
    try:
        import tkinter
        r = tkinter.Tk()
        r.withdraw()
        t = r.clipboard_get()
        r.destroy()
        return t
    except Exception:
        return ""


threading.Thread(target=trabajador, daemon=True).start()
