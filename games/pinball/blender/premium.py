"""Deterministic, additive V3 detailing over ferrisariato-photographic.blend.
Keeps the original camera and layout. Channel extensions are visual scenery.
"""
import bpy, math, random, json, sys, ast
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'blender'))
from props import Props
scene=bpy.context.scene
if scene.get('premium_pass'):raise RuntimeError('Start from the V2 photographic scene')
random.seed(43912)
for node in ast.parse((ROOT/'blender/generate.py').read_text()).body:
    if isinstance(node,ast.FunctionDef) and node.name in {'mat','place','pt','bevel','cube','cyl','sphere','line','polygon'}:exec(compile(ast.Module(body=[node],type_ignores=[]),'helpers','exec'))
# Direct datablock construction avoids thousands of global dependency-graph
# updates from operators; equal parts share their mesh, including material.
import bmesh
mesh_cache={}
def primitive(kind,name,x,y,z,dims,m,collection=None):
    key=(kind,tuple(round(d,6) for d in dims),m.name)
    if key not in mesh_cache:
        bm=bmesh.new()
        if kind=='cube':bmesh.ops.create_cube(bm,size=1)
        elif kind=='cyl':bmesh.ops.create_cone(bm,cap_ends=True,cap_tris=False,segments=32,radius1=1,radius2=1,depth=1)
        else:bmesh.ops.create_uvsphere(bm,u_segments=16,v_segments=10,radius=1)
        for v in bm.verts:
            for k in range(3):v.co[k]*=dims[k]
        me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free();me.materials.append(m)
        if kind!='cube':
            for face in me.polygons:face.use_smooth=True
        mesh_cache[key]=me
    o=bpy.data.objects.new(name,mesh_cache[key]);(collection or scene.collection).objects.link(o);o.location=pt(x,y,z)
    if kind!='sphere':bevel(o,min(.025,dims[2]/4))
    return o
def cube(name,x,y,z,sx,sy,sz,m,collection=None):return primitive('cube',name,x,y,z,(sx,sy,sz),m,collection)
def cyl(name,x,y,z,r,depth,m,collection=None):return primitive('cyl',name,x,y,z,(r,r,depth),m,collection)
def sphere(name,x,y,z,r,m,collection=None):return primitive('sphere',name,x,y,z,(r,r,r),m,collection)
lookup={'blue':'Ferrisariato cobalt enamel','navy':'Deep navy','gold':'Safety yellow enamel','steel':'Polished chrome','white':'Ivory paint','black':'Rubber','wood':'Cut pine','brick':'Terracotta','green':'Plant leaves','light':'Warm cabinet bulbs','window':'House warm glazing','floor':'Mineral concrete','glass':'Translucent elevated ramp','clear':'Clear acrylic channel walls','concrete':'Rough concrete blocks','cardboard':'Shipping cardboard','orange':'Safety cone orange','leaf':'Palm leaf light side','soil':'Potting soil'}
for key,name in lookup.items():globals()[key]=bpy.data.materials[name]
props=Props({k:globals()[k] for k in ['cube','cyl','line','sphere','pt','wood','steel','white','navy','gold','blue','brick','black','green','leaf','soil','orange','concrete','cardboard']})
original=set(scene.objects)
static=bpy.data.collections.new('Premium structural detailing');scene.collection.children.link(static)
foreground=bpy.data.collections['Foreground decorative raised channels'];interactive=bpy.data.collections['Interactive bumper tank target sling art'];dynamic=bpy.data.collections['Movable elements'];cover=bpy.data.collections['Protective glass reflections']
DATA=json.loads((ROOT/'layout.json').read_text())
amber=bpy.data.materials['Opal amber illuminated inserts'];metal=bpy.data.materials['Brushed aluminum mechanisms']
bronze=mat('Premium / satin brass sockets',(.38,.19,.035),.85,.22)
resin=mat('Premium / amber optical resin',(1,.42,.025),0,.16)
p=resin.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=.65;p.inputs['IOR'].default_value=1.48;p.inputs['Coat Weight'].default_value=.4
ivory=mat('Premium / flipper glazed ivory',(.88,.91,.91),.06,.19);ivory.node_tree.nodes.get('Principled BSDF').inputs['Coat Weight'].default_value=.65

def point(name,x,y,z,power=2,color=(1,.48,.08),radius=.08):
    d=bpy.data.lights.new(name,'POINT');d.energy=power;d.color=color;d.shadow_soft_size=radius;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=pt(x,y,z);return o

def screw(x,y,z,r=.037,collection=None):
    cyl('Premium / recessed chrome washer',x,y,z,r*1.38,.012,metal,collection)
    cyl('Premium / slotted screw head',x,y,z+.013,r,.025,steel,collection)
    for a in [0,math.pi/2]:
        line('Premium / screw drive',[(x-math.cos(a)*r*.65,y-math.sin(a)*r*.65,z+.027),(x+math.cos(a)*r*.65,y+math.sin(a)*r*.65,z+.027)],.004,black,collection)

def ring(name,x,y,z,r,thickness,material,collection=None):return line(name,[(x+r*math.cos(i*math.tau/64),y+r*math.sin(i*math.tau/64),z) for i in range(65)],thickness,material,collection)
def mesh(name,verts,faces,m,collection=None):
    me=bpy.data.meshes.new(name);me.from_pydata([pt(*v) for v in verts],[],faces);me.update();o=bpy.data.objects.new(name,me);(collection or static).objects.link(o);o.data.materials.append(m);return o

def bezier(a,b,c,d,n=25):return [tuple((1-t)**3*a[k]+3*(1-t)**2*t*b[k]+3*(1-t)*t*t*c[k]+t**3*d[k] for k in range(3)) for t in [i/n for i in range(n+1)]]
def channel(name,path,collection,ends=(1,1)):
    # Ribbon normals blend to original global-X cross sections at junctions.
    edges=[[],[]]
    for i,p in enumerate(path):
        q=path[min(len(path)-1,i+1)];r=path[max(0,i-1)];dx=q[0]-r[0];dy=q[1]-r[1];length=math.hypot(dx,dy);nx,ny=dy/length,-dx/length
        if i<4:
            w=i/4;nx=ends[0]*(1-w)+nx*w;ny*=w
        elif i>len(path)-5:
            w=(len(path)-1-i)/4;nx=ends[1]*(1-w)+nx*w;ny*=w
        for j,s in enumerate([-1,1]):edges[j].append((p[0]+s*.35*nx,p[1]+s*.35*ny,p[2]))
    verts=[p for pair in zip(*edges) for p in pair];faces=[(2*i,2*i+2,2*i+3,2*i+1) for i in range(len(path)-1)]
    o=mesh(name+' / continuous molded acrylic bed',verts,faces,glass,collection);s=o.modifiers.new('Acrylic floor thickness','SOLIDIFY');s.thickness=.045
    for edge in edges:
        wall=mesh(name+' / transparent safety wall',edge+[(x,y,z+.23) for x,y,z in edge],[(i,i+1,i+1+len(edge),i+len(edge)) for i in range(len(edge)-1)],clear,collection);wall.modifiers.new('Wall thickness','SOLIDIFY').thickness=.018
        line(name+' / chrome handrail',[(x,y,z+.25) for x,y,z in edge],.028,steel,collection)
        line(name+' / structural cobalt edge',[(x,y,z-.035) for x,y,z in edge],.045,blue,collection)
        for i in range(0,len(edge),9):
            x,y,z=edge[i]
            # Rear straight span and low landing carry floor-mounted columns.
            # Corner/descending spans use bed-mounted rail brackets so no post
            # pierces the pallets, paint cans or tools underneath the channel.
            anchored=(name=='Upper bridge' and 25<=i<=50) or (name!='Upper bridge' and i>=len(edge)-6)
            bottom=.09 if anchored else max(.06,z-.11)
            line(name+' / supporting stanchion',[(x,y,bottom),(x,y,z+.27)],.033,steel,collection)
            if anchored:
                cyl(name+' / bolted foot',x,y,.08,.09,.06,metal,collection);screw(x+.07,y,.12,.022,collection)
            for zz in [z-.07,z+.18]:ring(name+' / rail collar',x,y,zz,.044,.012,bronze,collection)
    for i in range(0,len(path),12):
        x,y,z=path[i];line(name+' / transverse joint',[(edges[0][i][0],edges[0][i][1],z+.012),(edges[1][i][0],edges[1][i][1],z+.012)],.013,steel,collection)
        for edge in edges:
            xx,yy,_=edge[i];sphere(name+' / amber marker',xx,yy,z+.27,.045,amber,collection);point(name+' / practical marker',xx,yy,z+.34,1.1)
    for i in range(8,len(path)-3,14):
        x,y,z=path[i];q=path[i+1];a=math.atan2(q[1]-y,q[0]-x)
        def tr(u,v):return (x+u*math.cos(a)-v*math.sin(a),y+u*math.sin(a)+v*math.cos(a))
        polygon(name+' / illuminated direction insert',[tr(.13,0),tr(-.1,.17),tr(-.04,0),tr(-.1,-.17)],z+.013,amber,collection)
    return path
# A single connected upper route, passing physically behind the existing house.
rear=bezier((1.45,1.7,1.73),(1.19,1.25,1.7),(1.7,1.05,1.42),(2.8,1.05,1.42))
rear+=bezier((2.8,1.05,1.42),(4.1,1.05,1.42),(5.6,1.05,1.42),(6.9,1.05,1.42))[1:]
rear+=bezier((6.9,1.05,1.42),(7.7,1.05,1.42),(7.84,1.25,1.7),(8.05,1.7,1.73))[1:]
channel('Upper bridge',rear,static,(-1,1))
lx=1.45+.65*math.sin(8.2*.8);rx=8.05+.5*math.sin(4*.85)
channel('Left return transition',bezier((lx,9.9,1.18),(2.15,10.6,1.18),(2.45,10.95,.35),(2.45,11.65,.065),40),foreground)
channel('Right return transition',bezier((rx,5.7,1.18),(7.65,6.23,1.12),(6.95,6.4,.35),(6.9,7.05,.065),40),foreground)
# Raised garden is integrated around, not moved beneath, the original house.
cube('Terrace / layered structural base',4.7,2.35,.115,5.0,3.0,.22,navy)
cube('Terrace / dressed stone slab',4.7,2.35,.245,4.94,2.94,.12,concrete)
for x in [2.22,7.18]:
    cube('Terrace / raised curb',x,2.35,.36,.13,2.95,.22,white)
    line('Terrace / recessed amber edge',[(x,1,.29),(x,3.72,.29)],.015,amber)
for x in [2.55,6.85]:
    cube('Garden / deep planting bed',x,2.1,.34,.55,2.1,.12,soil)
    for i in range(48):
        xx=x+random.uniform(-.22,.22);yy=1.12+random.random()*1.96
        for j in range(3):line('Garden / individual grass blades',[(xx,yy,.4),(xx+random.uniform(-.05,.05),yy+random.uniform(-.05,.05),random.uniform(.46,.57))],.009,green)
    for y in [1.05,1.55,2.05,2.55,3.05,3.55]:
        cube('Garden / patio paver',x+(.43 if x<4 else -.43),y,.328,.31,.43,.035,white)
for x in [2.3,3.0,6.4,7.1]:
    cube('Terrace / pilaster',x,3.79,.22,.2,.17,.36,concrete);screw(x,3.82,.41)
for x in [4.4,4.7,5.0]:cube('House / entry paving',x,3.56,.335,.28,.28,.045,white)
# Branches and many distinct leaf blades, with visible woody structure.
for x,y in [(2.48,1.85),(6.95,2.0)]:
    line('Garden tree / branching trunk',[(x,y,.38),(x-.06,y,1),(x+.04,y,1.65)],.065,wood)
    for j in range(7):
        a=j*2.4;xx=x+math.cos(a)*.32;yy=y+math.sin(a)*.28;zz=1.25+j*.085
        line('Garden tree / lateral branch',[(x,y,zz-.35),(xx,yy,zz)],.022,wood)
        for k in range(12):
            o=sphere('Garden tree / separate leaf',xx+random.uniform(-.17,.17),yy+random.uniform(-.17,.17),zz+random.uniform(-.07,.16),.065,leaf if k%3 else green);o.scale=(.5,1.6,.3);o.rotation_euler=(random.random(),random.random(),random.random()*6)
for x in [3.9,5.5]:
    cube('House / window header',x,3.44,1.46,.67,.10,.045,white)
    for dx in [-.18,.18]:cube('House / inner sash',x+dx,3.447,1.11,.016,.016,.58,wood)
for z in [.44,.9,1.36]:
    cube('House / brass door hinge',4.49,3.38,z,.035,.035,.09,bronze)
for z in [.56,1.12]:
    cube('House / recessed door panel',4.7,3.38,z,.31,.025,.42,navy);cube('House / inset oak door panel',4.7,3.40,z,.275,.02,.38,wood)
cube('House / stone threshold',4.7,3.43,.25,.52,.21,.07,concrete)
for x in [3.28,6.12]:
    for y in [1.6,2.15,2.7,3.3]:cube('House / gutter strap',x,y,1.73,.09,.025,.085,bronze)
for x in [3.08,6.32]:
    for z in [.22,1.04]:
        o=cyl('Sign / recessed frame bolt',x,3.728,z,.028,.02,steel);o.rotation_euler.x=math.pi/2
# Compact construction and hardware groups fill shoulders and front pockets.
props.pallet(1.1,13.75,.72,.8);props.crate(1.05,13.7,.55,.52,.43,.2);props.tape(1.06,13.7,.66)
props.block(1.5,13.5,.1);props.bucket(.84,12.5,.04,.16,.34)
props.pallet(8.24,14.05,.45,.75);props.box(8.22,14.0,.25,.36,.43);props.bucket(8.23,13.55,.05,.16,.32)
props.plant(7.99,14.55,.03,.38)
# Rear workshop corners are visible through the elevated acrylic bridge.
props.pallet(1.35,1.2,.85,.68);props.blocks(1.28,1.13,.18,4)
props.crate(7.92,1.1,.65,.54,.6,.04);props.bucket(7.96,1.1,.66,.19,.35)
props.plant(7.4,1.15,.06,.55)
for x,y,z in [(1.08,13.7,.88),(1.45,5.95,.98),(7.85,7.25,1.03),(8.18,14.02,.7)]:
    cube('Hardware tray / bottom',x,y,z,.35,.25,.025,navy)
    for dx in [-.18,0,.18]:cube('Hardware tray / divider',x+dx,y,z+.04,.018,.27,.08,blue)
    for dy in [-.13,.13]:cube('Hardware tray / lip',x,y+dy,z+.04,.37,.018,.08,blue)
    master=cyl('Hardware / reusable hex bolt',x-.09,y,z+.06,.022,.07,steel)
    for i in range(12):props.copy(master,'Hardware / linked tray fastener',random.uniform(-.03,.2),random.uniform(-.09,.09),random.uniform(0,.03))
for x,y,z in [(1.55,5.5,.18),(8.3,10.4,.12),(8.18,14.3,.15)]:
    for j in range(4):
        line('Plumbing / stacked copper pipe',[(x+j*.055,y-.27,z+(j%2)*.07),(x+j*.055,y+.27,z+(j%2)*.07)],.022,bronze)
        ring('Plumbing / pipe end collar',x+j*.055,y+.27,z+(j%2)*.07,.03,.008,steel)
for x,y in [(1.15,5.4),(1.12,8.6),(7.95,12.8)]:
    for j in range(3):cube('Workshop / stacked short boards',x,y,.12+j*.075,.55,.22,.065,wood)
    props.hand_tools(x,y,.35)
# Additional compact groups nest beneath the existing elevated shoulders.
props.pallet(2.0,5.0,.64,.56);props.bricks(1.92,5.0,.22,3)
props.bucket(1.91,8.75,.04,.16,.34);props.bucket(1.62,8.91,.05,.13,.27)
props.crate(7.72,4.3,.48,.43,.42,.02);props.tape(7.72,4.3,.46)
props.plant(7.15,4.8,.04,.4)
# Flush factory graphics occupy the concrete without introducing false obstacles.
for side in [-1,1]:
    for y in [5.05,5.8,6.55,9.8,12.0]:
        x=4.7+side*1.47
        polygon('Playfield / cobalt route chevron',[(x-.23,y+.23),(x,y-.12),(x+.23,y+.23),(x,y+.09)],.041,blue)
for x in [2.55,6.85]:
    line('Playfield / printed lane pinstripe',[(x,4.85,.04),(x,6.55,.04)],.018,gold)
# Real inserts have an opaque yellow bezel and a smaller luminous resin lens.
# Flush printed route ribbons add the reference's cobalt/yellow floor contrast.
for o in list(scene.objects):
    if o.name.startswith('Directional inlay'):
        coords=[(v.co.x+5,8-v.co.y) for v in o.data.vertices]
        cx=sum(x for x,y in coords)/len(coords);cy=sum(y for x,y in coords)/len(coords)
        o.data.materials.clear();o.data.materials.append(gold)
        polygon('Insert / inset opal lens',[(cx+(x-cx)*.66,cy+(y-cy)*.66) for x,y in coords],.052,amber)
        if cx<8.7:
            polygon('Playfield / broad cobalt route mark',[(cx-.38,cy+.64),(cx,cy+.23),(cx+.38,cy+.64),(cx,cy+.46)],.042,blue)
for side in [-1,1]:
    x=4.7+side*3.25
    for y in [4.7,5.8,6.9,8.0,9.1,10.2,11.3,12.4]:
        polygon('Workshop / lacquered hazard foundation',[(x-.38,y-.35),(x+.38,y-.2),(x+.38,y+.2),(x-.38,y+.05)],.042,gold)
# Layered sling assemblies retain the exact original footprint.
for s in DATA['slings']:
    v=s['vertices'];cx=sum(p[0] for p in v)/3;cy=sum(p[1] for p in v)/3
    inner=[(cx+(x-cx)*.91,cy+(y-cy)*.91) for x,y in v]
    for z,m,r in [(.15,black,.065),(.28,steel,.027),(.39,gold,.037)]:line('Sling / layered perimeter',[(x,y,z) for x,y in inner+[inner[0]]],r,m,interactive)
    for x,y in inner:
        cyl('Sling / chrome spacer',x,y,.23,.065,.25,steel,interactive);ring('Sling / insulating rubber foot',x,y,.115,.069,.018,black,interactive);screw(x,y,.43,.04,interactive)
    cyl('Sling / lamp socket',cx,cy,.39,.16,.055,bronze,interactive)
    sphere('Sling / optical amber dome',cx,cy,.49,.14,resin,interactive)
    point('Sling / warm spill',cx,cy,.68,2.6)
for b in DATA['bumpers']:
    x,y,r=b['x'],b['y'],b['radius'];tank=b.get('kind')=='tank';z=1.0 if tank else .77
    ring('Bumper / cap seam',x,y,z-.035,r*.94,.014,black,interactive)
    ring('Bumper / polished cap bead',x,y,z-.01,r*.95,.016,steel,interactive)
    for i in range(6):
        a=i*math.tau/6;xx=x+math.cos(a)*r*.83;yy=y+math.sin(a)*r*.83;screw(xx,yy,z+.025,.022,interactive)
    if tank:
        for a in [-1,1]:line('Tank / folded carrying handle',[(x+a*r*.98,y-.13,.76),(x+a*(r+.07),y-.13,.87),(x+a*(r+.07),y+.13,.87),(x+a*r*.98,y+.13,.76)],.018,steel,interactive)
for t in DATA['targets']:
    x,y=t['x'],t['y']
    for dx in [-.31,.31]:
        line('Target / folded frame',[(x+dx,y+.23,.16),(x+dx,y+.23,.86)],.019,steel,interactive)
        for z in [.2,.8]:
            o=cyl('Target / face screw',x+dx,y+.253,z,.025,.018,steel,interactive);o.rotation_euler.x=math.pi/2
# Flipper appearance: same center line, length and radius, with distinct vertical layers.
for o in list(dynamic.objects):
    if 'flipper' in o.name.lower():o.hide_render=True
for f in DATA['flippers']:
    x,y=f['x'],f['y'];a=f['rest'];length=f['length']
    def capsule(radius):
        ex=x+math.cos(a)*length;ey=y+math.sin(a)*length
        return [(ex+math.cos(a-math.pi/2+i*math.pi/24)*radius,ey+math.sin(a-math.pi/2+i*math.pi/24)*radius) for i in range(25)]+[(x+math.cos(a+math.pi/2+i*math.pi/24)*radius,y+math.sin(a+math.pi/2+i*math.pi/24)*radius) for i in range(25)]
    cyl('Flipper / chrome pivot bearing',x,y,.12,.20,.15,steel,dynamic)
    for radius,z,depth,m in [(.14,.13,.07,black),(.14,.28,.26,blue),(.135,.42,.025,steel),(.108,.46,.065,ivory)]:
        o=polygon('Flipper / assembled molded layer',capsule(radius),z,m,dynamic);o.modifiers.new('Molded thickness','SOLIDIFY').thickness=depth;bevel(o,.018)
    screw(x,y,.5,.033,dynamic)
# Reduce burned-out emitters and put lights outside opaque housings.
for name,strength in [('Warm cabinet bulbs',4.5),('Porcelain warm lamp',5),('Opal amber illuminated inserts',3)]:
    p=bpy.data.materials[name].node_tree.nodes.get('Principled BSDF');p.inputs['Emission Strength'].default_value=strength
for o in list(scene.objects):
    if o.type!='LIGHT':continue
    if o.name.startswith('Product /'):o.data.energy*=.72
    if o.name.startswith('Practical / bumper underlight'):
        nearest=min(DATA['bumpers'],key=lambda b:(o.location.x+5-b['x'])**2+(8-o.location.y-b['y'])**2)
        center=Vector(pt(nearest['x'],nearest['y'],0));d=o.location-center;d.z=0;d.normalize();o.location=center+d*(nearest['radius']+.16);o.location.z=.32;o.data.energy=2.1
    elif o.name.startswith('Practical / ') and 'blue cabinet' not in o.name and 'floor insert' not in o.name and 'pedestal' not in o.name:o.location.z+=.10
scene.world.node_tree.nodes.get('Background').inputs[1].default_value=.065
p=floor.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.37;p.inputs['Coat Weight'].default_value=.12
# Glass envelopes surround smaller emissive filaments, retaining warm edges.
for o in list(scene.objects):
    if o.type=='MESH' and ('Ramp glowing bulb' in o.name or o.name.startswith('Practical / warm bulb') or o.name.startswith('Warm safety beacon / lamp')):
        x,y,z=o.location.x+5,8-o.location.y,o.location.z
        radius=.10 if 'beacon' in o.name else .065
        collection=foreground if o.name in foreground.objects else static
        o.scale*=.57
        cyl('Lamp / brass collar',x,y,z-radius*.65,radius*.8,.045,bronze,collection)
        sphere('Lamp / amber glass envelope',x,y,z,radius,resin,collection)
    if o.name.startswith('Slingshot warm lamp'):o.scale*=.55
# Terminate the raised frame inside the image, preserving the pane and camera.
for o in cover.objects:
    if o.type=='MESH' and 'cheek' in o.name.lower():
        for v in o.data.vertices:
            if v.co.y>5.8 and v.co.z>.8:v.co.y=5.8;v.co.z=2.714
    if o.type=='CURVE' and any(s in o.name for s in ['retaining chrome','rubber gasket','polished edge']):
        for sp in o.data.splines:
            for p in sp.points:
                if p.co.y>5.8:p.co.y=5.8;p.co.z=2.714
    if o.type=='CURVE' and 'glass corner bracket' in o.name:
        for sp in o.data.splines:
            for p in sp.points:
                if p.co.y>5.8:p.co.y=5.8;p.co.z=min(p.co.z,2.714)
# Collect new static props without disturbing dedicated compositing layers.
for o in set(scene.objects)-original:
    if o.type in {'LIGHT','CAMERA'}:continue
    if any(o.name in c.objects for c in [static,foreground,interactive,dynamic,cover]):continue
    for c in list(o.users_collection):c.objects.unlink(o)
    static.objects.link(o)
scene.view_settings.exposure=.35
scene['premium_pass']='3.0';scene['channel_scope']='Continuous visual structure only; original Box2D remains unchanged'
scene.render.threads=4
for c in [static,foreground,interactive,dynamic,cover]:c.hide_render=False
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/ferrisariato-premium.blend'))
(ROOT/'assets/premium-inventory.json').write_text(json.dumps({'objects':len(scene.objects),'lights':sum(o.type=='LIGHT' for o in scene.objects),'shared_meshes':sum(m.users>1 for m in bpy.data.meshes),'added_objects':len(set(scene.objects)-original),'camera_matrix':[list(row) for row in scene.camera.matrix_world],'channel_scope':scene['channel_scope']},indent=2))
print('PREMIUM_SCENE_SAVED',len(scene.objects),flush=True)
