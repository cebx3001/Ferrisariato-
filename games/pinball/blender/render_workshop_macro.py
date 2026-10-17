"""Additional workshop closeup. Review camera only; never saved into game scene."""
import bpy,json,sys,os
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;B=Matrix(json.loads((R/'assets/projection.json').read_text())['boardTransform']);original=s.camera
camera=original.copy();camera.data=original.data.copy();camera.name='Workshop review camera only';s.collection.objects.link(camera);s.camera=camera
camera.location=B@Vector((5.5-5,8-11.0,5.8));target=B@Vector((8.25-5,8-8.45,.65));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=48;camera.data.shift_x=0;camera.data.shift_y=0
sys.argv=['blender','--','macro-tools'];os.environ['PINBALL_SAMPLES']='32'
exec(compile((R/'blender/render_precision.py').read_text(),str(R/'blender/render_precision.py'),'exec'),{'__file__':str(R/'blender/render_precision.py')})
s.camera=original
