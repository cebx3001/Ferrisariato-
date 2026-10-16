"""Export user supplied Blender files to web-ready GLB using Blender 4.2+ bpy.
Blender embedded Python scripts are not executed on opening files.
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Matrix

sources = {
 'umbrella': 'umbrella.blend',
 'chair': 'chair.blend',
 'format1': 'format1.blend',
 'poltrona': 'poltrona.blend',
}
source_dir = Path('/tmp/ferri-home-blend')
dest_dir = Path('home/assets/models/new')
dest_dir.mkdir(parents=True, exist_ok=True)
meta={}
for name,filename in sources.items():
    path=source_dir/filename
    print(f'\n--- Processing {name}: {path} ---',flush=True)
    bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False, use_scripts=False)
    scene=bpy.context.scene
    bpy.context.view_layer.update()
    objs=[o for o in scene.objects if o.type=='MESH' and not o.hide_render]
    if not objs: raise RuntimeError('No visible meshes in '+name)
    missing=[]
    for im in bpy.data.images:
        if im.source=='FILE' and not im.packed_file and im.filepath:
            f=Path(bpy.path.abspath(im.filepath))
            if not f.exists(): missing.append(im.name+' -> '+str(f))
    if missing: print('MISSING_IMAGES:', '\n'.join(missing[:30]),flush=True)
    # Blender is Z-up; glTF exporter handles conversion to Y-up.
    coords=[]
    for ob in objs:
        for corner in ob.bound_box:
            coords.append(ob.matrix_world @ __import__('mathutils').Vector(corner))
    lo=[min(p[i] for p in coords) for i in range(3)]
    hi=[max(p[i] for p in coords) for i in range(3)]
    dims=[hi[i]-lo[i] for i in range(3)]
    # Normalize scene to real-world scale: do not distort relative dimensions.
    # The originals can use centimeters/millimeters; ensure a plausible furniture footprint.
    span=max(dims)
    factor = (3.0/span if span>10 else (0.01 if span>5 and span<10 and False else 1.0))
    # For models already in meters, do not force arbitrary rescaling unless enormous/tiny.
    if span>10: factor=3.0/span
    elif span<0.15: factor=1.5/max(span,1e-5)
    else: factor=1.0
    center=[(lo[0]+hi[0])/2,(lo[1]+hi[1])/2,lo[2]]
    transform=Matrix.Scale(factor,4) @ Matrix.Translation((-center[0],-center[1],-center[2]))
    # Applying the same left multiplication to root matrices retains child hierarchy.
    roots=[ob for ob in scene.objects if ob.parent is None]
    for ob in roots: ob.matrix_world=transform @ ob.matrix_world
    bpy.context.view_layer.update()
    bpy.ops.object.select_all(action='DESELECT')
    for ob in scene.objects:
        if ob.type in {'MESH','EMPTY'} and (ob.type!='MESH' or not ob.hide_render): ob.select_set(True)
    if objs: bpy.context.view_layer.objects.active=objs[0]
    dest=dest_dir/(name+'.glb')
    bpy.ops.export_scene.gltf(filepath=str(dest.resolve()),export_format='GLB',export_yup=True,
       use_selection=True,export_image_format='AUTO',export_materials='EXPORT',export_cameras=False,
       export_lights=False)
    b=dest.read_bytes()
    if b[:4]!=b'glTF' or len(b)<500: raise RuntimeError('Invalid GLB '+name)
    result_dims=[round(v*factor,3) for v in dims]
    meta[name]={'dimensions_xyz_blender':result_dims,'meshes':len(objs),
       'materials':len(bpy.data.materials),'images':len(bpy.data.images),
       'missing_images':missing,'size_bytes':len(b)}
    print('SAVED',str(dest),'size',len(b),'dims',result_dims,'materials',len(bpy.data.materials),'missing',len(missing),flush=True)
(dest_dir/'report.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
print('CONVERSION COMPLETE',json.dumps(meta,ensure_ascii=False))