"""Restore transferred compressed originals and publish regenerated HOME assets."""
import subprocess,base64,json,os,shutil,sys
from pathlib import Path
ROOT=Path.cwd();parts=ROOT/'home/assets/new-packed';work=ROOT/'.home-model-work';work.mkdir(exist_ok=True)
models=ROOT/'home/assets/models';models.mkdir(parents=True,exist_ok=True)
imgs=ROOT/'home/assets/img';imgs.mkdir(parents=True,exist_ok=True)
for key,filename in [('umbrella','umbrella.blend'),('chair','chair.blend'),('format1','format1.blend'),('poltrona','poltrona.blend'),('patio','patio-set.glb')]:
 files=sorted(parts.glob(key+'.*.b64'))
 assert files,key+' parts not transferred'
 compressed=base64.b64decode(''.join(p.read_text().strip() for p in files))
 b= subprocess.run(['zstd','-dc'],input=compressed,capture_output=True,check=True).stdout
 (work/filename).write_bytes(b)
 print('RESTORED',key,len(b),flush=True)
# The Patio set has been locally converted using the complete original color,
# normal, roughness and metallic texture maps, with PBR materials embedded.
shutil.copy2(work/'patio-set.glb',models/'patio-set.glb')
assert (models/'patio-set.glb').read_bytes()[:4]==b'glTF'
reports={'patio':{'dimensions':[3.696,.779,2.719],'glb_bytes':(models/'patio-set.glb').stat().st_size}}
exe=os.getenv('BLENDER_BINARY','blender')
for key,filename in [('umbrella','umbrella.blend'),('chair','chair.blend'),('format1','format1.blend'),('poltrona','poltrona.blend')]:
 print('CONVERTING',key,flush=True)
 p=subprocess.run([exe,'--background','--factory-startup','--threads','2','--python-exit-code','7',
                   '--python',str(ROOT/'.github/scripts/convert_blends.py'),'--',
                   str(work/filename),str(models/(key+'.glb')),
                   str(imgs/(key+'.png')),key,str(work/(key+'.json'))],
                   text=True,capture_output=True,timeout=900)
 print('BLENDER_STDOUT',key,p.stdout[-6000:],flush=True)
 if p.returncode or not (models/(key+'.glb')).exists():
  print('CONVERSION_FAILED',key,p.returncode,p.stderr[-2000:],flush=True)
  continue
 reports[key]=json.loads((work/(key+'.json')).read_text())
# Render a photographed-looking thumbnail of the actual textured Patio set.
patio_command=[exe,'--background','--factory-startup','--threads','2','--python-exit-code','7',
               '--python',str(ROOT/'.github/scripts/convert_blends.py'),'--',
               str(work/'patio-set.glb'),str(models/'patio-set.glb'),
               str(imgs/'patio.png'),'patio',str(work/'patio.json')]
p=subprocess.run(patio_command,text=True,capture_output=True,timeout=900)
print('PATIO_RENDER',p.returncode,p.stdout[-2500:],p.stderr[-1000:],flush=True)
if p.returncode==0 and (work/'patio.json').exists():
 reports['patio']=json.loads((work/'patio.json').read_text())
print('REPORTS',json.dumps(reports,indent=2),flush=True)
(work/'reports.json').write_text(json.dumps(reports,indent=2))
# Only show new products whose GLBs actually passed conversion. Older products
# remain out of the catalogue permanently.
metadata=[
 dict(id='umbrella',name='SOMBRILLA',category='EXTERIORES',short='Sombrilla para patio y jardín',description='Visualiza esta sombrilla directamente en tu espacio.'),
 dict(id='chair',name='SILLA EXTERIOR',category='MOBILIARIO',short='Silla de diseño',description='Explora la silla en tres dimensiones y prueba su ubicación.'),
 dict(id='format1',name='FORMAT 1',category='MOBILIARIO',short='Modelo tridimensional original',description='Visualiza el modelo con su geometría y materiales originales.'),
 dict(id='poltrona',name='POLTRONA PL 461',category='DESCANSO',short='Sillón de diseño',description='Descubre el sillón en tu terraza o espacio interior.'),
 dict(id='patio',name='PATIO SET',category='CONJUNTO EXTERIOR',short='Conjunto con madera y cojines texturizados',description='Conjunto de patio con materiales PBR de madera y textiles.'),
]
products=[]
for item in metadata:
 key=item['id']
 if key not in reports:continue
 item.update(thumb=f'./assets/img/{key}.png' if (imgs/(key+'.png')).exists() else './assets/img/terraza-referencia.jpg',
             local=f'./assets/models/{key}.glb',pack=None,remote=None,modelReady=True,
             dimensions=reports[key]['dimensions'],source='Modelo original enviado por el usuario')
 products.append(item)
assert products and any(x['id']=='patio' for x in products)
(ROOT/'home/js/products.js').write_text('export const PRODUCTS='+json.dumps(products,ensure_ascii=False,indent=2)+';\n')
# Remove the outdated assets (including old packed copies) only after new ones exist.
keep={item['id']+'.glb' for item in products}
for f in models.rglob('*'):
 if f.is_file() and f.relative_to(models).as_posix() not in keep:f.unlink()
for d in sorted(models.rglob('*'),key=lambda p:len(p.parts),reverse=True):
 if d.is_dir() and not list(d.iterdir()):d.rmdir()
# Remove old item thumbnails but keep original site environment photograph.
for f in imgs.glob('*preview*'):
 if f.is_file():f.unlink()
# Clear unused legacy product-specific orientation and packed model requirement.
scene=ROOT/'home/js/scene.js'
s=scene.read_text()
s=s.replace("import {resolvePackedModel} from './packed-models.js';\n",'')
s=s.replace('const url=await resolvePackedModel(product);','const url=product.local;')
s=s.replace("if(product.id==='mesa'){root.setLocalEulerAngles(-90,0,0);root.setLocalPosition(0,0.483011,1.210748);}",'')
scene.write_text(s)
# Legacy packed model resolver is unused; delete it.
(ROOT/'home/js/packed-models.js').unlink(missing_ok=True)
shutil.rmtree(parts)
print('READY_TO_PUBLISH',len(products),'models, ids:',[x['id'] for x in products],flush=True)