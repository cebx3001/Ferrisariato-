"""Tiny same-camera corrections for the closed supports added during review."""
import bpy,os,sys,json,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;work=Path('/tmp/reference-support-patches');work.mkdir(exist_ok=True);manifest=[]
for w,h in [(1320,1980),(1760,2640)]:
 s.render.resolution_x=w;s.render.resolution_y=h;s.render.resolution_percentage=100;bpy.context.view_layer.update()
 for side in ['left','right']:
  uv=[world_to_camera_view(s,s.camera,o.matrix_world@Vector(v)) for o in s.objects if o.get('support_side')==side for v in o.bound_box]
  x0=max(0,int(min(v.x for v in uv)*w)-24);x1=min(w,math.ceil(max(v.x for v in uv)*w)+24);y0=max(0,int(min(v.y for v in uv)*h)-24);y1=min(h,math.ceil(max(v.y for v in uv)*h)+24)
  key=f'detail-support-{w}-{side}';os.environ['PINBALL_DETAIL_BORDER']=','.join(map(str,[x0/w,y0/h,x1/w,y1/h]));os.environ['PINBALL_OUTPUT_WIDTH']=str(w);os.environ['PINBALL_OUTPUT_HEIGHT']=str(h);os.environ['PINBALL_DOCUMENT_STAGE']=str(work);os.environ['PINBALL_SAMPLES']='64';sys.argv=['blender','--',key]
  exec(compile((R/'blender/render_precision.py').read_text(),str(R/'blender/render_precision.py'),'exec'),{'__file__':str(R/'blender/render_precision.py')})
  manifest.append({'width':w,'height':h,'x':int(s.render.border_min_x*w),'y':h-int(s.render.border_max_y*h),'file':'precision-'+key+'.png'})
(work/'manifest.json').write_text(json.dumps(manifest,indent=2))
