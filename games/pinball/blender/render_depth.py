"""Opaque scene depth for the live ball, exported from the exact render camera."""
import bpy,subprocess,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];s=bpy.context.scene
bpy.data.collections['Movable elements'].hide_render=True
bpy.data.collections['Protective glass reflections'].hide_render=True
for o in s.objects:
 if hasattr(o.data,'materials') and any(m and m.name in ['Clear acrylic channel walls','Translucent elevated ramp'] for m in o.data.materials):o.hide_render=True
s.render.resolution_x=880;s.render.resolution_y=1320;s.render.resolution_percentage=100
s.cycles.samples=1;s.cycles.use_denoising=False;s.use_nodes=False;s.view_layers[0].use_pass_z=True
s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';s.render.image_settings.color_depth='32';s.render.filepath='/tmp/precision-depth.exr'
bpy.ops.render.render(write_still=True)
env=os.environ.copy();env['PYTHONPATH']='/workspace/.cache/ferrisariato-python'
subprocess.run(['python3',str(ROOT/'scripts/pack-depth.py'),s.render.filepath,str(ROOT/'assets/depth.png')],env=env,check=True)
