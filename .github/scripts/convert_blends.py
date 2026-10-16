"""Blender 5 headless exporter for user-supplied HOME models.
Called with: blender -b -t 2 --python convert_blends.py -- INPUT.blend OUTPUT.glb PREVIEW.png KEY REPORT.json
"""
import bpy, sys, json, os, math, traceback
from pathlib import Path
from mathutils import Matrix, Vector
args=sys.argv[sys.argv.index('--')+1:]
source, target, thumbnail, key, report_path=args
print('ASSET_START',key,source,flush=True)
if source.lower().endswith('.glb'):
 # Clear Blender startup cube before import; otherwise it becomes part of the product.
 bpy.ops.object.select_all(action='SELECT')
 bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.gltf(filepath=str(Path(source).resolve()))
 if key=='patio':
  for ob in list(bpy.data.objects):
   if ob.type!='MESH':continue
   size=[max(p[i] for p in [ob.matrix_world @ Vector(x) for x in ob.bound_box]) - min(p[i] for p in [ob.matrix_world @ Vector(x) for x in ob.bound_box]) for i in range(3)]
   if ob.name.startswith('Cube') and len(ob.data.polygons)<=12 and all(abs(v-2.0)<0.01 for v in size):
    print('REMOVE_ACCIDENTAL_STARTUP_CUBE',ob.name,flush=True)
    bpy.data.objects.remove(ob,do_unlink=True)
else:
 bpy.ops.wm.open_mainfile(filepath=str(Path(source).resolve()),load_ui=False)
meshes=[o for o in bpy.data.objects if o.type=='MESH' and len(o.data.vertices)>0]
if not meshes: raise RuntimeError('No mesh objects found in '+key)
print('MESHES',len(meshes),'MATERIALS',sum(len(o.data.materials) for o in meshes),flush=True)
# Restore relative image paths; warn for files not packed in the original.
images=[];missing=[]
for im in bpy.data.images:
 if im.source=='FILE':
  packed=bool(im.packed_file)
  disk=os.path.isfile(bpy.path.abspath(im.filepath))
  images.append({'name':im.name,'packed':packed,'on_disk':disk})
  if not packed and not disk: missing.append(im.name)
print('IMAGES',images,'MISSING',missing,flush=True)
# Bounds in scene/world space (the original Blender scene uses Z-up).
pts=[]
for o in meshes:
 for corner in o.bound_box:pts.append(o.matrix_world @ Vector(corner))
mins=[min(p[i] for p in pts) for i in range(3)]
maxs=[max(p[i] for p in pts) for i in range(3)]
orig=[maxs[i]-mins[i] for i in range(3)]
# This scales the complete piece to an appropriate demonstration size, no per-part distortion.
width_m={'umbrella':2.8,'chair':.85,'format1':2.0,'poltrona':1.05,'patio':3.696}[key]
horiz=max(orig[0],orig[1],.0001)
factor=width_m/horiz
center=Vector(((mins[0]+maxs[0])/2,(mins[1]+maxs[1])/2,mins[2]))
normalizer=Matrix.Scale(factor,4) @ Matrix.Translation(-center)
# Parent chains can be present; set from stored matrices to avoid transform propagation twice.
world={o:o.matrix_world.copy() for o in meshes}
for o in meshes: o.parent=None
for o in meshes:
 o.matrix_world=normalizer @ world[o]
 o.hide_viewport=False; o.hide_render=False
for o in bpy.context.selected_objects:o.select_set(False)
for o in meshes:o.select_set(True)
bpy.context.view_layer.objects.active=meshes[0]
width=orig[0]*factor;depth=orig[1]*factor;height=orig[2]*factor
print('DIMENSIONS_METERS',key,width,height,depth,flush=True)
os.makedirs(os.path.dirname(target),exist_ok=True)
# Original node materials and packed textures exported in single self-contained GLB.
bpy.ops.export_scene.gltf(filepath=target,export_format='GLB',use_selection=True,
                          export_yup=True,export_animations=False,
                          export_materials='EXPORT',export_image_format='AUTO')
if not os.path.exists(target) or os.path.getsize(target)<2048 or open(target,'rb').read(4)!=b'glTF':
 raise RuntimeError('Invalid GLB output '+target)
# Preview render using original material appearance, simple product-photography lighting.
try:
 for o in bpy.data.objects:
  if o.type in {'CAMERA','LIGHT'}:o.hide_render=True
 bpy.context.scene.render.engine='CYCLES'
 bpy.context.scene.cycles.samples=16
 bpy.context.scene.render.resolution_x=680; bpy.context.scene.render.resolution_y=540
 bpy.context.scene.render.resolution_percentage=100
 bpy.context.scene.render.film_transparent=True
 look=Vector((0,0,max(height*.40,.20)))
 camdata=bpy.data.cameras.new('Product preview camera');cam=bpy.data.objects.new('Product preview camera',camdata)
 bpy.context.collection.objects.link(cam);bpy.context.scene.camera=cam
 cam.location=(width*1.65,-depth*1.85,height*1.75+.75)
 direction=look-cam.location;cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
 camdata.type='ORTHO';camdata.ortho_scale=max(width,depth,height)*1.7
 def area(name,loc,power,size):
  d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size
  o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o)
  o.location=loc;o.rotation_euler=(look-o.location).to_track_quat('-Z','Y').to_euler()
 area('KEY',(-3,-4,6),1250,6)
 area('FILL',(3,2,4),750,5)
 area('RIM',(0,4,6),950,4)
 bpy.context.scene.view_settings.view_transform='AgX'
 bpy.context.scene.render.image_settings.file_format='PNG';bpy.context.scene.render.filepath=thumbnail
 bpy.ops.render.render(write_still=True)
 print('PREVIEW',thumbnail,os.path.getsize(thumbnail),flush=True)
except Exception as e:
 print('PREVIEW_ERROR',str(e),traceback.format_exc(),flush=True)
record={'key':key,'dimensions':[round(width,4),round(height,4),round(depth,4)],
        'mesh_count':len(meshes),'images':images,'missing_images':missing,
        'glb_bytes':os.path.getsize(target)}
Path(report_path).write_text(json.dumps(record,indent=2))
print('ASSET_SUCCESS',key,flush=True)