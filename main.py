"""
Mi Consola v5 - Punto de entrada modular
Lanzador a pantalla completa + centro de descargas.
"""
import os
import sys
import time
import threading
import webbrowser

import pygame

from config import (
    NOMBRE, VERSION, BASE, JUEGOS, DESTINOS, EMU_DEFECTO,
    FONDO, PANEL, PANEL2, TEXTO, SUAVE, AZUL, VERDE, ROJO, DORADO, CIAN,
)
from library import (
    cargar_cfg, escanear, detectar_pc,
    cargar_favoritos, guardar_favoritos, clave_juego,
)
from launcher import jugar
from covers import cache_portadas, buscar_portada_local, pedir_portada
from downloads import cola, agregar_enlaces, leer_portapapeles, soporte_7z
from store import TIENDA, pedir
from system_status import lista_estado_emuladores
from controls import (
    ACCIONES, TECLAS_DEFECTO, JOY_DEFECTO,
    cargar_controles, guardar_controles,
    nombre_tecla, key_to_name,
)
from ui.stars import Estrellas
from ui.cards import dibujar_tarjeta


def mb(b):
    if b < 1 << 20:
        return f"{b / 1024:.0f} KB"
    if b < 1 << 30:
        return f"{b / 1048576:.0f} MB"
    return f"{b / (1 << 30):.1f} GB"


def tamano_ruta(ruta):
    try:
        if os.path.isfile(ruta):
            return os.path.getsize(ruta)
        if os.path.isdir(ruta):
            total = 0
            for r, _, fs in os.walk(ruta):
                for f in fs:
                    try:
                        total += os.path.getsize(os.path.join(r, f))
                    except Exception:
                        pass
            return total
    except Exception:
        pass
    return 0


def main():
    pygame.init()
    pygame.joystick.init()
    pygame.event.pump()

    joysticks = {}
    def init_joysticks():
        joysticks.clear()
        for i in range(pygame.joystick.get_count()):
            try:
                j = pygame.joystick.Joystick(i)
                j.init()
                joysticks[j.get_instance_id()] = j
            except Exception:
                pass
    init_joysticks()

    pantalla = pygame.display.set_mode((1280, 720), pygame.SCALED | pygame.FULLSCREEN)
    pygame.display.set_caption(NOMBRE)
    pygame.mouse.set_visible(False)

    f_tit = pygame.font.SysFont("segoeui", 38, bold=True)
    f_med = pygame.font.SysFont("segoeui", 22)
    f_peq = pygame.font.SysFont("segoeui", 17)
    f_mini = pygame.font.SysFont("segoeui", 14)

    cfg = cargar_cfg()
    map_teclas, map_joy = cargar_controles()
    favoritos = cargar_favoritos()
    reloj = pygame.time.Clock()

    vista, sel, sel_d, dest_i, aviso = "inicio", 0, 0, 0, ""
    sel_t = sel_c = sel_s = 0
    estado_emu = []
    esperando = None
    COLS = 5
    estrellas = Estrellas(1280, 720, 140)
    t_aviso = 0
    last_axis = {"x": 0, "y": 0, "t": 0}
    juegos, t_scan = [], 0
    modo_busqueda = False
    texto_busqueda = ""
    orden = "nombre"
    juegos_filtrados = []
    portadas_cache = {}
    t_portadas = 0

    def txt(s, f, c, x, y, centro=False):
        im = f.render(str(s), True, c)
        pantalla.blit(im, im.get_rect(center=(x, y)) if centro else (x, y))
        return im.get_width()

    def set_aviso(msg, dur=4.0):
        nonlocal aviso, t_aviso
        aviso = msg
        t_aviso = time.time() + dur

    def resolver_tecla(key_const):
        nombre = key_to_name(key_const)
        for acc, keys in map_teclas.items():
            if nombre in keys:
                return acc
        return None

    def resolver_joy(button):
        for acc, buttons in map_joy.items():
            if button in buttons:
                return acc
        return None

    def filtrar_y_ordenar():
        nonlocal juegos_filtrados, sel
        lista = list(juegos)
        if texto_busqueda.strip():
            q = texto_busqueda.lower().strip()
            lista = [j for j in lista if q in j[1].lower() or q in j[0].lower()]
        if orden == "nombre":
            lista.sort(key=lambda x: x[1].lower())
        elif orden == "sistema":
            lista.sort(key=lambda x: (x[0].lower(), x[1].lower()))
        elif orden == "favoritos":
            lista.sort(key=lambda x: (0 if clave_juego(x[0], x[1]) in favoritos else 1, x[1].lower()))
        juegos_filtrados = lista
        if sel >= len(juegos_filtrados):
            sel = max(0, len(juegos_filtrados) - 1)

    while True:
        dt = reloj.tick(30) / 1000.0
        ahora = time.time()
        if ahora - t_scan > 2.5:
            juegos = escanear()
            t_scan = ahora
            t_portadas = ahora
            filtrar_y_ordenar()

        for e in pygame.event.get():
            tecla = None
            if e.type == pygame.QUIT:
                return
            if e.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                init_joysticks()

            if modo_busqueda:
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        modo_busqueda = False
                        texto_busqueda = ""
                        filtrar_y_ordenar()
                        set_aviso("Busqueda cancelada")
                    elif e.key == pygame.K_RETURN:
                        modo_busqueda = False
                        filtrar_y_ordenar()
                        set_aviso(f"Filtro: <<{texto_busqueda}>>" if texto_busqueda else "Filtro quitado")
                    elif e.key == pygame.K_BACKSPACE:
                        texto_busqueda = texto_busqueda[:-1]
                        filtrar_y_ordenar()
                    else:
                        ch = e.unicode
                        if ch and ch.isprintable() and len(texto_busqueda) < 40:
                            texto_busqueda += ch
                            filtrar_y_ordenar()
                continue

            if esperando:
                tipo, accion = esperando
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        esperando = None
                        set_aviso("Cancelado")
                        continue
                    nombre = key_to_name(e.key)
                    for a in map_teclas:
                        if nombre in map_teclas[a]:
                            map_teclas[a].remove(nombre)
                    map_teclas[accion] = [nombre]
                    guardar_controles(map_teclas, map_joy)
                    esperando = None
                    set_aviso(f"Reasignado -> {nombre_tecla(nombre)}")
                    continue
                if e.type == pygame.JOYBUTTONDOWN and tipo == "joy":
                    btn = e.button
                    for a in map_joy:
                        if btn in map_joy[a]:
                            map_joy[a].remove(btn)
                    map_joy[accion] = [btn]
                    guardar_controles(map_teclas, map_joy)
                    esperando = None
                    set_aviso(f"Reasignado -> Boton {btn}")
                    continue
                continue

            if e.type == pygame.KEYDOWN:
                tecla = resolver_tecla(e.key)
            elif e.type == pygame.JOYHATMOTION:
                tecla = {(-1, 0): "i", (1, 0): "d", (0, 1): "a", (0, -1): "b"}.get(e.value)
            elif e.type == pygame.JOYBUTTONDOWN:
                tecla = resolver_joy(e.button)
            elif e.type == pygame.JOYAXISMOTION:
                if ahora - last_axis["t"] > 0.22:
                    if e.axis == 0:
                        if e.value < -0.55:
                            tecla = "i"
                            last_axis = {"x": e.value, "y": 0, "t": ahora}
                        elif e.value > 0.55:
                            tecla = "d"
                            last_axis = {"x": e.value, "y": 0, "t": ahora}
                    elif e.axis == 1:
                        if e.value < -0.55:
                            tecla = "a"
                            last_axis = {"x": 0, "y": e.value, "t": ahora}
                        elif e.value > 0.55:
                            tecla = "b"
                            last_axis = {"x": 0, "y": e.value, "t": ahora}

            if not tecla:
                continue
            if aviso and ahora > t_aviso:
                aviso = ""

            if tecla == "controles":
                vista = "controles"
                sel_c = 0
                continue
            if tecla == "sistema":
                vista = "sistema"
                sel_s = 0
                try:
                    estado_emu = lista_estado_emuladores(cfg)
                except Exception:
                    estado_emu = []
                    set_aviso("No se pudo leer el estado de emuladores")
                continue
            if tecla == "desc":
                vista = "descargas" if vista == "inicio" else "inicio"
            elif tecla == "tienda":
                vista = "tienda"
                sel_t = 0
            elif tecla == "rescan":
                detectar_pc(forzar=True)
                portadas_cache.clear()
                set_aviso("Re-escaneando discos...")
            elif tecla == "spotify":
                try:
                    if sys.platform == "win32":
                        os.startfile("spotify:")
                    else:
                        webbrowser.open("https://open.spotify.com")
                except Exception:
                    webbrowser.open("https://open.spotify.com")
                set_aviso("Abriendo Spotify...")
            elif tecla == "buscar" and vista == "inicio":
                modo_busqueda = True
                set_aviso("Escribi para filtrar... Enter aceptar  Esc cancelar")
            elif tecla == "ordenar" and vista == "inicio":
                ordenes = ["nombre", "sistema", "favoritos"]
                idx = ordenes.index(orden) if orden in ordenes else 0
                orden = ordenes[(idx + 1) % len(ordenes)]
                filtrar_y_ordenar()
                set_aviso(f"Orden: {orden}")
            elif tecla == "favorito" and vista == "inicio" and juegos_filtrados:
                j = juegos_filtrados[sel]
                k = clave_juego(j[0], j[1])
                if k in favoritos:
                    favoritos.discard(k)
                    set_aviso(f"Quitado de favoritos: {j[1]}")
                else:
                    favoritos.add(k)
                    set_aviso(f"* Favorito: {j[1]}")
                guardar_favoritos(favoritos)
                filtrar_y_ordenar()
            elif tecla == "atras":
                if vista in ("descargas", "tienda", "controles", "sistema"):
                    vista = "inicio"
                    esperando = None
                else:
                    return
            elif vista == "inicio" and juegos_filtrados:
                if tecla == "i":
                    sel = max(0, sel - 1)
                if tecla == "d":
                    sel = min(len(juegos_filtrados) - 1, sel + 1)
                if tecla == "a":
                    sel = max(0, sel - COLS)
                if tecla == "b":
                    sel = min(len(juegos_filtrados) - 1, sel + COLS)
                if tecla == "ok":
                    j = juegos_filtrados[sel]
                    msg = jugar(j[0], j[2], cfg)
                    if msg:
                        set_aviso(msg)
            elif vista == "tienda":
                if tecla == "a":
                    sel_t = max(0, sel_t - 1)
                if tecla == "b":
                    sel_t = min(len(TIENDA) - 1, sel_t + 1)
                if tecla == "ok":
                    j = TIENDA[sel_t]
                    threading.Thread(target=pedir, args=(j,), daemon=True).start()
                    set_aviso(f"Procesando <<{j['n']}>>...")
            elif vista == "sistema":
                if tecla == "a":
                    sel_s = max(0, sel_s - 1)
                if tecla == "b":
                    sel_s = min(max(0, len(estado_emu) - 1), sel_s + 1)
                if tecla == "ok" and estado_emu:
                    fila = estado_emu[sel_s]
                    if fila.get("instalado"):
                        set_aviso(f"Ya instalado: {fila['ruta'][:70]}")
                    else:
                        item = fila.get("item")
                        if item:
                            threading.Thread(target=pedir, args=(item,), daemon=True).start()
                            set_aviso(f"Instalando <<{fila['nombre']}>> (ver Tab descargas)...")
                        else:
                            set_aviso("No hay entrada de tienda para este emulador")
                if tecla == "rescan":
                    try:
                        estado_emu = lista_estado_emuladores(cfg)
                        set_aviso("Estado actualizado")
                    except Exception:
                        set_aviso("Error al actualizar estado")
            elif vista == "descargas":
                if tecla == "a":
                    sel_d = max(0, sel_d - 1)
                if tecla == "b":
                    sel_d = min(max(0, len(cola) - 1), sel_d + 1)
                if tecla == "dest":
                    dest_i = (dest_i + 1) % len(DESTINOS)
                if tecla == "pegar":
                    ok = agregar_enlaces(leer_portapapeles(), DESTINOS[dest_i])
                    set_aviso("Descarga agregada." if ok else "Copia un enlace http primero.")
                if cola and tecla == "pausa":
                    it = cola[sel_d]
                    if it["estado"] == "bajando":
                        it["estado"] = "pausado"
                    elif it["estado"] in ("pausado", "error"):
                        it["estado"] = "en cola"
                if cola and tecla == "quitar":
                    if cola[sel_d]["estado"] != "bajando":
                        cola.pop(sel_d)
                        sel_d = max(0, sel_d - 1)
            elif vista == "controles":
                n_acc = len(ACCIONES)
                if tecla == "a":
                    sel_c = max(0, sel_c - 1)
                if tecla == "b":
                    sel_c = min(n_acc * 2 + 1, sel_c + 1)
                if tecla == "ok":
                    if sel_c < n_acc:
                        accion = ACCIONES[sel_c][0]
                        esperando = ("teclado", accion)
                        set_aviso(f"Pulsa una TECLA para <<{ACCIONES[sel_c][1]}>>")
                    elif sel_c < n_acc * 2:
                        idx = sel_c - n_acc
                        accion = ACCIONES[idx][0]
                        esperando = ("joy", accion)
                        set_aviso(f"Pulsa un BOTON para <<{ACCIONES[idx][1]}>>")
                    else:
                        map_teclas = {k: list(v) for k, v in TECLAS_DEFECTO.items()}
                        map_joy = {k: list(v) for k, v in JOY_DEFECTO.items()}
                        guardar_controles(map_teclas, map_joy)
                        set_aviso("Controles restaurados")

        # ---- dibujo ----
        pantalla.fill(FONDO)
        estrellas.update(dt)
        estrellas.draw(pantalla)

        for i in range(110):
            t = i / 110
            col = (
                min(255, int(FONDO[0] + 18 * (1 - t))),
                min(255, int(FONDO[1] + 28 * (1 - t))),
                min(255, int(FONDO[2] + 55 * (1 - t))),
            )
            pygame.draw.line(pantalla, col, (0, i), (1280, i))

        pygame.draw.line(pantalla, (40, 90, 160), (40, 72), (1240, 72), 1)
        pygame.draw.line(pantalla, (255, 190, 60), (40, 73), (280, 73), 2)

        sombra = f_tit.render(NOMBRE, True, (0, 10, 30))
        pantalla.blit(sombra, (57, 20))
        txt(NOMBRE, f_tit, TEXTO, 55, 18)
        txt(time.strftime("%H:%M"), f_med, SUAVE, 1165, 22)

        if joysticks:
            txt(f"Gamepad x{len(joysticks)}", f_mini, VERDE, 1040, 28)
        else:
            txt("Sin gamepad", f_mini, SUAVE, 1040, 28)
        txt("Spotify", f_mini, (30, 215, 96), 920, 28)

        activas = [i for i in cola if i["estado"] in ("bajando", "en cola")]
        if activas and vista == "inicio":
            txt(f"v {len(activas)} descarga(s)  .  Tab", f_peq, VERDE, 55, 62)

        pie = ""
        if vista == "inicio":
            n_total = len(juegos)
            n_filtro = len(juegos_filtrados)
            info_barra = f"{n_filtro}/{n_total} juegos"
            if texto_busqueda:
                info_barra += f"  .  <<{texto_busqueda}>>"
            info_barra += f"  .  orden: {orden}"
            txt(info_barra, f_peq, SUAVE, 55, 88)

            if not juegos_filtrados:
                if not juegos:
                    txt("Todavia no hay juegos detectados", f_tit, TEXTO, 640, 280, True)
                    txt(f"ROMs ->  {JUEGOS}\\NES  \\SNES  \\N64  \\PS1  etc.", f_med, SUAVE, 640, 340, True)
                    txt("PC -> apreta R para escanear   .   Tab = descargas   .   T = tienda", f_peq, SUAVE, 640, 390, True)
                else:
                    txt("Ningun juego coincide con el filtro", f_tit, TEXTO, 640, 300, True)
            else:
                fila_sel = sel // COLS
                for n, (sis, nom, ruta, appid) in enumerate(juegos_filtrados):
                    fila, col = n // COLS, n % COLS
                    y = 120 + (fila - max(0, fila_sel - 1)) * 280
                    if y < 100 or y > 680:
                        continue
                    x = 40 + col * 245
                    es_fav = clave_juego(sis, nom) in favoritos
                    dibujar_tarjeta(
                        pantalla, x, y, 220, 250, sis, nom, ruta, appid,
                        n == sel, es_fav, portadas_cache, f_peq, f_mini, ahora, t_portadas
                    )

                if juegos_filtrados:
                    j = juegos_filtrados[sel]
                    sis, nom, ruta, appid = j
                    panel = pygame.Rect(980, 520, 270, 150)
                    pygame.draw.rect(pantalla, PANEL, panel, border_radius=10)
                    pygame.draw.rect(pantalla, AZUL, panel, 1, border_radius=10)
                    txt(nom[:28], f_peq, TEXTO, 995, 530)
                    txt(f"Sistema: {sis}", f_mini, CIAN, 995, 555)
                    if appid:
                        txt(f"Steam AppID: {appid}", f_mini, SUAVE, 995, 575)
                    else:
                        try:
                            tam = tamano_ruta(ruta) if not str(ruta).startswith("steam://") else 0
                            if tam:
                                txt(f"Tamano: {mb(tam)}", f_mini, SUAVE, 995, 575)
                        except Exception:
                            pass
                    es_fav = clave_juego(sis, nom) in favoritos
                    txt("* Favorito" if es_fav else "F = marcar favorito", f_mini, DORADO if es_fav else SUAVE, 995, 600)

            pie = "Enter jugar  F fav  / buscar  O orden  T tienda  E sistema  Tab descargas  M Spotify  C controles  R re-escanear  Esc"
            if modo_busqueda:
                pygame.draw.rect(pantalla, (30, 20, 50), (40, 650, 1200, 40), border_radius=8)
                txt(f"Buscar: {texto_busqueda}_", f_med, DORADO, 55, 658)

        elif vista == "tienda":
            txt("Tienda  .  juegos gratis y legales", f_med, TEXTO, 55, 85)
            txt(f"{len(TIENDA)} titulos  .  open-source / free-to-play / paginas oficiales", f_peq, SUAVE, 55, 115)
            top = max(0, sel_t - 4)
            for n, j in enumerate(TIENDA):
                if n < top or n > top + 5:
                    continue
                y = 150 + (n - top) * 85
                r = pygame.Rect(50, y, 1180, 76)
                pygame.draw.rect(pantalla, PANEL if n != sel_t else PANEL2, r, border_radius=12)
                if n == sel_t:
                    pygame.draw.rect(pantalla, AZUL, r, 3, border_radius=12)
                txt(j["n"], f_med, TEXTO, 70, y + 10)
                txt(j["d"][:90], f_peq, SUAVE, 70, y + 42)
                if j.get("pago"):
                    etiqueta, color_e = "Comprar", DORADO
                elif j.get("dl") or j.get("repo"):
                    etiqueta, color_e = "Descargar", VERDE
                else:
                    etiqueta, color_e = "Pagina oficial", CIAN
                txt(etiqueta, f_peq, color_e, 1020, y + 28)
            pie = "Enter bajar/abrir   flechas mover   Tab descargas   Esc volver"

        elif vista == "sistema":
            txt("Estado del sistema  .  emuladores", f_med, TEXTO, 55, 85)
            try:
                ok7, src7 = soporte_7z()
            except Exception:
                ok7, src7 = False, None
            if ok7:
                txt(f"Soporte .7z: SI ({src7})  .  VERSION {VERSION}", f_peq, VERDE, 55, 115)
            else:
                txt(f"Soporte .7z: NO (pip install py7zr o 7z.exe)  .  VERSION {VERSION}", f_peq, ROJO, 55, 115)
            if not estado_emu:
                txt("Sin emuladores en el catalogo de tienda", f_med, SUAVE, 640, 320, True)
            else:
                top = max(0, sel_s - 5)
                for n, fila in enumerate(estado_emu):
                    if n < top or n > top + 7:
                        continue
                    y = 145 + (n - top) * 62
                    r = pygame.Rect(50, y, 1180, 56)
                    pygame.draw.rect(pantalla, PANEL if n != sel_s else PANEL2, r, border_radius=10)
                    if n == sel_s:
                        pygame.draw.rect(pantalla, AZUL, r, 2, border_radius=10)
                    estado_txt = "INSTALADO" if fila["instalado"] else "FALTA"
                    color_e = VERDE if fila["instalado"] else ROJO
                    txt(fila["nombre"][:36], f_peq, TEXTO, 70, y + 8)
                    txt(f"Sistema: {fila['sistema']}", f_mini, CIAN, 70, y + 30)
                    txt(estado_txt, f_peq, color_e, 520, y + 16)
                    ruta_show = (fila["ruta"] or fila.get("esperado") or "")[:55]
                    txt(ruta_show, f_mini, SUAVE, 680, y + 18)
            pie = "Enter instalar si falta   flechas mover   R actualizar   Esc volver"

        elif vista == "controles":
            txt("Configuracion de controles", f_med, TEXTO, 55, 80)
            if esperando:
                txt("Esperando entrada... Esc cancelar", f_peq, DORADO, 55, 110)
            n_acc = len(ACCIONES)
            top = max(0, min(sel_c, n_acc * 2 + 1) - 6)
            for n in range(n_acc * 2 + 2):
                if n < top or n > top + 8:
                    continue
                y = 140 + (n - top) * 50
                r = pygame.Rect(50, y, 1180, 44)
                pygame.draw.rect(pantalla, PANEL if n != sel_c else PANEL2, r, border_radius=8)
                if n == sel_c:
                    pygame.draw.rect(pantalla, AZUL, r, 2, border_radius=8)
                if n < n_acc:
                    acc, label = ACCIONES[n]
                    keys = map_teclas.get(acc, [])
                    txt(f"Teclado  {label}", f_peq, TEXTO, 70, y + 10)
                    txt(", ".join(nombre_tecla(k) for k in keys) or "-", f_peq, SUAVE, 500, y + 10)
                elif n < n_acc * 2:
                    idx = n - n_acc
                    acc, label = ACCIONES[idx]
                    btns = map_joy.get(acc, [])
                    txt(f"Gamepad  {label}", f_peq, TEXTO, 70, y + 10)
                    txt(", ".join(f"B{b}" for b in btns) or "-", f_peq, SUAVE, 500, y + 10)
                else:
                    txt("Restaurar controles por defecto", f_peq, DORADO, 70, y + 10)
            pie = "flechas mover   Enter reasignar   Esc volver"

        elif vista == "descargas":
            txt("Centro de descargas", f_med, TEXTO, 55, 85)
            txt(f"Destino: {DESTINOS[dest_i]}  (S para cambiar)", f_peq, SUAVE, 55, 115)
            if not cola:
                txt("Cola vacia. Copia un enlace y apreta V, o usa la Tienda (T).", f_med, SUAVE, 640, 300, True)
            else:
                top = max(0, sel_d - 4)
                for n, it in enumerate(cola):
                    if n < top or n > top + 6:
                        continue
                    y = 150 + (n - top) * 70
                    r = pygame.Rect(50, y, 1180, 62)
                    pygame.draw.rect(pantalla, PANEL if n != sel_d else PANEL2, r, border_radius=10)
                    if n == sel_d:
                        pygame.draw.rect(pantalla, AZUL, r, 2, border_radius=10)
                    txt(it["nombre"][:40], f_peq, TEXTO, 70, y + 8)
                    st = it["estado"]
                    col_st = {"listo": VERDE, "error": ROJO, "bajando": CIAN, "pausado": DORADO}.get(st, SUAVE)
                    txt(st, f_peq, col_st, 700, y + 8)
                    if it.get("total"):
                        pct = min(100, int(100 * it["hecho"] / max(1, it["total"])))
                        txt(f"{pct}%  {mb(it['hecho'])}/{mb(it['total'])}", f_mini, SUAVE, 70, y + 34)
                    if it.get("error"):
                        txt(str(it["error"])[:60], f_mini, ROJO, 400, y + 34)
            pie = "V pegar   S destino   P pausar   Supr quitar   Tab volver"

        if aviso and ahora <= t_aviso:
            pygame.draw.rect(pantalla, (40, 20, 60), (40, 670, 1200, 36), border_radius=8)
            txt(aviso[:90], f_peq, DORADO, 55, 678)
        elif pie:
            txt(pie, f_mini, SUAVE, 55, 685)

        pygame.display.flip()


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--web":
        try:
            import webview
            webview.create_window("Mi Consola", sys.argv[2])
            webview.start()
        except ImportError:
            webbrowser.open(sys.argv[2])
    else:
        main()
