"""
Mi Consola - Soporte PS4 (shadPS4)

- Lee param.sfo de una carpeta de juego para obtener TITLE y TITLE_ID.
- Detecta icon0.png (portada oficial del juego) en sce_sys.
- Valida que la carpeta sea un juego listo para shadPS4 (tiene eboot.bin).

shadPS4 necesita juegos YA instalados/volcados (carpeta con eboot.bin).
Los .pkg se instalan desde la propia interfaz de shadPS4.
"""
import os
import struct

SFO_MAGIC = b"\x00PSF"


def leer_sfo(ruta_sfo):
    """Devuelve dict {clave: valor} del param.sfo, o {} si falla."""
    try:
        with open(ruta_sfo, "rb") as f:
            datos = f.read(1 << 20)
        if datos[:4] != SFO_MAGIC:
            return {}
        _ver, key_off, data_off, n = struct.unpack_from("<IIII", datos, 4)
        out = {}
        for i in range(min(n, 256)):
            kofs, fmt, ln, _mx, dofs = struct.unpack_from("<HHIII", datos, 20 + i * 16)
            kini = key_off + kofs
            kfin = datos.index(b"\x00", kini)
            clave = datos[kini:kfin].decode("ascii", "ignore")
            bruto = datos[data_off + dofs: data_off + dofs + ln]
            if fmt == 0x0204 or fmt == 0x0004:
                out[clave] = bruto.split(b"\x00", 1)[0].decode("utf-8", "ignore")
            elif fmt == 0x0404 and len(bruto) >= 4:
                out[clave] = struct.unpack("<I", bruto[:4])[0]
        return out
    except Exception:
        return {}


def es_juego_ps4(carpeta):
    return os.path.isfile(os.path.join(carpeta, "eboot.bin"))


def info_juego(carpeta):
    """(titulo, title_id, ruta_icono) de una carpeta de juego PS4."""
    sce = os.path.join(carpeta, "sce_sys")
    sfo = leer_sfo(os.path.join(sce, "param.sfo"))
    titulo = (sfo.get("TITLE") or "").strip() or os.path.basename(carpeta)
    tid = sfo.get("TITLE_ID") or os.path.basename(carpeta)
    icono = os.path.join(sce, "icon0.png")
    return titulo, tid, (icono if os.path.exists(icono) else None)


def buscar_juegos(raiz):
    """Busca juegos PS4 (carpetas con eboot.bin) hasta 3 niveles dentro de raiz.
    Devuelve lista de (titulo, carpeta). No entra dentro de un juego ya detectado."""
    out = []
    if not os.path.isdir(raiz):
        return out
    base = raiz.rstrip("\\/").count(os.sep)
    for r, ds, _fs in os.walk(raiz):
        if r.count(os.sep) - base >= 3:
            ds[:] = []
            continue
        if es_juego_ps4(r):
            out.append((info_juego(r)[0], r))
            ds[:] = []
    return out


def paquetes_pkg(raiz, max_depth=2):
    """Lista de .pkg sueltos (hay que instalarlos desde shadPS4).
    Solo mira los primeros niveles para no recorrer carpetas de juegos enormes."""
    pkgs = []
    if not os.path.isdir(raiz):
        return pkgs
    base = raiz.rstrip("\\/").count(os.sep)
    for r, ds, fs in os.walk(raiz):
        if r.count(os.sep) - base >= max_depth or es_juego_ps4(r):
            ds[:] = []
        pkgs += [os.path.join(r, f) for f in fs if f.lower().endswith(".pkg")]
    return pkgs
