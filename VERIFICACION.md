# Verificacion (v5.2)

Leyenda: VERIFICADO = comprobado contra una fuente; NO VERIFICADO = hay que probarlo en una PC real.

## shadPS4 (verificado por Claude, 2026-11-22)
- Ultima estable: v0.21.0 (30-oct-2026), repo `shadps4-emu/shadPS4` - VERIFICADO
  (https://shadps4.net, https://sourceforge.net/projects/shadps4.mirror/files/)
- Asset Windows: `shadps4-win64-sdl-0.21.0.zip` (solo build SDL) - VERIFICADO (espejo SourceForge)
- Flags `-g` y `-f true` - segun README oficial (reportado por Grok) - NO VERIFICADO por Claude
- Que el build SDL abra una GUI sin argumentos (tecla G) - NO VERIFICADO

## Emuladores
Patrones de asset documentados en store.py. Si un patron no encuentra asset, la tienda abre la pagina oficial.
Nombres de .exe en EMU_DEFECTO: **NO VERIFICADOS** (se usa EMU_ALTERNATIVAS + busqueda en carpeta).

## Extraccion
- `.zip`: stdlib, aplanado y a prueba de path traversal
- `.7z`: py7zr o 7z.exe (PATH / BASE\\tools) — extraccion real **NO VERIFICADA** en este entorno
