# Corrección de componentes y densidad V5

La entrega V4 conservaba flippers de ancho constante, slingshots demasiado planos y grupos laterales separados. El navegador además dibujaba sus propias barras, diferentes de los modelos Blender. Esta revisión sustituye esas piezas en la escena existente y elimina esa divergencia visual.

- Flippers con pivote ancho y punta estrecha; cuerpo azul, goma azul de mayor rugosidad, tapa blanca independiente, eje cromado y gráfico de casa con alero separado. Se eliminaron fijaciones antiguas que atravesaban el gráfico. Los colisionadores siguen el mismo contorno cónico; se conservaron pivotes, recorrido, motores y controles.
- Slingshots con base negra, espaciadores cromados, marco amarillo de espesor real, panel azul independiente, gomas, tornillos con arandela y bombilla dentro de un soporte rebajado. El contorno exterior conserva su triángulo funcional.
- Miniaturas individuales: taladro con batería, gatillo, agarre, ventilación y mandril; flexómetros con carcasa, cierre, cinta graduada y gancho; pinzas con mangos, pivote, mandíbulas y dientes; herramientas, carretilla con bastidor y grava individual, bloques realmente huecos, ladrillos, pallets clavados, tablones, cubetas, pintura, cables y tubos.
- Los conjuntos adicionales mezclan piezas sobre pallets, cajas y terrazas, con rotaciones, alturas y superposiciones. La revisión oblicua detectó que el taladro seguía siendo demasiado rectangular: se sustituyeron carcasa y agarre por contornos moldeados y se añadieron insertos de goma y filos helicoidales. Se corrigieron también los apoyos de dos grupos altos del fondo. El inventario de esta densificación se encuentra en `assets/dense-workshop-inventory.json`. Las plantas laterales tienen maceta abierta, tierra y hojas curvas; las palmeras de la casa tienen tronco segmentado y numerosos foliolos independientes.
- Piso mineral con microtextura conservada y recubrimiento pulido. Las bombillas y luces físicas iluminan los grupos y producen reflejos en piso, cromados, plásticos y acrílico.
- El juego carga un atlas de 62 renders Cycles de los propios flippers: 31 poses por lado desde la cámara compartida. Ya no existe la representación alternativa de barras dibujadas. La iluminación global del juego sigue prerenderizada.

## Revisión visual

Abrir `/games/pinball/docs/component-review.html`. Incluye captura general, seis acercamientos, una vista oblicua adicional de herramientas, referencias, antes/después, escena editable, mapa de colisiones y video del lanzamiento. Los seis recortes se renderizan a mayor resolución desde la misma cámara. `render_workshop_macro.py` añade una cámara de revisión oblicua que nunca se guarda en la escena del juego.

## Reproducir sobre la escena existente

```sh
blender -b games/pinball/blender/ferrisariato-precision.blend -P games/pinball/blender/reference_components.py
blender -b games/pinball/blender/ferrisariato-precision.blend -P games/pinball/blender/refine_component_finish.py
blender -b games/pinball/blender/ferrisariato-precision.blend -P games/pinball/blender/correct_component_clearances.py
blender -b games/pinball/blender/ferrisariato-precision.blend -P games/pinball/blender/garden_miniatures.py
blender -b games/pinball/blender/ferrisariato-precision.blend -P games/pinball/blender/finish_reference_scene.py
blender -b games/pinball/blender/ferrisariato-precision.blend -P games/pinball/blender/densify_reference_workshops.py
blender -b games/pinball/blender/ferrisariato-precision.blend -P games/pinball/blender/finish_dense_lighting.py
blender -b games/pinball/blender/ferrisariato-precision.blend -P games/pinball/blender/support_dense_canopies.py
blender -b games/pinball/blender/ferrisariato-precision.blend -P games/pinball/blender/sculpt_drill_details.py
blender -b games/pinball/blender/ferrisariato-precision.blend -P games/pinball/blender/populate_visible_rear_terraces.py
blender -b games/pinball/blender/ferrisariato-precision.blend -P games/pinball/blender/audit_precision.py
```

Exportar con `render_precision.py -- hero` (64 muestras), `-- web` (32 muestras), `render_depth.py`, `render_reference_details.py` y `render_flipper_atlas.py`; después ejecutar `export-web.py`, `pack-flipper-atlas.py`, `precision-review.py` y `component-review.py`. Los scripts requieren las herramientas fotográficas ya configuradas y conservan los originales de otras páginas del repositorio.

## Validación

`tests/physics.test.mjs` incluye el contacto del cuerpo ancho y la ausencia de contacto fantasma alrededor de la punta estrecha. `tests/components-browser.py` verifica que las poses renderizadas siguen ambos motores, que los recursos y acercamientos existen y que no hay errores JavaScript. Las pruebas generales y de partidas completas se ejecutan también sobre los recursos finales.

La auditoría usa las geometrías de las nuevas microescenas y comprueba tanto el piso como la esfera a lo largo de la spline. Los objetos escenográficos siguen sin introducir colisiones adicionales. La validación móvil usa Chromium con multitáctil emulado.

Resultados finales V5.4: 30 pruebas de física, 12 regresiones de navegador, 5 verificaciones de componentes y 11 verificaciones de canal y partidas completas: 58 aprobadas, 0 fallidas. Partida de escritorio: 120 segundos y 14.225 puntos; móvil emulado: tres lanzamientos y 8.850 puntos. Trabajo medio del canvas: 1,18 ms por cuadro. Auditoría geométrica: cero intrusiones decorativas en piso o canal. Informes individuales en `docs/precision-validation-summary.json`.
