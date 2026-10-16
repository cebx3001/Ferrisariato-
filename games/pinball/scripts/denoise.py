"""OIDN HDR denoising with Cycles albedo/normal guides; preserve original alpha.
Requires OpenEXR, numpy and the official oidnDenoise executable (OIDN_BIN).
"""
import os,sys,subprocess,tempfile
from pathlib import Path
import numpy as np
import OpenEXR
source,target=map(Path,sys.argv[1:3])
f=OpenEXR.InputFile(str(source));h=f.header();w=h['dataWindow'].max.x+1;hh=h['dataWindow'].max.y+1
names=list(h['channels'])
def read(suffix):
    name=next(n for n in names if n.endswith(suffix))
    return np.frombuffer(f.channel(name),np.float32).reshape(hh,w).copy()
def rgb(passname):return np.stack([read(passname+'.'+c) for c in 'RGB'],axis=-1)
def pfm(path,a):
    with open(path,'wb') as out:out.write(f'PF\n{w} {hh}\n-1.0\n'.encode());out.write(np.flipud(a).astype('<f4').tobytes())
with tempfile.TemporaryDirectory(prefix='pinball-oidn-') as tmp:
    tmp=Path(tmp);color=rgb('Combined');alpha=read('Combined.A')
    # Cycles Combined is premultiplied; denoise straight RGB to prevent alpha fringes.
    color=np.divide(color,alpha[...,None],out=np.zeros_like(color),where=alpha[...,None]>.001)
    pfm(tmp/'color.pfm',color)
    cmd=[os.environ.get('OIDN_BIN','oidnDenoise'),'--hdr',str(tmp/'color.pfm'),'--threads','4','--quality','high']
    for passname,flag in [('Denoising Albedo','--alb'),('Denoising Normal','--nrm')]:
        try:a=rgb(passname)
        except StopIteration:
            # Normal passes use XYZ channel names in Blender.
            if 'Normal' not in passname:raise
            a=np.stack([read(passname+'.'+c) for c in 'XYZ'],axis=-1)
        path=tmp/(flag[2:]+'.pfm');pfm(path,a);cmd.extend([flag,str(path)])
    cmd+=['-o',str(tmp/'denoised.pfm')];subprocess.run(cmd,check=True)
    with open(tmp/'denoised.pfm','rb') as inp:
        assert inp.readline().strip()==b'PF';dims=inp.readline();scale=inp.readline();out=np.flipud(np.frombuffer(inp.read(),'<f4').reshape(hh,w,3)).copy()
    out*=alpha[...,None]
    header=OpenEXR.Header(w,hh);header['channels']={c:h['channels'][next(n for n in names if n.endswith('Combined.'+c))] for c in 'RGBA'}
    result=OpenEXR.OutputFile(str(target),header)
    result.writePixels({**{c:out[:,:,i].astype(np.float32).tobytes() for i,c in enumerate('RGB')},'A':alpha.tobytes()});result.close()
print('DENOISED',target)
