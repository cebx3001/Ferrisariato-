"""Remove legacy flipper hardware left in the movable collection by earlier passes."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;dynamic=bpy.data.collections['Movable elements']
removed=[]
for o in list(dynamic.objects):
 if o.name.startswith('Premium /'):
  removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
p=bpy.data.materials['Reference V5 / cobalt lacquer'].node_tree.nodes.get('Principled BSDF');p.inputs['Coat Roughness'].default_value=.12
s['reference_components_complete']='5.2';bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/ferrisariato-precision.blend'))
print('REMOVED_LEGACY_FLIPPER_HARDWARE',removed)
