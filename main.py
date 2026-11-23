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
    NOMBRE, BASE, JUEGOS, DESTINOS,
    FONDO, PANEL, PANEL2, TEXTO, SUAVE, AZUL, VERDE, ROJO, DORADO, CIAN,
)
from library import (
    cargar_cfg, escanear, detectar_pc,
    cargar_favoritos, guardar_favoritos, clave_juego,
)
from launcher import jugar
from covers import cache_portadas, buscar_portada_local, pedir_portada
from downloads import cola, agregar_enlaces, leer_portapapeles
from store import TIENDA, pedir
from controls import (
    ACCIONES, TECLAS_DEFECTO, JOY_DEFECTO,
    cargar_controles, guardar_controles,
    nombre_tecla, key_to_name,
)
from ui.stars import Estrellas
from ui.cards import dibujar_tarjeta
from system_status import obtener_estado_pc, lista_estado_emuladores
from stats import resumen_estadisticas


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
    pygame.mouse.set_visible(True)

    f_tit = pygame.font.SysFont("segoeui", 38, bold=True)
    f_med = pygame.font.SysFont("segoeui", 22)
    f_peq = pygame.font.SysFont("segoeui", 17)
    f_mini = pygame.font.SysFont("segoeui", 14)

    cfg = cargar_cfg()
    map_teclas, map_joy = cargar_controles()
    favoritos = cargar_favoritos()
    reloj = pygame.time.Clock()

    vista, sel, sel_d, dest_i, aviso = "inicio", 0, 0, 0, ""
    sel_t = sel_c = 0
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
    estado_pc, emus_estado, t_estado = {}, [], 0
    stats_resumen = {"lanzamientos": 0, "segundos": 0, "juegos": 0, "top": []}

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
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = e.pos
                if 34 <= my <= 68:
                    tabs = [
                        (410, 505, "inicio"),
                        (510, 605, "tienda"),
                        (610, 705, "descargas"),
                        (710, 805, "estado"),
                        (810, 905, "controles"),
                    ]
                    for x1, x2, destino in tabs:
                        if x1 <= mx <= x2:
                            vista = destino
                            if destino == "estado":
                                t_estado = 0
                            continue

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

            if tecla == "estado":
                vista = "estado"
                t_estado = 0
                continue
            if tecla == "controles":
                vista = "controles"
                sel_c = 0
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
                if vista in ("descargas", "tienda", "controles", "estado"):
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
                    msg = jugar(j[0], j[2], cfg, j[1])
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
        nav_tabs = [
            (410, 505, "INICIO", "inicio"),
            (510, 605, "TIENDA", "tienda"),
            (610, 705, "DESCARGAS", "descargas"),
            (710, 805, "ESTADO", "estado"),
            (810, 905, "AJUSTES", "controles"),
        ]
        for x1, x2, etiqueta, destino in nav_tabs:
            activo = vista == destino
            nr = pygame.Rect(x1, 36, x2 - x1, 28)
            pygame.draw.rect(pantalla, PANEL2 if activo else PANEL, nr, border_radius=7)
            pygame.draw.rect(pantalla, AZUL if activo else (45, 70, 110), nr, 1, border_radius=7)
            txt(etiqueta, f_mini, TEXTO if activo else SUAVE, nr.centerx, nr.y + 6, True)

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

            pie = "Enter jugar  F favorito  / buscar  O ordenar  T tienda  Tab descargas  E estado PC  C controles  R escanear  Esc salir"
            if modo_busqueda:
                pygame.draw.rect(pantalla, (30, 20, 50), (40, 650, 1200, 40), border_radius=8)
                txt(f"Buscar: {texto_busqueda}_", f_med, DORADO, 55, 658)


        elif vista == "estado":
            if ahora - t_estado > 2.0:
                estado_pc = obtener_estado_pc()
                emus_estado = lista_estado_emuladores(cfg)
                stats_resumen = resumen_estadisticas()
                t_estado = ahora

            txt("Estado del equipo", f_tit, TEXTO, 55, 82)
            txt("Diagnostico local · metricas disponibles en este dispositivo", f_peq, SUAVE, 58, 125)

            def tarjeta_estado(x, y, w, h, titulo, valor, detalle, color):
                rr = pygame.Rect(x, y, w, h)
                pygame.draw.rect(pantalla, PANEL, rr, border_radius=12)
                pygame.draw.rect(pantalla, color, rr, 2, border_radius=12)
                txt(titulo, f_mini, SUAVE, x + 14, y + 12)
                txt(valor, f_tit, color, x + 14, y + 34)
                txt(detalle, f_mini, TEXTO, x + 14, y + h - 25)

            def gb(valor):
                return f"{valor / (1024 ** 3):.1f} GB" if valor else "No disponible"

            cpu = estado_pc.get("cpu_pct")
            ram = estado_pc.get("ram_pct")
            disco = estado_pc.get("disco_pct")
            tarjeta_estado(55, 155, 270, 112, "PROCESADOR", f"{cpu:.0f}%" if cpu is not None else "N/D",
                           f"{estado_pc.get('nucleos', 0)} nucleos · {estado_pc.get('cpu', '')[:24]}",
                           CIAN)
            tarjeta_estado(345, 155, 270, 112, "MEMORIA RAM", f"{ram:.0f}%" if ram is not None else "N/D",
                           f"{gb(estado_pc.get('ram_usada'))} / {gb(estado_pc.get('ram_total'))}", VERDE)
            tarjeta_estado(635, 155, 270, 112, "ALMACENAMIENTO", f"{disco:.0f}%" if disco is not None else "N/D",
                           f"{gb(estado_pc.get('disco_libre'))} libres", DORADO)
            tarjeta_estado(925, 155, 300, 112, "BIBLIOTECA", str(len(juegos)),
                           f"{len(favoritos)} favoritos · {len({j[0] for j in juegos})} sistemas", AZUL)

            txt("INFORMACION DEL SISTEMA", f_peq, DORADO, 60, 292)
            txt(estado_pc.get("sistema", "Sistema no identificado"), f_med, TEXTO, 60, 320)
            txt(f"Equipo: {estado_pc.get('equipo', 'PC')}", f_mini, SUAVE, 60, 350)
            txt(f"GPU: {estado_pc.get('gpu', 'No disponible')}", f_mini, SUAVE, 60, 374)
            txt(f"Temperatura: {estado_pc.get('temperatura', 'No disponible')}", f_mini, SUAVE, 60, 398)

            txt(f"EMULADORES · {sum(1 for e in emus_estado if e['instalado'])}/{len(emus_estado)} detectados",
                f_peq, DORADO, 650, 292)
            for i, emu in enumerate(emus_estado[:8]):
                col, fila = i // 4, i % 4
                x, y = 650 + col * 285, 320 + fila * 42
                ok = emu["instalado"]
                pygame.draw.rect(pantalla, PANEL if ok else (38, 28, 42),
                                 (x, y, 270, 34), border_radius=7)
                pygame.draw.circle(pantalla, VERDE if ok else ROJO, (x + 13, y + 17), 5)
                txt(emu["nombre"][:28], f_mini, TEXTO, x + 26, y + 9)
            if len(emus_estado) > 8:
                txt(f"+{len(emus_estado) - 8} emuladores en catalogo", f_mini, SUAVE, 650, 500)

            activos = sum(1 for d in cola if d.get("estado") in ("en cola", "bajando"))
            completadas = sum(1 for d in cola if d.get("estado") == "listo")
            txt(f"Descargas: {activos} activas · {completadas} completadas", f_mini, SUAVE, 60, 475)
            horas = stats_resumen.get("segundos", 0) / 3600
            txt(f"ESTADISTICAS DE JUEGO: {stats_resumen.get('lanzamientos', 0)} lanzamientos · "
                f"{stats_resumen.get('juegos', 0)} juegos iniciados · {horas:.1f} horas registradas",
                f_peq, CIAN, 60, 515)
            top_juegos = stats_resumen.get("top", [])
            if top_juegos:
                txt("MAS JUGADOS POR TIEMPO", f_mini, DORADO, 60, 550)
                for i, juego in enumerate(top_juegos[:3]):
                    minutos = int(float(juego.get("segundos", 0)) // 60)
                    txt(f"{i + 1}. {juego.get('nombre', 'Juego')[:30]} · {minutos} min",
                        f_mini, SUAVE, 60, 574 + i * 22)
            pie = "E / Esc volver   ·   R re-escanear biblioteca   ·   T tienda   ·   C controles"

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
                tile = pygame.Rect(62, y + 8, 60, 60)
                hue = sum(ord(ch) for ch in j["n"]) % 360
                tile_color = pygame.Color(0)
                tile_color.hsva = (hue, 58, 58, 100)
                pygame.draw.rect(pantalla, tile_color, tile, border_radius=9)
                inicial = f_med.render(j["n"][:1].upper(), True, TEXTO)
                pantalla.blit(inicial, inicial.get_rect(center=tile.center))
                txt(j["n"], f_med, TEXTO, 138, y + 10)
                txt(j["d"][:90], f_peq, SUAVE, 138, y + 42)
                if j.get("pago"):
                    etiqueta, color_e = "Comprar", DORADO
                elif j.get("dl") or j.get("repo"):
                    etiqueta, color_e = "Descargar", VERDE
                else:
                    etiqueta, color_e = "Pagina oficial", CIAN
                txt(etiqueta, f_peq, color_e, 1020, y + 28)
            pie = "Enter bajar/abrir   flechas mover   Tab descargas   Esc volver"

        elif vista == "controles":
            txt("Configuracion de controles", f_med, TEXTO, 55, 80)
            if esperando:
                tipo, acc = esperando
                nombre_acc = next((n for a, n in ACCIONES if a == acc), acc)
                msg = f"Esperando {'TECLA' if tipo == 'teclado' else 'BOTON'} para <<{nombre_acc}>>"
                pygame.draw.rect(pantalla, (40, 20, 60), (50, 115, 1180, 40), border_radius=8)
                txt(msg, f_peq, DORADO, 640, 125, True)
            else:
                txt("Enter = reasignar   .   Esc = volver", f_peq, SUAVE, 55, 112)
            n_acc = len(ACCIONES)
            top = max(0, min(sel_c, n_acc * 2) // 2 - 4)
            for i, (acc, nombre) in enumerate(ACCIONES):
                y = 160 + (i - top) * 36
                if 160 <= y <= 580:
                    sel_izq = (sel_c == i)
                    r = pygame.Rect(50, y, 560, 32)
                    pygame.draw.rect(pantalla, PANEL2 if sel_izq else PANEL, r, border_radius=6)
                    if sel_izq:
                        pygame.draw.rect(pantalla, AZUL, r, 2, border_radius=6)
                    keys = map_teclas.get(acc, [])
                    keys_str = ", ".join(nombre_tecla(k) for k in keys) if keys else "-"
                    txt(nombre, f_peq, TEXTO, 60, y + 6)
                    txt(keys_str, f_peq, VERDE if keys else SUAVE, 320, y + 6)
                y2 = 160 + (i - top) * 36
                if 160 <= y2 <= 580:
                    sel_der = (sel_c == n_acc + i)
                    r2 = pygame.Rect(640, y2, 560, 32)
                    pygame.draw.rect(pantalla, PANEL2 if sel_der else PANEL, r2, border_radius=6)
                    if sel_der:
                        pygame.draw.rect(pantalla, AZUL, r2, 2, border_radius=6)
                    btns = map_joy.get(acc, [])
                    btns_str = ", ".join(f"Btn {b}" for b in btns) if btns else "-"
                    txt(nombre, f_peq, TEXTO, 650, y2 + 6)
                    txt(btns_str, f_peq, CIAN if btns else SUAVE, 920, y2 + 6)
            y_reset = 160 + (n_acc - top) * 36 + 10
            if y_reset < 620:
                sel_reset = (sel_c == n_acc * 2)
                r3 = pygame.Rect(50, y_reset, 1150, 36)
                pygame.draw.rect(pantalla, (60, 30, 30) if sel_reset else PANEL, r3, border_radius=8)
                if sel_reset:
                    pygame.draw.rect(pantalla, ROJO, r3, 2, border_radius=8)
                txt("Restaurar controles por defecto", f_med, ROJO if sel_reset else SUAVE, 640, y_reset + 6, True)
            txt("TECLADO", f_mini, DORADO, 60, 145)
            txt("JOYSTICK / GAMEPAD", f_mini, DORADO, 650, 145)
            pie = "flechas mover   Enter reasignar   Esc volver"

        else:
            txt(f"Descargas  .  destino: {DESTINOS[dest_i]}", f_med, TEXTO, 55, 85)
            if not cola:
                txt("Copia un enlace (http...) y apreta V para empezar", f_med, SUAVE, 640, 300, True)
            for n, it in enumerate(cola):
                y = 145 + n * 88
                if y > 620:
                    break
                r = pygame.Rect(50, y, 1180, 78)
                pygame.draw.rect(pantalla, PANEL, r, border_radius=12)
                if n == sel_d:
                    pygame.draw.rect(pantalla, AZUL, r, 3, border_radius=12)
                txt(it["nombre"][:55], f_med, TEXTO, 70, y + 8)
                pct = it["hecho"] / it["total"] if it["total"] else 0
                est = it["estado"]
                if est == "error":
                    est = "error: " + it.get("error", "")
                partes = f"  (parte {it['parte']}/{len(it['urls'])})" if len(it["urls"]) > 1 else ""
                color_est = ROJO if it["estado"] == "error" else (VERDE if it["estado"] == "listo" else SUAVE)
                txt(f"{est}{partes}  {mb(it['hecho'])} / {mb(it['total'])}", f_peq, color_est, 70, y + 44)
                pygame.draw.rect(pantalla, FONDO, (720, y + 48, 480, 14), border_radius=7)
                wbar = int(480 * (1 if it["estado"] == "listo" else pct))
                pygame.draw.rect(pantalla, VERDE if it["estado"] == "listo" else AZUL, (720, y + 48, wbar, 14), border_radius=7)
            pie = "V pegar   S destino   P pausar   Supr quitar   Tab volver"

        if aviso and ahora < t_aviso and not modo_busqueda:
            pygame.draw.rect(pantalla, (20, 10, 30), (40, 630, 1200, 36), border_radius=8)
            txt(aviso, f_med, ROJO if "Error" in aviso or "error" in aviso.lower() else DORADO, 55, 636)

        if not modo_busqueda and pie:
            txt(pie, f_peq, SUAVE, 55, 685)
        pygame.display.flip()


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--web":
        try:
            import webview
            webview.create_window(NOMBRE + " - Tienda", sys.argv[2], width=1280, height=720, maximized=True)
            webview.start(private_mode=False, storage_path=os.path.join(BASE, "sesion_web"))
        except ImportError:
            webbrowser.open(sys.argv[2])
    else:
        main()
