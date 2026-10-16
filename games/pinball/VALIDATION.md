# Validación de la iteración fotográfica

La actualización conserva las 25 pruebas físicas y vuelve a pasar las 12
comprobaciones de navegador. Los informes actuales están en
`docs/photographic-browser-results.json`, `docs/photographic-preservation.json`
y `docs/photographic-geometry-audit.json`. Véase `PHOTOGRAPHIC_REVIEW.md` para
los renders y el alcance de las aproximaciones visuales.

La evidencia de la primera versión se conserva a continuación.

# Validación de la prueba de concepto

Ejecutada en este entorno cloud con Node 24.19.0, Python 3.12.14, Blender
4.3.2 y Chromium/Playwright. El servidor estático se ejecutó desde la raíz
del repositorio. No se publicó el sitio ni se validó un entorno nuevo.

## Física: 25 pruebas aprobadas

`node --test games/pinball/tests/physics.test.mjs`

- Cinco niveles de carga: la bola parte del lanzador, recorre su carril y
  entra físicamente al campo. No se teletransporta para superar la entrada.
- Tres bumpers principales y dos tanques: contacto, rebote, puntos y luz
  temporal. Se mide la respuesta en el primer contacto, antes de que otro
  elemento de la mesa vuelva a golpear la bola.
- Siete objetivos: cada contacto activa su propia luz y suma 150 puntos.
- Dos slingshots: impulso activo hacia arriba.
- Dos flippers: el motor mueve la articulación, golpea la bola, regresa y
  deja independiente la otra paleta.
- Tres pérdidas, reposición en el lanzador y fin de partida.
- Temporizador, reinicio y limpieza del estado.
- Colisión continua contra las paredes a alta velocidad.
- Simulación prolongada con estado finito, bola acotada y puntuación real.

## Navegador: 12 comprobaciones aprobadas

`python3 games/pinball/tests/browser.py`

1. Flechas izquierda/derecha independientes.
2. Carga con espacio, liberación y entrada real al campo.
3. Puntos y tiempo visibles, contexto Web Audio activo y sonidos emitidos.
4. Siete contactos con objetivos, puntuación, luces independientes y apagado.
5. Rebotes de los cinco bumpers.
6. Ambos slingshots activos.
7. Pausa y continuación del temporizador.
8. Tres pérdidas, fin de partida, reinicio y agotamiento del tiempo.
9. Tiempo medio de trabajo del fotograma por debajo de 20 ms en este equipo.
10. Dos dedos simultáneos y liberación independiente en emulación móvil.
11. Toques fuera del canvas, en el borde inferior, activan la mitad correcta.
12. Lanzador táctil independiente, entrada al campo y ausencia de desborde.

No hubo excepciones JavaScript ni solicitudes fallidas en el pinball. La
medición de trabajo de fotograma no garantiza FPS en teléfonos físicos.
Resultados y capturas del ejecutor: `/tmp/ferrisariato-pinball-tests`.
Las capturas de revisión se conservan también en `docs/`.

## Arte y aislamiento

Blender generó 1.810 objetos editables y 27 mallas compartidas. Se compararon
las capas compuestas con la infografía y se corrigieron los objetos ausentes,
las tapas de los tanques y la oclusión del taladro y la caja amarilla por los
canales. Ver `VISUAL_REVIEW.md` para el inventario y sus límites.

Los 11 archivos de la fuente original conservan sus hashes. El logotipo
coincide byte por byte con el recurso oficial del repositorio.
`git diff --exit-code` confirmó que ningún archivo previamente versionado
fue modificado: toda la implementación nueva está en `games/pinball/`.

Las dos pruebas existentes de XR también pasaron. Las rutas de HOME e
IN-STORE y sus recursos continúan sirviéndose. La navegación del catálogo,
favoritos y simulación de pisos fue comprobada. Para el visor 3D HOME se
entregó a Playwright una respuesta del CDN obtenida con TLS verificado:
Chromium directo no reconocía la CA del proxy del entorno. No se desactivó
TLS ni se modificó su almacén de confianza. Esta limitación no afecta al
pinball, cuyos recursos son locales.

Pendientes de aceptación externa: prueba en dispositivos físicos y
aprobación visual contra una eventual imagen final distinta de la
infografía recibida. La circulación por los canales elevados queda fuera
del alcance de esta versión, según la especificación.
