# Ferrisariato WebAR · integración 8th Wall desde Gaussian-AR

**Referencia concreta:** [`cebx3001/Gaussian-AR`](https://github.com/cebx3001/Gaussian-AR), especialmente `src/ar-page.ts`, `src/ar-cero.ts`, `vite.config.ts` y `package.json`.

## Integración añadida

- Motor: `@8thwall/engine-binary@1.0.0`, versión exacta de Gaussian-AR.
- Render: PlayCanvas `2.22.6`, versión exacta de Gaussian-AR, por CDN ESM.
- Adaptador común: `home/js/xr8-provider.js` y `instore/js/xr8-provider.js` (misma implementación reproducida sin empaquetar el binario en scripts propios).
- Se precarga `/external/xr/xr.js` y SLAM; carga dinámica del paquete original sin modificación. El pipeline usa `XR8.PlayCanvas.runXr({pcCamera, pcApp}, modules, {canvas,...})`.
- `XR8.XrController.configure({disableWorldTracking:false,scale:'responsive'})`. Se evita reiniciar la escala relativa con la cámara en movimiento.
- `hitTest` únicamente en `onUpdate` del módulo cuando `processCpuResult.reality` trae datos: evita consultas prematuras que en Gaussian-AR causaban errores internos. Se prefieren superficies detectadas/estimadas, con `FEATURE_POINT` como respaldo, y filtrado de inclinación cuando la superficie detectada trae orientación.
- Retícula suavizada siguiendo el rayo central al plano horizontal; altura de apoyo por mediana; colocación fija con copia de coordenadas, sin seguimiento posterior de la retícula.
- HOME: en móviles, modo 8th Wall SLAM por defecto tanto en Safari iOS como Chrome Android. Los tres GLB, selector, rotación y escala se conservan. El modo WebXR nativo permanece disponible con `?tracking=native`.
- IN-STORE: mismo método de seguimiento para AR del suelo PISOS, conservando los cuatro acabados y el reveal radial único. El modo WebXR nativo permanece con `?tracking=native`.
- Responsive: el contenido de escritorio continúa como catálogo/visor 3D y simulación; en móvil, la interfaz da acceso a XR Engine con cámara.

## Requisito de publicación del motor binario

El proyecto fuente no almacena una copia de `xr.js`, librerías SLAM ni recursos asociados en este archivo ZIP. El workflow `.github/workflows/sync-xr-engine.yml` instala la dependencia **original** desde npm y copia la carpeta completa del motor a `external/xr/`. Esto sigue el procedimiento de copia intacta usado en `Gaussian-AR/vite.config.ts`. El workflow realiza un commit con esos recursos en la rama `main` para que puedan servirse desde GitHub Pages con publicación basada en rama.

Una vez ejecutado exitosamente, deben existir `external/xr/xr.js` y el resto del runtime completo, además del aviso de licencia correspondiente. Sin ese paso, las páginas continúan sirviendo su UI, pero 8th Wall mostrará un error de motor ausente. **No se afirma que el seguimiento AR esté verificado sin ejecutar pruebas reales en iPhone y Android**.

## Licencia

Aunque el repositorio esté accesible públicamente, el motor se distribuye bajo **XR Engine License Agreement de Niantic Spatial, no una licencia permisiva típica como MIT**. Se respetan las obligaciones de conservar el motor sin cambios, su aviso de copyright y licencia. Fuente: https://github.com/8thwall/engine/blob/main/LICENSE

## Verificación necesaria

1. Comprobar en GitHub Actions que terminó `Sync unmodified XR Engine for static GitHub Pages` y se creó `external/xr/xr.js`.
2. Comprobar que GitHub Pages sirve correctamente `https://cebx3001.github.io/Ferrisariato-/external/xr/xr.js`.
3. Abrir `/home/` y `/instore/?spot=02` desde Safari iPhone y Chrome Android, aceptar permisos y observar la retícula real, la fijación del producto/suelo y la estabilidad al caminar alrededor.
4. Comprobar que las interfaces desktop permanecen navegables y el visor 3D sigue funcional sin iniciar una sesión de cámara.

No se ha creado un tracking AR falso, ni una simulación presentada como seguimiento real.
