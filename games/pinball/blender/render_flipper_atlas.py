"""Render the actual assembled Blender flippers at their motor angles.
Atlas frames use the unchanged game camera; no procedural substitute geometry.
"""
import bpy, math, json, os, subprocess
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;D=json.loads((R/'layout.json').read_text());B=Matrix(json.loads((R/'assets/projection.json').read_text())['boardTransform']);W=880;H=1320
work=Path('/tmp/reference-flippers');work.mkdir(exist_ok=True)
s.render.resolution_x=W;s.render.resolution_y=H;s.render.resolution_percentage=100;s.render.film_transparent=True;s.render.use_persistent_data=True;s.use_nodes=False;s.cycles.samples=int(os.environ.get('FLIPPER_SAMPLES','24'));s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=5
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8'
for c in bpy.data.collections:c.hide_render=False
for o in s.objects:
 if hasattr(o,'visible_camera'):o.visible_camera=False
# Avoid protective-glass bounce/refraction hiding the sprite itself.
bpy.data.collections['Protective glass reflections'].hide_render=True
from bpy_extras.object_utils import world_to_camera_view
manifest={'width':W,'height':H,'source':'Cycles renders of the editable V5 assemblies','frames':{}}
for f in D['flippers']:
 objs=[o for o in s.objects if o.get('flipper_id')==f['id']];orig={o:o.matrix_world.copy() for o in objs}
 for o in objs:o.visible_camera=True
 pivot=Vector((f['x']-5,8-f['y'],0));frames=[]
 # Box2D permits a small angular limit slop. Include that travel visually.
 direction=1 if f['active']>f['rest'] else -1
 angles=[f['rest']-direction*.055+(f['active']-f['rest']+direction*.11)*i/28 for i in range(29)]+[f['rest'],f['active']]
 angles.sort(reverse=direction<0)
 for i,a in enumerate(angles):
  delta=a-f['rest'];T=B@Matrix.Translation(pivot)@Matrix.Rotation(-delta,4,'Z')@Matrix.Translation(-pivot)@B.inverted()
  for o in objs:o.matrix_world=T@orig[o]
  bpy.context.view_layer.update()
  uv=[world_to_camera_view(s,s.camera,o.matrix_world@Vector(v)) for o in objs for v in o.bound_box]
  x0=max(0,int(min(v.x for v in uv)*W)-7);x1=min(W,math.ceil(max(v.x for v in uv)*W)+7)
  y0=max(0,int(min(v.y for v in uv)*H)-7);y1=min(H,math.ceil(max(v.y for v in uv)*H)+7)
  s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=x0/W;s.render.border_max_x=x1/W;s.render.border_min_y=y0/H;s.render.border_max_y=y1/H
  name=f'{f["id"]}-{i:02}.png';s.render.filepath=str(work/name);bpy.ops.render.render(write_still=True)
  frames.append({'angle':a,'file':name,'x':x0,'y':H-y1,'width':x1-x0,'height':y1-y0})
 for o in objs:o.matrix_world=orig[o];o.visible_camera=False
 manifest['frames'][f['id']]=frames
(work/'frames.json').write_text(json.dumps(manifest,indent=2))
print('FLIPPER_FRAMES_READY',flush=True)
