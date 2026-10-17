"""High-resolution crops from the unchanged game camera, including true side faces."""
import os,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
# Coordinates are normalized Blender render borders (origin at bottom-left).
regions={'flippers':(.25,.125,.72,.29),'slingshots':(.19,.22,.78,.37),'miniatures-tools':(.71,.34,.87,.65),'left-workshop':(.065,.20,.28,.60),'rear-corners':(.12,.58,.87,.86),'floor-reflections':(.30,.31,.73,.58)}
for name,border in regions.items():
 os.environ['PINBALL_DETAIL_BORDER']=','.join(map(str,border));os.environ['PINBALL_SAMPLES']='32'
 sys.argv=['blender','--','detail-'+name]
 exec(compile((R/'blender/render_precision.py').read_text(),str(R/'blender/render_precision.py'),'exec'),{'__file__':str(R/'blender/render_precision.py')})
 print('REFERENCE_DETAIL_SAVED',name,flush=True)
