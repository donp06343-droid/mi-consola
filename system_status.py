"""Diagnostico de emuladores para la vista Estado del sistema."""
import os
from config import BASE, EMU_DEFECTO
from launcher import _resolver_exe
from store import TIENDA


def lista_estado_emuladores(cfg=None):
    """Lista emuladores de la tienda: instalado/falta + ruta.
    Reutiliza _resolver_exe del launcher (no duplica logica).
    """
    filas = []
    try:
        vistos = set()
        for j in TIENDA:
            if not j.get("emu"):
                continue
            sis = j.get("sistema") or ""
            key = (j.get("n"), sis)
            if key in vistos:
                continue
            vistos.add(key)
            ruta = None
            esperado = ""
            try:
                cmd = (cfg or {}).get(sis) if cfg else None
                if not cmd:
                    cmd = EMU_DEFECTO.get(sis)
                exe_cfg = cmd[0] if cmd else ""
                if sis and exe_cfg:
                    ruta = _resolver_exe(sis, exe_cfg)
                    esperado = exe_cfg
                if not ruta and j.get("emu"):
                    if not os.path.isabs(str(j["emu"])):
                        carpeta = os.path.join(BASE, j["emu"])
                    else:
                        carpeta = j["emu"]
                    if os.path.isdir(carpeta):
                        for nom in os.listdir(carpeta):
                            if nom.lower().endswith(".exe"):
                                cand = os.path.join(carpeta, nom)
                                if os.path.isfile(cand):
                                    ruta = cand
                                    break
                    if not esperado:
                        esperado = carpeta
            except Exception:
                ruta = None
            filas.append({
                "nombre": j.get("n", "?"),
                "sistema": sis or "—",
                "instalado": bool(ruta),
                "ruta": ruta or "",
                "esperado": esperado or "",
                "item": j,
            })
    except Exception:
        pass
    return filas



def obtener_estado_pc():
    """Devuelve metricas reales del equipo; los sensores no disponibles se omiten."""
    import platform
    import shutil
    datos = {
        "sistema": f"{platform.system()} {platform.release()}",
        "equipo": platform.node() or "PC",
        "cpu": platform.processor() or "CPU no identificada",
        "nucleos": os.cpu_count() or 0,
        "ram_total": 0,
        "ram_usada": 0,
        "ram_pct": None,
        "cpu_pct": None,
        "disco_total": 0,
        "disco_libre": 0,
        "disco_pct": None,
        "gpu": "No disponible en esta lectura",
        "temperatura": "Sensor no disponible",
    }
    try:
        import psutil
        datos["cpu_pct"] = psutil.cpu_percent(interval=None)
        memoria = psutil.virtual_memory()
        datos["ram_total"] = memoria.total
        datos["ram_usada"] = memoria.used
        datos["ram_pct"] = memoria.percent
        raiz = os.path.abspath(os.sep)
        disco = psutil.disk_usage(raiz)
        datos["disco_total"] = disco.total
        datos["disco_libre"] = disco.free
        datos["disco_pct"] = disco.percent
    except Exception:
        try:
            disco = shutil.disk_usage(os.path.abspath(os.sep))
            datos["disco_total"] = disco.total
            datos["disco_libre"] = disco.free
            datos["disco_pct"] = round((disco.used / disco.total) * 100, 1) if disco.total else None
        except Exception:
            pass
    return datos
