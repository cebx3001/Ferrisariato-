from pathlib import Path
import json,subprocess,os,tempfile
import numpy as np
from PIL import Image
r=Path(__file__).resolve().parents[1];work=Path('/tmp/reference-flippers');d=json.loads((work/'frames.json').read_text());images=[]
for frames in d['frames'].values():
 for f in frames:
  im=Image.open(work/f.pop('file')).convert('RGBA')
  # Cycles alpha stays exact; OIDN removes Monte Carlo noise from the LDR RGB.
  rgb=np.asarray(im,dtype=np.float32)[:,:,:3]/255;h,w=rgb.shape[:2]
  raw=work/'sprite-color.pfm';clean=work/'sprite-clean.pfm'
  with raw.open('wb') as out:out.write(f'PF\n{w} {h}\n-1.0\n'.encode());out.write(np.flipud(rgb).astype('<f4').tobytes())
  subprocess.run([os.environ.get('OIDN_BIN','/workspace/.cache/oidn-2.3.3.x86_64.linux/bin/oidnDenoise'),'--ldr',str(raw),'--srgb','--threads','2','--quality','high','-o',str(clean)],check=True,stdout=subprocess.DEVNULL)
  with clean.open('rb') as inp:
   inp.readline();inp.readline();inp.readline();filtered=np.flipud(np.frombuffer(inp.read(),'<f4').reshape(h,w,3))
  pixels=np.array(im);pixels[:,:,:3]=np.clip((filtered*.96+rgb*.04)*255,0,255).astype('uint8');im=Image.fromarray(pixels)
  f['width'],f['height']=im.size;images.append((f,im))
maxw=2048;x=y=row=0
for f,im in images:
 if x+im.width>maxw:x=0;y+=row;row=0
 f['sx']=x;f['sy']=y;x+=im.width;row=max(row,im.height)
atlas=Image.new('RGBA',(maxw,y+row))
for f,im in images:atlas.paste(im,(f['sx'],f['sy']))
atlas.save(r/'assets/flippers.webp',lossless=True,method=6)
d['atlasWidth'],d['atlasHeight']=atlas.size
(r/'assets/flippers.json').write_text(json.dumps(d,indent=2)+'\n')
print('Packed',len(images),'actual model frames;',atlas.size)
