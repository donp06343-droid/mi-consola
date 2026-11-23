"""
Mi Consola - Cola de descargas
"""
import os
import re
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


def _ruta_segura(destino, rel):
    """Devuelve una ruta dentro de destino o None si el miembro intenta salir."""
    import ntpath
    rel = str(rel).replace("\\", "/")
    if not rel or rel.startswith("/") or ntpath.isabs(rel):
        return None
    if re.match(r"^[a-zA-Z]:", rel):
        return None
    partes = rel.split("/")
    if any(p in ("", ".", "..") for p in partes):
        return None
    base = os.path.realpath(destino)
    out = os.path.realpath(os.path.join(base, *partes))
    try:
        if os.path.commonpath((base, out)) != base:
            return None
    except (ValueError, OSError):
        return None
    return out


def _extraer_plano(zip_path, destino):
    """Extrae ZIP de forma segura y aplana una única carpeta raíz."""
    os.makedirs(destino, exist_ok=True)
    with zipfile.ZipFile(zip_path) as z:
        nombres = [n for n in z.namelist() if n and not n.endswith(("/", "\\"))]
        raices = {n.replace("\\", "/").split("/", 1)[0] for n in nombres}
        quitar = len(raices) == 1 and all("/" in n.replace("\\", "/") for n in nombres)
        for info in z.infolist():
            raw = info.filename.replace("\\", "/")
            if quitar:
                raw = raw.split("/", 1)[1] if "/" in raw else ""
            if not raw or raw.endswith("/"):
                continue
            out = _ruta_segura(destino, raw)
            if out is None:
                continue
            # No convertir enlaces simbólicos del ZIP en archivos del sistema.
            modo = (info.external_attr >> 16) & 0o170000
            if modo == 0o120000:
                continue
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with z.open(info) as src, open(out, "wb") as dst:
                shutil.copyfileobj(src, dst)


def _extraer_7z(arc_path, destino):
    """Extrae .7z a un temporal, aplana una raíz y copia solo rutas seguras."""
    os.makedirs(destino, exist_ok=True)

    def _aplanar_desde(tmp):
        entries = [e for e in os.listdir(tmp) if e not in (".", "..")]
        raiz = None
        if len(entries) == 1 and os.path.isdir(os.path.join(tmp, entries[0])):
            raiz = os.path.join(tmp, entries[0])
        src_root = raiz or tmp
        for root, dirs, files in os.walk(src_root, followlinks=False):
            dirs[:] = [d for d in dirs if not os.path.islink(os.path.join(root, d))]
            for f in files:
                full = os.path.join(root, f)
                if os.path.islink(full) or not os.path.isfile(full):
                    continue
                rel = os.path.relpath(full, src_root)
                out = _ruta_segura(destino, rel)
                if out is None:
                    continue
                os.makedirs(os.path.dirname(out), exist_ok=True)
                shutil.move(full, out)

    tmp = destino + ".__7z_tmp"
    if os.path.isdir(tmp):
        shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp, exist_ok=True)
    try:
        try:
            import py7zr
        except ImportError:
            py7zr = None
        if py7zr is not None:
            with py7zr.SevenZipFile(arc_path, mode="r") as z:
                # Validar todos los nombres antes de extraer: el temporal también
                # debe quedar protegido frente a miembros con rutas externas.
                if any(_ruta_segura(tmp, name) is None for name in z.getnames()):
                    raise RuntimeError("El archivo 7z contiene rutas no permitidas")
                z.extractall(path=tmp)
        else:
            candidatos = ("7z", "7z.exe", "7za", "7za.exe",
                          os.path.join(BASE, "tools", "7z.exe"),
                          os.path.join(BASE, "tools", "7za.exe"))
            exe = next((c if os.path.isabs(c) and os.path.isfile(c) else shutil.which(c)
                        for c in candidatos
                        if (os.path.isabs(c) and os.path.isfile(c)) or shutil.which(c)), None)
            if not exe:
                raise RuntimeError(
                    "No hay soporte .7z: instala py7zr o coloca 7z.exe en PATH / tools/"
                )
            r = subprocess.run(
                [exe, "x", "-y", f"-o{tmp}", arc_path],
                capture_output=True, text=True, timeout=600,
            )
            if r.returncode != 0:
                raise RuntimeError(
                    f"7z fallo ({r.returncode}): {(r.stderr or r.stdout or '')[:120]}"
                )
        _aplanar_desde(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _extraer_archivo(path, destino_fijo, carpeta, nombre):
    """
    Instala un archivo descargado y devuelve la ruta que realmente quedó lista.
    El comprimido solo se elimina después de una extracción correcta.
    """
    low = path.lower()
    if low.endswith((".zip", ".7z")):
        dest = destino_fijo or os.path.join(carpeta, nombre)
        if low.endswith(".zip"):
            _extraer_plano(path, dest)
        else:
            _extraer_7z(path, dest)
        # No informar éxito si la extracción no produjo ningún archivo.
        contiene_archivos = any(
            os.path.isfile(os.path.join(root, name))
            for root, _, files in os.walk(dest)
            for name in files
        )
        if not contiene_archivos:
            raise RuntimeError("El archivo se extrajo, pero no contiene archivos instalables")
        os.remove(path)
        return dest
    return path

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
                # La tarea solo avanza cuando el archivo está descargado e,
                # si corresponde, extraído correctamente. Si falla la extracción,
                # el error llega al manejador principal y no se marca como listo.
                ruta_lista = _extraer_archivo(
                    dest, destino_fijo, carpeta, item["nombre"]
                )
                item["listos"].append(ruta_lista)
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
