# Modelos enviados / Ferrisariato HOME
Se incorporan los modelos GLB convertidos desde los archivos recibidos:
- `SOFAOUTDOOR.3ds` -> `sofa-exterior-original.glb`
- `umbrella (1).obj` -> `sombrilla-original.glb`
- `Sunray_Daybed_By_Minotti__corona.obj` -> `sunray-daybed-original.glb`
- `Outdoor_table.FBX` -> `mesa-exterior-original.glb`
- `mangal.rar` (contenía FBX) -> `parrilla-original.glb`

Son los modelos originales convertidos, con geometría y materiales provisionales disponibles. No se reemplazaron por formas genéricas. Las dimensiones son las que resultaron de convertir los archivos y deben validarse visualmente. Las texturas faltantes en los archivos fuente no se inventaron. La Reposera Beach sigue sin GLB y por eso permanece como fotografía.

Los modelos grandes se almacenan como gzip y GitHub Actions los extrae a GLB para servirlos por GitHub Pages. Para comprobar que HOME ya muestra los cinco, verificar la ejecución `Unpack HOME customer GLB assets`. El seguimiento AR no cambia: Android con ARCore/WebXR prioritario, 8th Wall alternativo, iPhone 8th Wall.
