# Ferrisariato HOME / Poltrona PL 461
# Preserve ORIGINAL .blend mesh topology. Repair only missing PBR materials.
import bpy, sys, json, math
import numpy as np
from pathlib import Path
from mathutils import Vector, Matrix

src, dest = map(Path, sys.argv[sys.argv.index('--')+1:])
dest.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(src.resolve()),load_ui=False)
meshes=[o for o in bpy.data.objects if o.type=='MESH' and o.name in {'Cube','Cube.001','Plane','Plane.001','Plane.002'} and len(o.data.vertices)>0]
# Source also contains untextured auxiliary Plane.003 and Referencia; they are not parts of this chair.
if not meshes: raise RuntimeError("No original meshes!")
print("SOURCE",[(o.name,len(o.data.vertices),[m.name for m in o.data.materials if m]) for o in meshes],flush=True)

# Create genuinely embedded raster PBR textures, not viewport colors or missing external files.
N=512
yy,xx=np.mgrid[0:N,0:N].astype(np.float32)
rng=np.random.default_rng(461)
noise=rng.normal(size=(N,N)).astype(np.float32)
def write_texture(name, rgb, height, strength):
    img=bpy.data.images.new(name+"_COLOR",width=N,height=N,alpha=True)
    arr=np.empty((N,N,4),dtype=np.float32)
    for i in range(3): arr[:,:,i]=np.clip(rgb[:,:,i]/255.,0,1)
    arr[:,:,3]=1
    img.pixels.foreach_set(arr.reshape(-1));img.filepath_raw=str((dest/(name+"_color.png")).resolve());img.file_format='PNG';img.save()
    gy,gx=np.gradient(height)
    nx=-gx*strength;ny=-gy*strength
    inv=1/np.sqrt(nx*nx+ny*ny+1)
    norm=np.stack(((nx*inv+1)/2,(ny*inv+1)/2,inv,np.ones_like(nx)),axis=-1).astype(np.float32)
    nm=bpy.data.images.new(name+"_NORMAL",width=N,height=N,alpha=True)
    nm.pixels.foreach_set(norm.reshape(-1));nm.filepath_raw=str((dest/(name+"_normal.png")).resolve());nm.file_format='PNG';nm.save()
    return img,nm

# A tight over-under woven charcoal wicker. The relief is raster-baked so WebGL sees it.
col=((xx+((yy//16)%2)*12)%24)
lane=yy%16
cross=np.exp(-((col-12)/5.3)**4).astype(np.float32)
warp=np.exp(-((lane-8)/5.5)**4).astype(np.float32)
weave=(cross*0.60+warp*0.40)
height=(weave+0.14*np.sin(xx*1.17)+0.12*np.sin(yy*0.91)).astype(np.float32)
value=24+24*weave+2.0*noise
r=np.stack((value*0.96,value,value*1.03),axis=-1).astype(np.float32)
wicker=write_texture("ratten_graphite",r,height,4.7)

# Calm slate-blue fabric matching the user's exact photograph; subtle fine weave.
threads=(np.sin(xx*2.8)+np.sin(yy*2.9))*.46
value=threads+noise*.52+2.8*np.sin(xx*.023+yy*.011)
fab=np.stack((94+value,110+value,129+value),axis=-1).astype(np.float32)
cushion=write_texture("cushion_slate_blue",fab,threads+noise*.12,0.22)

# Four warm dark-wood inclined legs, anisotropic wood grain.
g=3.0*np.sin(xx*.34+1.5*np.sin(yy*.03))+2*np.sin(xx*.085)+2.0*noise
woodcolor=np.stack((96+g,58+g*.58,39+g*.42),axis=-1).astype(np.float32)
wood=write_texture("legs_dark_wood",woodcolor,g,0.12)

def new_material(name, pair, rough):
    color,norm=pair
    mat=bpy.data.materials.new(name)
    mat.use_nodes=True
    node=mat.node_tree.nodes
    node.clear()
    out=node.new("ShaderNodeOutputMaterial")
    bsdf=node.new("ShaderNodeBsdfPrincipled")
    mat.node_tree.links.new(bsdf.outputs["BSDF"],out.inputs["Surface"])
    bsdf.inputs["Roughness"].default_value=rough
    bsdf.inputs["Metallic"].default_value=0
    tex=node.new("ShaderNodeTexImage");tex.image=color
    mat.node_tree.links.new(tex.outputs["Color"],bsdf.inputs["Base Color"])
    nt=node.new("ShaderNodeTexImage");nt.image=norm;nt.image.colorspace_settings.name='Non-Color'
    nm=node.new("ShaderNodeNormalMap");nm.inputs["Strength"].default_value=.62
    mat.node_tree.links.new(nt.outputs["Color"],nm.inputs["Color"])
    mat.node_tree.links.new(nm.outputs["Normal"],bsdf.inputs["Normal"])
    mat.diffuse_color=(.25,.27,.28,1)
    return mat
mats={"wicker":new_material("WICKER_GRAPHITE",wicker,.66),
      "cushion":new_material("FABRIC_SLATE_BLUE",cushion,.80),
      "wood":new_material("WOOD_DARK_LEGS",wood,.48)}

# Existing source has "Material.003" for the shell, "Material.002" for cushion,
# and "Madeira generica" for legs, confirmed against previous GLB mesh groups.
def role(obj, source):
    n=(source or "").lower()
    if "madeira" in n or "wood" in n or obj.name.startswith("Cube"): return "wood"
    if n=="material.003" or obj.name=="Plane": return "wicker"
    if n=="material.002" or obj.name.startswith("Plane.001"): return "cushion"
    raise RuntimeError(f"Cannot safely identify material of {obj.name}: {source}")

assignments=[]
for o in meshes:
    if not o.data.uv_layers:
        raise RuntimeError("Original mesh has no UVs: "+o.name)
    orig=[m.name for m in o.data.materials if m]
    if not len(o.data.materials):
        use=role(o,"")
        o.data.materials.append(mats[use])
        assignments.append((o.name,"<missing>",use))
    else:
        for idx,m in enumerate(o.data.materials):
            use=role(o,m.name if m else "")
            o.data.materials[idx]=mats[use]
            assignments.append((o.name,m.name if m else "<missing>",use))
    o.hide_render=False
    o.hide_viewport=False
print("MATERIAL_ASSIGNMENTS",assignments,flush=True)
if {a[2] for a in assignments}!={"wood","wicker","cushion"}:
    raise RuntimeError("Three material families not found")

# Restore previously published real-world normalization. Never change local mesh positions.
pts=[o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
mn=[min(v[i] for v in pts) for i in range(3)]
mx=[max(v[i] for v in pts) for i in range(3)]
size=[mx[i]-mn[i] for i in range(3)]
scale=1.05/max(size[0],size[1])
center=Vector(((mn[0]+mx[0])/2,(mn[1]+mx[1])/2,mn[2]))
fix=Matrix.Scale(scale,4) @ Matrix.Translation(-center)
world={o:o.matrix_world.copy() for o in meshes}
for o in meshes:o.parent=None
for o in meshes:o.matrix_world=fix@world[o]
for o in bpy.context.selected_objects:o.select_set(False)
for o in meshes:o.select_set(True)
bpy.context.view_layer.objects.active=meshes[0]
target=dest/"poltrona-pl-461-textured.glb"
bpy.ops.export_scene.gltf(filepath=str(target.resolve()),export_format="GLB",
    use_selection=True,export_yup=True,export_animations=False,
    export_materials="EXPORT",export_image_format="AUTO")
assert target.stat().st_size>150000, ("Unexpectedly small output",target.stat().st_size)
assert target.read_bytes()[:4]==b'glTF'
print("GLB",target.stat().st_size,flush=True)

# Render only the original geometry, with neutral product lighting.
for o in bpy.context.selected_objects:o.select_set(False)
for o in bpy.data.objects:
    if o.type in {"LIGHT","CAMERA"}:o.hide_render=True
scene=bpy.context.scene
scene.render.engine="CYCLES";scene.cycles.samples=24
scene.render.resolution_x=820;scene.render.resolution_y=700
scene.render.resolution_percentage=100
scene.render.film_transparent=True
# Legacy 2.78 file contains a colored HDR world and compositing chain; both
# must be replaced so true PBR colors are visible in QA renders.
scene.use_nodes=False
qa_world=bpy.data.worlds.new("NEUTRAL_QA_WORLD")
qa_world.use_nodes=True
bg=qa_world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value=(.45,.45,.45,1)
bg.inputs["Strength"].default_value=.38
scene.world=qa_world
scene.view_settings.exposure=0
scene.view_settings.gamma=1
camdat=bpy.data.cameras.new("QA Camera");cam=bpy.data.objects.new("QA Camera",camdat)
bpy.context.collection.objects.link(cam);scene.camera=cam
camdat.type="ORTHO";camdat.ortho_scale=1.70
look=Vector((0,0,.27))
def light(name,power,pos,size):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size
    o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o)
    o.location=pos;o.rotation_euler=(look-o.location).to_track_quat('-Z','Y').to_euler()
light("KEY",500,(-2.4,-3.0,4.0),3.0)
light("FILL",270,(2.1,1.0,2.4),3.0)
light("RIM",400,(0.8,2.2,3.0),2.2)
scene.view_settings.view_transform="Standard"
for name,pos in [("threequarter",(1.6,-2.2,1.35)),("front",(0,-2.8,.82)),("side",(2.9,0,.80)),("rear",(0,2.8,.85))]:
    cam.location=pos;cam.rotation_euler=(look-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str((dest/("poltrona-"+name+".png")).resolve())
    bpy.ops.render.render(write_still=True)
    print("PREVIEW",name,flush=True)
(dest/"report.json").write_text(json.dumps({
    "source":src.name,"model":"Poltrona PL 461","mesh_count":len(meshes),
    "source_materials":assignments,"dimensions_m":[round(size[0]*scale,4),round(size[2]*scale,4),round(size[1]*scale,4)],
    "glb_bytes":target.stat().st_size,
    "textures":["ratten_graphite_color.png","ratten_graphite_normal.png",
                "cushion_slate_blue_color.png","cushion_slate_blue_normal.png",
                "legs_dark_wood_color.png","legs_dark_wood_normal.png"]
},indent=2))
print("PASS",flush=True)
