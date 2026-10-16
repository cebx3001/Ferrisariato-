# Revisión de fidelidad visual

Referencia: infografía Ferrisariato aportada en el chat. Se distinguen el
arte de la mesa y los cuadros explicativos superpuestos: estos últimos no
forman parte del juego. No se recibió otra imagen final distinta.

La primera pasada era demasiado simple: plantas redondeadas, cajas macizas,
una carretilla esquemática, bloques sin huecos y ausencia de pallets y cinta
métrica. La pasada ampliada sustituye esos elementos por los modelos
modulares de `blender/props.py`, sin añadir colisiones decorativas.

| Zona de la referencia | Objetos identificados y reproducidos | Corrección aplicada |
| --- | --- | --- |
| Fondo central | Casa con tejado azul, cumbrera, puerta, dos ventanas cálidas, escalón, dos jardineras, cerca blanca y cartel oficial | Juntas del tejado, paneles de puerta, pomo, travesaños y coronas de los postes |
| Jardín posterior | Dos palmeras pequeñas a ambos lados de la casa | Troncos segmentados, diez frondas curvas por palmera y folíolos individuales |
| Posterior izquierda | Bloques huecos apilados sobre pallet y planta en maceta | Tres bloques ensamblados con paredes y almas reales; suelo y hojas plegadas |
| Posterior derecha | Recipiente de pintura azul/blanco, maceta y soporte de madera | Cubo con tapa, reborde, asa de alambre y etiqueta; pallet de listones |
| Lateral medio izquierdo | Tablones apilados, planta, ladrillos, caja, caja de herramientas azul y cinta métrica amarilla | Veta, flejes, ladrillos biselados, caja de listones, cinta con graduaciones y gancho |
| Lateral medio derecho | Dos recipientes de pintura, caja de cartón, taladro amarillo y caja de madera | Taladro con batería, gatillo, agarre, ventilación, mandril y broca; cajas con rótulos |
| Inferior izquierda | Segunda pila de ladrillos, planta, caja amarilla sobre pallet y recipiente gris/blanco | Cierres, asa, nervaduras, listones, clavos y cubo con asa |
| Inferior derecha | Carretilla azul con grava, bloques de cemento y cono naranja | Bandeja abierta, rueda con buje, patas, mangos, 95 piedras; cuatro bloques huecos; bandas reflectantes |
| Bordes y canales | Dos canales elevados curvos, paredes transparentes, barandas, postes y apoyos | Acrílico separado del fondo azul, doble pasamanos, abrazaderas doradas, pies, tornillos y bombillas |
| Superficie | Flechas azules y amarillas, franjas de advertencia y medallón central de casa | Textura mineral editable, bases hexagonales de los bumpers y señalética proyectada |
| Siete módulos | Construcción, herramientas, pintura, electricidad, plomería, jardín y hogar | Paneles individuales con tornillos, icono y lámpara independiente |
| Frente | Paletas, resorte del lanzador, faldón azul y marca oficial | Cápsulas móviles alineadas al motor, resorte que se comprime y logotipo original con alfa |

Hay ocho conjuntos de soporte tipo pallet, dos cajas de madera, dos pilas
de ladrillos, una pila de tablones, cuatro cubos decorativos de pintura
además de los dos bumpers cilíndricos, cuatro macetas ornamentales y dos
palmeras. Las partes repetidas de pallets, ladrillos y tablones comparten
datos de malla. `assets/scene-inventory.json` registra los nombres y el
recuento real de objetos generado por Blender para auditar la escena.

La posición y escala se ajustan por zonas visibles de la infografía; sus
oclusiones no permiten reconstruir dimensiones ni cantidades ocultas con
exactitud. El resultado es una reconstrucción tridimensional para esta
prueba de concepto, no una afirmación de coincidencia píxel a píxel ni de
aprobación final de arte. Los PNG de trabajo permiten inspeccionar los
detalles a resolución completa y el `.blend` conserva todas las piezas.

La física se conserva al ampliar el decorado. Solo se ajustó en
`layout.json` la disposición de los bumpers para dejar el espacio central
que muestra la referencia; el render y los colliders leen esas mismas
coordenadas. Las pruebas de lanzamiento, contactos, paletas, puntuación y
tiempo se repiten después de ese ajuste.

En la comparación del render compuesto se detectó que los canales ocultaban
demasiado el taladro y la caja amarilla inferior. Se ajustaron sus recorridos
y extremos, conservando canaletas, acrílico, flechas, soportes y barandas,
para volver a dejar visibles esos objetos. También se elevaron las tapas
azules de los tanques por encima del borde de sus cuerpos y se retiró el
botón táctil de encima del resorte del lanzador.
