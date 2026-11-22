"""
Mi Consola - Lanzador de juegos y emuladores
"""

import os
import re
import sys
import subprocess
import webbrowser

from config import BASE, CFG, EMU_DEFECTO, EMU_ALTERNATIVAS
from library import _es_rom_valida


def _resolver_exe(sis: str, cfg: dict | None = None) -> str | None:
    """Devuelve la ruta real del .exe del emulador si existe, o None.
    Orden: cfg del usuario -> EMU_DEFECTO -> EMU_ALTERNATIVAS.
    No lanza excepciones (falla con gracia).
    """
    try:
        cfg = cfg or {}
        cmd = cfg.get(sis) or EMU_DEFECTO.get(sis)
        if cmd:
            p = cmd[0]
            if p and os.path.exists(p):
                return p
        for p in EMU_ALTERNATIVAS.get(sis, []):
            if p and os.path.exists(p):
                return p
        # Ultimo recurso: primer .exe en la carpeta del defecto (si existe)
        if cmd and cmd[0]:
            carpeta = os.path.dirname(cmd[0])
            if carpeta and os.path.isdir(carpeta):
                for nombre in os.listdir(carpeta):
                    if nombre.lower().endswith(".exe"):
                        full = os.path.join(carpeta, nombre)
                        if os.path.isfile(full):
                            return full
    except Exception:
        return None
    return None


def jugar(sis: str, ruta: str, cfg: dict) -> str:
    """
    Lanza el juego/emulador.
    Devuelve string vacio si todo ok, o mensaje de error.
    """
    # Steam protocol
    if ruta.startswith("steam://"):
        try:
            if sys.platform == "win32":
                os.startfile(ruta)
            else:
                webbrowser.open(ruta)
        except Exception:
            webbrowser.open(ruta)
        return ""

    # Juegos nativos PC / Epic / Steam / Xbox
    if sis in ("PC", "Epic", "Steam", "Xbox"):
        exe = ruta
        if os.path.isdir(ruta):
            nombre_carpeta = os.path.basename(ruta).lower().replace(" ", "").replace("-", "").replace("_", "")
            candidatos = []
            for r, _, fs in os.walk(ruta):
                depth = r[len(ruta):].count(os.sep)
                if depth > 3:
                    continue
                for f in fs:
                    fl = f.lower()
                    if not fl.endswith(".exe"):
                        continue
                    if re.search(r"(?i)unins|crash|redist|vc_?|setup|install|repair|helper|updater|bootstrap|notification|dxsetup|vcredist|oalinst|physx|dotnet", fl):
                        continue
                    p = os.path.join(r, f)
                    try:
                        tam = os.path.getsize(p)
                    except Exception:
                        continue
                    score = tam
                    base_name = fl[:-4].replace(" ", "").replace("-", "").replace("_", "")
                    if nombre_carpeta and (nombre_carpeta in base_name or base_name in nombre_carpeta):
                        score += 50_000_000
                    if depth <= 1:
                        score += 5_000_000
                    candidatos.append((score, p))
            if not candidatos:
                return "No encontre el .exe del juego."
            candidatos.sort(reverse=True)
            exe = candidatos[0][1]
        try:
            cwd = os.path.dirname(exe) or None
            subprocess.Popen([exe], cwd=cwd)
        except Exception as e:
            return f"Error al lanzar: {e}"
        return ""

    # Emuladores
    cmd = list(cfg.get(sis) or EMU_DEFECTO.get(sis) or cfg.get("Retro") or [])
    if not cmd:
        return f"No hay emulador configurado para {sis}. Edita {CFG}"

    exe_path = _resolver_exe(sis, cfg)
    if not exe_path:
        esperado = cmd[0]
        return f"Falta el emulador de {sis}:\n{esperado}\n\nInstalalo en esa ruta, usa Tienda (T) o edita {CFG}"

    # Reconstruir cmd con el exe encontrado
    cmd = [exe_path] + list(cmd[1:]) if cmd else [exe_path, "{rom}"]

    rom = ruta
    if os.path.isdir(ruta):
        eboot = os.path.join(ruta, "eboot.bin")
        if os.path.exists(eboot):
            rom = eboot
        else:
            mejores = []
            for r, _, fs in os.walk(ruta):
                for f in fs:
                    if _es_rom_valida(f, sis):
                        p = os.path.join(r, f)
                        try:
                            mejores.append((p, os.path.getsize(p)))
                        except Exception:
                            pass
            if mejores:
                rom = max(mejores, key=lambda x: x[1])[0]

    args = [a.replace("{rom}", rom) for a in cmd]
    if len(cmd) == 1 and sis not in ("Retro",):
        args.append(rom)

    try:
        cwd = os.path.dirname(exe_path) or None
        subprocess.Popen(args, cwd=cwd)
    except Exception as e:
        return f"Error al lanzar {sis}: {e}"
    return ""
