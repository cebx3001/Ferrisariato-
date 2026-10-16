# Iteración de acabado fotográfico

Esta pasada conserva la escena base, la matriz de cámara, los colliders, las
posiciones y dimensiones de todos los mecanismos, la física y los controles.
`blender/ferrisariato-pinball.blend` sigue siendo el original editable;
`blender/ferrisariato-photographic.blend` contiene la nueva dirección de arte.
La copia completa previa, incluido el juego funcional, está en
`/workspace/ferrisariato-revisions/pinball-v1-functional.zip`.

## Cambios visuales

- **Albañilería:** sacos cosidos y etiquetados, paletas de albañil, fragmentos
  de ladrillo y cemento junto a pallets, bloques y pilas existentes.
- **Carpintería:** serrucho con dientes individuales, escuadra, sargento con
  tornillo y mango, recortes de madera, cajas y flexómetro existente.
- **Herramientas:** segundo taladro, maletín abierto con espuma, brocas,
  alicates con articulación, martillo, llaves y destornilladores.
- **Pintura:** bandejas con costillas, pintura húmeda, rodillo de microfibra,
  brocha con cerdas, gotas y latas de distintos tamaños.
- **Obra y jardín:** tuberías y uniones, plantas adicionales, cono, balde y
  cable enrollado alrededor de la carretilla, macetas y bloques existentes.
- **Fabricación:** pernos y arandelas instanciados, perfiles, juntas, encaje
  del vidrio, tornillos avellanados, casquillos y resorte helicoidal.
- **Casa:** canaletas, bajantes con abrazaderas, juntas de revestimiento,
  jambas, alféizares, jardín y ventanas cálidas con luces físicas.

Las escenas laterales se amplían en las zonas ya ocupadas por decoración.
Los espacios de circulación permanecen libres de objetos volumétricos nuevos;
el piso recibe insertos luminosos, gráficos planos y juntas de concreto.
Esto conserva la correspondencia visual con el recorrido físico de la bola.

## Iluminación y materiales

Cycles calcula luces prácticas emparejadas con las bombillas emisivas, luces
bajo los bumpers, insertos del piso, ventanas y acentos azules. Cuatro fuentes
de área producen reflejos de estudio. La escena final contiene 2.834 objetos y 240 luces. El inventario exacto está en
`assets/photographic-inventory.json`.

Los materiales incorporan concreto mineral en dos escalas, poros, madera con
veta anisotrópica procedural, terracota, caucho, acero con rugosidad variable,
lacas con clearcoat y hojas con dispersión subsuperficial. Las microtexturas
son editables y no requieren descargas de recursos externos.

El vidrio usa reflexión Fresnel de lámina delgada, con intensidad atenuada
para representar vidrio antirreflejo fotografiado con polarizador. Sus bordes,
juntas y marco son geometría. Esta aproximación permite una capa alfa sobre
la bola y las paletas móviles; no simula la refracción volumétrica del vidrio
protector. Los acrílicos de las canaletas sí usan transmisión y espesor.

La bola de la web utiliza un sprite de acero renderizado en Cycles con los
reflejos de la escena. Posición y tamaño siguen viniendo de Box2D. Es un mapa
de reflejos fijo, no un trazado de rayos dinámico durante la partida. El
lanzador conserva su recorrido y añade sombreado metálico y hélice continua.
Los displays HTML existentes tienen marco empotrado, profundidad y cristal;
siguen mostrando la puntuación y el tiempo reales.

## Revisiones visuales realizadas

La comparación toma como referencia la infografía de Ferrisariato enviada
en el chat: agrupaciones de obra en los hombros, canales con barandas,
materiales azules y amarillos, luces cálidas y pequeños detalles de fabricación.
La perspectiva funcional existente se conserva por instrucción de esta pasada;
no se intenta igualar su encuadre mediante cambios de cámara o de mecánicas.

1. **Primer render:** más riqueza de materiales y luces, pero las reflexiones
   grandes del vidrio ocultaban parcialmente la casa y los mecanismos; el
   marco superior parecía suspendido y los targets no tenían símbolos en
   el render completo. Se conserva en `docs/photographic-iteration-1.png`.
2. **Segunda revisión:** vidrio menos reflectante y con inclinación compatible
   con la altura de la casa, laterales de apoyo, siete pictogramas físicos,
   variación mineral más suave y halos impresos alrededor de los bumpers.
3. **Exportación:** render de alta resolución, capas del juego y revisión
   posterior en Chromium de escritorio y móvil. Resultados abajo y en
   `docs/photographic-browser-results.json`.

## Reproducir

Se usa Blender 4.3.2, Cycles CPU, AgX, hasta 12 rebotes y 96 muestras en el
render de 1760 × 2200. Las capas web usan 64 muestras a 880 × 1100; la bola
se exporta a 128 × 128. El muestreo adaptativo detiene píxeles convergentes.

Este Blender no incluye OpenImageDenoise. La exportación usa **Intel Open
Image Denoise 2.3.3** externo, con color HDR lineal, albedo y normales de Cycles,
y conserva el canal alfa original. Después se aplica AgX y glare moderado.
No se desenfoca el resultado final ni se generan imágenes ajenas a la escena.

```sh
# Preparar herramientas locales de exportación (Linux x86_64, Python 3.12).
bash games/pinball/scripts/setup-photographic-tools.sh

# Crear la escena enriquecida desde el .blend original (no desde la enriquecida).
blender -b games/pinball/blender/ferrisariato-pinball.blend -t 4 \
  --python-exit-code 1 --python games/pinball/blender/photographic.py

# OIDN_BIN: ejecutable oficial oidnDenoise.
# PINBALL_PYTHON: Python con numpy y OpenEXR.
# PINBALL_PYTHONPATH: ruta opcional a esos módulos.
blender -b games/pinball/blender/ferrisariato-photographic.blend -t 4 \
  --python-exit-code 1 --python games/pinball/blender/render_photographic.py -- hero
blender -b games/pinball/blender/ferrisariato-photographic.blend -t 4 \
  --python-exit-code 1 --python games/pinball/blender/render_photographic.py -- web
python3 games/pinball/scripts/export-web.py
```

Los valores predeterminados de las herramientas externas corresponden a la
caché de este entorno. Fuera de él, se deben indicar las rutas mediante las
variables anteriores. El juego publicado no usa Blender, Python ni OIDN.
Los EXR intermedios quedan en `/tmp/ferrisariato-photo`.

El render aislado de Blender muestra los mecanismos en reposo; las capturas
del navegador muestran la integración con displays y una partida real.
La valoración final del parecido fotográfico sigue siendo una revisión de arte,
no una propiedad demostrable mediante pruebas automáticas.

La auditoría geométrica comparó **1.801 objetos originales**, incluida la cámara,
y encontró **cero cambios** de transformaciones o mallas base. La auditoría
no compara materiales ni modificadores decorativos; los insertos luminosos
incorporan un espesor visual nuevo. Los hashes de
`layout.json`, `physics.js`, `audio.js`, Box2D y `projection.json` también
coinciden con la copia anterior. Véanse los informes `docs/photographic-geometry-audit.json`
y `docs/photographic-preservation.json`.

## Resultado de validación

- **25/25 pruebas físicas** aprobadas.
- **12/12 comprobaciones de navegador** aprobadas, con teclado, multitáctil,
  lanzamiento real, contactos, luces transitorias, sonido, tiempo y reinicio.
- Cero errores JavaScript y cero solicitudes fallidas en la sesión verificada.
- Trabajo medio por fotograma: **0,74 ms** en Chromium de este entorno;
  no equivale a una garantía de FPS en teléfonos físicos.
- Cinco imágenes WebP: **401.228 bytes** en total.
- Visor de comparación: deslizador comprobado y capturas a 880 × 1100 desde
  el canvas real, en reposo, con la misma cámara.

Entrega: `docs/photographic-hero.png`, `docs/photographic-comparison.png`,
`docs/visual-comparison.html`, `docs/photographic-desktop.png` y
`docs/photographic-mobile.png`. Se revisaron el render completo y las capturas
antes de cerrar esta pasada. La versión funcional anterior continúa archivada.
