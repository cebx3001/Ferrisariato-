"""Fit the official logo to a physical apron, leaving the plunger slot open."""
import bpy,json
from pathlib import Path
from mathutils import Matrix
r=Path(__file__).resolve().parents[1];s=bpy.context.scene
for o in list(s.objects):
 if o.name in ['Bottom apron','Precision / fitted front apron']:bpy.data.objects.remove(o,do_unlink=True)
outline=[(.15,15.42),(8.75,15.42),(8.75,16.58),(9.85,16.58),(9.85,17.04),(.15,17.04)]
me=bpy.data.meshes.new('Fitted apron with launcher recess');me.from_pydata([(x-5,8-y,.37) for x,y in outline],[],[tuple(reversed(range(len(outline))))]);me.materials.append(bpy.data.materials['Ferrisariato cobalt enamel'])
o=bpy.data.objects.new('Precision / fitted front apron',me);bpy.data.collections['Collection'].objects.link(o);o.matrix_world=Matrix(json.loads((r/'assets/projection.json').read_text())['boardTransform'])
o.modifiers.new('Physical panel thickness','SOLIDIFY').thickness=.5;m=o.modifiers.new('Lacquered rounded edges','BEVEL');m.width=.035;m.segments=3
bpy.ops.file.pack_all();bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(r/'blender/ferrisariato-precision.blend'))
