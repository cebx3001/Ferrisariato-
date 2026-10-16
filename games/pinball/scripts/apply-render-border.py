"""Assemble a same-camera Cycles border render into its full-resolution output."""
import sys
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[1]
for name in sys.argv[1:]:
 target=root/('docs/precision-hero.png' if name=='hero' else f'assets/{name}.png')
 full=Image.open(target).convert('RGBA');patch=Image.open(Path('/tmp/precision-apron')/(name+'.png')).convert('RGBA')
 assert patch.width==full.width and patch.height<full.height
 full.paste(patch,(0,full.height-patch.height));full.save(target)
 if name!='hero':full.save(target.with_suffix('.webp'),quality=92,method=6)
 print('Integrated same-camera border',name,patch.size)
