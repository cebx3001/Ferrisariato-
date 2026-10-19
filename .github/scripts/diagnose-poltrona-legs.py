import json,struct,sys
from pathlib import Path
import numpy as np, trimesh
p=Path("home/assets/models/poltrona-pl-461.glb")
b=p.read_bytes();print("FILE_BYTES",len(b),"MAGIC",b[:4],flush=True)
if b[:4]!=b"glTF":raise RuntimeError("bad GLB")
chunklen,chunktype=struct.unpack_from("<II",b,12)
o=json.loads(b[20:20+chunklen])
print("GLTF_MATERIALS",[(i,m.get("name"),m.get("doubleSided"),m.get("alphaMode"),m.get("pbrMetallicRoughness",{}).get("baseColorFactor")) for i,m in enumerate(o.get("materials",[]))],flush=True)
print("NODE_LIST",[(i,x.get("name"),x.get("mesh"),x.get("translation"),x.get("rotation"),x.get("scale"),x.get("matrix"),x.get("children")) for i,x in enumerate(o.get("nodes",[]))],flush=True)
scene=trimesh.load(str(p),force="scene")
print("SCENE_BOUNDS",scene.bounds.tolist(),flush=True)
print("SCENE_MESHES",list(scene.geometry),flush=True)
for node_name in scene.graph.nodes_geometry:
    transform,geom=scene.graph.get(node_name)
    mesh=scene.geometry[geom]
    transformed=trimesh.transform_points(mesh.vertices,transform)
    bb=np.array([transformed.min(axis=0),transformed.max(axis=0)])
    edges=np.array(mesh.edges_unique)
    v=mesh.vertices
    print("NODE",node_name,"GEOM",geom,"VERTS",len(v),"FACES",len(mesh.faces),
          "WORLDBOUNDS_XYZ",bb.tolist(),"WORLDMIN_Y",round(bb[0,1],5),"WORLDMAX_Y",round(bb[1,1],5),
          "LOCAL_BOUNDS",mesh.bounds.tolist(),
          "WINDING",mesh.is_winding_consistent,
          "WATERTIGHT",mesh.is_watertight,
          "VOL",round(mesh.volume,5),
          "SAMPLE_NORMAL",mesh.face_normals[:3].tolist(),flush=True)
    if "WOOD" in geom.upper() or "CUBE" in geom.upper() or "FOOT" in geom.upper():
        print("WOOD_MESH_FACES",len(mesh.faces),"UNIQUE_V",len(v),"CENTER_XYZ",transformed.mean(axis=0).tolist())
bounds=scene.bounds
print("VERDICT_VERTICAL_Y_GROUND",float(bounds[0,1]),"TOP",float(bounds[1,1]),flush=True)
