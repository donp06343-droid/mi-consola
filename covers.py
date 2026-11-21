"""
Mi Consola - Sistema de Portadas e Iconos (mejorado v5)
Prioridad: Steam cache > Covers/ > junto a ROM > descarga (Steam CDN / Libretro)
"""
import os
import re
import time
import zlib
import threading
import urllib.request
from urllib.parse import quote

import pygame

from config import (
    COVERS, LIBRETRO_SISTEMAS, NOMBRES_PORTADA,
)
from covers_normalize import normalizar_nombre, nombre_archivo_seguro, score_similitud


def buscar_portada_local(sis: str, nom: str, ruta=None, appid=None):
    candidatos = []
    if appid:
        steam_roots = [
            os.path.join(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"), "Steam"),
            os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), "Steam"),
            os.path.join(os.environ.get("MI_CONSOLA_BASE", r"D:\Emulacion"), "Steam"),
        ]
        for root in steam_roots:
            libcache = os.path.join(root, "appcache", "librarycache")
            if not os.path.isdir(libcache):
                continue
            for suf in (
                f"{appid}_library_600x900.jpg",
                f"{appid}_library_600x900_2x.jpg",
                f"{appid}_library_hero.jpg",
                f"{appid}_header.jpg",
                f"{appid}.jpg",
            ):
                p = os.path.join(libcache, suf)
                if os.path.exists(p):
                    return p

    nom_norm = normalizar_nombre(nom)
    for carp in (os.path.join(COVERS, sis), COVERS):
        if not os.path.isdir(carp):
            continue
        try:
            for f in os.listdir(carp):
                fl = f.lower()
                if not fl.endswith((".jpg", ".jpeg", ".png", ".webp", ".bmp")):
                    continue
                base = normalizar_nombre(os.path.splitext(f)[0])
                sc = score_similitud(nom_norm, base)
                if sc >= 0.45:
                    candidatos.append((sc, os.path.join(carp, f)))
        except Exception:
            pass

    if ruta and not str(ruta).startswith("steam://"):
        dir_juego = ruta if os.path.isdir(ruta) else os.path.dirname(ruta)
        if dir_juego and os.path.isdir(dir_juego):
            for n in NOMBRES_PORTADA:
                p = os.path.join(dir_juego, n)
                if os.path.exists(p):
                    return p
            try:
                for f in os.listdir(dir_juego):
                    fl = f.lower()
                    if not fl.endswith((".jpg", ".jpeg", ".png", ".webp", ".bmp")):
                        continue
                    base = normalizar_nombre(os.path.splitext(f)[0])
                    sc = score_similitud(nom_norm, base)
                    if "cover" in fl or "box" in fl or "poster" in fl or "front" in fl:
                        sc = max(sc, 0.7)
                    if sc >= 0.4:
                        candidatos.append((sc, os.path.join(dir_juego, f)))
            except Exception:
                pass
            for sub in ("media", "covers", "images", "art", "boxart"):
                subdir = os.path.join(dir_juego, sub)
                if os.path.isdir(subdir):
                    for n in NOMBRES_PORTADA:
                        p = os.path.join(subdir, n)
                        if os.path.exists(p):
                            return p

    if candidatos:
        candidatos.sort(key=lambda x: (x[0], os.path.getsize(x[1]) if os.path.exists(x[1]) else 0), reverse=True)
        return candidatos[0][1]
    return None


_cola_portadas = []
_portadas_en_proceso = set()
_portadas_fallidas = set()
_lock_portadas = threading.Lock()
_MAX_CONCURRENT = 2


def _url_steam_portada(appid: str):
    base = f"https://steamcdn-a.akamaihd.net/steam/apps/{appid}"
    return [
        f"{base}/library_600x900_2x.jpg",
        f"{base}/library_600x900.jpg",
        f"{base}/library_hero.jpg",
        f"{base}/header.jpg",
    ]


def _url_libretro_portada(sis: str, nom: str):
    carpeta = LIBRETRO_SISTEMAS.get(sis)
    if not carpeta:
        return None
    nombre = re.sub(r"\s*[\(\[].*?[\)\]]", "", nom.strip())
    nombre = re.sub(r"\s+", " ", nombre).strip()
    if not nombre:
        return None
    encoded = quote(nombre + ".png")
    return f"https://thumbnails.libretro.com/{carpeta}/Named_Boxarts/{encoded}"


def _descargar_imagen(url: str, destino: str, timeout: int = 12) -> bool:
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MiConsola/5.0",
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
        })
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read()
            if len(data) < 2000:
                return False
            if not (data[:3] == b"\xff\xd8\xff" or data[:8] == b"\x89PNG\r\n\x1a\n" or data[:4] == b"RIFF"):
                return False
            os.makedirs(os.path.dirname(destino), exist_ok=True)
            tmp = destino + ".part"
            with open(tmp, "wb") as f:
                f.write(data)
            os.replace(tmp, destino)
            return True
    except Exception:
        return False


def _trabajador_portadas():
    while True:
        item = None
        with _lock_portadas:
            if _cola_portadas:
                item = _cola_portadas.pop(0)
        if not item:
            time.sleep(0.5)
            continue
        sis, nom, appid = item["sis"], item["nom"], item.get("appid")
        clave = f"{sis}::{nom}".lower()
        destino_base = os.path.join(COVERS, sis, nombre_archivo_seguro(nom))
        exito = False
        if appid:
            for url in _url_steam_portada(appid):
                for ext in (".jpg", ".png"):
                    if _descargar_imagen(url, destino_base + ext):
                        exito = True
                        break
                if exito:
                    break
        if not exito and sis in LIBRETRO_SISTEMAS:
            url = _url_libretro_portada(sis, nom)
            if url and _descargar_imagen(url, destino_base + ".png"):
                exito = True
        with _lock_portadas:
            if not exito:
                _portadas_fallidas.add(clave)
            _portadas_en_proceso.discard(clave)


def pedir_portada(sis: str, nom: str, appid=None):
    clave = f"{sis}::{nom}".lower()
    with _lock_portadas:
        if clave in _portadas_en_proceso or clave in _portadas_fallidas:
            return
        if buscar_portada_local(sis, nom, None, appid):
            return
        _portadas_en_proceso.add(clave)
        _cola_portadas.append({"sis": sis, "nom": nom, "appid": appid})


for _ in range(_MAX_CONCURRENT):
    threading.Thread(target=_trabajador_portadas, daemon=True).start()


class CachePortadas:
    def __init__(self, max_items: int = 400):
        self.cache = {}
        self.orden = []
        self.max_items = max_items
        self.fallidos = set()
        self.placeholders = {}

    def _clave(self, path, w, h):
        return f"{path}|{w}x{h}"

    def get(self, path, w, h):
        if not path or path in self.fallidos:
            return None
        k = self._clave(path, w, h)
        if k in self.cache:
            if k in self.orden:
                self.orden.remove(k)
            self.orden.append(k)
            return self.cache[k]
        try:
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.smoothscale(img, (w, h))
            self.cache[k] = img
            self.orden.append(k)
            while len(self.orden) > self.max_items:
                viejo = self.orden.pop(0)
                self.cache.pop(viejo, None)
            return img
        except Exception:
            self.fallidos.add(path)
            return None

    def placeholder(self, sis, nom, w, h):
        k = (sis, nom, w, h)
        if k in self.placeholders:
            return self.placeholders[k]
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        hsh = zlib.crc32(nom.encode()) % 360
        c1 = pygame.Color(0)
        c1.hsva = (hsh, 55, 38, 100)
        c2 = pygame.Color(0)
        c2.hsva = ((hsh + 40) % 360, 60, 22, 100)
        for y in range(h):
            t = y / max(1, h - 1)
            r = int(c1.r * (1 - t) + c2.r * t)
            g = int(c1.g * (1 - t) + c2.g * t)
            b = int(c1.b * (1 - t) + c2.b * t)
            pygame.draw.line(surf, (r, g, b), (0, y), (w, y))
        cx, cy = w // 2, h // 2 - 18
        radio = min(w, h) // 4
        s = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, 35), (radio, radio), radio)
        surf.blit(s, (cx - radio, cy - radio))
        try:
            font_big = pygame.font.SysFont("segoeui", max(36, h // 4), bold=True)
            letra = nom[:1].upper() if nom else "?"
            txt = font_big.render(letra, True, (255, 255, 255, 220))
            surf.blit(txt, txt.get_rect(center=(cx, cy)))
        except Exception:
            pass
        try:
            font_s = pygame.font.SysFont("segoeui", max(12, h // 14), bold=True)
            badge = font_s.render(sis.upper(), True, (220, 230, 255))
            br = badge.get_rect(center=(w // 2, h - 22))
            pad = 8
            bg = pygame.Surface((br.width + pad * 2, br.height + 6), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 110))
            surf.blit(bg, (br.x - pad, br.y - 3))
            surf.blit(badge, br)
        except Exception:
            pass
        self.placeholders[k] = surf
        return surf

    def limpiar(self):
        self.cache.clear()
        self.orden.clear()
        self.fallidos.clear()
        self.placeholders.clear()


cache_portadas = CachePortadas(max_items=400)
