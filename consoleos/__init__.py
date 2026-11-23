"""
Mi Consola OS
=============
Capa de sistema que se monta encima del launcher para que se comporte como
una consola real (modo kiosk) en lugar de un programa de Windows.

Capas (se implementan de a una):
    1. shell/    Shell / Kiosk Mode          <- esta version
    2. system/   System Manager              (pendiente)
    3. network/  Network Layer               (pendiente)
    4. storage/  Storage & Performance       (pendiente)
    5. experience/ Experiencia de consola    (pendiente)
"""
from .modes import Mode

__version__ = "0.1.0"
__all__ = ["Mode", "__version__"]
