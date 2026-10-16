"""Create reference/render comparison artifacts after the final Cycles export."""
from pathlib import Path
from PIL import Image,ImageDraw
import json
root=Path(__file__).resolve().parents[1];docs=root/'docs';hero=Image.open(docs/'precision-hero.png').convert('RGB')
refs=docs/'precision-references'
pairs=[('general','1-43994.jpg',(0,0,1,1)),('flippers-slingshot','2-43989.jpg',(.17,.54,.51,.86)),('casa-canal','3-43990.jpg',(.12,.12,.88,.40)),('descenso-izquierdo','4-43993.jpg',(.06,.18,.35,.63)),('terraza-derecha','5-43991.jpg',(.67,.22,.91,.70))]
for key,ref,box in pairs:
 a=Image.open(refs/ref).convert('RGB');b=hero.crop(tuple(int(v*(hero.width if i%2==0 else hero.height)) for i,v in enumerate(box)))
 b.save(docs/f'precision-detail-{key}.png')
 canvas=Image.new('RGB',(1200,1040),'#071b30');draw=ImageDraw.Draw(canvas)
 for i,im in enumerate([a,b]):
  im.thumbnail((580,980));canvas.paste(im,(i*600+(600-im.width)//2,40+(980-im.height)//2));draw.text((i*600+20,15),'FOTOGRAFIA APROBADA' if i==0 else 'ESCENA BLENDER / CYCLES',fill='white')
 canvas.save(docs/f'precision-compare-{key}.jpg',quality=94)
html='''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ferrisariato · Revisión de precisión</title><style>*{box-sizing:border-box}body{margin:0;background:#06172b;color:#ecf4ff;font:16px system-ui}main{max-width:1300px;margin:auto;padding:28px}h1{font-size:30px}p{color:#bbcede;line-height:1.5}a{color:#ffd329}figure{margin:25px 0}img{max-width:100%;display:block}figcaption{padding:10px 0}.overlay{position:relative;max-width:700px;margin:auto;aspect-ratio:2/3}.overlay img{position:absolute;width:100%;height:100%;object-fit:contain}label{display:block;margin:16px 0}input{width:min(500px,80%)}details{margin-top:24px;border-top:1px solid #406080;padding-top:16px}.links{display:flex;gap:25px;flex-wrap:wrap}</style><main><h1>Ferrisariato · Revisión de precisión V4</h1><p>Comparación con las cinco fotografías aprobadas. La escena usa un solo canal continuo, tablero inclinado 6,5°, cabezal integrado y proyección compartida con el juego.</p><div class="links"><a href="precision-hero.png">Render completo</a><a href="precision-collision-map.svg">Mapa de colisiones</a><a href="precision-tests/complete-channel-launch.webm">Lanzamiento grabado</a><a href="precision-tests/results.json">Pruebas individuales</a></div><label>Superposición de referencia: <input id="opacity" type="range" min="0" max="100" value="0"></label><div class="overlay"><img src="precision-hero.png" alt="Render final"><img id="reference" src="precision-references/1-43994.jpg" alt="Fotografía aprobada" style="opacity:0"></div>'''
for key,ref,box in pairs:html+=f'<details open><summary>{key.replace("-"," ").upper()}</summary><figure><img loading="lazy" src="precision-compare-{key}.jpg" alt="Comparación {key}"></figure></details>'
html+='''<details><summary>Iteraciones previas</summary><p>Se corrigieron separación del cabezal, altura de la casa, colocación de piezas, vidrio, decoración en el recorrido y barandas incompatibles.</p>'''
for i in range(1,5):html+=f'<a href="precision-pass{i}.png">Pasada {i}</a> · '
html+='</details></main><script>opacity.oninput=()=>reference.style.opacity=opacity.value/100;</script></html>'
(docs/'precision-comparison.html').write_text(html)
print('Precision comparison: five pairs and interactive overlay saved')
