"""Rebuild table materials from original 10-mesh CGTrader geometry already in Git history.
The user's completed Work deliverable used exactly this seeded wood PBR technique.
The original FBX (user Library) was the source; the historical GLB retains its geometry.
"""
import bpy, math, json, numpy as np
from mathutils import Vector, Matrix
from pathlib import Path
import sys
old=Path(sys.argv[-2]); dest=Path(sys.argv[-1])
dest.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(old.resolve()))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
print("INPUT_MESHES",[(o.name,len(o.data.vertices),[m.name for m in o.data.materials]) for o in meshes],flush=True)
if len(meshes)!=10: raise RuntimeError(f"Expected 10 table/chair meshes, got {len(meshes)}")
# Wood color reproduction, following the completed Work Blender script.
n=1024;rng=np.random.default_rng(48);x=np.arange(n)[None,:];y=np.arange(n)[:,None]
a=np.zeros((n,n),dtype=np.float64)
for i in range(1,55):
 a+=np.sin(x*(i*.027)+rng.uniform(0,6.28)+np.sin(y*.005+i)*(.5+2/i))*(.022/(i**.5))
a+=rng.normal(0,.007,(n,n));a+=.014*np.sin(y*.007+x*.03)
base=np.array([.29,.225,.16]);rgb=np.clip(base[None,None,:]+a[:,:,None],0,1)
img=bpy.data.images.new('Madera_veta_basecolor',width=n,height=n)
rgba=np.concatenate([rgb,np.ones((n,n,1))],axis=2).astype(np.float32)
img.pixels.foreach_set(rgba.ravel());img.filepath_raw=str((dest/'wood_basecolor.png').resolve());img.file_format='PNG';img.save()
def mat(name):
 m=bpy.data.materials.new(name);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF')
 return m,bs
wood,wb=mat('Madera_natural_veteada');wb.inputs['Roughness'].default_value=.58
tex=wood.node_tree.nodes.new('ShaderNodeTexImage');tex.image=img
wood.node_tree.links.new(tex.outputs['Color'],wb.inputs['Base Color'])
metal,mb=mat('Aluminio_claro_satinado')
mb.inputs['Base Color'].default_value=(.68,.71,.72,1);mb.inputs['Metallic'].default_value=.88;mb.inputs['Roughness'].default_value=.29
counts={'wood':0,'metal':0}
for o in meshes:
 existing=[m.name for m in o.data.materials if m]
 ids=[int(m.split('_')[-1]) for m in existing if m.startswith('mesh_') and m.split('_')[-1].isdigit()]
 if len(ids)!=1: raise RuntimeError(f"Unknown old material slots {o.name}: {existing}")
 kind='wood' if ids[0]<5 else 'metal'
 counts[kind]+=1
 for i in range(len(o.data.materials)):o.data.materials[i]=wood if kind=='wood' else metal
 if kind=='wood':
  uv=o.data.uv_layers.active or o.data.uv_layers.new(name='WoodUV')
  # Remap grain per separated connected component, matching successful Work script.
  parent=list(range(len(o.data.vertices)))
  def root(v):
   while parent[v]!=v:
    parent[v]=parent[parent[v]];v=parent[v]
   return v
  for poly in o.data.polygons:
   vv=list(poly.vertices)
   for v in vv[1:]:parent[root(v)]=root(vv[0])
  groups={}
  for poly in o.data.polygons:groups.setdefault(root(poly.vertices[0]),[]).append(poly)
  for ci,polys in enumerate(groups.values()):
   vi=set(v for p in polys for v in p.vertices)
   coords=[o.data.vertices[v].co for v in vi]
   lo=[min(v[k] for v in coords) for k in range(3)]
   hi=[max(v[k] for v in coords) for k in range(3)]
   axes=sorted(range(3),key=lambda k:hi[k]-lo[k],reverse=True)
   longest,widest=axes[:2]
   scale=o.matrix_world.to_scale()
   for poly in polys:
    for li in poly.loop_indices:
     co=o.data.vertices[o.data.loops[li].vertex_index].co
     uv.data[li].uv=((co[widest]-lo[widest])*abs(scale[widest])*5+ci*.137,
                      (co[longest]-lo[longest])*abs(scale[longest])*.5+ci*.317)
print("ASSIGNMENTS",counts,flush=True)
if counts!={'wood':5,'metal':5}:raise RuntimeError("Table materials must have five wood and five metal meshes")
# The historical GLB used a pre-Work orientation (y-axis was depth).
# Apply identical -90° X corrective rotation previously present in home/js/scene.js.
rotation=Matrix.Rotation(-math.pi/2,4,'X')
for o in meshes:o.matrix_world=rotation @ o.matrix_world
bpy.context.view_layer.update()
verts=[o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
mn=Vector([min(v[i] for v in verts) for i in range(3)])
mx=Vector([max(v[i] for v in verts) for i in range(3)])
trans=Matrix.Translation(Vector((-(mn.x+mx.x)*.5,-(mn.y+mx.y)*.5,-mn.z)))
for o in meshes:o.matrix_world=trans @ o.matrix_world
bpy.context.view_layer.update()
verts=[o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
mn=Vector([min(v[i] for v in verts) for i in range(3)])
mx=Vector([max(v[i] for v in verts) for i in range(3)])
dims=[round(mx.x-mn.x,4),round(mx.z-mn.z,4),round(mx.y-mn.y,4)]
print("TABLE_DIMS_W_H_D",dims,flush=True)
if not (1.8<dims[0]<2.25 and .75<dims[1]<1.15 and 2.1<dims[2]<2.65):
 raise RuntimeError(f"Geometry orientation/scale invalid {dims}; do not publish")
for o in bpy.context.selected_objects:o.select_set(False)
for o in meshes:o.select_set(True)
bpy.context.view_layer.objects.active=meshes[0]
output=dest/'outdoor-table-materials.glb'
bpy.ops.export_scene.gltf(filepath=str(output.resolve()),export_format='GLB',
    use_selection=True,export_apply=False,export_yup=True,export_animations=False,
    export_materials='EXPORT',export_image_format='AUTO')
assert output.stat().st_size>400000 and output.read_bytes()[:4]==b'glTF'
print('GLB',output.stat().st_size,flush=True)
# One neutral preview; no unrelated assets exported.
for o in bpy.context.selected_objects:o.select_set(False)
for o in bpy.data.objects:
 if o.type in {'CAMERA','LIGHT'}:o.hide_render=True
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=20
sc.render.resolution_x=720;sc.render.resolution_y=640;sc.render.resolution_percentage=100
sc.render.film_transparent=True;sc.use_nodes=False;sc.view_settings.view_transform='Standard'
qa=bpy.data.worlds.new('NEUTRAL');qa.use_nodes=True
qa.node_tree.nodes['Background'].inputs['Color'].default_value=(.44,.46,.48,1)
qa.node_tree.nodes['Background'].inputs['Strength'].default_value=.4;sc.world=qa
look=Vector((0,0,.40))
camd=bpy.data.cameras.new('Preview Camera');cam=bpy.data.objects.new('Preview Camera',camd)
bpy.context.collection.objects.link(cam);sc.camera=cam
camd.type='ORTHO';camd.ortho_scale=3.65
cam.location=(3.4,-4.3,3.4);cam.rotation_euler=(look-cam.location).to_track_quat('-Z','Y').to_euler()
for pos,power in [((-3,-4,5),650),((3,1,4),400),((1,4,5),450)]:
 ld=bpy.data.lights.new('Area','AREA');ld.energy=power;ld.shape='DISK';ld.size=4.5
 lo=bpy.data.objects.new('Area',ld);bpy.context.collection.objects.link(lo)
 lo.location=pos;lo.rotation_euler=(look-lo.location).to_track_quat('-Z','Y').to_euler()
sc.render.filepath=str((dest/'outdoor-table-preview.png').resolve())
bpy.ops.render.render(write_still=True)
(dest/'table-report.json').write_text(json.dumps({'mesh_count':len(meshes),'materials':counts,'dimensions_w_h_d_m':dims,'bytes':output.stat().st_size},indent=2))
