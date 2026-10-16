# Ferrisariato · Pinball

Prueba de concepto independiente. Ruta de publicación: `/games/pinball/`.
No modifica HOME, IN-STORE ni el manifiesto de dependencias de la raíz.

## Ejecutar

Desde la raíz del repositorio:

```sh
python3 -m http.server 8080 --bind 127.0.0.1
```

Abrir la ruta `/games/pinball/` del servidor. Todos los recursos de la partida
son locales; no necesita npm, CDN, backend, secretos ni una compilación web.
El audio se habilita con la primera interacción del usuario.

## Controles y reglas

| Acción | Escritorio | Móvil |
| --- | --- | --- |
| Paleta izquierda / derecha | Flechas ← / → | Cada mitad de la mesa, simultáneamente |
| Lanzador | Mantener espacio y soltar | Mantener el botón LANZAR y soltar |
| Pausa | Botón PAUSAR o P | Botón PAUSAR |
| Nueva partida | INICIAR / REINICIAR | INICIAR / REINICIAR |

Tres bolas y 120 segundos. Bumper principal: 100 puntos; tanque: 75;
objetivo: 150; slingshot: 25. Luces de impacto de 200 ms y sonidos sintetizados
con variaciones por elemento. La casa es escenografía permanente.
Perder el foco o cambiar de pestaña pausa y libera todos los controles.
El plunger activa un sensor físico y el estado `RAMP_TRAVEL`: la bola sube por
el canal derecho, rodea la casa, desciende por la izquierda y recupera Box2D
a nivel del piso. La pausa congela también este recorrido; reinicio y nuevas
bolas limpian su estado. El recorrido comparte los mismos 481 puntos con Blender.

## Estructura

| Ruta | Contenido |
| --- | --- |
| `upstream/` | Copia íntegra e inalterada de lrusso/Pinball en el commit documentado |
| `vendor/box2d.js` | Núcleo Box2D extraído del juego original, sin Phaser ni inicialización de su mesa |
| `layout.json` | Coordenadas compartidas por la escena, el render y los colliders |
| `src/physics.js` | Bola continua, paredes, articulaciones, contactos y ciclo de partida |
| `src/renderer.js` | Cámara exportada, capas, paletas y bola móviles, luces |
| `src/audio.js` | Audio sintetizado local mediante Web Audio |
| `src/game.js` | Entradas independientes, interfaz y bucle fijo a 120 Hz |
| `blender/generate.py` | Construcción determinista y exportación de la escena y sus capas |
| `blender/props.py` | Piezas modulares, detalles de construcción e instancias enlazadas |
| `blender/ferrisariato-pinball.blend` | Escena base conservada, cámara fija y logotipo incrustado |
| `blender/ferrisariato-photographic.blend` | Escena histórica V2 |
| `blender/photographic.py` | Pasada reproducible de materiales, miniaturas, luces y vidrio |
| `blender/ferrisariato-precision.blend` | Escena V4 editable, canal único y cabezal físico |
| `src/ramp.js` | Interpolación por longitud de arco sobre la trayectoria compartida |
| `assets/` | Capas PNG de trabajo, WebP para web, cámara y logotipo original |
| `tests/` | Física con Node y ejecución real en Chromium con Playwright |

## Iteración de acabado fotográfico

La versión actual usa `blender/ferrisariato-precision.blend` (V4).
Consulta [PRECISION_REVIEW.md](PRECISION_REVIEW.md) para reproducir el canal,
la cámara, los renders, las auditorías y las pruebas completas.
Las versiones V1, V2 y V3 se conservan como antecedentes.
Consulta [PREMIUM_REVIEW.md](PREMIUM_REVIEW.md) para la iteración V3,
las referencias de detalle, la comparación y sus comandos reproducibles.
La pasada V2 se conserva como antecedente.
Consulta [PHOTOGRAPHIC_REVIEW.md](PHOTOGRAPHIC_REVIEW.md) para ver los cambios,
las revisiones, las limitaciones del vidrio y los comandos de exportación con
Cycles y Open Image Denoise. El `.blend` original se conserva como base.

## Regenerar el arte base (versión anterior)

Estos comandos reconstruyen la base. Para actualizar el juego actual después
de ejecutarlos, continúa con la pasada fotográfica y su exportación descritas
en `PHOTOGRAPHIC_REVIEW.md`; las capas base no incluyen los nuevos pictogramas.

Herramientas comprobadas en el entorno: Blender 4.3.2, Python 3.12 con Pillow,
Node 24 y Chromium con Playwright. Blender usa CPU con cuatro hilos;
no necesita GPU. Esta distribución no incluye OpenImageDenoise, por lo que
se renderiza con muestreo real sin ese denoiser.

```sh
blender -b -t 4 --python games/pinball/blender/generate.py
python3 games/pinball/scripts/export-web.py
```

Para volver a renderizar una capa después de editar materiales en el `.blend`,
sin reconstruir toda la geometría:

```sh
blender -b games/pinball/blender/ferrisariato-pinball.blend -t 4 --python games/pinball/blender/render_existing.py -- interactives
python3 games/pinball/scripts/export-web.py
```

Colecciones separadas: escenografía estática, bumpers/tanques/objetivos/
slingshots, elementos móviles y canales elevados en primer plano. La web
compone `table.webp`, `interactives.webp`, `foreground.webp` y `glass.webp`; las luces son
una capa transitoria y los indicadores son HTML. La bola (`ball.webp`, acero renderizado en Cycles) y las paletas se
dibujan cada fotograma desde los cuerpos Box2D, usando la misma matriz
proyectiva que Blender, sin interpolar entre poses prerenderizadas.

Unidades físicas: ancho 10, largo 16,5; el origen está arriba a la izquierda.
La transformación a Blender es `(x - 5, 8 - y, altura)`. `projection.json`
contiene la transformación del tablero inclinado 6,5°, la matriz cámara/proyección y la resolución de 880 × 1320. Los
colliders corresponden a la huella en el suelo; las tapas, alturas y sombras
se proyectan a su altura real. `?debug=1` muestra las guías de colisión.

El logotipo se copia sin cambiar sus bytes desde
`home/assets/img/logo-ferrisariato.png`. Es blanco con canal alfa; debe
verse sobre azul. Los pictogramas de casa de la mesa son iconos de juego,
no una recreación del logotipo.

## Pruebas reproducibles

```sh
node --test games/pinball/tests/physics.test.mjs
python3 games/pinball/tests/browser.py
npm run test:xr
```

El servidor debe estar activo para la prueba de navegador. Los resultados y
capturas se escriben en `/tmp/ferrisariato-pinball-tests`; se puede cambiar
con `PINBALL_TEST_OUTPUT`. `PINBALL_TEST_URL` permite usar otro servidor.
La instrumentación de diagnóstico solo se expone con `?test=1`. Las pruebas
de contacto colocan una bola con posición y velocidad conocidas y ejecutan
el mundo físico real; no llaman directamente a la puntuación ni falsifican
colisiones. También se comprueban lanzamientos sin reposicionar la bola.

## Alcance y siguientes pasos

Las cinco fotografías aprobadas están en `docs/precision-references/`.
La comparación general, los acercamientos y las pasadas intermedias se revisan
en `docs/precision-comparison.html`. La versión actual conecta el plunger con
el canal elevado y vuelve a la física del campo en su desembocadura.

La reproducción usa capas Cycles con profundidad y física Box2D más un recorrido
3D guiado. Los reflejos globales están prerenderizados. La validación móvil usa
emulación y multitáctil de Chromium; queda pendiente probar dispositivos físicos
concretos y realizar una revisión artística final por parte del usuario.
No hay casa progresiva, premios comerciales, recogida de datos ni backend.

La ruta utiliza el mismo alojamiento estático GitHub Pages que el resto del
repositorio. No requiere compilación ni servicios externos.

- Juego: `https://cebx3001.github.io/Ferrisariato-/games/pinball/`
- Comparación visual: `https://cebx3001.github.io/Ferrisariato-/games/pinball/docs/precision-comparison.html`

La disponibilidad pública depende de que finalice correctamente el despliegue de Pages de la rama `main`.
