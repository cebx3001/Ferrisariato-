"""Fill the exposed gray rear terrace areas identified in the final closeup."""
import bpy,math,json,random,bmesh,ast
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;board=Matrix(json.loads((R/'assets/projection.json').read_text())['boardTransform']);coll=bpy.data.collections['Reference V5 / workshop assets'];cache={};made=[];asset=None
for key,name in {'blue':'Reference V5 / cobalt lacquer','yellow':'Reference V5 / safety yellow lacquer','black':'Reference V5 / rubber','chrome':'Reference V5 / polished chrome','dark':'Reference V5 / dark steel','white':'Reference V5 / white molded cap','orange':'Reference V5 / cone orange','wood':'Cut pine','terra':'Terracotta','concrete':'Rough concrete blocks','soil':'Potting soil'}.items():globals()[key]=bpy.data.materials[name]
leaves=[bpy.data.materials['Reference V5 / leaf '+str(i)] for i in range(4)]
for node in ast.parse((R/'blender/reference_components.py').read_text()).body:
 if isinstance(node,ast.FunctionDef):exec(compile(ast.Module(body=[node],type_ignores=[]),'reference props','exec'))
for o in list(s.objects):
 if str(o.get('reference_asset','')).startswith('DENSE / exposed rear terrace'):bpy.data.objects.remove(o,do_unlink=True)
for name,x,y,z in [('right upper',7.5,2.35,.55),('right lower',7.60,3.55,.54),('left workshop',1.97,2.7,.48)]:
 asset='DENSE / exposed rear terrace '+name;start=len(made)
 # Small raised trays, piles and containers fit the visible inner shelves.
 box('rear terrace / timber support crate',x,y,z+.15,.43,.54,.30,wood)
 for yy in [-.2,0,.2]:box('rear terrace / individual slat',x,y+yy,z+.315,.47,.17,.04,wood)
 if name=='right upper':
  for i in range(3):box('rear terrace / brick stack',x-.05,y+.10,z+.39+i*.13,.29,.22,.12,terra)
  bucket(x+.17,y-.12,z+.34,.12,.28)
  plant(x-.12,y+.13,z+.74,.48)
 elif name=='right lower':
  tape(x-.06,y-.02,z+.34);bucket(x+.20,y+.12,z+.34,.115,.27)
  tube('rear terrace / steel plier jaw',[(x-.13,y+.17,z+.37),(x+.02,y+.25,z+.37)],.018,chrome)
  for dx in [-.06,.06]:tube('rear terrace / red plier handle',[(x+.02,y+.25,z+.37),(x+.10+dx,y+.42,z+.37)],.022,orange)
 else:
  bucket(x-.10,y-.07,z+.34,.12,.31);tape(x+.10,y+.13,z+.34)
  box('rear terrace / loose timber offcut',x,y+.25,z+.35,.43,.065,.045,wood)
 for o in made[start:]:o['review_patch_group']='terrace-'+name.replace(' ','-')
s['rear_visible_terraces_populated']=True;bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/ferrisariato-precision.blend'));print('VISIBLE_REAR_TERRACES',len(made))
