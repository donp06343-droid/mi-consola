"""Diagnostico de emuladores para la vista Estado del sistema."""
import os
from config import BASE, EMU_DEFECTO
from launcher import _resolver_exe
from store import TIENDA


def lista_estado_emuladores(cfg):
    """Emuladores de la tienda: instalado/falta + ruta. Usa _resolver_exe."""
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
            try:
                if sis:
                    ruta = _resolver_exe(sis, cfg)
                if not ruta and j.get("emu"):
                    carpeta = os.path.join(BASE, j["emu"])
                    if os.path.isdir(carpeta):
                        for nom in os.listdir(carpeta):
                            if nom.lower().endswith(".exe"):
                                cand = os.path.join(carpeta, nom)
                                if os.path.isfile(cand):
                                    ruta = cand
                                    break
            except Exception:
                ruta = None
            esperado = ""
            try:
                if sis and EMU_DEFECTO.get(sis):
                    esperado = EMU_DEFECTO[sis][0]
                elif j.get("emu"):
                    esperado = os.path.join(BASE, j["emu"])
            except Exception:
                pass
            filas.append({
                "nombre": j.get("n", "?"),
                "sistema": sis or "—",
                "instalado": bool(ruta),
                "ruta": ruta or "",
                "esperado": esperado,
                "item": j,
            })
    except Exception:
        pass
    return filas
