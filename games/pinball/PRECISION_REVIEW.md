# Ferrisariato · Precisión V4

La implementación actual está en `/games/pinball/`. V4 modifica la escena V3 existente, conserva las versiones anteriores y conecta el plunger con un único canal elevado jugable. El logotipo conserva los píxeles y la proporción del recurso oficial.

## Entrega

- [Escena editable](blender/ferrisariato-precision.blend).
- [Render final Cycles](docs/precision-hero.png), 1320 × 1980, 96 muestras, AgX y Open Image Denoise con pases auxiliares.
- [Comparación interactiva y cinco acercamientos](docs/precision-comparison.html).
- [Mapa de colisiones](docs/precision-collision-map.svg) y [holguras medidas](docs/precision-corridor-clearances.json).
- [Video del lanzamiento completo](docs/precision-tests/complete-channel-launch.webm), [secuencia de ocho capturas](docs/precision-tests/launch-contact-sheet.jpg) y [posiciones registradas](docs/precision-tests/launch-timeline.json).
- [Resultados individuales de física](docs/precision-physics.tap) y [pruebas adicionales de navegador](docs/precision-tests/results.json).
- [Auditoría de decoración en el campo](docs/precision-decoration-audit.json) y [distancias de la bola a la decoración del canal](docs/precision-channel-decoration-audit.json). Una lista vacía significa que no se detectaron interferencias bajo el criterio documentado por el script.

## Resultados de validación

- 29 pruebas de física aprobadas.
- 12 comprobaciones de regresión en Chromium aprobadas, incluyendo teclado y multitáctil.
- 11 comprobaciones adicionales aprobadas: lanzamiento grabado, oclusiones, luces, pausa/reinicio y partidas completas de escritorio y móvil.
- Cero errores JavaScript registrados. El detalle de cada comprobación y las métricas están en los archivos enlazados arriba.

## Recorrido y física

`layout.json` contiene una sola spline muestreada en 481 puntos, su longitud de arco, el sensor, la velocidad de salida y los colisionadores. `scripts/build-ramp.py` construye esa información mediante interpolación cúbica XY y tangentes monótonas en Z para impedir que la desembocadura atraviese el piso.

1. Box2D impulsa la bola desde el plunger hasta un sensor real.
2. `RAMP_TRAVEL` desactiva el cuerpo de la bola, manteniendo activos los motores de los flippers.
3. `src/ramp.js` interpola por longitud de arco. El giro visible depende de distancia / radio; las luces siguen los mismos puntos del modelo.
4. Al llegar al último punto, la bola vuelve a activarse exactamente en la desembocadura con velocidad tangente hacia los bumpers. Solo entonces se emite el evento de entrada al campo.
5. La pausa detiene el avance y el reloj. Reinicio, nueva bola y fin por tiempo eliminan el estado guiado.

Se mantienen tres bolas, 120 segundos, los valores de puntuación, contactos de bumpers/targets/slings, audio, teclado y multitáctil. Los postes interiores tienen cuerpos circulares pasivos, sin otorgar puntos. Las paletas usan un radio de 0,21 tanto en su contorno visible como en sus fixtures.

El canal tiene 0,70 unidades de ancho para una bola de diámetro 0,32: 0,19 libres a cada lado. Los pasos exteriores junto a los bumpers, descontando los postes, tienen 0,495 y 0,595 unidades. La salida está en `(2.65, 7.05, 0.045)` y su dirección apunta hacia el bumper central.

## Cámara, profundidad e interfaz

El tablero y sus componentes tienen una inclinación física de 6,5°. La cámara conserva una orientación independiente. `assets/projection.json` exporta la matriz de cámara combinada con la transformación del tablero, además de los cuadriláteros de los displays físicos. El lienzo mide 880 × 1320.

El cabezal se renderiza dentro de la máquina: carcasa, marcos, lentes, tornillos, logotipo oficial y letrero «CONSTRUYE TU CASA CON TODO». Los números y las luces de bolas restantes se actualizan sobre ese cabezal; los elementos HTML originales siguen proporcionando los valores semánticos.

`assets/depth.png` almacena el pase Z opaco de la misma cámara. Se codifica como entero de 16 bits en los canales R/G, con alcance de 100 unidades. El renderizador compara profundidad en el eje de cámara —no distancia euclidiana— y enmascara por píxel la bola. Esto permite verla sobre el canal y ocultarla detrás de la casa, postes y componentes. El acrílico transparente y el vidrio protector no forman parte de esa máscara opaca.

El juego sigue siendo una composición 2,5D: Box2D para el campo, una spline 3D guiada para el canal y capas Cycles con profundidad para la imagen. Los reflejos del entorno y la iluminación global están prerenderizados; las luces de reacción se superponen en tiempo real. No hay trazado de rayos dinámico en el navegador. Las pruebas móviles usan Chromium con emulación táctil, no dispositivos físicos.

## Correcciones efectuadas tras comparar los renders

- Se sustituyeron todos los tramos antiguos por un solo canal continuo desde el lanzador hasta el piso.
- Se ajustaron cámara, altura del cabezal y plataforma residencial para evitar que el canal cubriera los números.
- Se elevó la casa sobre una base con escalones; se añadió el frontón y se reforzaron las copas mediante hojas individuales.
- Se añadieron terrazas y repisas con espesor, superficies, soportes y grupos de materiales/herramientas.
- Se corrigieron transformaciones de las piezas nuevas antes de inclinar el tablero; ninguna queda agrupada accidentalmente en el centro.
- Se movieron madera, recipientes, plantas y herramientas que invadían la salida. Las antiguas barandas interiores se sustituyeron por guías coherentes con los colliders.
- Se modelaron flippers por capas independientes y se mantuvieron los slingshots ensamblados.
- Los targets usan lentes empotradas orientadas hacia el jugador. Los tanques tienen tapa azul, mecanismo central e insignia frontal.
- El suelo mineral conserva poros y juntas bajo una capa pulida: rugosidad variable 0,10–0,18, coat 0,72 y coat roughness 0,085. Los cromados, pinturas, caucho, madera y acrílicos mantienen materiales separados.
- Se ajustó el faldón frontal al tamaño del logotipo y se mantuvo un recorte para el lanzador.
- Se elevó el vidrio para que no cortara la casa y se atenuó su reflejo. Se añadió una luz de producto dirigida al cabezal.

Las fotografías originales y los renders intermedios están conservados en `docs/`. La comparación visual permite revisar las diferencias de proporciones, densidad y acabado; las pruebas de software verifican el funcionamiento, no certifican equivalencia fotográfica.

## Reproducir

Desde la raíz del repositorio:

```sh
bash games/pinball/scripts/setup-photographic-tools.sh
python3 games/pinball/scripts/build-ramp.py
blender -b games/pinball/blender/ferrisariato-premium.blend -t 4 --python-exit-code 1 -P games/pinball/blender/precision.py
blender -b games/pinball/blender/ferrisariato-precision.blend -t 4 --python-exit-code 1 -P games/pinball/blender/audit_precision.py
blender -b games/pinball/blender/ferrisariato-precision.blend -t 4 --python-exit-code 1 -P games/pinball/blender/render_precision.py -- preview
```

Tras revisar el preview, exportar:

```sh
blender -b games/pinball/blender/ferrisariato-precision.blend -t 4 --python-exit-code 1 -P games/pinball/blender/render_precision.py -- hero
PINBALL_SAMPLES=48 blender -b games/pinball/blender/ferrisariato-precision.blend -t 4 --python-exit-code 1 -P games/pinball/blender/render_precision.py -- web
blender -b games/pinball/blender/ferrisariato-precision.blend -t 4 --python-exit-code 1 -P games/pinball/blender/render_depth.py
python3 games/pinball/scripts/export-web.py
python3 games/pinball/scripts/collision-map.py
python3 games/pinball/scripts/precision-review.py
```

Cada modo renderiza desde el `.blend` existente. `PINBALL_SAMPLES` permite modificar el muestreo; `PINBALL_ASSET_STAGE` cambia el destino de las capas PNG. El denoising externo conserva alfa y usa normales/albedo de Cycles. No ejecutar `generate.py` para esta revisión: reconstruye la versión base histórica.

Para pruebas, iniciar un servidor en otra sesión y ejecutar:

```sh
python3 -m http.server 8081 --bind 127.0.0.1
```

```sh
node --test --test-reporter=tap games/pinball/tests/physics.test.mjs
PINBALL_TEST_URL=http://127.0.0.1:8081/games/pinball/ python3 games/pinball/tests/browser.py
PINBALL_TEST_URL=http://127.0.0.1:8081/games/pinball/ python3 games/pinball/tests/precision-browser.py
```

El último script graba el lanzamiento, comprueba pausa/reinicio durante el recorrido, verifica profundidad/luces y termina partidas completas de escritorio y móvil mediante entradas reales. No acelera el tiempo ni teletransporta la bola en esas partidas. `?debug=1` permite superponer colisiones y recorrido durante el juego.

Los archivos de HOME, IN-STORE, el motor XR y el Box2D original no se modificaron en esta pasada. Las copias anteriores permanecen disponibles. La entrega está preparada para la publicación estática del repositorio en `/games/pinball/`; la revisión visual está en `/games/pinball/docs/precision-comparison.html`.
