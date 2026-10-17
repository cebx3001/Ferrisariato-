"""Physical warm illumination for the newly occupied workshop pockets."""
import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.context.scene
for o in s.objects:
 if o.type=='LIGHT':
  if o.name.startswith('Reference V5 / workshop warm accent'):o.data.energy=5.0
  elif o.name.startswith('Practical / side rail incandescent'):o.data.energy=5.0
  elif o.name.startswith('Single channel / physical LED'):o.data.energy=1.8
  elif o.name.startswith('Practical / floor insert'):o.data.energy=4.0
 if not s.get('dense_lighting_5_3') and o.type=='MESH' and o.name.startswith(('Lamp / amber glass envelope','Single channel / miniature LED')):o.scale*=1.28
s['dense_lighting_5_3']=True
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/ferrisariato-precision.blend'))
