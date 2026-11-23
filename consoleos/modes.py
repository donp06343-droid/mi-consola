"""
Modos de ejecucion del launcher.

    NORMAL   Ventana de pygame como siempre. No se toca nada de Windows.
    CONSOLE  Modo kiosk: oculta la barra de tareas, bloquea atajos del sistema,
             fuerza pantalla completa y gestiona el foco al abrir juegos.

Si Windows ya arranca sin explorer.exe (shell reemplazado, paso 2 del plan),
el modo CONSOLE funciona igual: los pasos que dependen de la barra de tareas
simplemente no encuentran nada que ocultar.
"""
from __future__ import annotations

from enum import Enum
from typing import Optional, Sequence


class Mode(str, Enum):
    NORMAL = "normal"
    CONSOLE = "console"

    @classmethod
    def parse(cls, value, default: Optional["Mode"] = None) -> Optional["Mode"]:
        if isinstance(value, cls):
            return value
        v = str(value or "").strip().lower()
        if v in ("console", "consola", "kiosk", "soft", "hard"):
            return cls.CONSOLE
        if v in ("normal", "windowed", "desktop"):
            return cls.NORMAL
        return default

    @classmethod
    def from_argv(cls, argv: Sequence[str]) -> Optional["Mode"]:
        """
        Lee el modo pedido por linea de comandos. Devuelve None si no se pidio
        ninguno (entonces manda el valor guardado en consoleos.json).

            --mode console | --mode=console | --console | --kiosk | --mode normal
        """
        args = list(argv)
        for i, a in enumerate(args):
            if a in ("--console", "--kiosk"):
                return cls.CONSOLE
            if a == "--mode" and i + 1 < len(args):
                return cls.parse(args[i + 1])
            if a.startswith("--mode="):
                return cls.parse(a.split("=", 1)[1])
        return None
