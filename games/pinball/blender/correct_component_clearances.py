"""Correct the exact floor/channel intrusions found during the V5 mesh audit."""
import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;B=Matrix(json.loads((R/'assets/projection.json').read_text())['boardTransform'])
if not s.get('reference_clearance_corrected'):
 for o in s.objects:
  a=o.get('reference_asset','');delta=Vector((0,0,0))
  if a=='right power tools':delta.x=.09
  if a=='left rear masonry 4.25':delta.x=-.23
  if a=='rear corner miniature plants':
   c=B.inverted()@o.matrix_world.translation
   # Rear-right high crown must sit beyond the channel's outer edge.
   if c.x+5>7 and 8-c.y<1.5:delta=Vector((.43,.18,0))
  if delta.length:o.location+=B.to_3x3()@delta
  if any(n in o.name for n in ['rounded yellow shell','molded yellow body','sculpted motor shell','separate lid']):
   for m in o.modifiers:
    if m.type=='BEVEL':m.width=.045;m.segments=5
 s['reference_clearance_corrected']=True
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/ferrisariato-precision.blend'))
