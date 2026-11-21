"""
Tarjetas de juegos con portadas mejoradas
"""
import zlib
import pygame
from config import TEXTO, SUAVE, AZUL, VERDE, DORADO, CIAN
from covers import cache_portadas, buscar_portada_local, pedir_portada


def color_por_nombre(nom: str):
    h = zlib.crc32(nom.encode()) % 360
    c = pygame.Color(0)
    c.hsva = (h, 55, 65, 100)
    return c


def dibujar_tarjeta(pantalla, x, y, w, h, sis, nom, ruta, appid,
                    seleccionado, es_fav, portadas_cache, f_peq, f_mini, ahora, t_portadas):
    r = pygame.Rect(x, y, w, h)
    if seleccionado:
        r.inflate_ip(12, 12)
        r.move_ip(0, -4)
        pygame.draw.rect(pantalla, (80, 140, 220), r.inflate(8, 8), border_radius=16)

    col = color_por_nombre(nom)
    pygame.draw.rect(pantalla, col, r, border_radius=12)

    clave = (sis, nom)
    path = portadas_cache.get(clave)
    if path is None and clave not in portadas_cache:
        path = buscar_portada_local(sis, nom, ruta, appid)
        portadas_cache[clave] = path
        if not path:
            pedir_portada(sis, nom, appid)
    elif path is None:
        if ahora - t_portadas > 2.5:
            nuevo = buscar_portada_local(sis, nom, ruta, appid)
            if nuevo:
                portadas_cache[clave] = nuevo
                path = nuevo

    img_w, img_h = w - 8, h - 50
    img = cache_portadas.get(path, img_w, img_h) if path else None

    if img:
        img_rect = img.get_rect(center=(r.centerx, r.centery - 12))
        pantalla.blit(img, img_rect)
        s = pygame.Surface((w - 4, 48), pygame.SRCALPHA)
        s.fill((0, 0, 0, 160))
        pantalla.blit(s, (r.x + 2, r.bottom - 50))
    else:
        ph = cache_portadas.placeholder(sis, nom, img_w, img_h)
        ph_rect = ph.get_rect(center=(r.centerx, r.centery - 12))
        pantalla.blit(ph, ph_rect)

    if seleccionado:
        pygame.draw.rect(pantalla, TEXTO, r, 3, border_radius=12)

    nombre_mostrar = nom[:18] + ("\u2026" if len(nom) > 18 else "")
    im = f_peq.render(nombre_mostrar, True, TEXTO)
    pantalla.blit(im, im.get_rect(center=(r.centerx, r.bottom - 36)))

    color_sis = VERDE if sis in ("PC", "Steam", "Epic") else AZUL
    im2 = f_mini.render(sis, True, color_sis)
    offset = 12 if es_fav else 0
    pantalla.blit(im2, im2.get_rect(center=(r.centerx - offset, r.bottom - 16)))
    if es_fav:
        im3 = f_mini.render("\u2605", True, DORADO)
        pantalla.blit(im3, im3.get_rect(center=(r.centerx + 28, r.bottom - 16)))
