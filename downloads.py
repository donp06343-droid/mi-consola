"""
Mi Consola - Cola de descargas
"""
import os
import time
import zipfile
import threading
import urllib.request
import urllib.parse

from config import JUEGOS

cola = []


def nombre_archivo(url, n):
    return os.path.basename(urllib.parse.unquote(urllib.parse.urlparse(url).path)) or f"archivo_{n}"


def trabajador():
    while True:
        item = next((i for i in cola if i["estado"] == "en cola"), None)
        if not item:
            time.sleep(0.8)
            continue
        item["estado"] = "bajando"
        try:
            carpeta = os.path.join(JUEGOS, item["sistema"])
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
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MiConsola/5.0",
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
                if dest.lower().endswith(".zip"):
                    try:
                        zipfile.ZipFile(dest).extractall(os.path.join(carpeta, item["nombre"]))
                        os.remove(dest)
                    except Exception:
                        pass
                item["listos"].append(dest)
            item["estado"] = "listo"
        except InterruptedError:
            pass
        except Exception as e:
            item["estado"] = "error"
            item["error"] = str(e)[:100]


def agregar_enlaces(texto, sistema, nombre=None):
    urls = [l.strip() for l in texto.splitlines() if l.strip().lower().startswith(("http://", "https://"))]
    if not urls:
        return False
    nombre = nombre or os.path.splitext(nombre_archivo(urls[0], 0))[0]
    cola.append({
        "nombre": nombre,
        "sistema": sistema,
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


# Arrancar trabajador
threading.Thread(target=trabajador, daemon=True).start()
