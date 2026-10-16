# Procedencia técnica

Base solicitada: https://github.com/lrusso/Pinball

Commit conservado: `fcf63f97d24467248fe1eaa89adaf273209f3da2`.
`upstream/` contiene todos los archivos originales de ese checkout, sin
modificaciones. No se carga su service worker desde el juego adaptado.

`vendor/box2d.js` conserva el núcleo Box2D del bloque
`box2d-plugin-full.js.js` de `upstream/PinballGame.js`. Se extrae hasta la
primera referencia a `Phaser.` y se termina la expresión con punto y coma.
La extracción evita ejecutar Phaser, los recursos embebidos y la mesa original.
Puede reproducirse con `python3 games/pinball/scripts/extract-engine.py`.

Se reutiliza el mismo motor físico, la bola continua y el patrón del original
de articulaciones revolutas con motor, callbacks de contacto, puntuación y
luces de 200 ms. La adaptación implementa nueva geometría, lanzador con carga,
contador de bolas, temporizador, controles simultáneos, render y audio.
El original documenta a su vez la referencia técnica
https://phaser.io/examples/v2/box2d/pinball.

El checkout original no contiene un archivo LICENSE. Se conserva esta
procedencia sin atribuir una licencia que no consta en él; los derechos de
redistribución para una publicación comercial requieren revisión.

El logotipo procede del recurso oficial ya incluido en el repositorio
Ferrisariato. Se conserva sin modificar, con sus proporciones y transparencia.
Los sonidos del módulo son sintetizados por `src/audio.js`; no se utilizan
los archivos de audio embebidos en el original. Los modelos y materiales de
la nueva mesa se generan con los scripts Blender incluidos.

## Herramientas de render de la iteración fotográfica

Intel Open Image Denoise 2.3.3 (Apache-2.0), descargado desde su release oficial:
https://github.com/RenderKit/oidn/releases/tag/v2.3.3.
OpenEXR 3.5.2 y NumPy 2.5.4 se usan para transferir pases HDR entre Cycles y OIDN.
Son herramientas externas de producción; no se incorporan sus binarios al juego
ni se cargan en el navegador. El script de preparación verifica SHA-256 del
archivo OIDN y mantiene las dependencias en la caché local del entorno.
