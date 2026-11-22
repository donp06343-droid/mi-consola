"""
Mi Consola - Controles (teclado + joystick)
"""
import os
import json
import pygame

from config import BASE

CONTROLES_CFG = os.path.join(BASE, "consola_controles.json")

ACCIONES = [
    ("ok",       "Confirmar / Jugar"),
    ("atras",    "Volver / Salir"),
    ("a",        "Arriba"),
    ("b",        "Abajo"),
    ("i",        "Izquierda"),
    ("d",        "Derecha"),
    ("desc",     "Descargas"),
    ("tienda",   "Tienda"),
    ("pegar",    "Pegar enlaces"),
    ("dest",     "Cambiar destino"),
    ("pausa",    "Pausar descarga"),
    ("quitar",   "Quitar de cola"),
    ("rescan",   "Re-escanear PC"),
    ("controles","Menu Controles"),
    ("favorito", "Marcar favorito"),
    ("buscar",   "Buscar"),
    ("ordenar",  "Cambiar orden"),
    ("spotify",  "Abrir Spotify"),
    ("shadps4",  "Abrir GUI shadPS4 (PKG)"),
    ("sistema",  "Estado del sistema"),
]

TECLAS_DEFECTO = {
    "ok": ["return", "space"],
    "atras": ["escape", "backspace"],
    "a": ["up", "w"],
    "b": ["down", "s"],
    "i": ["left", "a"],
    "d": ["right", "d"],
    "desc": ["tab"],
    "tienda": ["t"],
    "pegar": ["v"],
    "dest": ["s"],
    "pausa": ["p"],
    "quitar": ["delete"],
    "rescan": ["r"],
    "controles": ["c"],
    "favorito": ["f"],
    "buscar": ["slash", "f3"],
    "ordenar": ["o"],
    "spotify": ["m"],
    "shadps4": ["g"],
    "sistema": ["e"],
}

JOY_DEFECTO = {
    "ok": [0],
    "atras": [1, 6],
    "pausa": [2],
    "desc": [3],
    "tienda": [7],
    "favorito": [4],
}

NOMBRE_TECLA = {
    "return": "Enter", "space": "Espacio", "escape": "Esc", "backspace": "Retroceso",
    "up": "\u2191", "down": "\u2193", "left": "\u2190", "right": "\u2192",
    "tab": "Tab", "delete": "Supr", "insert": "Ins", "home": "Inicio", "end": "Fin",
    "pageup": "AvPag", "pagedown": "RePag", "slash": "/", "f3": "F3",
    "lctrl": "Ctrl Izq", "rctrl": "Ctrl Der", "lshift": "Shift Izq", "rshift": "Shift Der",
    "lalt": "Alt Izq", "ralt": "Alt Der",
}
for i in range(1, 13):
    NOMBRE_TECLA[f"f{i}"] = f"F{i}"


def nombre_tecla(k):
    return NOMBRE_TECLA.get(k, k.upper() if len(k) == 1 else k)


def key_to_name(key):
    for name in dir(pygame):
        if name.startswith("K_") and getattr(pygame, name) == key:
            return name[2:].lower()
    return str(key)


def cargar_controles():
    if os.path.exists(CONTROLES_CFG):
        try:
            with open(CONTROLES_CFG, encoding="utf-8") as f:
                data = json.load(f)
            teclas = data.get("teclas", TECLAS_DEFECTO)
            joy = data.get("joy", JOY_DEFECTO)
            for acc, _ in ACCIONES:
                teclas.setdefault(acc, TECLAS_DEFECTO.get(acc, []))
                joy.setdefault(acc, JOY_DEFECTO.get(acc, []))
            return teclas, joy
        except Exception:
            pass
    return {k: list(v) for k, v in TECLAS_DEFECTO.items()}, {k: list(v) for k, v in JOY_DEFECTO.items()}


def guardar_controles(teclas, joy):
    try:
        os.makedirs(BASE, exist_ok=True)
        with open(CONTROLES_CFG, "w", encoding="utf-8") as f:
            json.dump({"teclas": teclas, "joy": joy}, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("No se pudo guardar controles:", e)
