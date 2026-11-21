"""
Mi Consola - Lanzador de juegos y emuladores
"""

import os
import re
import sys
import subprocess
import webbrowser

from config import BASE, CFG, EMU_DEFECTO
from library import _es_rom_valida


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
    cmd = cfg.get(sis) or cfg.get("Retro")
    if not cmd:
        return f"No hay emulador configurado para {sis}. Edita {CFG}"

    exe_path = cmd[0]
    if not os.path.exists(exe_path):
        retro = cfg.get("Retro", EMU_DEFECTO.get("Retro", [""]))[0]
        if os.path.exists(retro) and sis != "PS4":
            cmd = [retro]
            exe_path = retro
        else:
            return f"Falta el emulador de {sis}:\n{exe_path}\n\nInstalalo en esa ruta o edita {CFG}"

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
