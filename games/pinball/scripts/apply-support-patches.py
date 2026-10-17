"""Assemble reviewed structural/drill regions at exact same-camera pixel positions.
Run after the full hero and detail exports. Full re-renders need no patch step.
"""
from pathlib import Path
from PIL import Image
import json
r=Path(__file__).resolve().parents[1]
regions={'flippers':(.25,.125,.72,.29),'slingshots':(.19,.22,.78,.37),'miniatures-tools':(.71,.34,.87,.65),'left-workshop':(.065,.20,.28,.60),'rear-corners':(.12,.58,.87,.86),'floor-reflections':(.30,.31,.73,.58)}
targets=[(1320,'precision-hero.png',(0,0)),(720,'precision-macro-tools.png',(0,0))]+[(1760,'precision-detail-'+name+'.png',(int(b[0]*1760),2640-int(b[3]*2640))) for name,b in regions.items()]
for folder in ['reference-support-patches','reference-drill-patches','reference-terrace-patches']:
 work=Path('/tmp')/folder;data=json.loads((work/'manifest.json').read_text())
 for width,target,offset in targets:
  path=r/'docs'/target;im=Image.open(path).convert('RGBA');updated=False
  for p in data:
   if p['width']!=width:continue
   patch=Image.open(work/p['file']).convert('RGBA');x=p['x']-offset[0];y=p['y']-offset[1]
   if x>=im.width or y>=im.height or x+patch.width<=0 or y+patch.height<=0:continue
   im.paste(patch,(x,y));updated=True
  if updated:im.save(path);print('Updated review geometry:',target)
