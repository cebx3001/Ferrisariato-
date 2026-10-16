"""Pack portable font/image dependencies and inventory the editable final scene."""
import bpy,json,hashlib
from pathlib import Path
r=Path(__file__).resolve().parents[1];s=bpy.context.scene
bpy.ops.file.pack_all();bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(r/'blender/ferrisariato-precision.blend'))
meta={'objects':len(s.objects),'lights':sum(o.type=='LIGHT' for o in s.objects),'sharedMeshes':sum(m.users>1 for m in bpy.data.meshes),'collections':{c.name:len(c.objects) for c in bpy.data.collections},'camera':{'position':list(s.camera.location),'lens':s.camera.data.lens},'render':{'hero':[1320,1980],'heroSamples':96,'web':[880,1320],'webSamples':48,'engine':'Cycles','viewTransform':'AgX'},'logoSHA256':hashlib.sha256((r/'assets/logo-ferrisariato.png').read_bytes()).hexdigest(),'fonts':[{'name':f.name,'packed':bool(f.packed_file)} for f in bpy.data.fonts if not f.name.startswith('Bfont')],'rampSamples':len(json.loads((r/'layout.json').read_text())['ramp']['samples'])}
(r/'assets/precision-inventory.json').write_text(json.dumps(meta,indent=2));print(json.dumps(meta,indent=2))
