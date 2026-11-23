# Roadmap — Mi Consola

Objetivo: convertir Mi Consola en una experiencia de consola para PC, manteniendo una base segura y recuperable.

## Fase 1 — Frontend unificado

- [x] Lobby a pantalla completa.
- [x] Navegación por teclado y soporte de gamepad configurable.
- [x] Pestañas clicables con mouse.
- [x] Biblioteca local, búsqueda, favoritos y ordenamiento.
- [x] Portadas locales y descarga automática de Steam/Libretro con placeholders.
- [x] Detección de juegos de PC y tiendas compatibles según el sistema.
- [x] Lanzamiento de juegos y emuladores desde la biblioteca.
- [x] Tienda curada de software libre/gratuito y emuladores.
- [x] Descargas HTTP/HTTPS y extracción ZIP/7z con validación de rutas.
- [x] Ajustes para abrir carpetas y añadir ubicaciones de juegos de PC.
- [x] Panel de estado con métricas reales disponibles y detección de emuladores.
- [x] Estadísticas locales de lanzamientos y tiempo de ejecución.
- [ ] Pruebas automatizadas y ejecución completa en Windows real.
- [ ] Mejorar la navegación por mando en todas las ventanas y diálogos nativos.
- [ ] Mejorar la ficha de cada juego con metadatos y arte de más fuentes verificadas.
- [ ] Catálogo amplio de metadatos (separado de la biblioteca instalada/local).

## Fase 2 — Consola OS en PC

- [ ] Arranque directo al launcher con mecanismo de recuperación.
- [ ] Autoarranque configurable y gestión segura de energía.
- [ ] Actualizaciones desde GitHub con verificación y rollback.
- [ ] Ajustes de Windows/Linux para audio, resolución, red y mandos.
- [ ] Instalador USB o modo kiosk documentado y reversible.

## Fase 3 — Consola física

- [ ] Definir hardware objetivo y requisitos de rendimiento.
- [ ] Imagen reproducible del sistema.
- [ ] Controles, refrigeración y carcasa.
- [ ] Respetar licencias: no incluir juegos, BIOS, firmware ni claves protegidas.

## Alcance importante

Mi Consola integra los emuladores como frontend: los detecta, organiza sus juegos y los inicia desde una interfaz común. Los emuladores siguen siendo programas independientes porque cada proyecto tiene su propio código, dependencias, licencia y requisitos. La tienda no distribuye juegos comerciales ni archivos protegidos.
