"""Capture geometry/camera signatures, excluding materials, modifiers and render visibility."""
import bpy,json,hashlib,sys
from pathlib import Path
result={}
for o in bpy.context.scene.objects:
    if o.type=='LIGHT':continue
    value={'matrix':[list(row) for row in o.matrix_world],'type':o.type}
    if o.type=='MESH':value['vertices']=[list(v.co) for v in o.data.vertices];value['faces']=[list(f.vertices) for f in o.data.polygons]
    elif o.type=='CURVE':value['splines']=[[list(p.co) for p in s.points] for s in o.data.splines]
    elif o.type=='CAMERA':value['camera']={k:getattr(o.data,k) for k in ['type','lens','shift_x','shift_y','sensor_width','sensor_height','sensor_fit']}
    result[o.name]=hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()
Path(sys.argv[-1]).write_text(json.dumps(result,indent=2))
print('GEOMETRY_AUDIT',len(result))
