"""Correct the block-like drill silhouette found in the oblique V5 review."""
import bpy,math,bmesh
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;C=bpy.data.collections['Reference V5 / workshop assets'];yellow=bpy.data.materials['Reference V5 / safety yellow lacquer'];black=bpy.data.materials['Reference V5 / rubber'];chrome=bpy.data.materials['Reference V5 / polished chrome']
motors=[o for o in s.objects if '/ drill / sculpted motor shell' in o.name]
for o in list(s.objects):
 if motors and o.name.startswith('Reference V5 / sculpted drill detail'):bpy.data.objects.remove(o,do_unlink=True)
def extrusion(name,outline,y0,y1,m,transform,asset):
 n=len(outline);ps=[(x,y,z) for y in [y0,y1] for x,z in outline];faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];me=bpy.data.meshes.new(name);me.from_pydata(ps,[],faces);me.update();me.materials.append(m);o=bpy.data.objects.new(name,me);C.objects.link(o);o.matrix_world=transform.copy();o['reference_asset']=asset;mod=o.modifiers.new('Injection molded fillet','BEVEL');mod.width=.025;mod.segments=5;o.modifiers.new('Weighted molded normals','WEIGHTED_NORMAL');return o
motors=[o for o in s.objects if '/ drill / sculpted motor shell' in o.name]
for motor in motors:
 asset=motor.get('reference_asset');parts=[o for o in s.objects if o.get('reference_asset')==asset and '/ drill /' in o.name];group='drill-left' if asset.startswith('DENSE') else 'drill-right'
 for o in parts:o['review_patch_group']=group
 T=motor.matrix_world.copy()
 # Rounded shoulder, sloped nose and swept lower contour replace the cuboid.
 outline=[(-.30,-.065),(-.30,.065),(-.23,.14),(-.10,.17),(.18,.145),(.285,.075),(.285,-.075),(.17,-.13),(.015,-.12),(-.11,-.065)]
 new=extrusion('Reference V5 / sculpted drill detail / motor shell',outline,-.155,.155,yellow,T,asset);new['review_patch_group']=group
 for side in [-1,1]:
  panel=[(.015,-.070),(.17,-.105),(.253,-.052),(.255,.055),(.16,.12),(.015,.113)]
  new=extrusion('Reference V5 / sculpted drill detail / black casing inlay',panel,side*.158-.005,side*.158+.005,black,T,asset);new['review_patch_group']=group
 grip=next(o for o in parts if 'molded pistol grip' in o.name);G=grip.matrix_world.copy()
 outline=[(-.105,-.20),(.065,-.20),(.14,.16),(.07,.235),(-.09,.22),(-.115,.10),(-.055,-.025)]
 new=extrusion('Reference V5 / sculpted drill detail / angled pistol grip',outline,-.105,.105,yellow,G,asset);new['review_patch_group']=group
 backstrap=[(.025,-.20),(.066,-.20),(.14,.16),(.10,.205),(.065,.14)]
 new=extrusion('Reference V5 / sculpted drill detail / rubber backstrap',backstrap,-.115,.115,black,G,asset);new['review_patch_group']=group
 for i in range(7):
  zz=-.145+i*.043;xx=.045+(zz+.145)*.20
  new=extrusion('Reference V5 / sculpted drill detail / molded grip rib',[(xx-.07,zz),(xx+.035,zz),(xx+.035,zz+.014),(xx-.07,zz+.014)],-.12,-.106,black,G,asset);new['review_patch_group']=group
 # Two helical cutting edges make the bit read as a drill bit, not a rod.
 for phase in [0,math.pi]:
  cu=bpy.data.curves.new('Helical drill flute','CURVE');cu.dimensions='3D';cu.bevel_depth=.004;cu.bevel_resolution=2;sp=cu.splines.new('POLY');sp.points.add(48)
  for j,v in enumerate(sp.points):a=j/48*math.tau*3+phase;v.co=(-.51-j/48*.20,.017*math.cos(a),.017*math.sin(a),1)
  cu.materials.append(chrome);o=bpy.data.objects.new('Reference V5 / sculpted drill detail / helical bit',cu);C.objects.link(o);o.matrix_world=T;o['reference_asset']=asset;o['review_patch_group']=group
 for o in parts:
  if any(n in o.name for n in ['sculpted motor shell','molded pistol grip','rubber grip backstrap','embossed grip ribs']):bpy.data.objects.remove(o,do_unlink=True)
 # Keep casing screws and vents, which now sit in the black side inlay.
s['sculpted_drill_review']='5.4';bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/ferrisariato-precision.blend'))
print('SCULPTED_DRILLS',len(motors))
