# Ferrisariato · HOME / Visualiza en tu espacio

Proyecto WebAR responsive de una sola web. **Entrega de desarrollo para desplegar e integrar**, no una aplicación instalada ni un render estático.

## Qué implementa

- Catálogo HOME: **juego de patio con sombrilla (mesa y 4 sillas)**, **grill** y **lámpara de pie**.
- Logotipo corporativo oficial con eslogan, extraído del manual facilitado por el cliente. No se sustituye por símbolos ajenos.
- Escena 3D con **PlayCanvas** y carga de modelos `.glb`, GLB local de respaldo para cada producto y opciones de modelos CC0 externos, cuando sean accesibles.
- Controles: elegir, colocar, mover (en preview), rotar, restaurar escala real, ajustar escala, quitar, marcar favoritos localmente.
- Modo **vista 3D en computadora** con cámara orbital; modo **AR con cámara real** mediante WebXR, hit testing sobre superficies reales y anclajes cuando estén disponibles.
- UI responsive, guía de uso y estados de carga/error explícitos.
- Catálogo referencial, sin precios, sin SKUs reales ni inventar integración comercial.

## Ejecutar

Abrir la **carpeta publicada**, no el archivo con protocolo `file://`. Puedes alojar la carpeta directamente en GitHub Pages (usa la raíz con `index.html`). Para probar localmente usa:

```bash
python -m http.server 8080
```

Visita `http://localhost:8080/` en escritorio. **Para AR real en teléfono se necesita HTTPS**, cámara permitida y navegador/dispositivo compatible WebXR/ARCore, habitualmente Android + Chrome. En iPhone esta versión no tiene aún tracking AR nativo: la UI indica falta de soporte y permite usar la vista 3D, si la dependencia del motor se carga.

PlayCanvas engine se importa desde un CDN en `js/scene.js`; se necesita conexión de red al CDN en el primer acceso. La app carga modelos GLB locales siempre que sea posible; para el patio y la lámpara intenta elevar la fidelidad con GLB externos CC0 provenientes de 3DAssets.dev cuando CORS lo permite. **Si la CDN remota no funciona, conserva el modelo local**.

## Fuentes 3D, licencias y alcance

| Producto | Fuente externa localizada y licencia | Lo incluido en esta entrega |
| --- | --- | --- |
| Patio, mesa + 4 sillas | https://3dassets.dev/assets/garden-centre-and-florist-garden-furniture-set-495897ab · CC0 · 2.5m ancho. GLB público: https://cdn.3dassets.dev/assets/17778/v1/model.glb | `patio-completo.glb` y `sombrilla.glb`, creados para respaldo, con sombrilla, cuatro sillas y mesa |
| Grill gas 3 quemadores | https://www.innerscene.com/tools/library/3d-parts/three-burner-gas-grill-with-hood-c477660a · CC0 · 1.46m ancho. **Archivo de terceros no descargado en esta sesión** | `grill-premium.glb` generado localmente para el demo |
| Lámpara de pie | https://3dassets.dev/assets/bedroom-and-living-room-furniture-floor-lamp-drum-eb15aef6 · CC0 · 1.63 m. GLB público: https://cdn.3dassets.dev/assets/38796/v1/model.glb | `lampara-de-pie.glb` creado para respaldo |

**Nota:** Estos tres son **modelos de demostración**, no productos ni modelos de catálogo oficial Ferrisariato. Algunos recursos de terceros son modelados por herramientas de IA (declaración de sus autores); la licencia indicada por las páginas es CC0. Las fuentes están documentadas para sustituir/validar activos antes de una campaña comercial.

## Arquitectura

- `index.html`: HTML y estados de UI.
- `css/app.css`: responsive Ferrisariato.
- `js/products.js`: datos de catálogo y modelo local/remoto.
- `js/scene.js`: motor PlayCanvas, carga GLB, escena y WebXR.
- `js/app.js`: controles, cambios de productos, estados de AR y favoritos.
- `assets/models/`: 4 modelos locales GLB válidos, en metros +Y arriba.
- `make_models.py`: script reproducible que construye modelos GLB locales mediante `trimesh`.
- `preview-interfaz.html`: **vista previa independiente de interfaz y catálogo**, sin motor 3D ni tracking de cámara. No debe presentarse como AR real.

## Calidad y validaciones pendientes

Se comprobó con análisis sintáctico Node, verificación de GLB con `trimesh`, y pruebas de interacción HTML responsive mediante Chromium/Playwright para el catálogo. **No se pudo ejecutar PlayCanvas ni pruebas AR en un dispositivo físico en este entorno**. Por tanto, hit test, anclaje, tamaño de modelos externos, tratamiento de la transparencia de cámara, orientación inicial y FPS requieren QA en teléfono real antes de presentar una versión final al cliente.

La colocación sobre planos reconocidos no reconstruye paredes ni oclusiones. Escala real corresponde a **100 %**, con medidas referenciales del activo 3D, no a dimensiones de SKU comercial.

El fallback 8th Wall depende del motor/versión y recursos del repositorio WebAR anterior. **Esta entrega implementa PlayCanvas/WebXR como primera ruta, y no simula un fallback de 8th Wall que todavía no se ha integrado.**
