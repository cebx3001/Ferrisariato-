"""Non-destructive photographic art pass over the original editable scene.
blender -b blender/ferrisariato-pinball.blend -t 4 --python blender/photographic.py
Writes a SECOND .blend; never modifies the physics layout, camera or base scene.
"""
import bpy, math, random, json, sys, ast
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'blender'))
from props import Props
scene=bpy.context.scene
if scene.get('photographic_pass'):raise RuntimeError('Load the original ferrisariato-pinball.blend, not the enhanced scene')
random.seed(243)
# Reuse exactly the original modeling helpers without executing its scene reset.
source=ast.parse((ROOT/'blender/generate.py').read_text())
for node in source.body:
    if isinstance(node,ast.FunctionDef) and node.name in {'mat','place','pt','bevel','cube','cyl','sphere','line','polygon'}:exec(compile(ast.Module(body=[node],type_ignores=[]),'geometry-helpers','exec'))
lookup={'blue':'Ferrisariato cobalt enamel','navy':'Deep navy','gold':'Safety yellow enamel','steel':'Polished chrome','white':'Ivory paint','black':'Rubber','wood':'Cut pine','brick':'Terracotta','green':'Plant leaves','light':'Warm cabinet bulbs','window':'House warm glazing','floor':'Mineral concrete','glass':'Translucent elevated ramp','clear':'Clear acrylic channel walls','concrete':'Rough concrete blocks','cardboard':'Shipping cardboard','orange':'Safety cone orange','leaf':'Palm leaf light side','soil':'Potting soil'}
for key,name in lookup.items():globals()[key]=bpy.data.materials[name]
props=Props({k:globals()[k] for k in ['cube','cyl','line','sphere','pt','wood','steel','white','navy','gold','blue','brick','black','green','leaf','soil','orange','concrete','cardboard']})
original=set(scene.objects)
photo=bpy.data.collections.new('Photographic workshop miniatures');scene.collection.children.link(photo)
cover=bpy.data.collections.new('Protective glass reflections');scene.collection.children.link(cover)
interactive=bpy.data.collections['Interactive bumper tank target sling art']
foreground=bpy.data.collections['Foreground decorative raised channels']
dynamic=bpy.data.collections['Movable elements']
DATA=json.loads((ROOT/'layout.json').read_text())

def pbr(m,color=None,metal=None,rough=None,coat=None):
    p=m.node_tree.nodes.get('Principled BSDF')
    for name,value in [('Base Color',(*color,1) if color else None),('Metallic',metal),('Roughness',rough),('Coat Weight',coat)]:
        if value is not None:p.inputs[name].default_value=value
    return p

def texture(m,scale,lo,hi,strength=.12,distance=.015,stretch=None):
    n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
    coord=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=4;noise.inputs['Roughness'].default_value=.7
    if stretch:
        v=n.new('ShaderNodeVectorMath');v.operation='MULTIPLY';v.inputs[1].default_value=stretch;l.new(coord.outputs['Object'],v.inputs[0]);l.new(v.outputs[0],noise.inputs['Vector'])
    else:l.new(coord.outputs['Object'],noise.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.23;ramp.color_ramp.elements[0].color=(*lo,1);ramp.color_ramp.elements[1].position=.78;ramp.color_ramp.elements[1].color=(*hi,1)
    l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color'])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=strength;bump.inputs['Distance'].default_value=distance;l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal'])
    return noise

pbr(blue,(.006,.032,.22),.24,.20,.65);pbr(navy,(.003,.008,.025),.25,.23,.4)
pbr(gold,(1,.57,.006),.18,.22,.55);pbr(steel,(.72,.79,.85),1,.12,.12)
pbr(white,(.78,.81,.78),.05,.28,.25);pbr(black,(.008,.011,.014),0,.61,0)
pbr(floor,metal=0,rough=.62);texture(floor,5,(.12,.13,.125),(.34,.35,.32),.25,.023)
# Separate fine mineral pores layered over larger aggregate; physical scale.
n=floor.node_tree.nodes;l=floor.node_tree.links;p=n.get('Principled BSDF');existing=p.inputs['Normal'].links[0].from_socket
fine=n.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=420
b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.18;b.inputs['Distance'].default_value=.006;l.new(fine.outputs['Fac'],b.inputs['Height']);l.new(existing,b.inputs['Normal']);l.new(b.outputs[0],p.inputs['Normal'])
texture(concrete,34,(.18,.19,.17),(.44,.45,.4),.4,.025)
texture(wood,3,(.19,.07,.021),(.63,.39,.15),.19,.018,(9,1,28))
texture(brick,23,(.25,.045,.013),(.65,.18,.06),.3,.013)
texture(black,160,(.006,.009,.012),(.018,.025,.028),.2,.004)
for m in [green,leaf]:
    p=pbr(m,rough=.36);p.inputs['Subsurface Weight'].default_value=.08;p.inputs['Subsurface Radius'].default_value=(.1,.3,.05)
    texture(m,4,(.012,.055,.004),(.12,.30,.018),.1,.008,(1,6,1))
# Microscopic brushed variations do not obscure the recognizable lamp reflections.
n=steel.node_tree.nodes;l=steel.node_tree.links;p=n.get('Principled BSDF');t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=230
r=n.new('ShaderNodeMapRange');r.inputs['To Min'].default_value=.085;r.inputs['To Max'].default_value=.18;l.new(t.outputs['Fac'],r.inputs[0]);l.new(r.outputs[0],p.inputs['Roughness'])
p=pbr(glass,(.035,.17,.48),0,.055,.3);p.inputs['Transmission Weight'].default_value=.85;p.inputs['IOR'].default_value=1.46
p=pbr(clear,(.88,.95,1),0,.035);p.inputs['Transmission Weight'].default_value=1;p.inputs['IOR'].default_value=1.46
pbr(window,rough=.17).inputs['Emission Strength'].default_value=3
pbr(light,rough=.2).inputs['Emission Strength'].default_value=9
amber=mat('Opal amber illuminated inserts',(1,.51,.018),0,.22,4)
blue_led=mat('Ice blue LED strip',(.035,.23,1),0,.2,4)
porcelain=mat('Porcelain warm lamp',(1,.75,.32),0,.18,12)
kraft=mat('Mortar sacks / kraft fibers',(.57,.43,.25),0,.85)
texture(kraft,90,(.32,.22,.12),(.66,.52,.31),.18,.008)
paint=mat('Spilled cobalt latex',(.008,.07,.45),0,.31,.0)
metal_dark=mat('Brushed aluminum mechanisms',(.22,.28,.32),.95,.27)

# All original lamp geometry becomes a real local source of illumination.
for o in list(scene.objects):
    if o.type=='LIGHT':bpy.data.objects.remove(o,do_unlink=True)
scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs[0].default_value=(.13,.19,.3,1);scene.world.node_tree.nodes.get('Background').inputs[1].default_value=.12

def point_light(name,x,y,z,power=3,color=(1,.55,.13),radius=.055):
    data=bpy.data.lights.new(name,'POINT');data.energy=power;data.color=color;data.shadow_soft_size=radius
    o=bpy.data.objects.new(name,data);scene.collection.objects.link(o);o.location=pt(x,y,z);return o

def area(name,location,target,power,color,size,size_y):
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.color=color;data.shape='RECTANGLE';data.size=size;data.size_y=size_y
    o=bpy.data.objects.new(name,data);scene.collection.objects.link(o);o.location=location;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
area('Product / overhead strip',(-4,-1,9),(0,0,0),540,(.79,.88,1),2,11)
area('Product / warm softbox',(4,3,8),(0,0,0),420,(1,.81,.56),3,8)
area('Product / front fill',(1,-10,7),(0,0,0),230,(.68,.80,1),5,3)
area('Product / back rim',(0,10,7),(0,0,0),650,(.64,.77,1),7,2)
for o in list(scene.objects):
    if o.type in {'MESH','CURVE'} and any(m==light for m in o.data.materials):
        # Local point lights pair with emission, not a post-process-only glow.
        loc=o.location if o.type=='MESH' else None
        if loc is not None:point_light('Practical / '+o.name,loc.x+5,8-loc.y,loc.z+.035,1.8 if 'Ramp' in o.name else 3.2)
for x in [.55,8.65]:
    for i in range(23):
        y=.75+i*.62
        cyl('Practical / brass lamp socket',x,y,.27,.08,.13,metal_dark)
        sphere('Practical / warm bulb',x,y,.37,.062,porcelain)
        point_light('Practical / side rail incandescent',x,y,.42,2.4)
for o in list(scene.objects):
    if o.name.startswith('Directional inlay'):
        o.data.materials.clear();o.data.materials.append(amber)
        solid=o.modifiers.new('Translucent resin thickness','SOLIDIFY');solid.thickness=.022
        center=sum((v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
        point_light('Practical / floor insert',center.x+5,8-center.y,.16,1.3,radius=.12)
for o in DATA['bumpers']:
    x,y,r=o['x'],o['y'],o['radius']
    for i in range(8):
        a=i*math.tau/8;point_light('Practical / bumper underlight',x+math.cos(a)*(r+.04),y+math.sin(a)*(r+.04),.23,1.5)
    for item in interactive.objects:
        if item.name.startswith(o['id']+' illuminated core'):item.data.materials.clear();item.data.materials.append(amber)
for o in DATA['targets']:
    point_light('Practical / target pedestal',o['x'],o['y']+.35,.19,2.5)
for o in scene.objects:
    if o.name.startswith('Target golden lamp'):o.data.materials.clear();o.data.materials.append(amber)
for x in [3.9,5.5]:point_light('Practical / porch window',x,3.62,1.13,4,(1,.6,.2),.18)
for x in [2.8,6.6]:
    cyl('Garden / bollard',x,3.1,.28,.055,.5,navy);sphere('Garden / opal globe',x,3.1,.55,.1,porcelain);point_light('Practical / garden globe',x,3.1,.62,3)
# Concealed blue lighting has genuine blue reflections on rails/acrylic.
for x in [.65,8.5]:
    for y in [2.5,5.2,8,10.8,13.4]:point_light('Practical / blue cabinet wash',x,y,.14,2.0,(.025,.16,1),.12)

# Carpenter cluster: saw, square, clamps, screw cartons and extended tape.
def saw(x,y,z):
    vertices=[(x-.42,y-.08),(x+.28,y-.05),(x+.30,y+.12),(x-.42,y+.17)]
    polygon('Carpentry / polished saw blade',vertices,z,steel)
    for i in range(18):polygon('Carpentry / triangular saw tooth',[(x-.4+i*.038,y+.16),(x-.38+i*.038,y+.20),(x-.36+i*.038,y+.16)],z,steel)
    line('Carpentry / saw handle',[(x+.24,y-.05,z),(x+.47,y-.10,z),(x+.52,y+.18,z),(x+.29,y+.17,z)],.045,gold)
def clamp(x,y,z):
    line('Carpentry / C clamp',[(x-.1,y,z+.20),(x-.2,y,z+.20),(x-.2,y,z-.06),(x+.07,y,z-.06)],.028,metal_dark)
    line('Carpentry / clamp screw',[(x-.03,y,z-.14),(x-.03,y,z+.15)],.016,steel)
    line('Carpentry / clamp T handle',[(x-.13,y,z-.13),(x+.07,y,z-.13)],.017,steel)
def sack(x,y,z,angle=0):
    o=cube('Masonry / creased mortar sack',x,y,z,.62,.42,.22,kraft);o.rotation_euler.z=angle
    line('Masonry / folded sack seam',[(x-.26,y+.2,z+.03),(x+.26,y+.2,z+.03)],.015,cardboard)
    props.text('Masonry / cement sack label','MORTERO',x,y,z+.116,.085,navy)
    for dx in [-.24,.24]:line('Masonry / sack stitched end',[(x+dx,y-.17,z+.11),(x+dx,y+.17,z+.11)],.008,white)
def trowel(x,y,z):
    polygon('Masonry / trowel blade',[(x-.13,y-.19),(x+.14,y-.19),(x,y+.17)],z,steel)
    line('Masonry / trowel curved tang',[(x,y,z),(x,y+.10,z+.08),(x,y+.25,z+.08)],.018,steel)
    line('Masonry / trowel rubber grip',[(x,y+.22,z+.08),(x,y+.42,z+.08)],.035,black)
# Left shoulder remains outside the original playable guide.
props.pallet(1.12,4.65,.85,.72);sack(1.12,4.65,.41);sack(1.16,4.67,.64,.1);props.block(.83,5.25,.22)
sack(.9,8.25,.16);sack(1.05,8.28,.4,-.12);trowel(1.17,8.3,.54)
saw(1.5,6.07,.94);clamp(1.92,6.28,.85)
line('Carpentry / steel square',[(1.25,5.5,.95),(1.25,6.1,.95),(1.62,6.1,.95)],.025,steel)
props.box(.86,5.65,.23,.35,.35)
for i in range(5):
    o=cube('Carpentry / irregular timber offcut',.85+i*.13,6.6,.10+(i%2)*.045,.11,.38+random.random()*.2,.09,wood);o.rotation_euler.z=random.uniform(-.2,.2)
# Additional masonry close to existing pallets, with chips and a trowel.
props.bricks(.93,11.25,.15,2);sack(1.23,11.65,.14,.08);trowel(1.2,11.63,.27)
for x,y in [(.85,7.7),(1.5,8.6),(.93,11.5),(8.16,10.9)]:
    for i in range(12):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=random.uniform(.022,.06),location=pt(x+random.uniform(-.22,.22),y+random.uniform(-.18,.18),.075));o=bpy.context.object;o.name='Masonry / scattered brick chip';o.scale=(1.5,.8,.6);o.data.materials.append(brick if i%2 else concrete)
# Paint station with open pans, bristles, rollers and pigment spills.
props.bucket(8.17,4.9,.04,.23,.48);props.bucket(7.56,5.08,.04,.18,.35)
def brush(x,y,z):
    cube('Painting / wooden brush handle',x,y,z,.055,.27,.045,wood)
    cube('Painting / crimped metal ferrule',x,y+.16,z,.15,.09,.055,steel)
    cube('Painting / natural bristle bundle',x,y+.27,z,.145,.15,.045,kraft)
    for i in range(9):line('Painting / individual brush bristles',[(x-.066+i*.016,y+.2,z+.025),(x-.066+i*.016,y+.36,z+.025)],.0035,wood)
for x,y in [(7.9,5.1),(8.16,5.65)]:
    cube('Painting / tray bottom',x,y,.07,.42,.62,.045,black)
    for dx in [-.21,.21]:cube('Painting / tray lip',x+dx,y,.11,.025,.62,.08,black)
    for dy in [-.31,.31]:cube('Painting / tray end',x,y+dy,.11,.43,.025,.08,black)
    cube('Painting / wet paint in pan',x,y+.10,.10,.37,.31,.02,paint)
    for i in range(6):cube('Painting / roller tray ribs',x,y-.25+i*.045,.1,.36,.012,.018,black)
brush(7.61,5.5,.13)
line('Painting / roller wire',[(8.02,5.42,.18),(8.02,5.2,.18),(7.86,5.2,.18)],.016,steel)
o=cyl('Painting / microfiber roller sleeve',7.8,5.2,.18,.062,.22,white);o.rotation_euler.y=math.pi/2
line('Painting / roller handle',[(8.02,5.42,.18),(8.02,5.65,.18)],.035,gold)
for i in range(11):
    x=7.7+random.uniform(-.18,.18);y=5.75+random.uniform(-.19,.19);cyl('Painting / latex droplets',x,y,.039,random.uniform(.012,.045),.003,paint)
# Open equipment case and recognizable tool assortment beside the drill.
x,y=7.9,8.25
cube('Tools / open case base',x,y,.13,.72,.53,.20,black)
cube('Tools / fitted foam insert',x,y,.245,.64,.45,.03,navy)
o=cube('Tools / raised hinged case lid',x,y-.30,.43,.73,.08,.48,black);o.rotation_euler.x=-.23
for dx in [-.28,.28]:cyl('Tools / case hinge barrel',x+dx,y-.25,.23,.035,.10,steel)
props.hand_tools(7.57,8.16,.29)
for i in range(7):
    line('Tools / drill bit set',[(7.65+i*.055,8.38,.28),(7.65+i*.055,8.23-(i%3)*.03,.28)],.009,steel)
props.drill(8.10,6.40,.08)
# Pliers: distinct twin red handles, hinge, and tapered steel jaws.
for sign in [-1,1]:
    line('Tools / pliers rubber handle',[(7.47+sign*.10,7.92,.09),(7.47+sign*.045,7.67,.09)],.027,orange)
    line('Tools / pliers jaw',[(7.47+sign*.045,7.67,.09),(7.47-sign*.045,7.52,.09)],.023,steel)
cyl('Tools / pliers pivot',7.47,7.66,.11,.035,.025,steel)
# Gardening cluster: pipes, bucket, soil, another pot and planting tools.
props.plant(7.18,11.55,.04,.66);props.plant(8.12,8.9,.04,.6)
props.plant(1.15,12.3,.04,.55);props.plant(8.0,13.35,.05,.45)
props.bucket(7.4,10.75,.04,.18,.35)
for i in range(4):
    x=8.22+i*.10
    line('Plumbing / loose copper tube',[(x,9.0,.10),(x,9.65,.10),(x-.09,9.74,.10)],.034,metal_dark)
    cyl('Plumbing / tube end collar',x,9.0,.1,.041,.07,steel)
props.cone(7.34,12.18,.04)
# Dense micro-hardware uses linked mesh instances, not duplicated meshes.
bolt=cyl('Hardware / master hex screw',.84,12.9,.07,.035,.07,steel)
washer=cyl('Hardware / master washer',.94,12.9,.044,.05,.01,metal_dark)
for x,y in [(1.8,6.5),(1.4,11.0),(7.55,8.0),(8.12,11.65)]:
    for i in range(9):
        props.copy(bolt,'Hardware / linked loose bolt',x-.84+random.uniform(-.2,.2),y-12.9+random.uniform(-.16,.16))
        props.copy(washer,'Hardware / linked washer',x-.94+random.uniform(-.2,.2),y-12.9+random.uniform(-.16,.16))
for x,y in [(1.05,12.9),(8.06,8.75)]:
    for j in range(4):
        line('Electrical / coiled extension cable',[(x+(.19+j*.018)*math.cos(i*math.tau/48),y+(.25+j*.018)*math.sin(i*math.tau/48),.09+j*.022) for i in range(49)],.016,orange if j%2 else black)
    cube('Electrical / cable plug',x+.25,y+.1,.09,.08,.12,.09,black)
# Architectural fascia, gutter brackets, drainpipes and clapboard joints.
for x in [3.28,6.12]:
    line('House / eaves gutter',[(x,1.46,1.72),(x,3.54,1.72)],.047,steel)
    line('House / downpipe',[(x,3.45,1.72),(x,3.47,.27),(x+.12,3.57,.20)],.032,white)
    for z in [.45,1.15]:cube('House / downpipe clamp',x,3.47,z,.09,.08,.035,steel)
for z in [.32,.47,.62,.77,.92,1.07,1.22,1.37,1.52]:
    for x in [3.37,6.03]:cube('House / siding joint',x,2.50,z,.012,1.62,.012,cardboard)
for x in [3.9,5.5]:
    cube('House / stone window sill',x,3.46,.78,.64,.17,.065,white)
    for dx in [-.30,.30]:cube('House / window jamb',x+dx,3.42,1.11,.035,.065,.69,white)
# Thin engraved joints and border profiles texture the playable floor without
# placing a false obstacle in any physical trajectory.
for y in [4.8,7.7,10.5,13.4]:
    line('Playfield / fine cast slab joint',[(1.75,y,.036),(8.55,y,.036)],.004,navy)
for x in [2.4,7.05]:
    for y in [5.0,7.8,10.4]:
        line('Playfield / hairline mineral fissure',[(x,y,.036),(x+.08,y+.18,.036),(x+.04,y+.31,.036),(x+.12,y+.43,.036)],.0025,navy)
# Mechanical housing and a genuine modeled spring in the editable product shot.
for y in [14.7,15.85]:
    cyl('Shooter / steel support bushing',9.25,y,.21,.25,.10,metal_dark)
    for dx in [-.19,.19]:cyl('Shooter / mounting screw',9.25+dx,y,.27,.032,.025,steel)
line('Shooter / polished piston',[(9.25,14.78,.23),(9.25,16,.23)],.066,steel,dynamic)
line('Shooter / helical steel spring',[(9.25+.15*math.cos(i*math.tau/24),14.9+i/240*.91,.23+.15*math.sin(i*math.tau/24)) for i in range(241)],.025,steel,dynamic)
sphere('Shooter / polished striker head',9.25,14.78,.23,.19,steel,dynamic)
# Glass fits into a physical raised metal frame. Thin-pane Fresnel reflection
# approximates negligible refraction and exports clean alpha above live bodies.
glass_m=bpy.data.materials.new('Protective glass / thin pane Fresnel');glass_m.use_nodes=True
n=glass_m.node_tree.nodes;n.clear();l=glass_m.node_tree.links
out=n.new('ShaderNodeOutputMaterial');mix=n.new('ShaderNodeMixShader');trans=n.new('ShaderNodeBsdfTransparent');gloss=n.new('ShaderNodeBsdfGlossy');fres=n.new('ShaderNodeFresnel');fres.inputs['IOR'].default_value=1.46;gloss.inputs['Roughness'].default_value=.055
l.new(fres.outputs[0],mix.inputs[0]);l.new(trans.outputs[0],mix.inputs[1]);l.new(gloss.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],out.inputs[0])
# One surface avoids counting Fresnel twice; actual thickness lives in edge strips.
pane=polygon('Protective glass / uninterrupted top pane',[(.43,.35),(9.70,.35),(9.70,15.72),(.43,15.72)],2.72,glass_m,cover)
for x in [.43,9.70]:
    line('Protective glass / polished edge',[(x,.35,2.72),(x,15.72,2.72)],.012,clear,cover)
    line('Protective glass / retaining chrome profile',[(x,.35,2.68),(x,15.72,2.68)],.025,steel,cover)
    line('Protective glass / rubber gasket',[(x,.35,2.65),(x,15.72,2.65)],.019,black,cover)
# Lower end frame with miter joins; no change to collision walls.
line('Protective glass / front clamp',[(.43,15.72,2.68),(9.70,15.72,2.68)],.035,steel,cover)
for x in [.5,9.63]:
    for y in [.5,4.2,8,11.8,15.58]:
        cyl('Protective glass / countersunk fixing',x,y,2.71,.045,.018,steel,cover)
        cube('Protective glass / screw recess',x,y,2.721,.042,.008,.003,black,cover)
# Move added set dressing into an editable collection, keeping dedicated layers.
for o in set(scene.objects)-original:
    if o.type not in {'LIGHT','CAMERA'} and o.name not in cover.objects and o.name not in dynamic.objects:
        for c in list(o.users_collection):c.objects.unlink(o)
        photo.objects.link(o)
# Render settings: fixed original camera/projection, physically traced lighting.
scene.render.engine='CYCLES';scene.cycles.samples=96;scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=.012
scene.cycles.max_bounces=12;scene.cycles.diffuse_bounces=5;scene.cycles.glossy_bounces=6;scene.cycles.transmission_bounces=8;scene.cycles.transparent_max_bounces=12
scene.cycles.sample_clamp_indirect=4;scene.cycles.use_denoising=False
scene.render.threads_mode='FIXED';scene.render.threads=5
scene.render.resolution_x=1760;scene.render.resolution_y=2200;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=True
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=.15
scene['photographic_pass']='2.0';scene['preserved_camera']='assets/projection.json unchanged';scene['glass_model']='Thin pane Fresnel reflection, alpha compatible'
scene.use_nodes=True;n=scene.node_tree.nodes;n.clear();rl=n.new('CompositorNodeRLayers');gl=n.new('CompositorNodeGlare');gl.glare_type='FOG_GLOW';gl.quality='HIGH';gl.threshold=2.0;gl.size=7;gl.mix=-.92;out=n.new('CompositorNodeComposite');scene.node_tree.links.new(rl.outputs['Image'],gl.inputs[0]);scene.node_tree.links.new(gl.outputs[0],out.inputs[0])
for c in [dynamic,interactive,foreground,cover]:c.hide_render=False
from refine_photographic import refine
refine(dict(globals()))
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/ferrisariato-photographic.blend'))
(ROOT/'assets/photographic-inventory.json').write_text(json.dumps({'objects':len(scene.objects),'lights':sum(o.type=='LIGHT' for o in scene.objects),'shared_meshes':sum(m.users>1 for m in bpy.data.meshes),'collections':{c.name:len(c.objects) for c in bpy.data.collections},'render':[1760,2200],'samples':96,'camera_unchanged':True,'object_names':[o.name for o in scene.objects]},indent=2))
print('PHOTOGRAPHIC_SCENE_SAVED',len(scene.objects),'objects')
