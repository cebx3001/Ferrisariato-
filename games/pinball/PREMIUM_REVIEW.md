# Iteración visual V3 — continuidad y ensamblaje

La escena editable de esta iteración es `blender/ferrisariato-premium.blend`.
Se deriva de `ferrisariato-photographic.blend`, que se conserva, junto con la
base original. No se reconstruyó la lógica del juego.

## Referencias y decisiones

Los cinco acercamientos están en `docs/references/`. Se usaron para revisar:

- **43912:** flipper azul con tapa marfil separada, eje cromado, tornillos,
  sling por capas, separadores, goma y cubierta ámbar.
- **43910 y 43909:** grupos compactos de pallets, ladrillos, tablones,
  flexómetros, herramientas, plantas y recipientes bajo las rampas;
  bandejas con tornillos y piezas enlazadas, tuberías y herrajes.
- **43907 y 43908:** terraza con base, bordes, patio, jardineras, césped,
  troncos ramificados y hojas individuales; marcos, bisagras, umbral,
  puerta con paneles y fijaciones del cartel. Ruta superior conectada
  detrás de la casa, soportes, uniones, barandas y descensos visibles.

La cámara, posiciones jugables y huellas de colisión siguen siendo las
anteriores. Los canales nuevos son **estructura visual**; no incorporan
circulación de bola en altura ni cambian Box2D. La densidad se concentra en
los laterales y bajo las rampas; las rutas jugables centrales permanecen libres.

## Revisión mediante renders

1. `docs/premium-pass1.png`: primera pasada en Cycles. Se detectó el puente
   demasiado alto/cortado por el encuadre, extremos del marco elevados,
   emisores blancos sin envolvente y huecos bajo dos tramos laterales.
2. Se bajó el puente posterior detrás de la casa, se recortó el remate del
   marco, se añadieron envolventes ámbar alrededor de núcleos más pequeños,
   sockets y grupos compactos adicionales. `docs/premium-preview.png`
   documenta la comprobación desde la misma cámara.
3. En una tercera comprobación se separaron los biseles amarillos y los
   centros opalinos de los inserts, y se reforzaron las flechas de cobalto
   y las bases de señalización junto a las microescenas.

El render conserva AgX, luces trazadas y reflejos del entorno. Se corrigieron
fuentes puntuales encerradas dentro de piezas opacas. Los emisivos y el
bloom moderado acompañan la iluminación; no son su único origen.

La exportación del fondo mantiene las rampas activas para sombras y
reflejos, pero invisibles a los rayos de cámara: las rampas visibles se
componen en su propia capa. La bola conserva el contexto de bumpers,
rampas y vidrio en su exportación reflectiva.

La capa de canales utiliza holdouts de las piezas estáticas para evitar
que los pies de los soportes se superpongan a herramientas situadas delante.
Se separaron dos árboles del recorrido posterior al revisar sus holguras.
Los tramos descendentes y curvos usan soportes cortos anclados al lecho
del canal; las columnas al suelo se concentran en el puente recto y los
desembarcos, evitando atravesar latas, pallets y herramientas.

Los flippers del navegador dibujan caras laterales y tapas separadas usando
el ángulo real de cada cuerpo, sin animación prefabricada. El acabado del
cabezal cambia por CSS: placa atornillada, lentes empotradas y una fuente
local de siete segmentos, con contornos originales generados mediante
`scripts/build-display-font.py` (fontTools, solo para regenerarla). Los
valores y elementos HTML funcionales permanecen intactos.
El vidrio usa la aproximación de capa fina documentada en la versión V2.

## Reproducir

Desde la raíz del repositorio, con el entorno de Blender/OIDN ya preparado:

```sh
blender -b games/pinball/blender/ferrisariato-photographic.blend -t 4 \
  --python-exit-code 1 --python games/pinball/blender/premium.py
blender -b games/pinball/blender/ferrisariato-premium.blend -t 4 \
  --python-exit-code 1 --python games/pinball/blender/render_premium.py -- preview
blender -b games/pinball/blender/ferrisariato-premium.blend -t 4 \
  --python-exit-code 1 --python games/pinball/blender/render_premium.py -- hero
blender -b games/pinball/blender/ferrisariato-premium.blend -t 4 \
  --python-exit-code 1 --python games/pinball/blender/render_premium.py -- web
python3 games/pinball/scripts/export-web.py
PINBALL_TEST_URL=http://127.0.0.1:8081/games/pinball/ \
  python3 games/pinball/scripts/capture-premium-review.py
```

`PINBALL_ASSET_STAGE` permite exportar PNG a una carpeta temporal antes de
activar las cinco capas del juego. Los EXR quedan en `/tmp/ferrisariato-premium`.
Las dependencias y sus versiones siguen en `PHOTOGRAPHIC_REVIEW.md` y
`scripts/setup-photographic-tools.sh`.

El render de Blender muestra la mesa con los mecanismos en reposo. El
cabezal de puntaje y temporizador aparece en las capturas del navegador.
La escena todavía es una representación estilizada: las pruebas funcionales
no certifican equivalencia fotográfica con las referencias ni aprobación de arte.

## Inventario y conservación

La escena contiene 4.645 objetos, 272 luces y 111 mallas compartidas; la
pasada incorpora 1.811 objetos sobre V2. El número incluye fijaciones,
hojas y herrajes: no es por sí mismo una medida de fidelidad visual.

La auditoría geométrica compara 2.594 objetos originales no luminosos:
2.492 mantienen mallas y transformaciones; 102 cambios corresponden al
remate del vidrio y la escala de los núcleos de las bombillas decorativas.
No faltan objetos originales. La cámara y las guías físicas se conservan.
El informe no compara materiales ni modificadores: estos sí se refinaron.

Los siete archivos protegidos coinciden byte por byte con V2: layout,
física, audio, controlador de juego, HTML, proyección y Box2D. Véanse
`docs/premium-preservation.json` y `docs/premium-geometry-audit.json`.

El borrador del entorno conserva instalación y arranque del sitio estático
y añade la preparación reproducible de OIDN y los comandos de V3. Guardar
el borrador no publica el sitio ni el snapshot del entorno.

## Archivos de revisión

- `docs/premium-hero.png`: render final de la escena, 1760 × 2200, Cycles,
  96 muestras máximas, muestreo adaptativo y OIDN con albedo/normales.
- `docs/premium-comparison.png`: V2 frente a V3 desde el canvas real.
- `docs/premium-comparison.html`: comparación con deslizador.
- `docs/premium-detail-comparison.jpg`: cinco referencias y recortes del render.
- `docs/premium-desktop.png` y `docs/premium-mobile.png`: juego integrado.

Las versiones anteriores siguen disponibles; los nuevos scripts de V3 no
sobrescriben los `.blend` base ni V2. Las capas web activas sí se actualizan
al completar la exportación y la comprobación de sus cinco archivos.
