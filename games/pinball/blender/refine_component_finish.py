"""Review pass over V5: visible floor reflections and populated rear terraces."""
import bpy,math,json
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;B=Matrix(json.loads((R/'assets/projection.json').read_text())['boardTransform'])
f=bpy.data.materials['Mineral concrete'];p=f.node_tree.nodes.get('Principled BSDF');p.inputs['Coat Weight'].default_value=1;p.inputs['Coat Roughness'].default_value=.045;p.inputs['IOR'].default_value=1.5
for n in f.node_tree.nodes:
 if n.type=='BUMP':n.inputs['Strength'].default_value=.035;n.inputs['Distance'].default_value=.0015
 if n.type=='VALTORGB':
  for e in n.color_ramp.elements:e.color=(.055+.045*e.position,)*3+(1,)
for o in s.objects:
 if o.type=='LIGHT' and o.name.startswith('Reference V5 / front strip'):o.data.energy=55
# Reuse the editable V5 leaf/pot geometry in additional shoulder/back-corner groups.
source=[o for o in s.objects if o.get('reference_asset')=='left lower workshop' and '/ garden /' in o.name]
# Group is built from individual linked leaves, soil and a hollow planter, not a blob.
for x,y,z,scale in [(1.0,.65,1.35,1.15),(8.15,.65,1.55,1.10),(1.10,3.8,.48,.75),(8.15,3.8,.65,.75)]:
 old=Vector((.94-5,8-13.25,.03));new=Vector((x-5,8-y,z));T=B@Matrix.Translation(new)@Matrix.Diagonal((scale,scale,scale,1))@Matrix.Translation(-old)@B.inverted()
 for original in source:
  o=original.copy();o.data=original.data;o.name='Reference V5 / rear terrace / '+original.name.split(' / ',1)[-1];bpy.data.collections['Reference V5 / workshop assets'].objects.link(o);o.matrix_world=T@original.matrix_world;o['reference_asset']='rear corner miniature plants'
# Warm pools light the adjacent floor and vertical prop faces, physically.
for x in [1.48,7.89]:
 for y in [5.1,7.9,10.8,13.35]:
  d=bpy.data.lights.new('Reference V5 / workshop warm accent','POINT');d.energy=2.8;d.color=(1,.53,.08);d.shadow_soft_size=.06;o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=B@Vector((x-5,8-y,.46))
s['reference_finish_pass']='5.1 / reflective floor and rear terrace planting'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/ferrisariato-precision.blend'))
