import sys,OpenEXR,numpy as np
from PIL import Image
f=OpenEXR.InputFile(sys.argv[1]);h=f.header();w=h['dataWindow'].max.x+1;hh=h['dataWindow'].max.y+1
name=next(n for n in h['channels'] if '.Depth.' in n);z=np.frombuffer(f.channel(name),np.float32).reshape(hh,w)
v=np.rint(np.clip(z/100,0,1)*65535).astype(np.uint16);rgb=np.stack([v>>8,v&255,np.zeros_like(v)],axis=-1).astype(np.uint8)
Image.fromarray(rgb).save(sys.argv[2]);print('Depth encoded',w,hh,'range',float(z.min()),float(z.max()))
