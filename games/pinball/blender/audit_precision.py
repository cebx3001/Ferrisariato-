import bpy,json
from mathutils import Matrix,Vector
from pathlib import Path
r=Path(__file__).resolve().parents[1];d=json.loads((r/'assets/projection.json').read_text());inv=Matrix(d['boardTransform']).inverted();bad=[];bpy.context.view_layer.update()
prefix=('Pallet','Crate','Timber','Brick','Concrete block','Cardboard','Carton','Tape measure','Toolbox','Cordless drill','Paint bucket','Cone','Ornamental','Pot /','Wheelbarrow','Small blue','Hammer','Wrench','Saw','Carpentry','Clamp','Sack','Mortar','Paint /','Hardware','Cable','Pipe','Brush','Roller','Worksite','Masonry','Painting','Electrical','Tools','Plumbing','Industrial guard','Warm safety','Playable corridor','Reference V5 /')
for o in bpy.context.scene.objects:
 if o.get('flipper_id') or str(o.get('reference_asset','')).startswith('sling-'):continue
 if o.hide_render or not o.name.startswith(prefix) or o.type not in {'MESH','CURVE','FONT'}:continue
 ps=[inv@o.matrix_world@Vector(v) for v in o.bound_box];xs=[p.x+5 for p in ps];ys=[8-p.y for p in ps];zs=[p.z for p in ps]
 if not o.name.startswith('Playable corridor') and min(zs)<.33 and max(zs)>.04 and min(ys)<11.5 and max(ys)>4.7 and max(xs)>1.68 and min(xs)<7.82:
  bad.append({'name':o.name,'x':[round(min(xs),3),round(max(xs),3)],'y':[round(min(ys),3),round(max(ys),3)],'z':[round(min(zs),3),round(max(zs),3)]})
(r/'docs/precision-decoration-audit.json').write_text(json.dumps(bad,indent=2));print(json.dumps(bad,indent=1))

# Exact triangle distances supplement the conservative playfield AABB report.
from mathutils.bvhtree import BVHTree
layout=json.loads((r/'layout.json').read_text());deps=bpy.context.evaluated_depsgraph_get();vs=[];fs=[];owners=[]
for o in bpy.context.scene.objects:
 if o.get('flipper_id') or str(o.get('reference_asset','')).startswith('sling-'):continue
 if o.hide_render or not o.name.startswith(prefix) or o.type not in {'MESH','CURVE','FONT'}:continue
 ev=o.evaluated_get(deps);me=ev.to_mesh()
 if not me:continue
 me.calc_loop_triangles();offset=len(vs);vs.extend(inv@o.matrix_world@v.co for v in me.vertices)
 for f in me.loop_triangles:fs.append(tuple(offset+i for i in f.vertices));owners.append(o.name)
 ev.to_mesh_clear()
bvh=BVHTree.FromPolygons(vs,fs,all_triangles=True);contacts=[]
for i,p in enumerate(layout['ramp']['samples']):
 co=Vector((p[0]-5,8-p[1],p[2]+layout['ballRadius']+.01));hit=bvh.find_nearest(co)
 if hit[0] is not None and hit[3]<layout['ballRadius']+.025:contacts.append({'sample':i,'name':owners[hit[2]],'clearance':round(hit[3]-layout['ballRadius'],4),'position':p})
(r/'docs/precision-channel-decoration-audit.json').write_text(json.dumps(contacts,indent=2));print('CHANNEL_INTERSECTIONS',json.dumps(contacts))

assert not bad, f"Decoration crosses playable floor: {len(bad)} parts"
assert not contacts, f"Channel clearance violation: {len(contacts)} samples"
