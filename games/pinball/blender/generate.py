"""blender -b -t 4 --python games/pinball/blender/generate.py
One layout, one fixed camera, deterministic geometry; no external assets.
The official logo is copied byte-for-byte from the existing HOME assets.
"""
import bpy, math, json, random, sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'blender'))
from props import Props
DATA=json.loads((ROOT/'layout.json').read_text())
OUT=ROOT/'assets'; OUT.mkdir(exist_ok=True)
random.seed(17)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name!='Collection': bpy.data.collections.remove(c)
scene=bpy.context.scene
scene.render.engine='CYCLES'; scene.cycles.samples=64; scene.cycles.use_denoising=False
scene.render.threads_mode='FIXED'; scene.render.threads=4
scene.render.resolution_x=880; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
scene.render.film_transparent=True; bpy.context.preferences.filepaths.save_version=0
scene.render.image_settings.file_format='PNG'; scene.render.image_settings.color_mode='RGBA'
scene.render.film_transparent=True
scene.world.color=(.25,.25,.25)
scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast'

def mat(name,color,metal=0,rough=.35,emission=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    if emission:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
    return m
blue=mat('Ferrisariato cobalt enamel',(.009,.055,.35),.65,.25)
navy=mat('Deep navy',(.006,.015,.06),.45,.25)
gold=mat('Safety yellow enamel',(.95,.55,.012),.5,.23)
steel=mat('Polished chrome',(.55,.65,.77),.95,.18)
white=mat('Ivory paint',(.84,.82,.69),.12,.35)
black=mat('Rubber',(.012,.017,.022),0,.45)
wood=mat('Cut pine',(.45,.25,.10),0,.65)
brick=mat('Terracotta',(.55,.13,.055),0,.6)
green=mat('Plant leaves',(.055,.22,.025),.05,.4)
light=mat('Warm cabinet bulbs',(1,.48,.015),.1,.23,5)
window=mat('House warm glazing',(1,.58,.06),.1,.25,2)
floor=mat('Mineral concrete',(.25,.26,.24),.18,.42)
n=floor.node_tree.nodes; links=floor.node_tree.links
noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=38
bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.05
links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],n.get('Principled BSDF').inputs['Normal'])
glass=mat('Translucent elevated ramp',(.018,.14,.65),.45,.12)
glass.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=.82
clear=mat('Clear acrylic channel walls',(.72,.84,1),0,.08)
clear.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=.96
concrete=mat('Rough concrete blocks',(.32,.34,.31),0,.8)
cardboard=mat('Shipping cardboard',(.48,.32,.15),0,.75)
orange=mat('Safety cone orange',(1,.12,.005),.1,.32)
leaf=mat('Palm leaf light side',(.12,.32,.025),0,.45)
soil=mat('Potting soil',(.045,.024,.009),0,.9)
# Procedural timber grain and concrete pores remain editable in the .blend.
for material,scale,strength in [(wood,7,.17),(concrete,45,.32)]:
    nodes=material.node_tree.nodes;links=material.node_tree.links
    texture=nodes.new('ShaderNodeTexNoise');texture.inputs['Scale'].default_value=scale
    bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=strength;bump.inputs['Distance'].default_value=.04
    links.new(texture.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],nodes.get('Principled BSDF').inputs['Normal'])
    if material==wood:
        coords=nodes.new('ShaderNodeTexCoord');stretch=nodes.new('ShaderNodeVectorMath');stretch.operation='MULTIPLY';stretch.inputs[1].default_value=(4,1,14)
        links.new(coords.outputs['Generated'],stretch.inputs[0]);links.new(stretch.outputs[0],texture.inputs['Vector'])
        ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.17,.075,.021,1);ramp.color_ramp.elements[1].color=(.62,.40,.19,1)
        links.new(texture.outputs['Fac'],ramp.inputs[0]);links.new(ramp.outputs[0],nodes.get('Principled BSDF').inputs['Base Color'])

foreground=bpy.data.collections.new('Foreground decorative raised channels');scene.collection.children.link(foreground)
dynamic=bpy.data.collections.new('Movable elements');scene.collection.children.link(dynamic)
interactive=bpy.data.collections.new('Interactive bumper tank target sling art');scene.collection.children.link(interactive)
def place(obj,name,material,collection=None):
    obj.name=name
    if material:obj.data.materials.append(material)
    if collection:
        for c in list(obj.users_collection):c.objects.unlink(obj)
        collection.objects.link(obj)
    return obj
def pt(x,y,z=0):return (x-5,8-y,z)
def bevel(o,amount=.06):
    m=o.modifiers.new('Machined edges','BEVEL');m.width=amount;m.segments=3
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');return o
def cube(name,x,y,z,sx,sy,sz,m,collection=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=pt(x,y,z));o=bpy.context.object;o.scale=(sx,sy,sz)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return bevel(place(o,name,m,collection),min(.055,sz/4))
def cyl(name,x,y,z,r,depth,m,collection=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=depth,location=pt(x,y,z));o=place(bpy.context.object,name,m,collection)
    for p in o.data.polygons:p.use_smooth=True
    return bevel(o,.025)
def sphere(name,x,y,z,r,m,collection=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=r,location=pt(x,y,z));o=place(bpy.context.object,name,m,collection)
    for p in o.data.polygons:p.use_smooth=True
    return o
def line(name,points,r,m,collection=None):
    curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.bevel_depth=r;curve.bevel_resolution=3
    s=curve.splines.new('POLY');s.points.add(len(points)-1)
    for p,v in zip(s.points,points):p.co=(*pt(*v),1)
    obj=bpy.data.objects.new(name,curve);(collection or scene.collection).objects.link(obj);obj.data.materials.append(m);return obj
def polygon(name,verts,z,m,collection=None):
    mesh=bpy.data.meshes.new(name);mesh.from_pydata([pt(x,y,z) for x,y in verts],[],[list(reversed(range(len(verts))))]);mesh.update()
    obj=bpy.data.objects.new(name,mesh);(collection or scene.collection).objects.link(obj);obj.data.materials.append(m);return obj
def arrow(x,y,size=.45,m=gold):
    return polygon('Directional inlay',[(x-size/2,y+.3),(x,y-.3),(x+size/2,y+.3),(x,y+.1)],.045,m)
def house_icon(x,y,z,s=.35):
    # Generic house pictogram; never used in place of the official wordmark.
    polygon('House pictogram',[(x-s,y),(x-s,y+s*.7),(x+s,y+s*.7),(x+s,y),(x,y-s*.8)],z,white)
    cube('House icon doorway',x,y+s*.4,z+.005,s*.35,s*.6,.008,blue)
def plant(x,y,size=.6):
    cyl('Terracotta pot',x,y,.2,size*.3,.4,brick)
    for i in range(11):
        a=i*2.4;r=size*random.uniform(.3,.7)
        o=sphere('Leaf',x+math.cos(a)*r*.45,y+math.sin(a)*r*.45,.5+random.random()*.25,.2,green)
        o.scale=(.37,.5,2.4);o.rotation_euler=(math.sin(a)*.7,math.cos(a)*.7,a)
def bricks(x,y):
    for k in range(3):
        for j in range(2):
            for i in range(2):cube('Stacked brick',x+i*.3+(k%2)*.1,y+j*.24,.12+k*.22,.28,.22,.20,brick)
def tool_box(x,y):
    cube('Yellow tool chest',x,y,.32,.95,.55,.6,gold)
    cube('Toolbox lid',x,y,.65,1.0,.6,.12,gold)
    line('Black handle',[(x-.22,y,.73),(x-.22,y,.86),(x+.22,y,.86),(x+.22,y,.73)],.06,black)
    for dx in [-.3,.3]:cube('Chest latch',x+dx,y+.29,.55,.09,.04,.22,steel)

props=Props(dict(cube=cube,cyl=cyl,line=line,sphere=sphere,pt=pt,wood=wood,steel=steel,white=white,navy=navy,gold=gold,blue=blue,brick=brick,black=black,green=green,leaf=leaf,soil=soil,orange=orange,concrete=concrete,cardboard=cardboard))

# Cabinet, apron and hazard details.
cube('Cabinet body',5,8,-.48,10,16.8,.9,blue)
cube('Concrete playfield',5,8,-.03,9.3,15.9,.12,floor)
for x in [.25,9.95]:
    cube('Blue side apron',x,8,.03,.28,16.6,.6,blue)
    line('Cabinet chrome edge',[(x,0,.37),(x,16.1,.37)],.065,steel)
    for y in [i*.72 for i in range(23)]:
        cyl('Cabinet / chrome fastening washer',x,y,.39,.065,.025,steel)
        cube('Cabinet / screw slot',x,y,.407,.07,.012,.006,navy)
cube('Bottom apron',5,16.2,.12,9.7,1.0,.5,blue)
for x in [1.1,8.25]:
    for y in [4.8+i*.58 for i in range(19)]:
        o=cube('Hazard stripe',x,y,.045,.42,.27,.018,gold);o.rotation_euler.z=.6
for wall in DATA['walls']:
    line('Physical steel guide',[(x,y,.18) for x,y in wall],.055,steel)
    for x,y in wall:cyl('Guide screw',x,y,.15,.09,.25,steel)
for x in [3.3,6.2]:
    for y in [5.2,6,6.8,8.9,9.7,11.2,12.1]:arrow(x,y,.42,gold if int(y*10)%2 else blue)
for y in [3.5+i*.85 for i in range(13)]:arrow(9.27,y,.5,gold)
for y in [6.8,9.0,11.5,12.4]:arrow(4.7,y,.55,gold)
polygon('Central cobalt house medallion',[(4.7+math.cos(i*math.tau/6)*.78,13.0+math.sin(i*math.tau/6)*.78) for i in range(6)],.043,blue)
house_icon(4.7,13.0,.050,.53)

# Fixed scenographic house, porch, windows, garden and sign.
cube('House foundation',4.7,2.55,.16,2.9,1.8,.3,white)
cube('House plaster',4.7,2.5,1.0,2.65,1.65,1.5,white)
for x,ang in [(4.02,-.5),(5.38,.5)]:
    roof=cube('Cobalt pitched roof',x,2.5,2.01,1.6,2.05,.12,blue);roof.rotation_euler.y=ang
    for i in range(18):
        rib=cube('Roof / standing seam rib',x,1.53+i*.114,2.075,1.60,.012,.028,blue);rib.rotation_euler.y=ang
line('Roof / ridge cap',[(4.7,1.45,2.45),(4.7,3.55,2.45)],.055,blue)
cube('Front door',4.7,3.34,.8,.43,.045,1.23,wood)
sphere('Door brass knob',4.83,3.39,.77,.035,gold)
for z in [.48,.88,1.21]:cube('Door / recessed timber panel',4.7,3.37,z,.32,.018,.25,wood)
cube('House / entrance step',4.7,3.59,.16,.65,.38,.18,white)
for x in [3.9,5.5]:
    cube('Window frame',x,3.34,1.10,.58,.06,.65,wood)
    cube('Lit window glass',x,3.39,1.1,.48,.025,.55,window)
    cube('Window mullion',x,3.42,1.1,.025,.025,.58,white)
    cube('Window mullion cross',x,3.42,1.1,.5,.025,.025,white)
for x in [2.4,2.7,3.0,3.3,6.1,6.4,6.7,7.0]:
    cube('Picket fence',x,3.4,.45,.18,.1,.75,white)
    sphere('Picket / rounded crown',x,3.4,.83,.09,white)
line('Fence rail',[(2.3,3.4,.4),(7.1,3.4,.4)],.06,white)
for x in [2.65,6.75]:props.palm(x,2.45)
for x in [3.85,5.55]:
    cube('House / raised flower bed',x,3.47,.14,.72,.25,.16,wood)
    for i in range(8):sphere('House / yellow flowers',x-.3+i*.08,3.49,.25,.045,light)
cube('Official brand sign',4.7,3.65,.63,3.4,.12,.95,blue)
logo=bpy.data.materials.new('Official provided logo / unchanged pixels');logo.use_nodes=True
nodes=logo.node_tree.nodes;nodes.clear();out=nodes.new('ShaderNodeOutputMaterial');mix=nodes.new('ShaderNodeMixShader')
trans=nodes.new('ShaderNodeBsdfTransparent');em=nodes.new('ShaderNodeEmission');tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(OUT/'logo-ferrisariato.png'));tex.image.pack()
logo.node_tree.links.new(tex.outputs['Color'],em.inputs['Color']);logo.node_tree.links.new(tex.outputs['Alpha'],mix.inputs[0]);logo.node_tree.links.new(trans.outputs[0],mix.inputs[1]);logo.node_tree.links.new(em.outputs[0],mix.inputs[2]);logo.node_tree.links.new(mix.outputs[0],out.inputs[0])
bpy.ops.mesh.primitive_plane_add(size=1,location=pt(4.7,3.72,.63));o=place(bpy.context.object,'Official logo image plane',logo);o.rotation_euler.x=math.pi/2;o.scale=(3.15,3.15*348/1051,1)
bpy.ops.mesh.primitive_plane_add(size=1,location=pt(5,16.2,.38));o=place(bpy.context.object,'Official apron logo / unchanged image',logo);o.scale=(2.75,2.75*348/1051,1)
for x in [1.5,8.3]:polygon('Apron / yellow chevron',[(x-.6,15.72),(x+.1,15.72),(x+.65,16.62),(x-.05,16.62)],.38,gold)

before_interactive=set(scene.objects)
for o in DATA['bumpers']:
    x,y,r=o['x'],o['y'],o['radius']
    polygon(o['id']+' blue hexagonal footprint',[(x+math.cos(i*math.tau/6)*(r+.25),y+math.sin(i*math.tau/6)*(r+.25)) for i in range(6)],.05,blue)
    for i in range(6):
        a=i*math.tau/6;polygon('Bumper / yellow hex corner',[(x+math.cos(a)*(r+.26),y+math.sin(a)*(r+.26)),(x+math.cos(a+.30)*(r+.17),y+math.sin(a+.30)*(r+.17)),(x+math.cos(a-.30)*(r+.17),y+math.sin(a-.30)*(r+.17))],.052,gold)
    cyl(o['id']+' hazard base',x,y,.09,r+.12,.12,gold)
    cyl(o['id']+' dark plinth',x,y,.16,r+.08,.16,navy)
    if o['kind']=='main':
        cyl(o['id']+' illuminated core',x,y,.4,r*.91,.4,gold)
        cyl(o['id']+' chrome rim',x,y,.64,r,.10,steel)
        cyl(o['id']+' blue cap',x,y,.71,r*.87,.08,blue)
        house_icon(x,y,.756,r*.5)
        for a in range(12):
            t=a*math.tau/12;cyl('Bumper light slit',x+math.cos(t)*r*.89,y+math.sin(t)*r*.89,.42,.045,.20,light)
    else:
        cyl(o['id']+' tank',x,y,.5,r*.88,.82,white)
        for z in [.14,.94]:cyl('Tank steel hoop',x,y,z,r,.06,steel)
        cyl('Tank blue lid',x,y,.96,r*.91,.06,blue)
        cyl('Tank lid knob',x,y,1.04,.065,.09,steel)
        house_icon(x,y,.997,.22)
        props.text('Bumper tank / front blue house','⌂',x,y+r*.9,.35,.35,blue,True)

for o in DATA['targets']:
    x,y=o['x'],o['y'];cube(o['id'],x,y,.38,.70,.40,.75,blue)
    for dx in [-.34,.34]:cube('Target chrome border',x+dx,y+.22,.38,.035,.045,.75,steel)
    for dx in [-.27,.27]:
        for zz in [.12,.66]:sphere('Target / panel screw',x+dx,y+.235,zz,.025,steel)
    cyl('Target golden lamp',x,y+.28,.08,.12,.10,gold)
    # Numbered modules until symbols are drawn by the UI overlay.
for o in DATA['slings']:
    mesh=polygon(o['id'],o['vertices'],.38,blue);solid=mesh.modifiers.new('Sling depth','SOLIDIFY');solid.thickness=.35;bevel(mesh,.06)
    line('Sling yellow rubber',[(x,y,.39) for x,y in o['vertices']+[o['vertices'][0]]],.07,gold)
    x=sum(p[0] for p in o['vertices'])/3;y=sum(p[1] for p in o['vertices'])/3
    sphere('Slingshot warm lamp',x,y,.49,.13,light)
    for x,y in o['vertices']:sphere('Sling screw',x,y,.43,.07,steel)

for obj in set(scene.objects)-before_interactive:
    for collection in list(obj.users_collection):collection.objects.unlink(obj)
    interactive.objects.link(obj)

# Full decorative inventory, grouped by the reference image's visible zones.
# None of these assemblies create a physics fixture.
props.pallet(1.30,3.4,.95,.75);props.blocks(1.30,3.4,.40,3);props.plant(.95,4.0,scale=.75)
props.pallet(7.95,3.65,.95,.85);props.bucket(7.45,3.0,.27,.32,.65);props.plant(8.12,3.8,.26,.85)
props.pallet(1.6,6.1,1.15,1.0);props.timber(1.60,6.05,.4);props.plant(2.15,5.7,.27,.85)
props.pallet(1.10,7.25,.90,.75);props.bricks(1.10,7.25,.36)
props.crate(1.32,7.95,.8,.65,.52,.04);props.tape(2.05,7.95,.10)
cube('Small blue industrial toolbox',2.0,6.8,.35,.48,.45,.55,blue);props.hand_tools(1.7,6.7,.65)
props.pallet(7.8,7.3,1.0,.85);props.crate(7.8,7.3,.9,.72,.72,.25);props.drill(7.8,7.3,1.0)
props.bucket(7.2,5.7,.04,.28,.63);props.bucket(7.75,6.05,.02,.32,.70)
props.box(7.65,6.65,.35,.55,.6)
props.pallet(1.20,10.4,1.15,.85);props.toolbox(1.2,10.4,.28)
props.pallet(.98,9.15,.85,.65);props.bricks(.98,9.15,.36,3);props.plant(1.85,9.7,.10,.8)
props.bucket(2.55,10.7,.04,.28,.65)
props.wheelbarrow(7.78,9.85,.04)
props.pallet(7.95,11.2,.95,.75);props.blocks(7.95,11.2,.40,4)
props.cone(8.1,12.5,.05)
# Exposed industrial guard rails, polished stanchions, collars, and bulbs.
for x,y0,y1 in [(1.0,3.2,5.1),(2.4,5.2,6.8),(1.7,9.2,11.0),(7.05,5.0,7.4),(7.05,9.3,11.1),(8.1,12.8,14.6)]:
    for zz in [.35,.72]:line('Industrial guard / horizontal tube',[(x,y0,zz),(x,y1,zz)],.025,steel)
    for i in range(5):
        y=y0+(y1-y0)*i/4;cyl('Industrial guard / chrome post',x,y,.39,.035,.77,steel)
        cyl('Industrial guard / foot collar',x,y,.08,.085,.08,steel);sphere('Industrial guard / post cap',x,y,.8,.055,steel)
for x in [2.0,7.5]:
    for y in [3.7,4.8]:
        cyl('Warm safety beacon / column',x,y,.45,.11,.85,gold);sphere('Warm safety beacon / lamp',x,y,.92,.10,light)

# Elevated decorative translucent lanes, their rails and supporting posts.
for side in ['left','right']:
    path=[]
    for i in range(80):
        y=1.7+i*(8.2 if side=='left' else 4.0)/79
        x=(1.45+.65*math.sin((y-1.7)*.8)) if side=='left' else (8.05+.50*math.sin((y-1.7)*.85))
        z=1.18+.55*(1-i/79);path.append((x,y,z))
    mesh=bpy.data.meshes.new('Curved ramp mesh');verts=[]
    for x,y,z in path:verts.extend([pt(x-.35,y,z),pt(x+.35,y,z)])
    mesh.from_pydata(verts,[],[(i*2,i*2+1,i*2+3,i*2+2) for i in range(len(path)-1)]);mesh.update()
    o=bpy.data.objects.new('Decorative channel '+side,mesh);foreground.objects.link(o);o.data.materials.append(glass)
    solid=o.modifiers.new('Transparent channel thickness','SOLIDIFY');solid.thickness=.04
    for offset in [-.38,.38]:
        points=[]
        for x,y,z in path:points.extend([pt(x+offset,y,z),pt(x+offset,y,z+.24)])
        wallmesh=bpy.data.meshes.new('Acrylic channel upright');wallmesh.from_pydata(points,[],[(i*2,i*2+1,i*2+3,i*2+2) for i in range(79)]);wallmesh.update()
        wall=bpy.data.objects.new('Transparent channel / acrylic wall',wallmesh);foreground.objects.link(wall);wall.data.materials.append(clear)
        thick=wall.modifiers.new('Acrylic thickness','SOLIDIFY');thick.thickness=.018
        line('Elevated chrome balustrade',[(x+offset,y,z+.27) for x,y,z in path],.035,steel,foreground)
        line('Channel blue lip',[(x+offset,y,z) for x,y,z in path],.055,blue,foreground)
        for i in range(0,80,8):
            x,y,z=path[i];line('Ramp support post',[(x+offset,y,.05),(x+offset,y,z+.3)],.035,steel,foreground)
            sphere('Ramp glowing bulb',x+offset,y,z+.31,.065,light,foreground)
            cyl('Ramp support / base foot',x+offset,y,.07,.09,.10,steel,foreground)
            cyl('Ramp support / gold clamp',x+offset,y,z-.08,.07,.12,gold,foreground)
    for i in range(5,75,10):
        x,y,z=path[i];polygon('Elevated lane / arrow inlay',[(x-.18,y+.24),(x,y-.20),(x+.18,y+.24),(x,y+.06)],z+.028,gold,foreground)

# Camera and scene lighting, reused for all layers and projection.
bpy.ops.object.camera_add(location=(0,-17.8,25.5));cam=bpy.context.object;cam.name='Fixed reference camera'
direction=Vector((0,0,.1))-cam.location;cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
cam.data.type='PERSP';cam.data.lens=49;scene.camera=cam
for name,loc,power,size in [('Softbox',(0,-6,13),1500,10),('Warm left',(-7,2,8),1000,7),('Rim right',(7,4,10),1300,6)]:
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size
    o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
for x,y in [(2.2,4.8),(7.2,4.8),(3.2,7.8),(6.2,7.8),(1.2,12.1),(8.0,12.1)]:
    bpy.ops.object.light_add(type='POINT',location=pt(x,y,.65));o=bpy.context.object;o.name='Warm playfield accent';o.data.energy=12;o.data.color=(1,.55,.1);o.data.shadow_soft_size=.2
bpy.context.view_layer.update()
# Fit the entire cabinet and house in the fixed camera, with a small chrome
# border margin. Derive framing from the geometry instead of image cropping.
corners=[Vector(pt(x,y,z)) for x in [0,10.15] for y in [-.4,16.8] for z in [-.9,.4]]+[Vector(pt(4.7,1.5,2.5))]
coords=[world_to_camera_view(scene,cam,p) for p in corners]
cam.data.lens*=min(.95/(max(p.x for p in coords)-min(p.x for p in coords)),.95/(max(p.y for p in coords)-min(p.y for p in coords)))
for axis,attribute in [('x','shift_x'),('y','shift_y')]:
    coords=[world_to_camera_view(scene,cam,p) for p in corners]
    mid=(min(getattr(p,axis) for p in coords)+max(getattr(p,axis) for p in coords))/2
    origin=getattr(world_to_camera_view(scene,cam,Vector((0,0,0))),axis)
    old=getattr(cam.data,attribute);setattr(cam.data,attribute,old+.01)
    derivative=(getattr(world_to_camera_view(scene,cam,Vector((0,0,0))),axis)-origin)/.01
    setattr(cam.data,attribute,old+(.5-mid)/derivative)
proj=cam.calc_matrix_camera(bpy.context.evaluated_depsgraph_get(),x=880,y=1100) @ cam.matrix_world.inverted()
(OUT/'projection.json').write_text(json.dumps({'width':880,'height':1100,'matrix':[list(row) for row in proj]},indent=2))

# Editable scene keeps every object and embedded logo. Live objects are a
# separate collection; camera-space mapping is exported for the game renderer.
for o in DATA['flippers']:
    x,y=o['x'],o['y'];end=(x+o['length']*math.cos(o['rest']),y+o['length']*math.sin(o['rest']))
    line('Editable '+o['id']+' flipper',[(x,y,.25),(*end,.25)],.14,blue,dynamic)
    line('Editable '+o['id']+' flipper white inset',[(x,y,.37),(*end,.37)],.10,white,dynamic)
sphere('Editable chrome ball',*DATA['spawn'],DATA['ballRadius'],DATA['ballRadius'],steel,dynamic)
(OUT/'scene-inventory.json').write_text(json.dumps({'objects':len(scene.objects),'shared_meshes':sum(1 for m in bpy.data.meshes if m.users>1),'collections':{c.name:len(c.objects) for c in bpy.data.collections},'object_names':[o.name for o in scene.objects]},indent=2))
dynamic.hide_render=True
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender'/'ferrisariato-pinball.blend'))
foreground.hide_render=True
interactive.hide_render=True
scene.render.filepath=str(OUT/'table.png');bpy.ops.render.render(write_still=True)
# Independent alpha layers share the exact camera. Other geometry continues
# to provide reflections and shadow context without appearing in the layer.
interactive.hide_render=False
for layer,name in [(interactive,'interactives'),(foreground,'foreground')]:
    foreground.hide_render=layer!=foreground
    hidden=[]
    for o in scene.objects:
        if o.type not in {'LIGHT','CAMERA'} and o.name not in layer.objects:
            if hasattr(o,'visible_camera'):hidden.append(o);o.visible_camera=False
    scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
    for o in hidden:o.visible_camera=True
foreground.hide_render=False
# Preserve the editable full scene with the original scene visibility.
dynamic.hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender'/'ferrisariato-pinball.blend'))
print('PINBALL_RENDER_COMPLETE')
