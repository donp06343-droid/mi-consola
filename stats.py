"""Estadisticas locales de uso de Mi Consola (sin telemetria ni red)."""
import json
import os
import threading
import time

from config import BASE

RUTA_ESTADISTICAS = os.path.join(BASE, "consola_estadisticas.json")
_LOCK = threading.RLock()


def _leer():
    try:
        with open(RUTA_ESTADISTICAS, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and isinstance(data.get("juegos", {}), dict):
            data.setdefault("juegos", {})
            return data
    except (OSError, ValueError, TypeError):
        pass
    return {"juegos": {}}


def _guardar(data):
    os.makedirs(BASE, exist_ok=True)
    temporal = RUTA_ESTADISTICAS + ".tmp"
    with open(temporal, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(temporal, RUTA_ESTADISTICAS)


def _clave(sistema, nombre):
    return f"{sistema}::{nombre}".casefold()


def registrar_lanzamiento(sistema, nombre, proceso=None):
    """Registra un inicio y, si hay proceso, suma el tiempo real al cerrarse."""
    nombre = str(nombre or "Juego")
    clave = _clave(sistema, nombre)
    inicio = time.time()
    with _LOCK:
        data = _leer()
        juegos = data.setdefault("juegos", {})
        item = juegos.setdefault(clave, {
            "sistema": str(sistema), "nombre": nombre,
            "lanzamientos": 0, "segundos": 0.0, "ultima_vez": 0,
        })
        item["lanzamientos"] = int(item.get("lanzamientos", 0)) + 1
        item["ultima_vez"] = int(inicio)
        try:
            _guardar(data)
        except OSError:
            pass

    if proceso is not None:
        def esperar_y_sumar():
            try:
                proceso.wait()
            except Exception:
                return
            duracion = max(0.0, time.time() - inicio)
            with _LOCK:
                actual = _leer()
                registro = actual.setdefault("juegos", {}).get(clave)
                if registro is not None:
                    registro["segundos"] = float(registro.get("segundos", 0.0)) + duracion
                    try:
                        _guardar(actual)
                    except OSError:
                        pass
        threading.Thread(target=esperar_y_sumar, daemon=True).start()


def resumen_estadisticas():
    with _LOCK:
        data = _leer()
    juegos = list(data.get("juegos", {}).values())
    return {
        "lanzamientos": sum(int(j.get("lanzamientos", 0)) for j in juegos),
        "segundos": sum(float(j.get("segundos", 0)) for j in juegos),
        "juegos": len(juegos),
        "top": sorted(juegos, key=lambda j: float(j.get("segundos", 0)), reverse=True)[:5],
    }
