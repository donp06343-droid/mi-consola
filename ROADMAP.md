# Roadmap - Mi Consola

Meta: pasar de un launcher a un **sistema de consola** (PC) y luego a una **consola fisica**.

## Fase 1 - Launcher completo (actual, v5.x)
- [x] Biblioteca, portadas, favoritos, tienda con categorias
- [x] Modo kiosk (Capa 1)
- [x] shadPS4: instalar, detectar, lanzar
- [x] Instalador generico de emuladores (+ .7z) - v5.2 (falta probar en PC real)
- [x] Pantalla de estado del sistema (tecla E)
- [ ] Tests + CI
- [ ] Navegacion total con mando

## Fase 2 - Consola OS en PC
- [ ] Arranque directo al launcher (reemplazo de shell de Windows) con recuperacion
- [ ] Autoarranque, login automatico, energia (suspender/apagar desde el menu)
- [ ] Actualizaciones automaticas desde GitHub (con rollback)
- [ ] Ajustes de sistema desde la UI: wifi, bluetooth, audio, resolucion
- [ ] Instalador / USB booteable
- [ ] Evaluar base Linux ligera (Steam Deck style) vs Windows kiosk

## Fase 3 - Consola fisica
- [ ] Definir hardware objetivo (mini-PC / SBC) y requisitos para PS2/PS3/Switch/PS4
- [ ] Imagen de sistema reproducible
- [ ] Controles, refrigeracion, carcasa
- [ ] Licencias: solo software libre/legal, sin BIOS/firmware/juegos incluidos
