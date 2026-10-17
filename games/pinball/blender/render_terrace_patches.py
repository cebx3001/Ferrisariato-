"""Same-camera regional re-renders of the exposed rear terrace micro-scenes."""
import bpy,os,sys,json,math
from pathlib import Path
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;work=Path('/tmp/reference-terrace-patches');work.mkdir(exist_ok=True);manifest=[];original=s.camera
for w,h,groups in [(1320,1980,['terrace-right-upper','terrace-right-lower','terrace-left-workshop']),(1760,2640,['terrace-right-upper','terrace-right-lower','terrace-left-workshop'])]:
 if w==720:
  B=Matrix(json.loads((R/'assets/projection.json').read_text())['boardTransform']);camera=original.copy();camera.data=original.data.copy();s.collection.objects.link(camera);s.camera=camera;camera.location=B@Vector((.5,-3,5.8));target=B@Vector((3.25,-.45,.65));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=48;camera.data.shift_x=0;camera.data.shift_y=0
 s.render.resolution_x=w;s.render.resolution_y=h;s.render.resolution_percentage=100;bpy.context.view_layer.update()
 for group in groups:
  uv=[world_to_camera_view(s,s.camera,o.matrix_world@Vector(v)) for o in s.objects if o.get('review_patch_group')==group for v in o.bound_box]
  x0=max(0,int(min(v.x for v in uv)*w)-28);x1=min(w,math.ceil(max(v.x for v in uv)*w)+28);y0=max(0,int(min(v.y for v in uv)*h)-28);y1=min(h,math.ceil(max(v.y for v in uv)*h)+28)
  key=f'detail-{group}-{w}';os.environ['PINBALL_DETAIL_BORDER']=','.join(map(str,[x0/w,y0/h,x1/w,y1/h]));os.environ['PINBALL_OUTPUT_WIDTH']=str(w);os.environ['PINBALL_OUTPUT_HEIGHT']=str(h);os.environ['PINBALL_DOCUMENT_STAGE']=str(work);os.environ['PINBALL_SAMPLES']='64';sys.argv=['blender','--',key]
  exec(compile((R/'blender/render_precision.py').read_text(),str(R/'blender/render_precision.py'),'exec'),{'__file__':str(R/'blender/render_precision.py')})
  manifest.append({'width':w,'height':h,'x':int(s.render.border_min_x*w),'y':h-int(s.render.border_max_y*h),'file':'precision-'+key+'.png'})
 s.camera=original
(work/'manifest.json').write_text(json.dumps(manifest,indent=2))
