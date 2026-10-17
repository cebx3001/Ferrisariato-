"""Tightly interlocked construction micro-scenes, outside every playable corridor.
Adds recognizable assets on pallets, crates and terraces, with staggered heights.
"""
import bpy,math,json,random,bmesh,ast
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;board=Matrix(json.loads((R/'assets/projection.json').read_text())['boardTransform']);B=board
coll=bpy.data.collections['Reference V5 / workshop assets'];cache={};made=[];asset=None
blue=bpy.data.materials['Reference V5 / cobalt lacquer'];yellow=bpy.data.materials['Reference V5 / safety yellow lacquer'];black=bpy.data.materials['Reference V5 / rubber'];chrome=bpy.data.materials['Reference V5 / polished chrome'];dark=bpy.data.materials['Reference V5 / dark steel'];white=bpy.data.materials['Reference V5 / white molded cap'];orange=bpy.data.materials['Reference V5 / cone orange'];wood=bpy.data.materials['Cut pine'];terra=bpy.data.materials['Terracotta'];concrete=bpy.data.materials['Rough concrete blocks'];soil=bpy.data.materials['Potting soil'];leaves=[bpy.data.materials['Reference V5 / leaf '+str(i)] for i in range(4)]
for node in ast.parse((R/'blender/reference_components.py').read_text()).body:
 if isinstance(node,ast.FunctionDef):exec(compile(ast.Module(body=[node],type_ignores=[]),'reference asset library','exec'))
random.seed(43994)
# Rerunning this density pass replaces only its own additions.
for o in list(s.objects):
 if str(o.get('reference_asset','')).startswith('DENSE /'):bpy.data.objects.remove(o,do_unlink=True)
def group(name,x,y,z,scale,angle,build):
 global asset
 asset='DENSE / '+name;start=len(made);build(x,y,z)
 pivot=Vector((x-5,8-y,z));T=B@Matrix.Translation(pivot)@Matrix.Rotation(-angle,4,'Z')@Matrix.Diagonal((scale,scale,scale,1))@Matrix.Translation(-pivot)@B.inverted()
 for o in made[start:]:o.matrix_world=T@o.matrix_world
 # Asset empty preserves the world-space placement and groups editable subparts.
 root=bpy.data.objects.new('Reference V5 / dense assembly / '+name,None);coll.objects.link(root);root.empty_display_size=.1;root['reference_asset']=asset
 for o in made[start:]:m=o.matrix_world.copy();o.parent=root;o.matrix_world=m

def pliers(x,y,z,angle=0):
 # A pair of curved insulated handles, central rivet and distinct steel jaws.
 def tr(u,v,zz):return(x+u*math.cos(angle)-v*math.sin(angle),y+u*math.sin(angle)+v*math.cos(angle),z+zz)
 for sign in [-1,1]:
  tube('pliers / curved yellow insulated handle',[tr(sign*.12,.27,.035),tr(sign*.105,.12,.035),tr(sign*.04,-.015,.035)],.035,yellow)
  tube('pliers / black rubber grip',[tr(sign*.12,.27,.037),tr(sign*.112,.17,.037)],.038,black)
  plate('pliers / forged steel jaw',[(tr(sign*.04,-.015,0)[0],tr(sign*.04,-.015,0)[1]),(tr(sign*.085,-.13,0)[0],tr(sign*.085,-.13,0)[1]),(tr(sign*.045,-.27,0)[0],tr(sign*.045,-.27,0)[1]),(tr(sign*.015,-.10,0)[0],tr(sign*.015,-.10,0)[1])],z+.025,.045,chrome)
 cyl('pliers / central pivot rivet',x,y-.015,z+.085,.045,.02,chrome)
 for sign in [-1,1]:
  for j in range(5):tube('pliers / serrated jaw tooth',[tr(sign*.023,-.13-j*.02,.073),tr(sign*.055,-.13-j*.02,.073)],.004,dark)
def wrench(x,y,z):
 tube('spanner / forged shank',[(x,y-.24,z),(x,y+.20,z)],.026,chrome)
 for yy,r in [(y-.24,.065),(y+.20,.078)]:
  tube('spanner / open head',[(x+math.cos(a)*r,yy+math.sin(a)*r,z) for a in [math.pi*.15+j*math.pi*1.7/20 for j in range(21)]],.021,chrome)
def paintkit(x,y,z):
 bucket(x-.18,y,z,.19,.39);bucket(x+.21,y+.09,z,.15,.31)
 box('painting / roller tray',x,y+.28,z+.03,.45,.28,.06,black)
 tube('painting / bent roller frame',[(x+.15,y+.17,z+.12),(x+.15,y+.29,z+.12),(x-.12,y+.29,z+.12)],.012,chrome)
 tube('painting / textured roller sleeve',[(x-.12,y+.29,z+.12),(x+.06,y+.29,z+.12)],.045,white)
 box('painting / brush timber handle',x+.26,y-.15,z+.05,.045,.23,.03,wood);box('painting / brush steel ferrule',x+.26,y-.29,z+.05,.09,.07,.04,chrome);box('painting / separate bristle bundle',x+.26,y-.36,z+.05,.085,.1,.035,black)
def hardware(x,y,z):
 for i in range(13):
  xx=x+random.uniform(-.26,.26);yy=y+random.uniform(-.26,.26)
  if i%2:
   ps=[]
   for radius in [.038,.018]:ps.extend((xx+math.cos(j*math.tau/6)*radius,yy+math.sin(j*math.tau/6)*radius) for j in range(6))
   plate('hardware / individual hex nut',ps[:6],z+.01,.025,chrome)
   cyl('hardware / nut threaded bore',xx,yy,z+.037,.014,.003,black)
  else:
   tube('hardware / threaded steel bolt',[(xx,yy-.04,z+.025),(xx,yy+.06,z+.025)],.009,chrome);box('hardware / hex bolt head',xx,yy+.066,z+.025,.03,.02,.03,dark)
# Posterior left: interlocking masonry, joinery, garden and tool stations.
group('rear left tall brick pile',.48,1.10,.48,.85,-.08,lambda x,y,z:(pallet(x,y,z,.75,.65),bricks(x,y,z+.25,6)))
group('rear left crate and paint',1.55,1.45,.42,.72,.13,lambda x,y,z:(crate(x,y,z),paintkit(x,y,z+.53),plant(x-.12,y+.38,z+.53,.68)))
group('rear left mixed blocks',.46,2.65,.40,.86,-.13,lambda x,y,z:(pallet(x,y,z,.74,.8),block(x,y,z+.25),block(x+.05,y+.02,z+.59),bricks(x,y+.35,z+.25,2)))
group('rear left timber tools',1.00,3.45,.48,.75,.08,lambda x,y,z:(crate(x,y,z),timber(x,y,z+.53,2),tape(x+.07,y+.03,z+.83),pliers(x-.2,y+.3,z+.83,.6)))
group('rear left garden support',.42,4.20,.20,.8,-.15,lambda x,y,z:(crate(x,y,z),plant(x,y,z+.53,.95),bucket(x+.26,y+.22,z,.16,.32)))
# Left shoulder below channel: tightly layered tools and materials.
group('left shoulder hardware bench',.67,5.25,.20,.82,-.12,lambda x,y,z:(pallet(x,y,z,.8,.8),toolbox(x,y,z+.25),tape(x+.08,y+.12,z+.80),pliers(x-.16,y-.12,z+.80,.3),hardware(x,y+.27,z+.79)))
group('left masonry pocket',.55,6.35,.06,.8,.15,lambda x,y,z:(block(x,y,z),bricks(x+.10,y+.05,z+.33,3),plant(x-.14,y-.32,z,.55)))
group('left brick pile shoulder',.62,8.45,.06,.7,-.10,lambda x,y,z:(crate(x,y,z),bricks(x,y,z+.53,3),bucket(x+.20,y+.25,z,.14,.32)))
group('left workbench clutter',.60,9.72,.08,.72,.12,lambda x,y,z:(pallet(x,y,z),tape(x-.12,y+.25,z+.25),pliers(x+.17,y+.16,z+.26,-.6),paintkit(x,y-.2,z+.25)))
group('left lower woodworking',1.12,11.5,.08,.58,-.17,lambda x,y,z:(crate(x,y,z),drill(x,y,z+.53),hardware(x,y+.26,z+.54)))
group('left sling garden crates',.55,12.85,.03,.85,.12,lambda x,y,z:(crate(x,y,z),plant(x,y,z+.53,.8),bricks(x+.25,y-.23,z,2)))
group('left flipper tool station',.66,14.50,.04,.72,-.12,lambda x,y,z:(pallet(x,y,z,.8,.65),toolbox(x,y,z+.25),pliers(x-.14,y+.08,z+.80,.2),tape(x+.2,y-.12,z+.80)))
# Posterior right: raised blocks, coating supplies and a crowded garden terrace.
group('rear right tall blocks',8.65,1.12,.55,.85,.08,lambda x,y,z:(pallet(x,y,z,.8,.7),block(x,y,z+.25),block(x,y,z+.58),block(x,y,z+.91)))
group('rear right garden terrace',7.65,1.00,.30,.65,-.12,lambda x,y,z:(crate(x,y,z),plant(x,y,z+.53,.85),bucket(x+.25,y+.12,z,.16,.38)))
group('rear right coating supplies',8.55,2.65,.45,.82,-.08,lambda x,y,z:(crate(x,y,z),paintkit(x,y,z+.53),tape(x+.23,y-.19,z+.55)))
group('rear right carpentry',8.18,3.75,.50,.73,.15,lambda x,y,z:(pallet(x,y,z,.8,.8),timber(x,y,z+.25,3),toolbox(x,y,z+.65),plant(x+.25,y+.32,z,.55)))
group('right paints and plants',8.37,5.60,.45,.76,-.08,lambda x,y,z:(crate(x,y,z),bucket(x-.17,y,z+.53,.19,.45),plant(x+.18,y+.1,z+.53,.65),pliers(x+.1,y-.22,z+.53,.2)))
group('right drill bench accessories',8.38,7.85,.45,.73,.11,lambda x,y,z:(pallet(x,y,z,.8,.7),tape(x-.18,y-.1,z+.25),pliers(x+.17,y-.1,z+.25,-.5),hardware(x,y+.22,z+.25)))
group('right barrow masonry',8.34,10.50,.04,.75,-.13,lambda x,y,z:(block(x,y,z),bricks(x,y,z+.33,3),bucket(x+.22,y-.15,z,.16,.35)))
group('right sling industrial pocket',8.4,12.85,.03,.72,.16,lambda x,y,z:(crate(x,y,z),paintkit(x,y,z+.53),tape(x-.19,y-.22,z+.53),plant(x+.24,y+.3,z,.64)))
group('right front mixed hardware',8.28,14.75,.04,.70,-.12,lambda x,y,z:(pallet(x,y,z,.8,.7),toolbox(x,y,z+.25),pliers(x,y+.05,z+.8,-.4),bucket(x+.23,y-.26,z,.16,.32)))
# Rear depth behind the house: short, connected workshop terraces below the arc.
for x in [2.2,7.15]:group('rear depth '+str(x),x,.35,.25,.58,(-.1 if x<5 else .1),lambda x,y,z:(crate(x,y,z),bricks(x,y,z+.53,2),bucket(x+.23,y,z+.53,.15,.31)))
# Taller vegetation is grouped with masonry so crowns fill the vertical gaps.
for name,x,y,z,scale in [('upper left canopy',.42,1.9,1.08,.95),('upper right canopy',9.2,1.3,1.0,.95),('left midway garden',.70,8.75,.40,.95),('left lower garden',.62,10.95,.48,.90),('right midway garden',8.4,8.8,.25,.95),('right lower garden',8.38,11.05,.28,.90)]:
 group(name,x,y,z,1,0,lambda x,y,z:(crate(x,y,z-.22),plant(x,y,z+.31,scale)))
# Electrical and plumbing pieces occupy narrow residual gaps between the larger assets.
for side,x,y in [('left',.70,7.08),('left',.65,13.75),('right',8.44,6.35),('right',8.44,11.95)]:
 def cable_group(x,y,z):
  pallet(x,y,z,.55,.55)
  for k in range(4):tube('electrical / wound black cable',[(x+math.cos(t)*.18,y+math.sin(t)*.18,z+.29+k*.025) for t in [i*math.tau/40 for i in range(41)]],.018,black)
  for k in range(3):tube('plumbing / bundled chrome pipe',[(x-.17+k*.14,y-.22,z+.43),(x-.17+k*.14,y+.21,z+.43)],.025,chrome)
  tape(x+.09,y-.05,z+.5);pliers(x-.10,y+.11,z+.50,.6)
 group(side+' gap electrical '+str(y),x,y,.07,.68,.15,cable_group)
# Rotate several old assets as whole assemblies, breaking the previous row/grid.
for asset_name,angle in ([] if s.get('dense_old_assets_rotated') else [('left brick and timber',-.10),('left carpentry',.08),('left toolbox',-.06),('right painting',.08),('right lower masonry',-.08)]):
 objs=[o for o in s.objects if o.get('reference_asset')==asset_name]
 if not objs:continue
 ps=[board.inverted()@o.matrix_world@Vector(v) for o in objs if o.type=='MESH' for v in o.bound_box]
 if not ps:continue
 c=Vector(((min(v.x for v in ps)+max(v.x for v in ps))/2,(min(v.y for v in ps)+max(v.y for v in ps))/2,0));T=board@Matrix.Translation(c)@Matrix.Rotation(angle,4,'Z')@Matrix.Translation(-c)@board.inverted()
 for o in objs:o.matrix_world=T@o.matrix_world
s['dense_old_assets_rotated']=True
s['dense_workshop_pass']='5.3';s['dense_added_parts']=len(made)
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/ferrisariato-precision.blend'))
(R/'assets/dense-workshop-inventory.json').write_text(json.dumps({'parts':len(made),'assemblies':sorted(set(o.get('reference_asset') for o in made)),'pliers':sum('central pivot rivet' in o.name for o in made),'tapeMeasures':sum('thumb lock' in o.name for o in made)},indent=2))
print('DENSE_WORKSHOP_SAVED',len(made),flush=True)
