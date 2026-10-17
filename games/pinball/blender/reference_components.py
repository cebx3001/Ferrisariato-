"""V5: replace V4 components in place using the approved detail photographs.
Run against ferrisariato-precision.blend. Camera, board, channel and mechanisms stay.
All geometry is independently editable; repeated manufactured parts share meshes.
"""
import bpy, math, json, random, bmesh
from pathlib import Path
from mathutils import Matrix, Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene
D=json.loads((R/'layout.json').read_text());P=json.loads((R/'assets/projection.json').read_text());board=Matrix(P['boardTransform'])
random.seed(43989)
for key in ['reference_clearance_corrected','dense_old_assets_rotated','sculpted_drill_review']:
 if key in s:del s[key]
interactive=bpy.data.collections['Interactive bumper tank target sling art'];dynamic=bpy.data.collections['Movable elements']
static=bpy.data.collections.get('Reference V5 / workshop assets') or bpy.data.collections.new('Reference V5 / workshop assets')
if static.name not in s.collection.children:s.collection.children.link(static)
# Remove the replaced assemblies, never the cabinet, channel, house or field.
prefix=('Flipper /','Sling','sling-','Pallet','Crate','Timber','Brick stack','Concrete block','Cardboard','Carton','Tape measure','Toolbox','Cordless drill','Paint bucket','Cone','Ornamental plant','Pot /','Wheelbarrow','Small blue industrial','Hammer','Wrench','Saw','Carpentry','Clamp','Sack','Mortar','Paint /','Hardware','Cable','Pipe','Brush','Roller','Worksite','Masonry','Painting','Electrical','Tools','Plumbing','Reference V5 /')
for o in list(s.objects):
 if o.name.startswith(prefix):bpy.data.objects.remove(o,do_unlink=True)
materials={}
def mat(name,color,rough=.3,metal=0,emit=0):
 m=bpy.data.materials.get('Reference V5 / '+name) or bpy.data.materials.new('Reference V5 / '+name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if emit:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emit
 materials[name]=m;return m
blue=mat('cobalt lacquer',(.004,.035,.34),.16,.12);blue.node_tree.nodes.get('Principled BSDF').inputs['Coat Weight'].default_value=.65
white=mat('white molded cap',(.91,.94,.98),.22);white.node_tree.nodes.get('Principled BSDF').inputs['Coat Weight'].default_value=.4
rubber_blue=mat('blue rubber sleeve',(.008,.025,.13),.48)
yellow=mat('safety yellow lacquer',(1,.68,.006),.21,.08);black=mat('rubber',(.007,.01,.016),.57);chrome=mat('polished chrome',(.72,.78,.84),.115,1);dark=mat('dark steel',(.075,.10,.14),.25,.8)
wood=bpy.data.materials['Cut pine'];concrete=bpy.data.materials['Rough concrete blocks'];terra=bpy.data.materials['Terracotta'];soil=bpy.data.materials['Potting soil'];orange=mat('cone orange',(1,.12,.006),.32);amber=mat('warm bulb',(1,.64,.08),.16,0,9)
leaves=[mat('leaf '+str(i),c,.38) for i,c in enumerate([(.035,.16,.008),(.12,.31,.016),(.21,.38,.025),(.055,.23,.012)])]
cache={};made=[];coll=static;asset=None
# All local coordinates use the existing playfield convention.
def xyz(p):return board@Vector((p[0]-5,8-p[1],p[2]))
def link(name,me):
 o=bpy.data.objects.new('Reference V5 / '+name,me);coll.objects.link(o);o['reference_asset']=asset or name;made.append(o);return o
def bevel(o,w=.025):
 m=o.modifiers.new('Manufactured edge radius','BEVEL');m.width=w;m.segments=3
 m=o.modifiers.new('Weighted surface normals','WEIGHTED_NORMAL');return o
def mesh(name,ps,faces,m):
 me=bpy.data.meshes.new(name);me.from_pydata([xyz(p) for p in ps],[],faces);me.materials.append(m);me.update();return link(name,me)
def primitive(name,p,dims,m,kind='box'):
 key=(kind,tuple(round(x,6) for x in dims),m.name)
 if key not in cache:
  bm=bmesh.new()
  if kind=='box':bmesh.ops.create_cube(bm,size=1)
  elif kind=='cyl':bmesh.ops.create_cone(bm,segments=48,cap_ends=True,cap_tris=False,radius1=1,radius2=1,depth=1)
  else:bmesh.ops.create_uvsphere(bm,u_segments=24,v_segments=16,radius=1)
  for v in bm.verts:
   for i in range(3):v.co[i]*=dims[i]
  me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free();me.materials.append(m)
  if kind!='box':
   for f in me.polygons:f.use_smooth=True
  cache[key]=me
 o=link(name,cache[key]);o.matrix_world=board@Matrix.Translation((p[0]-5,8-p[1],p[2]));
 if kind!='sphere':bevel(o,min(.025,min(dims)/5))
 return o
def box(n,x,y,z,w,d,h,m):return primitive(n,(x,y,z),(w,d,h),m)
def cyl(n,x,y,z,r,h,m):return primitive(n,(x,y,z),(r,r,h),m,'cyl')
def sphere(n,x,y,z,r,m):return primitive(n,(x,y,z),(r,r,r),m,'sphere')
def tube(n,ps,r,m):
 me=bpy.data.curves.new(n,'CURVE');me.dimensions='3D';me.bevel_depth=r;me.bevel_resolution=3;sp=me.splines.new('POLY');sp.points.add(len(ps)-1)
 for v,p in zip(sp.points,ps):v.co=(*xyz(p),1)
 me.materials.append(m);return link(n,me)
def plate(n,ps,z,h,m):
 k=len(ps);o=mesh(n,[(x,y,z) for x,y in ps]+[(x,y,z+h) for x,y in ps],[tuple(reversed(range(k))),tuple(range(k,2*k))]+[(i,(i+1)%k,(i+1)%k+k,i+k) for i in range(k)],m);bevel(o,min(.025,h*.24));return o
def rounded(poly,r=.12):
 out=[]
 for i,b in enumerate(poly):
  a=Vector(poly[i-1]);b=Vector(b);c=Vector(poly[(i+1)%len(poly)]);u=(a-b).normalized();v=(c-b).normalized();ang=u.angle(v);t=min(r/math.tan(ang/2),(a-b).length*.25,(c-b).length*.25);p=b+u*t;q=b+v*t
  # Quadratic corner follows the photograph's rounded molded outline.
  for j in range(9):
   f=j/8;out.append(tuple((1-f)**2*p+2*f*(1-f)*b+f*f*q))
 return out
def screw(x,y,z,r=.04):
 cyl('chrome washer',x,y,z,r*1.25,.014,chrome);sphere('domed fastener',x,y,z+.025,r,chrome)
 tube('cross drive',[(x-r*.5,y,z+r*.85),(x+r*.5,y,z+r*.85)],.005,dark)
 tube('cross drive',[(x,y-r*.5,z+r*.85),(x,y+r*.5,z+r*.85)],.005,dark)
def house(x,y,z,scale=1,m=blue):
 def poly(n,ps):return plate(n,[(x+a*scale,y+b*scale) for a,b in ps],z,.004,m)
 poly('house insignia / gabled body',[(-.13,.12),(-.13,-.035),(0,-.145),(.13,-.035),(.13,.12),(.045,.12),(.045,.01),(-.045,.01),(-.045,.12)])
 tube('house insignia / separate roof eave',[(x-.17*scale,y-.045*scale,z+.005),(x,y-.19*scale,z+.005),(x+.17*scale,y-.045*scale,z+.005)],.018*scale,m)
# Sculpted flipper layers: wide pivot, tapered nose, no top screws in the photo.
for f in D['flippers']:
 coll=dynamic;asset='flipper-'+f['id'];start=len(made);x,y,a,L=f['x'],f['y'],f['rest'],f['length']
 def contour(root,tip):
  nx=(root-tip)/L;ang=math.acos(nx)
  local=[(L+tip*math.cos(t),tip*math.sin(t)) for t in [-ang+2*ang*i/32 for i in range(33)]]+[(root*math.cos(t),root*math.sin(t)) for t in [ang+(math.tau-2*ang)*i/40 for i in range(41)]]
  return [(x+u*math.cos(a)-v*math.sin(a),y+u*math.sin(a)+v*math.cos(a)) for u,v in local]
 cyl('flipper / hidden axle',x,y,.14,.13,.26,chrome)
 cyl('flipper / underbody mounting collar',x,y,.10,.25,.08,dark)
 for n,z,h,r,t,m in [('black underside',.08,.07,.28,.18,black),('lacquered volumetric body',.15,.31,.28,.18,blue),('blue rubber perimeter',.45,.045,.276,.176,rubber_blue),('independent raised white cap',.495,.065,.235,.135,white)]:plate('flipper / '+n,contour(r,t),z,h,m)
 hx=x+math.cos(a)*.15;hy=y+math.sin(a)*.15;house(hx,hy,.563,.8)
 for o in made[start:]:o['flipper_id']=f['id'];o['rest_angle']=a
# Rounded and assembled slings. Exact outer hull remains the physical triangle.
coll=interactive
for sling in D['slings']:
 asset=sling['id'];v=sling['vertices'];cx=sum(x for x,y in v)/3;cy=sum(y for x,y in v)/3
 inset=lambda t:[(cx+(x-cx)*t,cy+(y-cy)*t) for x,y in v]
 plate('slingshot / raised black foundation',rounded(inset(.97)),.055,.14,black)
 for x,y in inset(.76):
  cyl('slingshot / chrome spacer',x,y,.29,.065,.27,chrome);cyl('slingshot / rubber spacer foot',x,y,.185,.083,.045,black)
 plate('slingshot / thick yellow molded frame',rounded(v),.38,.13,yellow)
 plate('slingshot / recessed blue lacquer panel',rounded(inset(.81),.09),.495,.035,blue)
 rubber=inset(.99);tube('slingshot / elastic rebound cord',[(x,y,.31) for x,y in rubber+[rubber[0]]],.025,black)
 for x,y in inset(.77):
  cyl('slingshot / inset bolt cup',x,y,.545,.072,.023,dark);screw(x,y,.56,.05)
 cyl('slingshot / brass bulb bezel',cx,cy,.55,.165,.05,yellow);cyl('slingshot / lamp holder',cx,cy,.59,.105,.07,chrome);sphere('slingshot / incandescent globe',cx,cy,.635,.105,amber)
 d=bpy.data.lights.new('Reference V5 / slingshot light','POINT');d.energy=6;d.color=(1,.56,.12);d.shadow_soft_size=.09;o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=xyz((cx,cy,.71))
# Workshop miniatures: local functions make physical assemblies, not proxy shapes.
coll=static
def pallet(x,y,z=0,w=.95,d=.8):
 for dx in [-w*.36,0,w*.36]:
  for dy in [-d*.34,d*.34]:box('pallet / spacer',x+dx,y+dy,z+.09,w*.17,d*.23,.18,wood)
  box('pallet / bottom runner',x+dx,y,z+.025,w*.18,d,.05,wood)
 for j in range(5):
  yy=y-d*.4+j*d*.2;box('pallet / deck board',x,yy,z+.21,w,d*.17,.065,wood)
  for dx in [-w*.36,0,w*.36]:cyl('pallet / individual nail',x+dx,yy,z+.247,.009,.006,dark)
 return z+.25
def bricks(x,y,z,rows=3):
 for row in range(rows):
  for col in range(3):
   for dep in range(2):box('masonry / individual ceramic brick',x+(col-1)*.28+(row%2)*.04,y+(dep-.5)*.22,z+.08+row*.17,.265,.21,.16,terra)
def block(x,y,z):
 # Four exterior walls plus centre web leave two open rectangular cavities.
 for dx in [-.275,0,.275]:box('masonry / hollow block web',x+dx,y,z+.16,.055,.40,.32,concrete)
 for dy in [-.18,.18]:box('masonry / hollow block outer wall',x,y+dy,z+.16,.60,.055,.32,concrete)
def timber(x,y,z,rows=4):
 for row in range(rows):
  for col in range(3):
   xx=x+(col-1)*.28;box('carpentry / individual pine plank',xx,y,z+.06+row*.13,.265,1.0,.12,wood)
   for yy in [y-.42,y+.42]:cyl('carpentry / nail head',xx,yy,z+.125+row*.13,.009,.005,dark)
def crate(x,y,z):
 for xx in [-.37,.37]:
  for yy in [-.3,.3]:box('crate / corner post',x+xx,y+yy,z+.25,.075,.075,.50,wood)
 for i in range(3):
  for yy in [-.33,.33]:box('crate / horizontal face slat',x,y+yy,z+.09+i*.16,.81,.05,.12,wood)
  for xx in [-.4,.4]:box('crate / side slat',x+xx,y,z+.09+i*.16,.05,.7,.12,wood)
 for i in range(4):box('crate / floorboard',x-.3+i*.2,y,z+.055,.18,.65,.08,wood)
 for xx in [-.35,.35]:
  for zz in [.09,.41]:sphere('crate / exposed nail',x+xx,y+.36,z+zz,.012,dark)
def toolbox(x,y,z):
 box('toolbox / molded yellow body',x,y,z+.22,.94,.52,.42,yellow);box('toolbox / separate lid',x,y,z+.47,.99,.57,.13,yellow)
 for dx in [-.3,.3]:box('toolbox / black hinged latch',x+dx,y+.29,z+.30,.10,.045,.22,black);box('toolbox / steel latch pin',x+dx,y+.32,z+.36,.065,.02,.035,chrome)
 tube('toolbox / recessed carrying handle',[(x-.22,y,z+.54),(x-.22,y,z+.64),(x+.22,y,z+.64),(x+.22,y,z+.54)],.04,blue)
 for dx in [-.39,.39]:
  for yy in [-.20,.20]:box('toolbox / rubber corner protector',x+dx,y+yy,z+.10,.13,.1,.16,black)
def tape(x,y,z):
 box('flexometer / rounded yellow shell',x,y,z+.20,.43,.30,.40,yellow);box('flexometer / black overmold top',x,y,z+.39,.29,.25,.045,black)
 c=cyl('flexometer / circular front label',x,y+.158,z+.21,.13,.018,black);c.matrix_world=board@Matrix.Translation((x-5,8-y-.158,z+.21))@Matrix.Rotation(math.pi/2,4,'X')
 c=cyl('flexometer / silver label ring',x,y+.173,z+.21,.072,.008,chrome);c.matrix_world=board@Matrix.Translation((x-5,8-y-.173,z+.21))@Matrix.Rotation(math.pi/2,4,'X')
 box('flexometer / thumb lock',x,y+.035,z+.43,.11,.10,.05,black);box('flexometer / extended metal tape',x+.3,y+.08,z+.055,.25,.09,.012,yellow)
 for i in range(7):box('flexometer / engraved graduation',x+.20+i*.028,y+.08,z+.064,.004,.055 if i%2 else .075,.003,black)
 box('flexometer / hooked end',x+.43,y+.08,z+.025,.018,.11,.07,chrome)
def bucket(x,y,z,r=.23,h=.48):
 cyl('paint / white metal can',x,y,z+h/2,r,h,white)
 for zz in [.035,h-.025]:cyl('paint / rolled chrome rim',x,y,z+zz,r+.015,.035,chrome)
 cyl('paint / blue pressed lid',x,y,z+h+.006,r-.012,.03,blue)
 house(x,y,z+h+.025,.65,white)
 tube('paint / wire carrying bail',[(x+r*math.cos(a),y,z+h*.55+r*math.sin(a)) for a in [i*math.pi/32 for i in range(33)]],.009,chrome)
 # Front label is real geometry facing the camera.
 n=mesh('paint / front house label',[(x-.1,y+r+.012,z+.1),(x-.1,y+r+.012,z+.23),(x,y+r+.012,z+.32),(x+.1,y+r+.012,z+.23),(x+.1,y+r+.012,z+.1)],[(0,1,2,3,4)],blue)
def drill(x,y,z):
 box('drill / black battery pack',x,y,z+.085,.46,.34,.17,black);box('drill / yellow battery rail',x,y,z+.18,.47,.35,.07,yellow)
 box('drill / molded pistol grip',x+.07,y,z+.40,.18,.22,.44,yellow);box('drill / rubber grip backstrap',x+.155,y,z+.42,.06,.23,.36,black)
 for i in range(6):box('drill / embossed grip ribs',x+.19,y,z+.26+i*.05,.012,.235,.018,black)
 box('drill / trigger',x-.055,y,z+.54,.10,.16,.10,black)
 box('drill / sculpted motor shell',x,y,z+.70,.57,.31,.29,yellow)
 box('drill / black rear cap',x+.25,y,z+.70,.09,.315,.25,black)
 for i in range(5):box('drill / ventilation slit',x+.09+i*.029,y+.16,z+.73,.012,.012,.12,black)
 for off,r,h,m in [(-.3,.145,.08,black),(-.37,.12,.09,chrome),(-.44,.10,.12,black)]:
  o=cyl('drill / torque collar and chuck',x+off,y,z+.70,r,h,m);o.matrix_world=board@Matrix.Translation((x+off-5,8-y,z+.70))@Matrix.Rotation(math.pi/2,4,'Y')
 for j in range(14):
  a=j*math.tau/14;tube('drill / chuck knurl',[(x-.50,y+math.cos(a)*.101,z+.70+math.sin(a)*.101),(x-.40,y+math.cos(a)*.101,z+.70+math.sin(a)*.101)],.006,chrome)
 tube('drill / steel bit',[(x-.51,y,z+.70),(x-.71,y,z+.70)],.016,chrome)
 for dx in [-.18,.18]:
  o=sphere('drill / visible casing screw',x+dx,y+.166,z+.7,.018,chrome)
def plant(x,y,z,scale=.8):
 # Lathed, tapered terracotta pot with an actual open rim and soil.
 rings=[(.15,0),(.22,.30),(.24,.31),(.24,.35),(.20,.35),(.185,.29)]
 ps=[(x+r*scale*math.cos(i*math.tau/48),y+r*scale*math.sin(i*math.tau/48),z+h*scale) for r,h in rings for i in range(48)]
 mesh('garden / hollow terracotta planter',ps,[(j*48+i,j*48+(i+1)%48,(j+1)*48+(i+1)%48,(j+1)*48+i) for j in range(len(rings)-1) for i in range(48)],terra)
 cyl('garden / visible potting soil',x,y,z+.30*scale,.19*scale,.025,soil)
 for j in range(48):
  a=j*2.39996;reach=scale*(.34+.06*(j%4));h=scale*(.48+.08*(j%5));ps=[]
  for k in range(7):
   t=k/6;rr=reach*t;zz=z+.30*scale+h*math.sin(t*1.6)-.20*scale*t*t;width=.058*scale*math.sin(math.pi*t)
   for side in [-1,0,1]:ps.append((x+math.cos(a)*rr-math.sin(a)*width*side,y+math.sin(a)*rr+math.cos(a)*width*side,zz+(.018*scale if side==0 else 0)))
  mesh('garden / curved lanceolate leaf',ps,[(k*3+i,(k+1)*3+i,(k+1)*3+i+1,k*3+i+1) for k in range(6) for i in range(2)],leaves[j%4])
def cone(x,y,z):
 box('site / orange square foot',x,y,z+.045,.42,.42,.09,orange)
 for name,r1,r2,zz,h,m in [('orange taper',.17,.025,.33,.53,orange),('lower white reflective band',.132,.105,.26,.1,white),('upper white reflective band',.078,.057,.44,.08,white)]:
  bm=bmesh.new();bmesh.ops.create_cone(bm,segments=48,cap_ends=True,radius1=r1,radius2=r2,depth=h);me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free();me.materials.append(m);o=link('site / '+name,me);o.matrix_world=board@Matrix.Translation((x-5,8-y,z+zz))
def wheelbarrow(x,y,z):
 ps=[(x-.23,y-.30,z+.40),(x+.23,y-.30,z+.40),(x+.23,y+.32,z+.40),(x-.23,y+.32,z+.40),(x-.43,y-.45,z+.79),(x+.43,y-.45,z+.79),(x+.43,y+.51,z+.79),(x-.43,y+.51,z+.79)]
 o=mesh('wheelbarrow / folded open steel tub',ps,[(0,1,2,3),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],blue);o.modifiers.new('Pressed sheet steel thickness','SOLIDIFY').thickness=.018;bevel(o,.02)
 tube('wheelbarrow / rolled blue lip',[ps[i] for i in [4,5,6,7,4]],.022,blue)
 for dx in [-.28,.28]:
  tube('wheelbarrow / steel chassis',[(x+dx,y-.95,z+.59),(x+dx,y-.2,z+.34),(x+dx,y+.67,z+.23)],.027,dark)
  tube('wheelbarrow / black hand grip',[(x+dx,y-.95,z+.59),(x+dx,y-.74,z+.53)],.043,black)
  tube('wheelbarrow / parking stand',[(x+dx,y-.18,z+.38),(x+dx,y-.08,z+.035),(x+dx,y+.14,z+.035),(x+dx,y+.26,z+.4)],.025,dark)
 o=cyl('wheelbarrow / rubber wheel',x,y+.61,z+.23,.21,.13,black);o.matrix_world=board@Matrix.Translation((x-5,8-y-.61,z+.23))@Matrix.Rotation(math.pi/2,4,'Y')
 o=cyl('wheelbarrow / exposed wheel hub',x,y+.61,z+.23,.085,.15,chrome);o.matrix_world=board@Matrix.Translation((x-5,8-y-.61,z+.23))@Matrix.Rotation(math.pi/2,4,'Y')
 for i in range(140):
  xx=x+random.uniform(-.32,.32);yy=y+random.uniform(-.32,.38);o=sphere('wheelbarrow / individual mineral pebble',xx,yy,z+.66+random.uniform(0,.09),random.uniform(.035,.061),concrete);o.scale=(1,.75,.7)
# Reference clusters. Each footprint fits outside the collision corridors.
for side in ['left','right']:
 x=.94 if side=='left' else 8.22
 for y,z in [(1.35,.72),(2.9,.50),(4.25,.40)]:
  asset=side+' rear masonry '+str(y);base=pallet(x,y,z,w=.83,d=.68);block(x,y,base);block(x,y,base+.33);plant(x,y+.47,z,.62)
asset='left brick and timber';z=pallet(.94,7.85,.03,w=.88,d=.82);bricks(.94,7.85,z,3)
asset='left carpentry';z=pallet(.94,9.4,.03,w=.88,d=.95);timber(.94,9.4,z,4);plant(.95,8.65,.06,.65)
asset='left toolbox';z=pallet(.94,10.65,.03,w=.94,d=.72);toolbox(.94,10.65,z);tape(.92,11.25,.05)
asset='left lower workshop';z=pallet(.96,12.0,.03,w=.88,d=.88);timber(.96,12,z,3);toolbox(.94,12,z+.42);plant(.94,13.25,.03,.78)
asset='left front hardware';z=pallet(.96,14.15,.03,w=.88,d=.72);toolbox(.94,14.15,z);tape(.94,14.15,z+.57)
asset='right painting';z=pallet(8.2,4.8,.38,w=.85,d=.8);bucket(7.98,4.8,z,.20,.44);bucket(8.43,4.8,z,.22,.51);plant(8.2,5.6,.55,.72)
asset='right power tools';crate(8.22,7.3,.23);drill(8.23,7.3,.77);block(8.2,6.45,.54);bucket(8.2,6.4,.87,.20,.43)
asset='right construction';wheelbarrow(8.25,9.65,.025)
asset='right lower masonry';block(8.2,11.4,.06);block(8.2,11.4,.39);cone(8.22,12.2,.035);plant(8.2,13.35,.07,.65)
asset='right industrial case';z=pallet(8.21,14.4,.03,w=.8,d=.65);toolbox(8.21,14.4,z)
# Complete the miniature catalog with recognizable hand tools on the workshop deck.
asset='hand tools';x,y,z=8.2,8.25,.58
box('hand tool / pine hammer handle',x,y,z,.06,.48,.05,wood);box('hand tool / chrome hammer head',x,y-.21,z+.025,.24,.08,.10,chrome)
tube('hand tool / screwdriver shaft',[(x+.18,y-.2,z),(x+.18,y+.04,z)],.009,chrome);tube('hand tool / screwdriver insulated grip',[(x+.18,y+.04,z),(x+.18,y+.22,z)],.025,yellow)
for dx in [-.17,-.08]:tube('hand tool / pliers insulated arm',[(x+dx,y+.2,z),(x-.13,y-.06,z)],.025,orange)
sphere('hand tool / pliers pivot',x-.13,y-.06,z+.01,.033,chrome)
for dx in [-.18,-.08]:tube('hand tool / pliers jaw',[(x-.13,y-.06,z),(x+dx,y-.19,z)],.017,chrome)
# Place a genuine support shelf below those loose tools.
box('workshop / hand tool tray',8.2,8.25,.52,.72,.85,.09,blue)
# Dedicated controlled soft highlights on the manufactured front assemblies.
for x in [-4,4]:
 d=bpy.data.lights.new('Reference V5 / front strip softbox','AREA');d.energy=100;d.shape='RECTANGLE';d.size=2.4;d.size_y=.45;o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=(x,-9,5);o.rotation_euler=(Vector((x*.5,-5,.5))-o.location).to_track_quat('-Z','Y').to_euler()
s['reference_components_version']='5.0';s['reference_components_source']='43989 flipper/sling assembly; 43991 workshop miniatures'
for c in [interactive,dynamic,static,bpy.data.collections['Foreground decorative raised channels'],bpy.data.collections['Protective glass reflections']]:c.hide_render=False
bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/ferrisariato-precision.blend'))
(R/'assets/reference-component-inventory.json').write_text(json.dumps({'version':'5.0','objects':len(made),'assets':sorted(set(o.get('reference_asset') for o in made)),'flippers':{'rootRadius':.28,'tipRadius':.18,'layers':4,'topFasteners':False},'source':['2-43989.jpg','5-43991.jpg']},indent=2))
print('REFERENCE_COMPONENTS_SAVED',len(made),flush=True)
