"""Extend the two outer rear terraces beneath their high planter/crate groups."""
import bpy,json,bmesh
from mathutils import Matrix
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;B=Matrix(json.loads((R/'assets/projection.json').read_text())['boardTransform']);c=bpy.data.collections['Reference V5 / workshop assets']
for o in list(s.objects):
 if o.name.startswith('Reference V5 / canopy terrace support'):bpy.data.objects.remove(o,do_unlink=True)
for side,x,y,h in [('left',.42,1.9,.86),('right',9.2,1.3,.78)]:
 for suffix,w,d,z,depth,material in [('closed pedestal',.46,.54,h/2,h,'Reference V5 / cobalt lacquer'),('capped top slab',.50,.58,h-.025,.05,'Rough concrete blocks')]:
  bm=bmesh.new();bmesh.ops.create_cube(bm,size=1)
  for v in bm.verts:v.co.x*=w;v.co.y*=d;v.co.z*=depth
  me=bpy.data.meshes.new('Closed terrace');bm.to_mesh(me);bm.free();me.materials.append(bpy.data.materials[material]);o=bpy.data.objects.new('Reference V5 / canopy terrace support / '+side+' / '+suffix,me);c.objects.link(o);o.matrix_world=B@Matrix.Translation((x-5,8-y,z));o['reference_asset']='rear canopy structural terrace';o['support_side']=side;m=o.modifiers.new('Machined edge','BEVEL');m.width=.018;m.segments=3
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/ferrisariato-precision.blend'))
