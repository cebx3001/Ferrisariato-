"""V4 precision revision. Run on the archived premium scene, never cumulatively."""
import bpy,math,json,sys,random,ast,bmesh
from pathlib import Path
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[1]
# Reuse the established modular asset library without executing V3 placement.
source=(ROOT/'blender/premium.py').read_text().split('# A single connected upper route')[0]
source=source.replace("if scene.get('premium_pass'):raise RuntimeError('Start from the V2 photographic scene')",'')
source=source.replace("bpy.data.collections.new('Premium structural detailing')","bpy.data.collections.new('Precision structural detailing')")
exec(compile(source,str(ROOT/'blender/premium.py'),'exec'))
random.seed(43994)
# Remove every obsolete raised channel, including its separate return branches.
for o in list(foreground.objects):bpy.data.objects.remove(o,do_unlink=True)
for o in list(scene.objects):
 if o.name.startswith(('Upper bridge','Left return transition','Right return transition','Practical / Ramp')):bpy.data.objects.remove(o,do_unlink=True)
for o in list(dynamic.objects):
 if 'flipper' in o.name.lower():bpy.data.objects.remove(o,do_unlink=True)
# Relocate existing independent props together using their world-space geometry.
bpy.context.view_layer.update()
def center(o):
 if o.type not in {'MESH','CURVE','FONT'}:return o.location.copy()
 return sum((o.matrix_world@Vector(v) for v in o.bound_box),Vector())/8
prop_prefix=('Pallet','Crate','Timber','Brick','Concrete block','Cardboard','Carton','Tape measure','Toolbox','Cordless drill','Paint bucket','Cone','Ornamental','Pot /','Wheelbarrow','Small blue','Hammer','Wrench','Saw','Carpentry','Clamp','Sack','Mortar','Paint /','Hardware','Cable','Pipe','Brush','Roller','Worksite')
for o in list(scene.objects):
 if not o.name.startswith(prop_prefix):continue
 c=center(o);x,y=c.x+5,8-c.y
 # Keep central circulation clear; compact side bays preserve whole assemblies.
 if 4.5<y<11.6 and x<2.8:o.location.x-=.55
 if 4.5<y<12 and 6.9<x<8.7:o.location.x+=.48
 # Rear objects sit on genuine stepped terraces.
 if y<4 and x<2.15:o.location.z+=.38
 if y<4 and x>7.2:o.location.z+=.45
# Raise the residential scene as one miniature, preserving window/door alignment.
for o in list(scene.objects):
 c=center(o);x,y=c.x+5,8-c.y
 if 1.8<x<7.3 and .7<y<3.85 and (o.name.startswith(('House','Front door','Door','Cobalt pitched','Roof','Window','Lit window','Picket','Palm','Garden','Terrace','Official brand sign','Official logo image','Tree','Residential'))):o.location.z+=.35
# The residence stands above its sign, on its own stepped upper foundation.
for o in list(scene.objects):
 if o.name.startswith(('House','Front door','Door','Cobalt pitched','Roof','Window','Lit window')) and 1<8-center(o).y<4:o.location.z+=.45
cube('Residence / raised masonry pedestal',4.7,2.55,.56,2.95,1.85,.5,white)
mesh('Residence / front plaster gable',[(3.37,3.33,2.55),(6.03,3.33,2.55),(4.7,3.33,3.25)],[(0,1,2)],white)
for i in range(3):cube('Residence / porch stair',4.7,3.7-i*.13,.36+i*.14,.68,.23,.15,white)
# A single continuous floor and two transparent walls, never separate tunnels.
path=DATA['ramp']['samples'];edges=[[],[]]
for i,p in enumerate(path):
 a=path[max(0,i-1)];b=path[min(len(path)-1,i+1)];dx=b[0]-a[0];dy=b[1]-a[1];l=math.hypot(dx,dy)
 for j,s in enumerate([-1,1]):edges[j].append((p[0]+s*.35*dy/l,p[1]-s*.35*dx/l,p[2]))
verts=[p for pair in zip(*edges) for p in pair]
o=mesh('Single channel / continuous ball-bearing bed',verts,[(2*i,2*i+2,2*i+3,2*i+1) for i in range(len(path)-1)],blue,foreground);o.modifiers.new('Molded floor thickness','SOLIDIFY').thickness=.045
for edge in edges:
 n=len(edge);o=mesh('Single channel / transparent acrylic sidewall',edge+[(x,y,z+.25) for x,y,z in edge],[(i,i+1,i+1+n,i+n) for i in range(n-1)],clear,foreground);o.modifiers.new('Actual acrylic wall thickness','SOLIDIFY').thickness=.025
 line('Single channel / polished upper profile',[(x,y,z+.27) for x,y,z in edge],.023,steel,foreground)
 line('Single channel / polished lower profile',[(x,y,z+.02) for x,y,z in edge],.019,steel,foreground)
 for i in range(8,n-5,16):
  x,y,z=edge[i];line('Single channel / floor anchored column',[(x,y,.065),(x,y,z+.28)],.027,steel,foreground)
  cyl('Single channel / column flange',x,y,.065,.065,.05,metal,foreground)
  for zz in [z-.06,z+.22]:ring('Single channel / bolted collar',x,y,zz,.038,.012,bronze,foreground)
  sphere('Single channel / miniature LED',x,y,z+.29,.039,amber,foreground);point('Single channel / physical LED',x,y,z+.36,1.1)
for i in range(12,len(path)-12,20):
 x,y,z=path[i];q=path[i+1];a=math.atan2(q[1]-y,q[0]-x)
 def tr(u,v):return(x+u*math.cos(a)-v*math.sin(a),y+u*math.sin(a)+v*math.cos(a))
 polygon('Single channel / backlit arrow',[tr(.19,0),tr(-.13,.19),tr(-.045,0),tr(-.13,-.19)],z+.009,amber,foreground)
# Side terraces have thickness, closed faces, seams and coherent understructure.
for x,y,w,d,h in [(1.05,1.3,1.4,1.5,.45),(1.0,3.2,1.2,1.5,.38),(1.0,5,1.15,1.2,.25),(7.95,1.35,1.35,1.6,.65),(8.0,3.1,1.2,1.45,.45),(8.15,5,1.0,1.5,.3)]:
 cube('Second level / structural blue plinth',x,y,h/2,w,d,h,navy)
 cube('Second level / slab with overhang',x,y,h+.045,w+.06,d+.06,.09,concrete)
 for xx in [x-w*.42,x+w*.42]:
  cube('Second level / support upright',xx,y,h*.5,.09,d*.75,h,steel)
  for yy in [y-d*.4,y+d*.4]:screw(xx,yy,h+.1,.025)
 line('Second level / recessed light strip',[(x-w/2,y+d/2+.035,h-.06),(x+w/2,y+d/2+.035,h-.06)],.014,amber)
# Compact reference clusters occupy both sides behind and beneath the ramp.
props.pallet(1.05,1.45,w=.95,d=.8,z=.53);props.blocks(1.05,1.45,z=.85,count=4);props.plant(.75,2.35,z=.45,scale=.8)
props.pallet(8.05,1.35,w=.95,d=.8,z=.75);props.blocks(8.05,1.35,z=1.05,count=4)
props.bucket(7.9,2.7,z=.65,r=.22,h=.48);props.plant(8.15,3.7,z=.55,scale=.75)
props.crate(.95,8.5,w=.8,d=.7,h=.5,z=.1);props.timber(.95,8.5,z=.7)
props.pallet(.95,10.2,w=.85,d=.7,z=.12);props.toolbox(.95,10.2,z=.42)
props.pallet(8.22,6.8,w=.85,d=.7,z=.1);props.bucket(8.2,6.8,z=.42,r=.22,h=.5)
# Floor-side guides agree with newly explicit collision boundaries.
for wall in DATA['walls'][4:]:
 for a,b in zip(wall,wall[1:]):
  rail=[(a[0],a[1],.2),(b[0],b[1],.2)]
  if a[0]==1.65 and a[1]<6<b[1]:rail=[(1.65,a[1],.2),(1.65,6.05,.2),(1.65,6.25,.045),(1.65,7.4,.045),(1.65,7.6,.2),(1.65,b[1],.2)]
  line('Playable corridor / chrome guide',rail,.028,steel,static)
  dist=math.dist(a,b)
  for j in range(max(2,int(dist/.8))+1):
   t=j/max(2,int(dist/.8));x=a[0]*(1-t)+b[0]*t;y=a[1]*(1-t)+b[1]*t
   # Near the channel mouth, the ball crosses above a low guide and lands inside.
   cyl('Playable corridor / flush anchor',x,y,.09,.055,.16,steel,static)
# Physically layered flippers: footprint shared with the Box2D fixtures.
for f in DATA['flippers']:
 x,y,a,L=f['x'],f['y'],f['rest'],f['length']
 def cap(r):
  ex=x+math.cos(a)*L;ey=y+math.sin(a)*L
  return [(ex+math.cos(a-math.pi/2+i*math.pi/24)*r,ey+math.sin(a-math.pi/2+i*math.pi/24)*r) for i in range(25)]+[(x+math.cos(a+math.pi/2+i*math.pi/24)*r,y+math.sin(a+math.pi/2+i*math.pi/24)*r) for i in range(25)]
 cyl('Flipper / chrome pivot',x,y,.13,.25,.18,steel,dynamic)
 for r,z,depth,m in [(.21,.15,.08,black),(.21,.30,.28,blue),(.205,.45,.035,navy),(.17,.5,.06,ivory)]:
  o=polygon('Flipper / separate assembled layer',cap(r),z,m,dynamic);o.modifiers.new('Layer thickness','SOLIDIFY').thickness=depth;bevel(o,.018)
 screw(x,y,.54,.036,dynamic)
 # White-cap house insignia, matching the reference's component graphic.
 hx=x+math.cos(a)*.2;hy=y+math.sin(a)*.2
 def tr(u,v):return(hx+u*math.cos(a)-v*math.sin(a),hy+u*math.sin(a)+v*math.cos(a))
 polygon('Flipper / blue house graphic',[tr(-.10,.07),tr(-.10,-.05),tr(0,-.13),tr(.10,-.05),tr(.10,.07),tr(.025,.07),tr(.025,.0),tr(-.025,.0),tr(-.025,.07)],.542,blue,dynamic)
# Polished mineral floor: pores remain under a physically glossy clear coating.
p=floor.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.13;p.inputs['Coat Weight'].default_value=.72;p.inputs['Coat Roughness'].default_value=.085;p.inputs['IOR'].default_value=1.48
for n in floor.node_tree.nodes:
 if n.type=='BUMP':n.inputs['Strength'].default_value=.09;n.inputs['Distance'].default_value=.006
noise=floor.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=36
ramp=floor.node_tree.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.10,.10,.10,1);ramp.color_ramp.elements[1].color=(.18,.18,.18,1)
floor.node_tree.links.new(noise.outputs['Fac'],ramp.inputs[0]);floor.node_tree.links.new(ramp.outputs['Color'],p.inputs['Roughness'])
# Lacquer saturation and controlled reflections follow the approved blue/yellow finish.
p=blue.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.008,.055,.36,1);p.inputs['Metallic'].default_value=.1;p.inputs['Roughness'].default_value=.24;p.inputs['Coat Weight'].default_value=.4
p=gold.node_tree.nodes.get('Principled BSDF');p.inputs['Metallic'].default_value=.05;p.inputs['Roughness'].default_value=.25;p.inputs['Coat Weight'].default_value=.4
# Tank lids are plain blue with a central mechanism; their insignia faces forward.
bpy.context.view_layer.update()
for o in list(interactive.objects):
 if o.name.startswith(('House pictogram','House icon doorway')) and 8-center(o).y>10.4:bpy.data.objects.remove(o,do_unlink=True)
for t in [b for b in DATA['bumpers'] if b['kind']=='tank']:
 x,y=t['x'],t['y'];r=.16;coords=[(-r,0),(-r,.2),(0,.34),(r,.2),(r,0),(.04,0),(.04,.13),(-.04,.13),(-.04,0)]
 mesh('Tank / front blue house insignia',[(x+u,y+.445,.3+v) for u,v in coords],[tuple(range(len(coords)))],blue,interactive)
# Optical finish correction after the first camera comparison.
for n in bpy.data.materials['Protective glass / thin pane Fresnel'].node_tree.nodes:
 if n.type=='MATH' and n.operation=='MULTIPLY':n.inputs[1].default_value=.006
# Milky yellow bumper barrels transmit and emit light, with chrome separated.
barrel=mat('Precision / illuminated yellow bumper resin',(1,.55,.015),0,.20,3)
bs=barrel.node_tree.nodes.get('Principled BSDF');bs.inputs['Transmission Weight'].default_value=.18;bs.inputs['Coat Weight'].default_value=.45
for o in scene.objects:
 if o.name.endswith('illuminated core'):o.data=o.data.copy();o.data.materials.clear();o.data.materials.append(barrel)
 if o.name.startswith('Practical / floor insert'):o.data.energy=3.6
 if o.name.startswith('Practical / target pedestal'):o.data.energy=4.0
 if o.name.startswith('Practical / side rail incandescent'):o.data.energy=3.5
 if o.name.startswith('Insert / inset opal lens'):
  o.data=o.data.copy();o.data.materials.clear();o.data.materials.append(amber)
 if o.name.startswith('Target golden lamp'):
  o.hide_render=True
 if o.name.startswith('Product / overhead'):o.data.energy*=.65
# Protected front-facing target indicators sit inside their metal bezel.
for t in DATA['targets']:
 x,y=t['x'],t['y']
 for name,r,yy,m in [('bezel',.135,y+.225,steel),('flush luminous lens',.108,y+.245,amber)]:
  o=cyl('Target / '+name,x,yy,.18,r,.018,m,interactive);o.rotation_euler.x=math.pi/2
for o in scene.objects:
 if o.name.startswith('Practical / bumper underlight'):o.data.energy=4.5
# Scale the original pixel-exact apron logo without changing its aspect ratio.
o=bpy.data.objects['Official apron logo / unchanged image'];o.scale=(4.5,4.5*348/1051,1)
# Review corrections: whole assemblies move together; no decoration in the outlet.
bpy.context.view_layer.update()
for o in list(scene.objects):
 c=center(o);x,y=c.x+5,8-c.y
 if o.name.startswith('Timber') and 5.35<y<6.85 and x<2.3:o.location.y-=2.65;o.location.z+=.35
 if o.name.startswith('Pallet') and 5.45<y<6.7 and x<2.3:o.location.y-=2.65;o.location.z+=.1
 if o.name.startswith(('Ornamental','Pot /')) and 5.1<y<6.3 and x<2.5:o.location.x-=1.1
 if o.name.startswith('Small blue industrial'):o.location.x-=.5
 if o.name.startswith('Tape measure') and 7.5<y<8.5 and x<2.5:o.location.x-=.5
 if o.name.startswith('Paint bucket') and 10.1<y<11.4 and x<3:o.location.x-=.95
 if o.name.startswith(('Painting','Tools','Paint bucket','Hammer','Wrench','Screwdriver','Electrical')) and 4.5<y<11.7 and x>7:
  o.location.z+=.47
 if o.name.startswith(('Ornamental','Pot /')) and 11<y<12.1 and x>7:o.location.x+=.55
 if o.name.startswith('Pallet') and 6.4<y<7.85 and x>7:o.location.x+=.13
 if o.name.startswith('Masonry / scattered') and x<2 and 7<y<9:o.location.x-=.2
 if o.name.startswith(('Pallet','Brick stack')) and 4.5<y<5.4 and x<2.2:o.location.x-=.35
 if o.name.startswith('Plumbing') and 4.8<y<6 and x<2.2:o.location.x-=.25
 if o.name.startswith(('Ornamental','Pot /')) and 4.3<y<5.3 and x>7:o.location.x+=.62;o.location.z+=.4
for y in [5.45,8.15,10.75]:
 cube('Side terrace / raised workshop deck',8.3,y,.39,.86,1.28,.16,navy)
 cube('Side terrace / top slab',8.3,y,.49,.89,1.3,.05,wood)
 for yy in [y-.5,y+.5]:cube('Side terrace / support leg',8.3,yy,.18,.65,.08,.36,steel)
# Decorative legacy rails follow the new physical guard boundaries.
bpy.context.view_layer.update()
for o in list(scene.objects):
 c=center(o);x,y=c.x+5,8-c.y
 if o.name.startswith('Industrial guard'):
  if 1.65<x<3 or 6.8<x<7.5:bpy.data.objects.remove(o,do_unlink=True);continue
 if 4.6<y<5 and (abs(x-2)<.17 or abs(x-7.5)<.17) and (o.name.startswith(('Warm safety','Lamp /','Practical /'))):o.location.x+=(-.5 if x<5 else .5)
# Dense miniature crowns retain individual folded leaves, trunks and branches.
for x in [2.65,6.75]:
 for i in range(42):
  a=i*2.39996;reach=.42+.18*(i%3);z=1.63+.13*(i%4);ux,uy=math.cos(a),math.sin(a);nx,ny=-uy*.12,ux*.12
  mesh('Garden / dense crown folded leaf',[(x,2.45,1.48),(x+ux*reach*.5+nx,2.45+uy*reach*.5+ny,z),(x+ux*reach,2.45+uy*reach,z-.12),(x+ux*reach*.5-nx,2.45+uy*reach*.5-ny,z),(x+ux*reach*.5,2.45+uy*reach*.5,z+.055)],[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],leaf if i%3 else green)
# The protective cover clears the newly raised residence instead of cutting its roof.
for o in cover.objects:
 if o.type=='MESH':
  if o.name.startswith('Protective glass / uninterrupted'):
   for v in o.data.vertices:v.co.z=4.0-.18*(8-v.co.y)
  elif 'cheek' not in o.name:o.location.z+=1-.05*(8-o.location.y)
 elif o.type=='CURVE':
  for sp in o.data.splines:
   for p in sp.points:p.co.z+=1-.05*(8-p.co.y)
# Datablock-created parts need evaluated transforms before the board rotation.
bpy.context.view_layer.update()
# Cabinet/playfield have a real 6.5-degree pitch, independent of the camera.
board=Matrix.Translation((0,-8,0))@Matrix.Rotation(math.radians(6.5),4,'X')@Matrix.Translation((0,8,0))
for o in list(scene.objects):
 if o.type=='CAMERA' or (o.type=='LIGHT' and o.name.startswith('Product /')):continue
 o.matrix_world=board@o.matrix_world
# Head components use world coordinates, physically joined to the sloped cabinet.
head_objects=set(scene.objects)
head_y=-.25
cube('Backbox / solid lacquer cabinet',5,head_y,5.25,10.0,.55,2.8,blue)
headpaint=mat('Precision / backbox cobalt lacquer',(.008,.055,.33),.05,.38);headpaint.node_tree.nodes.get('Principled BSDF').inputs['Coat Weight'].default_value=.15
cube('Backbox / inset face panel',5,head_y+.30,5.25,9.74,.08,2.56,headpaint)
for x in [.13,9.87]:
 cube('Backbox / chrome edge trim',x,head_y+.36,5.25,.045,.04,2.75,steel)
 cube('Backbox / structural rear support',x,head_y-.03,2.9,.15,.35,2.4,navy)
for z in [3.89,6.61]:cube('Backbox / horizontal chrome trim',5,head_y+.36,z,9.9,.04,.045,steel)
logo=bpy.data.materials['Official provided logo / unchanged pixels']
o=bpy.data.objects['Official logo image plane'].copy();o.data=o.data.copy();scene.collection.objects.link(o);o.name='Backbox / official unmodified logo';o.location=pt(4.4,head_y+.365,5.88);o.rotation_euler=(math.pi/2,0,0);o.scale=(5.05,5.05*348/1051,1)
for text,z,m in [('CONSTRUYE',6.00,white),('TU CASA',5.67,white),('CON TODO',5.34,gold)]:props.text('Backbox / approved slogan',text,8.33,head_y+.37,z,.31,m,True)
displays={}
for key,x,w,label in [('score',2.35,3.65,'PUNTOS'),('time',6.65,2.25,'TIEMPO')]:
 cube('Backbox / '+key+' recessed bezel',x,head_y+.37,4.65,w,.14,.93,black)
 cube('Backbox / '+key+' polished inner rim',x,head_y+.447,4.60,w-.12,.028,.64,steel)
 cube('Backbox / '+key+' dark lens',x,head_y+.465,4.60,w-.19,.025,.57,black)
 props.text('Backbox / '+key+' engraved legend',label,x-w*.34,head_y+.46,4.97,.18,white,True)
 displays[key]=[pt(x-w*.43,head_y+.485,4.82),pt(x+w*.43,head_y+.485,4.82),pt(x+w*.43,head_y+.485,4.38),pt(x-w*.43,head_y+.485,4.38)]
 for dx in [-w*.46,w*.46]:
  o=cyl('Backbox / lens retaining screw',x+dx,head_y+.46,4.99,.029,.025,steel);o.rotation_euler.x=math.pi/2
cube('Backbox / center indicator bezel',4.95,head_y+.39,4.65,1.02,.14,.95,blue)
props.text('Backbox / center house symbol','⌂',4.95,head_y+.48,4.43,.75,white,True)
# Render-only display numerals; runtime paints current values on the same quads.
font=bpy.data.fonts.load(str(ROOT/'assets/pinball-segment.ttf'));font.pack()
for key,txt,x in [('score','000.000',2.35),('time','02:00',6.65)]:
 o=props.text('Live display / '+key,txt,x,head_y+.49,4.40,.48,amber,True);o.data.font=font
 for c in list(o.users_collection):c.objects.unlink(o)
 dynamic.objects.link(o)
# Lower and join the head to a continuous rear cabinet wall.
for o in set(scene.objects)-head_objects:o.location.z-=.15
displays={k:[(p[0],p[1],p[2]-.15) for p in ps] for k,ps in displays.items()}
cube('Cabinet / continuous rear connection',5,head_y-.15,2.55,9.9,.34,1.6,blue)
# Collect all additions into editable static / dedicated channel / live collections.
for o in set(scene.objects)-original:
 if o.type in {'LIGHT','CAMERA'}:continue
 if any(o.name in c.objects for c in [static,foreground,interactive,dynamic,cover]):continue
 for c in list(o.users_collection):c.objects.unlink(o)
 static.objects.link(o)
cam=scene.camera;cam.location=(0,-22,24);target=Vector((0,.1,2.0));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.lens=52;cam.data.shift_x=0;cam.data.shift_y=0
scene.render.resolution_x=880;scene.render.resolution_y=1320;scene.render.resolution_percentage=100
bpy.context.view_layer.update()
corners=[board@Vector(pt(x,y,z)) for x in [0,10] for y in [0,16.7] for z in [-.5,.5]]+[Vector(pt(x,head_y, z)) for x in [0,10] for z in [3.70,6.50]]
for _ in range(3):
 uv=[world_to_camera_view(scene,cam,p) for p in corners];xmin=min(p.x for p in uv);xmax=max(p.x for p in uv);ymin=min(p.y for p in uv);ymax=max(p.y for p in uv)
 cam.data.lens*=min(.94/(xmax-xmin),.96/(ymax-ymin));bpy.context.view_layer.update()
 for axis in ['x','y']:
  uv=[world_to_camera_view(scene,cam,p) for p in corners];centeruv=(min(getattr(p,axis) for p in uv)+max(getattr(p,axis) for p in uv))/2
  orig=getattr(world_to_camera_view(scene,cam,Vector((0,0,0))),axis);attr='shift_'+axis;setattr(cam.data,attr,getattr(cam.data,attr)+.01);bpy.context.view_layer.update();deriv=(getattr(world_to_camera_view(scene,cam,Vector((0,0,0))),axis)-orig)/.01;setattr(cam.data,attr,getattr(cam.data,attr)+(.5-centeruv)/deriv-.01)
 bpy.context.view_layer.update()
proj=cam.calc_matrix_camera(bpy.context.evaluated_depsgraph_get(),x=880,y=1320)@cam.matrix_world.inverted()
def screen(p):
 v=proj@Vector((*p,1));return[(v.x/v.w+1)/2,(1-v.y/v.w)/2]
(ROOT/'assets/projection.json').write_text(json.dumps({'width':880,'height':1320,'matrix':[list(row) for row in proj@board],'boardTransform':[list(row) for row in board],'cameraPositionLocal':list(board.inverted()@cam.location),'displays':{k:[screen(p) for p in ps] for k,ps in displays.items()},'ballIndicators':[screen(pt(x,head_y+.49,4.15)) for x in [4.71,4.95,5.19]],'depthRange':100,'depthEncoding':'Cycles camera-axis Z, uint16 in PNG RG, 100 units','physicalPitchDegrees':6.5},indent=2))
d=bpy.data.lights.new('Product / dedicated backbox softbox','AREA');d.energy=230;d.shape='RECTANGLE';d.size=6;d.size_y=3;d.color=(.82,.9,1);o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o);o.location=(0,-8,9);o.rotation_euler=(Vector((0,8,5))-o.location).to_track_quat('-Z','Y').to_euler()
scene['precision_pass']='4.0';scene['channel_scope']='One shared 3D spline: physical shooter sensor, guided elevated travel, floor exit to Box2D'
scene.render.threads_mode='FIXED';scene.render.threads=4;scene.cycles.use_denoising=False
for c in [static,foreground,interactive,dynamic,cover]:c.hide_render=False
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/ferrisariato-precision.blend'))
print('PRECISION_SCENE_SAVED',len(scene.objects),flush=True)

exec(compile((ROOT/"blender/refine_apron.py").read_text(),str(ROOT/"blender/refine_apron.py"),"exec"))
